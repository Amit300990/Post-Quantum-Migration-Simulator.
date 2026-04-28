from __future__ import annotations

import sys
from pathlib import Path

# Ensure the project root (parent of this file's directory) is first on
# sys.path so that `from app.xxx import ...` resolves to the real app/
# package and not any file named app.py inside the dashboard/ folder.
_PROJECT_ROOT = str(Path(__file__).resolve().parents[1])
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

import streamlit as st
import pandas as pd
import plotly.express as px
from app.utils.config import settings
from app.db.database import engine


def load_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    try:
        benchmark_df = pd.read_sql("benchmark_results", con=engine)
    except Exception as exc:
        st.warning(f"Could not load benchmark data: {exc}")
        benchmark_df = pd.DataFrame()
    try:
        handshake_df = pd.read_sql("handshake_results", con=engine)
    except Exception as exc:
        st.warning(f"Could not load handshake data: {exc}")
        handshake_df = pd.DataFrame()
    return benchmark_df, handshake_df


def render_overview(benchmark_df: pd.DataFrame, handshake_df: pd.DataFrame) -> None:
    st.subheader("Overview")
    st.metric("Benchmark records", len(benchmark_df))
    st.metric("Handshake records", len(handshake_df))
    if not benchmark_df.empty:
        st.markdown("**Median encryption throughput**")
        st.write(benchmark_df.groupby("algorithm")["throughput_mb_s"].median().reset_index())


def render_comparison(benchmark_df: pd.DataFrame) -> None:
    st.subheader("RSA vs PQC Comparison")
    if benchmark_df.empty:
        st.info("Run the benchmark API first to populate data.")
        return

    chart = px.bar(
        benchmark_df,
        x="file_size",
        y="encrypt_time_ms",
        color="algorithm",
        barmode="group",
        title="Encrypt latency by algorithm and file size",
    )
    st.plotly_chart(chart, use_container_width=True)

    throughput_chart = px.line(
        benchmark_df,
        x="file_size",
        y="throughput_mb_s",
        color="algorithm",
        markers=True,
        title="Throughput vs File Size",
    )
    st.plotly_chart(throughput_chart, use_container_width=True)


def render_handshake(handshake_df: pd.DataFrame) -> None:
    st.subheader("Handshake Comparison")
    if handshake_df.empty:
        st.info("Run the handshake API first to collect data.")
        return

    latency_chart = px.bar(
        handshake_df,
        x="mode",
        y="handshake_latency_ms",
        color="algorithm",
        title="Handshake Latency by Mode",
    )
    st.plotly_chart(latency_chart, use_container_width=True)

    size_chart = px.bar(
        handshake_df,
        x="mode",
        y="payload_size",
        color="algorithm",
        title="Handshake Payload Size",
    )
    st.plotly_chart(size_chart, use_container_width=True)


def render_details(benchmark_df: pd.DataFrame, handshake_df: pd.DataFrame) -> None:
    st.subheader("Detailed Metrics Table")
    if not benchmark_df.empty:
        st.markdown("**Benchmark results**")
        st.dataframe(benchmark_df)
    if not handshake_df.empty:
        st.markdown("**Handshake results**")
        st.dataframe(handshake_df)


def main() -> None:
    st.title("Post-Quantum Migration Simulator")
    st.write("Interactive dashboard for classical RSA and PQC Kyber comparisons.")
    benchmark_df, handshake_df = load_data()

    tabs = st.tabs(["Overview", "RSA vs PQC", "Handshake", "Detailed metrics"])
    with tabs[0]:
        render_overview(benchmark_df, handshake_df)
    with tabs[1]:
        render_comparison(benchmark_df)
    with tabs[2]:
        render_handshake(handshake_df)
    with tabs[3]:
        render_details(benchmark_df, handshake_df)


if __name__ == "__main__":
    main()
