import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from google.cloud import bigquery
import os

# --- BigQuery Configuration ---
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = './.google/credentials/google_credentials.json'
client = bigquery.Client()

# --- STREAMLIT CONFIGURATION ---
st.set_page_config(
    page_title="Data Drive Health Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- PAGE HEADER ---
st.markdown("<h1 style='margin-bottom:0;'>Data Drive Health Analytics</h1>", unsafe_allow_html=True)
st.caption("Real-time metrics and failure trends for Backblaze Dataset")

# --- DATA LOADING & CACHING ---
@st.cache_data(ttl=3600) # Cache for 1 hour by default
def load_drive_data():
    """Simulates querying BigQuery based on your architecture."""
    sql_query="""
    SELECT *
    FROM `hard_drive_dataset.monthly_fail_rates`
    """

    query_job = client.query(sql_query)
    df_results = query_job.result().to_dataframe()
    return df_results

def load_drive_quarterly_data(ttl=3600):
    """Simulates querying BigQuery based on your architecture."""
    sql_query="""
    SELECT *
    FROM `hard_drive_dataset.quarterly_fail_drives_per_manufacturer`
    """

    query_job = client.query(sql_query)
    df_results = query_job.result().to_dataframe()
    return df_results



df = load_drive_data() # Load cached data
df2 = load_drive_quarterly_data()

col1, col2= st.columns(2)

# Metric calculations
target_month = df['year_month'].max()
filtered_df = df[df['year_month'] == target_month]

# --- METRICS SECTION (KPI Tiles) ---
with col1:
    st.metric(label=f"Total Failed Drives Q{df['quarter_number'].max()}:", value=f"{df['failed_drives'].sum():,}", delta="+5%", delta_color="inverse")

with col2:
    st.metric(label=f"Active Drives: {df['year_month'].max()}", value=f"{(filtered_df['total_drives'].sum() - filtered_df['failed_drives'].sum()):,}", delta="+5%", delta_color="normal")

col_chart1, col_chart2 = st.columns(2)

# --- VIZ SECTION (Charts) ---
with col_chart1:
    fig3 = go.Figure()

    # --- Trace 1: Active Drives (Green, Bottom Layer) ---
    fig3.add_trace(go.Bar(
        x=df2['manufacturer'],
        y=df2['total_drives'] - df2['failed_drives'], # Calculated as Total - Failed
        name='Active',
        marker=dict(color='green'), 
        textposition='outside'
    ))

    # --- Trace 2: Failed Drives (Red, Top Layer) ---
    fig3.add_trace(go.Bar(
        x=df2['manufacturer'],
        y=df2['failed_drives'],
        name='Failed',
        marker=dict(color='red'),
        textposition='outside'
    ))

    # --- Update Layout ---
    fig3.update_layout(
        title="Drive Reliability by Manufacturer (Stacked)",
        xaxis_title="Manufacturer",
        yaxis_title="Number of Drives",
        
        barmode='stack',  
        hovermode='x unified',
        
        height=500, width=800,
    )

    # --- Customization for Professional Look ---
    fig3.update_yaxes(type="linear", tickformat=',') 

    st.plotly_chart(fig3, use_container_width=True)

with col_chart2:
    st.dataframe(df2,
    height=500)


col_chart3, col_chart4 = st.columns(2)

with col_chart3:
    st.subheader("Monthly Failed Drive Trends")    
    # --- CREATE PLOTLY COLUMN CHART ---
    fig = px.bar(
        df, 
        x='month_year_name', 
        y='failed_drives',
        title="Failed Drives Per Month",
        labels={'failed_drives': 'Number of Failed Drives'},
        template="plotly_dark",
        hover_data=['month_name', 'failed_drives', 'failure_rate']
    )

    fig.update_traces(
        marker_color='#4cc9f0',
        opacity=0.85,
        marker=dict(
            color='rgba(76, 201, 240, 0.85)',
            line=dict(width=1, color='white')
        )
    )

    fig.update_xaxes(
        title="Month", 
        tickfont=dict(size=12),
        tickangle=45,
    )

    fig.update_yaxes(
        title="Failed Drives",
        tickformat=',',
        range=[0,400]
    )

    # --- DISPLAY IN STREAMLIT ---
    st.plotly_chart(fig, use_container_width=True)

with col_chart4:
    st.subheader("Manufacture Drive Trends")

    fig2 = make_subplots(specs=[[{"secondary_y": True}]])

    fig2.add_trace(
        go.Bar(
            x=df2['manufacturer'],
            y=df2['failed_drives'], 
            name='Total Failed Drives',
            marker_color='#4cc9f0'
        ),
        secondary_y=False
    )

    fig2.add_trace(
        go.Scatter(
            x=df2['manufacturer'],
            y=df2['failure_rate'],
            mode='lines+markers',    
            name='Failure Rate (%)',
            line=dict(width=2, color='red'),
            marker=dict(size=6)
        ),
        secondary_y=True
    )

    fig2.update_layout(
        title_text="Drive Health: Failed Drives vs Failure Rates",
        yaxis_title="Total Failed Drives",
    )

    # Set Secondary (Right) Y-Axis title
    fig2.update_yaxes(
        title_text="Failure Rate (%)", 
        secondary_y=True,
        range=[0,1]
        )

    # --- DISPLAY IN STREAMLIT ---
    st.plotly_chart(fig2, use_container_width=True)

# --- SIDEBAR FILTERS ---
with st.sidebar:
    st.header("Filters")

    time_range = st.selectbox(
        "Time Range", 
        options=["Last 12 Months", "Last 6 Months", "All Time"],
        index=0,
        key="time_filter" # Unique key to prevent state confusion
    )

    st.sidebar.markdown('''
    ---
    Created with ❤️ by [Amah](https://amahmartin.me).
    ''')

# Filter logic
if time_range == "Last 6 Months":
    df = df.iloc[-6:]
    
# --- FOOTER / DATA INFO ---
st.markdown(
    '''
    ---
    ''')
with st.expander("📚 Source Info", expanded=True):
    st.write("""
    **Source:** Backblaze Hard Drive Data CSVs  
    **ETL Tool:** Apache Airflow (Python)  
    **Transformation:** dbt (Star Schema on BigQuery)  
    **Visualization:** Streamlit with Plotly 
    """)
