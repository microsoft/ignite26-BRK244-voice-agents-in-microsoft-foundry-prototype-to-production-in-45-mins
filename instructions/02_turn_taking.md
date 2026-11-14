# Turn-taking and barge-in

Open [notebook 02](../src/notebooks/02_turn_taking_and_barge_in.ipynb).
Run setup and the 25-second conversation cell. Repeat with `silence_ms = 1000`
instead of `500` to compare tolerance for mid-sentence pauses.

## Exercise objective

Compare supported speech-boundary configuration and observe what happens when
new speech arrives during an assistant response. Use only options documented for
the selected API and deployment; semantic turn detection is not assumed.

Ask for a lengthy explanation of the water cycle, then interrupt with:
"Stop. Give me a one-sentence summary instead."

## Record your observations

Record speech-start and speech-stop events, response cancellation, and audible
playback behavior separately. Stopping generation does not by itself clear audio
already buffered for playback. A prerecorded input or local event simulation
cannot establish that microphone barge-in works.

Continue to [multilingual conversations](03_multilingual.md), or return to the
[attendee path](README.md).
