# Requirements Agent

**Status:** Active — v0.1.0  
**Stack:** LangGraph · FastAPI · Ollama (phi4-mini)  
**Input:** IBM DOORS CSV export  
**Output:** Structured ASPICE SWE.1 findings per requirement

---

## What it does

Three-step LangGraph analysis pipeline:

1. **Parse** — ingests DOORS CSV export, normalises column names across common DOORS configurations, flags pre-flight issues (missing IDs, TBD/TBI/TBC present, ambiguous terms)
2. **Analyze** — LLM evaluates each requirement against ASPICE SWE.1 criteria: ambiguity, testability, completeness, feasibility, allocation, and verification method
3. **Generate** — produces per-requirement findings with confidence scores, suggested rewrites, measurable acceptance criteria, and likely AUTOSAR BSW traceability refs

---

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/analyze/csv` | Upload a DOORS `.csv` file directly |
| POST | `/analyze/json` | Submit pre-parsed requirements as JSON (n8n integration) |
| GET  | `/health` | Health check |
| GET  | `/columns` | List recognised CSV column name variants |

---

## CSV Format

The agent recognises common DOORS export column name variants automatically.
Minimum required columns (any recognised variant):

| Canonical key | Recognised variants |
|---------------|-------------------|
| `req_id` | id, req id, requirement id, object id, doors id |
| `req_text` | text, requirement, requirement text, object text, description |

Optional columns (enrich analysis):

| Canonical key | Recognised variants |
|---------------|-------------------|
| `req_type` | type, object type |
| `allocated_to` | allocated to, allocation |
| `status` | status |
| `verification_method` | verification method |
| `rationale` | rationale |

See `tests/sample_doors_export.csv` for a working example.

---

## ASPICE SWE.1 Checklist

Each requirement is evaluated against:

- Uniquely identified
- Unambiguous language
- Testable / verifiable
- Complete (no TBDs)
- Consistent (no contradictions)
- Technically feasible
- Rationale documented
- Allocated to a component or BSW module
- Verification method specified

---

## Safety & Compliance

- Confidence score < 0.75 → `human_review_required: true`
- Any `error` severity finding → automatic escalation
- TBD/TBI/TBC in requirement text → always `error`
- No AI output enters a DOORS baseline without human approval (enforced by n8n gate — see ADR-001)

---

## Running locally

```bash
pip install -r requirements.txt
uvicorn main:app --reload --port 8002
```

Test with the sample CSV:
```bash
curl -X POST http://localhost:8002/analyze/csv \
  -F "file=@tests/sample_doors_export.csv" \
  -F "module_context=COM stack"
```
