# SecRAG - Security RAG Pipeline
Upload security PDFs (CVE reports, OWASP guides, pentest reports) and query them with natural language.

## What It Does
Ask "what vulnerabilities were found?" and get an answer from YOUR documents - not generic AI responses.

## Tech Stack
- **FastAPI** - API framework
- **LangChain** - RAG pipeline orchestration
- **FAISS** - Local vector database
- **HuggingFace** - Local embeddings (data never leaves your infra)
- **Google Gemini 2.0 Flash** - LLM for generating answers (free tier)
- **Docker + Kubernetes** - Deployment with security hardening

Kubernetes Security Hardening
Dedicated namespace (blast radius containment)

Non-root container, read-only filesystem, all capabilities dropped

Default-deny network policy (only HTTPS out to Gemini API)

RBAC with minimum permissions

API key in Kubernetes Secret- never in code, logs, or images

Local embeddings - document content never leaves your infrastructure

## Quick Start
```bash
git clone https://github.com/samuelHenris/SecRAG.git
cd SecRAG
python3 -m venv venv
source venv/bin/activate
pip install -r app/requirements.txt
export GEMINI_API_KEY='your-key-here'
python app/main.py

# Ingest
curl -X POST -F "file=@OWASP_Top10.pdf" http://localhost:8000/ingest

# Query
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question":"What are the top security risks?"}'

