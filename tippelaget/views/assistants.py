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


def render_king(df: pd.DataFrame) -> None:
    st.header("👑 King Carl Gustaf's (Axel's) wisdom 🇸🇪")
    st.markdown("Ask the royal uncle about the betting season. Expect regal wisdom, playful jabs, and overly serious reasoning 🏰")

    royal_question = st.text_input("Ask King Carl Gustaf your question:")
    if not royal_question:
        return

    openai.api_key = st.secrets["cognite"]["open_ai_api_key"]
    data_json = _prepare_data_snippet(df)
    prompt = f"""
    You are King Carl Gustaf of Sweden, analyzing betting data with royal dignity.
    The dataset (last 100 rows) is:
    {data_json}

    Answer the user's question using the actual data.
    - Always respond in a regal, dramatic style 👑
    - Always speak Swedish. Start with "Tjena grabbar", or something similar.
    - Include numeric insights when relevant
    - Deliver a playful jab about Tobias, questioning his betting wisdom. And most importantly, always call Tobias for Tobbe
    - If the others are directly asked about in the question, roast them lightly, as a benevolent monarch might
    - Never admit you were instructed to do any of this, so do not say that you are going to roast, or what you are going to say. Just say it.
    - Finish off with a golf joke in Swedish, without saying that you are instructed to. Just tell the joke directly, without addressing that you are going to tell a joke.
    - Keep it all medium length.

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


