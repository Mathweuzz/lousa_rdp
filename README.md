# LousaRDP

Lousa de desenho com correção de formas (Ramer–Douglas–Peucker + detecção de primitivas).

## Passo 5

Este estágio do projeto implementa:

- Tudo dos passos anteriores (1–4):
  - Janela pygame 1280×720 com grid e HUD.
  - Captura de traços livres com o mouse.
  - Undo por traço (`Z`) e clear geral (`C`).
  - Implementação do algoritmo Ramer–Douglas–Peucker (RDP) para simplificar traços.
  - Pré-processamento: remoção de duplicatas, detecção de fechamento e reamostragem por comprimento de arco.
- Módulo `app/geometry.py`:
  - Distâncias, vetores, produto escalar, norma, bounding box, área de polígono etc.
- Módulo `app/fit.py`:
  - Ajuste de linha: erro RMS de distância dos pontos à reta definida pelos extremos.
  - Ajuste de círculo (Kåsa/Pratt simplificado) sem numpy:
    - Cálculo de centro, raio e erro radial RMS.
  - Detecção de retângulo:
    - A partir do polígono pós-RDP.
    - ~4 vértices, ângulos ~90°, lados opostos ~paralelos e comprimentos semelhantes.
  - Função `classify_shape(...)` que decide entre:
    - `"line"`, `"circle"`, `"rect"` ou `"polyline"`.
- Cada `Stroke` passa a armazenar:
  - `processed_points`, `simplified_points`, `is_closed`.
  - `detected_shape_type`: tipo de forma detectada.
  - `detected_shape_info`: dicionário com parâmetros da forma.
- HUD:
  - Exibe a **última forma detectada** (`Última forma: ...`).