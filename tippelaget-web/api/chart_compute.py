from __future__ import annotations

from typing import Any

import pandas as pd


def _records(df: pd.DataFrame) -> list[dict[str, Any]]:
    if df.empty:
        return []
    return df.replace({float("nan"): None}).to_dict(orient="records")


def compute_total_payout(df: pd.DataFrame) -> list[dict[str, Any]]:
    if df.empty:
        return []
    payouts = df.groupby("player")["payout"].sum().reset_index()
    return _records(payouts)


def compute_average_odds(df: pd.DataFrame) -> list[dict[str, Any]]:
    if df.empty:
        return []
    odds = df.groupby("player")["odds"].mean().reset_index()
    return _records(odds)


def compute_cumulative_payout_series(df: pd.DataFrame) -> list[dict[str, Any]]:
    if df.empty:
        return []
    df_sorted = df.sort_values(["player", "gameweek_num", "date"]).copy()
    df_sorted["payout"] = df_sorted["payout"].fillna(0)
    df_sorted["cumulative_payout"] = df_sorted.groupby("player")["payout"].cumsum()
    out = []
    for player, group in df_sorted.groupby("player"):
        pts = [
            {"gameweek_num": int(r.gameweek_num), "cumulative_payout": float(r.cumulative_payout)}
            for r in group.itertuples()
        ]
        out.append(
            {
                "player": str(player),
                "points": pts,
                "last_label": f"{group['cumulative_payout'].iloc[-1]:.0f}",
            }
        )
    return out


def compute_win_rate(df: pd.DataFrame) -> list[dict[str, Any]]:
    if df.empty:
        return []
    weekly = (
        df.groupby(["player", "gameweek"])
        .agg(
            total_payout=("payout", "sum"),
            total_bet=("betNok", "sum"),
        )
        .reset_index()
    )
    weekly["won_week"] = weekly["total_payout"] >= weekly["total_bet"]
    winrate = weekly.groupby("player")["won_week"].mean().reset_index()
    winrate.rename(columns={"won_week": "win_rate"}, inplace=True)
    return _records(winrate)


def compute_cumulative_vs_baseline(df: pd.DataFrame) -> dict[str, Any]:
    if df.empty:
        return {"players": [], "baseline": []}
    weekly = df.groupby(["player", "gameweek_num"], as_index=False).agg(
        payout=("payout", "sum"),
        stake=("betNok", "sum"),
    )
    weekly["cumulative_payout"] = weekly.groupby("player")["payout"].cumsum()
    n_players = weekly["player"].nunique()
    baseline = (weekly.groupby("gameweek_num")["stake"].sum().cumsum() / n_players).reset_index(
        name="per_player_stake"
    )
    players = []
    for player, group in weekly.groupby("player"):
        pts = [
            {"gameweek_num": int(r.gameweek_num), "cumulative_payout": float(r.cumulative_payout)}
            for r in group.itertuples()
        ]
        players.append(
            {
                "player": str(player),
                "points": pts,
                "last_label": f"{group['cumulative_payout'].iloc[-1]:.0f}",
            }
        )
    base_pts = [
        {"gameweek_num": int(r.gameweek_num), "per_player_stake": float(r.per_player_stake)}
        for r in baseline.itertuples()
    ]
    return {
        "players": players,
        "baseline": base_pts,
        "baseline_last_label": f"{baseline['per_player_stake'].iloc[-1]:.0f}" if not baseline.empty else "",
    }


def compute_team_total(df: pd.DataFrame) -> dict[str, Any]:
    if df.empty:
        return {"series": [], "diff": None}
    team_weekly = df.groupby("gameweek_num", as_index=False).agg(
        payout=("payout", "sum"),
        stake=("betNok", "sum"),
    )
    team_weekly["cumulative_payout"] = team_weekly["payout"].cumsum()
    team_weekly["cumulative_stake"] = team_weekly["stake"].cumsum()
    series = [
        {
            "gameweek_num": int(r.gameweek_num),
            "cumulative_payout": float(r.cumulative_payout),
            "cumulative_stake": float(r.cumulative_stake),
        }
        for r in team_weekly.itertuples()
    ]
    last = team_weekly.sort_values("gameweek_num").iloc[-1]
    payout_last = float(last["cumulative_payout"]) if not pd.isna(last["cumulative_payout"]) else 0.0
    stake_last = float(last["cumulative_stake"]) if not pd.isna(last["cumulative_stake"]) else 0.0
    diff = payout_last - stake_last
    return {
        "series": series,
        "diff": diff,
        "last_gameweek": int(last["gameweek_num"]),
    }


def compute_luckiness(df: pd.DataFrame) -> dict[str, Any]:
    if df.empty:
        return {"bars": [], "luckiest": None, "unluckiest": None}
    d = df.copy()
    d["expected_payout"] = d["betNok"] / d["odds"]
    luck = d.groupby("player", as_index=False).agg(
        total_payout=("payout", "sum"),
        total_expected=("expected_payout", "sum"),
    )
    luck["luck_ratio"] = luck["total_payout"] / luck["total_expected"]
    luck = luck.sort_values("luck_ratio", ascending=False)
    bars = _records(luck[["player", "luck_ratio"]])
    luckiest = luck.iloc[0].to_dict() if len(luck) else None
    unluckiest = luck.iloc[-1].to_dict() if len(luck) else None
    if luckiest:
        luckiest = {"player": str(luckiest["player"]), "luck_ratio": float(luckiest["luck_ratio"])}
    if unluckiest:
        unluckiest = {"player": str(unluckiest["player"]), "luck_ratio": float(unluckiest["luck_ratio"])}
    return {"bars": bars, "luckiest": luckiest, "unluckiest": unluckiest}


def compute_tippekassa_vs_baseline(df: pd.DataFrame, innskudd_df: pd.DataFrame) -> dict[str, Any]:
    if df.empty:
        return {"series": []}
    gw_dates = df.groupby("gameweek_num")["date"].min().reset_index()
    innskudd_df = innskudd_df.copy()

    def map_gw(x) -> int | None:
        m = gw_dates[gw_dates["date"] <= x]["gameweek_num"].max()
        return int(m) if pd.notna(m) else None

    innskudd_df["gameweek_num"] = innskudd_df["date"].apply(map_gw)
    weekly = df.groupby("gameweek_num", as_index=False).agg(
        total_payout=("payout", "sum"),
        total_stake=("betNok", "sum"),
    )
    ins_sum = innskudd_df.groupby("gameweek_num")["innskudd"].sum().reset_index()
    weekly = weekly.merge(ins_sum, on="gameweek_num", how="left")
    weekly["innskudd"] = weekly["innskudd"].fillna(0)
    weekly["cum_payout_plus_innskudd"] = (weekly["total_payout"] + weekly["innskudd"]).cumsum()
    weekly["cum_stake_plus_innskudd"] = (weekly["total_stake"] + weekly["innskudd"]).cumsum()
    series = [
        {
            "gameweek_num": int(r.gameweek_num),
            "cum_payout_plus_innskudd": float(r.cum_payout_plus_innskudd),
            "cum_stake_plus_innskudd": float(r.cum_stake_plus_innskudd),
        }
        for r in weekly.itertuples()
    ]
    return {"series": series}


def compute_all_dashboard(df: pd.DataFrame, innskudd_df: pd.DataFrame) -> dict[str, Any]:
    return {
        "total_payout": compute_total_payout(df),
        "average_odds": compute_average_odds(df),
        "cumulative_payout": compute_cumulative_payout_series(df),
        "win_rate": compute_win_rate(df),
        "cumulative_vs_baseline": compute_cumulative_vs_baseline(df),
        "team_total": compute_team_total(df),
        "luckiness": compute_luckiness(df),
        "tippekassa_vs_baseline": compute_tippekassa_vs_baseline(df, innskudd_df),
    }
