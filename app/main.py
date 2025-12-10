import sys
import pygame

from .draw import draw_grid, draw_hud, draw_strokes, draw_current_stroke
from .strokes import Stroke

# Configurações da janela
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720

# Cor de fundo (um cinza bem escuro)
BACKGROUND_COLOR = (20, 20, 20)


def main():
    # Inicializa módulos principais do pygame
    pygame.init()
    pygame.font.init()

    # Cria a janela principal
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("LousaRDP - Lousa de Desenho com Correção de Formas (Passo 2)")

    # Relógio para controlar FPS
    clock = pygame.time.Clock()

    # Fonte para o HUD
    try:
        font = pygame.font.SysFont("consolas", 18)
    except Exception:
        font = pygame.font.Font(None, 18)

    running = True

    # Estado mínimo
    mode_text = "MODO: desenho"
    epsilon_value = 10.0  # placeholder (será dinâmico nos próximos passos)
    clear_count = 0       # quantas vezes o usuário apertou C

    # Estado de traços
    strokes = []          # lista de Stroke finalizados
    current_stroke = None  # traço em andamento (Stroke ou None)

    # Cor e espessura do traço padrão (por enquanto fixos)
    stroke_color = (255, 255, 255)
    stroke_width = 3

    while running:
        # Limita o FPS a ~60 e obtém o tempo desde o último frame (em ms)
        dt_ms = clock.tick(60)

        # FPS aproximado calculado pelo pygame
        fps = clock.get_fps()

        # Trata eventos (teclado, mouse, fechar janela, etc.)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # Usuário clicou no X da janela
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    # Tecla Q: sair da aplicação
                    print("[INFO] Tecla Q pressionada - saindo da LousaRDP (Passo 2).")
                    running = False

                elif event.key == pygame.K_c:
                    # Tecla C: limpar tudo (todos os traços)
                    clear_count += 1
                    strokes.clear()
                    current_stroke = None
                    print(f"[INFO] Tecla C pressionada - clear #{clear_count}. Todos os traços foram removidos.")

                elif event.key == pygame.K_z:
                    # Tecla Z: desfazer último traço
                    if strokes:
                        removed = strokes.pop()
                        print(
                            f"[INFO] Undo (Z): removido traço com {len(removed)} pontos. "
                            f"Traços restantes: {len(strokes)}"
                        )
                    else:
                        print("[INFO] Undo (Z): nenhum traço para remover.")

            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Botão esquerdo do mouse pressionado: inicia novo traço
                if event.button == 1:
                    t = pygame.time.get_ticks() / 1000.0  # tempo em segundos
                    current_stroke = Stroke(color=stroke_color, width=stroke_width)
                    current_stroke.add_point(event.pos, t)
                    print(f"[INFO] Iniciando novo traço em {event.pos} (t={t:.3f}s)")

            elif event.type == pygame.MOUSEMOTION:
                # Mouse se movendo com botão esquerdo pressionado: adiciona pontos ao traço atual
                if current_stroke is not None and event.buttons[0]:
                    t = pygame.time.get_ticks() / 1000.0
                    current_stroke.add_point(event.pos, t)

            elif event.type == pygame.MOUSEBUTTONUP:
                # Botão esquerdo do mouse solto: finaliza traço
                if event.button == 1 and current_stroke is not None:
                    if not current_stroke.is_empty():
                        strokes.append(current_stroke)
                        print(f"[INFO] Traço finalizado com {len(current_stroke)} pontos. Total de traços: {len(strokes)}")
                    else:
                        print("[INFO] Traço vazio descartado.")
                    current_stroke = None

        # Preenche o fundo da tela
        screen.fill(BACKGROUND_COLOR)

        # Desenha o grid
        draw_grid(screen, WINDOW_WIDTH, WINDOW_HEIGHT, cell_size=32)

        # Desenha todos os traços finalizados
        draw_strokes(screen, strokes)

        # Desenha o traço atual (se existir)
        draw_current_stroke(screen, current_stroke)

        # Desenha o HUD
        draw_hud(
            surface=screen,
            font=font,
            fps=fps,
            mode_text=mode_text,
            epsilon_value=epsilon_value,
            clear_count=clear_count,
            stroke_count=len(strokes),
        )

        # Atualiza a tela
        pygame.display.flip()

    # Finaliza pygame corretamente
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
