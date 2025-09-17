from __future__ import annotations

import pandas as pd
import streamlit as st
from cognite.client.data_classes.data_modeling.ids import ViewId


from .client import get_client
from .config import DEFAULT_SPACE, DEFAULT_VIEW, DEFAULT_VIEW_VERSION


@st.cache_data(ttl=0)
def fetch_bet_view(
    space: str = DEFAULT_SPACE,
    view_external_id: str = DEFAULT_VIEW,
    version: str = DEFAULT_VIEW_VERSION,
) -> pd.DataFrame:
    client = get_client()

    view_id = ViewId(space, view_external_id, version)
    rows = client.data_modeling.instances.list(
        sources=[view_id],
        limit=1000,
    )

    if not rows:
        return pd.DataFrame()

    extracted = []
    for row in rows:
        props = row.properties.get(view_id)
        extracted.append(props)

    df = pd.json_normalize(extracted)
    return df


def prepare_bets_df(df: pd.DataFrame) -> pd.DataFrame:
    """Standardize and enrich the raw bets dataframe for the app."""
    if df.empty:
        return df

    df = df.rename(
        columns={
            "player.externalId": "player",
            "gameweek.externalId": "gameweek",
        }
    )

    df = df.drop(columns=["player.space", "gameweek.space"], errors="ignore")

    # Convert gameweek string "GW_X" → integer
    df["gameweek_num"] = df["gameweek"].str.extract(r"GW_(\d+)").astype(int)

    # Win flag
    df["won"] = df["payout"] > 0

    # Ensure datetime
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"])

    return df


def create_monthly_innskudd_df() -> pd.DataFrame:
    dates = pd.date_range(
        start="2025-03-15", end=pd.Timestamp.today(), freq="MS"
    ) + pd.DateOffset(days=14)
    df = pd.DataFrame({"date": dates, "innskudd": 600})
    return df


def get_prepared_bets() -> pd.DataFrame:
    df = fetch_bet_view()
    return prepare_bets_df(df)

def execute_workflow(wf_external_id: str, version="1") -> WorkFlowExecution:
    client = get_client()
    res = client.workflows.executions.run(workflow_external_id=wf_external_id, version=version)
    return res

def check_workflow_status(execution_id: int) -> str:
    client = get_client()
    res = client.workflows.executions.retrieve(execution_id)
    return res.status