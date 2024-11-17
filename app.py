import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image

# Load data from Excel file
@st.cache_data
def load_data():
    df = pd.read_excel('data.xlsx', sheet_name='Sheet1')
    df2 = pd.read_excel('data.xlsx', sheet_name='Sheet2')
    df3 = pd.read_excel('data.xlsx', sheet_name='Sheet3')
    return df, df2, df3

# Function to create line chart for Reisekassa and Baseline
def line_chart(data):
    melted_data = pd.melt(data[['Uke', 'Reisekassa', 'Baseline']], id_vars=['Uke'], var_name='Category', value_name='Value')

    fig = px.line(melted_data, x='Uke', y='Value', color='Category', 
                  labels={'Value': 'NOK', 'Uke': 'Week'},
                  title='Reisekassa vs. Baseline')
    fig.update_layout(
        legend=dict(orientation="h", yanchor="bottom", y=-0.4, xanchor="center", x=0.5),
        yaxis=dict(title_font=dict(size=12), tickfont=dict(size=10))
    )
    return fig

# Function to create "head to head" chart
def head_to_head_chart(data):
    head_to_head_data = data.iloc[:, :5]
    melted_data = pd.melt(head_to_head_data, id_vars=['Gameweek'], var_name='Person', value_name='Value')

    fig = px.line(melted_data, x='Gameweek', y='Value', color='Person',
                  labels={'Value': 'NOK', 'Gameweek': 'Gameweek'},
                  title='Head to Head Comparison of Ball Knowledge')

    # Load custom icons
    icon_mapping = {
        'Elias': 'elias.png',
        'Mads': 'mads.png',
        'Tobias': 'tobias.png',
    }

    scale_mapping = {
        'Elias': 0.8,
        'Mads': 1.6,
        'Tobias': 1.6,
    }


    
    scale_factor = 0.8  # Scale down the image

    for person, icon_path in icon_mapping.items():
        img = Image.open(icon_path)
        img_width, img_height = img.size
        
        subset = melted_data[melted_data['Person'] == person]
        for idx, row in subset.iterrows():
            if not pd.isnull(row['Value']):
                fig.add_layout_image(
                    dict(
                        source=img,
                        x=row['Gameweek'],
                        y=row['Value'],
                        xref="x",
                        yref="y",
                        sizex=img_width * scale_mapping[person],
                        sizey=img_height * scale_mapping[person],
                        xanchor="center",
                        yanchor="middle"
                    )
                )

    fig.update_layout(
        legend=dict(orientation="h", yanchor="bottom", y=-0.4, xanchor="center", x=0.5),
        yaxis=dict(title_font=dict(size=12), tickfont=dict(size=10))
    )
    return fig

# Function to create prediction line chart
def prediction_line_chart(data):
    actual_data = data[data['Uke'] <= 36]
    predicted_data = data[data['Uke'] >= 36]

    melted_actual_data = pd.melt(actual_data[['Uke', 'Reisekassa', 'Baseline']], id_vars=['Uke'], var_name='Category', value_name='Value')
    melted_predicted_data = pd.melt(predicted_data[['Uke', 'Reisekassa']], id_vars=['Uke'], var_name='Category', value_name='Value')
    melted_predicted_base_data = pd.melt(predicted_data[['Uke', 'Baseline']], id_vars=['Uke'], var_name='Category', value_name='Value')
    
    fig = go.Figure()

    # Add actual lines
    for category in melted_actual_data['Category'].unique():
        subset = melted_actual_data[melted_actual_data['Category'] == category]
        fig.add_trace(go.Scatter(x=subset['Uke'], y=subset['Value'], mode='lines', name=category))

    # Add predicted lines
    fig.add_trace(go.Scatter(x=melted_predicted_data['Uke'], y=melted_predicted_data['Value'], mode='lines', 
                             name='Reisekassa (Predicted)', line=dict(dash='dash', color='darkred')))
    fig.add_trace(go.Scatter(x=melted_predicted_base_data['Uke'], y=melted_predicted_base_data['Value'], mode='lines', 
                             name='Baseline (Predicted)', line=dict(dash='dash', color='blue')))

    # Add vertical rule
    fig.add_vline(x=36, line=dict(color='grey', dash='dash'))

    fig.update_layout(
        title='Reisekassa vs. Baseline - Predictions',
        xaxis_title='Week',
        yaxis_title='NOK',
        legend=dict(orientation="h", yanchor="bottom", y=-0.8, xanchor="center", x=0.5),
        yaxis=dict(title_font=dict(size=12), tickfont=dict(size=10))
    )
    return fig

# Main function to run the Streamlit app
def main():
    st.set_page_config(page_title='Tippelaget Analytics', layout='wide')

    st.title("Tippelaget - Road to Köln :rocket:")
    st.image('sudkurve.jpg', use_column_width=True)

    data, data2, data3 = load_data()

    st.plotly_chart(line_chart(data), use_container_width=True)
    st.markdown("---")
    st.plotly_chart(head_to_head_chart(data3), use_container_width=True)
    st.markdown("---")
    st.plotly_chart(prediction_line_chart(data2), use_container_width=True)
    st.markdown("Based on state of the art prediction models from OpenAI, Meta, Alphabet and Alibaba, taking into account the joint ball knowledge within Tippelaget's members.")
    st.markdown("---")
    st.write('"Trust the process"')

if __name__ == '__main__':
    main()
