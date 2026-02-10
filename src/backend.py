from src.rag.classifier import EmailClassifier

class ComplianceBackend:
    """Main backend interface for Streamlit app"""
    
    def __init__(self):
        self.classifier = EmailClassifier()
    
    def load_sample_data(self, file_obj):
        """Load sample training data"""
        self.classifier.load_sample_data(file_obj)
    
    def classify_emails(self, file_obj):
        """Classify test emails"""
        return self.classifier.classify_batch(file_obj)
    
    def update_vectorstore_with_classified(self, dataframe):
        """Add classified emails to vector store"""
        self.classifier.add_classified_emails(dataframe)