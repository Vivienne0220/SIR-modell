import tkinter as tk
from tkinter import messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import pandas as pd
from scipy.optimize import least_squares


def run():
    window = tk.Tk()
    window.title("SIRD Modell")

    labels = [
        "S (Fogékony)", "I (Fertőzött)", "R (Felépült)", "D (Elhunyt)",
        "β (fertőzési ráta)", "γ (gyógyulási ráta)", "μ (halálozási ráta)",
        "Napok száma"
    ]
    entries = []

    for i, text in enumerate(labels):
        tk.Label(window, text=text).grid(row=i, column=0, sticky="e", padx=5, pady=5)
        e = tk.Entry(window)
        e.grid(row=i, column=1, padx=5, pady=5)
        entries.append(e)

    fig, ax = plt.subplots(figsize=(7, 5))
    canvas = FigureCanvasTkAgg(fig, master=window)
    canvas.get_tk_widget().grid(row=0, column=2, rowspan=12, padx=10, pady=10)

    def sird_step(S, I, R, D, beta, gamma, mu, N, dt):
        dS = -beta * S * I / N
        dI = beta * S * I / N - gamma * I - mu * I
        dR = gamma * I
        dD = mu * I

        S += dS * dt
        I += dI * dt
        R += dR * dt
        D += dD * dt

        return max(S, 0), max(I, 0), max(R, 0), max(D, 0)

    def simulate_sird():
        try:
            S = float(entries[0].get())
            I = float(entries[1].get())
            R = float(entries[2].get())
            D = float(entries[3].get())
            beta = float(entries[4].get())
            gamma = float(entries[5].get())
            mu = float(entries[6].get())
            days = int(entries[7].get())

            N = S + I + R + D

            S_list, I_list, R_list, D_list = [S], [I], [R], [D]

            for _ in range(days):
                S, I, R, D = sird_step(S, I, R, D, beta, gamma, mu, N, 1)
                S_list.append(S)
                I_list.append(I)
                R_list.append(R)
                D_list.append(D)

            ax.clear()
            ax.plot(S_list, label="S (Fogékony)")
            ax.plot(I_list, label="I (Fertőzött)")
            ax.plot(R_list, label="R (Felépült)")
            ax.plot(D_list, label="D (Elhunyt)")
            ax.set_xlabel("Napok")
            ax.set_ylabel("Ember szám")
            ax.set_title("SIRD Modell – Szimuláció")
            ax.legend()
            canvas.draw()

        except ValueError:
            messagebox.showerror("Hiba", "Minden mezőt tölts ki helyesen!")

    def fit_real_data():
        try:
            data = pd.read_csv("adatok.csv")

            days = data["nap"].values
            I_data = data["I"].values
            R_data = data["R"].values
            D_data = data["D"].values

            S0 = float(entries[0].get())
            I0, R0, D0 = I_data[0], R_data[0], D_data[0]
            N = S0 + I0 + R0 + D0

            def residuals(params):
                beta, gamma, mu = params
                S, I, R, D = S0, I0, R0, D0
                res = []

                for i in range(1, len(days)):
                    dt_total = days[i] - days[i - 1]
                    for _ in range(int(dt_total)):
                        S, I, R, D = sird_step(S, I, R, D, beta, gamma, mu, N, 1)
                    res.extend([I - I_data[i], R - R_data[i], D - D_data[i]])

                return res

            result = least_squares(residuals, x0=[0.3, 0.1, 0.02])
            beta, gamma, mu = result.x

            S, I, R, D = S0, I0, R0, D0
            I_fit, R_fit, D_fit = [I], [R], [D]

            for i in range(1, len(days)):
                dt_total = days[i] - days[i - 1]
                for _ in range(int(dt_total)):
                    S, I, R, D = sird_step(S, I, R, D, beta, gamma, mu, N, 1)
                I_fit.append(I)
                R_fit.append(R)
                D_fit.append(D)

            ax.clear()
            ax.scatter(days, I_data, label="Valós I")
            ax.scatter(days, R_data, label="Valós R")
            ax.scatter(days, D_data, label="Valós D")

            ax.plot(days, I_fit, "--", label="Illesztett I")
            ax.plot(days, R_fit, "--", label="Illesztett R")
            ax.plot(days, D_fit, "--", label="Illesztett D")

            ax.set_xlabel("Napok")
            ax.set_ylabel("Ember szám")
            ax.set_title("SIRD Modell – Illesztés")
            ax.legend()
            canvas.draw()

            messagebox.showinfo(
                "Illesztés kész",
                f"β={beta:.3f}\nγ={gamma:.3f}\nμ={mu:.3f}"
            )

        except Exception as e:
            messagebox.showerror("Hiba", str(e))

    def reset():
        for entry in entries:
            entry.delete(0, tk.END)
        ax.clear()
        canvas.draw()

    tk.Button(window, text="Grafikon készítése", command=simulate_sird)\
        .grid(row=8, column=0, pady=5)
    tk.Button(window, text="Illesztés valós adatokhoz", command=fit_real_data)\
        .grid(row=9, column=0, columnspan=2, pady=5)
    tk.Button(window, text="Reset", command=reset).grid(row=8, column=1, padx=5, pady=5)


    window.mainloop()


if __name__ == "__main__":
    run()
