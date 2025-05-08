import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import pandas as pd
from control.matlab import tf, feedback, step
import Sistema_PID as pid
from Graficos import plt_Ziegler_Nichols, plt_Cohen_Coon

def get_setpoint():
    setpoint_str = entry_setpoint.get().strip()
    if not setpoint_str:
        setpoint = 100.0
    else:
        setpoint = float(setpoint_str)
    return setpoint

def atualiza_entradas():
    metodo = metodo_var.get()
    if metodo == "Ziegler-Nichols" or metodo == "Cohen-Coon":
        entry_kp.config(state="disabled")
        entry_ti.config(state="disabled")
        entry_td.config(state="disabled")
    else:
        entry_kp.config(state="normal")
        entry_ti.config(state="normal")
        entry_td.config(state="normal")

def print_parametros(p):
    tr, ts, erro, mp, mp_t, overshoot = p
    print(p)

    output_param_label.config(text=(
        "Parametros de desempenho:"
        f"\nTr = {tr:.2f} "
        f"\nTs = {ts:.2f} "
        f"\nMp = {mp:.2f} "
        #f"\nOvershoot = {overshoot:.2f}"
    ))



# Carrega Dataset
df = pid.load_dataset()

t = df['Tempo'].astype(float).values    # Auxiliar de tempo

# Aplica Método de Smith
k ,tau, theta = pid.metodo_smith(df["Tempo"].values, df['Resultado Fisico'].values)

# Calculo da função de transferencia 
funcao_malha_aberta, malha_aberta = pid.funcao_transferencia(k, tau, theta, t)

# Calculo dos parametros de malha aberta
param_malha_aberta = pid.analisar_parametros(*malha_aberta)


# === Função ao clicar no botão ===
def simular():
    
    setpoint = get_setpoint()   # Le o valor do Setpoint

    atualiza_entradas()

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
        plt_Ziegler_Nichols(ax, canvas, *malha_aberta, *malha_fechada_ziegler, param_ziegler_nichols)
        print_parametros(param_ziegler_nichols)
    elif metodo == "Cohen-Coon":
        # Calcula os parametros do PID
        kp, ki, kd, ti, td = pid.cohen_coon(k ,tau, theta)
        
        # Cria uma malha fechada com o controlador PID
        funcao_cohen, malha_fechada_cohen = pid.cria_malha_fechada(kp, ki, kd, funcao_malha_aberta, setpoint, t)

        # Analisa os parametros relacionados aos dados do grafico de Cohen Coon
        param_cohen_coon = pid.analisar_parametros(*malha_fechada_cohen)

        # Plota o grafico de Ziegle-Nichols 
        plt_Cohen_Coon(ax, canvas, *malha_aberta, *malha_fechada_cohen, param_cohen_coon)
        print_parametros(param_cohen_coon)
    else:   # Método Manual
        try:
            kp = float(entry_kp.get())
            ti = float(entry_ti.get())
            td = float(entry_td.get())
        except ValueError:
            output_label.config(text="Erro: valores manuais inválidos.")
            return
        ki = kp/ti
        kd = kp*td

        # Cria uma malha fechada com o controlador PID
        funcao_manual, malha_fechada_manual = pid.cria_malha_fechada(kp, ki, kd, funcao_malha_aberta, setpoint, t)

        # Analisa os parametros relacionados aos dados do grafico de 
        param_manual = pid.analisar_parametros(*malha_fechada_manual)

        # Plota o grafico de Ziegle-Nichols 
        plt_Cohen_Coon(ax, canvas, *malha_aberta, *malha_fechada_manual, param_manual)
        print_parametros(param_manual)


    output_label.config(text=(
        "\nParametros de PID:              "
        f"\nKp = {kp:.2f} "
        f"\nTi = {ti:.2f} "
        f"\nTd = {td:.2f} "))



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

# Quando o método mudar, atualizar os campos
metodo_menu.bind("<<ComboboxSelected>>", lambda e: atualiza_entradas())

# Entrada de dados pelo usuário
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
output_label = ttk.Label(frame)
output_label.grid(row=6, columnspan=2)

output_param_label = ttk.Label(frame)
output_param_label.grid(row=7, columnspan=2)


# === Gráfico ===
fig, ax = plt.subplots(figsize=(6, 4))
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().grid(row=0, column=1)

# Inicializa as entradas com os valores corretos
atualiza_entradas()

root.mainloop()
