import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

# --- 美赛学术风格全局配置 ---
# 设置绘图风格为 Seaborn 的 "whitegrid" (白底带网格，清晰干净)
sns.set_theme(style="whitegrid")

# 设置全局字体（推荐 Times New Roman 或 Arial，需要系统安装）
# 如果没有安装，可以用 'sans-serif' 代替
plt.rcParams['font.family'] = 'Times New Roman' 
# 解决负号显示问题
plt.rcParams['axes.unicode_minus'] = False 

# 设置字体大小，确保在文章中清晰可读
plt.rcParams['font.size'] = 12
plt.rcParams['axes.labelsize'] = 14
plt.rcParams['axes.titlesize'] = 16
plt.rcParams['xtick.labelsize'] = 12
plt.rcParams['ytick.labelsize'] = 12
plt.rcParams['legend.fontsize'] = 12

# 设置分辨率 (非常重要！)
plt.rcParams['figure.dpi'] = 300

print("学术绘图风格配置完成！")
# --- 模拟数据生成 (比赛时替换为你的真实数据) ---
# 假设我们要对比两种策略下某指标随时间的变化
time = np.arange(0, 50)
# 策略 A 数据 (带随机噪声)
strategy_a = np.sin(time / 5) + np.random.normal(0, 0.2, 50) + 2
# 策略 B 数据
strategy_b = np.cos(time / 5) + np.random.normal(0, 0.2, 50) + 2.5

# 构建 DataFrame (Seaborn 喜欢长格式数据)
df_a = pd.DataFrame({'Time (Days)': time, 'Value': strategy_a, 'Strategy': 'Strategy A'})
df_b = pd.DataFrame({'Time (Days)': time, 'Value': strategy_b, 'Strategy': 'Strategy B'})
df_plot = pd.concat([df_a, df_b])


# --- 开始绘图 ---
plt.figure(figsize=(12, 7))
plt.title("Comparison of Strategy Performance Over Time", 
          pad=30, # 增加标题到顶部的距离
          fontweight='bold', fontsize=18)

plt.xlabel("Time (Days)", fontweight='bold', labelpad=15) # 增加 x 轴标签间距
plt.ylabel("Performance Index (Normalized)", fontweight='bold', labelpad=15) # 增加 y 轴标签间距
# 使用 sns.lineplot 绘制
# 它会自动计算均值并绘制阴影区域代表置信区间 (默认 95% CI)
# hue='Strategy': 根据策略自动区分颜色和图例
# style='Strategy': 根据策略自动区分线型 (实线/虚线)，增强黑白打印时的可读性
sns.lineplot(data=df_plot, x='Time (Days)', y='Value', hue='Strategy', style='Strategy', 
             palette="deep", linewidth=2.5)

# --- 调整美化 ---
plt.title("Comparison of Strategy Performance Over Time", pad=20, fontweight='bold')
plt.xlabel("Time (Days)", fontweight='bold')
plt.ylabel("Performance Index (Normalized)", fontweight='bold')
# 核心：使用 tight_layout 的同时增加边界填充
plt.tight_layout(pad=3.0)
# 优化图例位置和样式
plt.legend(title='Strategy Type', title_fontsize='13', loc='best', frameon=True, shadow=True)
plt.grid(True, which='major', linestyle='--', linewidth=0.7)

plt.tight_layout()
plt.subplots_adjust(left=0.15, right=0.95, top=0.85, bottom=0.15)
plt.savefig("final_plot.pdf", #保存pdf文件
            dpi=300, 
            bbox_inches='tight',
            facecolor='white'
            )
plt.show()