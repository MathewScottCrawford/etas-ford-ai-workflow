# PROJECT_STATE.md
# =============================================================================
# File:    PROJECT_STATE.md
# Project: AI-Assisted Automotive Software Engineering Workflow (MAPS)
# Author:  Mathew S. Crawford | mathew.s.crawford@gmail.com
# GitHub:  github.com/MathewScottCrawford/etas-ford-ai-workflow
# License: MIT
# Purpose: Living project state — read by Claude Code at session start,
#          updated at session end. Source of truth for current status,
#          decisions made, and next actions.
#          Part of MAPS (Mathew's Agentic Pipeline Stack).
# =============================================================================

## How to Use This File

- **Claude Code:** Read this entire file before touching anything.
  Then read CLAUDE.md if you haven't already.
- **Mathew:** Update the Active Tasks and Session Log sections after
  each session. Keep Decision Log entries permanent — never delete them.

---

## Current Status — March 2026

| Component | Status |
|-----------|--------|
| Docker Compose stack | ✅ Verified — all 3 containers healthy |
| config_agent (port 8001) | ✅ E2E tested — 7-change COM diff, confidence 0.8 |
| requirements_agent (port 8002) | ⚠️ Code complete — E2E test pending |
| arxml_diff.py | ✅ Tested — COM/OS/DCM module filter working |
| email_catchup_workflow (n8n) | ✅ Running — daily Gmail catchup |
| AUTOSAR review workflow (n8n) | ⚠️ Imported and published — blocked by 30s timeout |
| safety_guardrails.py | ⚠️ Code complete — not independently validated |
| GitHub Actions CI | ⚠️ ci.yml committed — needs push to trigger |
| Jenkinsfile | ❌ Needs Jenkins instance |
| Agent Dockerfiles | ✅ Written and building cleanly |

---

## Active Tasks

Priority order:

- [ ] **Fix n8n HTTP Request timeout** — Config Agent node: change timeout
      from 30000ms to 300000ms (5 min). Republish workflow. Retest with curl.
      Then export updated JSON to `workflows/n8n/autosar_review_workflow.json`.
- [ ] **requirements_agent E2E test** — containers already running on port 8002.
      Use Swagger UI at `http://localhost:8002/docs`, upload
      `agents/requirements_agent/tests/sample_doors_export.csv` to `/analyze/csv`.
- [ ] **Export updated autosar_review_workflow.json** from n8n after timeout fix.
- [ ] **GitHub Actions CI** — trigger by pushing a commit, verify green.
- [ ] **Commit** — CLAUDE.md, PROJECT_STATE.md, Dockerfiles,
      docker-compose.yml, workflow JSON.

---

## Phase Completion Map

```
DEFINE        [ ] Requirements Agent — roadmap
DESIGN        [ ] Design Agent — roadmap
CONFIGURE     [✅] config_agent E2E tested
              [⚠️] requirements_agent code complete, E2E pending
              [✅] arxml_diff.py tested
              [⚠️] n8n AUTOSAR review workflow — timeout fix pending
BUILD         [ ] Build Agent — roadmap
CI/CT/CD      [⚠️] GitHub Actions — needs trigger
              [⚠️] Docker Compose — verified but needs full workflow test
              [ ] Jenkinsfile — needs Jenkins instance
              [ ] Test Agent — roadmap
DELIVER       [ ] Release Agent — roadmap
              [ ] dSPACE HIL integration — roadmap
INFRASTRUCTURE[✅] Docker container environment
              [✅] Agentic workflow prototype (n8n email catchup)
              [✅] LLM Agent prototype (phi4-mini via Ollama)
              [✅] Architecture diagram, best practices PDF, ARCHITECTURE.md
              [✅] CLAUDE.md, PROJECT_STATE.md (MAPS onboarding)
              [⚠️] safety_guardrails.py — not independently validated
              [✅] pyproject.toml editable install
              [✅] Full repo — headers, ADR, README
```

---

## Decision Log

Permanent record — never delete entries. Add new ones at the bottom.

### ADR-001 — Agent Isolation Principle
**Decision:** No agent writes directly to any version-controlled AUTOSAR artifact.
All agent output carries `confidence_score` and `human_review_required` flags.
n8n enforces the human approval gate programmatically.
**Why:** ISO 26262 requires tool qualification for safety-relevant AI tooling.
Programmatic gates cannot be bypassed by schedule pressure the way process-only
gates can.
**Rejected alternative:** Auto-commit high-confidence results directly.
Rejected because confidence scoring is not yet validated against real program data.

### ADR-002 — Native Ollama, Not Containerized
**Decision:** Ollama runs natively on Windows host (`D:\ollama`).
Containers reach it via `host.docker.internal:11434`.
**Why:** GPU passthrough in Docker Desktop on Windows (WSL2) is unreliable
with GTX 970 / CUDA 5.2. Native Ollama has direct GPU access, verified working.
**Rejected alternative:** Containerized Ollama with nvidia-container-toolkit.
Rejected due to port conflict risk and GPU passthrough complexity on this hardware.

### ADR-003 — Repo Root Build Context
**Decision:** Docker Compose build context is repo root (`context: ..`),
not agent subfolder.
**Why:** Dockerfiles need to COPY from `agents/shared/` which is outside
any individual agent folder. Root context is the only way to access it.
**Impact:** All Dockerfiles must reference files relative to repo root.

### ADR-004 — Python 3.10.4 for All Agent Work
**Decision:** All agent development uses Python 3.10.4 (`py -3.10`).
**Why:** LangGraph and pydantic v2 compatibility. Python 3.14 (default on
this machine) has compatibility issues with several agent dependencies.
**Impact:** Virtual env is `.venv-agents` created with `py -3.10 -m venv`.

### ADR-005 — n8n Volume External Reference
**Decision:** n8n uses `n8n_n8n_data` volume with `external: true` in
docker-compose.yml.
**Why:** This volume was created by a standalone n8n run prior to Docker
Compose setup and contains existing workflows and credentials.
`infra_n8n_data` and `n8n_data` are incorrect — they are empty volumes.
**Critical:** Never run `docker compose down -v` — destroys workflow data.

### ADR-006 — MAPS Workflow Adoption
**Decision:** Development workflow migrated to MAPS (Mathew's Agentic
Pipeline Stack): claude.ai chat for design/architecture, Claude Code via
Nimbalyst for implementation, CLAUDE.md + PROJECT_STATE.md as the bridge.
**Why:** Download/upload cycle between chat and repo is the right learning
approach for understanding, but Claude Code via Nimbalyst provides
diff-level visibility and direct repo access for implementation tasks.
**CLAUDE.md** is derived from ai-os/_system/ source files. Update ai-os
first, then recompile CLAUDE.md.

---

## Known Issues / Watch Points

- **phi4-mini cold start:** ~35 second model load + 4 min first inference.
  n8n timeout was 30s — fix to 300000ms (5 min) is the immediate next task.
  Subsequent calls while model is warm: ~2 min.
- **n8n webhook body:** Payload lands in `$json.body`, not `$json`.
  Always use `{{ $json.body }}` in HTTP Request node JSON field.
- **Git Bash path mangling:** `/data` gets mangled. Use `//data` or
  `winpty` prefix, or use PowerShell.
- **requirements_agent prompt tuning:** Unknown whether phi4-mini handles
  ASPICE SWE.1 analysis adequately on first pass. May need prompt iteration.
- **safety_guardrails.py:** Only exercised through config_agent test.
  Not independently validated. Treat as unverified until tested directly.

---

## Startup Sequence

```bash
# 1. Docker Desktop (must be running)
# 2. Full stack
docker compose -f infra/docker-compose.yml up -d
# 3. Ollama — native Windows, separate terminal
ollama serve
# 4. Verify
curl http://localhost:8001/health
curl http://localhost:8002/health
# 5. n8n UI: http://localhost:5678
```

## Shutdown Sequence

```bash
docker compose -f infra/docker-compose.yml stop
# Stop Ollama: Ctrl+C in ollama terminal, or:
# Get-Process | Where-Object {$_.Name -like "*ollama*"} | Stop-Process -Force
```

---

## Session Log

### 2026-03-18 — Docker Compose + n8n AUTOSAR Workflow
**Completed:**
- Docker Compose full stack verified — all 3 containers healthy
- n8n existing workflows restored via n8n_n8n_data external volume
- Agent Dockerfiles written (config_agent, requirements_agent)
- docker-compose.yml updated — removed Ollama service, host.docker.internal
- AUTOSAR review workflow imported and published in n8n
- Pipeline verified reaching Ollama — blocked only by 30s timeout
- phi4-mini loaded successfully, inference confirmed working (4min26s first call)

**Decisions made:** ADR-002, ADR-003, ADR-005

**Blocked by:** n8n HTTP Request timeout 30s < phi4-mini cold start + inference

### 2026-03-19 — MAPS Migration, CLAUDE.md
**Completed:**
- MAPS workflow defined and adopted (ADR-006)
- CLAUDE.md written for repo root — Claude Code runtime instructions
- PROJECT_STATE.md created (replaces HANDOFF.md)
- ai-os updated: MAPS definition in IDENTITY.md and MEMORY.md
- Nimbalyst installed

**Next session start:** Fix n8n timeout → test full pipeline E2E
