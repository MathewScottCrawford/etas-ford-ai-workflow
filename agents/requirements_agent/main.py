"""
=============================================================================
File:    agents/requirements_agent/main.py
Project: AI-Assisted Automotive Software Engineering Workflow
Author:  Mathew S. Crawford
Contact: mathew.s.crawford@gmail.com | 734-765-4143
         linkedin.com/in/mathewscrawford
GitHub:  github.com/MathewScottCrawford/etas-ford-ai-workflow
License: MIT
Purpose: FastAPI entrypoint for DOORS requirements analysis agent
=============================================================================
"""

import io
import csv
import json
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
from .graph import run_requirements_analysis

app = FastAPI(
    title="Requirements Agent",
    description=(
        "LangGraph-based DOORS requirements analysis agent. "
        "Accepts CSV export, detects ambiguity, missing acceptance criteria, "
        "and ASPICE SWE.1 traceability gaps."
    ),
    version="0.1.0",
)


class RequirementsRequest(BaseModel):
    """For JSON-based submission (pre-parsed rows)."""
    requirements: list[dict]
    module_context: Optional[str] = None   # e.g. "COM stack", "DCM diagnostics"
    aspice_level:  Optional[str] = "SWE.1"


class RequirementFinding(BaseModel):
    req_id:               str
    req_text:             str
    issues:               list[str]
    severity:             str          # info | warning | error
    suggested_rewrite:    Optional[str]
    acceptance_criteria:  list[str]
    aspice_checklist:     dict
    traceability_refs:    list[str]
    confidence_score:     float
    human_review_required: bool


class RequirementsResponse(BaseModel):
    total_requirements:    int
    issues_found:          int
    overall_confidence:    float
    human_review_required: bool
    findings:              list[RequirementFinding]
    summary:               str


# ── CSV column name normalisation ─────────────────────────────────────────────
# DOORS exports vary by project configuration; map common variants to
# canonical keys used by the agent.
COLUMN_MAP = {
    # Requirement ID variants
    "id":             "req_id",
    "req id":         "req_id",
    "requirement id": "req_id",
    "object id":      "req_id",
    "doors id":       "req_id",
    # Requirement text variants
    "text":               "req_text",
    "requirement":        "req_text",
    "requirement text":   "req_text",
    "object text":        "req_text",
    "description":        "req_text",
    # Optional fields
    "type":               "req_type",
    "object type":        "req_type",
    "allocated to":       "allocated_to",
    "allocation":         "allocated_to",
    "status":             "status",
    "verification method":"verification_method",
    "rationale":          "rationale",
}


def normalise_row(row: dict) -> dict:
    """Normalise CSV column names to canonical keys."""
    normalised = {}
    for k, v in row.items():
        canon = COLUMN_MAP.get(k.strip().lower(), k.strip().lower())
        normalised[canon] = v.strip() if isinstance(v, str) else v
    return normalised


def parse_doors_csv(content: bytes) -> list[dict]:
    """
    Parse a DOORS CSV export into a list of normalised requirement dicts.
    Skips header-only rows and rows with no requirement text.
    """
    text    = content.decode("utf-8-sig")   # handle BOM from Windows exports
    reader  = csv.DictReader(io.StringIO(text))
    rows    = []
    for i, row in enumerate(reader):
        normalised = normalise_row(row)
        # Must have at least an ID and some text to be useful
        if not normalised.get("req_id") and not normalised.get("req_text"):
            continue
        # Auto-generate ID if missing
        if not normalised.get("req_id"):
            normalised["req_id"] = f"REQ-{i+1:04d}"
        rows.append(normalised)
    return rows


# ── Endpoints ─────────────────────────────────────────────────────────────────

@app.post("/analyze/csv", response_model=RequirementsResponse)
async def analyze_csv(
    file: UploadFile = File(...),
    module_context: Optional[str] = None,
    aspice_level:   Optional[str] = "SWE.1",
):
    """
    Upload a DOORS CSV export for analysis.
    Returns structured findings per requirement.
    """
    if not file.filename.endswith(".csv"):
        raise HTTPException(
            status_code=400,
            detail="File must be a .csv export from IBM DOORS."
        )
    content = await file.read()
    try:
        requirements = parse_doors_csv(content)
    except Exception as e:
        raise HTTPException(
            status_code=422,
            detail=f"CSV parse error: {e}"
        )
    if not requirements:
        raise HTTPException(
            status_code=422,
            detail="No valid requirements found in CSV. "
                   "Check that ID and text columns are present."
        )
    try:
        result = await run_requirements_analysis(
            requirements=requirements,
            module_context=module_context,
            aspice_level=aspice_level,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/analyze/json", response_model=RequirementsResponse)
async def analyze_json(request: RequirementsRequest):
    """
    Submit pre-parsed requirements as JSON.
    Useful for programmatic integration (e.g. from n8n HTTP node).
    """
    try:
        result = await run_requirements_analysis(
            requirements=request.requirements,
            module_context=request.module_context,
            aspice_level=request.aspice_level,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
def health():
    return {"status": "ok", "agent": "requirements_agent", "version": "0.1.0"}


@app.get("/columns")
def supported_columns():
    """Returns the CSV column names this agent recognises."""
    return {
        "required": ["req_id (or variant)", "req_text (or variant)"],
        "optional": ["req_type", "allocated_to", "status",
                     "verification_method", "rationale"],
        "recognised_variants": COLUMN_MAP,
    }
