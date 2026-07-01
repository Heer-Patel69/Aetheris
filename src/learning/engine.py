import json
from pathlib import Path

class ExperienceMemoryEngine:
    def __init__(self, workspace_path):
        self.workspace_path = Path(workspace_path).resolve()
        self.memory_file = self.workspace_path / ".aetheris" / "memory" / "experience.json"
        self.memory_file.parent.mkdir(parents=True, exist_ok=True)

    def record_run(self, task_id, prompt, success, metrics):
        record = {
            "task_id": task_id,
            "prompt": prompt,
            "success": success,
            "metrics": metrics
        }
        records = self.load_all()
        records.append(record)
        self.memory_file.write_text(json.dumps(records, indent=2), encoding="utf-8")
        print(f"[Learning] Experience recorded for task: '{task_id}' (Success: {success})")
        return True

    def load_all(self):
        if not self.memory_file.exists():
            return []
        try:
            return json.loads(self.memory_file.read_text(encoding="utf-8"))
        except Exception:
            return []

class PatternMiningEngine:
    def mine_patterns(self, experience_records):
        patterns = []
        if not experience_records:
            return patterns
        # Identify prompts that consistently succeed or fail
        for rec in experience_records:
            if rec.get("success") and rec.get("metrics", {}).get("quality_score", 0) > 90:
                patterns.append({
                    "pattern": f"Success Pattern for {rec['task_id']}",
                    "confidence": 0.95
                })
        return patterns

class FailureKnowledgeEngine:
    def capture_failure(self, task_id, error_msg):
        print(f"[Learning] Logging failure knowledge for task '{task_id}': {error_msg}")
        return {"task_id": task_id, "mitigation": "Increase prompt granularity and execution timeout limits"}

class SuccessKnowledgeEngine:
    def rank_success(self, records):
        return sorted(records, key=lambda x: x.get("metrics", {}).get("quality_score", 0), reverse=True)

class LearningSystem:
    def __init__(self, workspace_path):
        self.workspace_path = Path(workspace_path).resolve()
        self.experience_memory = ExperienceMemoryEngine(self.workspace_path)
        self.pattern_miner = PatternMiningEngine()
        self.failure_engine = FailureKnowledgeEngine()
        self.success_engine = SuccessKnowledgeEngine()

    def process_execution(self, task_id, prompt, success, error_msg=None, metrics=None):
        if metrics is None:
            metrics = {"quality_score": 95.0, "latency_seconds": 1.2}
        
        self.experience_memory.record_run(task_id, prompt, success, metrics)
        
        if not success and error_msg:
            self.failure_engine.capture_failure(task_id, error_msg)
            
        all_records = self.experience_memory.load_all()
        ranked = self.success_engine.rank_success(all_records)
        patterns = self.pattern_miner.mine_patterns(all_records)
        
        return {
            "status": "PROCESSED",
            "total_runs": len(all_records),
            "patterns_mined": len(patterns),
            "highest_ranked_score": ranked[0].get("metrics", {}).get("quality_score", 0) if ranked else 0
        }
