import streamlit as st
import pandas as pd
import requests
from cognite.client import CogniteClient, ClientConfig
from cognite.client.data_classes.data_modeling.ids import ViewId
import altair as alt
import matplotlib.pyplot as plt
import seaborn as sns
import openai

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
    version: str = "fcb537cee9eba5"
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

    # Extract properties correctly
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

st.title("📊 Tippelaget Season 2 ⚽ ")

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

# --- Global Dark Mode ---
plt.style.use("dark_background")
sns.set_theme(style="dark")
sns.set_palette("Spectral")

def style_ax_dark(ax, title, xlabel=None, ylabel=None):
    """Apply consistent dark-mode styling to axes."""
    ax.set_facecolor("#0E1117")  # match Streamlit dark bg
    ax.set_title(title, fontsize=16, weight="bold", color="white")
    if xlabel:
        ax.set_xlabel(xlabel, fontsize=12, color="white")
    if ylabel:
        ax.set_ylabel(ylabel, fontsize=12, color="white")

    # Tick styling
    ax.tick_params(axis='x', rotation=45, colors="white")
    ax.tick_params(axis='y', colors="white")

    # Minimal grid
    ax.grid(True, linestyle="--", linewidth=0.6, alpha=0.4, color="gray")

    # Hide spines
    for spine in ax.spines.values():
        spine.set_visible(False)

def new_fig(size=(8,5)):
    """Create borderless dark figure."""
    return plt.subplots(figsize=size, facecolor="#0E1117")

# ---- Tabs ----
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "Total Payout", "Average Odds", "Cumulative Payout", 
    "Win Rate", "Cumulative vs Baseline", "Team Total", "Luckiness / Ball knowledge?"
])

# --- Tab 1: Total Payout ---
with tab1:
    payouts = df.groupby("player")["payout"].sum().reset_index()
    fig, ax = new_fig((8,5))
    sns.barplot(data=payouts, x="player", y="payout", ax=ax, palette="coolwarm", edgecolor=None, linewidth=0, alpha=0.9)
    style_ax_dark(ax, "Total payout per player", ylabel="Total NOK")
    st.pyplot(fig, use_container_width=True)

# --- Tab 2: Average Odds ---
with tab2:
    odds = df.groupby("player")["odds"].mean().reset_index()
    fig, ax = new_fig((8,5))
    sns.barplot(data=odds, x="player", y="odds", ax=ax, palette="mako", edgecolor=None, linewidth=0, alpha=0.9)
    style_ax_dark(ax, "Average odds per player", ylabel="Mean odds")
    st.pyplot(fig, use_container_width=True)

# --- Tab 3: Cumulative payout over time ---
with tab3:
    df_sorted = df.sort_values(["player", "gameweek_num", "date"])
    df_sorted["payout"] = df_sorted["payout"].fillna(0)
    df_sorted["cumulative_payout"] = df_sorted.groupby("player")["payout"].cumsum()

    fig, ax = new_fig((10,6))
    colors = sns.color_palette("Spectral", n_colors=df_sorted["player"].nunique())
    for (player, group), color in zip(df_sorted.groupby("player"), colors):
        ax.plot(
            group["gameweek_num"], group["cumulative_payout"],
            marker="o", markersize=6, linewidth=2.2, alpha=0.85, label=player, color=color
        )
        # annotate last point
        ax.text(
            group["gameweek_num"].iloc[-1] + 0.1,
            group["cumulative_payout"].iloc[-1],
            f"{group['cumulative_payout'].iloc[-1]:.0f}",
            fontsize=9, color=color
        )

    style_ax_dark(ax, "Cumulative payout per player", xlabel="Gameweek", ylabel="Cumulative NOK")
    ax.legend(
    title="Player",
    loc="upper left",
    frameon=False,
    facecolor="#0E1117",
    edgecolor="none",
    labelcolor="white"
    )

    st.pyplot(fig, use_container_width=True)

# --- Tab 4: Win Rate ---
with tab4:
    weekly = df.groupby(["player", "gameweek"]).agg(
        total_payout=("payout", "sum"),
        total_bet=("betNok", "sum")
    ).reset_index()
    weekly["won_week"] = weekly["total_payout"] >= weekly["total_bet"]
    winrate = weekly.groupby("player")["won_week"].mean().reset_index()

    fig, ax = new_fig((8,5))
    sns.barplot(data=winrate, x="player", y="won_week", ax=ax, palette="flare", edgecolor=None, linewidth=0, alpha=0.9)
    style_ax_dark(ax, "Win rate per player (by gameweek)", ylabel="Win rate (%)")
    ax.set_yticklabels([f"{int(x*100)}%" for x in ax.get_yticks()], color="white")
    st.pyplot(fig, use_container_width=True)

# --- Tab 5: Cumulative payout vs baseline (shared per-player stake) ---
with tab5:
    # Aggregate by player + gameweek
    weekly = df.groupby(["player", "gameweek_num"], as_index=False).agg(
        payout=("payout", "sum"),
        stake=("betNok", "sum")
    )

    # Cumulative payout per player
    weekly["cumulative_payout"] = weekly.groupby("player")["payout"].cumsum()

    # Shared baseline = team stake / number of players
    n_players = weekly["player"].nunique()
    baseline = (
        weekly.groupby("gameweek_num")["stake"].sum().cumsum() / n_players
    ).reset_index(name="per_player_stake")

    fig, ax = new_fig((10,6))
    colors = sns.color_palette("Set2", n_colors=weekly["player"].nunique())

    # Player payout curves
    for (player, group), color in zip(weekly.groupby("player"), colors):
        ax.plot(
            group["gameweek_num"], group["cumulative_payout"],
            marker="o", linewidth=2, alpha=0.9, color=color, label=player
        )

    # Shared baseline (per player)
    ax.plot(
        baseline["gameweek_num"], baseline["per_player_stake"],
        linestyle="--", linewidth=2.2, alpha=0.9, color="white", label="Baseline (stake/share)"
    )

    style_ax_dark(ax, "Cumulative payout vs baseline (equal stake share)", xlabel="Gameweek", ylabel="Cumulative NOK")
    ax.legend(
    title="Player / Metric",
    loc="upper left",
    frameon=True,                     # keep a box so text is visible
    facecolor="black",                # slightly lighter than background
    edgecolor="none",
    labelcolor="white",
    fontsize=9,
    title_fontsize=10,
    fancybox=True,                    # rounded corners
    framealpha=0.6                    # semi-transparent so it doesn’t hide data
)

    st.pyplot(fig, use_container_width=True)

# --- Tab 6: Team total (all players summed) ---
with tab6:
    # Aggregate by gameweek across all players
    team_weekly = df.groupby("gameweek_num", as_index=False).agg(
        payout=("payout", "sum"),
        stake=("betNok", "sum")
    )

    # Cumulative totals
    team_weekly["cumulative_payout"] = team_weekly["payout"].cumsum()
    team_weekly["cumulative_stake"] = team_weekly["stake"].cumsum()

    fig, ax = new_fig((10,6))
    ax.plot(
        team_weekly["gameweek_num"], team_weekly["cumulative_payout"],
        marker="o", linewidth=2.5, color="lime", label="Team Payout"
    )
    ax.plot(
        team_weekly["gameweek_num"], team_weekly["cumulative_stake"],
        linestyle="--", linewidth=2.5, color="orange", label="Baseline (stake)"
    )

    style_ax_dark(ax, "Team cumulative payout vs stake", xlabel="Gameweek", ylabel="Cumulative NOK")
    ax.legend(
        title="Metric",
        facecolor="#0E1117",
        edgecolor="none",
        labelcolor="white"
    )
    st.pyplot(fig, use_container_width=True)

# --- Tab 7: Luckiness (Actual vs Expected based on Odds) ---

with tab7:
    # Compute expected payout per bet
    df["expected_payout"] = df["betNok"] / df["odds"]

    # Aggregate by player
    luck = df.groupby("player", as_index=False).agg(
        total_payout=("payout", "sum"),
        total_expected=("expected_payout", "sum")
    )
    luck["luck_ratio"] = luck["total_payout"] / luck["total_expected"]

    # Sort by luckiness
    luck = luck.sort_values("luck_ratio", ascending=False)

    # Plot
    fig, ax = new_fig((8,5))
    sns.barplot(
        data=luck, x="player", y="luck_ratio",
        ax=ax, palette="coolwarm", edgecolor=None
    )
    style_ax_dark(ax, "Luckiness per player / Ball knowledge? (Actual ÷ EV)", ylabel="Luck Ratio (Ball knowledge?)")

    # Baseline at 1 (fair expectation)
    ax.axhline(1, linestyle="--", color="white", alpha=0.6)
    ax.set_yticklabels([f"{int(y*100)}%" for y in ax.get_yticks()], color="white")

    st.pyplot(fig, use_container_width=True)

    # Explanation with formula
    st.markdown(
        """
        ### 📖 How luck is calculated using Expected Value (EV)
        For each player, we compare **actual payout** to the **expected payout** based on odds:

        $$
        \\text{Luck ratio} = \\frac{\\text{Total Actual Payout}}{\\text{Total Expected Payout (EV)}} 
        $$

        where for each bet:  
        $$
        \\text{Expected Payout (EV)} = \\text{Stake} \\times \\frac{1}{\\text{Odds}}
        $$

        - **> 1** → player won more than expected (lucky)  
        - **< 1** → player won less than expected (unlucky)  
        - **= 1** → exactly as expected
        """
    )

    # Highlight extremes
    luckiest = luck.iloc[0]
    unluckiest = luck.iloc[-1]
    st.markdown(
        f"🏆 **Luckiest player (Lots of ball knowledge?):** {luckiest['player']} (ratio {luckiest['luck_ratio']:.2f})  \n"
        f"💀 **Unluckiest player (Lack of ball knowledge?):** {unluckiest['player']} (ratio {unluckiest['luck_ratio']:.2f})"
    )

# --- Tab 8: The Prophet (Ask questions about the data) ---
tab8 = st.tabs(["The Prophet"])[0]

with tab8:
    st.header("🔮 The Prophet")
    st.markdown(
        "Ask questions about the betting season, e.g., 'Which player has the best ball knowledge? ⚽️ 🚀 '"
    )

    # User input
    user_question = st.text_input("Ask your question:")

    if user_question:
        # Set API key from Streamlit secrets
        import openai
        openai.api_key = st.secrets["cognite"]["open_ai_api_key"]

        # Prepare a data-aware summary (limited for token safety)
        df_snippet = df[["player", "gameweek_num", "payout", "betNok", "odds", "won", "description", "date"]]
        df_snippet = df_snippet.head(100)  # first 100 rows to limit prompt size
        data_json = df_snippet.to_dict(orient="records")

        prompt = f"""
        You are a sports betting assistant with access to actual data.
        The dataset (first 100 rows) is:
        {data_json}

        Answer the user's question based on this actual data. 
        Always include a playful roast about the player involved.
        Never admit Tobias has made a good bet. 
        Provide numeric insights when relevant.
        Question: {user_question}
        """

        try:
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )

            answer = response.choices[0].message.content
            st.markdown(f"**Prophet says:** {answer}")

        except Exception as e:
            st.error(f"Error calling OpenAI API: {e}")

# Display json data
st.json(data_json)