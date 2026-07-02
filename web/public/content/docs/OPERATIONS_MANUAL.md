# Aetheris Operations Manual

This operations manual details the procedures for executing, maintaining, and monitoring the Aetheris Kernel in a production environment.

## 1. Running the Core Kernel Loop
To launch the Aetheris core loop:
```bash
$env:PYTHONPATH="src"
python src/kernel/core.py --goal "Build database schema migrations and user authentication routes."
```

## 2. Monitoring & Logging
* **Standard Logs:** Console output redirects standard step events.
* **Audit Trails:** Security and tenant authorizations are appended to [audit_trail.log](file:///c:/AI/Agency%20owner/aetheris/.aetheris/audit_trail.log).
* **Metrics Dashboard:** Overall throughput and token counters are stored in [runtime.json](file:///c:/AI/Agency%20owner/aetheris/.aetheris/runtime.json).
