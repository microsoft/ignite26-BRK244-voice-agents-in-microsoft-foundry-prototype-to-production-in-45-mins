import asyncio
import base64
import io
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
import wave

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from shared.realtime import (
    BYTES_PER_SECOND, Playback, RealtimeError, Session, Settings,
    connect, converse, exchange, session_config, validate_pcm, wav_bytes,
)


class Socket:
    def __init__(self, events):
        self.events = iter(events)
        self.sent = []

    async def send(self, value):
        self.sent.append(json.loads(value))

    async def recv(self):
        return json.dumps(next(self.events))


class ProtocolTests(unittest.IsolatedAsyncioTestCase):
    async def test_configuration_ack_precedes_input(self):
        socket = Socket([{"type": "session.created"}, {"type": "session.updated"}])
        session = Session(socket)
        await session.configure("brief", 500)
        self.assertEqual(socket.sent[0]["type"], "session.update")
        self.assertEqual(len(session.events), 2)

    async def test_audio_exchange_commits_then_requests_and_collects_ga_audio(self):
        pcm = bytes(BYTES_PER_SECOND // 10)
        socket = Socket([
            {"type": "response.output_audio.delta", "delta": base64.b64encode(pcm).decode()},
            {"type": "response.done", "response": {"status": "completed"}},
        ])
        self.assertEqual(await exchange(Session(socket), pcm), pcm)
        self.assertEqual([x["type"] for x in socket.sent], [
            "input_audio_buffer.append", "input_audio_buffer.commit", "response.create",
        ])
        self.assertEqual(base64.b64decode(socket.sent[0]["audio"]), pcm)

    async def test_service_error_raises_without_echoing_payload(self):
        session = Session(Socket([{"type": "error", "error": {"type": "invalid_request_error", "message": "PRIVATE"}}]))
        with self.assertRaises(RealtimeError) as error:
            await session.receive()
        self.assertNotIn("PRIVATE", str(error.exception))

    async def test_failed_cancelled_and_empty_responses_are_not_success(self):
        for status in ("failed", "incomplete", "cancelled", "completed"):
            with self.subTest(status=status):
                socket = Socket([{"type": "response.done", "response": {"status": status}}])
                with self.assertRaises(RealtimeError):
                    await exchange(Session(socket), bytes(4800))

    async def test_receive_is_bounded_by_exchange_deadline(self):
        class HangingSocket(Socket):
            async def recv(self):
                await asyncio.sleep(10)
        with self.assertRaises(TimeoutError):
            await exchange(Session(HangingSocket([])), bytes(4800), timeout=0.01)

    async def test_connection_lifecycle_over_local_websocket_not_azure(self):
        from websockets.asyncio.client import connect as real_connect
        from websockets.asyncio.server import serve

        received = []
        pcm = b"\x01\x02" * 2400

        async def service(socket):
            self.assertEqual(socket.request.headers["api-key"], "offline-test-key")
            await socket.send(json.dumps({"type": "session.created"}))
            received.append(json.loads(await socket.recv()))
            await socket.send(json.dumps({"type": "session.updated"}))
            for _ in range(3):
                received.append(json.loads(await socket.recv()))
            await socket.send(json.dumps({
                "type": "response.output_audio.delta",
                "delta": base64.b64encode(pcm).decode(),
            }))
            await socket.send(json.dumps({"type": "response.done", "response": {"status": "completed"}}))
            await socket.wait_closed()

        async with serve(service, "127.0.0.1", 0) as server:
            port = server.sockets[0].getsockname()[1]

            def redirect(url, **kwargs):
                self.assertEqual(url, "wss://example.openai.azure.com/openai/v1/realtime?model=voice")
                return real_connect(f"ws://127.0.0.1:{port}", **kwargs)

            async with asyncio.timeout(5):
                with patch("websockets.asyncio.client.connect", redirect):
                    async with connect(Settings("https://example.openai.azure.com", "voice", "offline-test-key"), "brief") as session:
                        self.assertEqual(await exchange(session, pcm), pcm)
        self.assertEqual([event["type"] for event in received], [
            "session.update", "input_audio_buffer.append",
            "input_audio_buffer.commit", "response.create",
        ])

    async def test_duplex_interrupts_and_closes_audio_streams(self):
        class Stream:
            def __init__(self):
                self.closed = False

            def __enter__(self):
                return self

            def __exit__(self, *args):
                self.closed = True

            def read(self, frames):
                import time
                time.sleep(0.02)
                return bytes(frames * 2), False

            def write(self, data):
                import time
                time.sleep(0.02)
                return False

        class ConversationSocket(Socket):
            async def recv(self):
                try:
                    return json.dumps(next(self.events))
                except StopIteration:
                    await asyncio.sleep(10)

        input_stream, output_stream = Stream(), Stream()
        socket = ConversationSocket([
            {"type": "response.output_audio.delta", "item_id": "one", "content_index": 0, "delta": base64.b64encode(bytes(9600)).decode()},
            {"type": "input_audio_buffer.speech_started"},
            {"type": "response.done", "response": {"status": "cancelled"}},
        ])
        with patch("sounddevice.RawInputStream", return_value=input_stream), patch("sounddevice.RawOutputStream", return_value=output_stream):
            await converse(Session(socket), seconds=1)
        self.assertTrue(input_stream.closed)
        self.assertTrue(output_stream.closed)
        truncations = [event for event in socket.sent if event["type"] == "conversation.item.truncate"]
        self.assertEqual(len(truncations), 1)
        self.assertEqual(truncations[0]["item_id"], "one")


class AudioTests(unittest.TestCase):
    def test_interruption_truncates_played_not_received_audio_and_drops_late_chunks(self):
        playback = Playback()
        event = {"item_id": "one", "content_index": 0, "delta": base64.b64encode(b"\x01\x02" * 4800).decode()}
        playback.append(event)
        self.assertEqual(playback.take(4800), b"\x01\x02" * 2400)
        self.assertEqual(playback.interrupt(), {"item_id": "one", "content_index": 0, "audio_end_ms": 100})
        playback.append(event)
        self.assertEqual(playback.take(960), bytes(960))
        playback.append({**event, "item_id": "two"})
        self.assertEqual(len(playback.pending), 9600)

    def test_wav_has_required_format_and_exact_frame_count(self):
        pcm = bytes(4800)
        with wave.open(io.BytesIO(wav_bytes(pcm))) as audio:
            self.assertEqual((audio.getframerate(), audio.getnchannels(), audio.getsampwidth()), (24000, 1, 2))
            self.assertEqual(audio.readframes(2400), pcm)
        for invalid in (b"", b"x", bytes(4800000)):
            with self.assertRaises(ValueError):
                validate_pcm(invalid)

    def test_endpoint_validation_and_deployment_encoding(self):
        self.assertTrue(Settings("https://example.openai.azure.com", "voice /one").url.endswith("model=voice+%2Fone"))
        for endpoint in ("http://example.openai.azure.com", "https://evil.example", "https://example.openai.azure.com/openai/v1", "https://user:secret@example.openai.azure.com"):
            with self.subTest(endpoint=endpoint), self.assertRaises(ValueError):
                _ = Settings(endpoint, "voice").url
        self.assertNotIn("secret", repr(Settings("https://example.openai.azure.com", "voice", "secret")))

    def test_manual_and_server_vad_use_ga_schema(self):
        self.assertIsNone(session_config("brief")["audio"]["input"]["turn_detection"])
        vad = session_config("brief", 500)["audio"]["input"]["turn_detection"]
        self.assertTrue(vad["interrupt_response"])
        self.assertTrue(vad["create_response"])
        with self.assertRaises(ValueError):
            session_config("brief", 0)


if __name__ == "__main__":
    unittest.main()
