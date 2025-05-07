# Controlador PID para branqueamento térmico de glicerina

*Grupo 2  -  Integrantes: Júlia de Freitas e Gabriella*

O projeto busca aplicar um sistema controlado PID para o controle da temperatura do procasso de branqueamento térmico da glicerina.

## Etapas

1) Analise do conjunto de dados

  - Variavel de tempo: Tempo (s)
  - Variavel controlada: Temperatura (°C) 
  - Variavel observada: Resultado Fisico (°C) 

  Abaixo é possivel observa os dados do sistema:

  ![alt text](image.png)

2) Aplicação dos Metodos de Sundaresan e Smith para calculo de K, 𝜏 e θ

  Neste cenário o método de smith foi escolhido pois é oque mais se assemelha ao comportamento do sistema e também por possuir maior indide de EQM.

  ![alt text](image-1.png)

3) Aplicação de ajustes fino para aproximação satisfatória

  Apesar dos valores da função de Smith já serem satisfatórios, foi realizado ajustes finos para verificar possiibilidade de melhore no sistema.
  como pode ser obsesrvado a seguir, houve uma sutil melhora no modelo:
  ![alt text](image-2.png)

4) Implementação dos métodos de sintonia Ziegler-Nichols e Cohen-Coon para calculo dos parametros do PID

  
5) Implementação do controle PID


6) Comparação entre os sistemas de malha aberta e fechada 
  ![alt text](image-3.png)

