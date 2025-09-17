import streamlit as st
st.set_page_config(page_title="Tippelaget", page_icon="⚽", layout="wide", initial_sidebar_state="collapsed")
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

    lite_mode = st.toggle("⚡ Lite mode (recommended on mobile)", value=False, help="Render only one section at a time to speed up on phones.")

    if lite_mode:
        section = st.selectbox(
            "Section",
            [
                "Total Payout",
                "Average Odds",
                "Cumulative Payout",
                "Win Rate",
                "Cumulative vs Baseline",
                "Team Total",
                "Luckiness / Ball knowledge?",
                "Tippekassa vs Baseline",
                "The Prophet",
                "King Carl Gustaf's wisdom 🇸🇪",
            ],
        )

        if section == "Total Payout":
            render_total_payout(df)
        elif section == "Average Odds":
            render_average_odds(df)
        elif section == "Cumulative Payout":
            render_cumulative_payout(df)
        elif section == "Win Rate":
            render_win_rate(df)
        elif section == "Cumulative vs Baseline":
            render_cumulative_vs_baseline(df)
        elif section == "Team Total":
            render_team_total(df)
        elif section == "Luckiness / Ball knowledge?":
            render_luckiness(df)
        elif section == "Tippekassa vs Baseline":
            innskudd_df = create_monthly_innskudd_df()
            render_tippekassa_vs_baseline(df, innskudd_df)
        elif section == "The Prophet":
            render_prophet(df)
        elif section == "King Carl Gustaf's wisdom 🇸🇪":
            render_king(df)
    else:
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
        from tippelaget.core.data import execute_workflow, check_workflow_status
        with st.spinner("Updating... This may take a while."):
            res = execute_workflow(wf_external_id="wf_tippelaget_workflow", version="1")
            st.success(f"Workflow started with job id: {res.id}. It may take a few minutes to complete.")
            st.info("Please refresh the page after a while to see updated data." + f"{res}")
            # check status every 10 seconds until complete
            import time
            status = "running"
            while status == "running":
                time.sleep(10)
                status = check_workflow_status(res.id)
                st.info(f"Workflow status: {status}")
            st.success("Workflow completed!")

if __name__ == "__main__":
    main()
