# Engineering Team Assignment: Third-Party Engine Integration (v4.0)

This document assigns roles, skills, and specification domains for developing the integration of Headroom, Claude Code, and Claude Code Templates.

## Roles & Assignments

| Role | Mapped Skills | Governing RFC / SPEC | Responsibility |
|---|---|---|---|
| **Product Manager** | `aetheris-product-intelligence` | SPEC-124 | Define template conversion rules, target state configurations, and visual branding standards. |
| **Solution Architect** | `aetheris-kernel` | SPEC-123 | Design the modular adapter interface structures under `src/aetheris/adapters/`. |
| **Backend & Integration Engineer** | `agency-backend-architect` | SPEC-126, SPEC-066 | Develop `template_adapter.py` and `agent_runtime.py`. |
| **Proxy & Optimization Architect** | `aetheris-context-engine` | SPEC-128, SPEC-076 | Develop `proxy_adapter.py` and integrate it into `KernelController`. |
| **UI/UX Designer** | `agency-ui-designer` | SPEC-133 | Define theme tokens in `src/config/theme_contract.json` to ensure clean minimal styling. |
| **QA / Verification Engineer** | `aetheris-verification-engine` | SPEC-131 | Verify file mapping accuracy, subprocess wrapping safety, and compression rules compliance. |

## Department Mobilization

The following departments are mobilized:
- **Engineering / Backend**: For subprocess wrapping, path resolution, and filesystem automation.
- **Engineering / DevOps**: For configuring proxy daemon lifecycles and port settings.
- **Design / UI/UX**: For establishing visual themes.
- **Quality Assurance**: For writing unit verification tests.
