import streamlit as st
import pandas as pd
import altair as alt

# Load data from Excel file
@st.cache_data
def load_data():
    df = pd.read_excel('data.xlsx')
    return df

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

def main():
    st.set_page_config(page_title='Tippelaget Analytics', layout='wide')
    data = load_data()
    st.altair_chart(line_chart(data), use_container_width=True)
    st.markdown("---")
    st.write('"Trust the process" - Køøhln 2024')

if __name__ == '__main__':
    main()
