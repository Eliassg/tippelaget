import streamlit as st
import pandas as pd
import altair as alt
from cognite.client import CogniteClient
from cognite.client.credentials import OAuthClientCredentials


# -----------------------
# Connect to Cognite CDF
# -----------------------
@st.cache_resource
def get_client():
    return CogniteClient(
        token_client_credentials={
            "token_url": st.secrets["cognite"]["token_url"],
            "client_id": st.secrets["cognite"]["client_id"],
            "client_secret": st.secrets["cognite"]["client_secret"],
            "scopes": st.secrets["cognite"]["scopes"],
        }
    )



# -----------------------
# Fetch data from a View
# -----------------------
@st.cache_data(ttl=0)  # fetch fresh data on every refresh
def fetch_view(space: str, external_id: str, version: str) -> pd.DataFrame:
    client = get_client()
    view = client.models.views.retrieve(space=space, external_id=external_id, version=version)
    rows = client.models.instances.list(view_id=view.as_id())
    df = pd.DataFrame([row.properties for row in rows])

    # Convert date/time fields
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce", dayfirst=True)
    if "createdTime" in df.columns:
        df["createdTime"] = pd.to_datetime(df["createdTime"], errors="coerce")
    if "lastUpdatedTime" in df.columns:
        df["lastUpdatedTime"] = pd.to_datetime(df["lastUpdatedTime"], errors="coerce")

    return df


# -----------------------
# Streamlit App
# -----------------------
st.title("⚽ Betting Dashboard (CDF View)")
st.caption("Always fetching the latest data from Cognite Data Fusion")

space = "tippelaget_space_name"
view_external_id = "Bet"   # 👈 replace with your actual view name
view_version = "1"

df = fetch_view(space, view_external_id, view_version)

if df.empty:
    st.warning("No bets found in this view.")
else:
    st.subheader("Raw Bets Data")
    st.dataframe(df)

    # Summary KPIs
    st.subheader("Summary")
    total_bets = len(df)
    total_stake = df["betNok"].sum()
    total_payout = df["payout"].sum()
    roi = (total_payout - total_stake) / total_stake * 100 if total_stake > 0 else 0

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Bets", total_bets)
    col2.metric("Total Stake (NOK)", f"{total_stake:,.0f}")
    col3.metric("Total Payout (NOK)", f"{total_payout:,.0f}")
    col4.metric("ROI %", f"{roi:.1f}%")

    # Aggregation per player
    st.subheader("Performance by Player")
    player_stats = df.groupby("player").agg(
        bets=("externalId", "count"),
        total_stake=("betNok", "sum"),
        total_payout=("payout", "sum"),
    )
    player_stats["ROI %"] = (player_stats["total_payout"] - player_stats["total_stake"]) / player_stats["total_stake"] * 100
    st.dataframe(player_stats)

    # Chart: Stake vs. Payout by Player
    chart = (
        alt.Chart(player_stats.reset_index())
        .mark_bar()
        .encode(
            x="player:N",
            y="total_stake:Q",
            color=alt.Color("player:N", legend=None),
            tooltip=["player", "total_stake", "total_payout", "ROI %"],
        )
    )
    payout_chart = (
        alt.Chart(player_stats.reset_index())
        .mark_bar(opacity=0.6, color="green")
        .encode(
            x="player:N",
            y="total_payout:Q",
            tooltip=["player", "total_stake", "total_payout", "ROI %"],
        )
    )
    st.altair_chart(chart + payout_chart, use_container_width=True)

    # Bets timeline
    if "date" in df.columns:
        st.subheader("Bets over Time")
        timeline = (
            alt.Chart(df)
            .mark_circle(size=80)
            .encode(
                x="date:T",
                y="betNok:Q",
                color="player:N",
                tooltip=["description", "odds", "betNok", "payout", "player", "gameweek"],
            )
        )
        st.altair_chart(timeline, use_container_width=True)
