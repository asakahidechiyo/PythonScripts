import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler, MinMaxScaler

def quick_inspect(df):
    """1. 快速检查数据概况"""
    print("--- 基础信息 ---")
    print(df.info())
    print("\n--- 缺失值统计 ---")
    print(df.isnull().sum()[df.isnull().sum() > 0])
    print("\n--- 数值型变量统计 ---")
    print(df.describe())

def handle_missing_data(df, strategy='mean'):
    """2. 缺失值处理策略"""
    # strategy: 'mean', 'median', 'mode', or 'drop'
    df_clean = df.copy()
    if strategy == 'drop':
        df_clean = df_clean.dropna()
    else:
        for col in df_clean.select_dtypes(include=[np.number]).columns:
            if strategy == 'mean':
                df_clean[col] = df_clean[col].fillna(df_clean[col].mean())
            elif strategy == 'median':
                df_clean[col] = df_clean[col].fillna(df_clean[col].median())
    return df_clean

def detect_outliers_iqr(df, column):
    """3. 异常值检测 (IQR法则)"""
    Q1 = df[column].quantile(0.25)
    Q3 = df[column].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    
    outliers = df[(df[column] < lower_bound) | (df[column] > upper_bound)]
    print(f"变量 {column} 中的异常值数量: {len(outliers)}")
    return lower_bound, upper_bound

def convert_time_series(df, time_col):
    """4. 时间格式统一化 (C题必备)"""
    df[time_col] = pd.to_datetime(df[time_col])
    df = df.sort_values(by=time_col)
    # 提取特征：年份、月份、周几
    df['Year'] = df[time_col].dt.year
    df['Month'] = df[time_col].dt.month
    df['DayOfWeek'] = df[time_col].dt.dayofweek
    return df

# ================= 使用示例 (比赛开始后按此流程操作) =================

# 第一步：加载数据 (修改为实际文件名)
# df = pd.read_csv('data.csv') 

# 第二步：初步观察
# quick_inspect(df)

# 第三步：处理缺失值
# df = handle_missing_data(df, strategy='median')

# 第四步：特征缩放 (如果要做回归、聚类或神经网络，这一步必做)
# scaler = StandardScaler() # 或者 MinMaxScaler()
# columns_to_scale = ['feature1', 'feature2']
# df[columns_to_scale] = scaler.fit_transform(df[columns_to_scale])

# 第五步：保存清洗后的数据，供建模使用
# df.to_csv('cleaned_data.csv', index=False)