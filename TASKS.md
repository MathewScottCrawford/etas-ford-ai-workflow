# =============================================================================
# File:    TASKS.md
# Project: AI-Assisted Automotive Software Engineering Workflow
# Author:  Mathew S. Crawford | mathew.s.crawford@gmail.com
# GitHub:  github.com/MathewScottCrawford/etas-ford-ai-workflow
# License: MIT
# Purpose: Active task tracking — current work only, not a backlog
# =============================================================================

# TASKS.md — etas-ford-ai-workflow
---
last-updated: 2026-03-19
---

## Active

- [ ] Fix n8n HTTP Request timeout 30000 → 300000ms, republish, retest
- [ ] Export updated autosar_review_workflow.json from n8n after timeout fix
- [ ] requirements_agent E2E test (port 8002 running, sample_doors_export.csv)
- [ ] Commit — Dockerfiles, docker-compose.yml, workflow JSON
- [ ] GitHub Actions CI — trigger via push

## Recently Completed

- [x] Docker Compose full stack verified — all 3 containers healthy
- [x] n8n existing workflows restored (n8n_n8n_data external volume)
- [x] AUTOSAR review workflow imported and published in n8n
- [x] Pipeline reaching Ollama — blocked only by 30s timeout
- [x] agent Dockerfiles written (config_agent, requirements_agent)
- [x] docker-compose.yml updated — removed Ollama service, host.docker.internal
- [x] config_agent E2E tested (7-change COM diff, confidence 0.8, < 5s)
- [x] arxml_diff.py tested (COM/OS/DCM module filter verified)
- [x] clean_json() fix — LLM markdown fence stripping in both agents
- [x] pyproject.toml — editable install working on Python 3.10.4
- [x] Architecture deck (etas_ford_portfolio.pptx — 5 slides)
- [x] ARCHITECTURE.md — full pipeline walkthrough
- [x] ASE-workflow-best-practices.pdf — BP-01 through BP-10
- [x] HANDOFF.md — session state snapshot
- [x] File headers — all source files updated
