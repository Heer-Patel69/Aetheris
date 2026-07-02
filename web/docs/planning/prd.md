# Product Requirements Document — Aetheris Web platform

## 1. Product Goals
* Turn Aetheris from a "static-feeling website" into a **living reflection of the repository**.
* Create a robust, premium Jamstack platform that scans the workspace in a python compiler and renders dynamically on Vite + React.
* Provide an Apple-class storytelling and Stripe-class developer experience.

## 2. Technical Stack
* **Metadata Parser**: Python 3 (standard libraries: `os`, `json`, `zipfile`, `pathlib`, `re` + `pyyaml` dependency).
* **Frontend SPA**: React 19, TypeScript, Vite 8, Vanilla CSS.
* **Icons**: `lucide-react`.

## 3. UI/UX Structure
1. **Interactive Hero**: Booting status terminal showing active logs.
2. **Scroll Storytelling**: High-impact vertical presentation of the Aetheris timeline.
3. **Skills Marketplace**: Search grid with categories and detail view.
4. **Specification Hub**: left sidebar navigator for all 170 SPECs.
5. **Graph Viewer**: Node-link subsystem map.
6. **Command search menu**: Instant full-text search overlay.

## 4. Key Performance Indicators (KPIs)
* **First Contentful Paint (FCP)**: < 200ms (fast static load).
* **Search Search Speed**: < 10ms (pure client-side match).
* **Hot Reload Compilation**: < 500ms on workspace file edits.
