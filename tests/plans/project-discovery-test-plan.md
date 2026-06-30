# Test Plan: Project Discovery Engine

## 1. Scope
This test plan covers repository traversal limits, stack detection accuracy, fingerprint calculation, and empty folder handling.

## 2. Test Cases

### 2.1 — Stack Detection Accuracy (Pass)
- **Condition**: Run discovery scan on a mock React + Supabase project.
- **Expected Outcome**: Scanner detects language (TypeScript), frameworks (React, Vite, Supabase), and configuration conventions correctly.

### 2.2 — Depth Limitation (Pass)
- **Condition**: Run scanner on a workspace containing deep nested subdirectories (>5 levels).
- **Expected Outcome**: Traversal terminates at level 2. Execution completes without timeout, logging partial directory list where appropriate.

### 2.3 — Empty Workspace Handling (Edge Case)
- **Condition**: Run scanner on an empty directory.
- **Expected Outcome**: Scanner returns "no stack indicators found", registers profile as empty, and finishes without exception.

### 2.4 — Secret Redaction (Security)
- **Condition**: Scan a configuration file that contains a mock database password.
- **Expected Outcome**: Profile output contains the config fields, but the password value is redacted (e.g. replaced with `<REDACTED>`).

## 3. Performance Benchmarks
- Full repository scans must complete in **<2 seconds** for a codebase of 5,000 files.
- Fingerprint hashing of key config files must complete in **<100ms**.

## 4. Security Validation Scenarios
- Verify that the scanner script (`scanner.py`) does not read `.env` files.
- Test that scanner path arguments are checked against directory traversal vulnerabilities.
