import tkinter as tk
from tkinter import messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.ticker import StrMethodFormatter
import numpy as np
import pandas as pd
from scipy.optimize import least_squares

plt.style.use("seaborn-v0_8-whitegrid")

sird_window = None

def run():
    global sird_window

    if sird_window is not None and sird_window.winfo_exists():
        sird_window.lift()
        return

    window = tk.Toplevel()
    sird_window = window
    window.title("SIRD járványmodell")
    window.geometry("1100x520")

    labels = [
        "S (Fogékony) [fő]",
        "I (Fertőzött) [fő]",
        "R (Felépült) [fő]",
        "D (Elhunyt) [fő]",
        "β fertőzési ráta [0–1]",
        "γ gyógyulási ráta [0–1]",
        "μ halálozási ráta [0–1]",
        "Napok száma"
    ]

    default_values = [9900, 100, 0, 0, 0.3, 0.1, 0.02, 160]

    entries = []

    for i, text in enumerate(labels):
        tk.Label(window, text=text, font=("Segoe UI", 10)).grid(
            row=i, column=0, padx=10, pady=5, sticky="e"
        )

        e = tk.Entry(window, font=("Segoe UI", 10))
        e.grid(row=i, column=1, padx=10, pady=5)

        e.insert(0, str(default_values[i]))
        entries.append(e)

    fig, ax = plt.subplots(figsize=(7, 4))

    canvas = FigureCanvasTkAgg(fig, master=window)
    canvas.get_tk_widget().grid(row=0, column=2, rowspan=12, padx=20, pady=20)


    def sird_step(S, I, R, D, beta, gamma, mu, N):

        dS = -beta * S * I / N
        dI = beta * S * I / N - gamma * I - mu * I
        dR = gamma * I
        dD = mu * I

        S += dS
        I += dI
        R += dR
        D += dD

        return max(S, 0), max(I, 0), max(R, 0), max(D, 0)

    def simulate():
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

            S_list = [S]
            I_list = [I]
            R_list = [R]
            D_list = [D]

            for _ in range(days):
                S, I, R, D = sird_step(S, I, R, D, beta, gamma, mu, N)

                S_list.append(S)
                I_list.append(I)
                R_list.append(R)
                D_list.append(D)

            ax.clear()

            ax.plot(S_list, label="Fogékony", color="tab:blue", linewidth=2)
            ax.plot(I_list, label="Fertőzött", color="tab:red", linewidth=2)
            ax.plot(R_list, label="Felépült", color="tab:green", linewidth=2)
            ax.plot(D_list, label="Elhunyt", color="black", linewidth=2)

            ax.set_title("SIRD járványdinamika")
            ax.set_xlabel("Napok")
            ax.set_ylabel("Egyének száma")

            ax.legend(frameon=False)
            ax.grid(alpha=0.3)

            ax.yaxis.set_major_formatter(StrMethodFormatter('{x:,.0f}'))

            fig.tight_layout(pad=2)

            canvas.draw()

        except ValueError:
            messagebox.showerror(
                "Hiba",
                "Kérlek minden mezőbe érvényes számot adj meg."
            )

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
                    dt = days[i] - days[i - 1]

                    for _ in range(int(dt)):
                        S, I, R, D = sird_step(S, I, R, D, beta, gamma, mu, N)

                    res.extend([I - I_data[i], R - R_data[i], D - D_data[i]])
                return res

            result = least_squares(residuals, x0=[0.3, 0.1, 0.02])

            beta, gamma, mu = result.x

            S, I, R, D = S0, I0, R0, D0

            I_fit = [I]
            R_fit = [R]
            D_fit = [D]

            for i in range(1, len(days)):
                dt = days[i] - days[i - 1]

                for _ in range(int(dt)):
                    S, I, R, D = sird_step(S, I, R, D, beta, gamma, mu, N)

                I_fit.append(I)
                R_fit.append(R)
                D_fit.append(D)

            ax.clear()

            ax.scatter(days, I_data, label="Valós fertőzött", color="red")
            ax.scatter(days, R_data, label="Valós felépült", color="green")
            ax.scatter(days, D_data, label="Valós elhunyt", color="black")

            ax.plot(days, I_fit, "--", label="Illesztett I", color="red")
            ax.plot(days, R_fit, "--", label="Illesztett R", color="green")
            ax.plot(days, D_fit, "--", label="Illesztett D", color="black")

            ax.set_title("SIRD modell illesztése valós adatokhoz")
            ax.set_xlabel("Napok")
            ax.set_ylabel("Egyének száma")

            ax.legend()
            ax.grid(alpha=0.3)

            canvas.draw()

            messagebox.showinfo(
                "Illesztés kész",
                f"β = {beta:.3f}\nγ = {gamma:.3f}\nμ = {mu:.3f}"
            )

        except Exception as e:
            messagebox.showerror("Hiba", str(e))

    def reset():
        for i, entry in enumerate(entries):
            entry.delete(0, tk.END)
            entry.insert(0, str(default_values[i]))

        ax.clear()
        canvas.draw()

    tk.Button(
        window,
        text="Grafikon készítése",
        command=simulate,
        width=20
    ).grid(row=8, column=0, pady=10)

    tk.Button(
        window,
        text="Illesztés valós adatokhoz",
        command=fit_real_data,
        width=20
    ).grid(row=9, column=0)

    tk.Button(
        window,
        text="Alaphelyzet",
        command=reset,
        width=20
    ).grid(row=8, column=1)
