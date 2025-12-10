"""
Módulo de ajuste e detecção de formas na LousaRDP.

Formas tratadas (v1):
- Linha
- Círculo (Kåsa/Pratt simplificado)
- Retângulo (a partir de polígono pós-RDP)

A função principal é classify_shape, que recebe:
- processed_points: pontos (x, y) após pré-processamento.
- simplified_points: pontos (x, y) após RDP.
- is_closed: boolean indicando se o traço foi considerado fechado.

E retorna:
- (shape_type, shape_info), onde shape_type é uma string em:
  {"line", "circle", "rect", "polyline"}.
"""

import math
from .geometry import distance, vector, normalize, angle_cos


# ---------------------------------------------------------------------------
# Funções auxiliares de linha
# ---------------------------------------------------------------------------

def _perpendicular_distance_point_to_line(point, line_start, line_end):
    """
    Distância perpendicular de um ponto à reta definida por line_start-line_end.

    :param point: tupla (x0, y0)
    :param line_start: tupla (x1, y1)
    :param line_end: tupla (x2, y2)
    :return: distância (float)
    """
    x0, y0 = point
    x1, y1 = line_start
    x2, y2 = line_end

    dx = x2 - x1
    dy = y2 - y1

    if dx == 0 and dy == 0:
        # Segmento degenerado
        return math.hypot(x0 - x1, y0 - y1)

    # Fórmula da distância ponto-reta via área do paralelogramo
    numerator = abs(dy * x0 - dx * y0 + x2 * y1 - y2 * x1)
    denominator = math.hypot(dx, dy)

    return numerator / denominator


def line_fit_rms(points, line_start, line_end):
    """
    Calcula o erro RMS (root mean square) de distância dos pontos
    à reta definida por line_start-line_end.

    :param points: lista de (x, y)
    :param line_start: tupla (x1, y1)
    :param line_end: tupla (x2, y2)
    :return: erro RMS (float)
    """
    if not points:
        return float("inf")

    if distance(line_start, line_end) == 0.0:
        return float("inf")

    acc = 0.0
    for p in points:
        d = _perpendicular_distance_point_to_line(p, line_start, line_end)
        acc += d * d

    mean_sq = acc / len(points)
    return math.sqrt(mean_sq)


# ---------------------------------------------------------------------------
# Ajuste de círculo (Kåsa/Pratt simplificado)
# ---------------------------------------------------------------------------

def _solve_3x3(A, b):
    """
    Resolve um sistema linear 3x3 A * x = b via eliminação
    de Gauss simples (sem pivotação sofisticada).

    :param A: matriz 3x3 (lista de listas).
    :param b: vetor 3x1 (lista de 3 valores).
    :return: lista [x0, x1, x2] ou None se o sistema for singular.
    """
    # Copia para não modificar os argumentos originais
    a11, a12, a13 = A[0]
    a21, a22, a23 = A[1]
    a31, a32, a33 = A[2]
    b1, b2, b3 = b

    # Eliminação (bem direta, sem pivotação robusta)
    try:
        # Linha 2 -= (a21/a11) * Linha 1
        if a11 == 0:
            return None
        m21 = a21 / a11
        a21 = a21 - m21 * a11
        a22 = a22 - m21 * a12
        a23 = a23 - m21 * a13
        b2 = b2 - m21 * b1

        # Linha 3 -= (a31/a11) * Linha 1
        m31 = a31 / a11
        a31 = a31 - m31 * a11
        a32 = a32 - m31 * a12
        a33 = a33 - m31 * a13
        b3 = b3 - m31 * b1

        # Agora pivot em a22
        if a22 == 0:
            return None
        m32 = a32 / a22
        a32 = a32 - m32 * a22
        a33 = a33 - m32 * a23
        b3 = b3 - m32 * b2

        # Resolução de trás pra frente
        if a33 == 0:
            return None

        x3 = b3 / a33
        x2 = (b2 - a23 * x3) / a22
        x1 = (b1 - a12 * x2 - a13 * x3) / a11

        return [x1, x2, x3]
    except ZeroDivisionError:
        return None


def fit_circle_kasa(points):
    """
    Ajusta um círculo aos pontos (x, y) usando o método de Kåsa/Pratt
    simplificado (ajuste quadrático x^2 + y^2 + A x + B y + C = 0).

    :param points: lista de (x, y)
    :return: (cx, cy, r, rms_error) ou (None, None, None, None) em caso de falha.
    """
    n = len(points)
    if n < 3:
        return (None, None, None, None)

    # Somatórios
    sum_x = sum_y = 0.0
    sum_x2 = sum_y2 = 0.0
    sum_xy = 0.0
    sum_z = 0.0
    sum_xz = 0.0
    sum_yz = 0.0

    for (x, y) in points:
        z = x * x + y * y
        sum_x += x
        sum_y += y
        sum_x2 += x * x
        sum_y2 += y * y
        sum_xy += x * y
        sum_z += z
        sum_xz += x * z
        sum_yz += y * z

    # Monta sistema normal: M * [A, B, C]^T = v
    M = [
        [sum_x2, sum_xy, sum_x],
        [sum_xy, sum_y2, sum_y],
        [sum_x,  sum_y,  n],
    ]
    v = [sum_xz, sum_yz, sum_z]

    sol = _solve_3x3(M, v)
    if sol is None:
        return (None, None, None, None)

    A, B, C = sol

    # Converte parâmetros para centro (cx, cy) e raio r
    cx = -A / 2.0
    cy = -B / 2.0
    # r^2 = cx^2 + cy^2 - C
    r_sq = cx * cx + cy * cy - C

    if r_sq <= 0:
        return (None, None, None, None)

    r = math.sqrt(r_sq)

    # Calcula erro RMS radial (diferença entre raio observado e r)
    acc = 0.0
    for (x, y) in points:
        ri = math.hypot(x - cx, y - cy)
        acc += (ri - r) ** 2

    rms = math.sqrt(acc / n)

    return (cx, cy, r, rms)


# ---------------------------------------------------------------------------
# Detecção de retângulo
# ---------------------------------------------------------------------------

def detect_rectangle_from_polygon(poly_points):
    """
    Tenta detectar um retângulo a partir de um polígono (simplificado via RDP).

    Estratégia simples:
    - Remove duplicação do último ponto se for igual ao primeiro.
    - Exige exatamente 4 vértices "principais".
    - Verifica:
      - Ângulos próximos de 90° (produto escalar próximo de 0).
      - Lados opostos aproximadamente paralelos.
      - Comprimentos de lados opostos semelhantes.

    Retorna:
    - (is_rect, score, vertices)
      - is_rect: True/False.
      - score: valor de qualidade (quanto menor, mais retangular).
      - vertices: lista dos 4 vértices (se is_rect for True), ou [].
    """
    if len(poly_points) < 4:
        return (False, None, [])

    pts = list(poly_points)

    # Remove ponto final duplicado se for igual ao inicial
    if len(pts) >= 2 and pts[0] == pts[-1]:
        pts = pts[:-1]

    if len(pts) != 4:
        # v1: exigimos exatamente 4 vértices
        return (False, None, [])

    # Vetores das arestas
    v0 = vector(pts[0], pts[1])
    v1 = vector(pts[1], pts[2])
    v2 = vector(pts[2], pts[3])
    v3 = vector(pts[3], pts[0])

    lengths = [math.hypot(*v0), math.hypot(*v1), math.hypot(*v2), math.hypot(*v3)]

    # Descarta se algum lado for muito pequeno (ruído)
    min_edge_len = 10.0
    if any(L < min_edge_len for L in lengths):
        return (False, None, [])

    # Versões normalizadas dos vetores
    nv0 = normalize(v0)
    nv1 = normalize(v1)
    nv2 = normalize(v2)
    nv3 = normalize(v3)

    # Ângulos entre lados adjacentes (queremos ~90°, cos ~ 0)
    c01 = abs(angle_cos(nv0, nv1))
    c12 = abs(angle_cos(nv1, nv2))
    c23 = abs(angle_cos(nv2, nv3))
    c30 = abs(angle_cos(nv3, nv0))

    angle_penalty = c01 + c12 + c23 + c30  # 0 seria perfeito

    # Lados opostos paralelos (nv0 ~ -nv2, nv1 ~ -nv3) => cos ~ -1
    c02 = abs(angle_cos(nv0, (-nv2[0], -nv2[1])))
    c13 = abs(angle_cos(nv1, (-nv3[0], -nv3[1])))

    # Queremos c02 ~ 1 e c13 ~ 1. Penalidade é o "quanto falta" pra 1.
    parallel_penalty = (1.0 - c02) + (1.0 - c13)

    # Comprimentos de lados opostos semelhantes
    L0, L1, L2, L3 = lengths
    ratio01 = abs(L0 - L2) / max(L0, L2)
    ratio12 = abs(L1 - L3) / max(L1, L3)
    length_penalty = ratio01 + ratio12

    # Score final ponderando os componentes
    score = angle_penalty * 1.0 + parallel_penalty * 0.5 + length_penalty * 0.5

    # Threshold empírico
    if score < 1.0:
        return (True, score, pts)
    else:
        return (False, score, pts)


# ---------------------------------------------------------------------------
# Classificação geral de forma
# ---------------------------------------------------------------------------

def classify_shape(processed_points, simplified_points, is_closed):
    """
    Classifica o traço em:
    - "line"
    - "circle"
    - "rect"
    - "polyline" (nenhuma das anteriores)

    Estratégia:
    - Ajusta linha usando pontos processados e extremos como suporte.
    - Ajusta círculo com Kåsa usando pontos processados.
    - Tenta detectar retângulo a partir do polígono simplificado, se fechado.
    - Calcula "erros normalizados" e escolhe a forma com menor score <= 1.0.

    :param processed_points: lista de (x, y) após pré-processamento.
    :param simplified_points: lista de (x, y) após RDP.
    :param is_closed: boolean indicando se o traço é fechado.
    :return: (shape_type, shape_info)
    """
    shape_info = {}

    # Não há pontos suficientes
    if len(processed_points) < 2 or len(simplified_points) < 2:
        return ("polyline", shape_info)

    norm_scores = {}

    # -------------------------
    # Candidato: LINHA
    # -------------------------
    line_error = None
    if len(processed_points) >= 2:
        line_start = processed_points[0]
        line_end = processed_points[-1]
        line_error = line_fit_rms(processed_points, line_start, line_end)

        # Threshold ~ 3 pixels de erro RMS
        if line_error is not None and line_error < 3.0:
            # Normaliza erro pela tolerância
            norm_scores["line"] = line_error / 3.0
            shape_info["line"] = {
                "p0": line_start,
                "p1": line_end,
                "rms_error": line_error,
            }

    # -------------------------
    # Candidato: CÍRCULO
    # -------------------------
    circle_rel_error = None
    if len(processed_points) >= 6:  # exige um pouco mais de pontos
        cx, cy, r, rms = fit_circle_kasa(processed_points)
        if cx is not None and r > 5.0:
            # Erro relativo: RMS / raio
            circle_rel_error = rms / r
            # Threshold ~ 0.25 (25% de variação média)
            if circle_rel_error < 0.25:
                norm_scores["circle"] = circle_rel_error / 0.25
                shape_info["circle"] = {
                    "center": (cx, cy),
                    "radius": r,
                    "rms_radial_error": rms,
                    "relative_error": circle_rel_error,
                }

    # -------------------------
    # Candidato: RETÂNGULO
    # -------------------------
    rect_score = None
    if is_closed and len(simplified_points) >= 4:
        is_rect, score, vertices = detect_rectangle_from_polygon(simplified_points)
        if is_rect:
            rect_score = score
            # Threshold empírico para score final
            if rect_score < 1.0:
                norm_scores["rect"] = rect_score / 1.0
                shape_info["rect"] = {
                    "vertices": vertices,
                    "score": rect_score,
                }

    # -------------------------
    # Escolha da forma com menor erro normalizado
    # -------------------------
    if not norm_scores:
        return ("polyline", shape_info)

    best_type = None
    best_score = None

    for shape_type, score in norm_scores.items():
        if best_score is None or score < best_score:
            best_score = score
            best_type = shape_type

    # Exige score normalizado <= 1.0
    if best_score is None or best_score > 1.0:
        return ("polyline", shape_info)

    return (best_type, shape_info)