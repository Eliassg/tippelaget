from __future__ import annotations

import pandas as pd
import seaborn as sns
import streamlit as st

from ..ui.plotting import new_fig, style_ax_dark, show_fig


def render_total_payout(df: pd.DataFrame) -> None:
    payouts = df.groupby("player")["payout"].sum().reset_index()
    fig, ax = new_fig((8, 5))
    sns.barplot(data=payouts, x="player", y="payout", ax=ax, palette="coolwarm", edgecolor=None, linewidth=0, alpha=0.9)
    style_ax_dark(ax, "Total payout per player", ylabel="Total NOK")
    show_fig(fig)


def render_average_odds(df: pd.DataFrame) -> None:
    odds = df.groupby("player")["odds"].mean().reset_index()
    fig, ax = new_fig((8, 5))
    sns.barplot(data=odds, x="player", y="odds", ax=ax, palette="mako", edgecolor=None, linewidth=0, alpha=0.9)
    style_ax_dark(ax, "Average odds per player", ylabel="Mean odds")
    show_fig(fig)


def render_cumulative_payout(df: pd.DataFrame) -> None:
    df_sorted = df.sort_values(["player", "gameweek_num", "date"]).copy()
    df_sorted["payout"] = df_sorted["payout"].fillna(0)
    df_sorted["cumulative_payout"] = df_sorted.groupby("player")["payout"].cumsum()

    fig, ax = new_fig((10, 6))
    colors = sns.color_palette("Spectral", n_colors=df_sorted["player"].nunique())
    for (player, group), color in zip(df_sorted.groupby("player"), colors):
        ax.plot(
            group["gameweek_num"], group["cumulative_payout"],
            marker="o", markersize=6, linewidth=2.2, alpha=0.85, label=player, color=color
        )
        ax.text(
            group["gameweek_num"].iloc[-1] + 0.1,
            group["cumulative_payout"].iloc[-1],
            f"{group['cumulative_payout'].iloc[-1]:.0f}",
            fontsize=9, color=color,
        )

    style_ax_dark(ax, "Cumulative payout per player", xlabel="Gameweek", ylabel="Cumulative NOK")
    ax.legend(
        title="Player",
        loc="upper left",
        frameon=False,
        facecolor="#0E1117",
        edgecolor="none",
        labelcolor="white",
    )
    show_fig(fig)


def render_win_rate(df: pd.DataFrame) -> None:
    weekly = df.groupby(["player", "gameweek"]).agg(
        total_payout=("payout", "sum"),
        total_bet=("betNok", "sum"),
    ).reset_index()
    weekly["won_week"] = weekly["total_payout"] >= weekly["total_bet"]
    winrate = weekly.groupby("player")["won_week"].mean().reset_index()

    fig, ax = new_fig((8, 5))
    sns.barplot(data=winrate, x="player", y="won_week", ax=ax, palette="flare", edgecolor=None, linewidth=0, alpha=0.9)
    style_ax_dark(ax, "Win rate per player (by gameweek)", ylabel="Win rate (%)")
    ax.set_yticklabels([f"{int(x*100)}%" for x in ax.get_yticks()], color="white")
    show_fig(fig)


def render_cumulative_vs_baseline(df: pd.DataFrame) -> None:
    weekly = df.groupby(["player", "gameweek_num"], as_index=False).agg(
        payout=("payout", "sum"),
        stake=("betNok", "sum"),
    )
    weekly["cumulative_payout"] = weekly.groupby("player")["payout"].cumsum()

    n_players = weekly["player"].nunique()
    baseline = (
        weekly.groupby("gameweek_num")["stake"].sum().cumsum() / n_players
    ).reset_index(name="per_player_stake")

    fig, ax = new_fig((10, 6))
    colors = sns.color_palette("Set2", n_colors=weekly["player"].nunique())
    for (player, group), color in zip(weekly.groupby("player"), colors):
        ax.plot(
            group["gameweek_num"], group["cumulative_payout"],
            marker="o", linewidth=2, alpha=0.9, color=color, label=player,
        )
    ax.plot(
        baseline["gameweek_num"], baseline["per_player_stake"],
        linestyle="--", linewidth=2.2, alpha=0.9, color="white", label="Baseline (stake/share)",
    )

    style_ax_dark(ax, "Cumulative payout vs baseline (equal stake share)", xlabel="Gameweek", ylabel="Cumulative NOK")
    ax.legend(
        title="Player / Metric",
        loc="upper left",
        frameon=True,
        facecolor="black",
        edgecolor="none",
        labelcolor="white",
        fontsize=9,
        title_fontsize=10,
        fancybox=True,
        framealpha=0.6,
    )
    show_fig(fig)


def render_team_total(df: pd.DataFrame) -> None:
    team_weekly = df.groupby("gameweek_num", as_index=False).agg(
        payout=("payout", "sum"),
        stake=("betNok", "sum"),
    )
    team_weekly["cumulative_payout"] = team_weekly["payout"].cumsum()
    team_weekly["cumulative_stake"] = team_weekly["stake"].cumsum()

    fig, ax = new_fig((10, 6))
    ax.plot(
        team_weekly["gameweek_num"], team_weekly["cumulative_payout"],
        marker="o", linewidth=2.5, color="lime", label="Team Payout",
    )
    ax.plot(
        team_weekly["gameweek_num"], team_weekly["cumulative_stake"],
        linestyle="--", linewidth=2.5, color="orange", label="Baseline (stake)",
    )
    style_ax_dark(ax, "Team cumulative payout vs stake", xlabel="Gameweek", ylabel="Cumulative NOK")
    ax.legend(title="Metric", facecolor="#0E1117", edgecolor="none", labelcolor="white")

    # Draw difference bar at the latest gameweek between the two lines and label the numeric value
    if not team_weekly.empty:
        last_row = team_weekly.sort_values("gameweek_num").iloc[-1]
        last_x = last_row["gameweek_num"]
        payout_last = float(last_row["cumulative_payout"]) if not pd.isna(last_row["cumulative_payout"]) else 0.0
        stake_last = float(last_row["cumulative_stake"]) if not pd.isna(last_row["cumulative_stake"]) else 0.0
        diff = payout_last - stake_last

        bottom = min(payout_last, stake_last)
        height = abs(diff)
        if height > 0:
            bar_color = "#4CAF50" if diff >= 0 else "orange"
            ax.bar(
                last_x,
                height,
                bottom=bottom,
                width=0.6,
                color=bar_color,
                alpha=0.35,
                edgecolor="none",
                zorder=1,
            )

            y_mid = bottom + height / 2.0
            ax.text(
                last_x,
                y_mid,
                f"{diff:.0f}",
                color="white",
                ha="center",
                va="center",
                fontsize=10,
                zorder=4,
            )

    show_fig(fig)


def render_luckiness(df: pd.DataFrame) -> None:
    df = df.copy()
    df["expected_payout"] = df["betNok"] / df["odds"]
    luck = df.groupby("player", as_index=False).agg(
        total_payout=("payout", "sum"),
        total_expected=("expected_payout", "sum"),
    )
    luck["luck_ratio"] = luck["total_payout"] / luck["total_expected"]
    luck = luck.sort_values("luck_ratio", ascending=False)

    fig, ax = new_fig((8, 5))
    sns.barplot(
        data=luck,
        x="player",
        y="luck_ratio",
        ax=ax,
        palette="coolwarm",
        edgecolor=None,
        linewidth=0,
        alpha=0.9,
    )
    style_ax_dark(ax, "Luckiness per player / Ball knowledge? (Actual ÷ EV)", ylabel="Luck Ratio (Ball knowledge?)")
    ax.axhline(1, linestyle="--", color="white", alpha=0.6)
    ax.set_yticklabels([f"{int(y*100)}%" for y in ax.get_yticks()], color="white")
    show_fig(fig)

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

    luckiest = luck.iloc[0]
    unluckiest = luck.iloc[-1]
    st.markdown(
        f"🏆 **Luckiest player (Lots of ball knowledge?):** {luckiest['player']} (ratio {luckiest['luck_ratio']:.2f})  \n"
        f"💀 **Unluckiest player (Lack of ball knowledge?):** {unluckiest['player']} (ratio {unluckiest['luck_ratio']:.2f})"
    )


def render_tippekassa_vs_baseline(df: pd.DataFrame, innskudd_df: pd.DataFrame) -> None:
    gw_dates = df.groupby("gameweek_num")["date"].min().reset_index()
    innskudd_df = innskudd_df.copy()
    innskudd_df["gameweek_num"] = innskudd_df["date"].apply(
        lambda x: gw_dates[gw_dates["date"] <= x]["gameweek_num"].max()
    )

    weekly = df.groupby("gameweek_num", as_index=False).agg(
        total_payout=("payout", "sum"),
        total_stake=("betNok", "sum"),
    )
    weekly = weekly.merge(
        innskudd_df.groupby("gameweek_num")["innskudd"].sum().reset_index(),
        on="gameweek_num",
        how="left",
    )
    weekly["innskudd"] = weekly["innskudd"].fillna(0)
    weekly["cum_payout_plus_innskudd"] = (weekly["total_payout"] + weekly["innskudd"]).cumsum()
    weekly["cum_stake_plus_innskudd"] = (weekly["total_stake"] + weekly["innskudd"]).cumsum()

    fig, ax = new_fig((10, 6))
    ax.plot(
        weekly["gameweek_num"], weekly["cum_payout_plus_innskudd"],
        marker="o", linewidth=2.5, color="#4CAF50", label="Total Winnings + Innskudd",
    )

    ax.plot(
        weekly["gameweek_num"], weekly["cum_stake_plus_innskudd"],
        linestyle="--", linewidth=2, color="white", alpha=0.8, label="Total Stake + Innskudd (baseline)",
    )

    style_ax_dark(ax, title="Tippekassa vs Baseline", xlabel="Gameweek", ylabel="Cumulative NOK")
    ax.legend(loc="upper left", frameon=False, facecolor="#0E1117", edgecolor="none", labelcolor="white")
    show_fig(fig)


