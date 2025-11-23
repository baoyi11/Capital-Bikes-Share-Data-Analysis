# viz.py
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import streamlit as st
from plotly.subplots import make_subplots

def create_kpi_metrics(df):
    """创建关键绩效指标"""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_rides = len(df)
        st.metric("Total Rides", f"{total_rides:,}")
    
    with col2:
        member_rides = len(df[df['member_casual'] == 'member'])
        member_percentage = (member_rides / total_rides) * 100
        st.metric("Member Rides", f"{member_rides:,}", f"{member_percentage:.1f}%")
    
    with col3:
        avg_duration = df['ride_duration_minutes'].mean()
        st.metric("Avg Duration", f"{avg_duration:.1f} min")
    
    with col4:
        electric_bike_rides = len(df[df['rideable_type'] == 'electric_bike'])
        electric_percentage = (electric_bike_rides / total_rides) * 100
        st.metric("Electric Bike Rides", f"{electric_bike_rides:,}", f"{electric_percentage:.1f}%")

def create_time_series_chart(df, frequency='hourly'):
    """基于频率创建时间序列图表"""
    
    if frequency == 'hourly':
        data = df.groupby(['hour', 'member_casual']).size().reset_index(name='count')
        fig = px.line(data, x='hour', y='count', color='member_casual',
                     title='Hourly Usage Patterns',
                     labels={'hour': 'Hour of Day', 'count': 'Number of Rides'})
    
    elif frequency == 'daily':
        daily_data = df.groupby(['date', 'member_casual']).size().reset_index(name='count')
        fig = px.line(daily_data, x='date', y='count', color='member_casual',
                     title='Daily Usage Trends',
                     labels={'date': 'Date', 'count': 'Number of Rides'})
    
    elif frequency == 'weekday':
        weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        weekday_data = df.groupby(['day_of_week', 'member_casual']).size().reset_index(name='count')
        weekday_data['day_of_week'] = pd.Categorical(weekday_data['day_of_week'], categories=weekday_order, ordered=True)
        weekday_data = weekday_data.sort_values('day_of_week')
        
        fig = px.bar(weekday_data, x='day_of_week', y='count', color='member_casual',
                    title='Usage by Day of Week',
                    barmode='group',
                    labels={'day_of_week': 'Day of Week', 'count': 'Number of Rides'})
    
    elif frequency == 'monthly':
        monthly_data = df.groupby(['month', 'member_casual']).size().reset_index(name='count')
        fig = px.bar(monthly_data, x='month', y='count', color='member_casual',
                    title='Monthly Usage Distribution',
                    barmode='group',
                    labels={'month': 'Month', 'count': 'Number of Rides'})
    
    elif frequency == 'rolling_average':
        # 滚动平均图表
        daily_data = df.groupby(['date', 'member_casual']).size().reset_index(name='count')
        # 计算7天滚动平均
        daily_pivot = daily_data.pivot(index='date', columns='member_casual', values='count').fillna(0)
        rolling_avg = daily_pivot.rolling(window=7, min_periods=1).mean().reset_index()
        rolling_avg = pd.melt(rolling_avg, id_vars=['date'], value_name='count', var_name='member_casual')
        
        fig = px.line(rolling_avg, x='date', y='count', color='member_casual',
                     title='7-Day Rolling Average of Daily Rides',
                     labels={'date': 'Date', 'count': 'Number of Rides'})
    
    else:
        # 默认图表
        overall_data = df.groupby('member_casual').size().reset_index(name='count')
        fig = px.bar(overall_data, x='member_casual', y='count',
                    title='Overall Usage by User Type',
                    labels={'member_casual': 'User Type', 'count': 'Number of Rides'})
    
    fig.update_layout(showlegend=True, hovermode='x unified')
    return fig

def create_heatmap_analysis(df, heatmap_type='hour_weekday'):
    """创建热力图分析"""
    
    if heatmap_type == 'hour_weekday':
        # 小时-星期热力图
        df_heatmap = df.copy()
        # 确保星期顺序正确
        weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        df_heatmap['day_of_week'] = pd.Categorical(df_heatmap['day_of_week'], 
                                                 categories=weekday_order, ordered=True)
        
        # 创建交叉表：小时 vs 星期
        heatmap_data = pd.crosstab(df_heatmap['hour'], df_heatmap['day_of_week'])
        
        fig = px.imshow(heatmap_data,
                       title='Ride Frequency: Hour of Day vs Day of Week',
                       labels=dict(x="Day of Week", y="Hour of Day", color="Number of Rides"),
                       aspect="auto",
                       color_continuous_scale='Viridis')
        
        # 添加注释文本
        fig.update_traces(text=heatmap_data.values, texttemplate="%{text}")
        
    elif heatmap_type == 'member_casual_hourly':
        # 用户类型-小时热力图
        heatmap_data = df.groupby(['hour', 'member_casual']).size().unstack(fill_value=0)
        
        fig = px.imshow(heatmap_data.T,  # 转置以便更好的显示
                       title='Ride Frequency: User Type vs Hour of Day',
                       labels=dict(x="Hour of Day", y="User Type", color="Number of Rides"),
                       aspect="auto",
                       color_continuous_scale='Plasma')
        
        fig.update_traces(text=heatmap_data.T.values, texttemplate="%{text}")
    
    elif heatmap_type == 'station_popularity':
        # 站点热度热力图（基于地理坐标）
        station_usage = df.groupby(['start_station_name', 'start_lat', 'start_lng']).size().reset_index(name='count')
        station_usage = station_usage.dropna().nlargest(50, 'count')  # 取前50个最繁忙站点
        
        fig = px.density_mapbox(station_usage, 
                               lat='start_lat', 
                               lon='start_lng', 
                               z='count',
                               radius=20,
                               center=dict(lat=station_usage['start_lat'].mean(), 
                                         lon=station_usage['start_lng'].mean()),
                               zoom=10,
                               mapbox_style="open-street-map",
                               title='Station Usage Heatmap',
                               hover_data={'start_station_name': True, 'count': True})
        
        fig.update_layout(margin={"r":0,"t":30,"l":0,"b":0})
    
    else:
        # 默认热力图：月份-星期
        monthly_data = df.groupby(['month', 'day_of_week']).size().unstack(fill_value=0)
        fig = px.imshow(monthly_data,
                       title='Ride Frequency: Month vs Day of Week',
                       labels=dict(x="Day of Week", y="Month", color="Number of Rides"),
                       aspect="auto",
                       color_continuous_scale='Blues')
    
    return fig

def create_member_comparison_chart(df, chart_type='ride_duration'):
    """创建会员和临时用户的对比图表"""
    
    if chart_type == 'ride_duration':
        # 过滤极端值以便更好可视化
        temp_df = df[df['ride_duration_minutes'] <= 120]  # 限制在2小时内
        fig = px.box(temp_df, x='member_casual', y='ride_duration_minutes',
                    title='Ride Duration Distribution by User Type',
                    labels={'member_casual': 'User Type', 'ride_duration_minutes': 'Duration (minutes)'})
        fig.update_yaxes(range=[0, 120])
    
    elif chart_type == 'bike_type_preference':
        bike_type_data = df.groupby(['rideable_type', 'member_casual']).size().reset_index(name='count')
        fig = px.bar(bike_type_data, x='rideable_type', y='count', color='member_casual',
                    title='Bike Type Preference by User Type',
                    barmode='group',
                    labels={'rideable_type': 'Bike Type', 'count': 'Number of Rides'})
    
    elif chart_type == 'usage_by_time':
        time_data = df.groupby(['time_of_day', 'member_casual']).size().reset_index(name='count')
        # 确保时间顺序正确
        time_order = ['Early Morning (12-6am)', 'Morning (6-12pm)', 'Afternoon (12-6pm)', 'Evening (6-12am)']
        time_data['time_of_day'] = pd.Categorical(time_data['time_of_day'], categories=time_order, ordered=True)
        time_data = time_data.sort_values('time_of_day')
        
        fig = px.bar(time_data, x='time_of_day', y='count', color='member_casual',
                    title='Usage by Time of Day',
                    barmode='group',
                    labels={'time_of_day': 'Time of Day', 'count': 'Number of Rides'})
    
    elif chart_type == 'distance_analysis':
        # 距离分析图表
        # 过滤有效距离数据
        temp_df = df[(df['distance_km'] > 0) & (df['distance_km'] <= 10)]  # 限制在10公里内
        fig = px.box(temp_df, x='member_casual', y='distance_km',
                    title='Ride Distance Distribution by User Type',
                    labels={'member_casual': 'User Type', 'distance_km': 'Distance (km)'})
        fig.update_yaxes(range=[0, 10])
    
    else:
        # 默认图表，防止未定义的情况
        default_data = df['member_casual'].value_counts().reset_index()
        default_data.columns = ['member_casual', 'count']
        fig = px.pie(default_data, values='count', names='member_casual',
                    title='User Type Distribution')
    
    fig.update_layout(showlegend=True)
    return fig

def create_ride_duration_analysis(df, chart_type='distribution'):
    """分析骑行时长模式"""
    
    if chart_type == 'distribution':
        # 创建骑行时长直方图
        fig = px.histogram(df[df['ride_duration_minutes'] <= 120],  # 限制在2小时内以便清晰显示
                          x='ride_duration_minutes', 
                          color='member_casual',
                          title='Ride Duration Distribution',
                          labels={'ride_duration_minutes': 'Duration (minutes)'},
                          nbins=50,
                          opacity=0.7)
        fig.update_layout(barmode='overlay')
    
    elif chart_type == 'scatter':
        # 时长与近似距离的散点图
        scatter_df = df[(df['ride_duration_minutes'] <= 120) & (df['distance_km'] <= 10)].sample(n=1000)  # 采样以提高性能
        fig = px.scatter(scatter_df, x='distance_km', y='ride_duration_minutes', 
                        color='member_casual',
                        title='Ride Duration vs Distance',
                        labels={'distance_km': 'Distance (km)', 'ride_duration_minutes': 'Duration (minutes)'},
                        opacity=0.6)
    
    return fig

def create_station_analysis_chart(df, station_type='popular_start_stations'):
    """创建站点分析图表"""
    
    if station_type == 'popular_start_stations':
        station_data = df['start_station_name'].value_counts().head(10).reset_index()
        station_data.columns = ['station_name', 'count']
        fig = px.bar(station_data, x='count', y='station_name', orientation='h',
                    title='Top 10 Most Popular Start Stations',
                    labels={'count': 'Number of Rides', 'station_name': 'Station Name'})
    
    elif station_type == 'popular_end_stations':
        station_data = df['end_station_name'].value_counts().head(10).reset_index()
        station_data.columns = ['station_name', 'count']
        fig = px.bar(station_data, x='count', y='station_name', orientation='h',
                    title='Top 10 Most Popular End Stations',
                    labels={'count': 'Number of Rides', 'station_name': 'Station Name'})
    
    return fig

def create_bubble_chart(df, bubble_type='station_activity'):
    """创建气泡图分析"""
    
    if bubble_type == 'station_activity':
        # 站点活动气泡图：开始次数 vs 结束次数
        start_counts = df['start_station_name'].value_counts().reset_index()
        start_counts.columns = ['station_name', 'start_count']
        
        end_counts = df['end_station_name'].value_counts().reset_index()
        end_counts.columns = ['station_name', 'end_count']
        
        # 合并数据
        station_activity = pd.merge(start_counts, end_counts, on='station_name', how='outer').fillna(0)
        
        # 获取前30个最活跃站点
        station_activity['total_activity'] = station_activity['start_count'] + station_activity['end_count']
        station_activity = station_activity.nlargest(30, 'total_activity')
        
        # 计算净流量（开始-结束）
        station_activity['net_flow'] = station_activity['start_count'] - station_activity['end_count']
        
        fig = px.scatter(station_activity, 
                        x='start_count', 
                        y='end_count',
                        size='total_activity',
                        color='net_flow',
                        hover_name='station_name',
                        title='Station Activity Bubble Chart',
                        labels={
                            'start_count': 'Number of Rides Started',
                            'end_count': 'Number of Rides Ended',
                            'total_activity': 'Total Activity',
                            'net_flow': 'Net Flow (Start - End)'
                        },
                        color_continuous_scale='RdBu',
                        size_max=60)
        
        # 添加对角线参考线
        max_val = max(station_activity[['start_count', 'end_count']].max())
        fig.add_trace(go.Scatter(x=[0, max_val], y=[0, max_val], 
                               mode='lines', 
                               line=dict(dash='dash', color='gray'),
                               name='Balance Line',
                               showlegend=False))
        
        fig.update_layout(showlegend=True)
    
    elif bubble_type == 'duration_distance':
        # 时长-距离气泡图
        bubble_df = df[(df['ride_duration_minutes'] <= 120) & 
                      (df['distance_km'] <= 10)].copy()
        
        # 采样以避免过度绘制
        if len(bubble_df) > 1000:
            bubble_df = bubble_df.sample(n=1000, random_state=42)
        
        # 按用户类型分组计算平均速度和计数
        user_stats = bubble_df.groupby('member_casual').agg({
            'ride_duration_minutes': 'mean',
            'distance_km': 'mean',
            'ride_id': 'count'
        }).reset_index()
        user_stats.columns = ['member_casual', 'avg_duration', 'avg_distance', 'count']
        
        # 计算平均速度 (km/h)
        user_stats['avg_speed_kmh'] = (user_stats['avg_distance'] / 
                                     (user_stats['avg_duration'] / 60))
        
        fig = px.scatter(user_stats,
                        x='avg_distance',
                        y='avg_duration',
                        size='count',
                        color='member_casual',
                        hover_name='member_casual',
                        title='Average Ride Duration vs Distance by User Type',
                        labels={
                            'avg_distance': 'Average Distance (km)',
                            'avg_duration': 'Average Duration (minutes)',
                            'count': 'Number of Rides',
                            'member_casual': 'User Type'
                        },
                        size_max=40)
        
        # 添加速度注释
        for i, row in user_stats.iterrows():
            fig.add_annotation(x=row['avg_distance'], y=row['avg_duration'],
                             text=f"{row['avg_speed_kmh']:.1f} km/h",
                             showarrow=False,
                             yshift=10)
    
    elif bubble_type == 'time_usage_pattern':
        # 时间使用模式气泡图
        time_pattern = df.groupby(['hour', 'member_casual', 'rideable_type']).size().reset_index(name='count')
        
        # 取每个时段最常用的自行车类型
        time_pattern = time_pattern.loc[time_pattern.groupby(['hour', 'member_casual'])['count'].idxmax()]
        
        fig = px.scatter(time_pattern,
                        x='hour',
                        y='count',
                        size='count',
                        color='member_casual',
                        symbol='rideable_type',
                        title='Usage Patterns by Hour, User Type and Bike Type',
                        labels={
                            'hour': 'Hour of Day',
                            'count': 'Number of Rides',
                            'member_casual': 'User Type',
                            'rideable_type': 'Bike Type'
                        },
                        size_max=30)
        
        fig.update_xaxes(tickvals=list(range(0, 24)))
    
    return fig

def create_geographic_analysis(df, analysis_type='hourly_density'):
    """创建地理可视化 - 类似image.png的样式"""
    
    # 过滤掉缺失坐标的记录
    geo_df = df.dropna(subset=['start_lat', 'start_lng']).copy()
    
    if analysis_type == 'hourly_density':
        # 采样数据以避免过度绘制
        if len(geo_df) > 5000:
            geo_df = geo_df.sample(n=5000, random_state=42)
        
        # 创建类似image.png的散点图，按小时着色
        fig = px.scatter_mapbox(geo_df, 
                              lat='start_lat', 
                              lon='start_lng',
                              color='hour',
                              color_continuous_scale='viridis',
                              range_color=[0, 23],
                              title='Ride Locations Colored by Hour',
                              hover_data={
                                  'start_station_name': True,
                                  'hour': True,
                                  'member_casual': True,
                                  'rideable_type': True
                              },
                              mapbox_style="open-street-map",
                              zoom=10)
        
        fig.update_layout(
            margin={"r":0,"t":30,"l":0,"b":0},
            coloraxis_colorbar=dict(
                title="Hour of Day",
                tickvals=list(range(0, 24, 3)),
                ticktext=[f"{h}:00" for h in range(0, 24, 3)]
            )
        )
        
        return fig
    
    return None

def create_advanced_geographic_chart(df, chart_type='bubble_map'):
    """创建高级地理图表"""
    
    if chart_type == 'bubble_map':
        # 气泡地图：站点使用情况
        station_data = df.groupby(['start_station_name', 'start_lat', 'start_lng']).agg({
            'ride_id': 'count',
            'ride_duration_minutes': 'mean',
            'member_casual': lambda x: (x == 'member').mean()  # 会员比例
        }).reset_index()
        
        station_data.columns = ['station_name', 'lat', 'lng', 'ride_count', 'avg_duration', 'member_ratio']
        station_data = station_data.dropna().nlargest(100, 'ride_count')
        
        # 创建气泡地图
        fig = px.scatter_mapbox(station_data,
                              lat='lat',
                              lon='lng',
                              size='ride_count',
                              color='member_ratio',
                              hover_name='station_name',
                              hover_data={
                                  'ride_count': True,
                                  'avg_duration': ':.1f',
                                  'member_ratio': ':.2f',
                                  'lat': False,
                                  'lng': False
                              },
                              title='Station Usage Bubble Map',
                              mapbox_style="open-street-map",
                              color_continuous_scale='Viridis',
                              size_max=30,
                              zoom=10)
        
        fig.update_layout(margin={"r":0,"t":30,"l":0,"b":0},
                         coloraxis_colorbar=dict(title="Member Ratio"))
    
    elif chart_type == 'hexbin_map':
        # 六边形分箱地图（需要足够的数据点）
        hex_data = df[['start_lat', 'start_lng']].dropna()
        
        if len(hex_data) > 0:
            fig = px.density_mapbox(hex_data,
                                  lat='start_lat',
                                  lon='start_lng',
                                  radius=10,
                                  title='Ride Density Hexbin Map',
                                  mapbox_style="open-street-map",
                                  zoom=10)
            
            fig.update_layout(margin={"r":0,"t":30,"l":0,"b":0})
        else:
            # 如果没有足够数据，返回空图表
            fig = go.Figure()
            fig.update_layout(title="Insufficient data for hexbin map")
    
    return fig