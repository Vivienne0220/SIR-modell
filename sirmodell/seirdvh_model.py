import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.ticker import StrMethodFormatter
import matplotlib.dates as mdates
from matplotlib.patches import Patch
import pandas as pd

plt.style.use("seaborn-v0_8-whitegrid")

window_ref = None

def run():
    global window_ref

    if window_ref is not None and window_ref.winfo_exists():
        window_ref.lift()
        return

    root = tk.Toplevel()
    window_ref = root

    root.title("COVID epidemiológiai kimutatás")
    root.geometry("1120x680")

    def on_close():
        global window_ref
        window_ref = None
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_close)

    main = tk.Frame(root)
    main.pack(fill=tk.BOTH, expand=True)

    left = tk.Frame(main)
    left.pack(side=tk.LEFT, fill=tk.Y, padx=20, pady=20)

    right = tk.Frame(main)
    right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    options = ["Magyarország", "Szlovákia"]
    selected = tk.StringVar(value=options[0])

    ttk.Label(left, text="Ország", font=("Segoe UI", 11)).pack(pady=10)

    box = ttk.Combobox(
        left,
        textvariable=selected,
        values=options,
        state="readonly",
        width=20
    )
    box.pack()

    legend_info = tk.Label(
        left,
        text=(
            "Háttérjelölések:\n"
            "Szürke = kezdeti időszak\n"
            "Narancs = lockdown időszak\n"
            "Zöld = oltási időszak"
        ),
        justify="left",
        font=("Segoe UI", 9)
    )
    legend_info.pack(pady=18, anchor="w")

    fig, axs = plt.subplots(2, 2, figsize=(9.2, 6.2))
    canvas = FigureCanvasTkAgg(fig, master=right)
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    bg_handles = [
        Patch(facecolor="lightgray", edgecolor="none", alpha=0.25, label="Kezdeti időszak"),
        Patch(facecolor="orange", edgecolor="none", alpha=0.25, label="Lockdown időszak"),
        Patch(facecolor="green", edgecolor="none", alpha=0.20, label="Oltási időszak")
    ]

    HU_CUMULATIVE_COLS = {"newcases", "recovered", "vaccines"}

    def load_country(country):
        if country == "Magyarország":
            file = "covid_hu.csv"
            lockdown = "2020-03-28"
            vaccine = "2021-01-01"
            cumulative_cols = HU_CUMULATIVE_COLS
        else:
            file = "covid_sk.csv"
            lockdown = "2020-03-16"
            vaccine = "2021-01-06"
            cumulative_cols = set()

        df = pd.read_csv(file, parse_dates=["date"]).sort_values("date").copy()
        return df, lockdown, vaccine, cumulative_cols

    def numeric(series):
        return pd.to_numeric(series, errors="coerce").fillna(0).clip(lower=0)

    def get_level_series(df, col):
        return numeric(df[col])

    def get_daily_series(df, col, cumulative_cols):
        s = numeric(df[col])
        if col in cumulative_cols:
            return s.diff().fillna(0).clip(lower=0)
        return s

    def format_axes():
        for ax in axs.flat:
            ax.grid(alpha=0.3)
            ax.set_xlabel("Dátum")
            ax.xaxis.set_major_locator(mdates.MonthLocator(interval=4))
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
            ax.tick_params(axis="x", rotation=25)
            ax.yaxis.set_major_formatter(StrMethodFormatter('{x:,.0f}'))

    def add_period_backgrounds_single(x, lockdown, vaccine):
        lock = pd.to_datetime(lockdown)
        vac = pd.to_datetime(vaccine)
        start = x.min()
        end = x.max()

        for ax in axs.flat:
            if start < lock:
                ax.axvspan(start, lock, color="lightgray", alpha=0.08)

            if lock < vac:
                ax.axvspan(lock, vac, color="orange", alpha=0.12)

            if vac < end:
                ax.axvspan(vac, end, color="green", alpha=0.10)

            ax.axvline(lock, linestyle="--", color="darkorange", linewidth=1.1, alpha=0.7)
            ax.axvline(vac, linestyle="--", color="darkgreen", linewidth=1.1, alpha=0.7)

    def add_period_backgrounds_compare(hu_x, hu_lockdown, hu_vaccine, sk_lockdown, sk_vaccine):
        start = hu_x.min()
        end = hu_x.max()

        hu_lock = pd.to_datetime(hu_lockdown)
        hu_vac = pd.to_datetime(hu_vaccine)
        sk_lock = pd.to_datetime(sk_lockdown)
        sk_vac = pd.to_datetime(sk_vaccine)

        lock_start = min(hu_lock, sk_lock)
        vac_start = min(hu_vac, sk_vac)

        for ax in axs.flat:
            if start < lock_start:
                ax.axvspan(start, lock_start, color="lightgray", alpha=0.08)

            if lock_start < vac_start:
                ax.axvspan(lock_start, vac_start, color="orange", alpha=0.12)

            if vac_start < end:
                ax.axvspan(vac_start, end, color="green", alpha=0.10)

            ax.axvline(hu_lock, linestyle="--", color="tab:red", linewidth=1.0, alpha=0.55)
            ax.axvline(sk_lock, linestyle="--", color="tab:blue", linewidth=1.0, alpha=0.55)

            ax.axvline(hu_vac, linestyle=":", color="tab:red", linewidth=1.0, alpha=0.55)
            ax.axvline(sk_vac, linestyle=":", color="tab:blue", linewidth=1.0, alpha=0.55)

    def add_background_legend():
        for old_legend in fig.legends:
            old_legend.remove()

        fig.legend(
            handles=bg_handles,
            loc="upper center",
            ncol=3,
            frameon=False,
            bbox_to_anchor=(0.63, 0.99),
            fontsize=9
        )

    def plot():
        try:
            df, lockdown, vaccine, cumulative_cols = load_country(selected.get())
            x = df["date"]

            for ax in axs.flat:
                ax.clear()

            infections = get_daily_series(df, "newcases", cumulative_cols)
            deaths = get_level_series(df, "death")
            recovered = get_daily_series(df, "recovered", cumulative_cols)
            hospital = get_level_series(df, "hospital")
            vaccines = get_daily_series(df, "vaccines", cumulative_cols)

            axs[0, 0].plot(
                x,
                infections,
                color="tab:red",
                linewidth=2
            )
            axs[0, 0].set_title("Új fertőzések")
            axs[0, 0].set_ylim(0, infections.max() * 1.2 if infections.max() > 0 else 1)

            axs[0, 1].plot(
                x,
                deaths,
                color="black",
                linewidth=2
            )
            axs[0, 1].set_title("Halálozás")

            axs[1, 0].plot(
                x,
                recovered,
                color="tab:green",
                linewidth=2
            )
            axs[1, 0].set_title("Új gyógyult esetek")

            axs[1, 1].plot(
                x,
                hospital.rolling(7, min_periods=1).mean(),
                color="tab:orange",
                linewidth=2,
                label="Kórház"
            )
            axs[1, 1].plot(
                x,
                vaccines.rolling(7, min_periods=1).mean(),
                color="purple",
                linewidth=2,
                label="Oltás"
            )
            axs[1, 1].set_title("Kórház / Napi oltás")
            axs[1, 1].legend(frameon=False)

            format_axes()
            add_period_backgrounds_single(x, lockdown, vaccine)
            add_background_legend()

            fig.tight_layout(pad=2, rect=[0, 0, 1, 0.95])
            canvas.draw()

        except Exception as e:
            messagebox.showerror("Hiba", str(e))

    def compare():
        try:
            hu, hu_lockdown, hu_vaccine, hu_cum = load_country("Magyarország")
            sk, sk_lockdown, sk_vaccine, sk_cum = load_country("Szlovákia")

            pop_hu = 9600000
            pop_sk = 5450000

            for ax in axs.flat:
                ax.clear()

            hu_daily_cases = get_daily_series(hu, "newcases", hu_cum)
            sk_daily_cases = get_daily_series(sk, "newcases", sk_cum)

            hu_deaths_level = get_level_series(hu, "death")
            sk_deaths_level = get_level_series(sk, "death")

            hu_daily_rec = get_daily_series(hu, "recovered", hu_cum)
            sk_daily_rec = get_daily_series(sk, "recovered", sk_cum)

            hu_hosp = get_level_series(hu, "hospital")
            sk_hosp = get_level_series(sk, "hospital")

            hu_cases = hu_daily_cases / pop_hu * 100000
            sk_cases = sk_daily_cases / pop_sk * 100000

            hu_deaths = hu_deaths_level / pop_hu * 100000
            sk_deaths = sk_deaths_level / pop_sk * 100000

            hu_rec = hu_daily_rec.rolling(7, min_periods=1).mean() / pop_hu * 100000
            sk_rec = sk_daily_rec.rolling(7, min_periods=1).mean() / pop_sk * 100000

            hu_hosp_100k = hu_hosp.rolling(7, min_periods=1).mean() / pop_hu * 100000
            sk_hosp_100k = sk_hosp.rolling(7, min_periods=1).mean() / pop_sk * 100000

            axs[0, 0].plot(
                hu["date"],
                hu_cases,
                color="tab:red",
                linewidth=2,
                label="Magyarország"
            )
            axs[0, 0].plot(
                sk["date"],
                sk_cases,
                color="tab:blue",
                linewidth=2,
                label="Szlovákia"
            )
            axs[0, 0].set_title("Új fertőzések / 100k")
            axs[0, 0].legend(frameon=False)

            axs[0, 1].plot(
                hu["date"],
                hu_deaths,
                color="tab:red",
                linewidth=2,
                label="Magyarország"
            )
            axs[0, 1].plot(
                sk["date"],
                sk_deaths,
                color="tab:blue",
                linewidth=2,
                label="Szlovákia"
            )
            axs[0, 1].set_title("Halálozás / 100k")
            axs[0, 1].legend(frameon=False)

            axs[1, 0].plot(
                hu["date"],
                hu_rec,
                color="tab:red",
                linewidth=2,
                label="Magyarország"
            )
            axs[1, 0].plot(
                sk["date"],
                sk_rec,
                color="tab:blue",
                linewidth=2,
                label="Szlovákia"
            )
            axs[1, 0].set_title("Új gyógyult / 100k")
            axs[1, 0].legend(frameon=False)

            axs[1, 1].plot(
                hu["date"],
                hu_hosp_100k,
                color="tab:red",
                linewidth=2,
                label="Magyarország"
            )
            axs[1, 1].plot(
                sk["date"],
                sk_hosp_100k,
                color="tab:blue",
                linewidth=2,
                label="Szlovákia"
            )
            axs[1, 1].set_title("Kórház / 100k")
            axs[1, 1].legend(frameon=False)

            format_axes()
            add_period_backgrounds_compare(
                hu["date"], hu_lockdown, hu_vaccine, sk_lockdown, sk_vaccine
            )
            add_background_legend()

            fig.tight_layout(pad=2, rect=[0, 0, 1, 0.95])
            canvas.draw()

        except Exception as e:
            messagebox.showerror("Hiba", str(e))

    box.bind("<<ComboboxSelected>>", lambda event: plot())

    ttk.Button(
        left,
        text="Kimutatás",
        command=plot,
        width=22
    ).pack(pady=10)

    ttk.Button(
        left,
        text="HU vs SK összehasonlítás",
        command=compare,
        width=22
    ).pack(pady=10)

    plot()


if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    run()
    root.mainloop()