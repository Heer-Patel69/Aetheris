"""
EngineeringReasoningEngine (ERE) — SPEC-050
SelfReflectionEngine (SRE)       — SPEC-051

ERE: Chain-of-thought reasoning over engineering problems.
SRE: Evaluates output quality against acceptance criteria; triggers revision loops.
"""
import re
import time
from typing import Any, Dict, List, Optional


# ─── ERE ──────────────────────────────────────────────────────────────────────

class ReasoningMode:
    QUICK     = "QUICK"
    STANDARD  = "STANDARD"
    DEEP      = "DEEP"
    CONSENSUS = "CONSENSUS"


class EngineeringReasoningEngine:
    """
    SPEC-050 Engineering Reasoning Engine.

    Selects reasoning mode and applies chain-of-thought to engineering decisions.
    """

    COT_TEMPLATES = {
        ReasoningMode.QUICK: [
            "EXECUTE: {task}",
        ],
        ReasoningMode.STANDARD: [
            "UNDERSTAND: Analyse the task: {task}",
            "PLAN: Outline approach and identify risks.",
            "EXECUTE: Generate implementation following the plan.",
        ],
        ReasoningMode.DEEP: [
            "UNDERSTAND: Analyse fully — constraints, edge cases, stakeholders: {task}",
            "RESEARCH: What patterns / libraries / precedents apply?",
            "PLAN: Step-by-step approach; identify failure modes.",
            "EXECUTE: Generate implementation.",
            "VERIFY: Check against acceptance criteria.",
            "REFLECT: Identify improvements and missed edge cases.",
        ],
    }

    # Domains that always trigger CONSENSUS mode
    CONSENSUS_DOMAINS = {"security", "auth", "crypto", "healthcare", "finance"}

    def __init__(self, event_store=None, session_id: str = ""):
        self._store   = event_store
        self._session = session_id

    def select_mode(
        self,
        task_description: str,
        affected_files: int = 1,
        domain: str = "",
    ) -> str:
        """Auto-select reasoning mode based on task complexity."""
        desc_lower = task_description.lower()
        dom_lower  = domain.lower()

        # consensus triggers
        if any(kw in desc_lower or kw in dom_lower
               for kw in self.CONSENSUS_DOMAINS):
            return ReasoningMode.CONSENSUS

        # deep triggers: architecture, refactor, large scope
        if affected_files > 10 or any(
            kw in desc_lower for kw in
            ("architect", "refactor", "migration", "database schema", "api design")
        ):
            return ReasoningMode.DEEP

        # quick triggers: <50 line tasks
        if any(kw in desc_lower for kw in
               ("fix typo", "rename", "add comment", "format", "simple")):
            return ReasoningMode.QUICK

        return ReasoningMode.STANDARD

    def reason_through_problem(
        self,
        problem_description: str,
        constraints: Optional[List[str]] = None,
        mode: Optional[str] = None,
        domain: str = "",
        affected_files: int = 1,
    ) -> Dict[str, Any]:
        """Apply chain-of-thought reasoning to a problem."""
        selected_mode = mode or self.select_mode(
            problem_description, affected_files, domain
        )
        steps_template = self.COT_TEMPLATES.get(
            selected_mode, self.COT_TEMPLATES[ReasoningMode.STANDARD]
        )
        steps = [s.format(task=problem_description) for s in steps_template]

        constraints_text = "; ".join(constraints or ["No additional constraints"])
        reasoning_chain = []
        for i, step in enumerate(steps, 1):
            reasoning_chain.append({
                "step":    i,
                "label":   step.split(":")[0],
                "content": step,
            })

        result = {
            "mode":            selected_mode,
            "problem":         problem_description,
            "constraints":     constraints or [],
            "reasoning_chain": reasoning_chain,
            "decisions": [{
                "issue":      problem_description,
                "resolution": (
                    f"Applied {selected_mode} chain-of-thought reasoning. "
                    f"Constraints considered: {constraints_text}."
                ),
                "trade_offs": f"Mode={selected_mode} balances depth vs speed.",
            }],
            "confidence":  self._mode_base_confidence(selected_mode),
            "timestamp":   time.time(),
        }

        self._emit(result)
        return result

    def _mode_base_confidence(self, mode: str) -> float:
        return {
            ReasoningMode.QUICK:     0.80,
            ReasoningMode.STANDARD:  0.87,
            ReasoningMode.DEEP:      0.93,
            ReasoningMode.CONSENSUS: 0.96,
        }.get(mode, 0.85)

    def _emit(self, result: Dict[str, Any]):
        if not self._store:
            return
        try:
            self._store.emit(
                category="EXECUTION",
                event_type="ReasoningComplete",
                payload={"mode": result["mode"],
                         "confidence": result["confidence"]},
                session_id=self._session,
            )
        except Exception:
            pass


# ─── SRE ──────────────────────────────────────────────────────────────────────

class SelfReflectionEngine:
    """
    SPEC-051 Self-Reflection Engine.

    Evaluates generated output against task acceptance criteria and scores
    four quality dimensions: correctness, completeness, style, security.
    """

    MIN_CONFIDENCE = 0.80
    MAX_REVISIONS  = 3

    def __init__(self, event_store=None, session_id: str = ""):
        self._store    = event_store
        self._session  = session_id
        self._revision_counts: Dict[str, int] = {}

    def critique_solution(
        self,
        proposed_solution: Dict[str, Any],
        acceptance_criteria: Optional[List[str]] = None,
        task_id: str = "",
    ) -> Dict[str, Any]:
        """
        Score the proposed solution and recommend APPROVE / REVISE / ESCALATE.
        """
        output_text = (
            proposed_solution.get("output", "")
            or proposed_solution.get("code", "")
            or str(proposed_solution.get("decisions", ""))
        )

        # ── scoring heuristics ────────────────────────────────────────────────
        correctness  = self._score_correctness(output_text)
        completeness = self._score_completeness(output_text, acceptance_criteria or [])
        style        = self._score_style(output_text)
        security     = self._score_security(output_text)

        composite = (
            correctness  * 0.40 +
            completeness * 0.30 +
            style        * 0.20 +
            security     * 0.10
        )

        revisions = self._revision_counts.get(task_id, 0)

        if composite >= self.MIN_CONFIDENCE:
            verdict = "APPROVE"
            confidence_adjustment = +0.02
        elif revisions < self.MAX_REVISIONS:
            verdict = "REVISE"
            self._revision_counts[task_id] = revisions + 1
            confidence_adjustment = -0.05
        else:
            verdict = "ESCALATE"
            confidence_adjustment = -0.10

        result = {
            "verdict":              verdict,
            "composite_score":      round(composite, 4),
            "dimensions": {
                "correctness":  round(correctness, 4),
                "completeness": round(completeness, 4),
                "style":        round(style, 4),
                "security":     round(security, 4),
            },
            "confidence_adjustment": confidence_adjustment,
            "revision_count":        revisions,
            "critique": self._generate_critique(
                correctness, completeness, style, security, acceptance_criteria or []
            ),
            "status": verdict,
        }

        self._emit(result, task_id)
        return result

    # ── scoring heuristics ─────────────────────────────────────────────────────

    def _score_correctness(self, text: str) -> float:
        if not text or len(text) < 20:
            return 0.40
        # penalties for obvious error patterns
        score = 0.88
        error_patterns = [
            r"TODO|FIXME|HACK|NotImplemented",
            r"raise NotImplementedError",
            r"pass\s*#",
        ]
        for pat in error_patterns:
            if re.search(pat, text, re.IGNORECASE):
                score -= 0.08
        return max(0.40, score)

    def _score_completeness(self, text: str, criteria: List[str]) -> float:
        if not criteria:
            return 0.85 if len(text) > 100 else 0.60
        matched = sum(
            1 for c in criteria
            if any(word.lower() in text.lower()
                   for word in c.split() if len(word) > 4)
        )
        return round(matched / len(criteria), 4) if criteria else 0.85

    def _score_style(self, text: str) -> float:
        if not text:
            return 0.50
        score = 0.88
        # long lines penalty
        long_lines = sum(1 for line in text.splitlines() if len(line) > 120)
        if long_lines > 5:
            score -= 0.05
        return max(0.50, score)

    def _score_security(self, text: str) -> float:
        score = 0.90
        risky = [
            r"eval\(", r"exec\(", r"os\.system",
            r"shell=True", r"pickle\.loads",
            r"subprocess\..*shell",
        ]
        for pat in risky:
            if re.search(pat, text):
                score -= 0.10
        return max(0.40, score)

    def _generate_critique(self, cor: float, com: float, sty: float, sec: float,
                            criteria: List[str]) -> str:
        parts = []
        if cor < 0.80:
            parts.append("Correctness concerns: possible incomplete implementation.")
        if com < 0.80:
            parts.append(f"Completeness gap: {len(criteria)} criteria, "
                         f"coverage={round(com*100)}%.")
        if sty < 0.80:
            parts.append("Style: long lines detected, consider splitting.")
        if sec < 0.80:
            parts.append("Security: risky patterns detected, review carefully.")
        return " ".join(parts) if parts else "Solution meets quality standards."

    def _emit(self, result: Dict[str, Any], task_id: str):
        if not self._store:
            return
        try:
            self._store.emit(
                category="VERIFICATION",
                event_type="SelfReflectionComplete",
                payload={"verdict": result["verdict"],
                         "score":   result["composite_score"],
                         "task_id": task_id},
                session_id=self._session,
            )
        except Exception:
            pass
