import pygame

# Cores utilizadas na renderização
GRID_COLOR = (60, 60, 60)
HUD_TEXT_COLOR = (230, 230, 230)
HUD_BG_COLOR = (0, 0, 0)

# Cor para traços simplificados
SIMPLIFIED_COLOR = (255, 180, 0)


def draw_grid(surface, width, height, cell_size=32):
    """
    Desenha um grid leve (linhas horizontais e verticais)
    sobre toda a área da tela.

    :param surface: Surface do pygame onde será desenhado.
    :param width: Largura da janela em pixels.
    :param height: Altura da janela em pixels.
    :param cell_size: Espaçamento entre linhas do grid.
    """
    # Linhas verticais
    for x in range(0, width, cell_size):
        pygame.draw.line(surface, GRID_COLOR, (x, 0), (x, height))

    # Linhas horizontais
    for y in range(0, height, cell_size):
        pygame.draw.line(surface, GRID_COLOR, (0, y), (width, y))


def draw_hud(surface, font, fps, mode_text, epsilon_value, clear_count, stroke_count):
    """
    Desenha o HUD (overlay) com informações de status
    no canto superior esquerdo da tela.

    :param surface: Surface do pygame onde será desenhado.
    :param font: Fonte do pygame já carregada.
    :param fps: Valor atual de FPS (float).
    :param mode_text: Texto representando o modo atual (ex.: "MODO: desenho").
    :param epsilon_value: Valor atual de epsilon (usado pelo RDP).
    :param clear_count: Quantidade de vezes que o usuário apertou C (clear).
    :param stroke_count: Quantidade de traços finalizados.
    """
    # Linhas de texto que serão mostradas no HUD
    lines = [
        "LousaRDP - Passo 3",
        f"FPS: {fps:5.1f}",
        mode_text,
        f"epsilon (RDP): {epsilon_value:.2f}",
        f"Clears (C): {clear_count}",
        f"Traços: {stroke_count}",
        "Atalhos: Q=sair | C=limpar | Z=undo | [ / ] = epsilon",
    ]

    padding = 8
    line_height = font.get_linesize()

    # Primeiro medimos a largura máxima do texto para dimensionar o retângulo de fundo
    hud_width = 0
    for line in lines:
        text_surface = font.render(line, True, HUD_TEXT_COLOR)
        if text_surface.get_width() > hud_width:
            hud_width = text_surface.get_width()

    hud_height = line_height * len(lines) + padding * 2

    # Retângulo de fundo do HUD (no canto superior esquerdo)
    hud_rect = pygame.Rect(10, 10, hud_width + padding * 2, hud_height)

    # Desenha o fundo do HUD
    pygame.draw.rect(surface, HUD_BG_COLOR, hud_rect)

    # Desenha cada linha de texto
    y = hud_rect.y + padding
    for line in lines:
        text_surface = font.render(line, True, HUD_TEXT_COLOR)
        surface.blit(text_surface, (hud_rect.x + padding, y))
        y += line_height


def _draw_point_list(surface, points, color, width):
    """
    Desenha uma lista de pontos como segmentos de linha.

    :param surface: Surface do pygame onde será desenhado.
    :param points: lista de pontos (x, y) ou (x, y, t).
    :param color: tupla (R, G, B) da cor.
    :param width: espessura da linha.
    """
    if not points:
        return

    # Se tiver só um ponto, desenha um pequeno círculo
    if len(points) == 1:
        p = points[0]
        if len(p) == 3:
            x, y, _ = p
        else:
            x, y = p
        pygame.draw.circle(surface, color, (x, y), width)
        return

    # Caso geral: desenha segmentos entre pontos consecutivos
    for i in range(1, len(points)):
        p1 = points[i - 1]
        p2 = points[i]

        if len(p1) == 3:
            x1, y1, _ = p1
        else:
            x1, y1 = p1

        if len(p2) == 3:
            x2, y2, _ = p2
        else:
            x2, y2 = p2

        pygame.draw.line(surface, color, (x1, y1), (x2, y2), width)


def _draw_single_stroke(surface, stroke):
    """
    Desenha um único traço original na tela.

    :param surface: Surface do pygame onde será desenhado.
    :param stroke: Instância de Stroke (definida em app.strokes).
    """
    _draw_point_list(surface, stroke.points, stroke.color, stroke.width)


def draw_strokes(surface, strokes):
    """
    Desenha todos os traços finalizados (originais).

    :param surface: Surface do pygame onde será desenhado.
    :param strokes: Lista de instâncias de Stroke.
    """
    for stroke in strokes:
        _draw_single_stroke(surface, stroke)


def draw_current_stroke(surface, current_stroke):
    """
    Desenha o traço atualmente em andamento (se existir), na forma original.

    :param surface: Surface do pygame onde será desenhado.
    :param current_stroke: Instância de Stroke ou None.
    """
    if current_stroke is not None:
        _draw_single_stroke(surface, current_stroke)


def draw_strokes_simplified(surface, strokes):
    """
    Desenha a versão simplificada (RDP) de todos os traços finalizados,
    em uma cor diferente, por cima dos traços originais.

    :param surface: Surface do pygame onde será desenhado.
    :param strokes: Lista de instâncias de Stroke.
    """
    for stroke in strokes:
        if stroke.simplified_points:
            # Usa uma largura ligeiramente menor ou igual
            width = max(1, stroke.width - 1)
            _draw_point_list(surface, stroke.simplified_points, SIMPLIFIED_COLOR, width)
