# Aetheris Maintenance Guide

This document lists routine maintenance tasks for Aetheris system administrators.

## 1. Log Rotation & Purging
* **Telemetry logs:** Telemetry records in `.aetheris/telemetry/` should be compressed monthly.
* **Audit logs:** Rotate `.aetheris/audit_trail.log` every 10MB of writes.

## 2. Test Verification Runs
Run the complete regression suite after any platform patch:
```bash
$env:PYTHONPATH="src"
python -m unittest discover -s tests
```
