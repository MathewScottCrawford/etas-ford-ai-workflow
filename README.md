# AI-Assisted Automotive Software Engineering Workflow
### ETAS / Ford Motor Company — Reference Architecture

> **Status:** Exploration prototype | v0.1.0  
> **Stack:** n8n · LangGraph · FastAPI · Ollama · Docker · GitHub Actions  
> **Domain:** AUTOSAR Classic (RTA-CAR) · ISO 26262 / ASPICE-aware · Ford ASE integration

---

## Overview

This repository is a reference implementation of an **AI-assisted automotive software engineering (ASE) workflow** targeting the full definition-to-delivery pipeline for ECU software development. It demonstrates how agentic AI capabilities can be integrated into an AUTOSAR-based development environment without compromising ISO 26262 or ASPICE traceability requirements.

The architecture is directly aligned with ETAS's publicly stated AI tooling strategy:
- **Left-side AI** (coding): ARXML configuration assistance, BSW integration guidance, C code review
- **Right-side AI** (validation): automated test generation from requirements, AI calibration support
- **Orchestration layer**: multi-step agentic workflows coordinating across tools and phases

The `email_catchup_workflow.json` included in `workflows/n8n/` is a **working agentic prototype** (n8n + LangGraph + Ollama) originally developed as a standalone project — see [MathewScottCrawford/ClaudeClass](https://github.com/MathewScottCrawford/ClaudeClass) for the full repo. It demonstrates the same orchestration patterns used in the AUTOSAR-focused agents here.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                    n8n Orchestration Layer                          │
│            (workflow triggers, routing, human-in-the-loop)          │
└────────────┬──────────────┬──────────────┬──────────────┬───────────┘
             │              │              │              │
     ┌───────▼──────┐ ┌─────▼──────┐ ┌────▼──────┐ ┌────▼──────────┐
     │  Req Agent   │ │Config Agent│ │Build Agent│ │  Test Agent   │
     │  (LangGraph) │ │(LangGraph) │ │(LangGraph)│ │  (LangGraph)  │
     │  FastAPI svc │ │FastAPI svc │ │FastAPI svc│ │  FastAPI svc  │
     └───────┬──────┘ └─────┬──────┘ └────┬──────┘ └────┬──────────┘
             │              │              │              │
     ┌───────▼──────────────▼──────────────▼──────────────▼───────────┐
     │                   Ollama (local LLM inference)                  │
     │                phi4-mini / llama3 / codestral                   │
     └─────────────────────────────────────────────────────────────────┘
```

See [`docs/architecture_diagram.pdf`](docs/architecture_diagram.pdf) for the full phase-by-phase pipeline diagram.

---

## Pipeline Phases

| Phase | Tools | AI Assistance |
|-------|-------|---------------|
| **Define** | IBM DOORS, Jira, RTM Bridge | Requirement gap analysis, ambiguity detection |
| **Design** | Draw.io / EA, Structurizr, ARXML Linter | Design review, interface tradeoff analysis |
| **Configure** | ETAS RTA-CAR, MATLAB/Simulink, Embedded AI Coder | Config lint, ARXML schema validation |
| **Build** | GNU Make, TASKING Compiler, PC-lint/Polyspace, Artifactory | MISRA violation triage, build log analysis |
| **CI/CT/CD** | GitHub, Jenkins, VectorCAST/LDRA, Docker | Test case generation, failure root cause analysis |
| **Deliver** | dSPACE HIL, Release Package, ETAS AI Calibration Suite | Release notes generation, sign-off checklist |

---

## Repository Structure

```
etas-ford-ai-workflow/
├── README.md
├── docs/
│   ├── architecture_diagram.pdf             # Full pipeline architecture (A3 landscape)
│   ├── generate_architecture_pdf.py         # Diagram source — regenerate with Python
│   └── adr/
│       └── ADR-001-agent-isolation.md       # ISO 26262 agent isolation decision record
├── workflows/
│   ├── n8n/
│   │   ├── email_catchup_workflow.json      # Active: LinkedIn recruiter email extraction
│   │   │                                    #   n8n + LangGraph + Ollama (phi4-mini)
│   │   └── autosar_review_workflow.json     # Placeholder: ARXML review trigger
│   └── jenkins/
│       └── Jenkinsfile                      # CI/CD pipeline definition
├── agents/
│   ├── config_agent/
│   │   ├── main.py                          # FastAPI entrypoint
│   │   ├── graph.py                         # LangGraph 3-step ARXML review state machine
│   │   └── requirements.txt
│   ├── requirements_agent/
│   │   └── README.md                        # Planned v0.2.0
│   └── shared/
│       ├── llm_client.py                    # Ollama wrapper (phi4-mini)
│       └── safety_guardrails.py             # ISO 26262 confidence gate + MISRA guardrail
├── scripts/
│   └── arxml_diff.py                        # ARXML change detection utility
├── infra/
│   ├── docker-compose.yml                   # n8n + Ollama + agent services
│   └── .env.example
└── .github/
    └── workflows/
        └── ci.yml                           # GitHub Actions baseline
```

---

## Quick Start

```bash
# 1. Clone
git clone https://github.com/MathewScottCrawford/etas-ford-ai-workflow.git
cd etas-ford-ai-workflow

# 2. Configure environment
cp infra/.env.example infra/.env
# Edit .env: Ollama host, n8n credentials, Jira API token

# 3. Start services
docker compose -f infra/docker-compose.yml up -d

# 4. Access n8n
open http://localhost:5678

# 5. Regenerate architecture diagram (optional)
cd docs && python generate_architecture_pdf.py
```

---

## Safety & Compliance Notes

This prototype is designed with ISO 26262 and ASPICE traceability in mind:

- All AI-generated artifacts are flagged as **"AI-assisted, requires human review"** before entering any controlled baseline
- Agent outputs include a `confidence_score` and `traceability_refs` field linking back to source requirements
- No AI agent has write access to version-controlled AUTOSAR artifacts without an explicit human approval gate in n8n
- MISRA and static analysis results are never suppressed by AI — agents may *triage* findings but not *dismiss* them
- See [`docs/adr/ADR-001-agent-isolation.md`](docs/adr/ADR-001-agent-isolation.md) for the full architectural decision record

---

## Toolchain Mapping: Vector/EB → ETAS RTA-CAR

| Concept | Vector DaVinci | EB Tresos | ETAS RTA-CAR |
|---------|---------------|-----------|--------------|
| BSW configuration | .davinci project | tresos project | RTA-CAR workspace |
| ARXML output | SystemDesk export | Plugin-generated | Native ARXML |
| OS configuration | OsTask, OsAlarm | Os module | RTA-OS |
| COM stack | COM, ComM, PduR | COM, PduR | RTA-COM |
| Diagnostics | DCM, DEM | DCM, DEM | RTA-BSW DCM/DEM |
| Code generation | Generate button / CLI | tresos Studio gen | rta-gen CLI |

---

## Roadmap

- [x] Repository baseline and architecture diagram (A3 PDF, regenerable)
- [x] Email catchup workflow — working n8n + LangGraph prototype (submodule)
- [x] n8n AUTOSAR ARXML review workflow (placeholder, ISO 26262 gate)
- [x] config_agent — LangGraph ARXML review with confidence scoring
- [x] Safety guardrails module — ISO 26262 / MISRA output validation
- [x] Docker Compose stack — n8n + Ollama + agent microservices
- [x] GitHub Actions CI baseline
- [ ] requirements_agent — DOORS gap analysis agent (v0.2.0)
- [ ] Jenkins pipeline integration (v0.2.0)
- [ ] VectorCAST test result triage agent (v0.3.0)
- [ ] ETAS RTA-CAR ARXML schema validation scripts (v0.3.0)

---

## Author

**Mathew S. Crawford**  
AI-Assisted Automotive Software Engineering  
SE Michigan | UofM AGAIS Program  
[linkedin.com/in/mathewscrawford](https://www.linkedin.com/in/mathewscrawford/) · mathew.s.crawford@gmail.com · 734-765-4143
