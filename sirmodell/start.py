import tkinter as tk
from tkinter import messagebox
import sir_model
import sird_model
import seirdvh_model

def open_sir_model():
    sir_model.run()

def open_epidemic():
    sird_model.run()

def open_seirdvh_model():
    seirdvh_model.run()

# Ablak létrehozása
root = tk.Tk()
root.title("Főmenü")
root.geometry("400x300")
root.configure(bg="#f0f0f0")

# Cím
label = tk.Label(root, text="Válassz kategóriát", font=("Segoe UI", 16, "bold"), bg="#f0f0f0")
label.pack(pady=30)

# Gombok
btn1 = tk.Button(root, text="Saját SIR modell", font=("Segoe UI", 12), width=20, command=open_sir_model)
btn1.pack(pady=10)

btn2 = tk.Button(root, text="SIRD modell", font=("Segoe UI", 12), width=20, command=open_epidemic)
btn2.pack(pady=10)

btn3 = tk.Button(root, text="SEIHRD", font=("Segoe UI", 12), width=20, command=open_seirdvh_model)
btn3.pack(pady=10)

root.mainloop()
