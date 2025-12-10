import sys
import pygame

from draw import draw_grid, draw_hud

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
    pygame.display.set_caption("LousaRDP - Lousa de Desenho com Correção de Formas (Passo 1)")

    # Relógio para controlar FPS
    clock = pygame.time.Clock()

    # Fonte para o HUD
    # Tenta usar uma fonte monoespaçada (Consolas); se não existir, cai para a default
    try:
        font = pygame.font.SysFont("consolas", 18)
    except Exception:
        font = pygame.font.Font(None, 18)

    running = True

    # Estado mínimo para o Passo 1
    mode_text = "MODO: desenho"
    epsilon_value = 10.0  # placeholder (será dinâmico nos próximos passos)
    clear_count = 0       # quantas vezes o usuário apertou C

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
                    print("[INFO] Tecla Q pressionada - saindo da LousaRDP (Passo 1).")
                    running = False

                elif event.key == pygame.K_c:
                    # Tecla C: limpar estado
                    clear_count += 1
                    # Neste passo, não temos desenhos permanentes,
                    # então "limpar" é apenas resetar contadores/estado.
                    print(f"[INFO] Tecla C pressionada - clear #{clear_count}")

        # Preenche o fundo da tela
        screen.fill(BACKGROUND_COLOR)

        # Desenha o grid
        draw_grid(screen, WINDOW_WIDTH, WINDOW_HEIGHT, cell_size=32)

        # Desenha o HUD
        draw_hud(
            surface=screen,
            font=font,
            fps=fps,
            mode_text=mode_text,
            epsilon_value=epsilon_value,
            clear_count=clear_count,
        )

        # Atualiza a tela
        pygame.display.flip()

    # Finaliza pygame corretamente
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
