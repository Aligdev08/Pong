import pygame
from circles import Colour, Circle
from typing import Tuple
import random
import asyncio

pygame.init()
game_surface = pygame.display.set_mode([500, 500])

running = True

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
    def __init__(self, top_left: Tuple[int, int], width: int, height: int, speed: int = 5):
        x, y = top_left
        super().__init__(x, y, width, height)
        self.instance_moving = False
        self.speed = speed

    def move(self, up: int, down: int):
        force = down - up  # net force

        if force == 0:
            return

        self.y += force * self.speed

        if self.top < 0:
            self.top = 0
        elif self.bottom > 500:  # assuming the screen height is 500
            self.bottom = 500

    def set_moving(self, moving: bool):
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

    def bounce(self, axis: str):
        if axis == "x":
            self.trajectory.reflect_x()
        elif axis == "y":
            self.trajectory.reflect_y()

    def move(self):
        x, y = self.centre
        x += self.trajectory.x_velocity * self.speed
        y += self.trajectory.y_velocity * self.speed

        # Boundary checks
        if y + self.radius >= self.bounds[1][1]:
            y = self.bounds[1][1] - self.radius
            self.bounce("y")
        elif y - self.radius <= self.bounds[0][0]:
            y = self.radius
            self.bounce("y")

        if x + self.radius >= self.bounds[1][0]:
            x = self.bounds[1][0] - self.radius
            self.bounce("x")
        elif x - self.radius <= self.bounds[0][1]:
            x = self.radius  # Reset position if it goes out of bounds
            return False  # Indicate that the ball has left the screen

        self.centre = (int(x), int(y))
        return True  # Indicate that the ball is still in play

    def process(self, paddles: list[Paddle]):
        for paddle in paddles:
            collision_side = self.rectangle_intersect(paddle)
            if collision_side:
                if collision_side == "x":
                    self.bounce("x")  # Reflect ball on x-axis
                elif collision_side == "y":
                    self.bounce("y")  # Reflect ball on y-axis

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
            game_difficulty: int = DIFFICULTY_MEDIUM,
    ):
        self.ball_speed = ball_speed
        self.ball_radius = ball_radius
        self.paddle_speed = paddle_speed
        self.paddle_height = paddle_height
        self.paddle_starting_coordinates = paddle_starting_coordinates
        self.game_difficulty = game_difficulty
        self.ball_trajectory = Trajectory(
            random.uniform(1, 5.0) * game_difficulty, random.uniform(1, 5.0) * game_difficulty
        )


class Game:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.paddles = [
            Paddle(
                top_left=self.settings.paddle_starting_coordinates,
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
                trajectory=self.settings.ball_trajectory,
                bounds=self.settings.bounds,
                border=2,
                border_colour=Colour(255, 0, 0),
                speed=settings.ball_speed,
            )
        ]

        self.score = 0
        self.running = True

    async def tick(self):
        game_surface.fill((0, 0, 0))
        for ball in self.balls[:]:  # Iterate over a copy of the list
            if not ball.move():  # Check if the ball is still in play
                self.score -= 1  # Ball left, lose a point
                self.balls.remove(ball)  # Remove the ball from the list
                await asyncio.sleep(1)  # Pause for a second
                self.spawn_new_ball()  # Spawn a new ball
                continue
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
            else:
                paddle.set_moving(False)

        self.display_score()

    def spawn_new_ball(self):
        new_ball = Ball(
            fill=Colour(155, 0, 0),
            radius=self.settings.ball_radius,
            centre=(250, 250),
            surface=game_surface,
            trajectory=Trajectory(
                random.uniform(1, 5.0) * self.settings.game_difficulty,
                random.uniform(1, 5.0) * self.settings.game_difficulty
            ),
            bounds=self.settings.bounds,
            border=2,
            border_colour=Colour(255, 0, 0),
            speed=self.settings.ball_speed,
        )
        self.balls.append(new_ball)

    def display_score(self):
        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Aura: {self.score}", True, (255, 255, 255))
        game_surface.blit(score_text, (10, 10))


async def show_start_menu():
    font = pygame.font.Font(None, 50)
    waiting = True
    while waiting:
        game_surface.fill((0, 0, 0))
        start_text = font.render("Press Enter to Start", True, (255, 255, 255))
        game_surface.blit(start_text, (100, 200))

        difficulty_text = font.render("1 - Easy, 2 - Medium, 3 - Hard", True, (255, 255, 255))
        game_surface.blit(difficulty_text, (10, 300))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return None
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    waiting = False
                    await main()
                elif event.key == pygame.K_1:
                    return DIFFICULTY_EASY
                elif event.key == pygame.K_2:
                    return DIFFICULTY_MEDIUM
                elif event.key == pygame.K_3:
                    return DIFFICULTY_HARD


# Main game loop
async def main():
    difficulty = await show_start_menu()
    settings = Settings(
        ball_speed=1,
        ball_radius=35,
        paddle_speed=5,
        paddle_height=100,
        paddle_starting_coordinates=(50, 50),
        game_difficulty=difficulty,
    )

    game = Game(settings)

    clock = pygame.time.Clock()
    while game.running:
        await game.tick()  # Call the async tick method

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game.running = False

        pygame.display.flip()
        clock.tick(240)


# Run the game
if __name__ == "__main__":
    pygame.init()
    game_surface = pygame.display.set_mode([500, 500])
    asyncio.run(main())
    pygame.quit()