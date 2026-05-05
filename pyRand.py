import os
import sys

stderr = sys.stderr
sys.stderr = open(os.devnull, "w")

import matplotlib.pyplot as plt
import numpy as np
from rich.progress import track


def getNextRand(n):
    a, c, m = 1664525, 1013904223, 4294967296
    return (a * n + c) % m


def main():
    MAX = int(input("Enter MAX:"))
    T_list = []
    t_list = []

    current_val = 12345

    for i in track(range(MAX), description="Running Recursive LCG..."):
        current_val = getNextRand(current_val)

        T_list.append(current_val)
        t_list.append(i)

    T = np.array(T_list)
    t = np.array(t_list)

    k, b = np.polyfit(t, T, deg=1)
    print(f"k = {k:.4f}, b = {b:.4f}")

    T_pred = k * t + b
    SS_res = np.sum((T - T_pred) ** 2)
    SS_tot = np.sum((T - np.mean(T)) ** 2)
    R2 = 1 - SS_res / SS_tot
    print(f"R² = {R2:.4f}")
    plt.figure(figsize=(6, 4))
    plt.scatter(t, T, label="Origin Data", color="royalblue")
    plt.plot(t, T_pred, color="orangered", label=f"Fitted Line: t={k:.2f}T+{b:.2f}")
    plt.xlabel("T")
    plt.ylabel("t")
    plt.title("Fitting Result")
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.show()
    input("")


if __name__ == "__main__":
    main()
