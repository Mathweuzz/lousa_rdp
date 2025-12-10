import pygame

# Cores utilizadas na renderização
GRID_COLOR = (60, 60, 60)
HUD_TEXT_COLOR = (230, 230, 230)
HUD_BG_COLOR = (0, 0, 0)

# Cor para traços simplificados (RDP)
SIMPLIFIED_COLOR = (255, 180, 0)


def draw_grid(surface, width, height, cell_size=32):
    """
    Desenha um grid leve (linhas horizontais e verticais)
    sobre toda a área da tela.
    """
    # Linhas verticais
    for x in range(0, width, cell_size):
        pygame.draw.line(surface, GRID_COLOR, (x, 0), (x, height))

    # Linhas horizontais
    for y in range(0, height, cell_size):
        pygame.draw.line(surface, GRID_COLOR, (0, y), (width, y))


def draw_hud(
    surface,
    font,
    fps,
    mode_text,
    epsilon_value,
    clear_count,
    stroke_count,
    last_shape_text,
    snap_enabled,
    current_color_index,
    current_color,
):
    """
    Desenha o HUD (overlay) com informações de status
    no canto superior esquerdo da tela.
    """
    snap_text = "SNAP: ON" if snap_enabled else "SNAP: OFF"
    color_text = f"Cor atual: #{current_color_index + 1} {current_color}"

    lines = [
        "LousaRDP - Versão Final",
        f"FPS: {fps:5.1f}",
        mode_text,
        snap_text,
        f"epsilon (RDP): {epsilon_value:.2f}",
        f"Clears (C): {clear_count}",
        f"Traços: {stroke_count}",
        f"Última forma: {last_shape_text}",
        "Atalhos:",
        "  Q=sair | C=limpar | Z=undo | Y=redo | G=snap ON/OFF",
        "  S=salvar PNG | [ / ]=epsilon | 1..5=cor | V=modo seleção",
        color_text,
    ]

    padding = 8
    line_height = font.get_linesize()

    # Mede largura máxima
    hud_width = 0
    for line in lines:
        text_surface = font.render(line, True, HUD_TEXT_COLOR)
        hud_width = max(hud_width, text_surface.get_width())

    hud_height = line_height * len(lines) + padding * 2

    hud_rect = pygame.Rect(10, 10, hud_width + padding * 2, hud_height)

    pygame.draw.rect(surface, HUD_BG_COLOR, hud_rect)

    y = hud_rect.y + padding
    for line in lines:
        text_surface = font.render(line, True, HUD_TEXT_COLOR)
        surface.blit(text_surface, (hud_rect.x + padding, y))
        y += line_height


def _draw_point_list(surface, points, color, width):
    """
    Desenha uma lista de pontos como segmentos de linha.
    """
    if not points:
        return

    if len(points) == 1:
        p = points[0]
        if len(p) == 3:
            x, y, _ = p
        else:
            x, y = p
        pygame.draw.circle(surface, color, (int(x), int(y)), width)
        return

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

        pygame.draw.line(surface, color, (int(x1), int(y1)), (int(x2), int(y2)), width)


def _draw_single_stroke(surface, stroke):
    """
    Desenha um único traço original na tela.
    """
    _draw_point_list(surface, stroke.points, stroke.color, stroke.width)


def draw_strokes(surface, strokes):
    """
    Desenha todos os traços finalizados (originais).
    """
    for stroke in strokes:
        _draw_single_stroke(surface, stroke)


def draw_current_stroke(surface, current_stroke):
    """
    Desenha o traço atualmente em andamento (se existir), na forma original.
    """
    if current_stroke is not None:
        _draw_single_stroke(surface, current_stroke)


def draw_strokes_simplified(surface, strokes):
    """
    Desenha a versão simplificada (RDP) de todos os traços finalizados,
    em uma cor diferente, por cima dos traços originais.
    """
    for stroke in strokes:
        if stroke.simplified_points:
            width = max(1, stroke.width - 1)
            _draw_point_list(surface, stroke.simplified_points, SIMPLIFIED_COLOR, width)


def draw_shapes(surface, shapes, snap_enabled):
    """
    Desenha as formas canônicas (shapes) se o snap estiver ligado.
    """
    if not snap_enabled:
        return

    for shape in shapes:
        shape.draw(surface)
