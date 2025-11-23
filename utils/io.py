import pandas as pd
import streamlit as st

@st.cache_data
def load_data():
    """Load the Capital Bikeshare dataset"""
    try:
        df = pd.read_csv('data/202510-capitalbikeshare-tripdata.csv')
        return df
    except FileNotFoundError:
        st.error("Data file not found. Please ensure the CSV file is in the data/ directory.")
        return pd.DataFrame()

def get_data_summary(df):
    """Generate basic data summary"""
    summary = {
        'total_records': len(df),
        'date_range': {
            'start': df['started_at'].min(),
            'end': df['started_at'].max()
        },
        'member_casual_ratio': df['member_casual'].value_counts(normalize=True).to_dict(),
        'bike_type_distribution': df['rideable_type'].value_counts().to_dict()
    }
    return summary