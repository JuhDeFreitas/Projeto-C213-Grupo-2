import numpy as np
import pandas as pd
import scipy.io 
import matplotlib.pyplot as plt
import control as ctrl
from control.matlab import tf, step
from scipy.optimize import minimize
from Graficos import plt_dataset, plt_modelo, plt_modelo_ajustado

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

def calcular_erro(params, dataset):
    k, tau, theta = params
    if tau <= 0 or theta < 0:
        return np.inf
    try:
        H = funcao_transferencia(k, tau, theta)
        t_sim, y_sim = ctrl.step_response(H, T=dataset['Tempo'].values)
        erro = np.mean((dataset['Resultado Fisico'].values - y_sim) ** 2)
        return erro
    except:
        return np.inf  # Em caso de erro numérico

def ajustar_parametros(k, tau, theta, dataset):
    resultado = minimize(
        calcular_erro, 
        [k, tau, theta], 
        args=(dataset,), 
        method='Nelder-Mead'
    )
    parametros_otimizados = resultado.x
    H_otimizado = funcao_transferencia(*parametros_otimizados)
    return parametros_otimizados, H_otimizado





# Carrega o dataset
dataset = load_dataset()

# Mostra os dados iniciais 
plt_dataset(dataset)

# Calculo pelo metodo de Smith
k, tau, theta = metodo_smith(dataset['Tempo'].values, dataset['Resultado Fisico'].values)

# Calculo da func. de Tranferencia
H_smith = funcao_transferencia(k, tau, theta)

# Calcula a resposta no tempo da função de transferencia
t_smith, f_smith = ctrl.step_response(H_smith)

# Grafico com o Modelo da Função de Tranferencia
plt_modelo(dataset, t_smith, f_smith)

# Ajuste de parametros para o método de smith
(parametros_ajustados, H_ajustado) = ajustar_parametros(k, tau, theta, dataset)
t_ajustado, f_ajustado = ctrl.step_response(H_ajustado)

plt_modelo_ajustado(t_smith, f_smith, t_ajustado, f_ajustado, dataset)




