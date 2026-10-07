"""
GameEngine: owns the basket and all falling objects.

Starter version: basket movement and spawning both work at a basic
level (Tasks 2 and 3 ask you to improve them), there's no speed boost
yet (Task 4 builds it from scratch), and catch detection has two
known bugs (see game/collision.py and the catch-checking loop below)
that Task 1 asks you to fix.
"""

import random
import pygame

from game.basket import Basket
from game.falling_object import FallingObject
from game.collision import is_caught
from game.renderer import WIDTH, HEIGHT

MIN_SPAWN_INTERVAL_FRAMES = 30
MAX_SPAWN_INTERVAL_FRAMES = 70
MAX_OBJECTS = 5
SPAWN_MARGIN = 20
MIN_SPAWN_DISTANCE = 60
MAX_MISSES = 5


class GameEngine:
    def __init__(self):
        self.basket = Basket(x=WIDTH / 2, y=HEIGHT - 30)
        self.objects = []
        self.frames_until_spawn = 0
        self.last_spawn_x = None
        self.score = 0
        self.misses = 0
        self.game_over = False

    def _spawn_object(self):
        if len(self.objects) >= MAX_OBJECTS:
            return

        min_x = SPAWN_MARGIN
        max_x = WIDTH - SPAWN_MARGIN
        spawn_ranges = [(min_x, max_x)]

        if self.last_spawn_x is not None:
            spawn_ranges = []

            left_end = self.last_spawn_x - MIN_SPAWN_DISTANCE
            right_start = self.last_spawn_x + MIN_SPAWN_DISTANCE

            if left_end >= min_x:
                spawn_ranges.append((min_x, left_end))

            if right_start <= max_x:
                spawn_ranges.append((right_start, max_x))

        if spawn_ranges:
            start, end = random.choice(spawn_ranges)
            x = random.randint(start, end)
        else:
            # On narrow screens, use the furthest available edge.
            x = max(
                (min_x, max_x),
                key=lambda position: abs(position - self.last_spawn_x),
            )

        self.objects.append(FallingObject(x=x, y=-14, speed=3))
        self.last_spawn_x = x

    def handle_input(self, keys_pressed):
        if self.game_over:
            return

        if keys_pressed[pygame.K_LEFT]:
            self.basket.x -= self.basket.speed
        if keys_pressed[pygame.K_RIGHT]:
            self.basket.x += self.basket.speed

        half_width = self.basket.get_rect().width / 2
        self.basket.x = max(
            half_width,
            min(WIDTH - half_width, self.basket.x),
        )
    def handle_keydown(self, key):
        if self.game_over and key == pygame.K_r:
            self.__init__()

    def update(self):
        if self.game_over:
            return

        self.frames_until_spawn -= 1
        if self.frames_until_spawn <= 0:
            self._spawn_object()
            self.frames_until_spawn = random.randint(
                MIN_SPAWN_INTERVAL_FRAMES,
                MAX_SPAWN_INTERVAL_FRAMES,
            )

        for obj in self.objects:
            obj.update()

        basket_rect = self.basket.get_rect()
        for obj in self.objects[:]:
            if is_caught(basket_rect, obj):
                self.score += 1
                self.objects.remove(obj)

        missed = [o for o in self.objects if o.is_past_bottom(HEIGHT)]
        if missed:
            self.objects = [o for o in self.objects if not o.is_past_bottom(HEIGHT)]
            self.misses += len(missed)
            if self.misses >= MAX_MISSES:
                self.game_over = True

    def draw(self, surface, font):
        from game import renderer
        renderer.draw_scene(surface, self.basket, self.objects)
        renderer.draw_text(surface, font, f"Score: {self.score}", (10, 10))
        renderer.draw_text(surface, font, f"Misses: {self.misses}/{MAX_MISSES}", (10, 36))

        if self.game_over:
            renderer.draw_banner(surface, font, f"Game Over! Final score: {self.score}. Press R to restart.")
