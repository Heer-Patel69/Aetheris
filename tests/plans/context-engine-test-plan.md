# Test Plan: Context Engine

## 1. Scope
This test plan covers the intelligent file selection logic, token budget calculations, context compression mechanisms, and path validations.

## 2. Test Cases

### 2.1 — File Selection Relevance (Pass)
- **Condition**: Generate a context package for the task: "Update registration form authentication logic".
- **Expected Outcome**: Context Engine selects `LoginForm.tsx` and `authService.ts`, omitting unrelated stylesheets and configs.

### 2.2 — Context Budget Pruning (Pass / Recovery)
- **Condition**: Set model context limit configuration artificially low (e.g. 5,000 tokens) and request context for a task.
- **Expected Outcome**: Context Engine estimates tokens, catches budget overflow, drops lower priority files, compresses remaining code into interface signatures, and maintains budget constraints.

### 2.3 — Large File Compression (Pass)
- **Condition**: Request context including a source file larger than 100KB.
- **Expected Outcome**: Context Engine strips implementation blocks, extracts only public functions, signatures, and exported types, reducing token size by >70%.

### 2.4 — Secret Scrubbing (Security)
- **Condition**: Generate a context package containing code files with mocked private keys.
- **Expected Outcome**: The output package contents are scanned, the private keys are redacted, and no secrets are sent to the LLM.

## 3. Performance Benchmarks
- Context package generation MUST complete in **<200ms**.
- Token estimation on file contents must complete in **<20ms** per file.

## 4. Security Validation Scenarios
- Attempt to reference files outside the workspace root and verify the Context Engine throws a validation error.
- Verify that binary files and `node_modules` are ignored.
