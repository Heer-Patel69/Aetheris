# Software Architecture

## Overview
A decoupled architecture with a Python-based telemetry collector and a React-based frontend.
- **Frontend**: Vite + React
- **Backend/Middleware**: Python FastAPI or similar async server providing WebSocket streams.
- **Data Source**: `.aetheris/` state directory and Event Bus.