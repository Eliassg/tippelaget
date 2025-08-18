import streamlit as st
import pandas as pd
import requests
from cognite.client import CogniteClient, ClientConfig
import altair as alt

# -----------------------
@st.cache_resource
def get_client() -> CogniteClient:
    config = {
        "client_name": "tippelaget_app",
        "project": st.secrets["cognite"]["project"],
        "base_url": st.secrets["cognite"]["base_url"],
        "credentials": {
            "client_credentials": {
                "client_id": st.secrets["cognite"]["client_id"],
                "client_secret": st.secrets["cognite"]["client_secret"],
                "token_url": st.secrets["cognite"]["token_url"],
                "scopes": ["https://bluefield.cognitedata.com/.default"],
            },
        },
    }
    client_config = ClientConfig.load(config)
    return CogniteClient(config=client_config)


@st.cache_data(ttl=0)
def fetch_bet_view(space: str = "tippelaget_space_name", model_external_id: str = "tippelaget", view_external_id: str = "Bet", version: str = None) -> pd.DataFrame:
    client = get_client()
    
    # View identifier
    view_id = (space, view_external_id) if version is None else (space, view_external_id, version)
    
    # Retrieve the view
    views = client.data_modeling.views.retrieve(
        ids=view_id, 
        include_inherited_properties=True,
        all_versions=False
    )
    
    if not views:
        return pd.DataFrame()
    
    view = views[0]
    rows = client.data_modeling.instances.list(view_id=view.as_id())
    
    # Convert to DataFrame
    df = pd.DataFrame([row.properties for row in rows])
    
    # Optional: flatten nested objects (Player, Gameweek)
    if not df.empty:
        if 'player' in df.columns:
            df['player_name'] = df['player'].apply(lambda x: x.get('name') if isinstance(x, dict) else None)
            df.drop(columns='player', inplace=True)
        if 'gameweek' in df.columns:
            df['gameweek_number'] = df['gameweek'].apply(lambda x: x.get('number') if isinstance(x, dict) else None)
            df.drop(columns='gameweek', inplace=True)
    
    return df

# -----------------------
# Streamlit App
# -----------------------
st.title("⚽ Betting Dashboard (CDF View)")
st.caption("Always fetching the latest data from Cognite Data Fusion")

# Fetch and display Bet view
df = fetch_bet_view()
st.dataframe(df)