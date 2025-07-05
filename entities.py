import pygame
import math
import random

class Bullet:
    def __init__(self, world_x, world_y, target_world_x, target_world_y, spread_angle_degrees, bullet_image, speed=15):
        scale_factor = 0.4
        size = (int(5 * 5 * scale_factor), int(10 * 5 * scale_factor))
        self.original_image = pygame.transform.scale(bullet_image, size)
        self.world_x = world_x
        self.world_y = world_y
        self.speed = speed
        self.trail = []

        angle_to_target = math.atan2(target_world_y - world_y, target_world_x - world_x)
        spread = math.radians(random.uniform(-spread_angle_degrees / 2, spread_angle_degrees / 2))
        final_angle = angle_to_target + spread

        self.vx = math.cos(final_angle) * speed
        self.vy = math.sin(final_angle) * speed
        self.angle_degrees = math.degrees(final_angle)

    def update(self):
        self.trail.append((self.world_x, self.world_y))
        if len(self.trail) > 30:
            self.trail.pop(0)
        self.world_x += self.vx
        self.world_y += self.vy

    def draw(self, screen, world_x, world_y):
        if len(self.trail) >= 2:
            points = []
            for tx, ty in self.trail:
                screen_x = tx - world_x
                screen_y = ty - world_y
                points.append((screen_x, screen_y))

            alpha_surface = pygame.Surface(screen.get_size(), pygame.SRCALPHA)

            for i in range(len(points) - 1):
                alpha = int(255 * ((i + 1) / len(points)))
                pygame.draw.line(
                    alpha_surface,
                    (255, 255, 255, alpha),
                    points[i],
                    points[i + 1],
                    width=9
                )

            screen.blit(alpha_surface, (0, 0))

        screen_x = self.world_x - world_x
        screen_y = self.world_y - world_y
        rotated_image = pygame.transform.rotate(self.original_image, -self.angle_degrees - 90)
        rect = rotated_image.get_rect(center=(screen_x, screen_y))
        screen.blit(rotated_image, rect)

    def is_offscreen(self, screen_width, screen_height, world_x, world_y):
        screen_x = self.world_x - world_x
        screen_y = self.world_y - world_y
        return (screen_x < -100 or screen_x > screen_width + 100 or screen_y < -100 or screen_y > screen_height + 100)


class ScatteredBullet:
    def __init__(self, x, y, vx, vy, bullet_image):
        self.image_original = pygame.transform.scale(bullet_image, (3, 7))
        angle = math.degrees(math.atan2(vy, vx))
        self.image_original = pygame.transform.rotate(self.image_original, angle)
        self.image = self.image_original.copy()

        self.pos = [x, y]

        speed_scale = random.uniform(3, 8)
        self.vx = vx * speed_scale
        self.vy = vy * speed_scale

        self.friction = 0.85
        self.spawn_time = pygame.time.get_ticks()
        self.lifetime = 5000
        self.fade_time = 1000
        self.alpha = 255

        self.rotation_angle = 0
        self.rotation_speed = random.uniform(5, 15) * random.choice([-1, 1])

    def update(self):
        self.pos[0] += self.vx
        self.pos[1] += self.vy
        self.vx *= self.friction
        self.vy *= self.friction

        self.rotation_angle += self.rotation_speed
        self.rotation_speed *= 0.85

        if abs(self.rotation_speed) < 0.05 and self.rotation_speed != 0:
            self.rotation_speed = 0 if random.random() < 0.5 else self.rotation_speed * -1

        self.image = pygame.transform.rotate(self.image_original, self.rotation_angle)

        elapsed = pygame.time.get_ticks() - self.spawn_time
        if elapsed > self.lifetime:
            fade_elapsed = elapsed - self.lifetime
            if fade_elapsed < self.fade_time:
                self.alpha = int(255 * (1 - fade_elapsed / self.fade_time))
                self.image.set_alpha(self.alpha)
            else:
                self.alpha = 0

    def draw(self, screen, world_x, world_y):
        if self.alpha > 0:
            screen_x = self.pos[0] - world_x
            screen_y = self.pos[1] - world_y
            rect = self.image.get_rect(center=(screen_x, screen_y))
            screen.blit(self.image, rect)

class Obstacle:
    def __init__(self, image, world_x, world_y, colliders):
        self.image = image
        self.world_x = world_x
        self.world_y = world_y
        self.rect = self.image.get_rect(topleft=(world_x, world_y))
        self.colliders = colliders

    def draw(self, screen, world_offset_x, world_offset_y):
        screen_x = self.world_x - world_offset_x
        screen_y = self.world_y - world_offset_y
        screen.blit(self.image, (screen_x, screen_y))

