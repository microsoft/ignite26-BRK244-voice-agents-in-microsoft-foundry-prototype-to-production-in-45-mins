# Quickstart voice session

Open [notebook 01](../src/notebooks/01_quickstart_voice_session.ipynb).
Run the setup cell and then the voice cell. Speak during the five-second recording
and press Play on the returned audio widget.

## Exercise objective

Connect to an authorized realtime audio deployment, submit a neutral synthetic
utterance, and listen to the service response. Inspect session configuration and
received event types without printing secrets or retaining raw audio by default.

Suggested utterance: "Explain how a rainbow forms in two short sentences."

## Record your observations

Distinguish successful connection, accepted input, received response audio, and
completed response. A connection alone is not evidence that the full voice
exchange succeeded. Record errors explicitly and close the connection afterward.

Continue to [turn-taking](02_turn_taking.md), or return to the
[attendee path](README.md).
