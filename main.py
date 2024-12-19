import pygame
from circles import Colour, Circle
from typing import Tuple

pygame.init()
game_surface = pygame.display.set_mode([500, 500])

running = True


class Paddle(pygame.Rect):
    def __init__(self, top_left: Tuple[int, int], width: int, height: int, speed: int = 5):
        x, y = top_left
        super().__init__(x, y, width, height)
        self.speed = speed

    def move(self, up: int, down: int):
        force = down - up  # net force
        if force == 0:
            return

        self.y += force * self.speed

        if self.top < 0:
            self.top = 0
        elif self.bottom > game_surface.get_size()[1]:
            self.bottom = game_surface.get_size()[1]

    def draw(self):
        return pygame.draw.rect(game_surface, (0, 0, 255), self)

    def process(self, pressed_keys):
        self.draw()

        if pressed_keys[pygame.K_UP]:
            paddle.move(up=1, down=0)

        elif pressed_keys[pygame.K_DOWN]:
            paddle.move(up=0, down=1)


class Ball(Circle):
    def __init__(
            self,
            fill: Colour,
            radius: float,
            centre: tuple[int, int],
            surface: pygame.Surface,
            velocity: list[int],
            border: int = 2,
            border_colour: Colour = Colour(255, 0, 0)

    ):
        super().__init__(fill, radius, centre, surface, border, border_colour)
        self.velocity = velocity

    def bounce(self, axis: str):
        if axis == "x":
            self.velocity[0] *= -1
        elif axis == "y":
            self.velocity[1] *= -1

    def move(self):
        x, y = self.centre
        x += self.velocity[0]
        y += self.velocity[1]

        self.centre = (int(x), int(y))

    def process(self, paddles_: list[Paddle]):
        for paddle_ in paddles_:
            collision_side = self.rectangle_intersect(paddle_)
            if collision_side:
                if collision_side == "x":
                    self.bounce("x")
                if collision_side == "y":
                    self.bounce("y")
        if self.centre[0] >= 500 or self.centre[0] <= 0:
            self.bounce("x")
        if self.centre[1] >= 500 or self.centre[1] <= 0:
            self.bounce("y")

        self.move()
        self.draw()


balls = [
    Ball(
        fill=Colour(155, 0, 0),
        radius=50,
        centre=(200, 350),
        surface=game_surface,
        velocity=[5, 5],
    )
]

paddles = [
    Paddle(
        top_left=(50, 10),
        width=50,
        height=100,
        speed=5
    )
]

score = 0

while running:
    game_surface.fill((0, 0, 0))

    for ball in balls:
        ball.process(paddles)

    keys = pygame.key.get_pressed()

    for paddle in paddles:
        paddle.process(keys)

    font = pygame.font.Font(None, 36)
    score_text = font.render(f"Aura: {score}", True, (255, 255, 255))
    game_surface.blit(score_text, (10, 10))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    pygame.display.flip()

    clock = pygame.time.Clock()
    clock.tick(60)
