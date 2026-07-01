class ContextOptimizationEngine:
    def __init__(self):
        pass
    def filter_context(self, context: list) -> list:
        return [c for c in context if c.get("relevance", 0) > 0.5]
