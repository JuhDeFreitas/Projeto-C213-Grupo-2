import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import pandas as pd
from control.matlab import tf, feedback, step
import sistema_PID as pid
from Graficos import plt_Ziegler_Nichols, plt_Cohen_Coon

def atualizar_entradas():
    metodo = metodo_var.get()
    if metodo == "Ziegler-Nichols" or metodo == "Cohen-Coon":
        entry_kp.config(state="disabled")
        entry_ti.config(state="disabled")
        entry_td.config(state="disabled")
    else:
        entry_kp.config(state="normal")
        entry_ti.config(state="normal")
        entry_td.config(state="normal")

# === Função ao clicar no botão ===
def simular():
    
    # Carrega Dataset
    df = pid.load_dataset()

    t = df['Tempo'].astype(float).values
   # setpoint = 100

    # Método de Smith
    k ,tau, theta = pid.metodo_smith(df["Tempo"].values, df['Resultado Fisico'].values)

    # Calculo da função de transferencia 
    funcao_malha_aberta, malha_aberta = pid.funcao_transferencia(k, tau, theta, t)

    # Calcula os parametros da malha aberta
    param_malha_aberta = pid.analisar_parametros(*malha_aberta)

    # Le o valor do Setpoint
    
    setpoint_str = entry_setpoint.get().strip()
    try:
        setpoint = float(setpoint_str)
    except ValueError:
        setpoint = 100
        return

    # Calcula os parametros PID para cada método
    metodo = metodo_var.get()
    if metodo == "Ziegler-Nichols":
        # Calcula os parametros do PID
        kp, ki, kd, ti, td = pid.ziegler_nichols(k ,tau, theta)
        
        # Cria uma malha fechada com o controlador PID
        funcao_ziegler, malha_fechada_ziegler = pid.cria_malha_fechada(kp, ki, kd, funcao_malha_aberta, setpoint, t)

        # Analisa os parametros relacionados aos dados do grafico de Ziegler-Nichols
        param_ziegler_nichols = pid.analisar_parametros(*malha_fechada_ziegler)

        # Plota o grafico de Ziegle-Nichols 
        plt_Ziegler_Nichols(ax, canvas, *malha_aberta, *malha_fechada_ziegler)
    elif metodo == "Cohen-Coon":
         # Calcula os parametros do PID
        kp, ki, kd, ti, td = pid.cohen_coon(k ,tau, theta)
        
        # Cria uma malha fechada com o controlador PID
        funcao_cohen, malha_fechada_cohen = pid.cria_malha_fechada(kp, ki, kd, funcao_malha_aberta, setpoint, t)

        # Analisa os parametros relacionados aos dados do grafico de Ziegler-Nichols
        param_cohen_coon = pid.analisar_parametros(*malha_fechada_cohen)

        # Plota o grafico de Ziegle-Nichols 
        plt_Cohen_Coon(ax, canvas, *malha_aberta, *malha_fechada_cohen)
    else:
        try:
            kp = float(entry_kp.get())
            ti = float(entry_ti.get())
            td = float(entry_td.get())
        except:
            output_label.config(text="Erro: valores manuais inválidos.")
            return

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