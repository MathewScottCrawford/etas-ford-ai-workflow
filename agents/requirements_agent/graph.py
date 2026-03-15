"""
=============================================================================
File:    agents/requirements_agent/graph.py
Project: AI-Assisted Automotive Software Engineering Workflow
Author:  Mathew S. Crawford
Contact: mathew.s.crawford@gmail.com | 734-765-4143
         linkedin.com/in/mathewscrawford
GitHub:  github.com/MathewScottCrawford/etas-ford-ai-workflow
License: MIT
Purpose: LangGraph 3-step requirements analysis state machine
=============================================================================
"""

import json
import re
from typing import TypedDict, Optional
from langgraph.graph import StateGraph, END
from ..shared.llm_client import get_llm
from ..shared.safety_guardrails import validate_output


def clean_json(text: str) -> str:
    """
    Strip markdown fences and whitespace from LLM output before JSON parsing.
    Handles ```json ... ```, ``` ... ```, and bare JSON with leading/trailing text.
    """
    text = re.sub(r"```(?:json)?\s*", "", text)
    text = text.replace("```", "")
    text = text.strip()
    match = re.search(r"(\[.*\]|\{.*\})", text, re.DOTALL)
    if match:
        text = match.group(1)
    return text

# ── ASPICE SWE.1 checklist items ─────────────────────────────────────────────
# These are the key attributes ASPICE SWE.1 requires for each software
# requirement. The agent checks each requirement against this list.
ASPICE_SWE1_CHECKLIST = {
    "uniquely_identified":      "Requirement has a unique identifier",
    "unambiguous":              "Requirement uses precise, unambiguous language",
    "testable":                 "Requirement is verifiable / testable",
    "complete":                 "Requirement is complete (no TBDs or placeholders)",
    "consistent":               "Requirement does not contradict other requirements",
    "feasible":                 "Requirement is technically feasible",
    "has_rationale":            "Rationale or origin is documented",
    "allocated":                "Requirement is allocated to a component or BSW module",
    "has_verification_method":  "Verification method is specified (review/test/analysis)",
}

# ── Ambiguity patterns ────────────────────────────────────────────────────────
AMBIGUITY_TERMS = [
    "appropriate", "adequate", "as necessary", "if applicable",
    "tbd", "tbi", "tbc", "to be defined", "to be confirmed",
    "fast", "slow", "small", "large", "sufficient", "reasonable",
    "should", "may", "might", "could", "user friendly", "easy",
    "robust", "flexible", "efficient", "timely", "as required",
]

UNTESTABLE_PATTERNS = [
    "shall be easy", "shall be user friendly", "shall be fast",
    "shall be robust", "shall be flexible", "shall support future",
    "shall be maintainable", "shall be readable",
]


# ── State ─────────────────────────────────────────────────────────────────────
class RequirementsState(TypedDict):
    # Inputs
    requirements:    list[dict]
    module_context:  Optional[str]
    aspice_level:    Optional[str]
    # Intermediate
    parsed:          Optional[list[dict]]   # cleaned, validated req list
    analyzed:        Optional[list[dict]]   # per-req static analysis results
    # Output
    findings:        Optional[list[dict]]
    overall_confidence:    Optional[float]
    human_review_required: Optional[bool]
    summary:         Optional[str]


# ── Step 1: Parse & validate ──────────────────────────────────────────────────
async def parse_requirements(state: RequirementsState) -> RequirementsState:
    """
    Clean and validate the requirement list.
    Flags rows missing critical fields before LLM analysis.
    """
    parsed = []
    for req in state["requirements"]:
        req_id   = req.get("req_id",   "").strip()
        req_text = req.get("req_text", "").strip()

        entry = {
            "req_id":              req_id or "MISSING-ID",
            "req_text":            req_text,
            "req_type":            req.get("req_type", ""),
            "allocated_to":        req.get("allocated_to", ""),
            "status":              req.get("status", ""),
            "verification_method": req.get("verification_method", ""),
            "rationale":           req.get("rationale", ""),
            # Pre-flight flags (set before LLM)
            "missing_id":          not req_id,
            "missing_text":        not req_text,
            "has_tbd":             any(t in req_text.lower()
                                       for t in ["tbd", "tbi", "tbc"]),
            "ambiguity_hits":      [t for t in AMBIGUITY_TERMS
                                    if t in req_text.lower()],
            "untestable_hits":     [p for p in UNTESTABLE_PATTERNS
                                    if p in req_text.lower()],
        }
        parsed.append(entry)

    return {**state, "parsed": parsed}


# ── Step 2: LLM analysis ──────────────────────────────────────────────────────
async def analyze_requirements(state: RequirementsState) -> RequirementsState:
    """
    Run LLM analysis on each requirement.
    Checks for ambiguity, testability, completeness, and ASPICE SWE.1 coverage.
    Batches requirements to stay within context limits.
    """
    llm      = get_llm()
    parsed   = state["parsed"]
    context  = state.get("module_context") or "automotive ECU software"
    analyzed = []

    # Process in batches of 5 to stay within context window
    BATCH = 5
    for i in range(0, len(parsed), BATCH):
        batch = parsed[i:i + BATCH]

        batch_text = "\n\n".join(
            f"[{r['req_id']}] {r['req_text']}"
            + (f"\n  Allocated to: {r['allocated_to']}" if r['allocated_to'] else "")
            + (f"\n  Verification: {r['verification_method']}" if r['verification_method'] else "")
            + (f"\n  Rationale: {r['rationale']}" if r['rationale'] else "")
            for r in batch
        )

        prompt = f"""You are an ASPICE SWE.1 requirements quality expert reviewing software requirements
for an automotive ECU in the domain: {context}

For each requirement below, evaluate it against these ASPICE SWE.1 criteria:
{json.dumps(ASPICE_SWE1_CHECKLIST, indent=2)}

Return a JSON array — one object per requirement — with these exact fields:
  "req_id"             - string, the requirement ID
  "issues"             - list of specific issue descriptions (empty list if none)
  "severity"           - "info" | "warning" | "error"
  "suggested_rewrite"  - improved requirement text, or null if acceptable
  "acceptance_criteria"- list of 1-3 specific, measurable test criteria
  "aspice_checklist"   - object with each checklist key mapped to true/false
  "traceability_refs"  - list of likely AUTOSAR BSW module names (e.g. ["COM", "DCM", "OS"])

Requirements to analyze:
{batch_text}

IMPORTANT: Return ONLY the raw JSON array. No markdown. No backticks. No explanation.
Start your response with [ and end with ]."""

        response = await llm.ainvoke(prompt)
        try:
            batch_results = json.loads(clean_json(response.content))
            if not isinstance(batch_results, list):
                batch_results = [batch_results]
        except Exception:
            # Fallback: mark batch as needing human review
            batch_results = [
                {
                    "req_id":              r["req_id"],
                    "issues":              ["LLM parse error — manual review required"],
                    "severity":            "error",
                    "suggested_rewrite":   None,
                    "acceptance_criteria": [],
                    "aspice_checklist":    {k: False for k in ASPICE_SWE1_CHECKLIST},
                    "traceability_refs":   [],
                }
                for r in batch
            ]

        # Merge LLM results with pre-flight flags
        for req, llm_result in zip(batch, batch_results):
            # Escalate severity if pre-flight found TBDs
            if req["has_tbd"] and llm_result.get("severity") != "error":
                llm_result["severity"] = "error"
                llm_result["issues"] = (
                    [f"TBD/TBI/TBC found in requirement text"]
                    + llm_result.get("issues", [])
                )
            # Add ambiguity hits from static scan if not already caught
            for hit in req["ambiguity_hits"]:
                flag = f"Ambiguous term: '{hit}'"
                if flag not in llm_result.get("issues", []):
                    llm_result.setdefault("issues", []).append(flag)
                    if llm_result.get("severity") == "info":
                        llm_result["severity"] = "warning"

            analyzed.append({**req, **llm_result})

    return {**state, "analyzed": analyzed}


# ── Step 3: Generate findings ─────────────────────────────────────────────────
async def generate_findings(state: RequirementsState) -> RequirementsState:
    """
    Synthesise per-requirement findings into the final response structure.
    Computes overall confidence and summary statistics.
    """
    analyzed = state["analyzed"]
    findings = []

    error_count   = 0
    warning_count = 0

    for req in analyzed:
        severity = req.get("severity", "info")
        if severity == "error":
            error_count += 1
        elif severity == "warning":
            warning_count += 1

        # Confidence per requirement
        checklist  = req.get("aspice_checklist", {})
        pass_count = sum(1 for v in checklist.values() if v)
        total      = len(checklist) or 1
        req_confidence = round(pass_count / total, 2)

        finding = {
            "req_id":               req["req_id"],
            "req_text":             req["req_text"],
            "issues":               req.get("issues", []),
            "severity":             severity,
            "suggested_rewrite":    req.get("suggested_rewrite"),
            "acceptance_criteria":  req.get("acceptance_criteria", []),
            "aspice_checklist":     checklist,
            "traceability_refs":    req.get("traceability_refs", []),
            "confidence_score":     req_confidence,
            "human_review_required": (
                severity == "error" or req_confidence < 0.75
            ),
        }
        findings.append(finding)

    n = len(findings)
    overall_confidence = round(
        sum(f["confidence_score"] for f in findings) / n, 2
    ) if n else 0.0

    human_review_required = (
        overall_confidence < 0.75
        or error_count > 0
    )

    summary = (
        f"Analyzed {n} requirement(s): "
        f"{error_count} error(s), {warning_count} warning(s). "
        f"Overall ASPICE SWE.1 confidence: {overall_confidence:.0%}. "
        + ("Human review required." if human_review_required
           else "No blocking issues found.")
    )

    output = {
        **state,
        "findings":              findings,
        "overall_confidence":    overall_confidence,
        "human_review_required": human_review_required,
        "summary":               summary,
    }

    return validate_output(output)


# ── Graph ─────────────────────────────────────────────────────────────────────
def build_graph() -> StateGraph:
    g = StateGraph(RequirementsState)
    g.add_node("parse_requirements",   parse_requirements)
    g.add_node("analyze_requirements", analyze_requirements)
    g.add_node("generate_findings",    generate_findings)

    g.set_entry_point("parse_requirements")
    g.add_edge("parse_requirements",   "analyze_requirements")
    g.add_edge("analyze_requirements", "generate_findings")
    g.add_edge("generate_findings",    END)
    return g.compile()


_graph = build_graph()


async def run_requirements_analysis(
    requirements:   list[dict],
    module_context: Optional[str] = None,
    aspice_level:   Optional[str] = "SWE.1",
) -> dict:
    initial_state = RequirementsState(
        requirements=requirements,
        module_context=module_context,
        aspice_level=aspice_level,
        parsed=None,
        analyzed=None,
        findings=None,
        overall_confidence=None,
        human_review_required=None,
        summary=None,
    )
    result = await _graph.ainvoke(initial_state)
    return {
        "total_requirements":    len(result["findings"]),
        "issues_found":          sum(
            1 for f in result["findings"] if f["issues"]
        ),
        "overall_confidence":    result["overall_confidence"],
        "human_review_required": result["human_review_required"],
        "findings":              result["findings"],
        "summary":               result["summary"],
    }
