import streamlit as st
from pathlib import Path
import sys

# Add src to path
root_dir = Path(__file__).parent.parent
sys.path.append(str(root_dir))

st.set_page_config(
    page_title="Email Compliance System",
    page_icon="📧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .info-box {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .feature-card {
        background-color: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown('<p class="main-header">📧 Email Compliance Surveillance System</p>', unsafe_allow_html=True)

# Introduction
st.markdown("""
<div class="info-box">
    <h3>Welcome to the RAG-based Email Compliance System</h3>
    <p>This system uses Retrieval-Augmented Generation (RAG) to automatically detect potential compliance violations in email communications.</p>
</div>
""", unsafe_allow_html=True)

# Features
st.subheader(" Key Features")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class="feature-card">
        <h4>Upload Sample Data</h4>
        <p>Train the system by uploading labeled email samples. The system learns from these examples to identify compliance patterns.</p>
        <ul>
            <li>Upload CSV with labeled emails</li>
            <li>Automatic vectorization</li>
            <li>Persistent storage in FAISS</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="feature-card">
        <h4>Check Alerts</h4>
        <p>Analyze new emails for compliance violations. Get detailed reports with risk scores and evidence.</p>
        <ul>
            <li>Batch email classification</li>
            <li>Risk score calculation</li>
            <li>Downloadable reports</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# How it works
st.subheader("How It Works")

st.markdown("""
<div class="info-box">
    <ol>
        <li><strong>Upload Sample Data</strong>: Provide labeled training emails (compliant/non-compliant)</li>
        <li><strong>Vector Storage</strong>: System creates embeddings and stores them in FAISS vector database</li>
        <li><strong>RAG Classification</strong>: When checking new emails:
            <ul>
                <li>Retrieves similar examples from vector DB</li>
                <li>Uses LLM to classify based on retrieved context</li>
                <li>Calculates risk scores</li>
            </ul>
        </li>
        <li><strong>Results</strong>: Get detailed compliance report with categories, reasons, and evidence</li>
    </ol>
</div>
""", unsafe_allow_html=True)

# Compliance Categories
st.subheader("Compliance Categories")

categories_col1, categories_col2, categories_col3 = st.columns(3)

with categories_col1:
    st.markdown("**Secrecy** (Risk: 10)")
    st.markdown("**Market Manipulation** (Risk: 8)")

with categories_col2:
    st.markdown("**Market Bribery** (Risk: 7)")
    st.markdown("**Change in Communication** (Risk: 6)")

with categories_col3:
    st.markdown("**Complaints** (Risk: 5)")
    st.markdown("**Employee Ethics** (Risk: 4)")

# Getting Started
st.subheader("Getting Started")

st.info("""
**Step 1**: Go to **Upload Sample Data** page and upload your training CSV  
**Step 2**: Go to **Check Alerts** page and upload test emails for classification  
**Step 3**: Review results and download the compliance report
""")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666;">
    <p>Built with LangChain, OpenAI, and FAISS | RAG Architecture</p>
</div>
""", unsafe_allow_html=True)