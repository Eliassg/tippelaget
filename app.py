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

# Function to create line chart for Reisekassa and Baseline without the legend
def line_chart(data):

    melted_data = pd.melt(data[['Uke', 'Reisekassa', 'Baseline']], id_vars=['Uke'], var_name='Category', value_name='Value')

    # Define chart properties without legend
    chart = alt.Chart(melted_data).mark_line().encode(
        x=alt.X('Uke:Q', axis=alt.Axis(format='d')),
        y=alt.Y('Value:Q', axis=alt.Axis(title='NOK')),
        color=alt.Color('Category:N', legend=None, scale=alt.Scale(range=['blue', 'darkred'])),  # Separate lines by category and set custom colors
        tooltip=['Uke', 'Value']
    ).properties(
        width=700,
        height=400,
        title='Reisekassa vs. Baseline'
    )

    # Define legend separately
    legend = alt.Chart(melted_data).mark_point().encode(
        y=alt.Y('Category:N', axis=alt.Axis(orient='right')),
        color=alt.Color('Category:N', scale=alt.Scale(range=['blue', 'darkred'])),
    ).properties(
        width=700,
        height=50
    )

    return chart, legend

# Function to create "head to head" chart without the legend
def head_to_head_chart(data):

    head_to_head_data = data.iloc[:, :5]

    melted_data = pd.melt(head_to_head_data, id_vars=['Gameweek'], var_name='Person', value_name='Value')

    # Define chart properties without legend
    chart = alt.Chart(melted_data).mark_line().encode(
        x=alt.X('Gameweek:Q', axis=alt.Axis(format='d')),
        y=alt.Y('Value:Q', axis=alt.Axis(title='NOK')),
        color=alt.Color('Person:N', legend=None),
        tooltip=['Gameweek', 'Value']
    ).properties(
        width=700,
        height=400,
        title='Head to Head Comparison of Ball Knowledge'
    )

    # Define legend separately
    legend = alt.Chart(melted_data).mark_point().encode(
        y=alt.Y('Person:N', axis=alt.Axis(orient='right')),
        color=alt.Color('Person:N')
    ).properties(
        width=700,
        height=50
    )

    return chart, legend

def prediction_line_chart(data):
    actual_data = data[data['Uke'] <= 19]
    predicted_data = data[data['Uke'] >= 19]

    melted_actual_data = pd.melt(actual_data[['Uke', 'Reisekassa', 'Baseline']], id_vars=['Uke'], var_name='Category', value_name='Value')
    melted_predicted_data = pd.melt(predicted_data[['Uke', 'Reisekassa']], id_vars=['Uke'], var_name='Category', value_name='Value')
    melted_predicted_base_data = pd.melt(predicted_data[['Uke', 'Baseline']], id_vars=['Uke'], var_name='Category', value_name='Value')
    
    # Define chart properties for actual Reisekassa line
    actual_line = alt.Chart(melted_actual_data).mark_line().encode(
        x=alt.X('Uke:Q', axis=alt.Axis(format='d')),
        y=alt.Y('Value:Q', axis=alt.Axis(title='NOK')),
        color=alt.Color('Category:N', legend=None, scale=alt.Scale(range=['blue', 'darkred'])),
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

    vertical_rule = alt.Chart(pd.DataFrame({'Uke': [19]})).mark_rule(color='grey', strokeDash=[3, 3]).encode(
        x='Uke:Q',
        size=alt.value(2)
    )

    # Combine actual and predicted lines
    chart = alt.layer(actual_line, predicted_line, predicted_base, vertical_rule).properties(
        width=700,
        height=400,
        title='Reisekassa vs. Baseline - Predictions'
    )

    # Define legend separately
    legend_data = pd.DataFrame({'Category': ['Reisekassa', 'Baseline'], 'color': ['blue', 'darkred']})
    legend = alt.Chart(legend_data).mark_point().encode(
        y=alt.Y('Category:N', axis=alt.Axis(orient='right')),
        color=alt.Color('color:N', scale=None)
    ).properties(
        width=700,
        height=50
    )

    return chart, legend


# Main function to run the Streamlit app
def main():
    st.set_page_config(page_title='Tippelaget Analytics', layout='wide')

    st.title("Tippelaget - Road to Köln :rocket:")
    st.image('sudkurve.jpg', use_column_width=True)

    data, data2, data3 = load_data()   

    chart1, legend1 = line_chart(data)
    st.altair_chart(chart1, use_container_width=True)
    st.altair_chart(legend1, use_container_width=True)
    st.markdown("---")

    chart2, legend2 = head_to_head_chart(data3)
    st.altair_chart(chart2, use_container_width=True)
    st.altair_chart(legend2, use_container_width=True)
    st.markdown("---")

    chart3, legend3 = prediction_line_chart(data2)
    st.altair_chart(chart3, use_container_width=True)
    st.altair_chart(legend3, use_container_width=True)
    st.markdown("Based on state of the art prediction models from OpenAI, Meta, Alphabet and Alibaba, taking into account the joint ball knowledge within Tippelaget's members.")
    st.markdown("---")
    st.write('"Trust the process"')

if __name__ == '__main__':
    main()
