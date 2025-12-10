"""
Funções geométricas de utilidade para a LousaRDP.

Inclui:
- Distância entre pontos.
- Vetores, produto escalar, norma, normalização.
- Cálculo de ângulo (via cosseno).
- Bounding box e área de polígono (shoelace).
"""

import math


def distance(p, q):
    """
    Distância euclidiana entre dois pontos 2D.

    :param p: tupla (x1, y1)
    :param q: tupla (x2, y2)
    :return: distância (float)
    """
    x1, y1 = p
    x2, y2 = q
    return math.hypot(x2 - x1, y2 - y1)


def vector(p, q):
    """
    Vetor q - p.

    :param p: tupla (x1, y1)
    :param q: tupla (x2, y2)
    :return: tupla (dx, dy)
    """
    x1, y1 = p
    x2, y2 = q
    return (x2 - x1, y2 - y1)


def dot(u, v):
    """
    Produto escalar entre dois vetores 2D.

    :param u: tupla (ux, uy)
    :param v: tupla (vx, vy)
    :return: escalar (float)
    """
    ux, uy = u
    vx, vy = v
    return ux * vx + uy * vy


def norm(u):
    """
    Norma (comprimento) de um vetor 2D.

    :param u: tupla (ux, uy)
    :return: comprimento (float)
    """
    ux, uy = u
    return math.hypot(ux, uy)


def normalize(u):
    """
    Normaliza um vetor 2D.

    :param u: tupla (ux, uy)
    :return: tupla (ux', uy') com norma 1, ou (0.0, 0.0) se vetor nulo.
    """
    length = norm(u)
    if length == 0:
        return (0.0, 0.0)
    ux, uy = u
    return (ux / length, uy / length)


def angle_cos(u, v):
    """
    Retorna o cosseno do ângulo entre dois vetores 2D.

    :param u: tupla (ux, uy)
    :param v: tupla (vx, vy)
    :return: cos(theta) em [-1, 1], ou 1.0 se algum vetor for nulo.
    """
    nu = norm(u)
    nv = norm(v)
    if nu == 0 or nv == 0:
        return 1.0
    return dot(u, v) / (nu * nv)


def bounding_box(points):
    """
    Calcula o bounding box axis-aligned de um conjunto de pontos.

    :param points: lista de (x, y)
    :return: (min_x, min_y, max_x, max_y)
    """
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    return (min(xs), min(ys), max(xs), max(ys))


def polygon_area(points):
    """
    Calcula a área assinada de um polígono (shoelace).
    Se o polígono não for fechado, assume uma aresta entre
    o último e o primeiro ponto.

    :param points: lista de (x, y)
    :return: área assinada (float). Área geométrica = abs(área).
    """
    if len(points) < 3:
        return 0.0

    area = 0.0
    n = len(points)

    for i in range(n):
        x1, y1 = points[i]
        x2, y2 = points[(i + 1) % n]
        area += x1 * y2 - x2 * y1

    return area / 2.0