"""GA Azure OpenAI realtime sessions; no simulated service fallback."""

import asyncio
import base64
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
import io
import json
import math
import os
import time
from urllib.parse import urlencode, urlsplit
import wave

RATE = 24000
BYTES_PER_SECOND = RATE * 2
MAX_AUDIO_BYTES = BYTES_PER_SECOND * 60


@dataclass(frozen=True)
class Settings:
    endpoint: str
    deployment: str
    api_key: str = field(default="", repr=False)

    @classmethod
    def from_env(cls):
        return cls(
            os.environ.get("AZURE_OPENAI_ENDPOINT", ""),
            os.environ.get("AZURE_OPENAI_DEPLOYMENT_NAME", ""),
            os.environ.get("AZURE_OPENAI_API_KEY", ""),
        )

    @property
    def url(self):
        parsed = urlsplit(self.endpoint)
        if (
            parsed.scheme != "https"
            or not parsed.hostname
            or not parsed.hostname.endswith(".openai.azure.com")
            or parsed.username
            or parsed.password
            or parsed.port
            or parsed.path not in ("", "/")
            or parsed.query
            or parsed.fragment
        ):
            raise ValueError("Use an HTTPS Azure OpenAI resource endpoint, without a path or query.")
        if not self.deployment.strip() or self.deployment == "your-realtime-deployment":
            raise ValueError("Set AZURE_OPENAI_DEPLOYMENT_NAME to your deployed realtime model.")
        if parsed.hostname == "your-resource.openai.azure.com":
            raise ValueError("Replace the example resource endpoint.")
        return f"wss://{parsed.hostname}/openai/v1/realtime?{urlencode({'model': self.deployment})}"


def session_config(instructions, silence_ms=None):
    if silence_ms is not None and not 200 <= silence_ms <= 2000:
        raise ValueError("silence_ms must be between 200 and 2000.")
    turn_detection = None if silence_ms is None else {
        "type": "server_vad",
        "threshold": 0.5,
        "prefix_padding_ms": 300,
        "silence_duration_ms": silence_ms,
        "create_response": True,
        "interrupt_response": True,
    }
    return {
        "type": "realtime",
        "instructions": instructions,
        "output_modalities": ["audio"],
        "max_output_tokens": 512,
        "audio": {
            "input": {
                "format": {"type": "audio/pcm", "rate": RATE},
                "turn_detection": turn_detection,
            },
            "output": {
                "format": {"type": "audio/pcm", "rate": RATE},
                "voice": "alloy",
            },
        },
    }


class RealtimeError(RuntimeError):
    """Service failure with payloads deliberately omitted from notebook output."""


class Session:
    def __init__(self, socket):
        self.socket = socket
        self.events = []
        self.started = time.monotonic()

    async def send(self, kind, **payload):
        await self.socket.send(json.dumps({"type": kind, **payload}))

    async def receive(self):
        event = json.loads(await self.socket.recv())
        kind = event["type"]
        self.events.append({"type": kind, "elapsed_s": round(time.monotonic() - self.started, 3)})
        if kind == "error":
            # Service messages can echo input; expose only diagnostic classification.
            error = event.get("error", {})
            raise RealtimeError(f"Realtime service error ({error.get('type', 'unknown')}); inspect Azure diagnostics privately.")
        if kind == "response.done":
            status = event["response"]["status"]
            if status not in ("completed", "cancelled"):
                raise RealtimeError(f"Response ended with status {status}.")
        return event

    async def wait_for(self, kind):
        while True:
            event = await self.receive()
            if event["type"] == kind:
                return event

    async def configure(self, instructions, silence_ms):
        async with asyncio.timeout(20):
            await self.wait_for("session.created")
            await self.send("session.update", session=session_config(instructions, silence_ms))
            await self.wait_for("session.updated")


@asynccontextmanager
async def connect(settings, instructions, silence_ms=None):
    from websockets.asyncio.client import connect as websocket_connect

    url = settings.url
    if settings.api_key:
        headers = {"api-key": settings.api_key}
    else:
        from azure.identity.aio import DefaultAzureCredential

        async with DefaultAzureCredential() as credential:
            token = await credential.get_token("https://ai.azure.com/.default")
        headers = {"Authorization": f"Bearer {token.token}"}
    async with websocket_connect(
        url, additional_headers=headers, open_timeout=20, max_size=4 * 1024 * 1024
    ) as socket:
        session = Session(socket)
        await session.configure(instructions, silence_ms)
        yield session


def validate_pcm(pcm):
    if not isinstance(pcm, bytes) or len(pcm) % 2:
        raise ValueError("Audio must be signed 16-bit little-endian mono PCM bytes.")
    if not BYTES_PER_SECOND // 10 <= len(pcm) <= MAX_AUDIO_BYTES:
        raise ValueError("Provide between 0.1 and 60 seconds of 24 kHz mono PCM.")


def wav_bytes(pcm):
    validate_pcm(pcm)
    output = io.BytesIO()
    with wave.open(output, "wb") as audio:
        audio.setnchannels(1)
        audio.setsampwidth(2)
        audio.setframerate(RATE)
        audio.writeframes(pcm)
    return output.getvalue()


async def record(seconds=5):
    """Record from the kernel machine's default microphone, not the browser."""
    import sounddevice as sd

    if not math.isfinite(seconds) or not 0.1 <= seconds <= 60:
        raise ValueError("Recording duration must be between 0.1 and 60 seconds.")

    def capture():
        with sd.RawInputStream(samplerate=RATE, channels=1, dtype="int16") as stream:
            audio, overflowed = stream.read(round(seconds * RATE))
            if overflowed:
                raise RuntimeError("Microphone overflow; retry with a less busy audio device.")
            return bytes(audio)

    return await asyncio.to_thread(capture)


async def exchange(session, pcm, timeout=60):
    validate_pcm(pcm)
    async with asyncio.timeout(timeout):
        for offset in range(0, len(pcm), 4800):
            await session.send(
                "input_audio_buffer.append",
                audio=base64.b64encode(pcm[offset:offset + 4800]).decode("ascii"),
            )
        await session.send("input_audio_buffer.commit")
        await session.send("response.create")
        output = bytearray()
        while True:
            event = await session.receive()
            if event["type"] == "response.output_audio.delta":
                output.extend(base64.b64decode(event["delta"], validate=True))
                if len(output) > MAX_AUDIO_BYTES:
                    raise RealtimeError("Response exceeded the local 60-second audio buffer limit.")
            if event["type"] == "response.done":
                if event["response"]["status"] != "completed" or not output:
                    raise RealtimeError("The voice exchange did not complete with audio.")
                return bytes(output)


class Playback:
    """Track PCM submitted to the device so interruption can truncate history."""

    def __init__(self):
        self.pending = bytearray()
        self.item_id = None
        self.content_index = 0
        self.played = 0
        self.discarded = set()

    def append(self, event):
        item = event["item_id"]
        if item in self.discarded:
            return
        if item != self.item_id:
            if self.pending:
                raise RealtimeError("A new audio item arrived before playback drained.")
            self.item_id, self.content_index, self.played = item, event["content_index"], 0
        self.pending.extend(base64.b64decode(event["delta"], validate=True))
        if len(self.pending) > MAX_AUDIO_BYTES:
            raise RealtimeError("Playback exceeded the local 60-second buffer limit.")

    def take(self, size):
        chunk = bytes(self.pending[:size])
        del self.pending[:size]
        self.played += len(chunk)
        return chunk + bytes(size - len(chunk))

    def interrupt(self):
        if self.item_id is None:
            return None
        event = {
            "item_id": self.item_id,
            "content_index": self.content_index,
            "audio_end_ms": self.played * 1000 // BYTES_PER_SECOND,
        }
        self.discarded.add(self.item_id)
        self.pending.clear()
        self.item_id = None
        return event


async def converse(session, seconds=25):
    """Bounded full-duplex local-device exercise with server VAD interruption."""
    import sounddevice as sd

    if not math.isfinite(seconds) or not 1 <= seconds <= 120:
        raise ValueError("Conversation duration must be between 1 and 120 seconds.")
    playback = Playback()
    # Blocking device I/O runs on worker threads; playback state stays on the loop.
    async def microphone(stream):
        while True:
            data, overflowed = await asyncio.to_thread(stream.read, 480)
            if overflowed:
                raise RuntimeError("Microphone overflow; restart the exercise.")
            await session.send("input_audio_buffer.append", audio=base64.b64encode(data).decode("ascii"))

    async def speaker(stream):
        while True:
            chunk = playback.take(480 * 2)
            underflowed = await asyncio.to_thread(stream.write, chunk)
            if underflowed:
                raise RuntimeError("Speaker underflow; restart the exercise.")

    async def events():
        while True:
            event = await session.receive()
            if event["type"] == "response.output_audio.delta":
                playback.append(event)
            elif event["type"] == "input_audio_buffer.speech_started":
                truncation = playback.interrupt()
                if truncation:
                    await session.send("conversation.item.truncate", **truncation)

    with sd.RawInputStream(samplerate=RATE, channels=1, dtype="int16") as input_stream:
        with sd.RawOutputStream(samplerate=RATE, channels=1, dtype="int16", blocksize=480) as output_stream:
            async with asyncio.TaskGroup() as group:
                tasks = [
                    group.create_task(microphone(input_stream)),
                    group.create_task(speaker(output_stream)),
                    group.create_task(events()),
                ]
                try:
                    await asyncio.sleep(seconds)
                finally:
                    for task in tasks:
                        task.cancel()
    return session.events
