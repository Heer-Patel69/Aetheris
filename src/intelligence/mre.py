class MemoryRankingEngine:
    def __init__(self):
        pass
    def rank_memories(self, memories: list) -> list:
        # Simple score calculation: score = relevance*0.4 + confidence*0.3 + freshness*0.2 + success*0.1
        ranked = []
        for idx, mem in enumerate(memories):
            rel = mem.get("relevance", 0.5)
            conf = mem.get("confidence", 0.5)
            fresh = mem.get("freshness", 0.5)
            succ = mem.get("success", 0.5)
            score = rel * 0.4 + conf * 0.3 + fresh * 0.2 + succ * 0.1
            ranked.append({"id": mem.get("id", idx), "score": score})
        return sorted(ranked, key=lambda x: x["score"], reverse=True)
