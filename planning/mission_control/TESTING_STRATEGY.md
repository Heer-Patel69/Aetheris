# Testing Strategy

- **Frontend**: Unit tests for React components. E2E tests using Playwright against live local daemon.
- **Backend**: Pytest for telemetry parsers and WS broadcasters.
- **No Mock Rule**: Tests must run against real, recorded execution journals.