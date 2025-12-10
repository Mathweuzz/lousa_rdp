# LousaRDP

Lousa de desenho com correção de formas (Ramer–Douglas–Peucker + detecção de primitivas).

## Passo 4

Este estágio do projeto implementa:

- Tudo dos passos anteriores (1–3):
  - Janela pygame 1280×720 com grid e HUD.
  - Captura de traços livres com o mouse.
  - Undo por traço (`Z`) e clear geral (`C`).
  - Implementação do algoritmo Ramer–Douglas–Peucker (RDP) para simplificar traços.
- Pré-processamento de traços em `app/strokes.py`:
  1. Remoção de pontos duplicados consecutivos.
  2. Detecção de traço fechado (distância entre início e fim <= limiar).
  3. Fechamento opcional do traço (adicionando o primeiro ponto ao final).
  4. Reamostragem leve por comprimento de arco, com espaçamento alvo em pixels.
- Cada `Stroke` armazena:
  - `points`: pontos originais `(x, y, t)`.
  - `processed_points`: pontos `(x, y)` após pré-processamento.
  - `simplified_points`: pontos `(x, y)` após RDP.
  - `is_closed`: flag indicando se o traço foi considerado fechado.
- O RDP passa a operar sobre os pontos pré-processados, resultando em:
  - Polígonos mais limpos para traços fechados.
  - Comportamento mais estável em loops (ex.: círculos desenhados à mão).