<!--
=============================================================================
File:    docs/ARCHITECTURE.md
Project: AI-Assisted Automotive Software Engineering Workflow
Author:  Mathew S. Crawford
Contact: mathew.s.crawford@gmail.com | 734-765-4143
         linkedin.com/in/mathewscrawford
GitHub:  github.com/MathewScottCrawford/etas-ford-ai-workflow
License: MIT
Purpose: Verbal walkthrough of the pipeline architecture — definition to delivery
=============================================================================
-->

# Architecture Walkthrough

> See [`architecture_diagram.pdf`](architecture_diagram.pdf) for the visual reference.  
> This document is a verbal description of that diagram — how the system is structured,
> what each component does, and how the layers interact.

---

## Overview

The architecture has two layers: a **toolchain layer** representing the conventional
AUTOSAR ECU development pipeline, and an **AI orchestration layer** that sits on top
of it, adding intelligent assistance at each phase without disrupting existing processes.

The core design principle is **AI assists, humans approve**. No agent writes directly
to any version-controlled artifact. Every agent output carries a confidence score, and
anything below 0.75 automatically routes to a human review gate before any downstream
action is permitted. See [`adr/ADR-001-agent-isolation.md`](adr/ADR-001-agent-isolation.md)
for the architectural decision record.

---

## Pipeline Phases

The toolchain layer is organized as six sequential phases, each with three primary tools
and a dedicated AI agent.

### DEFINE

Requirements authoring and change management. **IBM DOORS** is the system of record for
software requirements. **Jira** tracks change requests and work items. The **RTM Bridge**
(roadmap) will provide automated linkage between DOORS requirement IDs, GitHub commits,
and test results — closing the traceability gap that is one of the most common ASPICE
audit findings. The **Requirements Agent** performs ASPICE SWE.1 quality analysis on
DOORS CSV exports at authoring time, detecting ambiguous language, untestable
requirements, and missing traceability fields before they enter the baseline.

### DESIGN

System and software architecture. **Draw.io / Enterprise Architect** captures
system-level architecture. **Structurizr with C4 notation** provides component and
context views at the software architecture level. The **ARXML Linter** validates schema
correctness and interface consistency. The **Design Agent** (roadmap) will assist with
architecture review and interface tradeoff analysis.

### CONFIGURE

AUTOSAR BSW configuration — the ETAS-specific phase. **ETAS RTA-CAR** is the BSW
configuration tool for AUTOSAR Classic, covering the full stack: OS, COM, DCM, DEM,
NvM, MCAL, and RTE. **MATLAB/Simulink** supports model-based design and automatic C
code generation. **Embedded AI Coder** converts trained neural networks (PyTorch,
TensorFlow) into optimized embedded C for deployment on ECUs. The **Config Agent**
performs automated ARXML diff analysis and cross-module integration risk assessment —
currently the most fully implemented agent in the pipeline, end-to-end tested.

### BUILD

Compilation and static analysis. **GNU Make** orchestrates the build. The **TASKING
Compiler** cross-compiles C code for ECU target architectures. **PC-lint / Polyspace**
enforces MISRA C compliance through static analysis. The **Build Agent** (roadmap) will
triage MISRA findings, suggest rationale for common violation patterns, and flag
safety-classified rules requiring engineer sign-off.

### CI / CT / CD

Continuous integration, test, and delivery. **GitHub** provides source control and
pull request triggers. **Jenkins** orchestrates the CI/CD pipeline. **Docker** ensures
reproducible build environments — every build runs in an identical, version-controlled
container regardless of host machine. The **Test Agent** (roadmap) will generate test
cases from Requirements Agent output and perform failure root cause analysis.

### DELIVER

Validation and release. **dSPACE HIL** provides hardware-in-the-loop validation —
the compiled ECU binary is flashed to real hardware and exercised against a simulated
vehicle environment before release. The **Release Package** assembles binaries, A2L
calibration files, and traceability documentation. The **ETAS AI Calibration Suite**
automates calibration workflows using AI. The **Release Agent** (roadmap) will generate
release notes and sign-off checklists.

---

## AI Orchestration Layer

Three tiers handle all AI capability in the system.

### n8n + LangGraph — Orchestrator

**n8n** is the workflow engine. It handles scheduling, webhook triggers, HTTP routing
between pipeline stages, and the human-in-the-loop approval gates. When an ARXML diff
arrives, n8n receives it via webhook, calls the Config Agent, evaluates the confidence
score, and either approves the result automatically or creates a Jira ticket for human
review before any downstream action proceeds.

**LangGraph** structures the reasoning inside each agent as a formal state machine
rather than a single LLM call. Every agent runs a defined graph — typically three
nodes: parse the input, analyze for risks or issues, generate structured findings.
This makes agent behavior inspectable, debuggable, and consistent.

### Six LangGraph Agents — Reasoners

Each agent is a **FastAPI microservice** exposing a REST endpoint. n8n calls them via
HTTP POST. Agents are independently deployable and versioned.

| Agent | Phase | Status | Function |
|-------|-------|--------|----------|
| Requirements Agent | DEFINE | Code complete | ASPICE SWE.1 analysis on DOORS CSV exports |
| Design Agent | DESIGN | Roadmap | Architecture review and interface tradeoff analysis |
| Config Agent | CONFIGURE | End-to-end tested | ARXML diff analysis and cross-module risk assessment |
| Build Agent | BUILD | Roadmap | MISRA triage and build log analysis |
| Test Agent | CI/CT/CD | Roadmap | Test case generation and failure root cause analysis |
| Release Agent | DELIVER | Roadmap | Release notes generation and sign-off checklist |

All agents share a common output contract: every response includes `confidence_score`,
`human_review_required`, `findings`, and `traceability_refs`. This consistent shape
allows n8n to apply the same approval gate logic regardless of which agent produced
the output.

### Ollama — Local LLM Inference

**Ollama** runs phi4-mini locally — no cloud dependency, no data leaving the network.
This is significant for automotive OEM environments where data sovereignty requirements
prohibit sending design artifacts to external services. GPU acceleration via GTX 970.
The LLM client is configured at temperature 0.1 across all agents — low temperature
keeps outputs deterministic and conservative, which is appropriate for
safety-critical review work.

---

## ISO 26262 Safety Guardrails

Three layers enforce the human-in-the-loop principle:

**Confidence scoring** — each agent computes a score based on change volume, risk
count, and checklist pass rate. Below 0.75, `human_review_required` is set to `true`
automatically regardless of finding severity.

**Severity escalation** — any finding classified as `error` severity (TBD in
requirements, untestable language, critical ARXML pattern) escalates to human review
regardless of confidence score.

**Programmatic gate enforcement** — n8n enforces the gate in the workflow itself.
Low-confidence or error-severity outputs create a Jira ticket; the workflow does not
proceed until that ticket is resolved. This means the gate cannot be bypassed by
schedule pressure the way a process-only gate can.

All agent output is tagged `ai_assisted: true` and `review_status:
pending_human_review | ai_reviewed`. No agent has write access to version-controlled
AUTOSAR artifacts.

---

## Key Design Decisions

**Why LangGraph over a single LLM call?** Multi-step reasoning produces better results
than a single prompt for complex analysis tasks, and the state machine structure makes
the agent's reasoning process inspectable and debuggable. Each node can be tested
independently.

**Why local Ollama over cloud LLM?** Automotive OEM data sovereignty requirements
and network security policies frequently prohibit sending design artifacts to external
APIs. Local inference eliminates that constraint entirely.

**Why n8n for orchestration?** n8n provides a visual workflow designer that makes
the orchestration logic accessible to engineers who are not Python developers, supports
human-in-the-loop approval steps natively, and integrates directly with Jira, GitHub,
Gmail, and other tools already in the pipeline without custom code.

**Why FastAPI for agent services?** FastAPI generates OpenAPI/Swagger documentation
automatically, providing a self-documenting API surface for each agent. This makes
the agents immediately testable via browser without any client code.

---

## Repository Structure Reference

```
etas-ford-ai-workflow/
├── agents/
│   ├── config_agent/       # ARXML review — FastAPI + LangGraph (tested)
│   ├── requirements_agent/ # DOORS analysis — FastAPI + LangGraph (code complete)
│   └── shared/             # Ollama client, ISO 26262 safety guardrails
├── docs/
│   ├── ARCHITECTURE.md            # This document
│   ├── architecture_diagram.pdf   # Visual pipeline diagram (A3 landscape)
│   ├── ASE-workflow-best-practices.pdf  # Common gaps addressed by this design
│   └── adr/
│       └── ADR-001-agent-isolation.md   # Agent isolation decision record
├── scripts/
│   ├── arxml_diff.py        # ARXML change detection utility (tested)
│   └── tests/               # Sample ARXML files for arxml_diff testing
├── workflows/
│   ├── n8n/                 # n8n workflow definitions (JSON)
│   └── jenkins/             # Jenkinsfile CI/CD pipeline
└── infra/
    └── docker-compose.yml   # Full stack: n8n + Ollama + agent services
```

---

*This document reflects the architecture as of March 2026. See the project roadmap
in `README.md` for planned additions.*
