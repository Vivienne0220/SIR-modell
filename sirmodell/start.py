import tkinter as tk
import sir_model
import sird_model
import seirdvh_model

BG = "#f4f6f8"
BTN = "#4a6fa5"
BTN_TXT = "white"


def open_sir():
    sir_model.run()


def open_sird():
    sird_model.run()


def open_seirdvh():
    seirdvh_model.run()


root = tk.Tk()
root.title("Járványmodellezési eszköz")
root.geometry("420x320")
root.configure(bg=BG)

title = tk.Label(
    root,
    text="Járvány modellező rendszer",
    font=("Segoe UI", 18, "bold"),
    bg=BG
)
title.pack(pady=30)

btn1 = tk.Button(
    root,
    text="SIR modell",
    font=("Segoe UI", 12),
    width=22,
    bg=BTN,
    fg=BTN_TXT,
    command=open_sir
)
btn1.pack(pady=8)

btn2 = tk.Button(
    root,
    text="SIRD modell",
    font=("Segoe UI", 12),
    width=22,
    bg=BTN,
    fg=BTN_TXT,
    command=open_sird
)
btn2.pack(pady=8)

btn3 = tk.Button(
    root,
    text="SEIRDVH elemzés",
    font=("Segoe UI", 12),
    width=22,
    bg=BTN,
    fg=BTN_TXT,
    command=open_seirdvh
)
btn3.pack(pady=8)

root.mainloop()