# Backend Architecture

## Components
- **Telemetry Server**: Subscribes to the Aetheris Event Bus.
- **Log Reader**: Tails and parses `.aetheris/telemetry/` and `.aetheris/runtime/`.
- **WebSocket Broadcaster**: Pushes typed events to connected clients.