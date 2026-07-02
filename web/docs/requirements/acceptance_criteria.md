# Aetheris Platform — Acceptance Criteria

## AC-1: Dynamic Scanner Validation
* **Given** a division directory with a new agent markdown file containing YAML frontmatter.
* **When** `compile_repo.py` is executed.
* **Then** the script must output a `data.json` containing the new agent in the skills registry, and copy the markdown file to `public/content/skills/`.

## AC-2: Sidebar Specification Navigation
* **Given** 170 specifications on disk in the `rfcs/` folder.
* **When** the Specifications tab is opened in the browser.
* **Then** all 170 SPECs must be listed in alphabetical order in the sidebar, and clicking a SPEC must dynamically fetch and render its content without full page reload.

## AC-3: Full-Text Command Search
* **Given** the global search index generated in `data.json`.
* **When** `Ctrl+K` is pressed.
* **Then** the search modal must open and inputting a keyword must filter matching skills, specs, RFCs, and documents instantly.

## AC-4: Interactive Graph Map
* **Given** the relationships map generated in the database.
* **When** a subsystem RFC is selected in the Graph tab dropdown.
* **Then** the SVG canvas must only render the selected RFC node and its primary and secondary connected nodes, drawing directed bezier links.
