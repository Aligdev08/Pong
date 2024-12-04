import pygame
from circles import Colour, Circle
from typing import Tuple
import random

pygame.init()
game_surface = pygame.display.set_mode([500, 500])

running = True

# Define constants for difficulty
DIFFICULTY_EASY = 1
DIFFICULTY_MEDIUM = 2
DIFFICULTY_HARD = 3


class Trajectory:
    def __init__(self, x_velocity: float, y_velocity: float):
        self.x_velocity = x_velocity
        self.y_velocity = y_velocity

    def reflect_x(self):
        self.x_velocity = -self.x_velocity

    def reflect_y(self):
        self.y_velocity = -self.y_velocity


class Paddle(pygame.Rect):
    def __init__(self, topleft: Tuple[int, int], width: int, height: int, speed: int = 5):
        x, y = topleft
        super().__init__(x, y, width, height)
        self.instance_moving = False  # Whether the paddle is moving
        self.speed = speed

    def move(self, up: int, down: int):
        force = down - up  # Calculate net force (down force minus up force)

        if force == 0:  # No movement if up and down are equal
            return

        # Update the paddle's vertical position based on the force
        if self.instance_moving:  # Only move if the paddle is supposed to move
            self.y += force * self.speed

            # Ensure the paddle stays within the screen boundaries
            if self.top < 0:
                self.top = 0
            elif self.bottom > 500:  # Assuming the screen height is 500
                self.bottom = 500

    def set_moving(self, moving: bool):
        """Sets whether the paddle is moving or not."""
        self.instance_moving = moving


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
        self.last_bounced = None

    def bounce(self, axis: str):
        """Handle boundary collisions and adjust trajectory based on the collision axis."""
        if axis == "x":
            self.trajectory.reflect_x()
            # Move slightly away from the boundary to avoid getting stuck
            self.centre = (
                self.centre[0] + self.trajectory.x_velocity * self.speed,
                self.centre[1],
            )
        elif axis == "y":
            self.trajectory.reflect_y()
            # Move slightly away from the boundary to avoid getting stuck
            self.centre = (
                self.centre[0],
                self.centre[1] + self.trajectory.y_velocity * self.speed,
            )

    def move(self):
        """Check for boundary collisions and update the ball's position."""
        x, y = self.centre
        epsilon = 1.0  # Tolerance for boundary detection

        # Check for horizontal boundary collisions


        # Check for vertical boundary collisions
        if y + self.radius >= self.bounds[1][1] - epsilon:
            self.bounce("y")
        elif y - self.radius <= self.bounds[0][0] + epsilon:
            self.bounce("y")
        elif x + self.radius >= self.bounds[1][0] - epsilon:
            self.bounce("x")
        elif x - self.radius <= self.bounds[0][1] + epsilon:
            pass

        # Update position
        x += self.trajectory.x_velocity * self.speed
        y += self.trajectory.y_velocity * self.speed
        self.centre = (int(x), int(y))

    def process(self, paddles: list[Paddle]):
        for paddle in paddles:
            collision_side = self.rectangle_intersect(paddle)
            if collision_side:
                if collision_side == "x":
                    self.bounce("x")  # Reflect ball on x-axis
                elif collision_side == "y":
                    self.bounce("y")  # Reflect ball on y-axis
        shadow = Circle(
            fill=self.fill.shadow(),
            radius=self.radius,
            centre=self.centre,
            surface=self.surface,
        )
        shadow.draw()
        shadow.blur(100)
        self.move()
        self.draw()


class Settings:
    paddle_width = 10
    bounds = ((0, 0), (500, 500))

    def __init__(
        self,
        ball_speed: int,
        ball_radius: int,
        paddle_speed: int,
        paddle_height: int,
        paddle_starting_coordinates: tuple[int, int],
        difficulty: int = DIFFICULTY_MEDIUM,
    ):
        self.ball_speed = ball_speed
        self.ball_radius = ball_radius
        self.paddle_speed = paddle_speed
        self.paddle_height = paddle_height
        self.paddle_starting_coordinates = paddle_starting_coordinates
        self.difficulty = difficulty
        self.ball_trajectory = Trajectory(
            random.uniform(1, 5.0) * difficulty, random.uniform(1, 5.0) * difficulty
        )


class Game:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.paddles = [
            Paddle(
                topleft=self.settings.paddle_starting_coordinates,
                width=self.settings.paddle_width,
                height=self.settings.paddle_height,
                speed=self.settings.paddle_speed,
            )
        ]

        self.balls = [
            Ball(
                fill=Colour(155, 0, 0),
                radius=settings.ball_radius,
                centre=(120, 120),
                surface=game_surface,
                trajectory=self.settings.ball_trajectory,  # x_velocity, y_velocity
                bounds=self.settings.bounds,
                border=2,
                border_colour=Colour(255, 0, 0),
                speed=settings.ball_speed,  # pixels moved per frame tick
            )
        ]

        self.score = 0
        self.running = True

    def tick(self):
        game_surface.fill((0, 0, 0))
        for ball in self.balls:
            ball.process(self.paddles)

        keys = pygame.key.get_pressed()
        for paddle in self.paddles:
            pygame.draw.rect(game_surface, (0, 0, 255), paddle)
            if keys[pygame.K_UP]:
                paddle.set_moving(True)
                paddle.move(up=1, down=0)
            elif keys[pygame.K_DOWN]:
                paddle.set_moving(True)
                paddle.move(up=0, down=1)

        # Check if the ball leaves the left side
        for ball in self.balls:
            if ball.centre[0] - ball.radius <= 0:
                self.score -= 1  # Ball left, lose a point
                if len(self.balls) < 1:
                    self.balls = []
                    self.spawn_new_ball()

        self.display_score()

    def spawn_new_ball(self):
        """Spawn a new ball in the center."""
        new_ball = Ball(
            fill=Colour(155, 0, 0),
            radius=self.settings.ball_radius,
            centre=(250, 250),  # Center of the screen
            surface=game_surface,
            trajectory=self.settings.ball_trajectory,
            bounds=self.settings.bounds,
            border=2,
            border_colour=Colour(255, 0, 0),
            speed=self.settings.ball_speed,
        )
        self.balls.append(new_ball)

    def display_score(self):
        """Display the score."""
        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Score: {self.score}", True, (255, 255, 255))
        game_surface.blit(score_text, (10, 10))


def show_start_menu():
    """Display the start menu."""
    font = pygame.font.Font(None, 50)
    game_surface.fill((0, 0, 0))
    start_text = font.render("Press Enter to Start", True, (255, 255, 255))
    game_surface.blit(start_text, (100, 200))

    difficulty_text = font.render("Press 1 for Easy, 2 for Medium, 3 for Hard", True, (255, 255, 255))
    game_surface.blit(difficulty_text, (30, 300))

    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    waiting = False
                elif event.key == pygame.K_1:
                    return DIFFICULTY_EASY
                elif event.key == pygame.K_2:
                    return DIFFICULTY_MEDIUM
                elif event.key == pygame.K_3:
                    return DIFFICULTY_HARD


difficulty = show_start_menu()

if difficulty is None:
    pygame.quit()

settings = Settings(
    ball_speed=1,
    ball_radius=35,
    paddle_speed=2,
    paddle_height=100,
    paddle_starting_coordinates=(50, 50),
    difficulty=difficulty,
)

game = Game(settings)

clock = pygame.time.Clock()
while game.running:
    game.tick()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game.running = False

    pygame.display.flip()
    clock.tick(240)

pygame.quit()
