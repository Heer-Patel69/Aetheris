# Aetheris Kernel — Tasks

**Version**: 2.1.0
**Target Phase**: PRODUCTION READY (Active Global Runtime)

---

## 🔴 Priority 1 — Phase 7: Installation & Diagnostics (COMPLETE)

- [x] Preflight checks passing
- [x] Transactional backup & restore logic implemented in `install.py`
- [x] Global runtime directory initialized at `~/.aetheris/`
- [x] 7 global skills deployed to `~/.gemini/config/skills/`
- [x] Activation rules injected to `~/.gemini/config/AGENTS.md`
- [x] Diagnostic suite `doctor.py` fully validated and healthy

---

## 🟡 Priority 2 — Phase 6: Integration (COMPLETE)

- [x] Inter-module Event Bus dispatch integrated
- [x] Global CLI wrappers deployed
- [x] Workspace fingerprint validation tested

---

## 🔵 Priority 3 — Phase 5: Implementation (COMPLETE)

- [x] 5a — Configuration Manager (`src/config.py`)
- [x] 5b — Telemetry Engine (`src/telemetry.py`)
- [x] 5c — Event Bus (`src/event_bus.py`)
- [x] 5d — Memory Engine (`src/memory.py`)
- [x] 5e — Project Discovery Engine (`src/scanner.py`)
- [x] 5f — Context Engine (`src/context.py`)
- [x] 5g — Planner (`skills/aetheris-product-intelligence/`)
- [x] 5h — Resource Router (`skills/aetheris-skill-orchestrator/`, `config/`)
- [x] 5i — Verification Engine (`skills/aetheris-verification-engine/`)
- [x] 5j — Plugin Manager (`src/plugins.py`)
- [x] 5k — Kernel (`skills/aetheris-kernel/`)

---

## 🟢 Priority 4 — Phase 4: Test Plans (COMPLETE)

- [x] `aetheris/tests/plans/config-manager-test-plan.md`
- [x] `aetheris/tests/plans/telemetry-engine-test-plan.md`
- [x] `aetheris/tests/plans/event-bus-test-plan.md`
- [x] `aetheris/tests/plans/memory-engine-test-plan.md`
- [x] `aetheris/tests/plans/project-discovery-test-plan.md`
- [x] `aetheris/tests/plans/context-engine-test-plan.md`
- [x] `aetheris/tests/plans/planner-test-plan.md`
- [x] `aetheris/tests/plans/resource-router-test-plan.md`
- [x] `aetheris/tests/plans/verification-engine-test-plan.md`
- [x] `aetheris/tests/plans/plugin-manager-test-plan.md`
- [x] `aetheris/tests/plans/kernel-test-plan.md`

---

## 🟣 Priority 5 — Phase 3: Configuration Schemas (COMPLETE)

- [x] `aetheris/schemas/brain.schema.json`
- [x] `aetheris/schemas/models.schema.json`
- [x] `aetheris/schemas/specialists.schema.json`
- [x] `aetheris/schemas/gates.schema.json`
- [x] `aetheris/schemas/costs.schema.json`
- [x] `aetheris/schemas/plugins.schema.json`

---

## 🟤 Priority 6 — Phase 2: Module Contracts (COMPLETE)

- [x] `aetheris/contracts/config-manager.md`
- [x] `aetheris/contracts/telemetry-engine.md`
- [x] `aetheris/contracts/event-bus.md`
- [x] `aetheris/contracts/memory-engine.md`
- [x] `aetheris/contracts/project-discovery.md`
- [x] `aetheris/contracts/context-engine.md`
- [x] `aetheris/contracts/planner.md`
- [x] `aetheris/contracts/resource-router.md`
- [x] `aetheris/contracts/verification-engine.md`
- [x] `aetheris/contracts/plugin-manager.md`
- [x] `aetheris/contracts/kernel.md`
