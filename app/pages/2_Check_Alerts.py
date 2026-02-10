import streamlit as st
import pandas as pd
from pathlib import Path
import sys
from datetime import datetime

# Add src to path
root_dir = Path(__file__).parent.parent.parent
sys.path.append(str(root_dir))

from src.backend import ComplianceBackend

st.set_page_config(
    page_title="Check Alerts",
    page_icon="🔍",
    layout="wide"
)

# Initialize backend
@st.cache_resource
def get_backend():
    return ComplianceBackend()

backend = get_backend()

# Session state
if 'results_df' not in st.session_state:
    st.session_state.results_df = None
if 'csv_data' not in st.session_state:
    st.session_state.csv_data = None

# Header
st.title("🔍 Check Compliance Alerts")
st.write("Upload test emails to check for potential compliance violations")

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
    
    **Note:** No need to include Classification or Category - the system will predict these.
    
    **Example:**
```
    Date,From,To,Subject,Body
    2024-01-15,john@enron.com,mary@home.net,Quarterly Update,We need to discuss...
```
    """)

st.markdown("---")

# File upload
st.subheader("📁 Upload Test Emails")

uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"])

if uploaded_file is not None:
    st.success(f"✅ File uploaded: **{uploaded_file.name}**")
    
    try:
        df = pd.read_csv(uploaded_file)
        
        # Preview
        st.subheader("📄 Preview")
        st.dataframe(df.head(10), use_container_width=True)
        
        # Validation
        required_cols = ['Date', 'From', 'To', 'Subject', 'Body']
        missing_cols = [col for col in required_cols if col not in df.columns]
        
        if missing_cols:
            st.error(f"❌ Missing required columns: {', '.join(missing_cols)}")
        else:
            st.success("✅ All required columns present")
            st.metric("Total Emails to Analyze", len(df))
            
            st.markdown("---")
            
            # Classify button
            if st.button("🔍 Check for Compliance Issues", type="primary", use_container_width=True):
                
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                try:
                    status_text.text("🔄 Analyzing emails for compliance violations...")
                    progress_bar.progress(25)
                    
                    uploaded_file.seek(0)
                    results = backend.classify_emails(uploaded_file)
                    progress_bar.progress(75)
                    
                    if results:
                        st.session_state.results_df = pd.DataFrame(results)
                        st.session_state.csv_data = st.session_state.results_df.to_csv(index=False).encode('utf-8')
                        progress_bar.progress(100)
                        status_text.text("✅ Analysis complete!")
                        st.success(f"Found **{len(results)}** potential compliance violations")
                    else:
                        progress_bar.progress(100)
                        status_text.text("✅ Analysis complete!")
                        st.success("🎉 No compliance violations detected!")
                        st.session_state.results_df = None
                    
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
    
    except Exception as e:
        st.error(f"❌ Error reading CSV: {str(e)}")

else:
    st.info("👆 Please upload a CSV file to continue")

# Display results - SHOW ALL RECORDS
if st.session_state.results_df is not None:
    st.markdown("---")
    st.subheader("📊 Compliance Alert Report")
    
    df_results = st.session_state.results_df
    
    # Simple metrics only
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("🚨 Total Violations", len(df_results))
    
    with col2:
        avg_risk = df_results['Risk Score'].mean()
        st.metric("⚠️ Average Risk Score", f"{avg_risk:.2f}")
    
    with col3:
        high_risk = len(df_results[df_results['Risk Score'] >= 10])
        st.metric("🔴 High Risk (≥10)", high_risk)
    
    st.markdown("---")
    
    # Results table - SHOWS ALL RECORDS (no height limit)
    st.subheader(f"📋 All Non-Compliant Emails ({len(df_results)} records)")
    st.dataframe(df_results, use_container_width=True)
    
    # Download button
    st.markdown("---")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    st.download_button(
        label="📥 Download Compliance Report (CSV)",
        data=st.session_state.csv_data,
        file_name=f"compliance_report_{timestamp}.csv",
        mime="text/csv",
        use_container_width=True,
        type="primary"
    )