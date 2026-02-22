import tkinter as tk
from tkinter import messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

def run():
    # --- Tkinter ablak ---
    window = tk.Tk()
    window.title("SIRD Modell")

    # --- Paraméterek és textboxok ---
    labels = [
        "S (Fogékony)", "I (Fertőzött)", "R (Felépült)", "D (Elhunyt)",
        "β (fertőzési ráta)", "γ (gyógyulási ráta)", "μ (halálozási ráta)",
        "Napok száma"
    ]
    entries = []

    for i, text in enumerate(labels):
        tk.Label(window, text=text).grid(row=i, column=0, padx=5, pady=5, sticky='e')
        entry = tk.Entry(window)
        entry.grid(row=i, column=1, padx=5, pady=5)
        entries.append(entry)

    # --- Matplotlib figura ---
    fig, ax = plt.subplots(figsize=(6,4))
    canvas = FigureCanvasTkAgg(fig, master=window)
    canvas.get_tk_widget().grid(row=0, column=2, rowspan=10, padx=10, pady=10)

    # -------------------- Funkciók --------------------
    def simulate_sird():
        try:
            S = float(entries[0].get())
            I = float(entries[1].get())
            R = float(entries[2].get())
            D = float(entries[3].get())
            beta = float(entries[4].get())
            gamma = float(entries[5].get())
            mu = float(entries[6].get())
            days_count = int(entries[7].get())

            N = max(S + I + R + D, 1)

            S_list = [S]
            I_list = [I]
            R_list = [R]
            D_list = [D]

            for _ in range(days_count):
                S_new = S - beta * S * I / N
                I_new = I + beta * S * I / N - gamma * I - mu * I
                R_new = R + gamma * I
                D_new = D + mu * I
                S, I, R, D = S_new, I_new, R_new, D_new
                S_list.append(S)
                I_list.append(I)
                R_list.append(R)
                D_list.append(D)

            # --- Grafikon ---
            ax.clear()
            ax.plot(S_list, label="S (Fogékony)", color='blue')
            ax.plot(I_list, label="I (Fertőzött)", color='red')
            ax.plot(R_list, label="R (Felépült)", color='green')
            ax.plot(D_list, label="D (Elhunyt)", color='black')
            ax.set_xlabel("Napok")
            ax.set_ylabel("Ember szám")
            ax.set_title("SIRD Modell")
            ax.legend()
            canvas.draw()

        except ValueError:
            messagebox.showerror("Hiba", "Kérlek, érvényes számokat adj meg minden mezőben!")

    def reset():
        for entry in entries:
            entry.delete(0, tk.END)
        ax.clear()
        canvas.draw()

    # --- Gombok ---
    tk.Button(window, text="Grafikon készítése", command=simulate_sird).grid(row=8, column=0, padx=5, pady=5)
    tk.Button(window, text="Reset", command=reset).grid(row=8, column=1, padx=5, pady=5)

    window.mainloop()
