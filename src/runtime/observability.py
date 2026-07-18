"""
ObservabilityEngine — Structured logging, metrics, and traces (Phase 4).

Provides three observability signals:
  Logs   — structured JSONL log records with context
  Metrics — counters, gauges, histograms keyed by engine
  Traces  — per-execution span trees
"""
import json
import time
import threading
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional


class Span:
    """A single trace span (engine step)."""

    def __init__(self, span_id: str, parent_id: Optional[str],
                 name: str, session_id: str):
        self.span_id   = span_id
        self.parent_id = parent_id
        self.name      = name
        self.session_id = session_id
        self.start_time = time.time()
        self.end_time: Optional[float] = None
        self.status    = "running"
        self.tags: Dict[str, Any] = {}
        self.error: Optional[str] = None

    def finish(self, status: str = "ok", error: Optional[str] = None):
        self.end_time = time.time()
        self.status   = status
        self.error    = error

    def duration_ms(self) -> float:
        if self.end_time:
            return round((self.end_time - self.start_time) * 1000, 2)
        return round((time.time() - self.start_time) * 1000, 2)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "span_id":    self.span_id,
            "parent_id":  self.parent_id,
            "name":       self.name,
            "session_id": self.session_id,
            "start_time": self.start_time,
            "end_time":   self.end_time,
            "duration_ms": self.duration_ms(),
            "status":     self.status,
            "tags":       self.tags,
            "error":      self.error,
        }


class ObservabilityEngine:
    """
    Unified observability layer: logs + metrics + traces.
    All data is written to .aetheris/observability/ on disk.
    """

    def __init__(self, workspace_path: str, session_id: str = ""):
        self.workspace  = Path(workspace_path).resolve()
        self.session_id = session_id

        self._obs_dir    = self.workspace / ".aetheris" / "observability"
        self._log_dir    = self._obs_dir / "logs"
        self._metric_dir = self._obs_dir / "metrics"
        self._trace_dir  = self._obs_dir / "traces"
        for d in (self._log_dir, self._metric_dir, self._trace_dir):
            d.mkdir(parents=True, exist_ok=True)

        self._lock    = threading.Lock()
        self._metrics: Dict[str, Any] = defaultdict(lambda: defaultdict(float))
        self._spans:   Dict[str, Span] = {}

    # ── logging ───────────────────────────────────────────────────────────────

    def log(self, level: str, engine: str, message: str,
            context: Optional[Dict[str, Any]] = None):
        record = {
            "ts":       time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "level":    level.upper(),
            "engine":   engine,
            "session":  self.session_id,
            "message":  message,
            "context":  context or {},
        }
        log_file = self._log_dir / f"{self.session_id or 'global'}.jsonl"
        with self._lock:
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(record) + "\n")

    def debug(self, engine: str, msg: str, **ctx):
        self.log("DEBUG", engine, msg, ctx or None)

    def info(self, engine: str, msg: str, **ctx):
        self.log("INFO", engine, msg, ctx or None)

    def warning(self, engine: str, msg: str, **ctx):
        self.log("WARNING", engine, msg, ctx or None)

    def error(self, engine: str, msg: str, **ctx):
        self.log("ERROR", engine, msg, ctx or None)

    # ── metrics ───────────────────────────────────────────────────────────────

    def counter_inc(self, engine: str, metric: str, value: float = 1.0):
        with self._lock:
            self._metrics[engine][metric] += value
        self._flush_metrics()

    def gauge_set(self, engine: str, metric: str, value: float):
        with self._lock:
            self._metrics[engine][f"gauge_{metric}"] = value
        self._flush_metrics()

    def histogram_record(self, engine: str, metric: str, value: float):
        key = f"hist_{metric}"
        with self._lock:
            bucket = self._metrics[engine].get(key, [])
            if isinstance(bucket, list):
                bucket.append(value)
                if len(bucket) > 1000:
                    bucket = bucket[-1000:]
                self._metrics[engine][key] = bucket
        self._flush_metrics()

    def _flush_metrics(self):
        metric_file = self._metric_dir / f"{self.session_id or 'global'}_metrics.json"
        try:
            snapshot = {eng: dict(vals) for eng, vals in self._metrics.items()}
            metric_file.write_text(json.dumps(snapshot, indent=2), encoding="utf-8")
        except Exception:
            pass

    def get_metrics(self) -> Dict[str, Any]:
        with self._lock:
            return {eng: dict(vals) for eng, vals in self._metrics.items()}

    # ── tracing ───────────────────────────────────────────────────────────────

    def start_span(self, name: str, parent_id: Optional[str] = None) -> Span:
        import uuid
        span = Span(
            span_id=str(uuid.uuid4())[:8],
            parent_id=parent_id,
            name=name,
            session_id=self.session_id,
        )
        with self._lock:
            self._spans[span.span_id] = span
        return span

    def finish_span(self, span: Span, status: str = "ok",
                    error: Optional[str] = None):
        span.finish(status=status, error=error)
        self._write_span(span)

    def _write_span(self, span: Span):
        trace_file = self._trace_dir / f"{self.session_id or 'global'}_spans.jsonl"
        with self._lock:
            with open(trace_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(span.to_dict()) + "\n")

    def get_trace(self, session_id: str) -> List[Dict[str, Any]]:
        trace_file = self._trace_dir / f"{session_id}_spans.jsonl"
        if not trace_file.exists():
            return []
        spans = []
        with open(trace_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        spans.append(json.loads(line))
                    except Exception:
                        pass
        return spans

    def read_logs(self, session_id: str, level: Optional[str] = None,
                  limit: int = 200) -> List[Dict[str, Any]]:
        log_file = self._log_dir / f"{session_id}.jsonl"
        if not log_file.exists():
            return []
        records = []
        with open(log_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                    if level is None or rec.get("level") == level.upper():
                        records.append(rec)
                except Exception:
                    pass
        return records[-limit:]
