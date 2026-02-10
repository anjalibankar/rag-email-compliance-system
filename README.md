# Email Compliance Surveillance System (RAG-based)

## Overview
This project is an AI-driven email compliance surveillance system designed for regulated industries such as banking and financial services.
It uses Retrieval-Augmented Generation (RAG) to analyze email communications, detect potential compliance violations, classify them into risk categories, and assign risk scores with supporting evidence.

The system combines:
- historical labeled emails (institutional memory)
- semantic search using vector databases
- Large Language Models (LLMs) for reasoning

## Key Features
- Upload Sample (Training) Data
  - Load labeled historical emails (compliant / non-compliant)
  - Create embeddings and store them in a FAISS vector database
- Check Compliance Alerts
  - Analyze new, unlabeled emails
  - Retrieve similar past examples using semantic search
  - Use an LLM to classify compliance violations
  - Generate risk scores, reasoning, and evidence
- Compliance Reporting
  - Risk-prioritized alerts
  - Summary metrics (total violations, high-risk emails)
  - Downloadable CSV reports for audit and investigation


## Architecture
Streamlit UI -> ComplianceBackend -> EmailClassifier (RAG Pipeline) -> FAISS Vector Store (Historical Emails) -> LLM (Reasoning + Classification) -> Risk Scoring Engine

## RAG Flow
- Retrieve semantically similar historical emails from FAISS
- Inject retrieved examples into the LLM prompt
- Classify compliance violations with reasoning and evidence
- Calculate risk scores based on category and participants

## Setup Instructions
Prerequisites
- Python 3.10+
- uv package manager
- OpenAI API key

1️⃣ Clone the Repository
- git clone https://github.com/anjalibankar/rag-email-compliance-system.git
- cd ag-email-compliance-system

2️⃣ Install Dependencies
uv sync

3️⃣ Set Environment Variables
OPENAI_API_KEY=your_api_key_here

4️⃣ (Important) Reset Vector Store on First Run
rm -rf vectorstore/faiss_index_store

5️⃣ Run the Application
streamlit run app/Home.py

## Notes
- Delete vectorstore/faiss_index_store before first run


## How to Use the Application
- Step 1: Upload Sample Data
  -  Navigate to Upload Sample Data
  - Upload a CSV with labeled emails:
    - Classification: compliant / non-compliant
    - Category: compliance category
  - This builds the vector database (institutional memory)
 
- Step 2: Check Alerts
- Navigate to Check Alerts
- Upload a CSV with unlabeled emails
- The system will:
    - retrieve similar examples
    - classify violations
    - calculate risk scores
    - generate a downloadable compliance report


## Disclaimer
This project uses synthetic/sample data only.
It is intended for educational and demonstration purposes and should not be used directly in production without further validation and governance controls.
