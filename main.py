from circles import Colour, Circle, pygame
from typing import Tuple

pygame.init()
game_surface = pygame.display.set_mode([500, 500])

running = True


class Trajectory:
    def __init__(self, gradient: float, y_intercept: float):
        self.gradient = gradient
        self.y_intercept = y_intercept

    def perpendicular(self, coordinates: tuple[int, int]) -> tuple[int, int]:
        try:
            self.gradient = -1 / self.gradient
        except ZeroDivisionError:
            self.gradient = 0
        
        x, y = coordinates

        self.y_intercept = y - self.gradient * x

    def get_gradient(self):
        return self.gradient

    def get_y_intercept(self):
        return self.y_intercept


class Paddle(pygame.Rect):
    def __init__(self, topleft: Tuple[int, int], width: int, height: int):
        x, y = topleft
        super().__init__(x, y, width, height)


class Ball(Circle):
    def __init__(
        self,
        fill: Colour,
        radius: float,
        centre: tuple[int, int],
        surface: pygame.Surface,
        trajectory: Trajectory,
        bounds: tuple[tuple[int, int], tuple[int, int]],
        border: int = 0,
        border_colour: Colour = None,
        speed: float = 5.00,
    ):
        super().__init__(fill, radius, centre, surface, border, border_colour)
        self.speed = speed
        self.trajectory = trajectory
        self.bounds = bounds

    def _intersect_bounds(self) -> bool:
        centrex, centrey = self.centre
        north, west = self.bounds[0]  # north, west bounds coordinates
        south, east = self.bounds[1]  # south, east bounds coordinates
        if centrex + self.radius >= east or centrex - self.radius <= west:
            return True
        elif centrey + self.radius >= south or centrey - self.radius <= north:
            return True
        return False

    def move(self):
        x, y = self.centre
        
        if self._intersect_bounds():
            print("ye")
            self.trajectory.perpendicular((x, y))

        x += self.speed * self.trajectory.get_gradient()
        y = self.trajectory.get_gradient() * x + self.trajectory.get_y_intercept()

        self.centre = (int(x), int(y))

    def process(self, paddles: list[Paddle]):
        # for paddle in paddles:
        #     if self.rectangle_intersect(paddle):
        #         overlap = self.centre[0] - paddle.centerx
        #         self.trajectory.gradient = -self.trajectory.gradient + overlap / 100
        self.move()
        self.draw()



#paddle1 = Paddle(topleft=(50, 50), width=10, height=70)

ball = Ball(
    fill=Colour(155, 0, 0),
    radius=35.0,
    centre=(120, 120),
    surface=game_surface,
    trajectory=Trajectory(3.0, 5.0),
    bounds=((0, 0), (500, 500)),
    border=2,
    border_colour=Colour(255, 0, 0),
    speed=0.50  # pixels moved per frame tick
)

paddles = []#[paddle1]

clock = pygame.time.Clock()
while running:
    game_surface.fill((255, 255, 255))
    for paddle in paddles:
        pygame.draw.rect(game_surface, (0, 0, 255), paddle)
    ball.process(paddles)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    pygame.display.flip()
    clock.tick(60)
