# Engineering Team Assignment: Cryptographic Web-Hook Validator Microservice

This document assigns roles, skills, and specification domains for developing the validation microservice.

## Roles & Assignments

| Role | Mapped Skills | Governing RFC / SPEC | Responsibility |
|---|---|---|---|
| **Product Manager** | `aetheris-product-intelligence` | SPEC-124 | Define webhook payload parameters, rate-limit thresholds, and dashboard display criteria. |
| **Solution Architect** | `aetheris-kernel` | SPEC-123 | Design the SQLite database schema and REST API endpoints. |
| **Backend & Database Engineer** | `agency-backend-architect` | SPEC-126, SPEC-103 | Implement the database mappings, connection handling, and indices. |
| **Cybersecurity Engineer** | `agency-application-security-engineer` | SPEC-130, SPEC-111 | Implement HMAC-SHA256 signature verification and timing-attack-safe comparisons. |
| **UI/UX Designer** | `agency-ui-designer` | SPEC-133 | Style the telemetry dashboard using the tokens defined in `src/config/theme_contract.json`. |
| **QA / Verification Engineer** | `aetheris-verification-engine` | SPEC-131 | Run integration stress tests to verify rate-limiting and timing-safety. |

## Department Mobilization

- **Engineering / Backend**: SQLite database modeling and FastAPI routing.
- **Security**: Timing-attack safe cryptographic validation.
- **Design**: Branded status view implementation.
- **Quality Assurance**: Automated validation test scripting.
