from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import os, shutil, logging
from ingest import DocumentIngestor
from rag import SecRAG

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="SecRAG", version="1.0.0")
API_KEY = os.getenv("GEMINI_API_KEY", "")
DATA_DIR = os.getenv("DATA_DIR", "data/docs")
os.makedirs(DATA_DIR, exist_ok=True)

ingestor = DocumentIngestor()
rag = SecRAG(api_key=API_KEY)

class QueryRequest(BaseModel):
    question: str

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/ingest")
async def ingest(file: UploadFile = File(...)):
    if not file.filename.endswith('.pdf'):
        raise HTTPException(400, "Only PDFs supported")
    file_path = os.path.join(DATA_DIR, file.filename)
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    chunks = ingestor.load_pdf(file_path)
    num = rag.ingest_documents(chunks)
    return {"status": "ingested", "filename": file.filename, "chunks": num}

@app.post("/query")
async def query(req: QueryRequest):
    answer, sources = rag.query(req.question)
    return {"answer": answer, "sources": sources}

if __name__ == "__main__":
    import uvicorn
    print("\nSecRAG starting on http://0.0.0.0:8000\n")
    uvicorn.run(app, host="0.0.0.0", port=8000)
