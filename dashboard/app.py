from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from app.core.inventory import scan_all_environments
from app.core.readiness import build_readiness_report


st.set_page_config(page_title="Post-Quantum Migration Simulator", layout="wide")
st.title("Post-Quantum Migration Simulator")

tabs = st.tabs(["Overview", "RSA vs PQC comparison", "Handshake comparison", "Crypto inventory", "Readiness"])

with tabs[0]:
    st.write("Benchmark and migration readiness overview.")

with tabs[1]:
    st.write("RSA vs PQC benchmark charts will be displayed here.")

with tabs[2]:
    st.write("Handshake comparison charts will be displayed here.")

with tabs[3]:
    report = scan_all_environments()
    env_rows = [
        {
            "Environment": inventory.environment.upper().replace("_", "-"),
            "Crypto keys": inventory.keys,
            "Certificates": inventory.certificates,
            "Ready to migrate": inventory.ready_to_migrate,
        }
        for inventory in report.environments
    ]
    env_df = pd.DataFrame(env_rows)

    col1, col2, col3 = st.columns(3)
    col1.metric("Total crypto keys", report.total_keys)
    col2.metric("Total certificates", report.total_certificates)
    col3.metric("Ready to migrate", report.total_ready_to_migrate)

    st.plotly_chart(
        px.bar(
            env_df,
            x="Environment",
            y=["Crypto keys", "Certificates", "Ready to migrate"],
            barmode="group",
            title="Crypto Assets by Environment",
        ),
        use_container_width=True,
    )
    st.dataframe(env_df, use_container_width=True)

    asset_rows = [
        {
            "Environment": asset.environment.upper().replace("_", "-"),
            "Type": asset.asset_type,
            "Name": asset.name,
            "Algorithm": asset.algorithm,
            "Source": asset.source,
            "Ready to migrate": asset.ready_to_migrate,
        }
        for inventory in report.environments
        for asset in inventory.assets
    ]
    st.dataframe(pd.DataFrame(asset_rows), use_container_width=True)

with tabs[4]:
    readiness = build_readiness_report()
    summary_rows = [
        {
            "Environment": env.environment.upper().replace("_", "-"),
            "Assets": env.asset_count,
            "Average risk": env.average_risk_score,
            "Average readiness": env.average_readiness_score,
            "Critical assets": env.critical_assets,
            "High-risk assets": env.high_risk_assets,
            "Ready to migrate": env.ready_to_migrate,
        }
        for env in readiness.environments
    ]
    summary_df = pd.DataFrame(summary_rows)

    metric1, metric2, metric3, metric4 = st.columns(4)
    metric1.metric("Total assets", readiness.total_assets)
    metric2.metric("Average risk", readiness.average_risk_score)
    metric3.metric("Average readiness", readiness.average_readiness_score)
    metric4.metric("Critical assets", readiness.total_critical_assets)

    st.plotly_chart(
        px.bar(
            summary_df,
            x="Environment",
            y=["Average risk", "Average readiness"],
            barmode="group",
            title="PQC Migration Risk and Readiness by Environment",
        ),
        use_container_width=True,
    )

    asset_df = pd.DataFrame(
        [
            {
                "Environment": asset.environment.upper().replace("_", "-"),
                "Asset": asset.asset_name,
                "Type": asset.asset_type,
                "Algorithm": asset.algorithm,
                "Risk": asset.risk_score,
                "Readiness": asset.readiness_score,
                "Level": asset.risk_level,
                "Priority": asset.migration_priority,
                "Why": "; ".join(asset.factors),
                "Next actions": "; ".join(asset.recommended_actions),
            }
            for asset in readiness.assets
        ]
    )
    level_filter = st.multiselect(
        "Risk level",
        sorted(asset_df["Level"].unique()) if not asset_df.empty else [],
        default=sorted(asset_df["Level"].unique()) if not asset_df.empty else [],
    )
    if level_filter:
        asset_df = asset_df[asset_df["Level"].isin(level_filter)]
    st.dataframe(asset_df.sort_values("Risk", ascending=False), use_container_width=True)
