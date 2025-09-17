import streamlit as st
import pandas as pd

from tippelaget.core.data import get_prepared_bets, create_monthly_innskudd_df
from tippelaget.ui.plotting import configure_theme
from tippelaget.views.metrics import (
    render_total_payout,
    render_average_odds,
    render_cumulative_payout,
    render_win_rate,
    render_cumulative_vs_baseline,
    render_team_total,
    render_luckiness,
    render_tippekassa_vs_baseline,
)
from tippelaget.views.assistants import render_prophet, render_king


def main() -> None:
    st.title("📊 Tippelaget Season 2 ⚽ ")

    configure_theme()
    df = get_prepared_bets()

    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
        "Total Payout", "Average Odds", "Cumulative Payout",
        "Win Rate", "Cumulative vs Baseline", "Team Total", "Luckiness / Ball knowledge?", "Tippekassa vs Baseline",
    ])

    with tab1:
        render_total_payout(df)

    with tab2:
        render_average_odds(df)

    with tab3:
        render_cumulative_payout(df)

    with tab4:
        render_win_rate(df)

    with tab5:
        render_cumulative_vs_baseline(df)

    with tab6:
        render_team_total(df)

    with tab7:
        render_luckiness(df)

    with tab8:
        innskudd_df = create_monthly_innskudd_df()
        render_tippekassa_vs_baseline(df, innskudd_df)

    tab9, tab10 = st.tabs(["The Prophet", "King Carl Gustaf's wisdom 🇸🇪"])
    with tab9:
        render_prophet(df)
    with tab10:
        render_king(df)

    #button to execute workflow to update the bets view
    if st.button("Populate data model"):
        from tippelaget.core.data import execute_workflow
        with st.spinner("Updating... This may take a while."):
            res = execute_workflow("wf_tippelaget_workflow")
            st.success(f"Workflow started with job id: {res.id}. It may take a few minutes to complete.")
            st.info("Please refresh the page after a while to see updated data." + f"{res}")

if __name__ == "__main__":
    main()
