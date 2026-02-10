from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain_community.docstore.document import Document
from src.config.settings import settings

def get_llm():
    """Initialize OpenAI LLM"""
    return ChatOpenAI(
        openai_api_key=settings.openai_api_key,
        model=settings.model_name,
        temperature=settings.temperature
    )

def get_classification_prompt():
    """Get the classification prompt template"""
    template = """You are a Bank Compliance officer analyzing email communication for potential policy violations.
Analyze the target email and flag it as compliant or non-compliant.
If non-compliant, classify it into the appropriate categories and provide reasoning.

Potential Categories:
{potential_categories}

Analyze the following target email:
From: {From}
To: {To}
Subject: {Subject}
Body: {Body}

Follow these steps:
1. Determine if the email is non-compliant or compliant.
2. If non-compliant, assign the most relevant compliance category.
   A single message can fall into multiple categories - assign all applicable ones.
3. Explain the reasoning.
4. Quote lines from the email as evidence.
5. Provide a confidence score on a scale of 1-5 (1 = not sure, 5 = very sure).

Here are example emails for context:
{examples}

Return your answer strictly in this JSON format:
{{
    "non_compliant": "Yes/No",
    "Category": "<category or list of categories>",
    "reason": "<reason>",
    "evidence": ["example line 1", "example line 2"],
    "confidence_score": "<1-5>"
}}
"""
    
    return PromptTemplate(
        input_variables=["From", "To", "Subject", "Body", "potential_categories", "examples"],
        template=template
    )

def create_document_from_row(row, action: str = "") -> Document:
    """Convert a dataframe row to a Document"""
    classification = row.get("Classification", "Compliant")
    category = row.get("Category", "Compliant")
    
    # Handle compliant cases
    if classification == "Compliant" or category is None or category == "":
        category = "Compliant"
    
    doc = Document(
        page_content=row["Body"],
        metadata={
            "From": row["From"],
            "To": row["To"],
            "Subject": row["Subject"],
            "Category": [category] if isinstance(category, str) else category,
            "Classification": classification
        }
    )
    return doc