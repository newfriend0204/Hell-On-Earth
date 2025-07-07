import pygame
import math
import random
from collider import Collider

class Bullet:
    def __init__(self, world_x, world_y, target_world_x, target_world_y,
                 spread_angle_degrees, bullet_image, speed=30, max_distance=500):
        scale_factor = 0.4
        size = (int(5 * 5 * scale_factor), int(10 * 5 * scale_factor))
        self.original_image = pygame.transform.scale(bullet_image, size)
        self.world_x = world_x
        self.world_y = world_y
        self.speed = speed
        self.trail = []
        self.to_remove = False
        self.start_x = world_x
        self.start_y = world_y
        self.max_distance = max_distance

        angle_to_target = math.atan2(target_world_y - world_y, target_world_x - world_x)
        spread = math.radians(random.uniform(-spread_angle_degrees / 2, spread_angle_degrees / 2))
        final_angle = angle_to_target + spread

        self.vx = math.cos(final_angle) * speed
        self.vy = math.sin(final_angle) * speed
        self.angle_degrees = math.degrees(final_angle)

        self.collider = Collider(
            shape="circle",
            center=(self.world_x, self.world_y),
            size=5.0
        )

    def update(self, obstacle_manager):
        self.world_x += self.vx
        self.world_y += self.vy
        self.collider.center = (self.world_x, self.world_y)

        dx = self.world_x - self.start_x
        dy = self.world_y - self.start_y
        travel_distance = math.hypot(dx, dy)
        if travel_distance > self.max_distance:
            self.to_remove = True
            return

        for obs in obstacle_manager.placed_obstacles:
            for c in obs.colliders:
                if c.check_collision_circle(
                    self.collider.center,
                    self.collider.size,
                    (obs.world_x, obs.world_y)
                ):
                    if not c.bullet_passable:
                        self.to_remove = True
                        return
            
    def draw(self, screen, world_x, world_y):
        screen_x = self.world_x - world_x
        screen_y = self.world_y - world_y
        rotated_image = pygame.transform.rotate(self.original_image, -self.angle_degrees - 90)
        rect = rotated_image.get_rect(center=(screen_x, screen_y))
        screen.blit(rotated_image, rect)

    def is_offscreen(self, screen_width, screen_height, world_x, world_y):
        margin = 2000  # 원하는 값
        screen_x = self.world_x - world_x
        screen_y = self.world_y - world_y
        return (screen_x < -margin or screen_x > screen_width + margin or
                screen_y < -margin or screen_y > screen_height + margin)



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


class ScatteredBlood:
    def __init__(self, x, y, num_particles=20):
        self.particles = []
        for _ in range(num_particles):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(3, 7)
            self.particles.append({
                "pos": [x, y],
                "vx": math.cos(angle) * speed,
                "vy": math.sin(angle) * speed,
                "size": 5,
            })

        self.friction = 0.9
        self.spawn_time = pygame.time.get_ticks()
        self.lifetime = 5000
        self.fade_time = 1000
        self.alpha = 255

    def update(self):
        for p in self.particles:
            p["pos"][0] += p["vx"]
            p["pos"][1] += p["vy"]
            p["vx"] *= self.friction
            p["vy"] *= self.friction

        elapsed = pygame.time.get_ticks() - self.spawn_time
        if elapsed > self.lifetime:
            fade_elapsed = elapsed - self.lifetime
            if fade_elapsed < self.fade_time:
                self.alpha = int(255 * (1 - fade_elapsed / self.fade_time))
            else:
                self.alpha = 0

    def draw(self, screen, world_x, world_y):
        if self.alpha > 0:
            for p in self.particles:
                screen_x = p["pos"][0] - world_x
                screen_y = p["pos"][1] - world_y
                s = p["size"]
                rect = pygame.Rect(screen_x - s/2, screen_y - s/2, s, s)
                surface = pygame.Surface((s, s), pygame.SRCALPHA)
                surface.fill((255, 0, 0, self.alpha))
                screen.blit(surface, rect)


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
