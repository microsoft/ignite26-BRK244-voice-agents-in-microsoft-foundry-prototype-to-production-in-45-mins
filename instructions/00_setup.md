# Setup and service prerequisites

Use Python 3.11 or later with a local Jupyter kernel. The microphone and speaker
belong to the machine running that kernel, not the browser; hosted notebooks,
remote kernels, and Codespaces are not supported audio paths in this increment.

## Before connecting

1. Obtain access to an authorized Microsoft Foundry deployment that supports the
   selected realtime audio API, model, and region.
2. Verify model and regional availability using the current
   [official references and capability boundaries](../docs/capabilities.md).
   Use a conversation-capable realtime deployment, not a transcription-only or
   translation-only model. This implementation uses the GA `/openai/v1/realtime`
   endpoint without an `api-version` query.
3. Confirm permission to incur service charges. This repository does not provision
   paid resources automatically.
4. Use a headset and a private listening environment for microphone exercises.
   Record only neutral synthetic speech with participant consent.

Never paste credentials into notebooks, notebook outputs, screenshots, or commits.
Keep local configuration outside version control. The exercises create fresh
sessions so that conversation history does not affect the next comparison.

## Install and configure

From the repository root, create a virtual environment and install dependencies:

```shell
python3 -m venv .venv
```

Activate it with `source .venv/bin/activate` on macOS/Linux, or
`.venv\Scripts\Activate.ps1` in Windows PowerShell, then run:

```shell
python -m pip install -r requirements.txt
python -m ipykernel install --user --name brk244 --display-name "Python (BRK244)"
python -m notebook
```

Select the **Python (BRK244)** kernel. Copy the root [.env.example](../.env.example)
to a local `.env` and replace the endpoint and deployment examples.
For recommended Microsoft Entra ID authentication, leave the key empty, sign in
with `az login`, and obtain the **Cognitive Services OpenAI User** role on the
resource. `DefaultAzureCredential` also supports other authorized credential
sources. Alternatively, set the API key locally; a nonempty key takes precedence.
The notebook loads `.env` without overriding existing environment variables.

On Linux, `sounddevice` may require the operating system's PortAudio library
(for example, `libportaudio2` on Debian/Ubuntu). Grant microphone permission to
the application running Python. Check the kernel's devices before connecting:

```python
import sounddevice as sd
print(sd.query_devices())
sd.check_input_settings(samplerate=24000, channels=1, dtype="int16")
sd.check_output_settings(samplerate=24000, channels=1, dtype="int16")
```

No automatic device fallback or resampling is implemented. Choose an appropriate
default device in system settings if 24 kHz mono input/output is unavailable.
Use a headset to avoid speaker echo. The recording cells announce when to speak;
they record five seconds and then submit the audio. The barge-in notebook instead
streams both directions for a bounded 25 seconds.

## Troubleshooting

Authentication errors require correcting the local credentials or resource role;
deployment errors require checking the deployment name and supported model/region.
Do not paste raw exception output into public issues if it includes resource
details. Service error payloads are intentionally omitted from the helper's error
messages. Timeouts fail explicitly; retry only after inspecting the cause.

Kernel interruption closes the service connection. Audio device errors fail the
exercise rather than replacing it with a synthetic result. Stop other applications
using the device, confirm permissions, and restart the kernel before retrying.
Clear all cell outputs before saving or sharing: notebook audio widgets embed
recorded/generated content when outputs are saved.

## What counts as evidence

A local fixture or mocked protocol check can validate local logic only. A live
exercise must report a real service connection and actual received events; failed
authentication, unavailable capabilities, and service errors must remain failures,
not silently fall back to simulated success.

Continue to [quickstart](01_quickstart.md), or return to the
[attendee path](README.md).
