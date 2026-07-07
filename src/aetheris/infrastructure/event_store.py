import sqlite3
import json
import asyncio
from pathlib import Path
from typing import List, Dict, Any
from aetheris.kernel.event_bus import AetherisEvent, AetherisEventBus

class EventStore:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(EventStore, cls).__new__(cls, *args, **kwargs)
            cls._instance.db_path = Path(".aetheris/telemetry/events.db")
            cls._instance.write_queue = asyncio.Queue()
            cls._instance.is_writing = False
            cls._instance._init_db()
            # Subscribe to the event bus
            AetherisEventBus().subscribe(cls._instance.on_event_published)
        return cls._instance

    def _init_db(self):
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS engineering_events (
            event_id TEXT PRIMARY KEY,
            session_id TEXT NOT NULL,
            project_id TEXT NOT NULL,
            workspace_id TEXT NOT NULL,
            execution_id TEXT,
            timestamp REAL NOT NULL,
            engine TEXT NOT NULL,
            category TEXT NOT NULL,
            severity TEXT NOT NULL,
            payload TEXT NOT NULL,
            duration REAL,
            dependencies TEXT,
            metadata TEXT,
            version INTEGER NOT NULL
        )
        """)
        
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_events_session ON engineering_events(session_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_events_timestamp ON engineering_events(timestamp)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_events_category ON engineering_events(category)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_events_execution ON engineering_events(execution_id)")
        
        cursor.execute("PRAGMA journal_mode=WAL")
        
        conn.commit()
        conn.close()

    async def on_event_published(self, event: AetherisEvent):
        await self.write_queue.put(event)
        if not self.is_writing:
            asyncio.create_task(self._process_write_queue())

    async def _process_write_queue(self):
        self.is_writing = True
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        while not self.write_queue.empty():
            event = await self.write_queue.get()
            try:
                cursor.execute("""
                INSERT OR REPLACE INTO engineering_events (
                    event_id, session_id, project_id, workspace_id, execution_id,
                    timestamp, engine, category, severity, payload, duration,
                    dependencies, metadata, version
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    event.event_id,
                    event.session_id,
                    event.project_id,
                    event.workspace_id,
                    event.execution_id,
                    event.timestamp,
                    event.engine,
                    event.category,
                    event.severity,
                    json.dumps(event.payload),
                    event.duration,
                    ",".join(event.dependencies),
                    json.dumps(event.metadata),
                    event.version
                ))
            except Exception:
                pass
            self.write_queue.task_done()
            
        conn.commit()
        conn.close()
        self.is_writing = False

    def get_session_events(self, session_id: str) -> List[AetherisEvent]:
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM engineering_events WHERE session_id = ? ORDER BY timestamp ASC", (session_id,))
        rows = cursor.fetchall()
        conn.close()
        
        events = []
        for row in rows:
            events.append(AetherisEvent(
                event_id=row["event_id"],
                session_id=row["session_id"],
                project_id=row["project_id"],
                workspace_id=row["workspace_id"],
                execution_id=row["execution_id"],
                timestamp=row["timestamp"],
                engine=row["engine"],
                category=row["category"],
                severity=row["severity"],
                payload=json.loads(row["payload"]),
                duration=row["duration"],
                dependencies=row["dependencies"].split(",") if row["dependencies"] else [],
                metadata=json.loads(row["metadata"]),
                version=row["version"]
            ))
        return events

    def get_execution_events(self, execution_id: str) -> List[AetherisEvent]:
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM engineering_events WHERE execution_id = ? ORDER BY timestamp ASC", (execution_id,))
        rows = cursor.fetchall()
        conn.close()
        
        events = []
        for row in rows:
            events.append(AetherisEvent(
                event_id=row["event_id"],
                session_id=row["session_id"],
                project_id=row["project_id"],
                workspace_id=row["workspace_id"],
                execution_id=row["execution_id"],
                timestamp=row["timestamp"],
                engine=row["engine"],
                category=row["category"],
                severity=row["severity"],
                payload=json.loads(row["payload"]),
                duration=row["duration"],
                dependencies=row["dependencies"].split(",") if row["dependencies"] else [],
                metadata=json.loads(row["metadata"]),
                version=row["version"]
            ))
        return events

    def get_all_sessions(self) -> List[Dict[str, Any]]:
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        cursor.execute("""
            SELECT session_id, project_id, MIN(timestamp) as started, COUNT(*) as event_count 
            FROM engineering_events 
            GROUP BY session_id 
            ORDER BY started DESC
        """)
        rows = cursor.fetchall()
        conn.close()
        
        sessions = []
        for row in rows:
            sessions.append({
                "session_id": row[0],
                "project_id": row[1],
                "started": row[2],
                "event_count": row[3]
            })
        return sessions
