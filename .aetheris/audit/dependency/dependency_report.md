# Dependency Report

This report details imports, dependency layers, and architectural violations.

## Circular Dependencies
- **No Circular Imports Detected:** Pyright audits and static code graph sweeps confirm that the import structure is strictly directed.
- **Import Layering Rules:** `kernel` modules import `intelligence` and `execution` modules. `intelligence` and `execution` do not import `kernel` modules. This ensures clean boundary layers.

## Boundary Violations
- **Strict Separation:** `execution` engines do not communicate directly. They exchange data through EKB registrations or events.
