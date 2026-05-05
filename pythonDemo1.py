import numpy as np
import matplotlib.pyplot as plt

# Data Preparation
T = np.array([48.9, 48.2, 47.4, 46.7, 46.0, 45.3, 44.7, 44.1])
t = np.array([30, 60, 90, 120, 150, 180, 210, 240])

# Fitting
k, b = np.polyfit(t, T, deg=1)
T_pred = k * t + b

# Statistics
SS_res = np.sum((T - T_pred) ** 2)
SS_tot = np.sum((T - np.mean(T)) ** 2)
R2 = 1 - SS_res / SS_tot

# Visualization (MCM Style)
plt.figure(figsize=(8, 5), dpi=120) # 提高分辨率以适应论文
plt.scatter(t, T, label='Observed Data', color='#1f77b4', s=50, zorder=5) # 学术蓝
plt.plot(t, T_pred, color='#d62728', linewidth=2, linestyle='--',
         label=f'Linear Fit: $T = {k:.4f}t + {b:.2f}$\n$R^2 = {R2:.4f}$') # 使用 LaTeX 格式图例

# Corrected Labels
plt.xlabel('Time $t$ (s)', fontsize=12) # 加上单位
plt.ylabel('Temperature $T$ ($^{\circ}$C)', fontsize=12)
plt.title('Time-Temperature Linear Regression Analysis', fontsize=14)

plt.legend(frameon=True, fancybox=True, shadow=True)
plt.grid(alpha=0.4, linestyle=':')
plt.tight_layout()
plt.show()

# Print text result for LaTeX table
print(f"Model: T = {k:.4f}t + {b:.4f}")
print(f"R-squared: {R2:.4f}")