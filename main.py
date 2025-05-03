import numpy as np
import pandas as pd
import scipy.io 
import matplotlib.pyplot as plt
import control as ctrl

def load_dataset():
  '''Tranformando arquivo .mat em um dataset'''

  # Carregar o arquivo .mat
  mat_data = scipy.io.loadmat('Dataset_Grupo2.mat')

  # Extrai o conteúdo da variável 'reactionExperiment'
  reaction = mat_data['reactionExperiment'][0, 0]

  # Acessa os dados
  sample_time = reaction['sampleTime'].flatten()
  temperature = reaction['dataInput'].flatten()
  resultado_fisico = reaction['dataOutput'].flatten()

  # Cria o DataFrame
  df = pd.DataFrame({
    'Tempo': sample_time,
    'Temperatura': temperature,
    'Resultado Fisico': resultado_fisico
  })

  print(df.head())
  return df

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

def metodo_sundaresan(tempo, resposta):
    """
    Aplica o método de Sundaresan e Krishnaswamy para estimar K, tau e theta.

    Parâmetros:
    - tempo: vetor com os instantes de tempo
    - resposta: vetor com os valores da variável de Estado Físico

    Retorna:
    - K: ganho estático
    - tau: constante de tempo do sistema
    - theta: tempo morto (delay)
    """

    # Normaliza a resposta
    resposta_normalizada = (resposta - resposta[0]) / (resposta[-1] - resposta[0])

    # Define os níveis de 35,3% e 85,3% da resposta
    y1_target = 0.353
    y2_target = 0.853

    # Encontra os tempos correspondentes a esses pontos
    t1 = np.interp(y1_target, resposta_normalizada, tempo)
    t2 = np.interp(y2_target, resposta_normalizada, tempo)

    # Calcula os parâmetros
    tau = 1.3 * (t2 - t1)
    theta = t1 - 0.29 * (t2 - t1)
    K = resposta[-1] - resposta[0]

    return K, tau, theta

def criar_funcao_transferencia(k, tau, theta, ordem_pade=1):
    """
    Gera a função de transferência de um sistema FOPDT

    Parâmetros:
    - k: ganho estático
    - tau: constante de tempo
    - theta: tempo morto (atraso)
    - ordem_pade: ordem da aproximação de Padé para o atraso (default = 1)

    Retorna:
    - G: função de transferência aproximada (objeto TransferFunction)
    """
    # Parte sem atraso
    G_sem_atraso = ctrl.tf([k], [tau, 1])

    # Aproximação de Padé para o atraso
    num_pade, den_pade = ctrl.pade(theta, ordem_pade)
    atraso_pade = ctrl.tf(num_pade, den_pade)

    # Combinando
    G = ctrl.series(atraso_pade, G_sem_atraso)
    return G

def plt_func_tranferencia(t, y):

  # Gráfico
  plt.plot(t, y)
  plt.xlabel('Tempo (s)')
  plt.ylabel('Resposta')
  plt.title('Resposta ao Degrau')
  plt.grid(True)
  plt.show()


# Carrega o dataset
dataset = load_dataset()

# Mostra os dados iniciais 
plt_dataset(dataset)

#Calculo do metodo de Sundaresan
k, tau, theta = metodo_sundaresan(dataset['Tempo'].values, dataset['Temperatura'].values)

print(f"Ganho K = {k:.2f}")
print(f"Constante de tempo τ = {tau:.2f} s")
print(f"Tempo morto θ = {theta:.2f} s")

# Calculo da func. de Tranferencia
func_transferencia = criar_funcao_transferencia(k, tau, theta)
print("Função de tranferenccia: ", func_transferencia)

# Calcula a resposta no tempo da função de transferencia
tempo_ft, estado_fisico_ft = ctrl.step_response(func_transferencia)

# Grafico da Função de Tranferencia
plt_func_tranferencia(tempo_ft, estado_fisico_ft)


