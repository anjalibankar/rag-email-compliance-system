from typing import Optional
from src.config.settings import settings
from src.models.llm_models import get_llm
from src.vectorstore.vector_db import VectorStoreManager

class SharedResources:
    """
    Singleton class to manage shared resources across the application.
    Ensures LLM and vector store are initialized only once.
    """
    
    _instance = None
    _initialized = False
    
    # Shared resources
    llm = None
    vectorstore_manager = None
    retriever = None
    categories = None
    weights = None
    
    def __new__(cls):
        """Implement singleton pattern"""
        if cls._instance is None:
            cls._instance = super(SharedResources, cls).__new__(cls)
        return cls._instance
    
    @classmethod
    def initialize(cls):
        """Initialize all shared resources"""
        if cls._initialized:
            return
        
        # Initialize LLM
        cls.llm = get_llm()
        
        # Initialize vector store manager
        cls.vectorstore_manager = VectorStoreManager()
        
        # Initialize retriever
        cls.retriever = cls.vectorstore_manager.get_retriever()
        
        # Load categories and weights from config
        cls.categories = settings.categories
        cls.weights = settings.weights
        
        cls._initialized = True
    
    @classmethod
    def get_llm(cls):
        """Get shared LLM instance"""
        if not cls._initialized:
            cls.initialize()
        return cls.llm
    
    @classmethod
    def get_vectorstore_manager(cls):
        """Get shared vector store manager instance"""
        if not cls._initialized:
            cls.initialize()
        return cls.vectorstore_manager
    
    @classmethod
    def get_retriever(cls):
        """Get shared retriever instance"""
        if not cls._initialized:
            cls.initialize()
        return cls.retriever
    
    @classmethod
    def get_categories(cls):
        """Get compliance categories"""
        if not cls._initialized:
            cls.initialize()
        return cls.categories
    
    @classmethod
    def get_weights(cls):
        """Get category weights"""
        if not cls._initialized:
            cls.initialize()
        return cls.weights
    
    @classmethod
    def reload_vectorstore(cls):
        """Reload vector store after adding new data"""
        cls.vectorstore_manager = VectorStoreManager()
        cls.retriever = cls.vectorstore_manager.get_retriever()