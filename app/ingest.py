from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
import os

class DocumentIngestor:
    def __init__(self, chunk_size=500, chunk_overlap=50):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
    
    def load_pdf(self, pdf_path: str):
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF not found: {pdf_path}")
        loader = PyPDFLoader(pdf_path)
        documents = loader.load()
        for doc in documents:
            doc.metadata["source"] = os.path.basename(pdf_path)
        chunks = self.text_splitter.split_documents(documents)
        print(f"Loaded {len(chunks)} chunks from {pdf_path}")
        return chunks

    def load_pdfs_from_directory(self, directory: str):
        chunks = []
        if not os.path.exists(directory):
            return chunks
        for filename in os.listdir(directory):
            if filename.endswith('.pdf'):
                pdf_path = os.path.join(directory, filename)
                chunks.extend(self.load_pdf(pdf_path))
        return chunks
