from backend.loader import load_csv
from backend.profiling import build_null_duplicate_table

import streamlit as st
import pandas as pd

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------
st.set_page_config(
    page_title="Maestro – Smurfing Determiner",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------
if "pandas_done" not in st.session_state:
    st.session_state.pandas_done = False

# --------------------------------------------------
# GLOBAL WHITE + LIGHT BLUE THEME
# --------------------------------------------------
st.markdown("""
<style>
/* ---------------------------------- */
/* GLOBAL RESET                        */
/* ---------------------------------- */
header, footer { visibility: hidden; }

.stApp {
    background-color: #FFFFFF;
    color: #000000;
    font-family: Inter, system-ui, sans-serif;
}

.block-container {
    padding-top: 1rem;
    padding-bottom: 1.5rem;
}

/* ---------------------------------- */
/* HEADINGS                            */
/* ---------------------------------- */
h1, h2, h3 {
    color: #1F4FD8; /* dark blue */
}

p, label {
    color: #000000;
    font-size: 14px;
}

/* ---------------------------------- */
/* BUTTONS                             */
/* ---------------------------------- */
div.stButton > button {
    background-color: #1F4FD8;
    color: #FFFFFF;
    border-radius: 6px;
    border: none;
    padding: 0.45rem 1.4rem;
    font-size: 14px;
    font-weight: 500;
}

div.stButton > button:hover {
    background-color: #163DB8;
}

/* ---------------------------------- */
/* FILE UPLOADER                       */
/* ---------------------------------- */
section[data-testid="stFileUploader"] {
    background-color: #FFFFFF;
    border: 1px dashed #1F4FD8;
    border-radius: 8px;
    padding: 14px;
}

/* ---------------------------------- */
/* DATAFRAME – PURE WHITE              */
/* ---------------------------------- */
[data-testid="stDataFrame"] {
    background-color: #FFFFFF !important;
    border-radius: 8px;
    padding: 8px;
    border: 1px solid rgba(31, 79, 216, 0.25);
}

/* Header row */
[data-testid="stDataFrame"] thead th {
    background-color: rgba(31, 79, 216, 0.08);
    color: #000000;        /* black text */
    font-weight: 600;
    border-bottom: 1px solid rgba(31, 79, 216, 0.25);
}

/* Table cells */
[data-testid="stDataFrame"] tbody tr td {
    background-color: #FFFFFF !important;
    color: #000000 !important;
}

/* Row hover – very subtle */
[data-testid="stDataFrame"] tbody tr:hover td {
    background-color: rgba(31, 79, 216, 0.04);
}
</style>
""", unsafe_allow_html=True)


# --------------------------------------------------
# MAESTRO HEADER
# --------------------------------------------------
st.markdown("""
<div style="margin-bottom:22px;">
    <h2>Smurfing Determiner</h2>
    <p>
        Graph-ready transaction data quality analysis to support detection of smurfing
        and money laundering patterns on blockchain networks.
    </p>
</div>
""", unsafe_allow_html=True)

# --------------------------------------------------
# DATASET INGESTION
# --------------------------------------------------
st.markdown("### Dataset Ingestion")

txn_file = st.file_uploader(
    "Upload Transaction Dataset (CSV)",
    type=["csv"]
)

txn_df = load_csv(txn_file) if txn_file else None

# --------------------------------------------------
# DATASET PREVIEW
# --------------------------------------------------
if txn_df is not None:
    st.markdown("### Transaction Dataset Preview")
    st.dataframe(txn_df.head(5), use_container_width=True)

# --------------------------------------------------
# DATA PROFILING
# --------------------------------------------------
if txn_df is not None and not st.session_state.pandas_done:
    if st.button("Analyze Dataset Quality"):
        st.session_state.pandas_done = True

if st.session_state.pandas_done:
    st.markdown("### Dataset Quality Summary")
    st.dataframe(
        build_null_duplicate_table(txn_df),
        use_container_width=True
    )
