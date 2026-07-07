# Orphan Report

This report identifies orphan assets (files that exist but are not referenced or integrated anywhere).

## Orphan Specifications
- No orphan specifications exist. Every SPEC from SPEC-001 to SPEC-170 is listed and linked inside its respective RFC index file.

## Orphan Code Modules
- `src/validation/readiness.py`: Not imported by any core kernel module. Used only by pre-flight check scripts.
- `src/adapters/`: Folders are currently empty except for `__init__.py`.
