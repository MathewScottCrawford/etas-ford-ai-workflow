"""
=============================================================================
File:    agents/config_agent/graph.py
Project: AI-Assisted Automotive Software Engineering Workflow
Author:  Mathew S. Crawford
Contact: mathew.s.crawford@gmail.com | 734-765-4143
         linkedin.com/in/mathewscrawford
GitHub:  github.com/MathewScottCrawford/etas-ford-ai-workflow
License: MIT
Purpose: LangGraph 3-step ARXML review state machine
=============================================================================
"""

from typing import TypedDict, Optional
import json
import re
from langgraph.graph import StateGraph, END
from ..shared.llm_client import get_llm
from ..shared.safety_guardrails import validate_output


def clean_json(text: str) -> str:
    """
    Strip markdown fences and whitespace from LLM output before JSON parsing.
    Handles ```json ... ```, ``` ... ```, and bare JSON with leading/trailing text.
    """
    # Remove fenced code blocks (```json ... ``` or ``` ... ```)
    text = re.sub(r"```(?:json)?\s*", "", text)
    text = text.replace("```", "")
    # Strip leading/trailing whitespace and newlines
    text = text.strip()
    # If the model added explanation before/after the JSON, extract just the
    # first [...] or {...} block
    match = re.search(r"(\[.*\]|\{.*\})", text, re.DOTALL)
    if match:
        text = match.group(1)
    return text


class ConfigReviewState(TypedDict):
    arxml_diff: str
    requirement_refs: list[str]
    module: Optional[str]
    context: Optional[str]
    # intermediate
    parsed_changes: Optional[list[dict]]
    cross_module_risks: Optional[list[str]]
    # output
    findings: Optional[list[dict]]
    confidence_score: Optional[float]
    rationale: Optional[str]
    traceability_refs: Optional[list[str]]
    human_review_required: Optional[bool]


async def parse_arxml_changes(state: ConfigReviewState) -> ConfigReviewState:
    """Step 1: Parse the ARXML diff into structured change list."""
    llm = get_llm()
    prompt = f"""You are an AUTOSAR BSW configuration expert. Parse the following ARXML diff
and return a JSON array of changes. Each object must have exactly these keys:
  "element"     - AUTOSAR element type (e.g. I-SIGNAL, I-PDU, TASK, DID)
  "change_type" - one of: added | removed | modified
  "path"        - ARXML element path
  "summary"     - one sentence describing the change

ARXML diff:
{state['arxml_diff']}

Module context: {state.get('module', 'unknown')}

IMPORTANT: Return ONLY the raw JSON array. No markdown. No backticks. No explanation.
Start your response with [ and end with ]."""

    response = await llm.ainvoke(prompt)
    try:
        parsed = json.loads(clean_json(response.content))
        if not isinstance(parsed, list):
            parsed = [parsed]
    except Exception:
        parsed = [{"element": "unknown", "change_type": "unknown",
                   "path": "/", "summary": response.content[:200]}]
    return {**state, "parsed_changes": parsed}


async def assess_cross_module_risk(state: ConfigReviewState) -> ConfigReviewState:
    """Step 2: Identify cross-module integration risks from the changes."""
    llm = get_llm()
    changes_str = str(state.get("parsed_changes", []))
    prompt = f"""You are an AUTOSAR integration expert reviewing changes for cross-module risks.
Known risk patterns:
- COM/PduR changes that affect buffer sizing in MemIf/NvM
- OS task priority changes that affect timing of COM callbacks
- DCM session handling changes that conflict with ComM channel states
- MCAL pin assignments that conflict with IoHwAb abstraction layer

Changes detected:
{changes_str}

Requirement references: {state.get('requirement_refs', [])}

List any cross-module integration risks as a JSON array of strings.
If there are no risks return an empty array: []

IMPORTANT: Return ONLY the raw JSON array. No markdown. No backticks. No explanation.
Start your response with [ and end with ]."""

    response = await llm.ainvoke(prompt)
    try:
        risks = json.loads(clean_json(response.content))
        if not isinstance(risks, list):
            risks = [str(risks)]
    except Exception:
        risks = [response.content[:300]]
    return {**state, "cross_module_risks": risks}


async def generate_findings(state: ConfigReviewState) -> ConfigReviewState:
    """Step 3: Synthesize findings with confidence score and traceability."""
    changes = state.get("parsed_changes", [])
    risks = state.get("cross_module_risks", [])
    refs = state.get("requirement_refs", [])

    findings = []
    for change in changes:
        finding = {
            "element": change.get("element"),
            "severity": "info",
            "summary": change.get("summary"),
            "traceability": refs[:2] if refs else [],
        }
        # Elevate severity if cross-module risk references this element
        for risk in risks:
            if change.get("element", "").lower() in risk.lower():
                finding["severity"] = "warning"
                finding["risk_detail"] = risk
        findings.append(finding)

    # Confidence scoring heuristic
    warning_count = sum(1 for f in findings if f["severity"] == "warning")
    base_confidence = 0.90 if len(changes) < 5 else 0.80
    confidence = max(0.50, base_confidence - (warning_count * 0.08))

    rationale = (
        f"Reviewed {len(changes)} ARXML change(s) across module '{state.get('module', 'unspecified')}'. "
        f"Identified {warning_count} cross-module risk(s). "
        f"Confidence reflects change volume and risk count."
    )

    output = {
        **state,
        "findings": findings,
        "confidence_score": round(confidence, 2),
        "rationale": rationale,
        "traceability_refs": refs,
        "human_review_required": confidence < 0.75,
    }

    # ISO 26262 safety guardrail pass
    return validate_output(output)


def build_graph() -> StateGraph:
    g = StateGraph(ConfigReviewState)
    g.add_node("parse_arxml_changes", parse_arxml_changes)
    g.add_node("assess_cross_module_risk", assess_cross_module_risk)
    g.add_node("generate_findings", generate_findings)

    g.set_entry_point("parse_arxml_changes")
    g.add_edge("parse_arxml_changes", "assess_cross_module_risk")
    g.add_edge("assess_cross_module_risk", "generate_findings")
    g.add_edge("generate_findings", END)
    return g.compile()


_graph = build_graph()


async def run_config_review(arxml_diff, requirement_refs, module, context):
    initial_state = ConfigReviewState(
        arxml_diff=arxml_diff,
        requirement_refs=requirement_refs or [],
        module=module,
        context=context,
        parsed_changes=None,
        cross_module_risks=None,
        findings=None,
        confidence_score=None,
        rationale=None,
        traceability_refs=None,
        human_review_required=None,
    )
    result = await _graph.ainvoke(initial_state)
    return {
        "findings": result["findings"],
        "confidence_score": result["confidence_score"],
        "rationale": result["rationale"],
        "traceability_refs": result["traceability_refs"],
        "human_review_required": result["human_review_required"],
    }
