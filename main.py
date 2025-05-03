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
    'Tempo': sample_time/1000,
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

def metodo_smith(tempo, resposta, u0=0, uf=1):
    """
    Estima os parâmetros K, tau e theta pelo método de Smith.

    Parâmetros:
    - tempo: vetor de tempo (numpy array)
    - resposta: vetor da resposta ao degrau (numpy array)
    - u0: valor inicial do degrau (default=0)
    - uf: valor final do degrau (default=1)

    Retorna:
    - k: ganho estático
    - tau: constante de tempo
    - theta: tempo morto
    """

    # Valor final da resposta (assumindo que atinge o regime)
    y_final = resposta[-1]
    y_inicial = resposta[0]
    delta_y = y_final - y_inicial

    # Pontos para o método de Smith
    y_283 = y_inicial + 0.283 * delta_y
    y_632 = y_inicial + 0.632 * delta_y

    # Encontra os tempos correspondentes
    t_283 = tempo[np.where(resposta >= y_283)[0][0]]
    t_632 = tempo[np.where(resposta >= y_632)[0][0]]

    # Calcula parâmetros
    theta = 1.5 * t_283 - 0.5 * t_632
    tau = t_632 - theta
    k = delta_y / (uf - u0)

    return k, tau, theta

def funcao_transferencia(k, tau, theta, ordem_pade=1):
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

def plt_func_tranferencia(dataset, t, f):
  plt.figure(figsize=(10, 5))
  plt.plot(t, f, label='Modelo (FOPDT)', linewidth=2)
  plt.plot(dataset['Tempo'], dataset['Resultado Fisico'], label='Dados experimentais', linestyle='--', linewidth=2)
  plt.xlabel('Tempo (s)')
  plt.ylabel('Resposta (Resultado Físico)')
  plt.title('Comparação: Modelo vs Dados Reais')
  plt.grid(True)
  plt.legend()
  plt.tight_layout()
  plt.show()



# Carrega o dataset
dataset = load_dataset()

# Mostra os dados iniciais 
plt_dataset(dataset)

#Calculo do metodo de Sundaresan
k, tau, theta = metodo_sundaresan(dataset['Tempo'].values, dataset['Resultado Fisico'].values)

# Calculo da func. de Tranferencia
H_sundaresan = funcao_transferencia(k, tau, theta)

# Calcula a resposta no tempo da função de transferencia
t_sundaresan, f_sundaresan = ctrl.step_response(H_sundaresan)

# Grafico da Função de Tranferencia
plt_func_tranferencia(dataset, t_sundaresan, f_sundaresan)


