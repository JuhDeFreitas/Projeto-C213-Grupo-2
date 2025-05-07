import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

def plt_dataset(dataset):
    '''Mostra os graficos de Temp X Tempo e Est.físico X Tempo com as dados do dataset'''
    # Criar os subplots lado a lado
    plt.figure(figsize=(12, 6))

    # Gráfico 1 - Temperatura (Entrada)
    plt.subplot(1, 2, 1)
    plt.plot(dataset['Tempo'], dataset['Temperatura'], color='blue')
    plt.xlabel('Tempo (s)')
    plt.ylabel('Temperatura (°C)')
    plt.title('Simulação de Temperatura ao Longo do Tempo')

    # Gráfico 2 - Resultado Físico (Saída)
    plt.subplot(1, 2, 2)
    plt.plot(dataset['Tempo'], dataset['Resultado Fisico'],label='Resultado Físico', color='green')
    plt.plot(dataset['Tempo'], dataset['Temperatura'],label='Temperatura', color='blue')
    plt.xlabel('Tempo (s)')
    plt.ylabel('Resultado Físico')
    plt.title('Resposta do Sistema (Resultado Físico)')

    # Ajustar layout para não sobrepor elementos
    plt.legend()
    plt.tight_layout()
    plt.show()

def plt_modelo(dataset, t, f):
    '''Plota o grafico de função de transferencia com parametros calculados pelo metodo de Smith X Dados Reais'''
    plt.figure(figsize=(10, 5))
    plt.plot(t, f, label='Metodo Smith', linewidth=2)
    plt.plot(dataset['Tempo'], dataset['Resultado Fisico'], label='Dados experimentais', linestyle='--', linewidth=2)
    plt.xlabel('Tempo (s)')
    plt.ylabel('Resposta (Resultado Físico)')
    plt.title('Comparação: Modelo vs Dados Reais')
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()


def plt_modelo_ajustado(t, f, t_ajustado, f_ajustado, dataset):
    plt.figure(figsize=(10, 5))

    # Plotar as curvas
    plt.plot(t_ajustado, f_ajustado, label='Metodo Smith Ajustado', linewidth=2)
    plt.plot(t, f, label='Metodo Smith', linewidth=2)
    plt.plot(dataset['Tempo'], dataset['Resultado Fisico'], label='Dados experimentais', linestyle='--', linewidth=2)

    # Focar apenas na primeira metade do tempo
    tempo_max = dataset['Tempo'].max()
    plt.xlim(0, tempo_max / 3)  # Zoom na primeira metade do tempo

    # Labels e título
    plt.xlabel('Tempo (s)')
    plt.ylabel('Resposta (Resultado Físico)')
    plt.title('Comparação: Modelo vs Dados Reais (Zoom na primeira metade)')
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()


def plt_Ziegler_Nichols(ax, canvas, t_modelo, f_modelo, t_pid, f_pid):
    
    # Encontra o primeiro índice onde f > 0
    idx = np.argmax(f_pid > 0)

    # Corta os vetores a partir desse índice
    t_pid = t_pid[idx:]
    f_pid = f_pid[idx:]
    
    ax.clear()
    ax.plot(t_modelo, f_modelo, label="Resposta Original", color="gray")
    ax.plot(t_pid, f_pid, label="Controle Ziegler-Nichols (PID)", linestyle="--", color="red")

    ax.set_title("Resposta da Malha Fechada com Controle PID (Ziegler-Nichols)")
    ax.set_xlabel("Tempo (s)")
    ax.set_ylabel("Temperatura (°C)")
    ax.grid(True)
    ax.legend()
    canvas.draw()
    
    

def plt_malhas(t1, f1, t2, f2, t3, f3):
    '''Mostra três gráficos de Resultado Físico X Tempo comparando malha aberta e controladas'''
    
    # Criar a figura com tamanho adequado
    plt.figure(figsize=(15, 4))
    
    # Gráfico 1 - Malha aberta
    plt.subplot(1, 3, 1)  # 1 linha, 3 colunas, posição 1
    plt.plot(t1, f1, color='blue', label='Malha Aberta')
    plt.xlabel('Tempo (s)')
    plt.ylabel('Resultado Físico')
    plt.title('Malha Aberta')
    plt.grid(True)
    plt.legend()

    # Gráfico 2 - Malha Fechada Ziegler-Nichols
    plt.subplot(1, 3, 2)  # posição 2
    plt.plot(t2, f2, color='green', label='Ziegler-Nichols')
    plt.xlabel('Tempo (s)')
    plt.ylabel('Resultado Físico')
    plt.title('Fechada (Ziegler-Nichols)')
    plt.grid(True)
    plt.legend()

    # Gráfico 3 - Malha Fechada Cohen-Coon
    plt.subplot(1, 3, 3)  # posição 3
    plt.plot(t3, f3, color='red', label='Cohen-Coon')
    plt.xlabel('Tempo (s)')
    plt.ylabel('Resultado Físico')
    plt.title('Fechada (Cohen-Coon)')
    plt.grid(True)
    plt.legend()
    
    # Ajustar layout para não sobrepor os elementos
    plt.tight_layout()
    plt.show()



