class CostAnalyzer:
    PRICING = {
        "gemini-1.5-flash": {"input_per_m": 0.075, "output_per_m": 0.30},
        "gemini-1.5-pro": {"input_per_m": 1.25, "output_per_m": 5.00},
        "claude-3.5-sonnet": {"input_per_m": 3.00, "output_per_m": 15.00},
        "gpt-4o": {"input_per_m": 5.00, "output_per_m": 15.00},
        "default": {"input_per_m": 0.15, "output_per_m": 0.60}
    }

    def calculate_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """
        Calculate total cost based on model and token counts.
        """
        model_key = model.lower()
        pricing = self.PRICING.get(model_key, self.PRICING["default"])
        
        input_cost = (input_tokens / 1_000_000) * pricing["input_per_m"]
        output_cost = (output_tokens / 1_000_000) * pricing["output_per_m"]
        
        return round(input_cost + output_cost, 6)
