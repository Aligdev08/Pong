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
        if self.border > 0:
            pygame.draw.circle(self.surface, self.border_colour.to_tuple(), self.centre, self.radius)
            pygame.draw.circle(self.surface, self.fill.to_tuple(), self.centre, self.radius - self.border)
        else:
            pygame.draw.circle(self.surface, self.fill.to_tuple(), self.centre, self.radius)

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

    def rectangle_intersect(self, rect: pygame.Rect) -> str | None:
        a, b = self.centre
        rect_x, rect_y, rect_width, rect_height = rect

        # Calculate the closest point on the rectangle to the ball center
        closest_x = max(rect_x, min(a, rect_x + rect_width))
        closest_y = max(rect_y, min(b, rect_y + rect_height))

        dist_x = (closest_x - a) ** 2
        dist_y = (closest_y - b) ** 2

        # Check for intersection
        if dist_x + dist_y <= self.radius ** 2:
            overlap_x = abs(a - closest_x)
            overlap_y = abs(b - closest_y)

            # Determine which side the ball collided with based on the overlap
            if overlap_x >= overlap_y:
                # x-axis collision (ball's center x is closer to rect's edge)
                if a <= closest_x:
                    # Ball is to the left of the paddle
                    self.centre = (closest_x + self.radius, b)  # Push the ball away
                else:
                    # Ball is to the right of the paddle
                    self.centre = (closest_x - self.radius, b)  # Push the ball away
                return "x"
            else:
                # y-axis collision (ball's center y is closer to rect's edge)
                if b <= closest_y:
                    # Ball is above the paddle
                    self.centre = (a, closest_y + self.radius)  # Push the ball away
                else:
                    # Ball is below the paddle
                    self.centre = (a, closest_y - self.radius)  # Push the ball away
                return "y"

        return None

    def set_fill(self, fill: Colour):
        self.fill = fill
