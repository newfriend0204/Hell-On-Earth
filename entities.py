import pygame
import math
import time
import random
from collider import Collider
from config import PLAYER_VIEW_SCALE
import config

PARTICLE_COUNT = 30
PARTICLE_SIZE = int(6 * PLAYER_VIEW_SCALE)
PARTICLE_SPEED_MIN = 4
PARTICLE_SPEED_MAX = 12
PARTICLE_LIFETIME = 2000
PARTICLE_FADE_TIME = 500

class ParticleBlood:
    def __init__(self, x, y, scale=1.0):
        self.particles = []
        self.spawn_time = pygame.time.get_ticks()

        for i in range(PARTICLE_COUNT):
            angle = i * (2 * math.pi / PARTICLE_COUNT)
            speed = random.uniform(PARTICLE_SPEED_MIN, PARTICLE_SPEED_MAX)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed

            self.particles.append({
                "pos": [x, y],
                "vel": [vx, vy],
                "size": int(PARTICLE_SIZE * scale),
                "alpha": 255
            })

        self.alpha = 255

    def update(self):
        elapsed = pygame.time.get_ticks() - self.spawn_time

        for p in self.particles:
            p["pos"][0] += p["vel"][0]
            p["pos"][1] += p["vel"][1]
            p["vel"][0] *= 0.9
            p["vel"][1] *= 0.9

        if elapsed > PARTICLE_LIFETIME:
            fade_elapsed = elapsed - PARTICLE_LIFETIME
            if fade_elapsed < PARTICLE_FADE_TIME:
                self.alpha = int(255 * (1 - fade_elapsed / PARTICLE_FADE_TIME))
            else:
                self.alpha = 0

    def draw(self, surface, world_x, world_y):
        for p in self.particles:
            pos = p["pos"]
            size = p["size"]
            alpha = min(p["alpha"], self.alpha)

            rect = pygame.Rect(
                pos[0] - size / 2 - world_x,
                pos[1] - size / 2 - world_y,
                size,
                size
            )
            color = (255, 0, 0, alpha)

            s = pygame.Surface((size, size), pygame.SRCALPHA)
            s.fill(color)
            surface.blit(s, rect.topleft)

class DroppedItem:
    SPREAD_FRICTION = 0.88
    SPREAD_DURATION = 0.17
    TRAIL_KEEP_MS = 100
    TRAIL_SPACING = 2

    def __init__(self, x, y, image, item_type, value, get_player_pos_fn, color=None):
        self.x, self.y = x, y
        self.image = pygame.transform.smoothscale(image, (16, 16))
        self.item_type = item_type
        self.value = value
        self.get_player_pos = get_player_pos_fn

        self.state = "spread"
        self.spawn_time = pygame.time.get_ticks()
        self.idle_time = None

        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(11, 17)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed

        self.magnet_start_time = None
        self.magnet_origin = None
        self.magnet_target = None
        self.magnet_start_dist = None

        self.trail = []
        self.trail_color = color
        if color is not None:
            if not isinstance(color, (tuple, list)) or len(color) not in (3, 4):
                color = (255, 255, 255)
                self.trail_color = color
        else:
            self.trail_color = self.get_image_average_color(self.image)

    def get_image_average_color(self, img):
        arr = pygame.surfarray.pixels3d(img)
        mask = pygame.surfarray.pixels_alpha(img)
        valid = (mask > 0)
        if valid.sum() == 0:
            return (255,255,255)
        color = arr[valid].mean(axis=0)
        return tuple(int(c) for c in color)

    def update(self):
        now = pygame.time.get_ticks()
        px, py = self.get_player_pos()

        if not self.trail or (abs(self.x-self.trail[-1][0]) > self.TRAIL_SPACING or abs(self.y-self.trail[-1][1]) > self.TRAIL_SPACING):
            self.trail.append((self.x, self.y, now))
        while self.trail and (now - self.trail[0][2]) > self.TRAIL_KEEP_MS:
            self.trail.pop(0)

        if self.state == "spread":
            t = (now - self.spawn_time) / 1000
            if t < self.SPREAD_DURATION:
                self.x += self.vx
                self.y += self.vy
                self.vx *= self.SPREAD_FRICTION
                self.vy *= self.SPREAD_FRICTION
            else:
                self.state = "idle"
                self.idle_time = now
                self.vx = 0
                self.vy = 0

        elif self.state == "idle":
            dist = math.hypot(self.x - px, self.y - py)
            if dist < 90:
                self.state = "magnet"
                self.magnet_start_time = now
                self.magnet_origin = (self.x, self.y)
                self.magnet_target = (px, py)
                self.magnet_start_dist = dist

        elif self.state == "magnet":
            elapsed = (now - self.magnet_start_time) / 1000.0
            t = min(elapsed / 0.11, 1.0)
            tx, ty = self.get_player_pos()
            self.magnet_target = (tx, ty)
            ox, oy = self.magnet_origin
            dx = tx - ox
            dy = ty - oy

            def ease_out_back(t, s=1.5):
                return 1 + s * (t-1)**3 + s * (t-1)**2 + (t-1)
            overshoot = 0.13
            if t < 1.0:
                curve_t = ease_out_back(t)
                if curve_t < 0: curve_t = 0
                if curve_t > 1 + overshoot: curve_t = 1 + overshoot
                self.x = ox + dx * curve_t
                self.y = oy + dy * curve_t
            else:
                self.x = tx
                self.y = ty

    def is_close_to_player(self):
        px, py = self.get_player_pos()
        return math.hypot(self.x - px, self.y - py) < 30

    def draw(self, screen, world_x, world_y):
        n = len(self.trail)
        if n > 1:
            for i in range(n - 1):
                (tx, ty, t0) = self.trail[i]
                (tx2, ty2, t1) = self.trail[i + 1]
                dt = pygame.time.get_ticks() - t0
                alpha = int(160 * (1 - dt / self.TRAIL_KEEP_MS))
                color = self.trail_color if isinstance(self.trail_color, (tuple, list)) and len(self.trail_color) in (3, 4) else (255,255,255) + (alpha,)
                width = 6 * (i / n) + 2
                pygame.draw.line(
                    screen, color,
                    (tx - world_x, ty - world_y),
                    (tx2 - world_x, ty2 - world_y),
                    int(width)
                )
        rect = self.image.get_rect(center=(self.x - world_x, self.y - world_y))
        screen.blit(self.image, rect)

class Bullet:
    def __init__(self, world_x, world_y, target_world_x, target_world_y,
                 spread_angle_degrees, bullet_image, speed=30, max_distance=500, damage=10):
        self.original_image = bullet_image
        self.world_x = world_x
        self.world_y = world_y
        self.speed = speed * PLAYER_VIEW_SCALE
        self.trail = []
        self.trail_enabled = True
        self.to_remove = False
        self.start_x = world_x
        self.start_y = world_y
        self.max_distance = max_distance * PLAYER_VIEW_SCALE
        self.damage = damage

        angle_to_target = math.atan2(target_world_y - world_y, target_world_x - world_x)
        spread = math.radians(random.uniform(-spread_angle_degrees / 2, spread_angle_degrees / 2))
        final_angle = angle_to_target + spread

        self.vx = math.cos(final_angle) * self.speed
        self.vy = math.sin(final_angle) * self.speed
        self.angle_degrees = math.degrees(final_angle)

        bullet_radius = bullet_image.get_width() / 2
        self.collider = Collider(
            shape="circle",
            center=(self.world_x, self.world_y),
            size=bullet_radius
        )

    def update(self, obstacle_manager):
        self.world_x += self.vx
        self.world_y += self.vy
        self.collider.center = (self.world_x, self.world_y)

        if self.trail_enabled:
            self.trail.append((self.world_x, self.world_y))
            if len(self.trail) > 25:
                self.trail.pop(0)

        dx = self.world_x - self.start_x
        dy = self.world_y - self.start_y
        travel_distance = math.hypot(dx, dy)
        if travel_distance > self.max_distance:
            self.to_remove = True
            return

        for obs in (
            obstacle_manager.placed_obstacles
            + obstacle_manager.static_obstacles
            + obstacle_manager.combat_obstacles
        ):
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
        if self.trail_enabled:
            for pos in self.trail:
                screen_x = pos[0] - world_x
                screen_y = pos[1] - world_y

                trail_width = 20
                trail_height = 4
                alpha = 40

                trail_surf = pygame.Surface((trail_width, trail_height), pygame.SRCALPHA)
                trail_surf.fill((255, 255, 255, alpha))

                rotated_trail = pygame.transform.rotate(trail_surf, -self.angle_degrees)
                rect = rotated_trail.get_rect(center=(screen_x, screen_y))
                screen.blit(rotated_trail, rect)

        screen_x = self.world_x - world_x
        screen_y = self.world_y - world_y
        rotated_image = pygame.transform.rotate(self.original_image, -self.angle_degrees)
        rect = rotated_image.get_rect(center=(screen_x, screen_y))
        screen.blit(rotated_image, rect)

    def is_offscreen(self, screen_width, screen_height, world_x, world_y):
        margin = 2000
        screen_x = self.world_x - world_x
        screen_y = self.world_y - world_y
        return (screen_x < -margin or screen_x > screen_width + margin or
                screen_y < -margin or screen_y > screen_height + margin)

class Grenade:
    def __init__(self, x, y, vx, vy, image, explosion_radius, max_damage, min_damage, explosion_image, explosion_sound):
        self.x = x
        self.y = y
        self.vx = vx * 8 * config.PLAYER_VIEW_SCALE
        self.vy = vy * 8 * config.PLAYER_VIEW_SCALE
        self.image = image
        self.start_x = x
        self.start_y = y
        self.max_distance = 400 * config.PLAYER_VIEW_SCALE
        self.explosion_radius = explosion_radius
        self.max_damage = max_damage
        self.min_damage = min_damage
        self.explosion_image = explosion_image
        self.explosion_sound = explosion_sound
        self.alive = True
        self.angle_degrees = math.degrees(math.atan2(self.vy, self.vx))
        self.exploded = False
        self.collider = Collider("circle", center=(self.x, self.y), size=image.get_width() // 2)

        self.explosion_start_time = None
        self.explosion_duration = 0.4
        self.explosion_scale = 1.5
        self.explosion_alpha = 255
        self.explosion_played = False

    def update(self, obstacle_manager=None):
        if not self.alive and not self.exploded:
            return

        if not self.exploded:
            self.x += self.vx
            self.y += self.vy
            self.collider.center = (self.x, self.y)

            dx = self.x - self.start_x
            dy = self.y - self.start_y
            traveled = math.hypot(dx, dy)
            if traveled >= self.max_distance:
                self.explode()
                return

            if config.combat_state:
                for enemy in config.all_enemies:
                    if enemy.alive:
                        dist = math.hypot(enemy.world_x - self.x, enemy.world_y - self.y)
                        if dist < self.collider.size + enemy.radius:
                            self.explode()
                            return

            if obstacle_manager:
                for obs in obstacle_manager.placed_obstacles + obstacle_manager.static_obstacles + obstacle_manager.combat_obstacles:
                    for c in obs.colliders:
                        if c.check_collision_circle((self.x, self.y), self.image.get_width() / 2, (obs.world_x, obs.world_y)):
                            if not getattr(c, "bullet_passable", False):
                                self.explode()
                                return

        elif self.exploded:
            elapsed = time.time() - self.explosion_start_time
            if elapsed >= self.explosion_duration:
                self.alive = False
                return
            else:
                ratio = 1 - (elapsed / self.explosion_duration)
                self.explosion_alpha = int(255 * ratio)
                self.explosion_scale = 1.5 * ratio

    def explode(self):
        if self.exploded:
            return
        self.exploded = True
        self.explosion_start_time = time.time()

        if not self.explosion_played:
            self.explosion_sound.play()
            self.explosion_played = True

        config.bullets.append(
            ExplosionEffectPersistent(self.x, self.y, self.explosion_image)
        )

        if not config.combat_state:
            return

        for enemy in config.all_enemies[:]:
            if not getattr(enemy, "alive", True):
                continue
            dist = math.hypot(enemy.world_x - self.x, enemy.world_y - self.y)
            if dist <= self.explosion_radius:
                factor = max(0, min(1, 1 - dist / self.explosion_radius))
                damage = self.min_damage + (self.max_damage - self.min_damage) * factor
                print(f"[DEBUG] 유탄 폭발 거리 {dist:.1f}, 데미지 {damage:.1f}")
                enemy.hit(damage, config.blood_effects)

                if not enemy.alive:
                    if enemy in config.all_enemies:
                        config.all_enemies.remove(enemy)
                    config.blood_effects.append(
                        ScatteredBlood(enemy.world_x, enemy.world_y)
                    )

    def draw(self, screen, world_x, world_y):
        if self.alive and not self.exploded:
            rotated_image = pygame.transform.rotate(self.image, -self.angle_degrees)
            rect = rotated_image.get_rect(center=(self.x - world_x, self.y - world_y))
            screen.blit(rotated_image, rect)
        elif self.exploded:
            size = int(self.explosion_image.get_width() * self.explosion_scale)
            image_scaled = pygame.transform.smoothscale(self.explosion_image, (size, size)).copy()
            image_scaled.set_alpha(self.explosion_alpha)
            screen.blit(
                image_scaled,
                (self.x - size // 2 - world_x, self.y - size // 2 - world_y)
            )

    def is_offscreen(self, screen_width, screen_height, world_x, world_y):
        margin = 2000
        screen_x = self.x - world_x
        screen_y = self.y - world_y
        return (
            screen_x < -margin or screen_x > screen_width + margin or
            screen_y < -margin or screen_y > screen_height + margin
        )

class ExplosionEffectPersistent:
    def __init__(self, x, y, image, duration=0.4, scale=1.5):
        self.x = x
        self.y = y
        self.image = image
        self.start_time = time.time()
        self.duration = duration
        self.scale = scale
        self.alpha = 255
        self.finished = False
        self.drawn_once = False

    def update(self):
        elapsed = time.time() - self.start_time
        if elapsed >= self.duration:
            self.finished = True
        else:
            ratio = 1 - (elapsed / self.duration)
            self.alpha = int(255 * ratio)
            self.scale = 1.5 * ratio

    def draw(self, screen, world_x, world_y):
        self.drawn_once = True
        size = int(self.image.get_width() * self.scale)
        scaled = pygame.transform.smoothscale(self.image, (size, size)).copy()
        scaled.set_alpha(self.alpha)
        screen.blit(scaled, (self.x - size // 2 - world_x, self.y - size // 2 - world_y))

class ScatteredBullet:
    def __init__(self, x, y, vx, vy, bullet_image, scale=1.0):
        self.image_original = pygame.transform.scale(
            bullet_image,
            (
                max(1, int(3 * PLAYER_VIEW_SCALE * scale)),
                max(1, int(7 * PLAYER_VIEW_SCALE * scale))
            )
        )
        self.image = self.image_original.copy()

        self.pos = [x, y]
        speed_scale = random.uniform(3, 8)
        self.vx = vx * speed_scale * PLAYER_VIEW_SCALE
        self.vy = vy * speed_scale * PLAYER_VIEW_SCALE

        self.friction = 0.85
        self.spawn_time = pygame.time.get_ticks()
        self.lifetime = 5000
        self.fade_time = 1000
        self.alpha = 255

        self.rotation_angle = 0
        self.rotation_speed = random.uniform(5, 15) * random.choice([-1, 1])
    
    @staticmethod
    def get_player_world_position():
        return config.world_x + config.player_rect.centerx, config.world_y + config.player_rect.centery

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
                "size": max(1, int(5 * PLAYER_VIEW_SCALE)),
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
    def __init__(
        self,
        image,
        world_x,
        world_y,
        colliders,
        image_filename=None,
        is_covering=False,
        cover_collider=None,
        trunk_image=None,
        transparent_alpha=128
    ):
        self.image = image
        self.world_x = world_x
        self.world_y = world_y
        self.rect = self.image.get_rect(topleft=(world_x, world_y))
        self.colliders = colliders
        self.image_filename = image_filename
        self.is_covering = is_covering
        self.cover_collider = cover_collider
        self.trunk_image = trunk_image
        self.transparent_alpha = transparent_alpha
        self.transparent = False

    def draw(self, screen, world_offset_x, world_offset_y, player_center=None, enemies=None):
        screen_x = self.world_x - world_offset_x
        screen_y = self.world_y - world_offset_y

        img_to_draw = self.image.copy()

        if self.is_covering and self.cover_collider:
            transparent_needed = False

            if player_center:
                if self.cover_collider.check_collision_circle(
                    player_center,
                    30,
                    (self.world_x, self.world_y)
                ):
                    transparent_needed = True

            if enemies:
                for enemy in enemies:
                    enemy_center = (enemy.world_x, enemy.world_y)
                    if self.cover_collider.check_collision_circle(
                        enemy_center,
                        enemy.radius if hasattr(enemy, "radius") else 30,
                        (self.world_x, self.world_y)
                    ):
                        transparent_needed = True
                        break

            if transparent_needed:
                self.transparent = True
                img_to_draw.set_alpha(self.transparent_alpha)
            else:
                self.transparent = False

        if self.trunk_image:
            trunk_width, trunk_height = self.trunk_image.get_size()
            main_width, main_height = self.image.get_size()

            trunk_x = screen_x + (main_width - trunk_width) // 2
            trunk_y = screen_y + (main_height - trunk_height) // 2

            screen.blit(self.trunk_image, (trunk_x, trunk_y))

        screen.blit(img_to_draw, (screen_x, screen_y))