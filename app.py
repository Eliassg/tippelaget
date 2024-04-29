import streamlit as st
import pandas as pd
import altair as alt

# Hardcoded data as a DataFrame
data = pd.DataFrame({
    'Uke': [1, 2, 3, 4, 5, 6, 7],
    'Reisekassa': [600, 600, 600, 600, 600, 1411, 1769],
    'Baseline': [800, 1000, 1200, 1400, 1600, 2200, 2400]
})

# Function to create line chart
def line_chart(data):
    # Reshape the data
    melted_data = pd.melt(data, id_vars=['Uke'], var_name='Category', value_name='Value')

    # Define chart properties
    chart = alt.Chart(melted_data).mark_line().encode(
        x=alt.X('Uke:Q', axis=alt.Axis(format='d')),  # Display integer increments on x-axis
        y=alt.Y('Value:Q', axis=alt.Axis(title='NOK')),  # Shared y-axis title
        color=alt.Color('Category:N', legend=alt.Legend(), scale=alt.Scale(domain=['Reisekassa', 'Baseline'], range=['blue', 'darkred'])),  # Separate lines by category and set custom colors
        tooltip=['Uke', 'Value']
    ).properties(
        width=700,
        height=400,
        title='Tippelaget - Reisekassa vs. Baseline'
    ).configure_legend(
        titleFontSize=14,
        labelFontSize=12
    )

    return chart

# Main function to run the Streamlit app
def main():
    st.set_page_config(page_title='Tippelaget Analytics', layout='wide')

    # Custom theme
    st.altair_chart(line_chart(data), use_container_width=True)

    st.markdown("---")
    st.write("Trust the process")

if __name__ == '__main__':
    main()
