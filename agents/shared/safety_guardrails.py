"""
=============================================================================
File:    agents/shared/safety_guardrails.py
Project: AI-Assisted Automotive Software Engineering Workflow
Author:  Mathew S. Crawford
Contact: mathew.s.crawford@gmail.com | 734-765-4143
         linkedin.com/in/mathewscrawford
GitHub:  github.com/MathewScottCrawford/etas-ford-ai-workflow
License: MIT
Purpose: ISO 26262 / ASPICE output validation and escalation guardrails
=============================================================================
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
    Handles both config_agent and requirements_agent output shapes.
    - Ensures all required traceability fields are present
    - Escalates to human review if any critical findings exist
    - Never allows AI to dismiss MISRA or safety-classified findings
    - Tags all output as AI-assisted
    """
    # Requirements agent uses 'findings' list with per-req dicts
    # Config agent uses 'findings' list with per-change dicts
    # Both must have human_review_required and confidence score
    findings = state.get("findings", [])

    # Determine which confidence field is present
    confidence = state.get("confidence_score") or state.get("overall_confidence")
    if confidence is None:
        raise ValueError(
            "Safety guardrail violation: no confidence score in agent output."
        )

    # Check for required traceability fields (config_agent shape)
    if "confidence_score" in state:
        for field in ["findings", "confidence_score", "rationale",
                      "traceability_refs", "human_review_required"]:
            if field not in state or state[field] is None:
                raise ValueError(
                    f"Safety guardrail violation: required field '{field}' "
                    f"missing from agent output."
                )

    # Escalate if any finding has critical/error severity
    has_critical = any(
        f.get("severity") in ALWAYS_ESCALATE_SEVERITIES
        for f in findings
    )
    if has_critical:
        state["human_review_required"] = True
        # Append escalation note to whichever summary/rationale field exists
        note = " [ESCALATED: critical/error severity finding — human review required per ISO 26262 guardrail.]"
        if "rationale" in state:
            state["rationale"] = state["rationale"] + note
        if "summary" in state:
            state["summary"] = state["summary"] + note

    # Enforce confidence threshold
    if confidence < CONFIDENCE_THRESHOLD:
        state["human_review_required"] = True

    # Tag all output as AI-assisted
    state["ai_assisted"]   = True
    state["review_status"] = (
        "pending_human_review" if state["human_review_required"]
        else "ai_reviewed"
    )

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
