"""
KnowledgeRetrievalEngine (KRE) — SPEC-053.

Performs semantic search over the EKB (Engineering Knowledge Base).
Scores entries by relevance to a query using keyword + TF-IDF heuristics.
Production upgrade: replace with embedding-based vector search.
"""
import math
import re
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Optional


class KnowledgeRetrievalEngine:
    """SPEC-053 Knowledge Retrieval Engine."""

    def __init__(self, workspace_path: str = ".", event_store=None,
                 session_id: str = ""):
        self._workspace = Path(workspace_path).resolve()
        self._store     = event_store
        self._session   = session_id
        self._kb_dir    = self._workspace / ".aetheris" / "kb"

    def retrieve_evidence(self, query: str) -> List[Dict[str, Any]]:
        """Retrieve evidence for a query (mock/shim)."""
        return [{"source": "00_SYSTEM_CONSTITUTION.md", "content": "Constitution rules."}]

    def search(self, query: str, top_k: int = 5,
               obj_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Return top-k knowledge base entries relevant to query."""
        if not self._kb_dir.exists():
            return []

        query_terms = set(re.findall(r"\w+", query.lower()))
        candidates  = []

        for f in self._kb_dir.glob("*.json"):
            if "_v" in f.name or "_history" in f.name:
                continue
            try:
                import json
                entry = json.loads(f.read_text(encoding="utf-8"))
            except Exception:
                continue

            if obj_type and entry.get("type") != obj_type:
                continue

            text  = str(entry).lower()
            terms = Counter(re.findall(r"\w+", text))
            total = sum(terms.values()) or 1
            score = sum(
                (terms.get(t, 0) / total) * math.log(1 + terms.get(t, 0))
                for t in query_terms
            )
            if score > 0:
                candidates.append((score, entry, f.stem))

        candidates.sort(key=lambda x: x[0], reverse=True)
        return [
            {"score": round(s, 6), "entry": e, "id": fid}
            for s, e, fid in candidates[:top_k]
        ]

    def get_relevant_context(self, goal: str,
                             max_entries: int = 5) -> List[Dict[str, Any]]:
        """Return top EKB entries relevant to a goal — for PCE knowledge field."""
        results = self.search(goal, top_k=max_entries)
        return [
            {
                "source":  r["id"],
                "content": r["entry"].get("content",
                           r["entry"].get("summary", str(r["entry"])[:300])),
            }
            for r in results
        ]
