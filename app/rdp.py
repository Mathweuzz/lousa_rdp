"""
Implementação pura do algoritmo Ramer–Douglas–Peucker (RDP),
sem dependências externas além da biblioteca padrão.

O objetivo é simplificar uma polilinha (lista de pontos 2D) de forma
a preservar a forma geral, removendo pontos redundantes.

Entrada:
- points: lista de (x, y)
- epsilon: distância máxima permitida entre o segmento simplificado
           e os pontos originais.

Saída:
- nova lista de (x, y) com menos pontos (ou igual se não houver o que simplificar).
"""

import math


def _perpendicular_distance(point, start, end):
    """
    Calcula a distância perpendicular do ponto à linha definida por start-end.

    :param point: tupla (x0, y0)
    :param start: tupla (x1, y1)
    :param end: tupla (x2, y2)
    :return: distância (float)
    """
    x0, y0 = point
    x1, y1 = start
    x2, y2 = end

    dx = x2 - x1
    dy = y2 - y1

    # Se o segmento é degenerado (start == end), usa distância euclidiana simples
    if dx == 0 and dy == 0:
        return math.hypot(x0 - x1, y0 - y1)

    # Fórmula da distância ponto-reta via área do paralelogramo
    numerator = abs(dy * x0 - dx * y0 + x2 * y1 - y2 * x1)
    denominator = math.hypot(dx, dy)

    return numerator / denominator


def rdp(points, epsilon):
    """
    Aplica o algoritmo Ramer–Douglas–Peucker em uma lista de pontos 2D.

    :param points: lista de pontos [(x, y), ...]
    :param epsilon: tolerância de distância. Valores maiores resultam
                    em mais simplificação.
    :return: nova lista de pontos simplificados [(x, y), ...]
    """
    if not points:
        return []

    if len(points) < 3:
        # Com 0, 1 ou 2 pontos não há o que simplificar
        return list(points)

    if epsilon <= 0:
        # Epsilon não positivo => não simplifica
        return list(points)

    # Encontra o ponto com maior distância em relação ao segmento start-end
    start = points[0]
    end = points[-1]

    max_distance = 0.0
    index_of_max = -1

    for i in range(1, len(points) - 1):
        d = _perpendicular_distance(points[i], start, end)
        if d > max_distance:
            max_distance = d
            index_of_max = i

    # Se a maior distância é maior que epsilon, recursão
    if max_distance > epsilon and index_of_max != -1:
        # Parte esquerda (start até ponto de maior distância)
        left = rdp(points[: index_of_max + 1], epsilon)
        # Parte direita (do ponto de maior distância até end)
        right = rdp(points[index_of_max:], epsilon)

        # Combina, evitando duplicar o ponto de junção
        return left[:-1] + right
    else:
        # Tudo pode ser representado apenas por start e end
        return [start, end]
