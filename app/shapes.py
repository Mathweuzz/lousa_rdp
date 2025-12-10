"""
Módulo de formas canônicas (shapes) da LousaRDP.

Cada shape sabe:
- desenhar-se em uma surface do pygame;
- mover-se (para seleção/edição simples);
- responder se "contém" um ponto (para seleção com o mouse).
"""

import math
import pygame

from .geometry import bounding_box, distance


class BaseShape:
    """
    Classe base para shapes canônicos.

    Atributos:
    - color: tupla (R, G, B)
    - width: espessura do traço
    """

    def __init__(self, color=(255, 255, 255), width=3):
        self.color = color
        self.width = width

    def draw(self, surface):
        raise NotImplementedError

    def move(self, dx, dy):
        """
        Move o shape por (dx, dy) em pixels.
        """
        pass

    def contains_point(self, pos):
        """
        Retorna True se o ponto (x, y) estiver "sobre" o shape,
        usado para seleção. A implementação padrão retorna False.
        """
        return False


class LineShape(BaseShape):
    """
    Segmento de reta canônico.
    """

    def __init__(self, p0, p1, color=(255, 255, 255), width=3):
        super().__init__(color=color, width=width)
        self.p0 = (float(p0[0]), float(p0[1]))
        self.p1 = (float(p1[0]), float(p1[1]))

    def draw(self, surface):
        pygame.draw.line(
            surface,
            self.color,
            (int(self.p0[0]), int(self.p0[1])),
            (int(self.p1[0]), int(self.p1[1])),
            self.width,
        )

    def move(self, dx, dy):
        self.p0 = (self.p0[0] + dx, self.p0[1] + dy)
        self.p1 = (self.p1[0] + dx, self.p1[1] + dy)

    def contains_point(self, pos):
        # Distância ponto-segmento com tolerância
        x0, y0 = pos
        x1, y1 = self.p0
        x2, y2 = self.p1

        dx = x2 - x1
        dy = y2 - y1
        if dx == 0 and dy == 0:
            # Segmento degenerado => checa distância ao ponto
            return distance((x0, y0), (x1, y1)) <= max(self.width + 4, 6)

        # Projeção do ponto na linha paramétrica
        t = ((x0 - x1) * dx + (y0 - y1) * dy) / (dx * dx + dy * dy)
        t = max(0.0, min(1.0, t))
        proj_x = x1 + t * dx
        proj_y = y1 + t * dy

        d = distance((x0, y0), (proj_x, proj_y))
        return d <= max(self.width + 4, 6)


class CircleShape(BaseShape):
    """
    Círculo canônico.
    """

    def __init__(self, center, radius, color=(255, 255, 255), width=3):
        super().__init__(color=color, width=width)
        self.cx = float(center[0])
        self.cy = float(center[1])
        self.radius = float(radius)

    def draw(self, surface):
        pygame.draw.circle(
            surface,
            self.color,
            (int(self.cx), int(self.cy)),
            max(1, int(self.radius)),
            self.width,
        )

    def move(self, dx, dy):
        self.cx += dx
        self.cy += dy

    def contains_point(self, pos):
        d = distance((self.cx, self.cy), pos)
        # Seleciona se estiver perto da circunferência
        return abs(d - self.radius) <= max(self.width + 4, 8)


class RectShape(BaseShape):
    """
    Retângulo axis-aligned (alinhado aos eixos).
    Representado por canto superior esquerdo (x, y) e dimensões (w, h).
    """

    def __init__(self, topleft, width_rect, height_rect, color=(255, 255, 255), width=3):
        super().__init__(color=color, width=width)
        self.x = float(topleft[0])
        self.y = float(topleft[1])
        self.w = float(width_rect)
        self.h = float(height_rect)

    def draw(self, surface):
        rect = pygame.Rect(
            int(self.x),
            int(self.y),
            max(1, int(self.w)),
            max(1, int(self.h)),
        )
        pygame.draw.rect(surface, self.color, rect, self.width)

    def move(self, dx, dy):
        self.x += dx
        self.y += dy

    def contains_point(self, pos):
        x, y = pos
        margin = max(self.width + 4, 8)
        return (
            x >= self.x - margin
            and x <= self.x + self.w + margin
            and y >= self.y - margin
            and y <= self.y + self.h + margin
        )


class PolylineShape(BaseShape):
    """
    Polilinha canônica (simplificada).
    """

    def __init__(self, points, is_closed=False, color=(255, 255, 255), width=3):
        super().__init__(color=color, width=width)
        self.points = [(float(x), float(y)) for (x, y) in points]
        self.is_closed = bool(is_closed)

    def draw(self, surface):
        if not self.points:
            return

        if len(self.points) == 1:
            x, y = self.points[0]
            pygame.draw.circle(surface, self.color, (int(x), int(y)), self.width)
            return

        # Desenha segments
        for i in range(1, len(self.points)):
            x1, y1 = self.points[i - 1]
            x2, y2 = self.points[i]
            pygame.draw.line(
                surface,
                self.color,
                (int(x1), int(y1)),
                (int(x2), int(y2)),
                self.width,
            )

        # Se for polígono fechado, conecta último ao primeiro
        if self.is_closed and len(self.points) > 2:
            x1, y1 = self.points[-1]
            x2, y2 = self.points[0]
            pygame.draw.line(
                surface,
                self.color,
                (int(x1), int(y1)),
                (int(x2), int(y2)),
                self.width,
            )

    def move(self, dx, dy):
        self.points = [(x + dx, y + dy) for (x, y) in self.points]

    def contains_point(self, pos):
        # Aproxima com bounding box inflado (bem simples)
        if not self.points:
            return False

        min_x, min_y, max_x, max_y = bounding_box(self.points)
        margin = max(self.width + 6, 10)
        x, y = pos
        return (
            x >= min_x - margin
            and x <= max_x + margin
            and y >= min_y - margin
            and y <= max_y + margin
        )
