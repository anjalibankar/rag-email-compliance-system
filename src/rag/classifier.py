import pandas as pd
from typing import List, Dict
from langchain_core.output_parsers import JsonOutputParser
from src.models.llm_models import get_llm, get_classification_prompt, create_document_from_row
from src.vectorstore.vector_db import VectorStoreManager
from src.utils.risk_calculator import RiskCalculator
from src.config.settings import settings

class EmailClassifier:
    """RAG-based email compliance classifier"""
    
    def __init__(self):
        self.vectorstore_manager = VectorStoreManager()
        self.llm = get_llm()
        self.retriever = self.vectorstore_manager.get_retriever()
        self.prompt = get_classification_prompt()
        self.parser = JsonOutputParser()
        self.risk_calculator = RiskCalculator()
    
    def load_sample_data(self, file_obj) -> None:
        """Load sample data into vector store"""
        df = pd.read_csv(file_obj)
        documents = []
        
        for _, row in df.iterrows():
            doc = create_document_from_row(row, "training")
            documents.append(doc)
        
        self.vectorstore_manager.add_documents(documents)
        print(f"Loaded {len(documents)} sample emails into vector store")
    
    def _format_examples(self, similar_docs: List) -> str:
        """Format similar documents as examples"""
        examples = []
        for doc in similar_docs:
            category = doc.metadata.get('Category', ['Unknown'])
            examples.append(
                f"Category: {category}\n"
                f"Body: {doc.page_content.strip()}\n"
            )
        return "\n".join(examples)
    
    def classify_email(self, row: pd.Series) -> Dict:
        """Classify a single email"""
        # Retrieve similar examples
        similar_docs = self.retriever.get_relevant_documents(row["Body"])
        examples_str = self._format_examples(similar_docs)
        
        # Prepare prompt input
        prompt_input = {
            "From": row["From"],
            "To": row["To"],
            "Subject": row["Subject"],
            "Body": row["Body"],
            "potential_categories": "\n".join(f"- {cat}" for cat in settings.categories),
            "examples": examples_str
        }
        
        # Run classification chain
        chain = self.prompt | self.llm | self.parser
        result = chain.invoke(prompt_input)
        
        # Parse result
        category = result.get("Category", "Compliant")
        if category == "nan" or not category:
            category = "Compliant"
        
        # Handle list categories
        if isinstance(category, list):
            category = ", ".join(category)
        
        classification = "Non-Compliant" if result.get("non_compliant") == "Yes" else "Compliant"
        
        # Calculate risk score
        category_list = [cat.strip() for cat in category.split(",")]
        risk_score = self.risk_calculator.calculate_risk_score(
            category_list, row["From"], row["To"]
        )
        
        return {
            "Classification": classification,
            "Category": category,
            "Risk Score": risk_score,
            "From": row["From"],
            "To": row["To"],
            "Subject": row["Subject"],
            "Body": row["Body"],
            "Reason": result.get("reason", ""),
            "Evidence": result.get("evidence", [""])[0] if result.get("evidence") else "",
            "Confidence Score": result.get("confidence_score", "")
        }
    
    def classify_batch(self, file_obj) -> List[Dict]:
        """Classify multiple emails from CSV"""
        test_df = pd.read_csv(file_obj)
        results = []
        
        print(f" Classifying {len(test_df)} emails...")
        
        for idx, row in test_df.iterrows():
            try:
                print(f" Processing {idx + 1}/{len(test_df)}...", end='\r')
                result = self.classify_email(row)
                result['idx'] = idx
                results.append(result)
            except Exception as e:
                print(f"\n Error on email {idx}: {e}")
        
        # Filter and sort non-compliant emails
        non_compliant = [r for r in results if r["Classification"] == "Non-Compliant"]
        sorted_results = sorted(non_compliant, key=lambda x: x["Risk Score"], reverse=True)
        
        print(f"\n Found {len(sorted_results)} non-compliant emails")
        return sorted_results
    
    def add_classified_emails(self, df: pd.DataFrame):
        """Add classified emails back to vector store"""
        documents = []
        for _, row in df.iterrows():
            doc = create_document_from_row(row, "classified")
            documents.append(doc)
        
        self.vectorstore_manager.add_documents(documents)
        print(f" Added {len(documents)} classified emails to vector store")