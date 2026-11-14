<a name="start-building"></a>

<p align="center">
<img src="img/banner-ignite-26.png" alt="Microsoft Ignite 2026" width="100%"/>
</p>

# [Microsoft Ignite 2026](https://ignite.microsoft.com)

## 🔥BRK244: Voice agents in Microsoft Foundry: Prototype to production in 45 mins

### Session description

Voice is quickly becoming how people talk to AI agents, but a voice agent that impresses in a demo can struggle with real customers. They interrupt, pause, switch languages and call from noisy places. Voice agents in Microsoft Foundry are now generally available, with new real-time models, built-in handoff between agents, and lifecycle management from the first build to production. In this session, you’ll see how to build a voice agent from a template or with AZD CLI, deploy it to web and phone channels, and use tracing, monitoring and evaluation to keep improving it. You’ll also catch up on the latest Azure Speech launches, then hear from Landis, ASUS and Leapmotor on running voice agents in contact centers, global customer service and the car.

### 🚀 Getting started

#### On your own

Use this repository to revisit the session at your own pace:

1. Clone or browse this repository.
2. Review the session description, learning outcomes, and technologies below.
3. Follow the [attendee instructions](instructions/README.md), starting with
   [Azure deployment and local setup](instructions/00_setup.md).
4. Work through notebooks 01–03 in order, using the step-by-step guidance below.
5. Return for the session slides when they are added.

| Exercise | Step-by-step guidance | Runnable notebook |
|----------|-----------------------|-------------------|
| Quickstart voice session | [Quickstart](instructions/01_quickstart.md) | [Notebook 01](src/notebooks/01_quickstart_voice_session.ipynb) |
| Turn-taking and barge-in | [Turn-taking](instructions/02_turn_taking.md) | [Notebook 02](src/notebooks/02_turn_taking_and_barge_in.ipynb) |
| Multilingual and code-switching | [Multilingual](instructions/03_multilingual.md) | [Notebook 03](src/notebooks/03_multilingual_code_switching.ipynb) |

These product-capability exercises use neutral synthetic material and a local
Python 3.11+ kernel with microphone access. They currently cover the GA Azure
OpenAI realtime WebSocket API, not every technology or scenario presented in the
session. Customer presentations are session content only, not repository demos
or datasets. Tracing/evaluation and optional extensions remain later increments;
live Azure and audio-device behavior still require validation on your deployment.
Review the [capability boundaries](docs/capabilities.md) before connecting.

#### Session materials

Session slides will be added later.

### 🎯 Learning outcomes

By the end of this session, you will be able to:

- Build a production-ready voice agent in Microsoft Foundry: start from one of 40+ templates or with the AZD CLI and GitHub Copilot, choose a real-time model such as GPT-Live-1 or Microsoft Realtime Flash 1, and connect tools, knowledge, memory and guardrails.
- Deploy and operate it with confidence: release versioned agents to web and phone through Teams Phone, other telephony providers or SIP, then use tracing, monitoring and evaluation to find and fix latency and quality issues.
- Apply proven patterns from customers in production: handing off from AI to human agents with context (Landis), multilingual service across countries (ASUS), and voice that works across cloud and edge (Leapmotor).

### 💻 Technologies used

- Microsoft Foundry: Foundry Agent Service (voice agents, prompt and hosted agents), Foundry IQ, Foundry Tools (including MCP tools), guardrails, memory, observability (tracing, evals)
- GenAI models: GPT-Live-1, Microsoft Realtime Flash 1, Azure OpenAI Realtime, GPT-6 series and broader Foundry models
- Azure Speech: real-time and fast transcription (including MAI-Transcribe-2), text to speech, avatar, Live Interpreter API
- Telephony: Microsoft Teams Phone, Azure Communication Services, third-party providers, SIP
- Azure Developer CLI (azd) and GitHub Copilot

### 📚 Continue your learning

Pick your next step based on your learning style:

| Resource | What you'll get |
|----------|-----------------|
| **[Ignite 2026 Next Steps](https://aka.ms/ignite26-next-steps)** | Additional session repos and materials from Microsoft Ignite 2026 |
| **[Microsoft AI Skills Navigator](https://aka.ms/ignite26-asn)** | Discover AI skills, learning paths, and resources for your next step |
| **[Microsoft Learn](https://aka.ms/ignite26-learn)** | Official documentation and guided learning paths on these topics |
| **[Microsoft Foundry Community](https://aka.ms/MicrosoftFoundryDiscord-Ignite26)** | Connect with other learners and experts in our Discord community |

### 🌟 Microsoft Learn MCP Server

The Microsoft Learn MCP Server gives your AI agent direct access to Microsoft's official documentation — grounded, up-to-date answers about the topics in this session.

**GitHub Copilot CLI** — Install with:

```shell
copilot plugin install microsoftdocs/mcp
```

**VS Code** — One-click install:  
[![Install in VS Code](https://img.shields.io/badge/VS_Code-Install_Microsoft_Learn_MCP-0098FF?style=flat-square&logo=visualstudiocode&logoColor=white)](https://vscode.dev/redirect/mcp/install?name=microsoft-learn&config=%7B%22type%22%3A%22http%22%2C%22url%22%3A%22https%3A%2F%2Flearn.microsoft.com%2Fapi%2Fmcp%22%7D)

For more information, visit the [Learn MCP Server repo](https://aka.ms/learnmcp).

### 👥 Content owners

<table>
<tr>
    <td align="center"><a href="https://github.com/gcordido">
        <img src="https://github.com/gcordido.png" width="100px;" alt="Gustavo Cordido"/><br />
        <sub><b>Gustavo Cordido</b></sub></a><br />
            <a href="https://github.com/gcordido" title="talk">📢</a>
    </td>
    <td align="center">
        <sub><b>Irene Du</b></sub><br />
        <code>@toscanet</code>
    </td>
</tr></table>

### ⚖️ Trademarks

This project may contain trademarks or logos for projects, products, or services. Authorized use of Microsoft trademarks or logos is subject to and must follow [Microsoft's Trademark & Brand Guidelines](https://www.microsoft.com/legal/intellectualproperty/trademarks/usage/general). Use of Microsoft trademarks or logos in modified versions of this project must not cause confusion or imply Microsoft sponsorship.

Any use of third-party trademarks or logos are subject to those third-party's policies.
