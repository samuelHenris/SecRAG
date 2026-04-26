from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
import google.generativeai as genai
import os

class SecRAG:
    def __init__(self, api_key: str, model_name: str = "gemini-2.0-flash"):
        self.api_key = api_key
        self.model_name = model_name
        print("Loading embedding model...")
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)
        self.vector_store_path = "data/faiss_index"
        self.vector_store = None
        if os.path.exists(self.vector_store_path):
            try:
                self.vector_store = FAISS.load_local(
                    self.vector_store_path, self.embeddings,
                    allow_dangerous_deserialization=True
                )
            except:
                pass

    def ingest_documents(self, chunks):
        if self.vector_store is None:
            self.vector_store = FAISS.from_documents(chunks, self.embeddings)
        else:
            self.vector_store.add_documents(chunks)
        os.makedirs(os.path.dirname(self.vector_store_path), exist_ok=True)
        self.vector_store.save_local(self.vector_store_path)
        return len(chunks)

    def query(self, question: str, k: int = 4):
        if self.vector_store is None:
            return "No documents ingested yet.", []
        
        docs = self.vector_store.similarity_search(question, k=k)
        context = "\n\n".join([doc.page_content for doc in docs])
        sources = list(set([doc.metadata.get('source', 'unknown') for doc in docs]))
        
        prompt = f"""Answer based ONLY on the context below.

Context:
{context}

Question: {question}

Answer:"""
        
        try:
            response = self.model.generate_content(prompt)
            return response.text, sources
        except Exception as e:
            return f"Error: {str(e)}", sources
