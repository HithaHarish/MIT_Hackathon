import streamlit as st

def visa_header():
    st.markdown("""
    <div class="visa-header">
        <div class="visa-title">VISA Data Quality Score Summariser</div>
        <div class="visa-subtitle">
            Explainable, dimension-based data quality scoring for payment datasets
        </div>
    </div>
    """, unsafe_allow_html=True)
