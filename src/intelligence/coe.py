class CostOptimizationEngine:
    def __init__(self):
        pass
    def calculate_optimal_cost(self, tokens_count: int, model_id: str) -> float:
        rate = 0.00001 if "flash" in model_id else 0.00005
        return tokens_count * rate
