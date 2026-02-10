from typing import List
from src.config.settings import settings

class RiskCalculator:
    """Calculate risk scores for emails"""
    
    @staticmethod
    def calculate_risk_score(categories: List[str], sender: str, receiver: str) -> float:
        """
        Calculate risk score based on categories and email domains
        
        Args:
            categories: List of compliance categories
            sender: Sender email address
            receiver: Receiver email address
            
        Returns:
            Risk score (float)
        """
        risk_score = 0
        
        # Check if email is external
        sender_domain = sender.split('@')[-1].lower()
        receiver_domain = receiver.split('@')[-1].lower()
        
        external_score = 0
        for domain in settings.trusted_domains:
            if sender_domain != domain or receiver_domain != domain:
                external_score = 1
                break
        
        # Add category weights
        for cat in categories:
            cat = cat.strip()
            category_weight = settings.weights.get(cat)
            if category_weight is not None:
                risk_score += category_weight
        
        risk_score += external_score
        return round(risk_score, 2)