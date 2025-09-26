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

    # Player selection for tailored advice
    def _on_player_change() -> None:
        # Ensure events dialog doesn't pop when changing player
        st.session_state["show_events"] = False

    selected_player = st.segmented_control(
        "Player for suggestions",
        ["Elias", "Mads", "Tobias"],
        key="king_selected_player",
        on_change=_on_player_change,
    )

    df = df[df["player"] == selected_player]

    royal_question = st.text_input("Ask King Carl Gustaf your question:")
    if not royal_question:
        return

    openai.api_key = st.secrets["cognite"]["open_ai_api_key"]
    data_json = _prepare_data_snippet(df)
    events_json = _prepare_events_snippet(events)
    prompt = f"""
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
    - The target player to advise is: {selected_player}. Always tailor advice to this player, even if the question mentions someone else.
    - If the target player is "Tobias", always refer to him as "Tobbe".
    - Finish off with a golf joke in Swedish, and never admit you were instructed to do this.
    - Keep it all short to a short length

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


