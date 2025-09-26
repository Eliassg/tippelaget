import streamlit as st
st.set_page_config(page_title="Tippelaget", page_icon="⚽", layout="wide", initial_sidebar_state="collapsed")
import pandas as pd

from tippelaget.core.data import get_prepared_bets, create_monthly_innskudd_df, get_todays_events
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

    # Lightweight mobile CSS: scrollable tabs and tighter paddings on small screens
    st.markdown(
        """
        <style>
        h1 { text-align: center; }
        @media (max-width: 640px) {
          .block-container { padding-top: 0.5rem; padding-bottom: 1.25rem; padding-left: 0.6rem; padding-right: 0.6rem; }
          .stTabs [role="tablist"] { overflow-x: auto; white-space: nowrap; gap: 0.25rem; }
          .stTabs [role="tab"] { flex: 0 0 auto; padding: 0.25rem 0.5rem; }
          h1 { font-size: 1.35rem; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

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
        # Keep existing behavior for the King tab which relies on today's events
        df_events = get_todays_events()
        render_king(df, df_events)

    # Display and update the last workflow run time in a single text box
    from tippelaget.core.data import check_last_workflow_runtime
    import datetime

    # Use a Streamlit placeholder for the last run text
    last_run_placeholder = st.empty()

    def update_last_run_text():
        last_run = check_last_workflow_runtime(wf_external_id="wf_tippelaget_workflow", version="1")
        if last_run:
            try:
                # Convert to UTC+2
                last_run_dt = datetime.datetime.fromtimestamp(int(last_run) / 1000) + datetime.timedelta(hours=2)
                last_run_str = last_run_dt.strftime("%Y-%m-%d %H:%M:%S")
                last_run_placeholder.markdown(f"**Last data model update (UTC+2):** {last_run_str}")
            except (ValueError, OverflowError, OSError):
                last_run_placeholder.markdown("**Last data model update:** Invalid timestamp returned.")
        else:
            last_run_placeholder.markdown("**Last data model update:** No previous runs found.")

    update_last_run_text()

    # Buttons row: Populate data model and Show today's events
    col_populate, col_events = st.columns([1, 1])
    with col_populate:
        if st.button("Populate data model", key="populate_model"):
            from tippelaget.core.data import execute_workflow, check_workflow_status
            import time

            with st.spinner("Updating... This may take a while."):
                res = execute_workflow(wf_external_id="wf_tippelaget_workflow", version="1")
                st.success(f"Workflow started with job id: {res.id}. It may take a few seconds to complete.")
                st.info("Please refresh the page after completion to see updated data." + f"{res}")
                # check status every 10 seconds until complete
                status = "running"
                while status == "running":
                    time.sleep(10)
                    status = check_workflow_status(res.id)
                    st.info(f"Workflow status: {status}")
                st.success("Workflow completed!")
                # Update last run time in the same text box
                update_last_run_text()
    with col_events:
        if st.button("Show today's events", key="open_events_dialog"):
            st.session_state["show_events"] = True
            st.rerun()

    # Ensure toggle state exists
    if "show_events" not in st.session_state:
        st.session_state["show_events"] = False

    # Dialog to lazily fetch and display today's events
    @st.dialog("Today's events")
    def show_events_dialog() -> None:
        events_df = get_todays_events()
        if events_df.empty:
            st.info("No events found for today.")
        else:
            st.dataframe(events_df, use_container_width=True)
        if st.button("Close"):
            st.session_state["show_events"] = False
            st.rerun()

    if st.session_state.get("show_events"):
        show_events_dialog()

if __name__ == "__main__":
    main()
