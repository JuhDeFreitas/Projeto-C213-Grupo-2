import numpy as np
import pandas as pd
import scipy.io 
import matplotlib.pyplot as plt
import control as ctrl
from control.matlab import tf, step
from scipy.optimize import minimize
from Graficos import plt_dataset, plt_modelo, plt_modelo_ajustado, plt_malhas

def load_dataset():
  '''Tranformando arquivo .mat em um dataset'''

  # Carregar o arquivo .mat
  data = scipy.io.loadmat('Dataset_Grupo2.mat')
 
  struct = data['reactionExperiment'][0, 0]
  
  sample_time = struct['sampleTime'].squeeze()
  data_input = struct['dataInput'].squeeze()
  data_output = struct['dataOutput'].squeeze()

  df = pd.DataFrame({
      'Tempo': sample_time,
      'Temperatura': data_input,
      'Resultado Fisico': data_output
  })
  
  return df

def metodo_smith(tempo, resposta, u0=0, uf=1):
    """Estima os parâmetros K, tau e theta pelo método de Smith."""

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
  """  Gera a função de transferência de um sistema FOPDT  """

  # Parte sem atraso
  G_sem_atraso = ctrl.tf([k], [tau, 1])

  # Aproximação de Padé para o atraso
  num_pade, den_pade = ctrl.pade(theta, ordem_pade)
  atraso_pade = ctrl.tf(num_pade, den_pade)

  # Combinando
  G = ctrl.series(atraso_pade, G_sem_atraso)
  return G

def ziegler_nichols(k, tau, theta):
    Kp = 1.2 * tau / (k * theta)
    Ti = 2 * theta
    Td = 0.5 * theta
    Ki = Kp / Ti
    Kd = Kp * Td
    print("\n\nk, tau, theta em ziegle nichols: ", Kp, Ki, Td)
    return Kp, Ki, Kd

def cohen_coon(K, tau, theta):
    if tau == 0 or theta == 0 or K == 0:
        raise ValueError("K, tau e theta devem ser diferentes de zero")
    
    kp = (tau / (K * theta)) * ((16 * tau + 3 * theta) / (12 * tau))
    ti = theta * ((32 + 6 * (theta / tau)) / (13 + 8 * (theta / tau)))
    td = (4 * theta) / (11 + 2 * (theta / tau))

    # Conversão para forma padrão do PID
    ki = kp / ti
    kd = kp * td

    return kp,ki,kd

def cria_malha_fechada(kp, ki, kd, malha_aberta):
   # Cria o controlador PID
  PID = ctrl.tf([kd, kp, ki], [1, 0])  # Forma: Kp + Ki/s + Kd*s

  # Fecha a malha com realimentação
  h_fechada = ctrl.feedback(PID * malha_aberta, 1)

  return h_fechada

def analisar_resposta(t, y, ref=1.0, tolerancia=0.02):
    y_final = y[-1]
    
    # Tempo de subida: de 10% a 90% do valor final
    idx_10 = np.argmax(y >= 0.1 * y_final)
    idx_90 = np.argmax(y >= 0.9 * y_final)
    tempo_subida = t[idx_90] - t[idx_10]

    # Tempo de acomodação: quando entra e permanece dentro da faixa de tolerância
    superior = y_final * (1 + tolerancia)
    inferior = y_final * (1 - tolerancia)

    for i in range(len(y)-1, -1, -1):
        if y[i] > superior or y[i] < inferior:
            tempo_acomodacao = t[i+1]
            break
    else:
        tempo_acomodacao = 0  # Se nunca saiu, já estava acomodado

    # Erro em regime permanente
    erro_regime = abs(ref - y_final)

        # Pico máximo (overshoot)
    pico_maximo = np.max(y)
    tempo_pico = t[np.argmax(y)]
    overshoot_percent = ((pico_maximo - y_final) / y_final) * 100 if y_final != 0 else 0

    return tempo_subida, tempo_acomodacao, erro_regime, pico_maximo, tempo_pico, overshoot_percent




# Carrega o dataset
dataset = load_dataset()

# Mostra os dados iniciais 
plt_dataset(dataset)

# Calculo pelo metodo de Smith
k, tau, theta = metodo_smith(dataset['Tempo'].values, dataset['Resultado Fisico'].values)
print(f"Smith -  k: {k}, tau: {tau}, theta: {theta}")

# Calculo da func. de Tranferencia
H = funcao_transferencia(k, tau, theta)

# Calcula a resposta no tempo da função de transferencia
tempo_sim = dataset['Tempo'].astype(float).values
t_smith, f_smith = ctrl.step_response(H, T=tempo_sim)

# Grafico com o Modelo da Função de Tranferencia
plt_modelo(dataset, t_smith, f_smith)

#Definição da malha aberta = função de transferencia
malha_aberta = H

# Cria malha fechada com cada um dos métodos de controle
malha_fechada_Ziegler = cria_malha_fechada(*ziegler_nichols(k, tau, theta), malha_aberta)
malha_fechada_Cohen = cria_malha_fechada(*cohen_coon(k, tau, theta), malha_aberta)

# Simulando ambas as malhas
t1, f1 = ctrl.step_response(malha_aberta, T=tempo_sim)
t2, f2 = ctrl.step_response(malha_fechada_Ziegler, T=tempo_sim)
t3, f3 = ctrl.step_response(malha_fechada_Cohen, T=tempo_sim)

pontos_malha_aberta = analisar_resposta(t1, f1)
pontos_ziegler_nichols = analisar_resposta(t2, f2)
pontos_cohen_coon = analisar_resposta(t3,f3)

print("Malha aberta: ", pontos_malha_aberta)
print("Malha ziegler: ", pontos_ziegler_nichols)
print("Malha Cohen: ", pontos_cohen_coon)

plt_malhas(t1,f1, t2,f2, t3,f3)






