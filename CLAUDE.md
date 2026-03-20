# CLAUDE.md
# =============================================================================
# File:    CLAUDE.md
# Project: AI-Assisted Automotive Software Engineering Workflow (MAPS)
# Author:  Mathew S. Crawford | mathew.s.crawford@gmail.com
# GitHub:  github.com/MathewScottCrawford/etas-ford-ai-workflow
# License: MIT
# Purpose: Claude Code runtime instructions — read at the start of every session
#
# SOURCE OF TRUTH: This file is derived from ai-os/_system/ (SOUL.md,
# IDENTITY.md, USER.md). When preferences change, update ai-os first,
# then recompile here.
# =============================================================================

## Project Identity

This is the **ETAS/Ford AI-Assisted Automotive Software Engineering Workflow** —
a reference implementation of an AI-assisted AUTOSAR Classic ECU development
pipeline targeting a Sr. Automotive Software Engineering Consultant engagement
with ETAS Inc. / Ford Motor Company.

This project is part of **MAPS (Mathew's Agentic Pipeline Stack)** — the
development workflow combining claude.ai chat (design/architecture) with
Claude Code via Nimbalyst (implementation), with this file as the bridge.

**Owner:** Mathew S. Crawford | mathew.s.crawford@gmail.com | 734-765-4143
**Repo:** github.com/MathewScottCrawford/etas-ford-ai-workflow

---

## Current Project State

See `PROJECT_STATE.md` for:
- What is working end-to-end
- What is in progress
- What is on the roadmap
- Architectural decisions made and why
- Open questions

**Always read PROJECT_STATE.md before starting any session.**

---

## Architectural Constraints — DO NOT VIOLATE

These are hard rules. Flag before deviating, never silently work around them.

1. **Agent isolation (ADR-001):** No agent writes directly to any
   version-controlled AUTOSAR artifact. All agent output must carry
   `confidence_score` and `human_review_required` flags. The n8n workflow
   enforces the human approval gate — do not bypass it.

2. **Ollama runs natively on Windows host** — NOT in Docker. Containers
   reach it via `host.docker.internal:11434`. Do not add an Ollama service
   to docker-compose.yml.

3. **n8n data volume is `n8n_n8n_data` (external: true)** — this volume
   contains existing workflows and credentials. Never run
   `docker compose down -v` — it destroys the volume.

4. **Build context is repo root** — Dockerfiles for agents use `context: ..`
   so they can access `agents/shared/`. Do not change build context to an
   agent subfolder.

5. **Python version is 3.10.4** — all agent work uses `py -3.10`. Do not
   introduce dependencies that require 3.11+.

6. **Relative imports only** — use `from .graph import ...` not
   `from graph import ...`. Editable install via `pip install -e .` handles
   resolution. Do not add sys.path hacks.

7. **No changes to `agents/shared/`** without explicit discussion —
   safety_guardrails.py and llm_client.py are shared across all agents.
   A change here affects every agent simultaneously.

---

## Behavioral Requirements — ALWAYS FOLLOW

These are non-negotiable working style requirements.

- **Explain the why before making any change.** State what you're about to
  do and why before touching any file. This is not optional — it is the
  primary learning mechanism.

- **Ask clarifying questions before acting on ambiguous instructions.**
  Do not fill gaps with assumptions. Surface the ambiguity and resolve it
  first.

- **One file change at a time, with approval between each.** Do not batch
  multiple file changes into a single step without explicit go-ahead. Show
  the diff, wait for approval, then proceed.

- **Follow Conventional Commits format** for all commit messages:
  `type(scope): description` — feat, fix, docs, chore, refactor, test.
  Always include an extended description body for non-trivial commits.

- **Flag any deviation from existing architecture before proceeding.**
  If the right solution requires changing an architectural constraint above,
  say so explicitly — do not work around it silently.

- **Never use `docker compose down -v`.** Use `docker compose stop` or
  `docker compose down` (without `-v`) only.

- **Never commit without explicit go-ahead.** Stage, show the diff, get
  approval, then commit.

---

## Environment Reference

| Tool | Detail |
|------|--------|
| OS | Windows 11 |
| Shell | Git Bash (MINGW64) |
| Editor | VSCode |
| Git client | Fork GUI + Git Bash |
| Python | 3.10.4 (`py -3.10`) |
| Venv | `.venv-agents` — activate: `source .venv-agents/Scripts/activate` |
| Docker | Docker Desktop, WSL2 VHDX on D: drive |
| Ollama | Native Windows, models at `D:\ollama`, port 11434 |
| GPU | GTX 970, 4GB VRAM, CUDA compute 5.2 |
| Model | phi4-mini (cold start ~35s, first inference ~4min, warm ~2min) |

**Key paths:**
- Repo root: `D:\Workspaces\etas-ford-ai-workflow\`
- n8n UI: `http://localhost:5678`
- config_agent: `http://localhost:8001` (Docker)
- requirements_agent: `http://localhost:8002` (Docker)
- Ollama: `http://localhost:11434` (native)

**Git Bash gotchas:**
- Use `source .venv-agents/Scripts/activate` (not backslashes)
- Use `//data` not `/data` in docker exec commands (path mangling)
- Use `winpty` prefix for interactive Docker commands

---

## Stack Reference

```
agents/config_agent/        FastAPI + LangGraph — ARXML review (E2E tested)
agents/requirements_agent/  FastAPI + LangGraph — DOORS analysis (code complete)
agents/shared/              Ollama client, ISO 26262 safety guardrails (shared)
scripts/arxml_diff.py       ARXML change detection utility (tested)
workflows/n8n/              n8n workflow definitions
infra/docker-compose.yml    Full stack — n8n + agents (Ollama is native)
docs/ARCHITECTURE.md        Full pipeline walkthrough
docs/ASE-workflow-best-practices.pdf  BP-01 through BP-10
pyproject.toml              Editable install — pip install -e .
PROJECT_STATE.md            Current state, decisions, roadmap (read first)
```

---

## ISO 26262 Safety Awareness

This is an automotive safety-critical context. The confidence scoring and
human approval gate are not suggestions — they are the core safety design.

- AI output confidence < 0.75 → `human_review_required: true`
- Error severity findings → escalate regardless of confidence
- No agent output enters the AUTOSAR baseline without human review

When in doubt, add a gate. Do not remove existing gates.
