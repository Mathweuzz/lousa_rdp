"""
Módulo responsável pela representação de traços (strokes).

Cada traço é uma sequência de pontos (x, y, t), onde:
- x, y: coordenadas na tela (pixels).
- t: tempo em segundos desde o início (float).

Além disso, cada traço pode guardar uma versão simplificada de seus pontos
(sem o tempo), tipicamente gerada pelo algoritmo Ramer–Douglas–Peucker (RDP).
"""


class Stroke:
    """
    Representa um único traço desenhado pelo usuário.

    Atributos:
    - color: tupla (R, G, B) com a cor do traço.
    - width: espessura da linha.
    - points: lista de tuplas (x, y, t) com os pontos originais.
    - simplified_points: lista de tuplas (x, y) com os pontos simplificados.
    """

    def __init__(self, color=(255, 255, 255), width=3):
        self.color = color
        self.width = width
        self.points = []
        self.simplified_points = []

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

    def set_simplified_points(self, xy_points):
        """
        Define a lista de pontos simplificados (após RDP, por exemplo).

        :param xy_points: lista de tuplas (x, y).
        """
        self.simplified_points = list(xy_points) if xy_points is not None else []
