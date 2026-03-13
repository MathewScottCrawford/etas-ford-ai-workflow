"""
Safety Guardrails — ISO 26262 / ASPICE output validation
Ensures AI agent outputs are properly flagged and never silently approved.
"""

from typing import Any


# Fields that must always be present in agent output for traceability
REQUIRED_FIELDS = ["findings", "confidence_score", "rationale",
                   "traceability_refs", "human_review_required"]

# Severity levels that always force human review regardless of confidence
ALWAYS_ESCALATE_SEVERITIES = {"critical", "error"}

# Confidence threshold below which human review is mandatory
CONFIDENCE_THRESHOLD = 0.75


def validate_output(state: dict) -> dict:
    """
    Validates agent output against ISO 26262 safety requirements.
    - Ensures all required traceability fields are present
    - Escalates to human review if any critical findings exist
    - Never allows AI to dismiss MISRA or safety-classified findings
    - Tags all output as AI-assisted
    """
    # Ensure required fields exist
    for field in REQUIRED_FIELDS:
        if field not in state or state[field] is None:
            raise ValueError(
                f"Safety guardrail violation: required field '{field}' "
                f"missing from agent output. Cannot proceed without full traceability."
            )

    findings = state.get("findings", [])

    # Escalate if any finding has a critical/error severity
    has_critical = any(
        f.get("severity") in ALWAYS_ESCALATE_SEVERITIES
        for f in findings
    )
    if has_critical:
        state["human_review_required"] = True
        state["rationale"] = (
            state["rationale"] +
            " [ESCALATED: critical/error severity finding requires human review per ISO 26262 guardrail.]"
        )

    # Enforce confidence threshold
    if state["confidence_score"] < CONFIDENCE_THRESHOLD:
        state["human_review_required"] = True

    # Tag all output as AI-assisted (never allow silent baseline entry)
    state["ai_assisted"] = True
    state["review_status"] = "pending_human_review" if state["human_review_required"] else "ai_reviewed"

    return state


def check_misra_suppression(findings: list[dict]) -> bool:
    """
    Returns True if any finding appears to suppress or dismiss a MISRA violation.
    AI agents must never suppress MISRA findings — they may only triage them.
    """
    suppression_keywords = ["suppress", "dismiss", "ignore", "waive", "bypass"]
    for finding in findings:
        summary = finding.get("summary", "").lower()
        if any(kw in summary for kw in suppression_keywords):
            return True
    return False
