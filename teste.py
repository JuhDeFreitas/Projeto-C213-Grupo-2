import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import pandas as pd
from control.matlab import tf, feedback, step
import sistema_PID as pid

# === Carregar Dataset ===
df = pid.dataset
t = df['Tempo'].values
u = df['Temperatura'].values
y = df['Resultado Fisico'].values

# === Identificação com Sundaresan ===
final_value = np.mean(y[int(len(y)*0.9):])
y1_target = 0.353 * final_value
y2_target = 0.853 * final_value
t1 = t[np.where(y >= y1_target)[0][0]]
t2 = t[np.where(y >= y2_target)[0][0]]
tau = (2/3) * (t2 - t1)
theta = 1.3 * t1 - 0.29 * t2
k = (max(y) - min(y)) / (max(u) - min(u))

# === Modelo de processo ===
sys = tf([k], [tau, 1])  # Sem atraso para simplificar na IHM

# === Função para simular PID ===
def simular_pid(kp, ti, td):
    pid = tf([kp*td, kp, kp/ti], [1, 0])
    malha = feedback(pid * sys, 1)
    t_out, y_out = step(malha, T=t)
    return t_out, y_out

# === Função ao clicar no botão ===
def simular():
    metodo = metodo_var.get()
    if metodo == "Ziegler-Nichols":
        kp = 1.2 * tau / (k * theta)
        ti = 2 * theta
        td = theta / 2
    elif metodo == "Cohen-Coon":
        kp = (tau / (k * theta)) * ((16 * theta + 3 * tau) / (12 * tau))
        ti = theta * (32 + 6 * (theta / tau)) / (13 + 8 * (theta / tau))
        td = 4 * theta / (11 + 2 * (theta / tau))
    else:
        try:
            kp = float(entry_kp.get())
            ti = float(entry_ti.get())
            td = float(entry_td.get())
        except:
            output_label.config(text="Erro: valores manuais inválidos.")
            return

    t_sim, y_sim = simular_pid(kp, ti, td)
    ax.clear()
    ax.plot(t, y, label="Original")
    ax.plot(t_sim, y_sim, label="Controlado", linestyle="--")
    ax.set_title("Resposta do Sistema com PID")
    ax.set_xlabel("Tempo (s)")
    ax.set_ylabel("Temperatura")
    ax.grid(True)
    ax.legend()
    canvas.draw()

    output_label.config(text=f"Kp={kp:.2f}, Ti={ti:.2f}, Td={td:.2f}")

# === Criar janela ===
root = tk.Tk()
root.title("Controle PID - Grupo 2")

# === Widgets ===
frame = ttk.Frame(root, padding="10")
frame.grid()

ttk.Label(frame, text="Método de Sintonia:").grid(row=0, column=0)
metodo_var = tk.StringVar(value="Ziegler-Nichols")
metodo_menu = ttk.Combobox(frame, textvariable=metodo_var, values=["Ziegler-Nichols", "Cohen-Coon", "Manual"])
metodo_menu.grid(row=0, column=1)

#Entrada de dados pelo usuàrio
ttk.Label(frame, text="Kp:").grid(row=1, column=0)
entry_kp = ttk.Entry(frame)
entry_kp.grid(row=1, column=1)

ttk.Label(frame, text="Ti:").grid(row=2, column=0)
entry_ti = ttk.Entry(frame)
entry_ti.grid(row=2, column=1)

ttk.Label(frame, text="Td:").grid(row=3, column=0)
entry_td = ttk.Entry(frame)
entry_td.grid(row=3, column=1)

ttk.Label(frame, text="Set Point:").grid(row=4, column=0)
entry_setpoint = ttk.Entry(frame)
entry_setpoint.grid(row=4, column=1)


ttk.Button(frame, text="Simular", command=simular).grid(row=5, columnspan=2, pady=10)
output_label = ttk.Label(frame, text="Parâmetros PID aparecerão aqui.")
output_label.grid(row=6, columnspan=2)

# === Gráfico ===
fig, ax = plt.subplots(figsize=(6, 4))
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().grid(row=0, column=1)

root.mainloop()