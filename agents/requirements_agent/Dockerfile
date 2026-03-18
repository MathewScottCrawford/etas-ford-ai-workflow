# =============================================================================
# File:    agents/requirements_agent/Dockerfile
# Project: AI-Assisted Automotive Software Engineering Workflow
# Author:  Mathew S. Crawford | mathew.s.crawford@gmail.com
# GitHub:  github.com/MathewScottCrawford/etas-ford-ai-workflow
# License: MIT
# Purpose: Container image for requirements_agent FastAPI microservice
# =============================================================================

FROM python:3.10-slim

WORKDIR /app

# Copy shared module and requirements_agent source
COPY agents/shared/ ./agents/shared/
COPY agents/requirements_agent/ ./agents/requirements_agent/
COPY pyproject.toml .

# Install dependencies
RUN pip install --no-cache-dir \
    fastapi>=0.111.0 \
    uvicorn>=0.29.0 \
    langgraph>=0.1.0 \
    langchain-ollama>=0.1.0 \
    pydantic>=2.0.0 \
    python-multipart>=0.0.9

# Make agents a package so relative imports resolve
RUN touch agents/__init__.py

EXPOSE 8002

CMD ["uvicorn", "agents.requirements_agent.main:app", "--host", "0.0.0.0", "--port", "8002"]
