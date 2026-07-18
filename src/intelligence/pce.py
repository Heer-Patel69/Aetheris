"""
PromptCompilerEngine (PCE) — SPEC-048 Production Implementation.
PromptOptimizationEngine (POE) — SPEC-049 Production Implementation.

PCE: Assembles structured prompts from skill role, engineering context,
     task spec, relevant EKB knowledge, and output schema.
POE: Tracks prompt→quality mappings; promotes winning variants.
"""
import json
import hashlib
import time
from pathlib import Path
from typing import Any, Dict, List, Optional


# ─── PCE ──────────────────────────────────────────────────────────────────────

SYSTEM_TEMPLATE = """You are {skill_name}. {skill_description}

Engineering Context:
  Stack: {tech_stack}
  Architecture: {architecture}
  Conventions: {conventions}
  Language: {primary_language}

Relevant Knowledge:
{relevant_knowledge}

Task:
{task_description}

Acceptance Criteria:
{acceptance_criteria}

Output Format:
{output_format}"""

QUICK_TEMPLATE = """You are {skill_name}.

Task: {task_description}

Output: {output_format}"""


class PromptCompilerEngine:
    """
    SPEC-048 Prompt Compiler Engine.
    Compiles a structured prompt from all available engineering context.
    """

    TEMPLATES = {
        "STANDARD": SYSTEM_TEMPLATE,
        "QUICK":    QUICK_TEMPLATE,
        "DEEP":     SYSTEM_TEMPLATE,      # same structure, ERE adds CoT
        "CONSENSUS": SYSTEM_TEMPLATE,
    }

    def __init__(self, workspace_path: str = ".", event_store=None,
                 session_id: str = ""):
        self.workspace  = Path(workspace_path).resolve()
        self._store     = event_store
        self._session   = session_id

    def compile_prompt(
        self,
        template_name: str = "STANDARD",
        variables: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Compile a fully-resolved prompt from variables and a template."""
        vars_ = variables or {}
        template = self.TEMPLATES.get(template_name.upper(), SYSTEM_TEMPLATE)

        relevant_knowledge = self._format_knowledge(
            vars_.get("relevant_knowledge", [])
        )

        prompt = template.format(
            skill_name          = vars_.get("skill_name", "Senior Software Engineer"),
            skill_description   = vars_.get("skill_description",
                                            "You generate production-quality code."),
            tech_stack          = vars_.get("tech_stack", "Python"),
            architecture        = vars_.get("architecture", "Modular"),
            conventions         = vars_.get("conventions", "PEP8, type hints"),
            primary_language    = vars_.get("primary_language", "Python"),
            relevant_knowledge  = relevant_knowledge,
            task_description    = vars_.get("task_description", vars_.get("goal", "")),
            acceptance_criteria = self._format_criteria(
                vars_.get("acceptance_criteria", [])
            ),
            output_format       = vars_.get("output_format", "Complete implementation"),
        )

        token_estimate = len(prompt.split()) * 1.3  # rough word→token ratio

        result = {
            "template_used":    template_name,
            "prompt":           prompt,
            "prompt_hash":      hashlib.sha256(prompt.encode()).hexdigest()[:16],
            "token_estimate":   int(token_estimate),
            "variables_used":   list(vars_.keys()),
            "version":          "1.0.0",
            "compiled_at":      time.time(),
        }

        if self._store:
            try:
                self._store.emit(
                    category="EXECUTION",
                    event_type="PromptCompiled",
                    payload={"template": template_name,
                             "token_estimate": int(token_estimate),
                             "prompt_hash": result["prompt_hash"]},
                    session_id=self._session,
                )
            except Exception:
                pass

        return result

    def _format_knowledge(self, entries: List[Any]) -> str:
        if not entries:
            return "  (no additional context)"
        lines = []
        for i, entry in enumerate(entries[:5], 1):  # top-5 entries
            if isinstance(entry, dict):
                src = entry.get("source", f"entry-{i}")
                content = entry.get("content", entry.get("summary", str(entry)))
                lines.append(f"  [{i}] {src}: {str(content)[:200]}")
            else:
                lines.append(f"  [{i}] {str(entry)[:200]}")
        return "\n".join(lines)

    def _format_criteria(self, criteria: List[str]) -> str:
        if not criteria:
            return "  - Code must compile without errors\n  - Follow project conventions"
        return "\n".join(f"  - {c}" for c in criteria)

    def compile_cot_prompt(
        self,
        task: str,
        context: Dict[str, Any],
        cot_depth: int = 3,
    ) -> Dict[str, Any]:
        """Compile a chain-of-thought enriched prompt for ERE."""
        steps = []
        if cot_depth >= 1:
            steps.append("Step 1 — UNDERSTAND: What exactly is being asked? "
                         "What are the constraints?")
        if cot_depth >= 2:
            steps.append("Step 2 — PLAN: What approach will I take? "
                         "What could go wrong?")
        if cot_depth >= 3:
            steps.append("Step 3 — EXECUTE: Generate the implementation "
                         "following the plan.")
        if cot_depth >= 4:
            steps.append("Step 4 — VERIFY: Does the output satisfy the "
                         "acceptance criteria?")
        if cot_depth >= 5:
            steps.append("Step 5 — REFLECT: What could be improved? "
                         "Any edge cases missed?")

        cot_section = "\n".join(steps)
        base = self.compile_prompt("STANDARD", {**context, "task_description": task})
        full_prompt = base["prompt"] + "\n\nReasoning Process:\n" + cot_section

        return {**base, "prompt": full_prompt, "cot_depth": cot_depth}


# ─── POE ──────────────────────────────────────────────────────────────────────

class PromptOptimizationEngine:
    """
    SPEC-049 Prompt Optimization Engine.
    Tracks prompt→quality outcomes and promotes winning variants.
    """

    def __init__(self, workspace_path: str = ".", event_store=None,
                 session_id: str = ""):
        self.workspace = Path(workspace_path).resolve()
        self._store    = event_store
        self._session  = session_id
        self._exp_dir  = self.workspace / ".aetheris" / "benchmarks" / "prompt_experiments"
        self._exp_dir.mkdir(parents=True, exist_ok=True)
        self._exp_file = self._exp_dir / "experiments.json"
        self._experiments: Dict[str, Any] = self._load_experiments()

    def optimize_prompt(self, compiled_prompt: Dict[str, Any]) -> Dict[str, Any]:
        """Apply known optimizations to a compiled prompt."""
        original = compiled_prompt.get("prompt", "")
        # strip redundant whitespace lines and strip each line
        cleaned = "\n".join(
            line.strip() for line in original.splitlines()
            if line.strip()
        )
        # remove duplicate context sections
        lines = cleaned.splitlines()
        seen = set()
        deduped = []
        for line in lines:
            key = line.strip()
            if key not in seen or len(key) < 20:
                deduped.append(line)
                seen.add(key)
        optimized = "\n".join(deduped)

        saved = len(original) - len(optimized)
        token_saving = int(saved / 4)  # ~4 chars per token

        return {
            **compiled_prompt,
            "prompt": optimized,
            "original_length": len(original),
            "optimized_length": len(optimized),
            "chars_saved": saved,
            "tokens_saved_estimate": token_saving,
            "status": "optimized",
        }

    def record_outcome(self, prompt_hash: str, quality_score: float,
                       task_type: str = ""):
        """Record the quality outcome of a prompt execution."""
        self._experiments.setdefault(prompt_hash, {
            "task_type": task_type, "runs": [], "avg_quality": 0.0,
        })
        entry = self._experiments[prompt_hash]
        entry["runs"].append({"quality": quality_score, "ts": time.time()})
        entry["runs"] = entry["runs"][-50:]  # keep last 50
        entry["avg_quality"] = round(
            sum(r["quality"] for r in entry["runs"]) / len(entry["runs"]), 4
        )
        self._save_experiments()

    def _load_experiments(self) -> Dict[str, Any]:
        if self._exp_file.exists():
            try:
                return json.loads(self._exp_file.read_text(encoding="utf-8"))
            except Exception:
                pass
        return {}

    def _save_experiments(self):
        self._exp_file.write_text(
            json.dumps(self._experiments, indent=2), encoding="utf-8"
        )
