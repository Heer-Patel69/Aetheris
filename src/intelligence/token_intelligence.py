from typing import Optional, Dict, Any
from intelligence.cost_analyzer import CostAnalyzer

class TokenIntelligence:
    def __init__(self, model: str = "gemini-1.5-flash"):
        self.model = model
        self.cost_analyzer = CostAnalyzer()
        
        self.input_tokens = 0
        self.output_tokens = 0
        self.cached_tokens = 0
        self.reasoning_tokens = 0
        self.total_tokens = 0
        self.cost = 0.0
        self.latency = 0.0
        self.streaming_duration = 0.0
        self.api_calls = 0
        self.retry_count = 0
        self.errors = 0
        self.context_window_usage = 0.0
        self.prompt_size = 0  # in bytes
        self.completion_size = 0  # in bytes

    def track_request(
        self,
        input_tokens: int,
        output_tokens: int,
        cached_tokens: int = 0,
        reasoning_tokens: int = 0,
        latency: float = 0.0,
        streaming_duration: float = 0.0,
        retry_count: int = 0,
        error_occurred: bool = False,
        prompt_size: int = 0,
        completion_size: int = 0,
        context_limit: int = 1_000_000
    ) -> Dict[str, Any]:
        """
        Record and measure a single API request metrics.
        """
        self.api_calls += 1
        if error_occurred:
            self.errors += 1
            
        self.retry_count += retry_count
        self.input_tokens += input_tokens
        self.output_tokens += output_tokens
        self.cached_tokens += cached_tokens
        self.reasoning_tokens += reasoning_tokens
        
        req_total = input_tokens + output_tokens
        self.total_tokens += req_total
        
        self.latency += latency
        self.streaming_duration += streaming_duration
        self.prompt_size += prompt_size
        self.completion_size += completion_size
        
        # Calculate cost for this specific request
        req_cost = self.cost_analyzer.calculate_cost(self.model, input_tokens, output_tokens)
        self.cost = round(self.cost + req_cost, 6)
        
        # Context window usage percentage
        self.context_window_usage = round((self.input_tokens / context_limit) * 100, 2)
        
        return {
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cached_tokens": cached_tokens,
            "reasoning_tokens": reasoning_tokens,
            "total_tokens": req_total,
            "cost": req_cost,
            "latency": latency,
            "streaming_duration": streaming_duration,
            "retry_count": retry_count,
            "context_window_usage_pct": self.context_window_usage
        }

    def get_summary(self) -> Dict[str, Any]:
        return {
            "model": self.model,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "cached_tokens": self.cached_tokens,
            "reasoning_tokens": self.reasoning_tokens,
            "total_tokens": self.total_tokens,
            "cost": round(self.cost, 6),
            "latency": round(self.latency, 3),
            "streaming_duration": round(self.streaming_duration, 3),
            "api_calls": self.api_calls,
            "retry_count": self.retry_count,
            "errors": self.errors,
            "context_window_usage_pct": self.context_window_usage,
            "prompt_size_bytes": self.prompt_size,
            "completion_size_bytes": self.completion_size
        }
