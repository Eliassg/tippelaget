from __future__ import annotations

from datetime import datetime, timedelta

import pandas as pd
from cognite.client import CogniteClient, ClientConfig
from cognite.client.data_classes.data_modeling import ViewId
from cognite.client.data_classes.data_modeling.query import (
    NodeResultSetExpression,
    Query,
    Select,
    SourceSelector,
)
from cognite.client.data_classes.filters import And, Range, SpaceFilter
from cognite.client.exceptions import CogniteAPIError

from settings import Settings, get_settings


def build_client(settings: Settings | None = None) -> CogniteClient:
    s = settings or get_settings()
    cfg = {
        "client_name": "tippelaget_web_api",
        "project": s.cognite_project,
        "base_url": s.cognite_base_url,
        "credentials": {
            "client_credentials": {
                "client_id": s.cognite_client_id,
                "client_secret": s.cognite_client_secret,
                "token_url": s.cognite_token_url,
                "scopes": [s.cognite_scopes],
            }
        },
    }
    return CogniteClient(config=ClientConfig.load(cfg))


def fetch_bet_view(client: CogniteClient, settings: Settings) -> pd.DataFrame:
    view_id = ViewId(settings.default_space, settings.default_view, settings.default_view_version)
    rows = client.data_modeling.instances.list(sources=[view_id], limit=1000)
    if not rows:
        return pd.DataFrame()
    extracted = []
    for row in rows:
        props = row.properties.get(view_id)
        extracted.append(props)
    return pd.json_normalize(extracted)


def fetch_event_view(client: CogniteClient, settings: Settings) -> pd.DataFrame:
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    today = datetime.now().strftime("%Y-%m-%d")
    event_vid = ViewId(
        space=settings.default_space,
        external_id=settings.event_view,
        version=settings.event_view_version,
    )
    query = Query(
        with_={
            "Event": NodeResultSetExpression(
                filter=And(
                    Range((event_vid.as_property_ref("eventDate")), gt=yesterday, lte=today),
                    SpaceFilter(space=settings.default_space),
                ),
            ),
        },
        select={
            "Event": Select([SourceSelector(event_vid, ["*"])]),
        },
    )
    try:
        res = client.data_modeling.instances.query(query=query)
        return res.get_nodes("Event").to_pandas(expand_properties=True)
    except CogniteAPIError:
        return pd.DataFrame()


def prepare_bets_df(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    df = df.rename(
        columns={
            "player.externalId": "player",
            "gameweek.externalId": "gameweek",
        }
    )
    df = df.drop(columns=["player.space", "gameweek.space"], errors="ignore")
    df["gameweek_num"] = df["gameweek"].str.extract(r"GW_(\d+)").astype(int)
    df["won"] = df["payout"] > 0
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"])
    return df


def create_monthly_innskudd_df() -> pd.DataFrame:
    dates = pd.date_range(start="2025-03-15", end=pd.Timestamp.today(), freq="MS") + pd.DateOffset(days=14)
    return pd.DataFrame({"date": dates, "innskudd": 600})


def get_prepared_bets(client: CogniteClient, settings: Settings) -> pd.DataFrame:
    return prepare_bets_df(fetch_bet_view(client, settings))


def get_todays_events_prepared(client: CogniteClient, settings: Settings) -> pd.DataFrame:
    df = fetch_event_view(client, settings)
    if df.empty:
        return df
    cols = ["eventName", "H", "A", "D"]
    available = [c for c in cols if c in df.columns]
    return df[available]


def execute_workflow(client: CogniteClient, settings: Settings):
    return client.workflows.executions.run(
        workflow_external_id=settings.workflow_external_id,
        version=settings.workflow_version,
    )


def check_workflow_status(client: CogniteClient, execution_id: int) -> str:
    res = client.workflows.executions.retrieve_detailed(execution_id)
    return res.status


def check_last_workflow_runtime(client: CogniteClient, settings: Settings) -> int | None:
    res = client.workflows.executions.list((settings.workflow_external_id, settings.workflow_version))
    if not res:
        return None
    detailed = client.workflows.executions.retrieve_detailed(res[0].id)
    if not detailed or not detailed.created_time:
        return None
    return detailed.created_time
