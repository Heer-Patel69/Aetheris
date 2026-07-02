# Aetheris Platform — Engineering Execution Plan

## Phase 1: Environment Bootstrapping
* Create self-contained folder structure `aetheris/web/`.
* Initialize React + Vite + TypeScript.
* Install node modules (`npm install`, `lucide-react`).

## Phase 2: Compiler Development
* Write `compile_repo.py` to parse skills, RFCs, SPECs, docs, and build `data.json`.
* Write ZIP, JSON, YAML package generators.
* Write `dev.py` polling watcher script for local development.

## Phase 3: Core UI Development
* Write custom Markdown renderer `DocRenderer.tsx` and link-rewriter.
* Implement Homepage Hero rolling monitor.
* Implement scroll storytelling.
* Implement search shortcut command panel.

## Phase 4: Tab Views Integration
* Implement Skills Marketplace grid, category filters, and download links.
* Implement SPEC Hub sidebar showing 170 specifications.
* Implement RFC explorer grid.
* Implement SVG node-link dependency graph.

## Phase 5: Verification & Audit
* Implement unit tests for parser (`test_compile_repo.py`).
* Verify build commands compile with zero TypeScript/CSS errors.
