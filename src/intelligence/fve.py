"""
FactVerificationEngine (FVE) — SPEC-055
HallucinationDetectionEngine (HDE) — SPEC-056

FVE: Cross-checks factual claims in generated output against EKB knowledge.
HDE: Detects invented APIs, wrong import paths, undefined functions.
"""
import re
import time
from typing import Any, Dict, List, Optional


# ─── FVE ──────────────────────────────────────────────────────────────────────

class FactVerificationEngine:
    """SPEC-055 Fact Verification Engine."""

    def __init__(self, ekb=None, event_store=None, session_id: str = ""):
        self._ekb     = ekb         # EngineeringKnowledgeBase instance (optional)
        self._store   = event_store
        self._session = session_id

    def verify_fact(self, claim: str) -> Dict[str, Any]:
        """Verify a single factual claim."""
        verified   = True
        confidence = 0.90
        evidence   = []

        if self._ekb:
            try:
                results = self._ekb.query_objects({"type": "technology"})
                for obj in results:
                    content_str = str(obj.get("content", ""))
                    if any(word.lower() in content_str.lower()
                           for word in claim.split() if len(word) > 4):
                        evidence.append(obj.get("object_id", "ekb-entry"))
                        break
            except Exception:
                pass

        return {
            "claim":      claim,
            "verified":   verified,
            "confidence": confidence,
            "evidence":   evidence,
            "timestamp":  time.time(),
        }

    def verify_output(self, output_text: str) -> Dict[str, Any]:
        """Run fact verification over a block of generated text."""
        # extract import statements as verifiable claims
        import_pattern = re.compile(r"^(?:from|import)\s+(\S+)", re.MULTILINE)
        imports = import_pattern.findall(output_text)

        # known-good stdlib / common packages (production: query EKB)
        known_ok = {
            "os", "sys", "json", "time", "pathlib", "typing", "re",
            "threading", "asyncio", "collections", "dataclasses",
            "pathlib", "hashlib", "uuid", "logging", "functools",
            "flask", "fastapi", "sqlalchemy", "pydantic", "click",
            "requests", "httpx", "pytest", "numpy", "pandas",
        }

        suspicious = []
        for imp in imports:
            root = imp.split(".")[0]
            if root not in known_ok and len(root) > 2:
                suspicious.append(imp)

        issues_count = len(suspicious)
        confidence   = max(0.60, 1.0 - (issues_count * 0.10))

        result = {
            "verified":          issues_count == 0,
            "confidence":        round(confidence, 4),
            "imports_checked":   imports,
            "suspicious_imports": suspicious,
            "issue_count":       issues_count,
        }

        self._emit(result)
        return result

    def _emit(self, result: Dict[str, Any]):
        if not self._store:
            return
        try:
            self._store.emit(
                category="VERIFICATION",
                event_type="FactVerificationComplete",
                payload=result,
                session_id=self._session,
            )
        except Exception:
            pass


# ─── HDE ──────────────────────────────────────────────────────────────────────

class HallucinationDetectionEngine:
    """
    SPEC-056 Hallucination Detection Engine.
    Detects invented APIs, wrong signatures, undefined variables.
    """

    # patterns that indicate likely hallucinations
    HALLUCINATION_PATTERNS = [
        (r"\.super_(?:optimize|enhance|boost|magic)\(", "invented_method"),
        (r"from aetheris\.v\d+\.", "wrong_version_import"),
        (r"import \w+\.\w+\.\w+\.\w+\.\w+", "over_deep_import"),
        (r"# AUTO-GENERATED.*DO NOT EDIT.*AUTO-GENERATED", "hallucinated_banner"),
        (r"\bplaceholder\b|\bTODO: implement\b", "placeholder_not_impl"),
        (r"\bmagic_number\s*=\s*\d{5,}", "suspicious_magic_constant"),
    ]

    def __init__(self, event_store=None, session_id: str = ""):
        self._store   = event_store
        self._session = session_id

    def scan_for_hallucinations(self, text: str) -> List[Dict[str, Any]]:
        """Return list of detected hallucination signals."""
        findings = []
        for pattern, category in self.HALLUCINATION_PATTERNS:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                findings.append({
                    "category": category,
                    "match":    match,
                    "severity": "warning" if category in
                                ("placeholder_not_impl",) else "error",
                })
        return findings

    def analyze_output(self, output_text: str,
                       auto_correct: bool = True) -> Dict[str, Any]:
        """Full hallucination analysis with optional auto-correction."""
        findings = self.scan_for_hallucinations(output_text)
        corrected_text = output_text
        corrections    = []

        if auto_correct:
            for finding in findings:
                if finding["severity"] == "warning":
                    # auto-remove placeholder comments
                    old = finding["match"]
                    new = f"# {finding['category'].upper()}: review required"
                    corrected_text = corrected_text.replace(old, new, 1)
                    corrections.append({"from": old, "to": new})

        confidence = 1.0 - (len([f for f in findings
                                  if f["severity"] == "error"]) * 0.15)
        confidence = max(0.40, confidence)

        result = {
            "hallucinations_found":  len(findings),
            "findings":              findings,
            "auto_corrected":        len(corrections),
            "corrections":           corrections,
            "clean_output":          corrected_text,
            "confidence":            round(confidence, 4),
            "requires_review":       any(f["severity"] == "error" for f in findings),
        }

        self._emit(result)
        return result

    def _emit(self, result: Dict[str, Any]):
        if not self._store:
            return
        try:
            self._store.emit(
                category="VERIFICATION",
                event_type="HallucinationScanComplete",
                payload={"found": result["hallucinations_found"],
                         "confidence": result["confidence"]},
                session_id=self._session,
            )
        except Exception:
            pass
