from backend.loader import load_csv
from backend.dq_dimensions import compute_dq_dimensions
from backend.dqs_scoring import compute_composite_dqs
from backend.profiling import build_null_duplicate_table
from backend.explanations import generate_dqs_explanation_text
from backend.ai.genai_service import generate_ai_summary
from backend.visuals import (
    plot_overall_dqs,
    plot_dimension_heatmap
)

import streamlit as st
import pandas as pd

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------
st.set_page_config(
    page_title="VISA Data Quality Score Summariser",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --------------------------------------------------
# SESSION STATE INITIALIZATION
# --------------------------------------------------
if "pandas_done" not in st.session_state:
    st.session_state.pandas_done = False
if "dq_done" not in st.session_state:
    st.session_state.dq_done = False
if "ai_done" not in st.session_state:
    st.session_state.ai_done = False
if "visuals_done" not in st.session_state:
    st.session_state.visuals_done = False

# --------------------------------------------------
# GLOBAL CSS — VISA STYLE
# --------------------------------------------------
st.markdown("""
<style>
header {visibility: hidden;}
footer {visibility: hidden;}

.block-container {
    padding-top: 0rem !important;
    padding-bottom: 1.2rem;
}

.stApp {
    background-color: #FFFFFF;
}

.visa-header {
    background-color: #0A1F44;
    padding: 12px 28px;
    margin-bottom: 18px;
}

.visa-title {
    color: #FFFFFF;
    font-size: 20px;
    font-weight: 600;
    margin: 0;
}

.visa-subtitle {
    color: #D6DEEB;
    font-size: 12.5px;
    margin-top: 4px;
}

.section-title {
    font-size: 18px;
    font-weight: 600;
    color: #0A1F44;
    margin-top: 20px;
    margin-bottom: 4px;
}

.section-accent {
    width: 48px;
    height: 2px;
    background-color: #F7B600;
    margin-bottom: 10px;
}

label {
    font-size: 13px !important;
}

/* ============================= */
/* VISA STYLE BUTTONS            */
/* ============================= */

/* Main button */
div.stButton > button {
    background-color: #0A1F44;
    color: #FFFFFF;
    border: 1px solid #0A1F44;
    border-radius: 4px;
    padding: 0.4rem 1.2rem;
    font-size: 14px;
    font-weight: 500;
}

/* Hover effect */
div.stButton > button:hover {
    background-color: #0A1F44;
    color: #FFFFFF;
    border: 1px solid #F7B600;
    box-shadow: 0 0 0 1px #F7B600;
}

/* Focus / active */
div.stButton > button:focus {
    outline: none;
    box-shadow: 0 0 0 2px rgba(247, 182, 0, 0.4);
}

</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# VISA HEADER
# --------------------------------------------------
st.markdown("""
<div class="visa-header">
    <div class="visa-title">VISA Data Quality Score Summariser</div>
    <div class="visa-subtitle">
        Explainable, dimension-based data quality scoring for payment datasets
    </div>
</div>
""", unsafe_allow_html=True)

# --------------------------------------------------
# DATASET INGESTION
# --------------------------------------------------
st.markdown('<div class="section-title">Dataset Ingestion</div>', unsafe_allow_html=True)
st.markdown('<div class="section-accent"></div>', unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)
with c1:
    txn_file = st.file_uploader("Transaction Dataset (CSV)", type=["csv"])
with c2:
    kyc_file = st.file_uploader("Customer KYC Dataset (CSV)", type=["csv"])
with c3:
    merchant_file = st.file_uploader("Merchant Master Dataset (CSV)", type=["csv"])

txn_df = load_csv(txn_file) if txn_file else None
kyc_df = load_csv(kyc_file) if kyc_file else None
merchant_df = load_csv(merchant_file) if merchant_file else None

# --------------------------------------------------
# DATASET PREVIEWS
# --------------------------------------------------
if txn_df is not None:
    st.markdown('<div class="section-title">Transaction Dataset Preview</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-accent"></div>', unsafe_allow_html=True)
    st.dataframe(txn_df.head(3), use_container_width=True)

if kyc_df is not None:
    st.markdown('<div class="section-title">Customer KYC Dataset Preview</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-accent"></div>', unsafe_allow_html=True)
    st.dataframe(kyc_df.head(3), use_container_width=True)

if merchant_df is not None:
    st.markdown('<div class="section-title">Merchant Master Dataset Preview</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-accent"></div>', unsafe_allow_html=True)
    st.dataframe(merchant_df.head(3), use_container_width=True)

# --------------------------------------------------
# STEP 1: PANDAS SUMMARY
# --------------------------------------------------
if txn_df is not None and kyc_df is not None and merchant_df is not None:

    if not st.session_state.pandas_done:
        if st.button("Summarize Dataset (Pandas Profiling)"):
            st.session_state.pandas_done = True

    if st.session_state.pandas_done:
        st.markdown('<div class="section-title">Pandas Profiling Summary</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-accent"></div>', unsafe_allow_html=True)

        st.subheader("Transaction Dataset")
        st.dataframe(build_null_duplicate_table(txn_df), use_container_width=True)

        st.subheader("Customer KYC Dataset")
        st.dataframe(build_null_duplicate_table(kyc_df), use_container_width=True)

        st.subheader("Merchant Master Dataset")
        st.dataframe(build_null_duplicate_table(merchant_df), use_container_width=True)

# --------------------------------------------------
# STEP 2: DATA QUALITY DIMENSIONS
# --------------------------------------------------
if st.session_state.pandas_done and not st.session_state.dq_done:
    col_btn, col_dl = st.columns([1, 1])

    with col_btn:
        if st.button("Compute Data Quality Dimensions"):
            st.session_state.dq_done = True

    with col_dl:
        st.download_button(
            label="Download DQS Explanation",
            data=generate_dqs_explanation_text(),
            file_name="VISA_Data_Quality_Score_Explanation.txt",
            mime="text/plain"
        )

if st.session_state.dq_done:

    txn_scores = compute_dq_dimensions(
        txn_df,
        "transaction",
        ref_customers=kyc_df["customer_id"].dropna().unique(),
        ref_merchants=merchant_df["merchant_id"].dropna().unique()
    )
    kyc_scores = compute_dq_dimensions(kyc_df, "kyc")
    merchant_scores = compute_dq_dimensions(merchant_df, "merchant")

    txn_dqs = compute_composite_dqs(txn_scores)
    kyc_dqs = compute_composite_dqs(kyc_scores)
    merchant_dqs = compute_composite_dqs(merchant_scores)


    st.markdown('<div class="section-title">Data Quality Dimension Comparison</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-accent"></div>', unsafe_allow_html=True)

    dimensions_with_formula = {
        "Completeness : (1 − Nulls / Total Cells)": "Completeness",
        "Uniqueness : (1 − Duplicate Rows / Total Rows)": "Uniqueness",
        "Validity : (1 − Invalid Values / Total Rows)": "Validity",
        "Accuracy : (Proxy = Validity)": "Accuracy",
        "Consistency : (Avg of Completeness & Validity)": "Consistency",
        "Timeliness : (1 − Late Records / Total Records)": "Timeliness",
        "Integrity : (1 − Broken References / Total Records)": "Integrity"
    }

    dq_table = pd.DataFrame({
        "Transaction Dataset": [txn_scores.get(v) for v in dimensions_with_formula.values()],
        "Customer KYC Dataset": [kyc_scores.get(v) for v in dimensions_with_formula.values()],
        "Merchant Master Dataset": [merchant_scores.get(v) for v in dimensions_with_formula.values()]
    }, index=dimensions_with_formula.keys())

    st.dataframe(dq_table, use_container_width=True)

    st.markdown('<div class="section-title">Overall Data Quality Score (DQS)</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-accent"></div>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    c1.metric("Transaction Dataset DQS", f"{txn_dqs} / 100")
    c2.metric("Customer KYC Dataset DQS", f"{kyc_dqs} / 100")
    c3.metric("Merchant Master Dataset DQS", f"{merchant_dqs} / 100")


# --------------------------------------------------
# STEP 3: AI SUMMARY 
# --------------------------------------------------
if st.session_state.dq_done and not st.session_state.ai_done:
    if st.button("Generate AI Data Quality Summary"):
        st.session_state.ai_done = True

if st.session_state.ai_done:
    st.markdown('<div class="section-title">AI-Generated Data Quality Summary</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-accent"></div>', unsafe_allow_html=True)

    with st.spinner("Generating insights using GenAI..."):
        txn_ai = generate_ai_summary(txn_df, txn_scores, "Transaction Dataset")
        kyc_ai = generate_ai_summary(kyc_df, kyc_scores, "Customer KYC Dataset")
        merchant_ai = generate_ai_summary(merchant_df, merchant_scores, "Merchant Master Dataset")


    st.subheader("Transaction Dataset")
    st.write(txn_ai)
    st.subheader("Customer KYC Dataset")
    st.write(kyc_ai)
    st.subheader("Merchant Master Dataset")
    st.write(merchant_ai)

# --------------------------------------------------
# STEP 4: VISUAL DATA QUALITY ANALYSIS (BUTTON)
# --------------------------------------------------
    st.markdown('<div class="section-title">Visual Data Quality Analysis</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-accent"></div>', unsafe_allow_html=True)

    # -------------------------------
    # Overall DQS Comparison
    # -------------------------------
    st.subheader("Overall Data Quality Score Comparison")

    dqs_scores = {
        "Transaction Dataset": txn_dqs,
        "Customer KYC Dataset": kyc_dqs,
        "Merchant Master Dataset": merchant_dqs
    }

    st.plotly_chart(
        plot_overall_dqs(dqs_scores),
        use_container_width=True
    )

    # -------------------------------
    # Dimension Heatmap
    # -------------------------------
    st.subheader("Dimension-Level Quality Heatmap")

    st.plotly_chart(
        plot_dimension_heatmap(dq_table),
        use_container_width=True
    )

