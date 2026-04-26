# SecRAG
A self-hosted RAG pipeline for querying security documents.

Security teams can't paste confidential client reports, internal CVEs, 
or pentest findings into ChatGPT. This runs entirely in your own 
infrastructure. Upload your PDFs, ask questions in plain English, get 
answers from your actual documents.

## How It Works

1. You upload a PDF (CVE report, OWASP guide, pentest finding)
2. LangChain splits it into chunks, HuggingFace embeds them locally
3. Chunks are stored in a local FAISS vector index
4. You ask a question, the top 4 most relevant chunks are retrieved
5. Gemini generates an answer grounded in those chunks only

Embeddings run entirely on your machine. Document content never 
leaves your infrastructure.

## Tech Stack

- FastAPI - REST API
- LangChain - RAG pipeline orchestration  
- FAISS - Local vector database
- HuggingFace sentence-transformers - Local embeddings
- Google Gemini 2.0 Flash - Answer generation
- Docker + Kubernetes - Deployment

## Kubernetes Security Hardening

Every decision here was intentional:

| Control | Why |
|---|---|
| Dedicated namespace | Blast radius containment if pod is compromised |
| Non-root container | Prevents privilege escalation |
| Read-only filesystem | Attacker cannot write malicious files inside container |
| All Linux capabilities dropped | Removes low-level OS access |
| Default-deny NetworkPolicy | No lateral movement possible, only HTTPS out to Gemini |
| RBAC with least privilege | Pod cannot access cluster resources it does not own |
| API key in Kubernetes Secret | Never in code, image layers, or logs |
| Local HuggingFace embeddings | Document content never leaves your infrastructure |

## Run Locally

git clone https://github.com/samuelHenris/SecRAG.git
cd SecRAG
python3 -m venv venv
source venv/bin/activate
pip install -r app/requirements.txt
export GEMINI_API_KEY='your-key-here'
python app/main.py

## API

# Ingest a PDF
curl -X POST -F "file=@OWASP_Top10.pdf" \
  http://localhost:8000/ingest

# Query your documents  
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question":"What access control vulnerabilities were found?"}'

# Health check
curl http://localhost:8000/health

## Deploy on Kubernetes

kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/secret.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/rbac.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/network-policy.yaml
