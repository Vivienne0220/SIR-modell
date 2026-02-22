import tkinter as tk
from tkinter import messagebox, ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
from matplotlib.ticker import StrMethodFormatter


# ---------- KÖZÖS GRAFIKON ABLAK ----------
def open_country_window(country):

    win = tk.Toplevel()
    win.title(f"{country} – SEIRDVH elemzés")
    win.geometry("1000x600")

    fig, ax = plt.subplots(figsize=(6, 4))
    canvas = FigureCanvasTkAgg(fig, master=win)
    canvas.get_tk_widget().pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    data_holder = {"data": None}

    # ---------- CSV BETÖLTÉS ----------

    # ---------- RESET ----------
    def reset():
        ax.clear()
        canvas.draw()
        data_holder["data"] = None

    # ---------- KIMUTATÁS ----------
    def plot_data():
        if country == "Szlovákia":
                file = "covid_sk.csv"
        elif country == "Magyarország":
                file = "covid_hu.csv"
        else:
                messagebox.showerror("Hiba", "Ismeretlen ország")
                return

        df = pd.read_csv(file, parse_dates=["date"])
        df = df.sort_values("date")
        data_holder["data"] = df

        df = data_holder["data"]
        if df is None:
            messagebox.showerror("Hiba", "Előbb töltsd be az adatokat!")
            return

        ax.clear()
        x = df["date"]

        # Színek a szlovák stílus szerint
        colors = {
            "newcases": "blue",       # Fertőzött (I)
            "recovered": "orange",    # Gyógyult (R)
            "death": "green",         # Halott (D)
            "hospital": "red",        # Kórház (H)
            "vaccines": "purple"      # Oltott (V)
        }

        linestyles = {
            "newcases": "-", 
            "recovered": "-", 
            "death": "-", 
            "hospital": "-", 
            "vaccines": "-"
        }

        # Mindkét országra ugyanaz a stílus, de Magyarország adatainál
        ax.plot(x, df["newcases"], label="Fertőzött (I)", color=colors["newcases"], linestyle=linestyles["newcases"])
        ax.plot(x, df["recovered"], label="Gyógyult (R)", color=colors["recovered"], linestyle=linestyles["recovered"])
        ax.plot(x, df["death"], label="Halott (D)", color=colors["death"], linestyle=linestyles["death"])
        ax.plot(x, df["hospital"], label="Kórház (H)", color=colors["hospital"], linestyle=linestyles["hospital"])
        ax.plot(x, df["vaccines"], label="Oltott (V)", color=colors["vaccines"], linestyle=linestyles["vaccines"])

        ax.set_ylabel("Esetek száma")
        ax.ticklabel_format(style='plain', axis='y')
        ax.yaxis.set_major_formatter(StrMethodFormatter('{x:,.0f}'))

        ax.set_title(f"Valós adatok időben – {country}")
        ax.legend()
        fig.autofmt_xdate()
        canvas.draw()

    # ---------- PANEL ----------
    panel = tk.Frame(win)
    panel.pack(side=tk.LEFT, fill=tk.Y, padx=60, pady=10)

    tk.Button(panel, text="Kimutatás", command=plot_data, width=20).pack(pady=5)
    tk.Button(panel, text="Reset", command=reset, width=20, bg="lightcoral").pack(pady=20)


# ---------- FŐ ABLAK ----------
def run():
    root = tk.Tk()
    root.title("SEIRDVH model")
    root.geometry("350x200")

    options = ["Magyarország", "Szlovákia"]
    selected = tk.StringVar(value=options[0])

    ttk.Label(root, text="Válassz országot:").pack(pady=10)

    dropdown = ttk.Combobox(
        root,
        textvariable=selected,
        values=options,
        state="readonly"

    )
    dropdown.pack(pady=10)

    def go():
        open_country_window(selected.get())

    tk.Button(root, text="OK", command=go, width=20).pack(pady=10)

    root.mainloop()


if __name__ == "__main__":
    run()
