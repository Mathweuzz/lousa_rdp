import os
import sys
from datetime import datetime

import pygame

from .draw import (
    draw_grid,
    draw_hud,
    draw_strokes,
    draw_current_stroke,
    draw_strokes_simplified,
    draw_shapes,
)
from .strokes import (
    Stroke,
    preprocess_points_for_rdp,
)
from .rdp import rdp
from .fit import classify_shape
from .shapes import LineShape, CircleShape, RectShape, PolylineShape

# Configurações da janela
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720

# Cor de fundo (um cinza bem escuro)
BACKGROUND_COLOR = (20, 20, 20)

# Limites e passo de variação do epsilon (RDP)
EPSILON_MIN = 1.0
EPSILON_MAX = 200.0
EPSILON_STEP = 2.0

# Parâmetros de pré-processamento
CLOSE_THRESHOLD_PX = 20.0
TARGET_SPACING_PX = 5.0

# Diretório de exportação de imagens
EXPORT_DIR = "exports"

# Paleta de cores (1..5)
COLOR_PALETTE = [
    (255, 255, 255),  # 1: branco
    (255, 0, 0),      # 2: vermelho
    (0, 255, 0),      # 3: verde
    (0, 128, 255),    # 4: azul claro
    (255, 255, 0),    # 5: amarelo
]


def save_screenshot(surface):
    """
    Salva a surface atual em um arquivo PNG dentro de exports/.
    """
    os.makedirs(EXPORT_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"lousa_{timestamp}.png"
    path = os.path.join(EXPORT_DIR, filename)
    try:
        pygame.image.save(surface, path)
        print(f"[INFO] Screenshot salvo em {path}")
    except Exception as exc:
        print(f"[ERRO] Falha ao salvar screenshot em {path}: {exc}")


def create_shape_from_classification(
    shape_type,
    shape_info,
    simplified_points,
    processed_points,
    is_closed,
    color,
    width,
):
    """
    Cria uma instância de Shape (LineShape, CircleShape, RectShape, PolylineShape)
    a partir do resultado da classificação.

    Se shape_type for 'polyline' ou não tivermos informações suficientes,
    cria uma PolylineShape com os pontos simplificados.
    """
    # Fallback: pontos para a polilinha
    if simplified_points:
        poly_points = simplified_points
    elif processed_points:
        poly_points = processed_points
    else:
        poly_points = []

    if shape_type == "line" and "line" in shape_info:
        info = shape_info["line"]
        p0 = info["p0"]
        p1 = info["p1"]
        return LineShape(p0, p1, color=color, width=width)

    if shape_type == "circle" and "circle" in shape_info:
        info = shape_info["circle"]
        center = info["center"]
        radius = info["radius"]
        return CircleShape(center, radius, color=color, width=width)

    if shape_type == "rect" and "rect" in shape_info:
        info = shape_info["rect"]
        vertices = info["vertices"]
        if vertices:
            xs = [p[0] for p in vertices]
            ys = [p[1] for p in vertices]
            min_x = min(xs)
            max_x = max(xs)
            min_y = min(ys)
            max_y = max(ys)
            w = max_x - min_x
            h = max_y - min_y
            return RectShape((min_x, min_y), w, h, color=color, width=width)

    # Caso geral: polilinha simplificada
    return PolylineShape(poly_points, is_closed=is_closed, color=color, width=width)


def main():
    # Inicializa módulos principais do pygame
    pygame.init()
    pygame.font.init()

    # Cria a janela principal
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("LousaRDP - Versão Final")

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
    epsilon_value = 10.0  # usado pelo RDP
    clear_count = 0

    # Estado de traços e shapes
    strokes = []           # lista de Stroke finalizados
    shapes = []            # lista de Shapes canônicos
    redo_stack = []        # pilha para redo (tuplas (Stroke, Shape))
    current_stroke = None  # traço em andamento

    # Texto com a última forma detectada
    last_shape_text = "N/A"

    # Snap ligado/desligado
    snap_enabled = True

    # Paleta de cores
    current_color_index = 0  # índice em COLOR_PALETTE
    stroke_color = COLOR_PALETTE[current_color_index]
    stroke_width = 3

    # Seleção
    selected_shape = None
    last_mouse_pos = None

    while running:
        dt_ms = clock.tick(60)
        fps = clock.get_fps()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                # Saída
                if event.key == pygame.K_q:
                    print("[INFO] Tecla Q pressionada - saindo da LousaRDP (Versão Final).")
                    running = False

                # Clear geral
                elif event.key == pygame.K_c:
                    clear_count += 1
                    strokes.clear()
                    shapes.clear()
                    redo_stack.clear()
                    current_stroke = None
                    selected_shape = None
                    last_mouse_pos = None
                    last_shape_text = "N/A"
                    print(f"[INFO] Tecla C pressionada - clear #{clear_count}. Tudo removido.")

                # Undo
                elif event.key == pygame.K_z:
                    if strokes and shapes:
                        removed_stroke = strokes.pop()
                        removed_shape = shapes.pop()
                        redo_stack.append((removed_stroke, removed_shape))
                        print(
                            f"[INFO] Undo (Z): removido traço com "
                            f"{len(removed_stroke.points)} pontos originais. "
                            f"Traços restantes: {len(strokes)}"
                        )
                        if strokes and strokes[-1].detected_shape_type:
                            last_shape_text = strokes[-1].detected_shape_type.upper()
                        else:
                            last_shape_text = "N/A"
                    else:
                        print("[INFO] Undo (Z): nada para desfazer.")

                # Redo
                elif event.key == pygame.K_y:
                    if redo_stack:
                        restored_stroke, restored_shape = redo_stack.pop()
                        strokes.append(restored_stroke)
                        shapes.append(restored_shape)
                        if restored_stroke.detected_shape_type:
                            last_shape_text = restored_stroke.detected_shape_type.upper()
                        else:
                            last_shape_text = "N/A"
                        print(
                            f"[INFO] Redo (Y): restaurado traço com "
                            f"{len(restored_stroke.points)} pontos originais. "
                            f"Total de traços: {len(strokes)}"
                        )
                    else:
                        print("[INFO] Redo (Y): nada para refazer.")

                # Ajuste de epsilon
                elif event.key == pygame.K_LEFTBRACKET:
                    old = epsilon_value
                    epsilon_value = max(EPSILON_MIN, epsilon_value - EPSILON_STEP)
                    print(f"[INFO] Epsilon diminuído: {old:.2f} -> {epsilon_value:.2f}")

                elif event.key == pygame.K_RIGHTBRACKET:
                    old = epsilon_value
                    epsilon_value = min(EPSILON_MAX, epsilon_value + EPSILON_STEP)
                    print(f"[INFO] Epsilon aumentado: {old:.2f} -> {epsilon_value:.2f}")

                # Snap ON/OFF
                elif event.key == pygame.K_g:
                    snap_enabled = not snap_enabled
                    print(f"[INFO] Snap {'ativado' if snap_enabled else 'desativado'} (G).")

                # Salvar PNG
                elif event.key == pygame.K_s:
                    save_screenshot(screen)

                # Paleta de cores 1..5
                elif event.key in (pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5):
                    key_to_index = {
                        pygame.K_1: 0,
                        pygame.K_2: 1,
                        pygame.K_3: 2,
                        pygame.K_4: 3,
                        pygame.K_5: 4,
                    }
                    idx = key_to_index[event.key]
                    current_color_index = idx
                    stroke_color = COLOR_PALETTE[current_color_index]
                    print(f"[INFO] Cor atual alterada para índice {current_color_index + 1}: {stroke_color}")

                # Modo seleção / desenho
                elif event.key == pygame.K_v:
                    if mode_text.startswith("MODO: seleção"):
                        mode_text = "MODO: desenho"
                        selected_shape = None
                        last_mouse_pos = None
                        print("[INFO] Modo alterado para DESENHO (V).")
                    else:
                        mode_text = "MODO: seleção"
                        selected_shape = None
                        last_mouse_pos = None
                        print("[INFO] Modo alterado para SELEÇÃO (V).")

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if mode_text.startswith("MODO: seleção"):
                        # Seleção de shape
                        clicked_pos = event.pos
                        selected_shape = None
                        # Percorre shapes do topo para o fundo
                        for shape in reversed(shapes):
                            if shape.contains_point(clicked_pos):
                                selected_shape = shape
                                last_mouse_pos = clicked_pos
                                print("[INFO] Shape selecionado para mover.")
                                break
                    else:
                        # MODO desenho – inicia traço
                        t = pygame.time.get_ticks() / 1000.0
                        current_stroke = Stroke(color=stroke_color, width=stroke_width)
                        current_stroke.add_point(event.pos, t)
                        print(f"[INFO] Iniciando novo traço em {event.pos} (t={t:.3f}s)")

            elif event.type == pygame.MOUSEMOTION:
                if event.buttons[0]:
                    if mode_text.startswith("MODO: seleção"):
                        # Mover shape selecionado
                        if selected_shape is not None and last_mouse_pos is not None:
                            cur_pos = event.pos
                            dx = cur_pos[0] - last_mouse_pos[0]
                            dy = cur_pos[1] - last_mouse_pos[1]
                            selected_shape.move(dx, dy)
                            last_mouse_pos = cur_pos
                    else:
                        # MODO desenho – atualiza traço em andamento
                        if current_stroke is not None:
                            t = pygame.time.get_ticks() / 1000.0
                            current_stroke.add_point(event.pos, t)

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    if mode_text.startswith("MODO: seleção"):
                        # Solta shape
                        selected_shape = None
                        last_mouse_pos = None
                    else:
                        # Finaliza traço de desenho
                        if current_stroke is not None and not current_stroke.is_empty():
                            xy_points = current_stroke.get_xy_points()

                            # Pré-processamento
                            processed_xy, is_closed = preprocess_points_for_rdp(
                                xy_points,
                                close_threshold=CLOSE_THRESHOLD_PX,
                                target_spacing=TARGET_SPACING_PX,
                            )
                            current_stroke.set_processed_points(processed_xy, is_closed)

                            if len(processed_xy) >= 2:
                                rdp_input = processed_xy
                            else:
                                rdp_input = xy_points

                            # RDP
                            if len(rdp_input) >= 2:
                                simplified = rdp(rdp_input, epsilon_value)
                            else:
                                simplified = rdp_input

                            current_stroke.set_simplified_points(simplified)

                            # Classificação de forma
                            shape_type, shape_info = classify_shape(
                                processed_points=processed_xy,
                                simplified_points=simplified,
                                is_closed=is_closed,
                            )
                            current_stroke.set_detected_shape(shape_type, shape_info)
                            last_shape_text = shape_type.upper() if shape_type else "N/A"

                            # Cria shape canônico
                            shape_obj = create_shape_from_classification(
                                shape_type=shape_type,
                                shape_info=shape_info,
                                simplified_points=simplified,
                                processed_points=processed_xy,
                                is_closed=is_closed,
                                color=stroke_color,
                                width=stroke_width,
                            )

                            strokes.append(current_stroke)
                            shapes.append(shape_obj)
                            # Novo traço invalida a pilha de redo
                            redo_stack.clear()

                            print(
                                f"[INFO] Traço finalizado. "
                                f"Originais: {len(xy_points)} pts | "
                                f"Pré-processados: {len(processed_xy)} pts | "
                                f"Simplificados (RDP): {len(simplified)} pts | "
                                f"Fechado: {is_closed} | "
                                f"Forma detectada: {shape_type}."
                            )
                        elif current_stroke is not None:
                            print("[INFO] Traço vazio descartado.")
                        current_stroke = None

        # Desenho da cena
        screen.fill(BACKGROUND_COLOR)
        draw_grid(screen, WINDOW_WIDTH, WINDOW_HEIGHT, cell_size=32)

        # Traços originais + traço atual + polilinhas simplificadas
        draw_strokes(screen, strokes)
        draw_current_stroke(screen, current_stroke)
        draw_strokes_simplified(screen, strokes)

        # Shapes canônicos (snap ON)
        draw_shapes(screen, shapes, snap_enabled=snap_enabled)

        # HUD
        draw_hud(
            surface=screen,
            font=font,
            fps=fps,
            mode_text=mode_text,
            epsilon_value=epsilon_value,
            clear_count=clear_count,
            stroke_count=len(strokes),
            last_shape_text=last_shape_text,
            snap_enabled=snap_enabled,
            current_color_index=current_color_index,
            current_color=stroke_color,
        )

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
