import pygame
import math


class Colour:
    def __init__(self, red: int, green: int, blue: int):
        self.red = red
        self.green = green
        self.blue = blue

    def to_tuple(self) -> tuple[int, int, int]:
        return self.red, self.green, self.blue

    def shadow(self) -> 'Colour':
        # darken the color by multiplying each component by 0.5
        shadow_red = max(0, int(self.red * 0.5))
        shadow_green = max(0, int(self.green * 0.5))
        shadow_blue = max(0, int(self.blue * 0.5))
        return Colour(shadow_red, shadow_green, shadow_blue)


class Circle:
    def __init__(self, fill: Colour, radius: float, centre: tuple[int, int], surface: pygame.Surface, border: int = 0,
                 border_colour: Colour = None):
        self.fill = fill
        self.radius = radius
        self.centre = centre
        self.surface = surface
        self.border = border
        self.border_colour = border_colour if border_colour is not None else Colour(0, 0, 0)  # default to black

    def draw(self):
        pygame.draw.circle(self.surface, self.border_colour.to_tuple(), self.centre, self.radius)

        if self.border > 0:
            pygame.draw.circle(self.surface, self.fill.to_tuple(), self.centre, self.radius - self.border)

    def point_intersect(self, position: tuple[int, int]):
        x, y = position
        a, b = self.centre
        equation = (x - a) ** 2 + (y - b) ** 2
        return equation <= self.radius ** 2

    def circle_intersect(self, circle: "Circle"):
        x1, y1 = self.centre
        r1 = self.radius
        x2, y2 = circle.centre
        r2 = circle.radius
        d = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)  # pythagoras

        if d == r1 + r2 or d == r2 - r1:  # intersect at one point
            return True
        elif r2 - r1 < d < r1 + r2:  # intersect at two points
            return True
        else:
            return False

    def rectangle_intersect(self, rect: pygame.Rect) -> bool:
        a, b = self.centre

        closest_x = max(rect.left, min(a, rect.right))
        # this is the closest x value on/in the rectangle to the centre of the circle

        closest_y = max(rect.top, min(b, rect.bottom))
        # this is the closest y value on/in the rectangle to the centre of the circle

        if (closest_x - a) ** 2 + (closest_y - b) ** 2 <= self.radius ** 2:
            return True
        else:
            return False
    
    def expected_linear_intersect(self, gradient: float, y_intercept: float) -> bool:
        centrex, centrey = self.centre

        a = 1 + gradient**2
        b = 2 * gradient * (y_intercept - centrey) - 2 * centrex
        c = centrex**2 + (y_intercept - centrey)**2 - self.radius**2

        discriminant = b**2 - 4 * a * c  # b² - 4ac
        if discriminant > 0:
            return True  # intersects at two real points
        elif discriminant == 0:
            return True  # intersects at one real point
        else:
            return False  # discriminant < 0 ∴ intersects at no real points
    

    def set_fill(self, fill: Colour):
        self.fill = fill