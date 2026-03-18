import tkinter as tk
from tkinter import messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
import matplotlib.dates as mdates
from matplotlib.ticker import StrMethodFormatter

plt.style.use("seaborn-v0_8-whitegrid")

RECOVERY_DELAY = 14
SMOOTHING_WINDOW = 7


def numeric(series):
    return pd.to_numeric(series, errors="coerce").fillna(0).clip(lower=0)


def estimate_recovered(df):
    """
    SEIRDVH-alapú becslés:
    Recovered(t) ≈ Newcases(t-14) - Death(t-14)

    Értelmezés:
    - a kb. 14 nappal korábbi új fertőzések jelentős része addigra gyógyultnak tekinthető
    - ebből levonjuk a halálozást
    - negatív értéket nem engedünk
    """
    delayed_cases = df["Newcases"].shift(RECOVERY_DELAY).fillna(0)
    delayed_deaths = df["Death"].shift(RECOVERY_DELAY).fillna(0)
    recovered = (delayed_cases - delayed_deaths).clip(lower=0)
    return recovered


def estimate_active(df, recovered):
    """
    Becsült aktív esetek:
    active ≈ cumulative_cases - cumulative_deaths - cumulative_recovered
    """
    cumulative_cases = df["Newcases"].cumsum()
    cumulative_deaths = df["Death"].cumsum()
    cumulative_recovered = recovered.cumsum()

    active = cumulative_cases - cumulative_deaths - cumulative_recovered
    return active.clip(lower=0)


def infer_periods(df):
    """
    Egyszerű háttérszínezési időszakok:
    - kezdeti időszak: indulástól +30 nap
    - oltási időszak: amikor először megjelenik nem nulla vaccination
    """
    start = df["Date"].min()
    end = df["Date"].max()

    lockdown = start + pd.Timedelta(days=30)

    vaccination_nonzero = df[df["Vaccination"] > 0]
    if not vaccination_nonzero.empty:
        vaccine_start = vaccination_nonzero["Date"].iloc[0]
    else:
        vaccine_start = start + pd.Timedelta(days=300)

    if vaccine_start < lockdown:
        vaccine_start = lockdown + pd.Timedelta(days=30)

    if vaccine_start > end:
        vaccine_start = end

    return start, end, lockdown, vaccine_start


def run():
    try:
        df = pd.read_csv("covid_ni.csv", sep=";")
    except Exception as e:
        messagebox.showerror("Hiba", f"A fájl beolvasása nem sikerült:\n{e}")
        return

    required_columns = ["Date", "Vaccination", "Death", "Newcases", "Hospital", "Positive"]
    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        messagebox.showerror(
            "Hiba",
            "Hiányzó oszlop(ok):\n" + ", ".join(missing)
        )
        return

    try:
        df["Date"] = pd.to_datetime(df["Date"], format="%Y.%m.%d")
    except Exception as e:
        messagebox.showerror("Hiba", f"A dátum formátuma hibás:\n{e}")
        return

    df = df.sort_values("Date").copy()

    df["Vaccination"] = numeric(df["Vaccination"])
    df["Death"] = numeric(df["Death"])
    df["Newcases"] = numeric(df["Newcases"])
    df["Hospital"] = numeric(df["Hospital"])
    df["Positive"] = numeric(df["Positive"])

    recovered = estimate_recovered(df)
    active = estimate_active(df, recovered)

    newcases_smooth = df["Newcases"].rolling(SMOOTHING_WINDOW, min_periods=1).mean()
    positive_smooth = df["Positive"].rolling(SMOOTHING_WINDOW, min_periods=1).mean()
    death_smooth = df["Death"].rolling(SMOOTHING_WINDOW, min_periods=1).mean()
    recovered_smooth = recovered.rolling(SMOOTHING_WINDOW, min_periods=1).mean()
    active_smooth = active.rolling(SMOOTHING_WINDOW, min_periods=1).mean()
    hospital_smooth = df["Hospital"].rolling(SMOOTHING_WINDOW, min_periods=1).mean()
    vaccination_smooth = df["Vaccination"].rolling(SMOOTHING_WINDOW, min_periods=1).mean()

    root = tk.Tk()
    root.title("COVID epidemiológiai kimutatás – SEIRDVH modell")
    root.geometry("1180x720")

    info_label = tk.Label(
        root,
        text=(
            "Alkalmazott modell: SEIRDVH-alapú becslés | "
            f"Gyógyult képlet: Recovered(t) ≈ Newcases(t-{RECOVERY_DELAY}) - Death(t-{RECOVERY_DELAY})"
        ),
        font=("Segoe UI", 10),
        pady=8
    )
    info_label.pack()

    fig, axs = plt.subplots(2, 2, figsize=(11, 7))
    x = df["Date"]

    start, end, lockdown, vaccine_start = infer_periods(df)

    for ax in axs.flat:
        if start < lockdown:
            ax.axvspan(start, lockdown, color="lightgray", alpha=0.08)

        if lockdown < vaccine_start:
            ax.axvspan(lockdown, vaccine_start, color="orange", alpha=0.12)

        if vaccine_start < end:
            ax.axvspan(vaccine_start, end, color="green", alpha=0.10)

        ax.axvline(lockdown, linestyle="--", color="darkorange", linewidth=1.1, alpha=0.7)
        ax.axvline(vaccine_start, linestyle="--", color="darkgreen", linewidth=1.1, alpha=0.7)

    axs[0, 0].plot(
        x,
        newcases_smooth,
        color="tab:red",
        linewidth=2,
        label="Új esetek"
    )
    axs[0, 0].plot(
        x,
        positive_smooth,
        color="tab:blue",
        linewidth=2,
        label="Pozitív tesztek"
    )
    axs[0, 0].set_title("Fertőzések / pozitív tesztek")
    axs[0, 0].legend(frameon=False)

    axs[0, 1].plot(
        x,
        death_smooth,
        color="black",
        linewidth=2,
        label="Halálozás"
    )
    axs[0, 1].set_title("Napi halálozás")
    axs[0, 1].legend(frameon=False)

    axs[1, 0].plot(
        x,
        recovered_smooth,
        color="tab:green",
        linewidth=2,
        label="Becsült gyógyult"
    )
    axs[1, 0].plot(
        x,
        active_smooth,
        color="purple",
        linewidth=2,
        label="Becsült aktív"
    )
    axs[1, 0].set_title("SEIRDVH becslések")
    axs[1, 0].legend(frameon=False)

    axs[1, 1].plot(
        x,
        hospital_smooth,
        color="tab:orange",
        linewidth=2,
        label="Kórház"
    )
    axs[1, 1].plot(
        x,
        vaccination_smooth,
        color="teal",
        linewidth=2,
        label="Oltás"
    )
    axs[1, 1].set_title("Kórház / oltás")
    axs[1, 1].legend(frameon=False)

    for ax in axs.flat:
        ax.grid(alpha=0.3)
        ax.set_xlabel("Dátum")
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=4))
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
        ax.tick_params(axis="x", rotation=25)
        ax.yaxis.set_major_formatter(StrMethodFormatter("{x:,.0f}"))

    fig.suptitle("COVID epidemiológiai kimutatás (SEIRDVH modell)", fontsize=14)
    fig.tight_layout(rect=[0, 0, 1, 0.95])

    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    canvas.draw()

    root.mainloop()


if __name__ == "__main__":
    run()
