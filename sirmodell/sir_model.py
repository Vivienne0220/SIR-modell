import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, CheckButtons

def run():
    N = 10000 

    def SIR_model(S, I, R, beta, gamma):
        dS = -beta * S * I
        dI = beta * S * I - gamma * I
        dR = gamma * I
        return dS, dI, dR

    def simulate(S0, I0, R0, beta, gamma, days=160, dt=0.1):
        steps = int(days / dt)
        S, I, R = [S0], [I0], [R0]
        for _ in range(steps):
            dS, dI, dR = SIR_model(S[-1], I[-1], R[-1], beta, gamma)
            S.append(S[-1] + dS * dt)
            I.append(I[-1] + dI * dt)
            R.append(R[-1] + dR * dt)
        t = np.linspace(0, days, steps + 1)
        S = np.array(S) * N
        I = np.array(I) * N
        R = np.array(R) * N
        return t, S, I, R

    S0_init = 0.99
    I0_init = 0.01
    R0_init = 0.0
    beta_init = 0.35
    gamma_init = 0.1

    fig, ax = plt.subplots(figsize=(10,6))
    plt.subplots_adjust(left=0.25, bottom=0.45, right=0.85)

    t, S, I, R = simulate(S0_init, I0_init, R0_init, beta_init, gamma_init)
    lS, = ax.plot(t, S, label='Fogékony (S)')
    lI, = ax.plot(t, I, label='Fertőzött (I)')
    lR, = ax.plot(t, R, label='Gyógyult (R)')
    ax.set_xlabel('Napok száma')
    ax.set_ylabel('Szám a populációban')
    ax.set_title('SIR modell a védelmi intézkedések figyelembevételével')
    ax.legend()
    ax.grid()

    ax_beta = plt.axes([0.3, 0.35, 0.5, 0.03])
    ax_gamma = plt.axes([0.3, 0.31, 0.5, 0.03])
    ax_I0 = plt.axes([0.3, 0.27, 0.5, 0.03])
    ax_mask = plt.axes([0.3, 0.23, 0.5, 0.03])
    ax_vax = plt.axes([0.3, 0.19, 0.5, 0.03])
    ax_recover = plt.axes([0.3, 0.15, 0.5, 0.03])
    ax_dist = plt.axes([0.3, 0.11, 0.5, 0.03])

    s_beta = Slider(ax_beta, 'Transzmissziós arány (β)', 0.0, 1.0, valinit=beta_init, valstep=0.01)
    s_gamma = Slider(ax_gamma, 'Gyógyulási arány (γ)', 0.0, 1.0, valinit=gamma_init, valstep=0.01)
    s_I0 = Slider(ax_I0, 'Kezdeti prevalencia', 0.0, 0.1, valinit=I0_init, valstep=0.001)
    s_mask = Slider(ax_mask, 'Maszkhasználat aránya', 0.0, 1.0, valinit=0.0, valstep=0.01)
    s_vax = Slider(ax_vax, 'Oltottsági arány', 0.0, 1.0, valinit=0.0, valstep=0.01)
    s_recover = Slider(ax_recover, 'Immunitással rendelkezők', 0.0, 1.0, valinit=0.0, valstep=0.01)
    s_dist = Slider(ax_dist, 'Szociális távolságtartás mértéke', 0.0, 1.0, valinit=0.0, valstep=0.01)

    def create_checkbox(ax_pos, init=True):
        ax_cb = plt.axes(ax_pos)
        check = CheckButtons(ax_cb, [''], [init])
        txt = ax_cb.text(0.7, 0.5, 'BE' if init else 'KI', ha='left', va='center', transform=ax_cb.transAxes)
        return check, txt

    check_mask, txt_mask = create_checkbox([0.85, 0.23, 0.08, 0.03])
    check_vax, txt_vax = create_checkbox([0.85, 0.19, 0.08, 0.03])
    check_recover, txt_recover = create_checkbox([0.85, 0.15, 00.08, 0.03])
    check_dist, txt_dist = create_checkbox([0.85, 0.11, 0.08, 0.03])

    mask_on = [True]
    vax_on = [True]
    recover_on = [True]
    dist_on = [True]

    def toggle_mask(label):
        mask_on[0] = not mask_on[0]
        txt_mask.set_text('BE' if mask_on[0] else 'KI')
        update(None)
    check_mask.on_clicked(toggle_mask)

    def toggle_vax(label):
        vax_on[0] = not vax_on[0]
        txt_vax.set_text('BE' if vax_on[0] else 'KI')
        update(None)
    check_vax.on_clicked(toggle_vax)

    def toggle_recover(label):
        recover_on[0] = not recover_on[0]
        txt_recover.set_text('BE' if recover_on[0] else 'KI')
        update(None)
    check_recover.on_clicked(toggle_recover)

    def toggle_dist(label):
        dist_on[0] = not dist_on[0]
        txt_dist.set_text('BE' if dist_on[0] else 'KI')
        update(None)
    check_dist.on_clicked(toggle_dist)

    def update(val):
        beta = s_beta.val
        gamma = s_gamma.val
        I0 = s_I0.val
        S0 = 1 - I0
        m = s_mask.val if mask_on[0] else 0
        v = s_vax.val if vax_on[0] else 0
        p = s_recover.val if recover_on[0] else 0
        d = s_dist.val if dist_on[0] else 0
        beta_eff = beta * (1 - m) * (1 - v) * (1 - p) * (1 - d)

        t, S, I, R = simulate(S0, I0, R0_init, beta_eff, gamma)
        lS.set_ydata(S)
        lI.set_ydata(I)
        lR.set_ydata(R)
        ax.relim()
        ax.autoscale_view()
        fig.canvas.draw_idle()

    for s in [s_beta, s_gamma, s_I0, s_mask, s_vax, s_recover, s_dist]:
        s.on_changed(update)

    plt.show()

if __name__ == "__main__":
    run()
