import streamlit as st
import pandas as pd
import altair as alt

# Load data from Excel file
@st.cache_data
def load_data():
    df = pd.read_excel('data.xlsx', sheet_name='Sheet1')
    df2 = pd.read_excel('data.xlsx', sheet_name='Sheet2')
    df3 = pd.read_excel('data.xlsx', sheet_name='Sheet3')
    print(df3.columns)

    return df, df2, df3

# Function to create line chart for Reisekassa and Baseline
def line_chart(data):

    melted_data = pd.melt(data[['Uke', 'Reisekassa', 'Baseline']], id_vars=['Uke'], var_name='Category', value_name='Value')

    # Define chart properties
    chart = alt.Chart(melted_data).mark_line().encode(
        x=alt.X('Uke:Q', axis=alt.Axis(format='d')),
        y=alt.Y('Value:Q', axis=alt.Axis(title='NOK')),
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

    head_to_head_data = data

    melted_data = pd.melt(head_to_head_data, id_vars=['Gameweek'], var_name='Person', value_name='Value')

    # Define chart properties
    chart = alt.Chart(melted_data).mark_line().encode(
        x=alt.X('Gameweek:Q', axis=alt.Axis(format='d')),
        y=alt.Y('Value:Q', axis=alt.Axis(title='NOK')),
        color=alt.Color('Person:N', legend=alt.Legend(title='Head to Head')),
        tooltip=['Gameweek', 'Value']
    ).properties(
        width=700,
        height=400,
        title='Head to Head Comparison of Ball Knowledge'
    ).configure_legend(
        titleFontSize=14,
        labelFontSize=12
    )

    return chart

def prediction_line_chart(data):
    actual_data = data[data['Uke'] <= 9]
    predicted_data = data[data['Uke'] >= 9]

    melted_actual_data = pd.melt(actual_data[['Uke', 'Reisekassa', 'Baseline']], id_vars=['Uke'], var_name='Category', value_name='Value')
    melted_predicted_data = pd.melt(predicted_data[['Uke', 'Reisekassa']], id_vars=['Uke'], var_name='Category', value_name='Value')
    melted_predicted_base_data = pd.melt(predicted_data[['Uke', 'Baseline']], id_vars=['Uke'], var_name='Category', value_name='Value')
    
    # Define chart properties for actual Reisekassa line
    actual_line = alt.Chart(melted_actual_data).mark_line().encode(
        x=alt.X('Uke:Q', axis=alt.Axis(format='d')),
        y=alt.Y('Value:Q', axis=alt.Axis(title='NOK')),
        color=alt.Color('Category:N', legend=alt.Legend(), scale=alt.Scale(range=['blue', 'darkred'])),
        tooltip=['Uke', 'Value']
    )

    predicted_base = alt.Chart(melted_predicted_base_data).mark_line().encode(
        x=alt.X('Uke:Q', axis=alt.Axis(format='d')),
        y=alt.Y('Value:Q', axis=alt.Axis(title='NOK')),
        color=alt.value('blue'),
        tooltip=['Uke', 'Value']
    )

    # Define chart properties for predicted Reisekassa line (dashed)
    predicted_line = alt.Chart(melted_predicted_data).mark_line(strokeDash=[5, 5]).encode(
        x=alt.X('Uke:Q', axis=alt.Axis(format='d')),
        y=alt.Y('Value:Q', axis=alt.Axis(title='NOK')),
        color=alt.value('darkred'),
        tooltip=['Uke', 'Value']
    )

    vertical_rule = alt.Chart(pd.DataFrame({'Uke': [8]})).mark_rule(color='grey', strokeDash=[3, 3]).encode(
        x='Uke:Q',
        size=alt.value(2)
    )

    # Combine actual and predicted lines
    chart = alt.layer(actual_line, predicted_line, predicted_base, vertical_rule).properties(
        width=700,
        height=400,
        title='Reisekassa vs. Baseline - Predictions'
    ).configure_legend(
        titleFontSize=14,
        labelFontSize=12
    )

    return chart




# Main function to run the Streamlit app
def main():
    st.set_page_config(page_title='Tippelaget Analytics', layout='wide')

    st.title("Tippelaget - Road to Köln :rocket:")
    st.image('sudkurve.jpg', use_column_width=True)

    data, data2, data3 = load_data()   

    st.altair_chart(line_chart(data), use_container_width=True)
    st.markdown("---")
    st.altair_chart(head_to_head_chart(data3), use_container_width=True)
    st.markdown("---")
    st.altair_chart(prediction_line_chart(data2), use_container_width=True)
    st.markdown("Based on state of the art prediction models from OpenAI, Meta, Alphabet and Alibaba, taking into account the joint ball knowledge within Tippelaget's members.")
    st.markdown("---")
    st.write('"Trust the process"')

if __name__ == '__main__':
    main()
