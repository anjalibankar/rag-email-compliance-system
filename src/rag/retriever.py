from typing import List, Dict, Optional
from langchain_community.docstore.document import Document
from src.vectorstore.vector_db import VectorStoreManager
from src.config.settings import settings
import logging

logger = logging.getLogger(__name__)

class ComplianceRetriever:
    """Retrieve similar compliance examples from vector store"""
    
    def __init__(self, vectorstore_manager: Optional[VectorStoreManager] = None):
        """
        Initialize retriever
        
        Args:
            vectorstore_manager: Optional VectorStoreManager instance
        """
        self.vectorstore_manager = vectorstore_manager or VectorStoreManager()
        self.retriever = self._create_retriever()
    
    def _create_retriever(self):
        """Create retriever with configured search parameters"""
        return self.vectorstore_manager.get_retriever()
    
    def get_similar_emails(self, query: str, k: Optional[int] = None) -> List[Document]:
        """
        Retrieve similar emails from vector store
        
        Args:
            query: Email text to search for similar examples
            k: Number of results to return (default from config)
            
        Returns:
            List of similar Document objects
        """
        if k is None:
            k = settings.search_kwargs.get('k', 3)
        
        try:
            similar_docs = self.retriever.get_relevant_documents(query)
            logger.info(f"Retrieved {len(similar_docs)} similar emails for query")
            return similar_docs
        
        except Exception as e:
            logger.error(f"Error retrieving similar emails: {e}")
            return []
    
    def get_similar_by_category(self, query: str, category: str, k: int = 3) -> List[Document]:
        """
        Retrieve similar emails filtered by category
        
        Args:
            query: Email text to search
            category: Compliance category to filter by
            k: Number of results
            
        Returns:
            List of similar documents from specified category
        """
        try:
            # Get more documents than needed for filtering
            all_docs = self.vectorstore_manager.similarity_search(query, k=k*3)
            
            # Filter by category
            filtered_docs = [
                doc for doc in all_docs 
                if category in doc.metadata.get('Category', [])
            ]
            
            # Return top k
            return filtered_docs[:k]
        
        except Exception as e:
            logger.error(f"Error retrieving by category: {e}")
            return []
    
    def get_similar_by_classification(self, query: str, classification: str, k: int = 3) -> List[Document]:
        """
        Retrieve similar emails filtered by classification (compliant/non-compliant)
        
        Args:
            query: Email text to search
            classification: 'compliant' or 'non-compliant'
            k: Number of results
            
        Returns:
            List of similar documents with specified classification
        """
        try:
            # Get more documents for filtering
            all_docs = self.vectorstore_manager.similarity_search(query, k=k*3)
            
            # Filter by classification
            filtered_docs = [
                doc for doc in all_docs 
                if doc.metadata.get('Classification', '').lower() == classification.lower()
            ]
            
            return filtered_docs[:k]
        
        except Exception as e:
            logger.error(f"Error retrieving by classification: {e}")
            return []
    
    def format_examples_for_prompt(self, documents: List[Document]) -> str:
        """
        Format retrieved documents as examples for LLM prompt
        
        Args:
            documents: List of retrieved documents
            
        Returns:
            Formatted string of examples
        """
        if not documents:
            return "No similar examples found. Classify based on general compliance knowledge."
        
        examples = []
        for i, doc in enumerate(documents, 1):
            category = doc.metadata.get('Category', ['Unknown'])
            classification = doc.metadata.get('Classification', 'Unknown')
            
            # Handle category as list or string
            if isinstance(category, list):
                category_str = ', '.join(category)
            else:
                category_str = str(category)
            
            example = f"""Example {i}:
Classification: {classification}
Category: {category_str}
Body: {doc.page_content.strip()}
"""
            examples.append(example)
        
        return "\n".join(examples)
    
    def get_diverse_examples(self, query: str, k: int = 5) -> List[Document]:
        """
        Retrieve diverse examples covering multiple categories
        
        Args:
            query: Email text to search
            k: Total number of examples to return
            
        Returns:
            List of diverse documents
        """
        try:
            # Get more documents
            all_docs = self.vectorstore_manager.similarity_search(query, k=k*2)
            
            # Track categories seen
            seen_categories = set()
            diverse_docs = []
            
            # First pass: one from each category
            for doc in all_docs:
                categories = doc.metadata.get('Category', [])
                if isinstance(categories, list):
                    category_key = tuple(sorted(categories))
                else:
                    category_key = (str(categories),)
                
                if category_key not in seen_categories:
                    diverse_docs.append(doc)
                    seen_categories.add(category_key)
                    
                    if len(diverse_docs) >= k:
                        break
            
            # Second pass: fill remaining slots with most similar
            if len(diverse_docs) < k:
                for doc in all_docs:
                    if doc not in diverse_docs:
                        diverse_docs.append(doc)
                        if len(diverse_docs) >= k:
                            break
            
            logger.info(f"Retrieved {len(diverse_docs)} diverse examples covering {len(seen_categories)} categories")
            return diverse_docs
        
        except Exception as e:
            logger.error(f"Error retrieving diverse examples: {e}")
            return self.get_similar_emails(query, k)
    
    def get_context_for_email(self, subject: str, body: str, use_diverse: bool = True) -> Dict:
        """
        Get complete retrieval context for an email
        
        Args:
            subject: Email subject
            body: Email body
            use_diverse: Whether to get diverse examples
            
        Returns:
            Dictionary with retrieval context
        """
        # Combine subject and body for search
        query = f"{subject} {body}"
        
        # Get examples
        if use_diverse:
            similar_docs = self.get_diverse_examples(query, k=settings.search_kwargs.get('k', 3))
        else:
            similar_docs = self.get_similar_emails(query)
        
        # Format examples
        formatted_examples = self.format_examples_for_prompt(similar_docs)
        
        # Get category distribution from examples
        category_distribution = {}
        for doc in similar_docs:
            categories = doc.metadata.get('Category', [])
            if isinstance(categories, list):
                for cat in categories:
                    category_distribution[cat] = category_distribution.get(cat, 0) + 1
            else:
                category_distribution[str(categories)] = category_distribution.get(str(categories), 0) + 1
        
        return {
            'similar_documents': similar_docs,
            'formatted_examples': formatted_examples,
            'num_examples': len(similar_docs),
            'category_distribution': category_distribution
        }
    
    def search_by_sender_domain(self, query: str, domain: str, k: int = 3) -> List[Document]:
        """
        Retrieve emails from specific sender domain
        
        Args:
            query: Email text to search
            domain: Email domain (e.g., 'enron.com')
            k: Number of results
            
        Returns:
            List of documents from specified domain
        """
        try:
            all_docs = self.vectorstore_manager.similarity_search(query, k=k*3)
            
            # Filter by sender domain
            filtered_docs = [
                doc for doc in all_docs 
                if domain in doc.metadata.get('From', '').lower()
            ]
            
            return filtered_docs[:k]
        
        except Exception as e:
            logger.error(f"Error searching by domain: {e}")
            return []
    
    def get_statistics(self) -> Dict:
        """
        Get retriever statistics
        
        Returns:
            Dictionary with retriever stats
        """
        try:
            # This would require accessing the vector store directly
            # Placeholder for now
            return {
                'retriever_type': settings.search_type,
                'k': settings.search_kwargs.get('k', 3),
                'lambda_mult': settings.search_kwargs.get('lambda_mult', 0.5)
            }
        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            return {}