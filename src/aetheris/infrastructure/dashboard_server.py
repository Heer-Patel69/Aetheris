import asyncio
import json
from pathlib import Path
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start background tasks to watch files
    task1 = asyncio.create_task(tail_file(Path(".aetheris/state/runtime.json"), "RUNTIME_UPDATE"))
    task2 = asyncio.create_task(tail_file(Path(".aetheris/execution_state.json"), "EXECUTION_UPDATE"))
    yield
    task1.cancel()
    task2.cancel()

app = FastAPI(title="Aetheris Telemetry Stream", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception:
                pass

manager = ConnectionManager()

async def tail_file(filepath: Path, event_type: str):
    """Poll a file and broadcast its contents when it changes."""
    last_mtime = 0
    while True:
        try:
            if filepath.exists():
                current_mtime = os.path.getmtime(filepath)
                if current_mtime > last_mtime:
                    last_mtime = current_mtime
                    with open(filepath, 'r', encoding='utf-8') as f:
                        try:
                            data = json.load(f)
                            message = json.dumps({"type": event_type, "payload": data})
                            await manager.broadcast(message)
                        except json.JSONDecodeError:
                            # File might be partially written, ignore
                            pass
        except Exception as e:
            pass
        await asyncio.sleep(1)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        # Send initial state
        state_dir = Path(".aetheris/state")
        
        runtime_path = state_dir / "runtime.json"
        if runtime_path.exists():
            with open(runtime_path, 'r', encoding='utf-8') as f:
                try:
                    await websocket.send_text(json.dumps({"type": "RUNTIME_UPDATE", "payload": json.load(f)}))
                except Exception:
                    pass
                    
        execution_path = Path(".aetheris/execution_state.json")
        if execution_path.exists():
            with open(execution_path, 'r', encoding='utf-8') as f:
                try:
                    await websocket.send_text(json.dumps({"type": "EXECUTION_UPDATE", "payload": json.load(f)}))
                except Exception:
                    pass

        while True:
            data = await websocket.receive_text()
            # Handle incoming messages from dashboard if necessary
    except WebSocketDisconnect:
        manager.disconnect(websocket)

def start_server():
    uvicorn.run("aetheris.infrastructure.dashboard_server:app", host="127.0.0.1", port=8449, reload=False)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8449)
