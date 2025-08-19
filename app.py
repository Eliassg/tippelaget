import streamlit as st
import pandas as pd
import requests
from cognite.client import CogniteClient, ClientConfig
from cognite.client.data_classes.data_modeling.ids import ViewId
import altair as alt
import matplotlib.pyplot as plt
import seaborn as sns

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
def fetch_bet_view(
    space: str = "tippelaget_space_name", 
    view_external_id: str = "Bet", 
    version: str = "fcb537cee9eba5"  # 👈 replace with latest version if needed
) -> pd.DataFrame:
    client = get_client()
    
    # View identifier
    view_id = ViewId(space, view_external_id, version)

    # Retrieve the instances
    rows = client.data_modeling.instances.list(
        sources=[view_id],
        limit=1000
    )
    if not rows:
        print("⚠️ No rows found in this view")
        return pd.DataFrame()

    # ✅ Extract properties correctly
    extracted = []
    for row in rows:
        props = row.properties.get(view_id)  # each row has dict keyed by viewId
        extracted.append(props)

    # Convert to DataFrame
    df = pd.json_normalize(extracted)

    return df

# -----------------------
# Streamlit App
# -----------------------

# Fetch and display Bet view
df = fetch_bet_view()

st.title("📊 Tippelaget 2025 ⚽ ")

# --- Flatten columns ---
df = df.rename(columns={
    "player.externalId": "player",
    "gameweek.externalId": "gameweek"
})

# Drop unused space columns
df = df.drop(columns=["player.space", "gameweek.space"], errors="ignore")

# Convert gameweek string "GW_X" → integer
df["gameweek_num"] = df["gameweek"].str.extract(r"GW_(\d+)").astype(int)

# Win flag
df["won"] = df["payout"] > 0

# ---- Tabs ----
tab1, tab2, tab3, tab4 = st.tabs([
    "Total Payout", "Average Odds", "Cumulative Payout", "Win Rate"
])

# Set Seaborn dark theme and figure style
sns.set_theme(style="darkgrid")  # darkgrid works nicely in dark mode
sns.set_palette("Set2")           # nice soft colors

def style_ax(ax, title, xlabel=None, ylabel=None):
    """Apply consistent styling to axes."""
    ax.set_title(title, fontsize=16, weight="bold")
    if xlabel:
        ax.set_xlabel(xlabel, fontsize=12)
    if ylabel:
        ax.set_ylabel(ylabel, fontsize=12)
    ax.tick_params(axis='x', rotation=45)
    ax.grid(True, linestyle="--", alpha=0.5)

# --- Tab 1: Total Payout ---
with tab1:
    payouts = df.groupby("player")["payout"].sum().reset_index()

    fig, ax = plt.subplots(figsize=(8,5))
    sns.barplot(data=payouts, x="player", y="payout", ax=ax)
    style_ax(ax, "Total payout per player", ylabel="Total NOK")
    st.pyplot(fig)

# --- Tab 2: Average Odds ---
with tab2:
    odds = df.groupby("player")["odds"].mean().reset_index()

    fig, ax = plt.subplots(figsize=(8,5))
    sns.barplot(data=odds, x="player", y="odds", ax=ax)
    style_ax(ax, "Average odds per player", ylabel="Mean odds")
    st.pyplot(fig)

# --- Tab 3: Cumulative payout over time ---
with tab3:
    df_sorted = df.sort_values(["player", "gameweek_num", "date"])
    df_sorted["payout"] = df_sorted["payout"].fillna(0)
    df_sorted["cumulative_payout"] = df_sorted.groupby("player")["payout"].cumsum()

    fig, ax = plt.subplots(figsize=(10,6))
    for player, group in df_sorted.groupby("player"):
        ax.plot(group["gameweek_num"], group["cumulative_payout"], marker="o", linewidth=2, label=player)
        # Optional: annotate last value
        ax.text(group["gameweek_num"].iloc[-1]+0.1, group["cumulative_payout"].iloc[-1], f"{group['cumulative_payout'].iloc[-1]:.0f}", fontsize=9)

    style_ax(ax, "Cumulative payout per player", xlabel="Gameweek", ylabel="Cumulative NOK")
    ax.legend(title="Player", bbox_to_anchor=(1.05, 1), loc="upper left")
    st.pyplot(fig)

# --- Tab 4: Win Rate ---
with tab4:
    weekly = df.groupby(["player", "gameweek"]).agg(
        total_payout=("payout", "sum"),
        total_bet=("betNok", "sum")
    ).reset_index()

    weekly["won_week"] = weekly["total_payout"] >= weekly["total_bet"]
    winrate = weekly.groupby("player")["won_week"].mean().reset_index()

    fig, ax = plt.subplots(figsize=(8,5))
    sns.barplot(data=winrate, x="player", y="won_week", ax=ax)
    style_ax(ax, "Win rate per player (by gameweek)", ylabel="Win rate (%)")
    ax.set_yticklabels([f"{int(x*100)}%" for x in ax.get_yticks()])
    st.pyplot(fig)
