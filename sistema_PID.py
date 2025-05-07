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

def funcao_transferencia(k, tau, theta, t, ordem_pade=1):
  """  Gera a função de transferência de um sistema FOPDT  """

  # Parte sem atraso
  H_sem_atraso = ctrl.tf([k], [tau, 1])

  # Aproximação de Padé para o atraso
  num_pade, den_pade = ctrl.pade(theta, ordem_pade)
  atraso_pade = ctrl.tf(num_pade, den_pade)

  # Combinando
  funcao = ctrl.series(atraso_pade, H_sem_atraso)

  # Simula H em malha aberta
  H_malha_aberta =  ctrl.step_response(funcao, T=t)
  return funcao, H_malha_aberta

def ziegler_nichols(k, tau, theta):
    Kp = 1.2 * tau / (k * theta)
    ti = 2 * theta
    td = 0.5 * theta
    Ki = Kp / ti
    Kd = Kp * td
    print("\n\nk, tau, theta em ziegle nichols: ", Kp, Ki, Kd)
    return Kp, Ki, Kd, ti, td

def cohen_coon(K, tau, theta):
    if tau == 0 or theta == 0 or K == 0:
        raise ValueError("K, tau e theta devem ser diferentes de zero")
    
    kp = (tau / (K * theta)) * ((16 * tau + 3 * theta) / (12 * tau))
    ti = theta * ((32 + 6 * (theta / tau)) / (13 + 8 * (theta / tau)))
    td = (4 * theta) / (11 + 2 * (theta / tau))

    # Conversão para forma padrão do PID
    ki = kp / ti
    kd = kp * td

    return kp,ki,kd,ti,td

def cria_malha_fechada(kp, ki, kd, malha_aberta,setpoint, t):
   # Cria o controlador PID
  PID = ctrl.tf([kd, kp, ki], [1, 0])  # Forma: Kp + Ki/s + Kd*s

  # Fecha a malha com realimentação
  funcao = ctrl.feedback(PID * (malha_aberta), 1) 
  h_malha_fechada = ctrl.step_response(funcao * setpoint, T=t)

  return funcao, h_malha_fechada

def analisar_parametros(t, f, ref=1.0, tolerancia=0.02):
    f_final = f[-1]
    
    # Tempo de subida: de 10% a 90% do valor final
    idx_10 = np.argmax(f >= 0.1 * f_final)
    idx_90 = np.argmax(f >= 0.9 * f_final)
    tempo_subida = t[idx_90] - t[idx_10]

    # Tempo de acomodação: quando entra e permanece dentro da faixa de tolerância
    superior = f_final * (1 + tolerancia)
    inferior = f_final * (1 - tolerancia)
    for i in range(len(f)-1, -1, -1):
        if f[i] > superior or f[i] < inferior:
            tempo_acomodacao = t[i+1]
            break
    else:
        tempo_acomodacao = 0  # Se nunca saiu, já estava acomodado

    # Erro em regime permanente
    erro_regime = abs(ref - f_final)

    # Pico máximo (overshoot)
    pico_maximo = np.max(f)
    tempo_pico = t[np.argmax(f)]
    overshoot_percent = ((pico_maximo - f_final) / f_final) * 100 if f_final != 0 else 0

    return tempo_subida, tempo_acomodacao, erro_regime, pico_maximo, tempo_pico, overshoot_percent


'''
# Carrega o dataset
dataset = load_dataset()

# Mostra os dados iniciais 
plt_dataset(dataset)

# Calculo pelo metodo de Smith
k, tau, theta = metodo_smith(dataset['Tempo'].values, dataset['Resultado Fisico'].values)

t = dataset['Tempo'].astype(float).values

# Calculo da func. de Tranferencia
funcao_H, malha_aberta = funcao_transferencia(k, tau, theta, t)

# Grafico com o Modelo da Função de Tranferencia
plt_modelo(dataset, *malha_aberta)

setpoint = 100 #media dos valores da entrada

# Malha fechada Ziegler Nichols
kp, ki, kd, ti, td = ziegler_nichols(k, tau, theta)
funcao_Ziegler, malha_fechada_Ziegler = cria_malha_fechada(kp, ki, kd, funcao_H, setpoint, t)

# Malha fechada Cohen Coon
kp, ki, kd, ti, td = cohen_coon(k, tau, theta)
funcao_Cohen, malha_fechada_Cohen = cria_malha_fechada(kp, ki, kd, funcao_H, setpoint, t)

pontos_malha_aberta = analisar_parametros(*malha_aberta)
pontos_ziegler_nichols = analisar_parametros(*malha_fechada_Ziegler)
pontos_cohen_coon = analisar_parametros(*malha_fechada_Cohen)

print("Malha aberta: ", pontos_malha_aberta)
print("Malha ziegler: ", pontos_ziegler_nichols)
print("Malha Cohen: ", pontos_cohen_coon)

plt_malhas(*malha_aberta, *malha_fechada_Ziegler, *malha_fechada_Cohen)


'''