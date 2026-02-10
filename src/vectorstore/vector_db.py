from langchain_community.embeddings.huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores.faiss import FAISS
from langchain_community.docstore.document import Document
from typing import List
from pathlib import Path
from src.config.settings import settings

class VectorStoreManager:
    """Manage FAISS vector store operations"""
    
    def __init__(self):
        self.embedding_model = HuggingFaceEmbeddings(
            model_name=settings.embedding_model
        )
        self.persist_dir = Path(settings.persist_directory)
        self.vectorstore = self._load_or_create()
    
    def _load_or_create(self):
        """Load existing vector store or create new one"""
        if self.persist_dir.exists():
            print(f"Loading existing vector store from {self.persist_dir}")
            return FAISS.load_local(
                str(self.persist_dir),
                self.embedding_model,
                allow_dangerous_deserialization=True
            )
        else:
            print("Creating new vector store")
            # Create empty vector store
            return FAISS.from_texts(
                ["initialization"],
                self.embedding_model
            )
    
    def add_documents(self, documents: List[Document]):
        """Add documents to vector store"""
        self.vectorstore.add_documents(documents)
        self.save()
    
    def save(self):
        """Persist vector store to disk"""
        self.persist_dir.parent.mkdir(parents=True, exist_ok=True)
        self.vectorstore.save_local(str(self.persist_dir))
        print(f" Vector store saved to {self.persist_dir}")
    
    def get_retriever(self):
        """Get retriever instance"""
        return self.vectorstore.as_retriever(
            search_type=settings.search_type,
            search_kwargs=settings.search_kwargs
        )
    
    def similarity_search(self, query: str, k: int = 3):
        """Search for similar documents"""
        return self.vectorstore.similarity_search(query, k=k)