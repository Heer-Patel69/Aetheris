# Aetheris Engineering Operating System

```
     _    _____ _____ _   _ _____ ____  ___ ____
    / \  | ____|_   _| | | | ____|  _ \|_ _/ ___|
   / _ \ |  _|   | | | |_| |  _| | |_) || |\___ \
  / ___ \| |___  | | |  _  | |___|  _ < | | ___) |
 /_/   \_\_____| |_| |_| |_|_____|_| \_\___|____/
```

[![Python Version](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)]()
[![Core Engine](https://img.shields.io/badge/core-dynamic%20scanner-magenta.svg)]()

---

## What is Aetheris?

**Aetheris** is an AI Engineering Operating System designed to inject strict architectural discipline, engineering workflows, and deterministic persistence into any LLM runtime engine.

### Core Philosophy: Stateless Reasoning over Stateful Projects
Traditional AI coding assistants rely heavily on fragile, short-term conversational chat history. Aetheris shifts this paradigm by treating the LLM as a stateless reasoning agent. 

The entire execution state, memory, decisions, and system constraints live directly inside the repository under the hidden `.aetheris/` directory layer. This ensures that the engineering context is version-controlled, fully auditable, and easily shared across multi-agent environments or human developer handoffs.

---

## What Does It Do? (Core Features)

Aetheris powers your development workspace using a highly dynamic, Python-driven CLI core:

* **Dynamic Registry Tracking:** Aetheris automatically crawls the workspace in real time using `.gitignore`-aware file discovery. It scales seamlessly to index a growing matrix of **244 Skills**, **9 RFC engineering laws**, and **170 SPECs execution contracts** without any hardcoded filesystem limits.
* **Context Precision & Optimization (Headroom Integration):** Automatically compiles and token-optimizes prompt payloads. It compresses heavy logs, machine-generated tracebacks, and dense JSON payloads while ensuring your core source code remains completely uncompromised.
* **12-Phase Architectural Lifecycle:** Moves AI code creation away from ad-hoc hacking. The operating system forces the agentic lifecycle to flow strictly through sequential, deliberate phases including: Requirements Analysis, UI/UX Design, DB Schema Definition, Security Hardening, Automated Code Verification, and Telemetry Instrumentation.
* **Global Runtime Routing Engine:** Control background telemetry and process daemons (`aetheris start` and `aetheris stop`). These daemons manage whether the workspace compilation pipeline is actively intercepted and governed by the Aetheris Kernel or routed back cleanly to local native IDE configurations.

---

## Prerequisites

Before installing Aetheris, ensure your system meets the following software stack requirements:

1. **Python Runtime:** Python `>= 3.10` installed globally and registered to your system path.
2. **Package Installer:** `pip` updated to the latest version (`python -m pip install --upgrade pip`).
3. **Version Control:** `git` system binary installed and available on the command line.
4. **System Dependencies:** Internet connectivity (for cloud-based LLM routers) or a running local instance of `Ollama` / `LM Studio` (for completely offline local operations).

---

## Step-by-Step Installation Protocols

Select the installation pathway that fits your deployment needs:

### Pathway A: Local Development Installation (Editable Mode)
For developers actively modifying the Aetheris codebase. Installs the package globally, but links execution to your local workspace so any code changes inside `src/` take effect immediately:

```bash
git clone https://github.com/aetheris/aetheris.git
cd aetheris
pip install -e .
```

### Pathway B: Open-Source Distribution (Direct from GitHub)
For end-users deploying Aetheris globally on a target machine directly from a remote repository:

```bash
pip install git+https://github.com/aetheris/aetheris.git
```

### Pathway C: Compiled Offline Packaging (.whl Wheel Builds)
For closed, offline enterprise environments where external internet access is restricted:

1. **Build the wheel package on an internet-enabled machine:**
   ```bash
   pip install build
   python -m build
   ```
2. **Transfer the compiled wheel file** from `dist/` (e.g. `aetheris-0.1.0-py3-none-any.whl`) to the target machine.
3. **Install the wheel package offline:**
   ```bash
   pip install aetheris-0.1.0-py3-none-any.whl
   ```

---

## Interactive CLI Quick-Start Commands

Use the following CLI commands to manage the Aetheris workspace lifecycle:

| Command | Description |
|:---|:---|
| `aetheris init` | Scaffolds the structural directory layout (`.aetheris/`) in the current folder. |
| `aetheris analyze` | Triggers a real-time, `.gitignore`-aware filesystem crawl and lists registry counts. |
| `aetheris start` | Boots the persistent telemetry proxies and routes coding tasks through the Kernel. |
| `aetheris stop` | Dismantles context daemons and returns execution control back to native IDE settings. |
| `aetheris dashboard` | Exposes the metrics dashboard endpoint (default: `http://localhost:8448`). |
| `aetheris skill [name]` | Inspects and queries capabilities and skills registered in the system. |

---

## Operational State Routing

> [!IMPORTANT]
> Running `aetheris start` spins up background context compression brokers. Once locked onto the system PID, the entire development pipeline is governed by Aetheris Kernel laws, verifying specifications and enforcing RFC compliance.

> [!WARNING]
> Running `aetheris stop` safely detaches the Aetheris control plane. Standard text editor behavior is immediately restored, letting you pass prompts back directly to your local IDE's native LLM configurations without workspace interventions.
