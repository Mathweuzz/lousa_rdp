"""
Módulo responsável pela representação de traços (strokes) e
funções de pré-processamento.

Cada traço é uma sequência de pontos (x, y, t), onde:
- x, y: coordenadas na tela (pixels).
- t: tempo em segundos desde o início (float).

Além disso, cada traço pode guardar:
- processed_points: pontos (x, y) após pré-processamento
  (limpeza, fechamento opcional, reamostragem).
- simplified_points: pontos (x, y) após simplificação (RDP).
- is_closed: boolean indicando se o traço é considerado "fechado".
"""

import math


class Stroke:
    """
    Representa um único traço desenhado pelo usuário.

    Atributos:
    - color: tupla (R, G, B) com a cor do traço.
    - width: espessura da linha.
    - points: lista de tuplas (x, y, t) com os pontos originais.
    - processed_points: lista de tuplas (x, y) após pré-processamento.
    - simplified_points: lista de tuplas (x, y) após RDP.
    - is_closed: boolean indicando se o traço é considerado "fechado".
    """

    def __init__(self, color=(255, 255, 255), width=3):
        self.color = color
        self.width = width
        self.points = []
        self.processed_points = []
        self.simplified_points = []
        self.is_closed = False

    def add_point(self, pos, t):
        """
        Adiciona um ponto (x, y, t) ao traço.

        :param pos: tupla (x, y) com a posição do mouse.
        :param t: tempo em segundos (float) desde o início (pygame.time.get_ticks()/1000).
        """
        x, y = pos

        # Evita adicionar pontos duplicados consecutivos na mesma posição
        if not self.points:
            self.points.append((x, y, t))
        else:
            last_x, last_y, _ = self.points[-1]
            if last_x != x or last_y != y:
                self.points.append((x, y, t))

    def is_empty(self):
        """
        Retorna True se o traço não contém pontos.
        """
        return len(self.points) == 0

    def __len__(self):
        """
        Permite usar len(stroke) para obter a quantidade de pontos originais.
        """
        return len(self.points)

    def get_xy_points(self):
        """
        Retorna apenas as coordenadas (x, y) dos pontos originais, ignorando o tempo.
        """
        return [(x, y) for (x, y, _) in self.points]

    def set_processed_points(self, xy_points, is_closed):
        """
        Define a lista de pontos pré-processados (após limpeza, fechamento, reamostragem)
        e atualiza a flag de fechamento.

        :param xy_points: lista de tuplas (x, y).
        :param is_closed: boolean indicando se o traço foi considerado fechado.
        """
        self.processed_points = list(xy_points) if xy_points is not None else []
        self.is_closed = bool(is_closed)

    def set_simplified_points(self, xy_points):
        """
        Define a lista de pontos simplificados (após RDP, por exemplo).

        :param xy_points: lista de tuplas (x, y).
        """
        self.simplified_points = list(xy_points) if xy_points is not None else []


# ---------------------------------------------------------------------------
# Funções de utilidade para pré-processamento de listas de pontos (x, y)
# ---------------------------------------------------------------------------

def remove_consecutive_duplicates_xy(points):
    """
    Remove pontos duplicados consecutivos em uma lista de (x, y).

    :param points: lista de tuplas (x, y).
    :return: nova lista sem duplicatas consecutivas.
    """
    if not points:
        return []

    result = [points[0]]
    for p in points[1:]:
        if p != result[-1]:
            result.append(p)
    return result


def is_path_closed(points, close_threshold):
    """
    Verifica se o caminho é "fechado" com base na distância entre
    o primeiro e o último ponto.

    :param points: lista de (x, y).
    :param close_threshold: distância máxima para considerar o traço fechado.
    :return: True se for fechado, False caso contrário.
    """
    if len(points) < 3:
        return False

    x0, y0 = points[0]
    x1, y1 = points[-1]
    dist = math.hypot(x1 - x0, y1 - y0)

    return dist <= close_threshold


def resample_by_arc_length(points, target_spacing):
    """
    Reamostra a polilinha para que os pontos fiquem aproximadamente
    espaçados por 'target_spacing' ao longo do comprimento de arco.

    :param points: lista de (x, y).
    :param target_spacing: espaçamento alvo em pixels.
    :return: nova lista de pontos (x, y) reamostrados.
    """
    if not points:
        return []

    if len(points) < 2:
        return list(points)

    if target_spacing <= 0:
        return list(points)

    # Calcula distâncias acumuladas ao longo da polilinha
    cumulative = [0.0]
    for i in range(1, len(points)):
        x0, y0 = points[i - 1]
        x1, y1 = points[i]
        seg_len = math.hypot(x1 - x0, y1 - y0)
        cumulative.append(cumulative[-1] + seg_len)

    total_length = cumulative[-1]

    if total_length == 0.0:
        # Todos os pontos são iguais
        return [points[0]]

    # Gera distâncias alvo ao longo da curva
    num_samples = int(total_length / target_spacing)

    if num_samples < 1:
        # Muito curto para reamostrar de forma útil
        return list(points)

    target_distances = [i * target_spacing for i in range(num_samples)]
    # Garante que o último ponto seja sempre o fim da polilinha
    if target_distances[-1] < total_length:
        target_distances.append(total_length)

    resampled = []
    j = 1  # índice que percorre segmentos originais

    for td in target_distances:
        # Avança j até encontrar o segmento que contém a distância td
        while j < len(points) and cumulative[j] < td:
            j += 1

        if j == len(points):
            # Em casos numéricos estranhos, clampa no último ponto
            resampled.append(points[-1])
            continue

        # Segmento entre points[j-1] e points[j]
        x0, y0 = points[j - 1]
        x1, y1 = points[j]

        d0 = cumulative[j - 1]
        d1 = cumulative[j]

        if d1 == d0:
            # Segmento degenerado
            resampled.append((x0, y0))
        else:
            alpha = (td - d0) / (d1 - d0)
            x = x0 + alpha * (x1 - x0)
            y = y0 + alpha * (y1 - y0)
            resampled.append((x, y))

    return resampled


def preprocess_points_for_rdp(points_xy, close_threshold=20.0, target_spacing=5.0):
    """
    Pipeline de pré-processamento antes do RDP:

    1. Remove duplicatas consecutivas.
    2. Verifica se o traço é fechado (distância entre início e fim <= close_threshold).
       Se for fechado e o último ponto não for exatamente igual ao primeiro,
       adiciona o primeiro ponto ao final para fechar o loop.
    3. Reamostra a polilinha por comprimento de arco usando target_spacing.

    Também garante que, se o traço for considerado fechado, o resultado
    final mantenha início e fim próximos (fechamento aproximado).

    :param points_xy: lista de (x, y) dos pontos originais.
    :param close_threshold: distância máxima para considerar o traço fechado.
    :param target_spacing: espaçamento alvo em pixels para a reamostragem.
    :return: (processed_points, is_closed)
    """
    # 1) Remoção de duplicatas consecutivas
    cleaned = remove_consecutive_duplicates_xy(points_xy)

    if not cleaned:
        return [], False

    # 2) Detecção de traço fechado
    closed = is_path_closed(cleaned, close_threshold)

    # Se for fechado, garante que o caminho seja explicitamente fechado
    if closed and cleaned[0] != cleaned[-1]:
        cleaned.append(cleaned[0])

    # 3) Reamostragem por comprimento de arco
    processed = resample_by_arc_length(cleaned, target_spacing)

    # Se for fechado, tenta garantir que o resultado final também seja "quase fechado"
    if closed and len(processed) >= 2:
        x0, y0 = processed[0]
        x1, y1 = processed[-1]
        dist = math.hypot(x1 - x0, y1 - y0)
        if dist > close_threshold:
            # Adiciona o primeiro ponto ao final para reforçar o fechamento
            processed.append(processed[0])

    return processed, closed