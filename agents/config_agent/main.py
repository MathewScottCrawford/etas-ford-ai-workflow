"""
Config Agent — FastAPI entrypoint
Handles AUTOSAR ARXML configuration review requests via LangGraph.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from graph import run_config_review

app = FastAPI(
    title="Config Agent",
    description="LangGraph-based AUTOSAR configuration review agent",
    version="0.1.0",
)


class ARXMLReviewRequest(BaseModel):
    arxml_diff: str
    requirement_refs: Optional[list[str]] = []
    module: Optional[str] = None  # e.g. "COM", "DCM", "OS"
    context: Optional[str] = None


class ARXMLReviewResponse(BaseModel):
    findings: list[dict]
    confidence_score: float
    rationale: str
    traceability_refs: list[str]
    human_review_required: bool


@app.post("/review", response_model=ARXMLReviewResponse)
async def review_arxml(request: ARXMLReviewRequest):
    """
    Accepts an ARXML diff and returns a structured review.
    Confidence score < 0.75 triggers human review gate in n8n (per ADR-001).
    """
    try:
        result = await run_config_review(
            arxml_diff=request.arxml_diff,
            requirement_refs=request.requirement_refs,
            module=request.module,
            context=request.context,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
def health():
    return {"status": "ok", "agent": "config_agent", "version": "0.1.0"}
