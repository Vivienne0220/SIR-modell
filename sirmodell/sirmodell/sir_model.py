import tkinter as tk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.ticker import StrMethodFormatter

plt.style.use("seaborn-v0_8-whitegrid")

sir_window = None

def run():
    global sir_window

    if sir_window is not None and sir_window.winfo_exists():
        sir_window.lift()
        return

    window = tk.Toplevel()
    sir_window = window

    window.title("SIR járványmodell")
    window.geometry("1100x560")
    window.minsize(1000, 520)

    def on_close():
        global sir_window
        sir_window = None
        window.destroy()

    window.protocol("WM_DELETE_WINDOW", on_close)

    N = 10000

    def sir(S, I, R, beta, gamma):
        dS = -beta * S * I
        dI = beta * S * I - gamma * I
        dR = gamma * I
        return dS, dI, dR

    def simulate(S0, I0, R0, beta, gamma, days=160, dt=0.1):
        steps = int(days / dt)

        S = [S0]
        I = [I0]
        R = [R0]

        for _ in range(steps):
            dS, dI, dR = sir(S[-1], I[-1], R[-1], beta, gamma)
            S.append(S[-1] + dS * dt)
            I.append(I[-1] + dI * dt)
            R.append(R[-1] + dR * dt)

        t = np.linspace(0, days, steps + 1)
        return t, np.array(S) * N, np.array(I) * N, np.array(R) * N
    
    S0_init = 0.99
    I0_init = 0.01
    R0_init = 0.0
    beta_init = 0.35
    gamma_init = 0.10

    main_frame = tk.Frame(window)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    control_frame = tk.Frame(main_frame)
    control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 15))

    chart_frame = tk.Frame(main_frame)
    chart_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    fig, ax = plt.subplots(figsize=(7, 4.8))
    canvas = FigureCanvasTkAgg(fig, master=chart_frame)
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    t, S, I, R = simulate(S0_init, I0_init, R0_init, beta_init, gamma_init)

    lS, = ax.plot(t, S, label="Fogékony", color="tab:blue", linewidth=2)
    lI, = ax.plot(t, I, label="Fertőzött", color="tab:red", linewidth=2)
    lR, = ax.plot(t, R, label="Gyógyult", color="tab:green", linewidth=2)

    ax.set_title("SIR járványdinamika")
    ax.set_xlabel("Napok")
    ax.set_ylabel("Egyének száma")
    ax.legend(frameon=False)
    ax.grid(alpha=0.3)
    ax.yaxis.set_major_formatter(StrMethodFormatter("{x:,.0f}"))
    fig.tight_layout(pad=2)

    tk.Label(
        control_frame,
        text="Modell paraméterei",
        font=("Segoe UI", 12, "bold")
    ).pack(anchor="w", pady=(0, 8))

    slider_width = 260

    beta_slider = tk.Scale(
        control_frame,
        from_=0,
        to=1,
        resolution=0.01,
        orient=tk.HORIZONTAL,
        label="β fertőzési ráta",
        length=slider_width,
        font=("Segoe UI", 9)
    )
    beta_slider.set(beta_init)
    beta_slider.pack(anchor="w", pady=2)

    gamma_slider = tk.Scale(
        control_frame,
        from_=0,
        to=1,
        resolution=0.01,
        orient=tk.HORIZONTAL,
        label="γ gyógyulási ráta",
        length=slider_width,
        font=("Segoe UI", 9)
    )
    gamma_slider.set(gamma_init)
    gamma_slider.pack(anchor="w", pady=2)

    I0_slider = tk.Scale(
        control_frame,
        from_=0,
        to=0.1,
        resolution=0.001,
        orient=tk.HORIZONTAL,
        label="Kezdeti fertőzöttek aránya",
        length=slider_width,
        font=("Segoe UI", 9)
    )
    I0_slider.set(I0_init)
    I0_slider.pack(anchor="w", pady=2)

    mask_slider = tk.Scale(
        control_frame,
        from_=0,
        to=1,
        resolution=0.01,
        orient=tk.HORIZONTAL,
        label="Maszkhasználat aránya",
        length=slider_width,
        font=("Segoe UI", 9)
    )
    mask_slider.set(0.0)
    mask_slider.pack(anchor="w", pady=2)

    vax_slider = tk.Scale(
        control_frame,
        from_=0,
        to=1,
        resolution=0.01,
        orient=tk.HORIZONTAL,
        label="Oltottsági arány",
        length=slider_width,
        font=("Segoe UI", 9)
    )
    vax_slider.set(0.0)
    vax_slider.pack(anchor="w", pady=2)

    recover_slider = tk.Scale(
        control_frame,
        from_=0,
        to=1,
        resolution=0.01,
        orient=tk.HORIZONTAL,
        label="Immunitással rendelkezők",
        length=slider_width,
        font=("Segoe UI", 9)
    )
    recover_slider.set(0.0)
    recover_slider.pack(anchor="w", pady=2)

    dist_slider = tk.Scale(
        control_frame,
        from_=0,
        to=1,
        resolution=0.01,
        orient=tk.HORIZONTAL,
        label="Szociális távolságtartás",
        length=slider_width,
        font=("Segoe UI", 9)
    )
    dist_slider.set(0.0)
    dist_slider.pack(anchor="w", pady=2)

    tk.Label(
        control_frame,
        text="Intézkedések kapcsolása",
        font=("Segoe UI", 10, "bold")
    ).pack(anchor="w", pady=(10, 4))

    mask_on = tk.BooleanVar(value=True)
    vax_on = tk.BooleanVar(value=True)
    recover_on = tk.BooleanVar(value=True)
    dist_on = tk.BooleanVar(value=True)

    check_frame = tk.Frame(control_frame)
    check_frame.pack(anchor="w", pady=(0, 10))

    info_label = tk.Label(
        control_frame,
        text="",
        justify="left",
        font=("Segoe UI", 9)
    )
    info_label.pack(anchor="w", pady=(6, 10))

    def update(val=None):
        beta = beta_slider.get()
        gamma = gamma_slider.get()

        I0 = I0_slider.get()
        S0 = 1 - I0

        m = mask_slider.get() if mask_on.get() else 0
        v = vax_slider.get() if vax_on.get() else 0
        p = recover_slider.get() if recover_on.get() else 0
        d = dist_slider.get() if dist_on.get() else 0

        beta_eff = beta * (1 - m) * (1 - v) * (1 - p) * (1 - d)

        t, S, I, R = simulate(S0, I0, R0_init, beta_eff, gamma)

        lS.set_data(t, S)
        lI.set_data(t, I)
        lR.set_data(t, R)

        ax.relim()
        ax.autoscale_view()

        peak_i = np.max(I)
        peak_day = t[np.argmax(I)]

        info_label.config(
            text=(
                f"Effektív β: {beta_eff:.3f}\n"
                f"Csúcspont napja: {peak_day:.1f}\n"
                f"Max fertőzöttek: {peak_i:,.0f} fő"
            )
        )

        canvas.draw()

    tk.Checkbutton(
        check_frame,
        text="Maszk aktív",
        variable=mask_on,
        command=update
    ).pack(anchor="w")

    tk.Checkbutton(
        check_frame,
        text="Oltás aktív",
        variable=vax_on,
        command=update
    ).pack(anchor="w")

    tk.Checkbutton(
        check_frame,
        text="Immunitás aktív",
        variable=recover_on,
        command=update
    ).pack(anchor="w")

    tk.Checkbutton(
        check_frame,
        text="Távolságtartás aktív",
        variable=dist_on,
        command=update
    ).pack(anchor="w")

    button_frame = tk.Frame(control_frame)
    button_frame.pack(anchor="w", pady=(5, 0))

    def reset():
        beta_slider.set(beta_init)
        gamma_slider.set(gamma_init)
        I0_slider.set(I0_init)
        mask_slider.set(0.0)
        vax_slider.set(0.0)
        recover_slider.set(0.0)
        dist_slider.set(0.0)

        mask_on.set(True)
        vax_on.set(True)
        recover_on.set(True)
        dist_on.set(True)

        update()

    tk.Button(
        button_frame,
        text="Alaphelyzet",
        width=18,
        command=reset
    ).pack(anchor="w")

    for s in [
        beta_slider,
        gamma_slider,
        I0_slider,
        mask_slider,
        vax_slider,
        recover_slider,
        dist_slider
    ]:
        s.config(command=update)

    update()
