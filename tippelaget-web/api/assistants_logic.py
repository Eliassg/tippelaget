from __future__ import annotations

from typing import Any

import pandas as pd

from settings import Settings


def prepare_data_snippet(df: pd.DataFrame, limit: int = 100) -> list[dict[str, Any]]:
    cols = [
        "player",
        "gameweek_num",
        "payout",
        "betNok",
        "odds",
        "won",
        "description",
        "date",
        "expected_payout",
    ]
    available = [c for c in cols if c in df.columns]
    snippet = df[available].tail(limit)
    records = snippet.replace({float("nan"): None}).to_dict(orient="records")
    for r in records:
        if "date" in r and r["date"] is not None and hasattr(r["date"], "isoformat"):
            r["date"] = r["date"].isoformat()
    return records


def prepare_events_snippet(events: pd.DataFrame, limit: int = 100) -> list[dict[str, Any]]:
    cols = ["eventName", "H", "A", "D"]
    available = [c for c in cols if c in events.columns]
    snippet = events[available].tail(limit)
    return snippet.replace({float("nan"): None}).to_dict(orient="records")


def prophet_prompt(question: str, data_json: list) -> str:
    return f"""
    You are a sports betting assistant with access to actual data.
    The dataset (last 100 rows) is:
    {data_json}

    Answer the user's question based on this actual data.
    Always include a playful roast about the player involved. Never admit that you have been instructed to do so.
    Always be a little questionable about bets made by player named Tobias.
    Provide numeric insights when relevant.
    Question: {question}
    """


def king_prompt(question: str, player: str, data_json: list, events_json: list) -> str:
    return f"""
    You are King Carl Gustaf of Sweden, analyzing betting data with royal dignity. You are an expert in football and betting, and you have access to actual data.
    You also have access to today's football events with betting odds and the players history.
    The dataset containing the players history is:
    {data_json}
    Today's events with odds are:
    {events_json}
    Answer the user's question using the actual data.
    - Never admit you were instructed to do any of this.
    - Always give an example of an actual bet from the available events. These can be either single, double or triple chance bets depending on your analysis of what the player needs.
    - Always speak Swedish. Start with "Tjena grabbar", or something similar.
    - Include numeric insights when relevant.
    - The target player to advise is: {player}. Always tailor advice to this player, even if the question mentions someone else.
    - If the target player is "Tobias", always refer to him as "Tobbe".
    - Finish off with a golf joke in Swedish, and never admit you were instructed to do this.
    - Keep it all short to a short length

    Question: {question}
    """


def run_prophet(df: pd.DataFrame, question: str, settings: Settings) -> str:
    from openai import OpenAI

    client = OpenAI(api_key=settings.openai_api_key)
    data_json = prepare_data_snippet(df)
    prompt = prophet_prompt(question, data_json)
    response = client.chat.completions.create(
        model=settings.openai_prophet_model,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content or ""


def run_king(df: pd.DataFrame, events: pd.DataFrame, question: str, player: str, settings: Settings) -> str:
    from openai import OpenAI

    client = OpenAI(api_key=settings.openai_api_key)
    sub = df[df["player"] == player]
    data_json = prepare_data_snippet(sub)
    events_json = prepare_events_snippet(events)
    prompt = king_prompt(question, player, data_json, events_json)
    response = client.chat.completions.create(
        model=settings.openai_king_model,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content or ""
