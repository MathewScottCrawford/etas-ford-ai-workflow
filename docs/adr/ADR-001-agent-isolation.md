# ADR-001: Agent Isolation and Human Approval Gates

> **File:** docs/adr/ADR-001-agent-isolation.md
> **Project:** AI-Assisted Automotive Software Engineering Workflow — ETAS/Ford Motor Company
> **Author:** Mathew S. Crawford | mathew.s.crawford@gmail.com | linkedin.com/in/mathewscrawford
> **License:** MIT | github.com/MathewScottCrawford/etas-ford-ai-workflow



**Date:** 2026-03-13  
**Status:** Accepted  
**Context:** AI-assisted AUTOSAR workflow for safety-critical automotive ECU development

## Decision

Each LangGraph agent operates as an isolated FastAPI microservice with no direct write access to version-controlled AUTOSAR artifacts (ARXML, generated C code, calibration data). All agent outputs must pass through an explicit human approval gate in n8n before entering any controlled baseline.

## Rationale

In an ISO 26262 / ASPICE-governed development environment, AI-generated content cannot be treated as equivalent to engineer-reviewed content without explicit qualification of the AI tool. Until such qualification is in place, agents are advisory only.

## Consequences

- Agents produce structured output with `confidence_score`, `rationale`, and `traceability_refs`
- n8n workflow surfaces output to a human reviewer before any downstream action
- Audit trail is maintained in n8n execution history and optionally in Jira
- AI suggestions are never auto-committed to DOORS baselines or ARXML repositories
