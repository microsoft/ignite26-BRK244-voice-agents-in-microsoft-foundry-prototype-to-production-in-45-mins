# Source

<!-- IGNITE TEMPLATE PLACEHOLDER: remove this folder when the session needs no source files. -->

Run [notebooks 01–03](../instructions/README.md) with a local Python kernel.
Reusable GA realtime session and audio logic lives in [shared/realtime.py](shared/realtime.py).
These educational samples are not a production client or a deployment template.

Run focused, offline checks from the repository root:

```shell
python -m unittest discover -s tests -v
```

Protocol tests use explicitly fake sockets. They do not authenticate to Azure,
capture microphone audio, prove model availability, or score speech quality.
