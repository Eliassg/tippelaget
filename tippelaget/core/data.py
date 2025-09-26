from __future__ import annotations
from datetime import datetime, timedelta

import pandas as pd
import streamlit as st
from cognite.client.data_classes.data_modeling.ids import ViewId


from .client import get_client
from .config import DEFAULT_SPACE, DEFAULT_VIEW, DEFAULT_VIEW_VERSION
from cognite.client.data_classes.data_modeling import (
    ViewId
)
from cognite.client.data_classes.data_modeling.query import (
    NodeResultSetExpression,
    Query,
    Select,
    SourceSelector
)
from cognite.client.data_classes.filters import (
    And,
    SpaceFilter,
    Range
)
from cognite.client.exceptions import CogniteAPIError


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


@st.cache_data(ttl=0)
def fetch_event_view(
    space: str = DEFAULT_SPACE,
    view_external_id: str = "Event",
    version: str = "1.0.3",
) -> pd.DataFrame:
    client = get_client()
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    event_vid = ViewId(space=space, external_id=view_external_id, version=version)
    
    query = Query(
        with_={
            "Event": NodeResultSetExpression(
                filter=And(
                    Range((event_vid.as_property_ref("eventDate")), gt=yesterday, lte=datetime.now().strftime("%Y-%m-%d")), 
                    SpaceFilter(space="tippelaget_space_name")
                ),
            ),
        },
        select={
            "Event": Select(
                [
                    SourceSelector(event_vid, ["*"])
                ],
            ),
        },
    )
    try:
        res = client.data_modeling.instances.query(query=query)
        print(res["Event"])   
        df = res.get_nodes("Event").to_pandas(expand_properties=True)
    except CogniteAPIError as e:
        print(e)
        return pd.DataFrame()
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


@st.cache_data(ttl=0)
def create_monthly_innskudd_df() -> pd.DataFrame:
    dates = pd.date_range(
        start="2025-03-15", end=pd.Timestamp.today(), freq="MS"
    ) + pd.DateOffset(days=14)
    df = pd.DataFrame({"date": dates, "innskudd": 600})
    return df


@st.cache_data(ttl=0)
def get_prepared_bets() -> pd.DataFrame:
    df = fetch_bet_view()
    return prepare_bets_df(df)

@st.cache_data(ttl=0)
def get_todays_events() -> pd.DataFrame:
    df = fetch_event_view()
    #select relevant columns: "eventName, "H", "A", "D"
    if df.empty:
        return df
    df = df[["eventName", "H", "A", "D"]]
    return df

def execute_workflow(wf_external_id: str, version="1") -> WorkFlowExecution:
    client = get_client()
    res = client.workflows.executions.run(workflow_external_id=wf_external_id, version=version)
    return res

def check_workflow_status(execution_id: int) -> str:
    client = get_client()
    res = client.workflows.executions.retrieve_detailed(execution_id)
    return res.status

def check_last_workflow_runtime(wf_external_id: str, version="1") -> int | None:
    client = get_client()
    res = client.workflows.executions.list((wf_external_id, version))
    if not res:
        return None  
    res = client.workflows.executions.retrieve_detailed(res[0].id)
    if not res or not res.created_time:
        return None
    return res.created_time
