import numpy as np
import matplotlib.pyplot as plt

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
    plt.plot(dataset['Tempo'], dataset['Resultado Fisico'], color='green')
    plt.xlabel('Tempo (s)')
    plt.ylabel('Resultado Físico')
    plt.title('Resposta do Sistema (Resultado Físico)')

    # Ajustar layout para não sobrepor elementos
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

'''def plt_modelo_ajustado(t, f, t_ajustado, f_ajustado, dataset):
  plt.figure(figsize=(10, 5))
  plt.plot(t_ajustado, f_ajustado, label='Metodo Smith Ajustado', linewidth=2)
  plt.plot(t, f, label='Metodo Smith', linewidth=2)
  plt.plot(dataset['Tempo'], dataset['Resultado Fisico'], label='Dados experimentais', linestyle='--', linewidth=2)
  plt.xlabel('Tempo (s)')
  plt.ylabel('Resposta (Resultado Físico)')
  plt.title('Comparação: Modelo vs Dados Reais')
  plt.grid(True)
  plt.legend()
  plt.tight_layout()
  plt.show()'''


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


