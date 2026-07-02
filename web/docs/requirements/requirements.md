# Aetheris Platform — Functional & Non-Functional Requirements

## 1. Functional Requirements
* **FR-1 (Dynamic Scanning)**: The system must dynamically sweep the workspace at startup and in a live loop to find all division folders (`divisions.json`) and core skills (`aetheris/skills`), extracting all metadata without any hardcoded registry lists.
* **FR-2 (Ecosystem Parser)**: The system must parse RFC and SPEC files, automatically identifying titles, headers, status, goals, inputs/outputs, and Definition of Done sections.
* **FR-3 (Relational Linking)**: The system must detect `RFC-XXX` and `SPEC-XXX` tokens in files, building a bi-directional network graph representing dependencies.
* **FR-4 (Documentation Engine)**: The platform must parse markdown on the client side, rewriting relative references (e.g. `[link](SPEC-040.md)`) into route navigation elements.
* **FR-5 (Full-Text Search)**: The search bar must index all titles, subtitles, tags, and full text to allow instantaneous client-side keyword matches.
* **FR-6 (Multi-Format Downloads)**: Each skill must automatically generate downloads in MD, JSON, YAML, and ZIP formats.
* **FR-7 (Live Hero Monitor)**: The homepage hero must show a rolling terminal animation simulating live Aetheris kernel operations and execution phases.
* **FR-8 (Scroll Storytelling)**: The platform must present an Apple-style storytelling view explaining the core values of Aetheris (Chapters 1 to 9).

## 2. Non-Functional Requirements
* **NFR-1 (Performance)**: Client search and tab navigation latency must be under 50ms.
* **NFR-2 (Zero Backend)**: The web platform must be Jamstack/Static, loading all repository state from a single pre-compiled JSON database.
* **NFR-3 (Developer Experience)**: Provide a live watcher loop (`dev.py`) that instantly recompiles data on workspace edits.
* **NFR-4 (Visuals)**: Sleek dark-mode aesthetic with custom Inter typography, neon accents, and smooth glow cards.
