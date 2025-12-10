import pygame

# Cores utlizadas na renderização
GRID_COLOR = (60, 60, 60)
HUD_TEXT_COLOR = (230, 230, 230)
HUD_BG_COLOR = (0, 0, 0)

def draw_grid(surface, width, height, cell_size=32):
    """
    Desenha um grid leve (linhas horizontais e verticais)
    sobre toda a área da tela.

    :param surface: Surface do pygame onde será desenhado.
    :param width: Largura da janela em pixels.
    :param height: Altura da janela em pixels.
    :param cell_size: Espaçamento entre linhas do grid.
    """

    # linhas verticais
    for x in range(0, width, cell_size):
        pygame.draw.line(surface, GRID_COLOR, (x, 0), (x, height))

    # linhas horizontais
    for y in range(0, height, cell_size):
        pygame.draw.line(surface, GRID_COLOR, (0, y), (width, y))

def draw_hud(surface, font, fps, mode_text, epsilon_value, clear_count):
    """
    Desenha o HUD (overlay) com informações de status
    no canto superior esquerdo da tela.

    :param surface: Surface do pygame onde será desenhado.
    :param font: Fonte do pygame já carregada.
    :param fps: Valor atual de FPS (float).
    :param mode_text: Texto representando o modo atual (ex.: "MODO: desenho").
    :param epsilon_value: Valor atual de epsilon (placeholder neste passo).
    :param clear_count: Quantidade de vezes que o usuário apertou C (clear).
    """
    # linhas de texto que serão mostradas no HUD 
    lines = [
        "LousaRPD - Passo 1",
        f"FPS: {fps:5.1f}",
        mode_text,
        f"epsilon (placeholder): {epsilon_value:.2f}",
        f"Clears (C): {clear_count}",
        "Atalhos: Q = sair | C = limpar",
    ]

    padding = 8
    line_height = font.get_linesize()

    # Primeiro medimos a largura do texto para dimensionar o retângulo de fundo
    hud_width = 0
    for line in lines:
        text_surface = font.render(line, True, HUD_TEXT_COLOR)
        if text_surface.get_width() > hud_width:
            hud_width = text_surface.get_width()

    hud_height = line_height * len(lines) + padding * 2

    # retangulo de fundo do HUD (no canto superior esquerdo)
    hud_rect = pygame.Rect(10, 10, hud_width + padding * 2, hud_height)

    # desenha cada linha de texto
    y = hud_rect.y  + padding
    for line in lines:
        text_surface = font.render(line, True, HUD_TEXT_COLOR)
        surface.blit(text_surface, (hud_rect.x + padding, y))
        y += line_height