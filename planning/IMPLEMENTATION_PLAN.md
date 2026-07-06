# Refined Implementation Plan — Third-Party Engine Integration (v4.0)

Build a production-grade, modular adapter infrastructure under `src/aetheris/adapters/` to integrate Headroom, Claude Code runtime, and the Claude Code Template system (ECC) directly into Aetheris, excluding Ponytail.

## Ingestion Mapping Matrix

| Source Path | Target Aetheris Path | Classification type |
| --- | --- | --- |
| `third party/ECC-main/ECC-main/skills/` | `skills/third_party/claude_templates/` | **Engineering Capability Skills** |
| `third party/ECC-main/ECC-main/AGENTS.md` | `rfcs/third_party/AGENTS.md` | **Structural Rule Contract** |
| `third party/ECC-main/ECC-main/CLAUDE.md` | `rfcs/third_party/CLAUDE.md` | **Structural Rule Contract** |
| `third party/ECC-main/ECC-main/RULES.md` | `rfcs/third_party/RULES.md` | **Governance Law** |

## Proposed Changes

### Component: Ingestion & Skill Translation
#### [NEW] [template_adapter.py](file:///c:/AI/Aehteris%20main/aetheris/src/aetheris/adapters/template_adapter.py)
Programmatically parses and maps third-party skills and global templates (ECC) into valid Aetheris Skills under `skills/third_party/claude_templates/` and RFC standards under `rfcs/third_party/`.

#### [MODIFY] [repository.py](file:///c:/AI/Aehteris%20main/aetheris/src/aetheris/intelligence/repository.py)
Hooks the dynamic scan pipeline to trigger the template parser before crawling files.

#### [MODIFY] [wde.py](file:///c:/AI/Aehteris%20main/aetheris/src/intelligence/wde.py)
Hooks the kernel discovery scanner to trigger template parser updates.

---

### Component: Runtime Execution & State Control
#### [NEW] [agent_runtime.py](file:///c:/AI/Aehteris%20main/aetheris/src/aetheris/adapters/agent_runtime.py)
Implements an asynchronous subprocess wrapper around the Claude Code CLI. Reads `.aetheris/ENGINEERING_MANIFEST.json` and injects state configurations as stateless environment configurations/inputs before invocation.

---

### Component: Telemetry & Traffic Compression Proxy
#### [NEW] [proxy_adapter.py](file:///c:/AI/Aehteris%20main/aetheris/src/aetheris/adapters/proxy_adapter.py)
Manages the Headroom proxy server daemon lifecycle and configures outbound redirection to `http://localhost:8787`. Enforces SmartCrusher compression on logs/payloads with 0% compression on raw source code files.

#### [MODIFY] [core.py](file:///c:/AI/Aehteris%20main/aetheris/src/aetheris/kernel/core.py)
Integrates Headroom daemon lifecycle management into `KernelController`.

---

### Component: Theme Configuration
#### [NEW] [theme_contract.json](file:///c:/AI/Aehteris%20main/aetheris/src/config/theme_contract.json)
Maps design token colors and assets to a clean, high-contrast, minimal luxury monochromatic visual style.

---

## Verification Plan

### Automated Tests
- Build and execute unit tests checking the template scanning logic, mapping parsing accuracy, subprocess state injection, and proxy daemon control.

### Manual Verification
- Execute `aetheris analyze` and ensure that the ingested third-party skills show up correctly in the CLI matrix.
- Launch the Aetheris daemon using `aetheris start` and verify that the Headroom proxy process starts successfully.
