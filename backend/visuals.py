# backend/visuals.py
import pandas as pd
import plotly.express as px


# --------------------------------------------------
# 1. OVERALL DQS BAR CHART
# --------------------------------------------------
def plot_overall_dqs(dqs_scores: dict):
    """
    dqs_scores = {
        "Transaction Dataset": 82.5,
        "Customer KYC Dataset": 91.2,
        "Merchant Master Dataset": 95.6
    }
    """
    df = pd.DataFrame(
        list(dqs_scores.items()),
        columns=["Dataset", "DQS"]
    )

    fig = px.bar(
        df,
        x="DQS",
        y="Dataset",
        orientation="h",
        title="Overall Data Quality Score (DQS) Comparison",
        text="DQS",
        range_x=[0, 100]
    )

    fig.update_traces(texttemplate="%{text}%", textposition="outside")
    fig.update_layout(
        xaxis_title="Data Quality Score (%)",
        yaxis_title="",
        height=300
    )

    return fig


# --------------------------------------------------
# 2. DIMENSION HEATMAP
# --------------------------------------------------
def plot_dimension_heatmap(dq_table: pd.DataFrame):
    """
    dq_table:
        index = dimensions
        columns = datasets
    """
    fig = px.imshow(
        dq_table,
        text_auto=True,
        aspect="auto",
        color_continuous_scale="RdYlGn",
        title="Data Quality Dimension Heatmap"
    )

    fig.update_layout(
        xaxis_title="Dataset",
        yaxis_title="Data Quality Dimension",
        height=400
    )

    return fig

