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

## What needs to be deployed

Notebooks 01–03 share **one Azure resource and one conversation-capable realtime
model deployment**. Reuse an existing authorized resource and deployment when
possible; each notebook opens its own session on that deployment.

| Requirement | What to prepare |
|-------------|-----------------|
| Azure subscription | Permission to use the resource and sufficient realtime model quota |
| Azure OpenAI or Microsoft Foundry resource | A resource exposing an Azure OpenAI endpoint such as `https://your-resource.openai.azure.com` |
| Realtime model deployment | A conversation-capable GPT realtime model, such as `gpt-realtime` or `gpt-realtime-mini`, where currently available |
| Inference access | **Cognitive Services OpenAI User** on the resource for the identity used by the local kernel, or an authorized API key |
| Network access | The kernel machine can reach the resource over TLS WebSocket on port 443 |

These notebooks do **not** require a separate Speech resource, transcription
model deployment, hosted agent, web app, database, search index, or cloud compute
deployment. Python, Jupyter, and audio devices run locally. Tracing/evaluation
infrastructure is not a prerequisite for this first increment.

### Prepare the resource and model

Complete this before the session; resource creation, quota approval, and role
assignment can take time.

1. Review the current [realtime model and API support](https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/realtime-audio)
   and [region availability](https://learn.microsoft.com/en-us/azure/foundry/foundry-models/concepts/models-sold-directly-by-azure-region-availability).
   Confirm your subscription has quota for the chosen conversation model and
   deployment type. Do not select a transcription-only or translation-only model.
2. In the [Foundry portal](https://ai.azure.com/), select your existing project
   and resource. If you have no suitable resource, ask your subscription
   administrator to create an Azure OpenAI or Microsoft Foundry resource in a
   supported region using the
   [official resource setup guidance](https://learn.microsoft.com/en-us/azure/ai-services/multi-service-resource?pivots=azportal).
   Creating resources and assigning access require permissions separate from
   permission to call an existing model.
3. Open **Models + endpoints** or **Deployments**, depending on the portal view.
   Choose **Deploy model** and select a conversation-capable realtime model.
   Review the model version, deployment type, region, quota, and pricing before
   confirming. Record the deployment name you choose; it can differ from the
   underlying model name. Wait until deployment succeeds.
4. Ask the resource administrator to grant your identity
   **Cognitive Services OpenAI User** on that resource for recommended keyless
   access. If using a key instead, obtain it securely from the resource's
   **Keys and Endpoint** page; do not share it in notebook outputs or commits.
5. From **Keys and Endpoint**, copy the resource's Azure OpenAI endpoint, and
   map it and the deployment name to `.env` as shown below. Do not use a Foundry
   project endpoint, append `/openai/v1`, or add an API version.
6. Confirm that resource firewall/private-network settings allow your local
   kernel to connect. If your organization requires a VPN or private network,
   use that approved path; do not disable network policies for the exercise.

For the detailed portal walkthrough, see the
[official realtime WebSocket quickstart](https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/realtime-audio-websockets#deploy-a-model-for-real-time-audio).
Availability in documentation is not proof of quota or access in your subscription.

### Map the deployment to local configuration

Copy [.env.example](../.env.example) to `.env` at the repository root.

| Local variable | Where its value comes from |
|----------------|----------------------------|
| `AZURE_OPENAI_ENDPOINT` | Resource **Keys and Endpoint**; use the HTTPS resource root ending in `.openai.azure.com` |
| `AZURE_OPENAI_DEPLOYMENT_NAME` | The exact deployment name chosen in the portal, not an assumed model name |
| `AZURE_OPENAI_API_KEY` | Leave empty for Microsoft Entra ID; otherwise use the resource key locally |

The helper builds the GA WebSocket URL from those values. No additional
transcription deployment, API-version variable, or service URL is needed.

### Check readiness and control cost

Before opening the notebooks, confirm that the deployment reports success, the
local identity has inference access, the kernel can reach the resource, and the
microphone/output devices pass the checks below. Notebook 01 provides the first
actual connection and audio exchange; only that live run can verify the full path.

Review current [Azure OpenAI pricing](https://azure.microsoft.com/en-us/pricing/details/cognitive-services/openai-service/)
and your subscription's budget with the resource owner before deploying or running
exercises. Budget alerts are not a hard spending cap. The 25-second conversation
limit bounds a notebook run, not total subscription spend.

After the session, close notebook sessions and the Jupyter process. If you created
a dedicated deployment/resource only for this exercise, remove it when no longer
needed with the resource owner's approval. Do not delete shared resources.

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
