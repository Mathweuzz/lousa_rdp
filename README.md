# LousaRDP

Lousa de desenho com correção de formas (Ramer–Douglas–Peucker + detecção de primitivas) implementada em Python + pygame (sem numpy, sem opencv).

## Funcionalidades principais

- Janela pygame 1280×720 com:
  - Fundo em grid.
  - HUD com FPS, modo, epsilon, clears, traços, forma detectada, cor atual e atalhos.
- Captura de traços:
  - Botão esquerdo do mouse: pressione, arraste e solte para desenhar.
  - Cada traço é armazenado com pontos `(x, y, t)`.
- Pré-processamento de traços:
  - Remoção de pontos duplicados consecutivos.
  - Detecção de traço fechado (início ≈ fim).
  - Fechamento opcional para loops.
  - Reamostragem por comprimento de arco (pontos mais uniformemente espaçados).
- Simplificação com **Ramer–Douglas–Peucker (RDP)**:
  - Implementação própria em `app/rdp.py`.
  - Epsilon ajustável em tempo real.
  - Traços simplificados são desenhados em cor diferente.
- Detecção de formas (v1) em `app/fit.py`:
  - **Linha**:
    - Erro RMS em relação à reta definida pelos extremos.
  - **Círculo** (Kåsa/Pratt simplificado, sem numpy):
    - Centro `(cx, cy)`, raio `r`, erro radial RMS.
  - **Retângulo**:
    - A partir do polígono pós-RDP:
      - ~4 vértices, ângulos ~90°, lados opostos ~paralelos e com comprimentos semelhantes.
  - Classificação final:
    - `"line"`, `"circle"`, `"rect"` ou `"polyline"`.
- Shapes canônicos em `app/shapes.py`:
  - `LineShape`, `CircleShape`, `RectShape` (axis-aligned), `PolylineShape`.
  - Cada shape sabe desenhar-se e mover-se.
- Snap (ink-to-shape):
  - Ao soltar o traço:
    1. Pré-processamento.
    2. RDP.
    3. Classificação de forma.
    4. Criação de shape canônico correspondente.
  - Os shapes são desenhados por cima dos traços/brutos.
  - Pode ser ligado/desligado.

## Controles

- **Desenho**:
  - Mouse esquerdo: desenhar traços.
- **Modo**:
  - `V` — alternar:
    - `MODO: desenho`
    - `MODO: seleção`
- **Seleção e movimento (modo seleção)**:
  - Clique com mouse esquerdo em cima de um shape canônico para selecioná-lo.
  - Arraste para mover o shape.
- **Snap e epsilon**:
  - `G` — liga/desliga snap (shapes canônicos).
  - `[` / `]` — diminuir/aumentar `epsilon` usado pelo RDP.
- **Cores**:
  - `1`..`5` — altera a cor atual (novos traços/shapes).
- **Undo/Redo, limpar, salvar**:
  - `Z` — undo (remove último traço + shape, empilha em redo).
  - `Y` — redo (restaura de redo).
  - `C` — limpar tudo (traços, shapes, redo).
  - `S` — salvar PNG da tela atual em `exports/`.
- **Sair**:
  - `Q` — sair da aplicação.
  - Fechar a janela no “X” também encerra.