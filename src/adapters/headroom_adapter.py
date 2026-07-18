"""
HeadroomAdapter — Production Implementation (Phase 3 / Phase 4).

Routes context compression through Headroom AI when available,
falls back to built-in TokenOptimizationEngine (TOE) when not installed.
"""
import re
from .base_adapter import IntegrationAdapter


class HeadroomAdapter(IntegrationAdapter):
    """
    Handles:
      - Repository Compression
      - Prompt Compression
      - Context Ranking
      - Context Retrieval
      - Context Packing
      - Token Optimisation

    Outputs to the Context Intelligence Engine and Phase 4 TOE.
    """

    def initialize(self):
        self._headroom_available = self._check_headroom()

    def _check_headroom(self) -> bool:
        try:
            import headroom  # type: ignore
            return True
        except ImportError:
            return False

    # ── primary interface ─────────────────────────────────────────────────────

    def compress(self, text: str) -> str:
        """Compress a single text string (used by CapabilityRegistry.resolve('compression'))."""
        return self.compress_context(text)

    def compress_context(self, raw_context: str) -> str:
        """Full compression pipeline — Headroom AI or TOE fallback."""
        if not raw_context:
            return raw_context

        if self._headroom_available:
            try:
                import headroom  # type: ignore
                result = headroom.compress(raw_context)
                return result.compressed_text
            except Exception:
                pass

        # TOE built-in fallback
        return self._toe_compress(raw_context)

    def _toe_compress(self, text: str) -> str:
        """Lightweight internal compression (TOE Technique 1 + 2)."""
        # 1. normalise excess whitespace
        compressed = re.sub(r"\n{3,}", "\n\n", text)
        compressed = re.sub(r" {2,}", " ", compressed)
        # 2. deduplicate identical lines
        lines = compressed.splitlines()
        seen, deduped = set(), []
        for line in lines:
            key = line.strip()
            if key not in seen or len(key) < 15:
                deduped.append(line)
                seen.add(key)
        return "\n".join(deduped)

    def rank_context(self, context_items: list, query: str) -> list:
        """Rank context items by relevance to a query (keyword match scoring)."""
        scored = []
        query_terms = set(query.lower().split())
        for item in context_items:
            text = str(item).lower()
            score = sum(1 for t in query_terms if t in text)
            scored.append((score, item))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [item for _, item in scored]

    def pack_context(self, items: list, max_chars: int = 60_000) -> str:
        """Pack context items into a single string up to max_chars."""
        parts = []
        total = 0
        for item in items:
            chunk = str(item)
            if total + len(chunk) > max_chars:
                break
            parts.append(chunk)
            total += len(chunk)
        return "\n\n".join(parts)

    # ── lifecycle ─────────────────────────────────────────────────────────────

    def start(self):
        self.initialize()

    def stop(self):
        pass
