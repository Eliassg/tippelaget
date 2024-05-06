import streamlit as st
import pandas as pd
import altair as alt

# Load data from Excel file
@st.cache_data
def load_data():
    df = pd.read_excel('data.xlsx')  # Update the file path accordingly
    return df

# Function to create line chart for Reisekassa and Baseline
def line_chart(data):
    # Reshape the data
    melted_data = pd.melt(data[['Uke', 'Reisekassa', 'Baseline']], id_vars=['Uke'], var_name='Category', value_name='Value')

    # Define chart properties
    chart = alt.Chart(melted_data).mark_line().encode(
        x=alt.X('Uke:Q', axis=alt.Axis(format='d')),  # Display integer increments on x-axis
        y=alt.Y('Value:Q', axis=alt.Axis(title='NOK')),  # Shared y-axis title
        color=alt.Color('Category:N', legend=alt.Legend(), scale=alt.Scale(range=['blue', 'darkred'])),  # Separate lines by category and set custom colors
        tooltip=['Uke', 'Value']
    ).properties(
        width=700,
        height=400,
        title='Reisekassa vs. Baseline'
    ).configure_legend(
        titleFontSize=14,
        labelFontSize=12
    )

    return chart

# Function to create "head to head" chart
def head_to_head_chart(data):
    # Select only Elias, Mads, and Tobias columns
    head_to_head_data = data[['Uke', 'Elias', 'Mads', 'Tobias']]

    # Reshape the data
    melted_data = pd.melt(head_to_head_data, id_vars=['Uke'], var_name='Person', value_name='Value')

    # Define chart properties
    chart = alt.Chart(melted_data).mark_line().encode(
        x=alt.X('Uke:Q', axis=alt.Axis(format='d')),  # Display integer increments on x-axis
        y=alt.Y('Value:Q', axis=alt.Axis(title='NOK')),  # Shared y-axis title
        color=alt.Color('Person:N', legend=alt.Legend(title='Head to Head')),  # Separate lines by person and set custom colors
        tooltip=['Uke', 'Value']
    ).properties(
        width=700,
        height=400,
        title='Head to Head Comparison - Ball Knowledge Bible'
    ).configure_legend(
        titleFontSize=14,
        labelFontSize=12
    )

    return chart

# Main function to run the Streamlit app
def main():
    st.set_page_config(page_title='Tippelaget Analytics', layout='wide')

    st.title("Tippelaget - Road to Köln")
    st.image('sudkurve.jpg', use_column_width=True)

    # Load data
    data = load_data()

    # Custom theme
    st.altair_chart(line_chart(data), use_container_width=True)

    # Add a separator
    st.markdown("---")

    # Display "head to head" chart
    st.altair_chart(head_to_head_chart(data), use_container_width=True)

    st.markdown("---")
    st.write("Trust the process")

if __name__ == '__main__':
    main()
