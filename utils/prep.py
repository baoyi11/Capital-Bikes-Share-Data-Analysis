import pandas as pd
import numpy as np
from datetime import datetime

def prepare_data(df):
    """Clean and prepare the dataset for analysis"""
    df_clean = df.copy()
    
    # 转换日期时间列 Convert date and time column
    df_clean['started_at'] = pd.to_datetime(df_clean['started_at'])
    df_clean['ended_at'] = pd.to_datetime(df_clean['ended_at'])
    
    # 计算骑行时长（分钟）Calculate cycling time (minutes)
    df_clean['ride_duration_minutes'] = (df_clean['ended_at'] - df_clean['started_at']).dt.total_seconds() / 60
    
    # 移除不合理的时长（太短或太长）Remove unreasonable durations (too short or too long)
    df_clean = df_clean[(df_clean['ride_duration_minutes'] >= 1) & (df_clean['ride_duration_minutes'] <= 24*60)]
    
    # 提取时间特征 Extracting time features
    df_clean['hour'] = df_clean['started_at'].dt.hour
    df_clean['day_of_week'] = df_clean['started_at'].dt.day_name()
    df_clean['date'] = df_clean['started_at'].dt.date
    df_clean['month'] = df_clean['started_at'].dt.month
    df_clean['weekend'] = df_clean['started_at'].dt.dayofweek >= 5
    
    # 创建时间段分类 Create time period categories
    conditions = [
        (df_clean['hour'] < 6),
        (df_clean['hour'] < 12),
        (df_clean['hour'] < 18),
        (df_clean['hour'] <= 23)
    ]
    choices = ['Early Morning (12-6am)', 'Morning (6-12pm)', 'Afternoon (12-6pm)', 'Evening (6-12am)']
    df_clean['time_of_day'] = np.select(conditions, choices, default='Unknown')
    
    # 计算近似距离 Calculate approximate distance
    df_clean['distance_km'] = calculate_approximate_distance(df_clean)
    
    return df_clean

def calculate_approximate_distance(df):
    """Calculate approximate distance between start and end coordinates"""
    # 检查必要的列是否存在且没有缺失值 Check that the necessary columns exist and that there are no missing values.
    required_cols = ['start_lat', 'start_lng', 'end_lat', 'end_lng']
    if not all(col in df.columns for col in required_cols):
        return np.zeros(len(df))
    
    # 处理缺失值 Handle missing values
    mask = df[required_cols].notna().all(axis=1)
    distances = np.zeros(len(df))
    
    if mask.any():
        R = 6371  # 地球半径（公里） Earth radius (km)
        
        lat1 = np.radians(df.loc[mask, 'start_lat'])
        lon1 = np.radians(df.loc[mask, 'start_lng'])
        lat2 = np.radians(df.loc[mask, 'end_lat'])
        lon2 = np.radians(df.loc[mask, 'end_lng'])
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
        c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))
        
        distances[mask] = R * c
    
    return distances

def create_analysis_tables(df):
    """Create aggregated tables for different analyses"""
    tables = {}
    
    # 基于时间的聚合 Time-based aggregations
    tables['hourly_usage'] = df.groupby(['hour', 'member_casual']).size().unstack(fill_value=0)
    tables['daily_usage'] = df.groupby(['date', 'member_casual']).size().unstack(fill_value=0)
    tables['weekday_usage'] = df.groupby(['day_of_week', 'member_casual']).size().unstack(fill_value=0)
    
    # 站点分析 Station analysis
    start_station_counts = df['start_station_name'].value_counts().head(20)
    end_station_counts = df['end_station_name'].value_counts().head(20)
    tables['popular_stations'] = pd.DataFrame({
        'start_stations': start_station_counts,
        'end_stations': end_station_counts
    })
    
    # 自行车类型分析 Bike type analysis
    tables['bike_type_usage'] = df.groupby(['rideable_type', 'member_casual']).size().unstack(fill_value=0)
    
    # 时长分析 Duration analysis
    tables['duration_stats'] = df.groupby('member_casual')['ride_duration_minutes'].describe()
    
    return tables