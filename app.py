# app.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from utils.io import load_data
from utils.prep import prepare_data, create_analysis_tables
from utils.viz import (
    create_kpi_metrics, create_time_series_chart, create_member_comparison_chart,
    create_station_analysis_chart, create_geographic_analysis, create_ride_duration_analysis,
    create_heatmap_analysis, create_bubble_chart, create_advanced_geographic_chart
)

# 页面配置 Page configuration
st.set_page_config(
    page_title="Capital Bikeshare Data Analysis",
    page_icon="🚲",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 加载和缓存数据 Load and cache data
@st.cache_data(show_spinner=False)
def get_processed_data():
    df_raw = load_data()
    df_processed = prepare_data(df_raw)
    tables = create_analysis_tables(df_processed)
    return df_raw, df_processed, tables

# 主应用 Main application
def main():
    st.title("🚲 Capital Bikeshare Data Analysis")
    st.caption("Source: Capital Bikeshare Trip Data - October 2025 - Public Dataset")
    
    # 加载数据 Load data
    with st.spinner('Loading and processing data...'):
        raw_df, processed_df, analysis_tables = get_processed_data()
    
    #  侧边栏筛选器 Sidebar filters
    with st.sidebar:
        st.header("🔍 Data Filters")
        
        # 日期范围筛选 Date range filter
        min_date = processed_df['started_at'].dt.date.min()
        max_date = processed_df['started_at'].dt.date.max()
        date_range = st.date_input(
            "Date Range",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date
        )
        
        # 用户类型筛选  User type filter
        user_types = st.multiselect(
            "User Type",
            options=processed_df['member_casual'].unique(),
            default=processed_df['member_casual'].unique()
        )
        
        # 自行车类型筛选 Bike type filter
        bike_types = st.multiselect(
            "Bike Type",
            options=processed_df['rideable_type'].unique(),
            default=processed_df['rideable_type'].unique()
        )
        
        # 时间段筛选 Time of day filter
        time_ranges = st.multiselect(
            "Time of Day",
            options=['Early Morning (12-6am)', 'Morning (6-12pm)', 'Afternoon (12-6pm)', 'Evening (6-12am)'],
            default=['Early Morning (12-6am)', 'Morning (6-12pm)', 'Afternoon (12-6pm)', 'Evening (6-12am)']
        )
        
        st.markdown("---")
        st.markdown("### 📊 Data Summary")
        st.metric("Total Rides", f"{len(processed_df):,}")
        st.metric("Members vs Casual", f"{len(processed_df[processed_df['member_casual']=='member']):,} / {len(processed_df[processed_df['member_casual']=='casual']):,}")
    
    # 应用筛选器 Apply filters
    filtered_df = processed_df.copy()
    
    if len(date_range) == 2:
        filtered_df = filtered_df[
            (filtered_df['started_at'].dt.date >= date_range[0]) & 
            (filtered_df['started_at'].dt.date <= date_range[1])
        ]
    
    if user_types:
        filtered_df = filtered_df[filtered_df['member_casual'].isin(user_types)]
    
    if bike_types:
        filtered_df = filtered_df[filtered_df['rideable_type'].isin(bike_types)]
    
    # 导航 Navigation
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📖 Navigation")
    page = st.sidebar.radio("Go to", [
        "📊 Executive Summary",
        "⏰ Time Analysis", 
        "👥 User Behavior",
        "📍 Geographic Insights",
        "🔍 Deep Dives",
        "📈 Conclusions"
    ])
    
    # 在侧边栏最下面添加Author信息和Logo Author info and logos at the bottom of sidebar
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 👨‍💻 Author Information")
    st.sidebar.markdown("**Author:** Baoyi Zhou")
    st.sidebar.markdown("**Email:** baoyi.zhou@efrei.net")
    st.sidebar.markdown("**GitHub:** https://github.com/baoyi11/Capital-Bikes-Share-Data-Analysis")
    st.sidebar.markdown("**Course: Data Visualization 2025**")
    st.sidebar.markdown("**Prof. Mano Mathew**")
    st.sidebar.markdown("[Check out this LinkedIn](https://www.linkedin.com/in/manomathew/)", unsafe_allow_html=True)
    st.sidebar.markdown("**Data Source:** [Capital Bikeshare System Data](https://capitalbikeshare.com/system-data)") 
    # 添加两张图片作为logo Add two images as logos
    col1, col2 = st.sidebar.columns(2)
    
    with col1:
        try:
            st.image("assets/WUT-Logo.png", caption="Wuhan University of Technology", use_container_width=True)
        except:
            st.markdown("**Wuhan University of Technology**")
    
    with col2:
        try:
            st.image("assets/EFREI-Logo.png", caption="eFrei Paris Panthéon-Assas Université", use_container_width=True)
        except:
            st.markdown("**eFrei Paris Panthéon-Assas Université**")
    
    # 页面路由 Page routing
    if page == "📊 Executive Summary":
        show_executive_summary(filtered_df, analysis_tables)
    elif page == "⏰ Time Analysis":
        show_time_analysis(filtered_df)
    elif page == "👥 User Behavior":
        show_user_behavior(filtered_df)
    elif page == "📍 Geographic Insights":
        show_geographic_insights(filtered_df)
    elif page == "🔍 Deep Dives":
        show_deep_dives(filtered_df)
    elif page == "📈 Conclusions":
        show_conclusions(filtered_df)

def show_executive_summary(df, tables):
    st.header("📊 Executive Summary")
    
    # KPI 指标 KPI Metrics
    st.subheader("Key Performance Indicators")
    create_kpi_metrics(df)
    
    # 介绍 Introduction
    st.markdown("""
    ### 🎯 Analysis Overview
    
    This dashboard explores Capital Bikeshare usage patterns to understand:
    - **When** are bikes most frequently used?
    - **Who** uses the service (members vs casual riders)?
    - **Where** are the most popular stations and routes?
    - **How** do riding patterns differ across user types?
    
    Understanding these patterns can help optimize bike distribution, marketing strategies, and service improvements.
    """)
    
    # 数据质量信息 Data Quality Information
    st.markdown("### 📋 Data Quality & Limitations")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        missing_stations = df['start_station_name'].isna().sum()
        st.metric("Missing Start Stations", f"{missing_stations:,}", 
                 f"{(missing_stations/len(df)*100):.1f}%")
    
    with col2:
        missing_end_stations = df['end_station_name'].isna().sum()
        st.metric("Missing End Stations", f"{missing_end_stations:,}", 
                 f"{(missing_end_stations/len(df)*100):.1f}%")
    
    with col3:
        st.metric("Total Records", f"{len(df):,}")
    
    st.info("""
    **Data Notes:** 
    - Some rides have missing station information (likely dockless electric bikes)
    - Ride duration calculations exclude extreme outliers
    - Geographic analysis uses available coordinate data
    """)

def show_time_analysis(df):
    st.header("⏰ Time-Based Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.plotly_chart(create_time_series_chart(df, 'hourly'), use_container_width=True)
        st.plotly_chart(create_time_series_chart(df, 'weekday'), use_container_width=True)
        st.plotly_chart(create_time_series_chart(df, 'monthly'), use_container_width=True)
    
    with col2:
        st.plotly_chart(create_time_series_chart(df, 'rolling_average'), use_container_width=True)
        st.plotly_chart(create_heatmap_analysis(df, 'hour_weekday'), use_container_width=True)
        st.plotly_chart(create_heatmap_analysis(df, 'member_casual_hourly'), use_container_width=True)
    
    # 洞察 Insights
    st.markdown("""
    ### 💡 Key Time-Based Insights
    
    **Peak Usage Patterns:**
    - **Members**: Show strong commute patterns with peaks at 8-9am and 5-6pm
    - **Casual Riders**: More weekend and evening usage, suggesting recreational use
    
    **Seasonal Trends:**
    - Higher usage on weekdays for members (work commutes)
    - Weekend peaks for casual riders (leisure activities)
    """)

def show_user_behavior(df):
    st.header("👥 User Behavior Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.plotly_chart(create_member_comparison_chart(df, 'ride_duration'), use_container_width=True)
        st.plotly_chart(create_member_comparison_chart(df, 'bike_type_preference'), use_container_width=True)
        st.plotly_chart(create_member_comparison_chart(df, 'usage_by_time'), use_container_width=True)
    
    with col2:
        st.plotly_chart(create_member_comparison_chart(df, 'distance_analysis'), use_container_width=True)
        st.plotly_chart(create_ride_duration_analysis(df, 'distribution'), use_container_width=True)
        st.plotly_chart(create_member_comparison_chart(df, 'default'), use_container_width=True) # User Type Distribution
    
    # 用户细分洞察 User Segmentation Insights
    st.markdown("""
    ### 🎯 User Segmentation Insights
    
    **Member Riders:**
    - Shorter, more frequent rides
    - Primarily use classic bikes for commuting
    - Consistent weekday usage patterns
    
    **Casual Riders:**
    - Longer, less frequent rides  
    - Prefer electric bikes for ease of use
    - More flexible, recreational usage patterns
    """)

def show_geographic_insights(df):
    st.header("📍 Geographic Insights")
    
    # 使用选项卡组织不同的地理可视化 Organize different geographic visualizations using tabs
    tab1, tab2, tab3 = st.tabs([
        "🗺️ Station Map", 
        "🔥 Heatmaps", 
        "📊 Station Analysis"
    ])
    
    with tab1:
        st.subheader("Ride Locations by Hour")
        map_chart = create_geographic_analysis(df, 'hourly_density')
        if map_chart:
            st.plotly_chart(map_chart, use_container_width=True)
        else:
            st.warning("Insufficient geographic data for mapping")
    
    with tab2:
        st.subheader("Usage Pattern Heatmaps")
        
        # 地理热力图 Geographic heatmaps
        st.plotly_chart(create_heatmap_analysis(df, 'station_popularity'), 
                      use_container_width=True)
        
    
    with tab3:
        st.subheader("Station Analysis")
        
        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(create_station_analysis_chart(df, 'popular_start_stations'), 
                          use_container_width=True)
        with col2:
            st.plotly_chart(create_station_analysis_chart(df, 'popular_end_stations'), 
                          use_container_width=True)
        
        st.plotly_chart(create_bubble_chart(df, 'station_activity'), 
                      use_container_width=True)
    
    # 地理洞察分析  Geographic Insights Analysis
    st.markdown("""
    ### 🗺️ Geographic Patterns & Insights
    
    **Station Activity Patterns:**
    - **Downtown Core**: High activity with balanced start/end patterns
    - **Tourist Areas**: More ride starts than ends, suggesting one-way tourist usage
    - **Residential Areas**: Higher member usage with consistent commute patterns
    
    **Usage Hotspots:**
    - Morning/evening peaks around business districts
    - Weekend hotspots in recreational areas
    - Consistent member usage in residential-to-downtown corridors
    """)

def show_deep_dives(df):
    st.header("🔍 Deep Dive Analysis")
    
    # 相关性分析 Correlation Analysis
    st.subheader("Ride Duration vs Distance Analysis")
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.plotly_chart(create_ride_duration_analysis(df, 'scatter'), use_container_width=True)
    
    with col2:
        st.metric("Avg Ride Duration", f"{df['ride_duration_minutes'].mean():.1f} min")
        st.metric("Median Duration", f"{df['ride_duration_minutes'].median():.1f} min")
        st.metric("Max Duration", f"{df['ride_duration_minutes'].max():.1f} min")
    
    # 高级分析 - 使用选项卡组织 Advanced Analysis - Organized with tabs
    
    st.subheader("📈Bubble Chart Analysis")
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(create_bubble_chart(df, 'duration_distance'), use_container_width=True)
    with col2:
        st.plotly_chart(create_bubble_chart(df, 'time_usage_pattern'), use_container_width=True)

def show_conclusions(df):
    st.header("📈 Conclusions & Recommendations")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.success("""
        ### ✅ Key Success Factors
        
        **Strong Member Base:**
        - Consistent commuter usage patterns
        - High frequency of short trips
        - Predictable demand patterns
        
        **Popular Service Areas:**
        - Well-utilized downtown stations
        - Good geographic coverage
        """)
    
    with col2:
        st.warning("""
        ### ⚠️ Improvement Opportunities
        
        **Casual Rider Engagement:**
        - Convert more casual users to members
        - Target marketing for weekend usage patterns
        
        **Station Optimization:**
        - Address station imbalance issues
        - Improve electric bike distribution
        """)
    
    # 建议 Recommendations
    st.markdown("""
    ### 🎯 Strategic Recommendations
    
    1. **Member Retention & Growth**
       - Develop loyalty programs for frequent casual riders
       - Target commuter-focused marketing campaigns
    
    2. **Operational Optimization** 
       - Redistribute bikes based on time and usage patterns
       - Increase electric bike availability in tourist areas
    
    3. **Service Expansion**
       - Identify underserved areas for new station placement
       - Develop partnerships with local businesses
    """)
    
    # 最终指标 Final Metrics
    st.subheader("📊 Final Performance Summary")
    
    metrics_cols = st.columns(4)
    with metrics_cols[0]:
        st.metric("Total Rides", f"{len(df):,}")
    with metrics_cols[1]:
        member_pct = (len(df[df['member_casual']=='member'])/len(df)*100)
        st.metric("Member Percentage", f"{member_pct:.1f}%")
    with metrics_cols[2]:
        avg_duration = df['ride_duration_minutes'].mean()
        st.metric("Average Duration", f"{avg_duration:.1f} min")
    with metrics_cols[3]:
        electric_pct = (len(df[df['rideable_type']=='electric_bike'])/len(df)*100)
        st.metric("Electric Bike Usage", f"{electric_pct:.1f}%")

if __name__ == "__main__":
    main()