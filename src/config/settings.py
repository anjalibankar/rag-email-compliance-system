import yaml
import os
from pathlib import Path
from dotenv import load_dotenv

class Settings:
    """Application settings and configuration"""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        load_dotenv()
        self.config_path = Path(config_path)
        self._load_config()
        self._load_env_vars()
    
    def _load_config(self):
        """Load YAML configuration"""
        with open(self.config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        # Model settings
        self.model_name = config['model']['name']
        self.temperature = config['model']['temperature']
        
        # Embeddings
        self.embedding_model = config['embeddings']['model_name']
        
        # Vector store
        self.vectorstore_type = config['vectorstore']['type']
        self.persist_directory = config['vectorstore']['persist_directory']
        self.search_type = config['vectorstore']['search_type']
        self.search_kwargs = config['vectorstore']['search_kwargs']
        
        # Categories and weights
        self.categories = config['categories']
        self.weights = config['weights']
        
        # Domains
        self.trusted_domains = config.get('trusted_domains', ['enron.com'])
    
    def _load_env_vars(self):
        """Load environment variables"""
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        
        # Validate
        if not self.openai_api_key:
            raise ValueError("Missing OPENAI_API_KEY environment variable")

# Global settings instance
settings = Settings()