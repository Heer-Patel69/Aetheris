# Dead Code Report

A sweep of the codebase was performed to identify unused classes, functions, or modules.

## Dead Modules
- No dead modules were found. Every file under `src/` is imported by at least one other module or active unit test file.

## Dead Classes / Functions
- `src/intelligence/technology.py` -> `TechnologyAssessor` is imported but has no active calls in the core planner loops.
- `src/intelligence/blueprint.py` -> `SystemBlueprint` is parsed during planning stages but has no downstream consumption.
