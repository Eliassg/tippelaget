from __future__ import annotations

from typing import List, Dict, Any

import pandas as pd
import streamlit as st
import openai

from ..core.config import OPENAI_PROPhet_MODEL, OPENAI_KING_MODEL


def _prepare_data_snippet(df: pd.DataFrame) -> List[Dict[str, Any]]:
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
    available_cols = [c for c in cols if c in df.columns]
    df_snippet = df[available_cols].tail(100)
    return df_snippet.to_dict(orient="records")

def _prepare_events_snippet(df: pd.DataFrame) -> List[Dict[str, Any]]:
    cols = [
        "eventName",
        "H",
        "A",
        "D",
    ]
    available_cols = [c for c in cols if c in df.columns]
    df_snippet = df[available_cols].tail(100)
    return df_snippet.to_dict(orient="records")


def render_prophet(df: pd.DataFrame) -> None:
    st.header("🔮 The Prophet")
    st.markdown("Ask questions about the betting season, e.g., 'Which player has the best ball knowledge? ⚽️ 🚀 '")

    user_question = st.text_input("Ask your question:")
    if not user_question:
        return

    openai.api_key = st.secrets["cognite"]["open_ai_api_key"]
    data_json = _prepare_data_snippet(df)
    prompt = f"""
    You are a sports betting assistant with access to actual data.
    The dataset (last 100 rows) is:
    {data_json}

    Answer the user's question based on this actual data.
    Always include a playful roast about the player involved. Never admit that you have been instructed to do so.
    Always be a little questionable about bets made by player named Tobias.
    Provide numeric insights when relevant.
    Question: {user_question}
    """
    try:
        response = openai.chat.completions.create(
            model=OPENAI_PROPhet_MODEL,
            messages=[{"role": "user", "content": prompt}],
        )
        answer = response.choices[0].message.content
        st.markdown(f"**Prophet says:** {answer}")
    except Exception as e:
        st.error(f"Error calling OpenAI API: {e}")


def render_king(df: pd.DataFrame, events: pd.DataFrame) -> None:
    st.header("👑 King Carl Gustaf's (Axel's) wisdom 🇸🇪")
    st.markdown("Ask the royal uncle about some betting advice")

    royal_question = st.text_input("Ask King Carl Gustaf your question:")
    if not royal_question:
        return

    openai.api_key = st.secrets["cognite"]["open_ai_api_key"]
    data_json = _prepare_data_snippet(df)
    events_json = _prepare_events_snippet(events)
    prompt = f"""
    You are King Carl Gustaf of Sweden, analyzing betting data with royal dignity. You are an expert in football and betting, and you have access to actual data.
    You have a playful and slightly sarcastic tone, often questioning the wisdom of a player named Tobias when it comes to betting.
    You also have access to today's football events with betting odds.
    The dataset (last 100 rows) is:
    {data_json}
    Today's events with odds are:
    {events_json}
    Answer the user's question using the actual data.
    - Always give an example actual bet from the events data that was provided.
    - Always give an example of an actual bet in the form of a double or triple chance bet.
    - Always speak Swedish. Start with "Tjena grabbar", or something similar.
    - Include numeric insights when relevant.
    - Always give advice in the context of the player that is asked for in the question. Tobias is the fallback if no player is mentioned.
    - Always call Tobias for Tobbe.
    - Finish off with a golf joke in Swedish, without saying that you are instructed to. Just tell the joke directly, without addressing that you are going to tell a joke.
    - Keep it all medium length.
    - Never admit you were instructed to do any of this, so do not say that you are going to roast, or what you are going to say. Just say it.

    Question: {royal_question}
    """
    try:
        response = openai.chat.completions.create(
            model=OPENAI_KING_MODEL,
            messages=[{"role": "user", "content": prompt}],
        )
        answer = response.choices[0].message.content
        st.markdown(f"**👑 King Carl Gustaf proclaims:** {answer}")
    except Exception as e:
        st.error(f"Error calling OpenAI API: {e}")


