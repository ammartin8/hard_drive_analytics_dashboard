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
    page_title="Storage Drive Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- PAGE HEADER ---
st.markdown("<h1 style='margin-bottom:0;'>Storage Drive Analytics</h1>", unsafe_allow_html=True)
st.caption("Quarterly/Monthly metrics and failure trends for Backblaze Storage Drive Dataset")

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

def load_drive_quarterly_data_v2(ttl=3600):
    """Simulates querying BigQuery based on your architecture."""
    sql_query="""
    SELECT *
    FROM `hard_drive_dataset.latest_quarterly_drive_trends_per_manufacturer`
    """

    query_job = client.query(sql_query)
    df_results = query_job.result().to_dataframe()
    return df_results



df = load_drive_data() # Load cached data
df2 = load_drive_quarterly_data()
df3 = load_drive_quarterly_data_v2()

col1, col2= st.columns(2)

# Metric calculations
# Latest month
target_month = df['year_month'].iloc[-1]
filtered_df = df[df['year_month'] == target_month].copy()

# Prior month
previous_month = df['year_month'].iloc[-2]
previous_mth_filtered_df = df[df['year_month'] == previous_month].copy()

# Month over Month Difference
curr_net = filtered_df['total_drives'] - filtered_df['failed_drives']
prev_net = previous_mth_filtered_df['total_drives'] - previous_mth_filtered_df['failed_drives']
mth_over_mth_diff = (curr_net.sum() - prev_net.sum()) / prev_net.sum()

# Latest Year & Its Latest Quarter
target_yr = df2[df2['year_number'] == df2['year_number'].max()]
target_qtr = target_yr['quarter_number'].max()
filtered_qtr_df = target_yr[
                (target_yr['quarter_number'] == target_yr['quarter_number'].max())
                ].copy()

# Prior Quarter
# Handling previous_qtr logic first
if target_qtr == 1:
    previous_qtr = 4
else:
    previous_qtr = target_qtr - 1
previous_qtr_filtered_df = df2[df2['quarter_number'] == previous_qtr].copy()


# --- METRICS SECTION (KPI Tiles) ---
with col1:
    st.metric(label=f"Latest Month Active Drives: {target_month}", value=f"{(filtered_df['total_drives'].sum() - filtered_df['failed_drives'].sum()):,}", delta=f"{(mth_over_mth_diff):.02%}", delta_color="normal")

with col2:
    st.metric(label=f"Total Failed Drives Since: {df['year_number'].min()}", value=f"{df['failed_drives'].sum():,}", delta_color="inverse")    

# --- VIZ SECTION (Charts) ---
vis_data_latest = filtered_qtr_df[['year_number', 'quarter_number', 'manufacturer', 'total_drives', 'failed_drives', 'failure_rate']].copy()
# Row 1
col_chart1, col_chart2 = st.columns(2)

with col_chart1:
    st.subheader(f"Drive Reliability by Manufacturer (Q{target_yr['quarter_number'].max()}) {df2['year_number'].max()}")
    fig3 = make_subplots(specs=[[{"secondary_y": True}]])

    # --- Trace 1: Active Drives (Green, Bottom Layer) ---
    active_values = vis_data_latest['total_drives'] - vis_data_latest['failed_drives']
    fig3.add_trace(go.Bar(
        x=vis_data_latest['manufacturer'],
        y=active_values, # Calculated as Total - Failed
        name='Active',
        marker=dict(color='#4cc9f0'), 
        textposition='outside',
        opacity=.85
    ))

    # --- Trace 2: Failed Drives (Red, Top Layer) ---
    fig3.add_trace(go.Bar(
        x=vis_data_latest['manufacturer'],
        y=vis_data_latest['failed_drives'],
        name='Failed',
        marker=dict(color='red'),
        textposition='outside',
        opacity=.85
    ))

    # -- Trace 3: Adding Failure Rate Line
    fig3.add_trace(
    go.Scatter(
        x=vis_data_latest['manufacturer'],
        y=vis_data_latest['failure_rate'],
        mode='lines+markers',    
        name='Failure Rate (%)',
        line=dict(width=2, color='red'),
        marker=dict(size=6)
    ),
    secondary_y=True
    )

    # --- Update Layout ---
    fig3.update_layout(
        title=f"Total Active and Failed Drives in (Q{target_yr['quarter_number'].max()}) {df2['year_number'].max()}",
        xaxis_title="Manufacturer",
        yaxis_title="Number of Drives",
        
        barmode='stack',  
        hovermode='x unified',
        
        height=500, width=800,
    )

    fig3.update_yaxes(
        secondary_y=True,
        range=[0,1], 
        tickformat=',') 

    st.plotly_chart(fig3, use_container_width=True)

with col_chart2:
    st.subheader("Manufacturer & Model Storage Drive Trends")
    st.dataframe(df3,
    height=500,
    hide_index=True,
    column_config={
        # Rename the header text
        "year_number": st.column_config.TextColumn("year"), 
        "quarter_number": st.column_config.NumberColumn("quarter"),
        "failure_rate": st.column_config.NumberColumn("failure rate (%)")
    }
    )

# Row 2
col_chart3 = st.columns(1)[0]

with col_chart3:
    st.subheader("Monthly Storage Drive Health Trends")  
    # --- CREATE PLOTLY COLUMN CHART ---
    fig = go.Figure()

    # --- Trace 1: Active Drives (Green, Bottom Layer) ---
    fig.add_trace(go.Bar(
        x=df['month_year_name'],
        y=df['total_drives'] - df['failed_drives'], # Calculated as Total - Failed
        name='Active',
        marker=dict(color='#4cc9f0'), 
        textposition='outside',
        opacity=.85
    ))

    # --- Trace 2: Failed Drives (Red, Top Layer) ---
    fig.add_trace(go.Bar(
        x=df['month_year_name'],
        y=df['failed_drives'],
        name='Failed',
        marker=dict(color='red'),
        textposition='outside',
        opacity=.85
    ))

    # --- Update Layout ---
    fig.update_layout(
        xaxis_title="Month-Year",
        yaxis_title="Number of Drives",
        barmode='stack',  
        hovermode='x unified',
        height=500, width=800,
    )

    # --- DISPLAY IN STREAMLIT ---
    st.plotly_chart(fig, use_container_width=True)

# --- SIDEBAR FILTERS ---
with st.sidebar:
    st.header("📚 Data Definitions & Info")
    
    # --- Metric Definitions ---
    st.markdown("### Key Metrics")
    st.markdown(
        f"""
        **Active Drives**
        
        *Definition:* `Total Drives` minus `Failed Drives`.
        
        Represents healthy, online storage capacity.
        """
    )
    
    st.markdown(
        f"""
        **Failed Drives**
        
        *Definition:* Count of drives currently in a failed state.
        
        Examples include dead sectors or unresponsive drives.
        """
    )
    
    st.markdown(
        f"""
        **Failure Rate**
        
        *Definition:* Percentage of total drives that have failed.
        
        Calculated for the selected period or latest quarter.
        """
    )

    # --- Data Context ---
    st.markdown("---")
    st.markdown("### Data Context")
    
    # Constructing the context string with newlines
    latest_record = pd.to_datetime(df['month_year_name']).max() if 'month_year_name' in df.columns else "N/A"
    
    st.caption(
        f"*Latest Record:* {latest_record} (UTC)"
    )

    # --- Legend/Notes ---
    st.markdown("---")
    st.markdown("### 📝 Notes")
    
    notes_text = (
        "• Data is updated automatically on every page refresh.\n\n"
        "• 'Total Drives' includes drives in both Active and Failed states.\n\n"
        "• Charts are sorted by default to highlight high-impact manufacturers."
    )
    st.caption(notes_text)
    st.sidebar.markdown('''
    ---
    Created with ❤️ by [Amah](https://github.com/ammartin8).
    ''')
    
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
