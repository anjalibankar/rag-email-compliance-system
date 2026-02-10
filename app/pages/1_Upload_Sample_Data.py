import streamlit as st
import pandas as pd
from pathlib import Path
import sys

# Add src to path
root_dir = Path(__file__).parent.parent.parent
sys.path.append(str(root_dir))

from src.backend import ComplianceBackend

st.set_page_config(
    page_title="Upload Sample Data",
    page_icon="📤",
    layout="wide"
)

# Initialize backend
@st.cache_resource
def get_backend():
    return ComplianceBackend()

backend = get_backend()

# Header
st.title("📤 Upload Sample Data")
st.write("Upload labeled email data to train the compliance detection system")

st.markdown("---")

# Instructions
with st.expander("📋 CSV Format Requirements"):
    st.write("""
    **Required Columns:**
    - Date (YYYY-MM-DD)
    - From (email address)
    - To (email address)
    - Subject (email subject)
    - Body (email content)
    - Classification (compliant or non-compliant)
    - Category (compliance category or 'compliant')
    
    **Example:**
```
    Date,From,To,Subject,Body,Classification,Category
    2024-01-15,john@enron.com,mary@enron.com,Q3 Results,We should delay...,non-compliant,Secrecy
```
    """)

st.markdown("---")

# File upload
st.subheader("📁 Upload Training Data")

uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"])

if uploaded_file is not None:
    st.success(f"✅ File uploaded: **{uploaded_file.name}**")
    
    try:
        df = pd.read_csv(uploaded_file)
        
        # Preview
        st.subheader("📄 Preview")
        st.dataframe(df.head(10), use_container_width=True)
        
        # Validation
        required_cols = ['Date', 'From', 'To', 'Subject', 'Body', 'Classification', 'Category']
        missing_cols = [col for col in required_cols if col not in df.columns]
        
        if missing_cols:
            st.error(f"❌ Missing required columns: {', '.join(missing_cols)}")
        else:
            st.success("✅ All required columns present")
            
            # Simple stats
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Emails", len(df))
            
            with col2:
                compliant = len(df[df['Classification'] == 'compliant'])
                st.metric("Compliant", compliant)
            
            with col3:
                non_compliant = len(df[df['Classification'] == 'non-compliant'])
                st.metric("Non-Compliant", non_compliant)
            
            st.markdown("---")
            
            # Update button
            if st.button("🔄 Update Vector Database", type="primary", use_container_width=True):
                with st.spinner("Processing and updating vector database..."):
                    try:
                        uploaded_file.seek(0)
                        backend.load_sample_data(uploaded_file)
                        
                        st.success("✅ Vector database updated successfully!")
                        st.info("**Next Step:** Go to the Check Alerts page to classify test emails")
                        
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
    
    except Exception as e:
        st.error(f"❌ Error reading CSV: {str(e)}")

else:
    st.info("👆 Please upload a CSV file to continue")