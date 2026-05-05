import numpy as np
import matplotlib.pyplot as plt

#T = np.array([49.2,48.5,47.7,47.0,46.3,45.6,45.0,44.3])
T = np.array([48.9,48.2,47.4,46.7,46.0,45.3,44.7,44.1])
t = np.array([30,60,90,120,150,180,210,240])

k, b = np.polyfit(t, T, deg=1)
print(f"k = {k:.4f}, b = {b:.4f}")

T_pred = k * t + b
SS_res = np.sum((T - T_pred) ** 2)
SS_tot = np.sum((T - np.mean(T)) ** 2)
R2 = 1 - SS_res / SS_tot
print(f"R² = {R2:.4f}")

plt.figure(figsize=(6, 4))
plt.scatter(t, T, label='Origin Data', color='royalblue')
plt.plot(t, T_pred, color='orangered', label=f'Fitted Line: t={k:.2f}T+{b:.2f}')
plt.xlabel('T')
plt.ylabel('t')
plt.title('Fitting Result')
plt.legend()
plt.grid(alpha=0.3)
plt.tight_layout()
plt.show()