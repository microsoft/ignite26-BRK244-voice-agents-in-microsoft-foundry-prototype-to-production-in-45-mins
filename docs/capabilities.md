# Capability boundaries

## Implemented foundation

The local Python notebook kernel connects directly over TLS WebSocket to the
GA Azure OpenAI `/openai/v1/realtime?model=<deployment>` endpoint.
It sends signed 16-bit little-endian mono PCM at 24 kHz. A configured
conversation-capable realtime deployment is required. The implementation uses
the documented GA nested `audio.input`/`audio.output` session schema and
`response.output_audio.delta` events, not preview API schemas.

Notebook 01 records one utterance, commits it manually, explicitly requests a
response, and returns audio for listening. Notebook 02 streams microphone input
and output, uses server VAD to cancel generation, clears its local queued audio,
and sends `conversation.item.truncate` at the PCM submitted to the output device.
Device buffering means the truncation boundary is approximate; already submitted
audio can leave a short audible tail. Notebook 03 compares separate English,
Spanish, and mixed-language utterances in fresh sessions with synthetic prompts.

Session/event logs contain event names and client-relative arrival times only,
not raw service payloads, transcripts, keys, or audio. These offsets are not a
latency benchmark. Returned response audio remains in memory and becomes embedded
in a notebook if an audio-widget output is saved. Clear outputs before sharing.

## Service support versus sample support

Official documentation currently lists multiple realtime models and deployment
regions; verify current model/version/region availability and quota for your own
resource. A deployment name is not necessarily the model name. Dedicated
transcription/translation models are not interchangeable with these
conversation-style exercises. Input transcription is not configured, so no
additional transcription model deployment is assumed.

The exercises deliberately use server VAD only. They do not promise semantic VAD,
custom pronunciation, language accuracy, multimodal input, cloud-to-edge
execution, echo cancellation, reconnection, tool execution, routing, escalation,
production monitoring, or automated evaluation. Prompted language behavior must
be judged from actual audio. None of those optional capabilities is silently
represented by mock success.

WebSockets suit a kernel-based teaching client; official guidance recommends
WebRTC for browser/mobile low-latency media. This notebook is not a browser audio
implementation, does not mint browser credentials, and does not send microphone
audio from the browser to a remote kernel.

## Validation boundary

Offline tests exercise protocol ordering, GA event handling, error propagation,
timeouts, audio formatting, interruption buffer/truncation logic, and notebook
structure. Fake sockets are test fixtures only; live helpers have no mock mode.
An authenticated Azure run, actual device playback, interruption quality, and
language behavior must still be validated on the authorized deployment and
attendee hardware. No paid resources are provisioned by this repository.

## Official references

Reviewed on November 13, 2026:

- [Azure realtime overview, models, API support, and VAD](https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/realtime-audio)
- [Azure WebSocket quickstart and GA Python session configuration](https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/realtime-audio-websockets)
- [Azure realtime reference and Azure-specific transcription deviations](https://learn.microsoft.com/en-us/azure/foundry/openai/realtime-audio-reference)
- [GA client events, server VAD interruption, and conversation truncation](https://developers.openai.com/api/reference/resources/realtime/client-events)
- [Current Azure model and region availability](https://learn.microsoft.com/en-us/azure/foundry/foundry-models/concepts/models-sold-directly-by-azure-region-availability)

Documentation establishes the target contract, not evidence that a specific
subscription, region, deployment, or microphone has been tested.
