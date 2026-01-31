import streamlit as st
import pandas as pd
import torch
from pyvis.network import Network
import streamlit.components.v1 as components

from graph.build_graph import build_transaction_graph
from models.gnn_model import GNN
from models.transformer_model import TransactionTransformer

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------
st.set_page_config(page_title="Smurfing Determiner", layout="wide")

st.title("🔍 Smurfing Determiner")
st.caption("Graph + Transformer based AML detection for blockchain transactions")

# --------------------------------------------------
# HELPERS
# --------------------------------------------------
def risk_color(score):
    if score >= 0.6:
        return "#e74c3c"  # red
    elif score >= 0.3:
        return "#f1c40f"  # yellow
    else:
        return "#2ecc71"  # green


def risk_bar(score, width=260):
    pct = int(score * 100)
    color = risk_color(score)

    return (
        f"<div style='display:flex;align-items:center;gap:10px;'>"
        f"<div style='background:#2a2a2a;border-radius:6px;width:{width}px;height:14px;'>"
        f"<div style='width:{pct}%;background:{color};height:14px;border-radius:6px;'></div>"
        f"</div>"
        f"<span style='font-size:12px;color:#ddd'>{pct}%</span>"
        f"</div>"
    )


# --------------------------------------------------
# FILE UPLOAD
# --------------------------------------------------
uploaded_file = st.file_uploader("Upload Transaction Dataset (CSV)", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    # --------------------------------------------------
    # DATASET PREVIEW
    # --------------------------------------------------
    st.subheader("📄 Dataset Preview")
    st.dataframe(df.head(10), use_container_width=True)

    # --------------------------------------------------
    # GRAPH BUILD
    # --------------------------------------------------
    G, node_map = build_transaction_graph(df)

    x = torch.tensor(
        [[G.out_degree(n), G.in_degree(n)] for n in G.nodes()],
        dtype=torch.float
    )

    edge_index = torch.tensor(
        [[node_map[s], node_map[d]] for s, d in G.edges()],
        dtype=torch.long
    ).t().contiguous()

    # --------------------------------------------------
    # LOAD MODELS
    # --------------------------------------------------
    gnn = GNN()
    gnn.load_state_dict(torch.load("models/gnn_model.pt", map_location="cpu"))
    gnn.eval()

    transformer = TransactionTransformer()
    transformer.load_state_dict(torch.load("models/transformer_model.pt", map_location="cpu"))
    transformer.eval()

    # --------------------------------------------------
    # INFERENCE
    # --------------------------------------------------
    with torch.no_grad():
        wallet_scores = gnn(x, edge_index).numpy()

    wallet_risk = dict(zip(G.nodes(), wallet_scores))

    amounts = torch.tensor(df["Amount"].values, dtype=torch.float).unsqueeze(1)
    with torch.no_grad():
        txn_scores = transformer(amounts).numpy()

    df["GNN_Risk"] = df["Source_Wallet_ID"].map(wallet_risk).fillna(0)
    df["Transformer_Risk"] = txn_scores
    df["Final_Risk"] = 0.6 * df["GNN_Risk"] + 0.4 * df["Transformer_Risk"]

    df["Label"] = df["Final_Risk"].apply(
        lambda x: "illicit" if x >= 0.6 else "legal"
    )

    # --------------------------------------------------
    # TRANSACTION RISK TABLE (AML STYLE)
    # --------------------------------------------------
    st.subheader("⚠️ Transaction Risk Results")

    for _, r in df.sort_values("Final_Risk", ascending=False).head(10).iterrows():
        st.markdown(
            f"""
            <div style="
                display:grid;
                grid-template-columns: 120px 120px 120px 100px auto;
                padding:10px;
                border-bottom:1px solid #2c2c2c;
                align-items:center;
            ">
                <div><b>{r['Source_Wallet_ID']}</b></div>
                <div>{r['Dest_Wallet_ID']}</div>
                <div>{r['Label'].upper()}</div>
                <div>{risk_bar(r['Final_Risk'], 120)}</div>
                <div style="font-size:12px;">
                    {"🔴 High Risk Pattern" if r["Final_Risk"] > 0.6 else
                     "🟠 Moderate Risk" if r["Final_Risk"] > 0.3 else
                     "🟢 Normal Activity"}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # --------------------------------------------------
    # TOP SUSPICIOUS WALLETS (CLEAN BAR VIEW)
    # --------------------------------------------------
    st.subheader("🚨 Top Suspicious Wallets")

    wallet_rank = (
        df.groupby("Source_Wallet_ID")["Final_Risk"]
        .mean()
        .sort_values(ascending=False)
        .head(10)
    )

    for wallet, score in wallet_rank.items():
        st.markdown(
            f"""
            <div style="margin-bottom:14px;">
                <div style="font-weight:600;">{wallet}</div>
                {risk_bar(score, 300)}
            </div>
            """,
            unsafe_allow_html=True
        )

    # --------------------------------------------------
    # GRAPH VISUALIZATION
    # --------------------------------------------------
    st.subheader("🧠 Transaction Graphs")

    col1, col2 = st.columns(2)

    # ---------- ORIGINAL GRAPH ----------
    with col1:
        st.markdown("### Original Transaction Graph")
        net1 = Network(height="500px", width="100%", bgcolor="#ffffff", directed=True)

        for n in G.nodes():
            net1.add_node(n, label=n, color="#b0dfea")

        for s, d in G.edges():
            net1.add_edge(s, d, color="#cccccc")

        net1.save_graph("graph_original.html")
        components.html(open("graph_original.html").read(), height=520)

    # ---------- RISK GRAPH ----------
    with col2:
        st.markdown("### Risk-Highlighted Graph")
        net2 = Network(height="500px", width="100%", bgcolor="#ffffff", directed=True)

        for n in G.nodes():
            score = wallet_risk.get(n, 0)
            net2.add_node(
                n,
                label=n,
                color=risk_color(score),
                title=f"Wallet Risk: {score:.2f}"
            )

        for _, r in df.iterrows():
            net2.add_edge(
                r["Source_Wallet_ID"],
                r["Dest_Wallet_ID"],
                color=risk_color(r["Final_Risk"]),
                title=f"Txn Risk: {r['Final_Risk']:.2f}"
            )

        net2.save_graph("graph_risk.html")
        components.html(open("graph_risk.html").read(), height=520)
