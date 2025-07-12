import pygame
import math
import random
from config import *
import config
from entities import ScatteredBullet, Bullet

# --------------------------
# 피튀김 파티클 클래스 정의
# --------------------------

PARTICLE_COUNT = 30
PARTICLE_SIZE = int(6 * PLAYER_VIEW_SCALE)
PARTICLE_SPEED_MIN = 1
PARTICLE_SPEED_MAX = 4
PARTICLE_LIFETIME = 2500  # ms
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

# --------------------------
# Enemy 클래스
# --------------------------

class Enemy1:
    def __init__(
        self,
        world_x,
        world_y,
        image,
        gun_image,
        bullet_image,
        sounds,
        get_player_center_world_fn,
        obstacle_manager,
        check_circle_collision_fn,
        check_ellipse_circle_collision_fn,
        player_bullet_image,
        map_width,
        map_height,
        kill_callback=None,
    ):
        self.world_x = world_x
        self.world_y = world_y
        self.image_original = image
        self.gun_image_original = gun_image
        self.bullet_image = bullet_image
        self.sounds = sounds
        self.hp = 100
        self.player_bullet_image = player_bullet_image
        self.kill_callback = kill_callback

        self.obstacle_manager = obstacle_manager
        self.check_circle_collision = check_circle_collision_fn
        self.check_ellipse_circle_collision = check_ellipse_circle_collision_fn

        self.rect = self.image_original.get_rect(center=(0, 0))
        self.speed = NORMAL_MAX_SPEED * PLAYER_VIEW_SCALE

        self.direction_angle = random.uniform(0, 2 * math.pi)
        self.velocity_x = 0.0
        self.velocity_y = 0.0

        self.move_timer = 0
        self.move_delay = random.randint(500, 1000)

        self.shoot_timer = 0
        self.shoot_delay = random.randint(500, 1500)

        self.radius = 30 * PLAYER_VIEW_SCALE

        self.bullets = []
        self.scattered_bullets = []

        self.fire_sound = self.sounds["gun1_fire_enemy"]

        self.recoil_offset = 0
        self.recoil_velocity = 0
        self.recoil_in_progress = False

        self.current_distance = GUN1_DISTANCE_FROM_CENTER * PLAYER_VIEW_SCALE
        self.get_player_center_world_fn = get_player_center_world_fn

        self.last_pos = (self.world_x, self.world_y)
        self.stuck_timer = 0
        self.goal_pos = None
        self.stuck_count = 0

        self.alive = True
        self.blood_effect = None

        self.map_width = map_width
        self.map_height = map_height

    def hit(self, damage, blood_effects):
        if not self.alive or not config.combat_state:
            return

        self.hp -= damage
        print(f"[DEBUG] Enemy HP 감소 → 현재 HP: {self.hp}")

        if self.hp <= 0:
            self.die(blood_effects)

    def die(self, blood_effects):
        print("[DEBUG] Enemy 사망!")
        if self.kill_callback:
            self.kill_callback()
        self.hp = 0
        self.alive = False
        blood_x = self.world_x
        blood_y = self.world_y
        blood = ParticleBlood(blood_x, blood_y, scale=PLAYER_VIEW_SCALE)
        blood_effects.append(blood)

    def _revert_movement(self):
        self.world_x -= self.velocity_x
        self.world_y -= self.velocity_y
        self.velocity_x = 0
        self.velocity_y = 0

    def update(self, dt, world_x, world_y, player_rect, enemies=[]):
        if not self.alive or not config.combat_state:
            return
        
        dist = math.hypot(
        self.world_x - self.last_pos[0],
        self.world_y - self.last_pos[1]
        )

        player_world_pos = self.get_player_center_world_fn(world_x, world_y)
        dx = player_world_pos[0] - self.world_x
        dy = player_world_pos[1] - self.world_y
        dist_to_player = math.hypot(dx, dy)

        self.direction_angle = math.atan2(dy, dx)

        near_threshold = 150 * PLAYER_VIEW_SCALE
        far_threshold = 500 * PLAYER_VIEW_SCALE

        if dist_to_player > far_threshold:
            self.goal_pos = player_world_pos
        elif dist_to_player < near_threshold:
            angle = self.direction_angle + math.pi
            self.goal_pos = (
                self.world_x + math.cos(angle) * 200,
                self.world_y + math.sin(angle) * 200
            )
        else:
            if self.goal_pos is None or self.move_timer <= 0:
                angle = random.uniform(0, 2 * math.pi)
                dist = random.randint(50, 150)
                self.goal_pos = (
                    self.world_x + math.cos(angle) * dist,
                    self.world_y + math.sin(angle) * dist
                )
                self.move_timer = random.randint(500, 1000)

        if self.goal_pos:
            goal_dx = self.goal_pos[0] - self.world_x
            goal_dy = self.goal_pos[1] - self.world_y
            goal_dist = math.hypot(goal_dx, goal_dy)

            if goal_dist > 5:
                goal_angle = math.atan2(goal_dy, goal_dx)
                self.velocity_x = math.cos(goal_angle) * self.speed
                self.velocity_y = math.sin(goal_angle) * self.speed
            else:
                self.goal_pos = None
                self.velocity_x = 0
                self.velocity_y = 0

        penetration_total = [0.0, 0.0]

        for obs in self.obstacle_manager.placed_obstacles:
            for c in obs.colliders:
                penetration = c.compute_penetration_circle(
                    (self.world_x, self.world_y),
                    self.radius,
                    (obs.world_x, obs.world_y)
                )
                if penetration:
                    penetration_total[0] += penetration[0]
                    penetration_total[1] += penetration[1]

        # Enemy끼리 충돌 처리
        for other in enemies:
            if other == self:
                continue
            dx = self.world_x - other.world_x
            dy = self.world_y - other.world_y
            dist_sq = dx * dx + dy * dy
            r_sum = self.radius + other.radius
            if dist_sq < r_sum * r_sum:
                dist = math.sqrt(dist_sq) if dist_sq > 0 else 0.0001
                penetration = r_sum - dist
                penetration_total[0] += (dx / dist) * penetration
                penetration_total[1] += (dy / dist) * penetration

        if math.hypot(*penetration_total) > 0.001:
            self.world_x += penetration_total[0]
            self.world_y += penetration_total[1]
        else:
            self.world_x += self.velocity_x
            self.world_y += self.velocity_y

        self.world_x = max(0, min(self.world_x, self.map_width))
        self.world_y = max(0, min(self.world_y, self.map_height))

        if dist < 1.0 or (abs(self.velocity_x) < 0.01 and abs(self.velocity_y) < 0.01):
            self.stuck_timer += dt
            if self.stuck_timer > 1000:
                self._escape_stuck()
                self.stuck_timer = 0
        else:
            self.stuck_timer = 0
            self.last_pos = (self.world_x, self.world_y)

        if self.stuck_count >= 3:
            self._escape_stuck()
            self.stuck_count = 0

        self.shoot_timer -= dt
        if self.shoot_timer <= 0 and dist_to_player < far_threshold:
            self.shoot()
            self.shoot_timer = random.randint(500, 1500)

        for b in self.bullets[:]:
            b.update(self.obstacle_manager)
            if getattr(b, "to_remove", False):
                self.bullets.remove(b)
                continue
            if b.is_offscreen(SCREEN_WIDTH, SCREEN_HEIGHT, world_x, world_y):
                self.bullets.remove(b)

        for s in self.scattered_bullets[:]:
            s.update()
            if s.alpha <= 0:
                self.scattered_bullets.remove(s)

    def _escape_stuck(self):
        angles = [
            self.direction_angle + math.pi,
            self.direction_angle + math.pi + math.radians(45),
            self.direction_angle + math.pi - math.radians(45),
            self.direction_angle + math.radians(90),
            self.direction_angle - math.radians(90),
        ]
        random.shuffle(angles)

        for angle in angles:
            test_x = self.world_x + math.cos(angle) * 50
            test_y = self.world_y + math.sin(angle) * 50
            collided = False

            for obs in self.obstacle_manager.placed_obstacles:
                for c in obs.colliders:
                    collider_world_center = (
                        obs.world_x + c.center[0],
                        obs.world_y + c.center[1]
                    )
                    if c.shape == "circle":
                        collider_radius = float(c.size)
                        if self.check_circle_collision(
                            (test_x, test_y),
                            self.radius,
                            collider_world_center,
                            collider_radius
                        ):
                            collided = True
                            break
                    elif c.shape == "ellipse":
                        rx, ry = c.size
                        if self.check_ellipse_circle_collision(
                            (test_x, test_y),
                            self.radius,
                            collider_world_center,
                            rx,
                            ry
                        ):
                            collided = True
                            break
                    elif c.shape == "rectangle":
                        w, h = c.size
                        collider_radius = math.sqrt((w/2)**2 + (h/2)**2)
                        if self.check_circle_collision(
                            (test_x, test_y),
                            self.radius,
                            collider_world_center,
                            collider_radius
                        ):
                            collided = True
                            break
                if collided:
                    break

            if not collided:
                self.goal_pos = (test_x, test_y)
                return

        self.goal_pos = None
        self.velocity_x = 0
        self.velocity_y = 0

    def shoot(self):
        self.fire_sound.play()

        self.recoil_offset = 0
        self.recoil_velocity = -GUN1_RECOIL
        self.recoil_in_progress = True

        spawn_offset = 30
        vertical_offset = 6
        offset_angle = self.direction_angle + math.radians(90)
        offset_dx = math.cos(offset_angle) * vertical_offset
        offset_dy = math.sin(offset_angle) * vertical_offset

        bullet_world_x = self.world_x + math.cos(self.direction_angle) * spawn_offset + offset_dx
        bullet_world_y = self.world_y + math.sin(self.direction_angle) * spawn_offset + offset_dy

        target_world_x = bullet_world_x + math.cos(self.direction_angle) * 2000
        target_world_y = bullet_world_y + math.sin(self.direction_angle) * 2000

        new_bullet = Bullet(
            bullet_world_x,
            bullet_world_y,
            target_world_x,
            target_world_y,
            15,
            self.bullet_image,
            speed=5,
            max_distance=2000
        )

        self.bullets.append(new_bullet)

        eject_angle = self.direction_angle + math.radians(90 + random.uniform(-15, 15))
        eject_speed = 1
        vx = math.cos(eject_angle) * eject_speed
        vy = math.sin(eject_angle) * eject_speed

        scatter_x = bullet_world_x
        scatter_y = bullet_world_y

        self.scattered_bullets.append(
            ScatteredBullet(scatter_x, scatter_y, vx, vy, self.player_bullet_image)
        )

    def draw(self, screen, world_x, world_y, shake_offset_x=0, shake_offset_y=0):
        if not self.alive:
            return

        screen_x = self.world_x - world_x
        screen_y = self.world_y - world_y

        screen_x += shake_offset_x
        screen_y += shake_offset_y

        gun_pos_x = screen_x + math.cos(self.direction_angle) * (self.current_distance + self.recoil_offset)
        gun_pos_y = screen_y + math.sin(self.direction_angle) * (self.current_distance + self.recoil_offset)
        scaled_gun = pygame.transform.smoothscale(
        self.gun_image_original,
            (
                int(self.gun_image_original.get_width() * PLAYER_VIEW_SCALE),
                int(self.gun_image_original.get_height() * PLAYER_VIEW_SCALE)
            )
        )
        rotated_gun = pygame.transform.rotate(
            scaled_gun, -math.degrees(self.direction_angle) + 90
        )

        gun_rect = rotated_gun.get_rect(center=(gun_pos_x, gun_pos_y))
        screen.blit(rotated_gun, gun_rect)

        scaled_img = pygame.transform.smoothscale(
        self.image_original,
            (
                int(self.image_original.get_width() * PLAYER_VIEW_SCALE),
                int(self.image_original.get_height() * PLAYER_VIEW_SCALE)
            )
        )
        rotated_img = pygame.transform.rotate(
            scaled_img, -math.degrees(self.direction_angle) + 90
        )
        rect = rotated_img.get_rect(center=(screen_x, screen_y))
        screen.blit(rotated_img, rect)

        for b in self.bullets:
            b.draw(screen, world_x, world_y)

class Enemy2(Enemy1):
    def __init__(
        self,
        world_x,
        world_y,
        image,
        gun_image,
        bullet_image,
        sounds,
        get_player_center_world_fn,
        obstacle_manager,
        check_circle_collision_fn,
        check_ellipse_circle_collision_fn,
        player_bullet_image,
        map_width,
        map_height,
        kill_callback=None,
    ):
        super().__init__(
            world_x,
            world_y,
            image,
            gun_image,
            bullet_image,
            sounds,
            get_player_center_world_fn,
            obstacle_manager,
            check_circle_collision_fn,
            check_ellipse_circle_collision_fn,
            player_bullet_image,
            map_width,
            map_height,
            kill_callback,
        )
        self.hp = 150
        self.speed = 3.5 * PLAYER_VIEW_SCALE
        self.fire_sound = self.sounds["gun2_fire_enemy"]
        self.current_distance = GUN2_DISTANCE_FROM_CENTER * PLAYER_VIEW_SCALE
        self.shoot_delay = random.randint(700, 1700)

        # 원거리 사격 관련
        self.is_preparing_far_shot = False
        self.prepare_start_time = 0
        self.far_shot_step = 0
        self.far_shot_timer = 0
        self.far_shot_check_timer = random.randint(4000, 8000)
        self.fixed_far_shot_angle = None

        self.map_height = map_height
        self.map_width = map_width

    def update(self, dt, world_x, world_y, player_rect, enemies=[]):
        if not self.alive:
            return

        player_world_pos = self.get_player_center_world_fn(world_x, world_y)
        dx = player_world_pos[0] - self.world_x
        dy = player_world_pos[1] - self.world_y
        dist_to_player = math.hypot(dx, dy)

        near_threshold = 150 * PLAYER_VIEW_SCALE
        far_threshold = 500 * PLAYER_VIEW_SCALE

        if self.is_preparing_far_shot:
            elapsed = pygame.time.get_ticks() - self.prepare_start_time

            if elapsed < 1500:
                # ✅ 조준 중 → angle 계속 갱신
                self.direction_angle = math.atan2(dy, dx)
            else:
                # ✅ 사격 시작 → angle 고정
                if self.fixed_far_shot_angle is None:
                    self.fixed_far_shot_angle = self.direction_angle

                now = pygame.time.get_ticks()
                if self.far_shot_step < 3:
                    if now >= self.far_shot_timer:
                        self.shoot(
                            spread_angle=0,
                            fixed_angle=self.fixed_far_shot_angle
                        )
                        self.far_shot_step += 1
                        self.far_shot_timer = now + 200
                else:
                    self.is_preparing_far_shot = False
                    self.far_shot_step = 0
                    self.fixed_far_shot_angle = None
                    self.far_shot_check_timer = random.randint(4000, 8000)
            return

        self.far_shot_check_timer -= dt
        if self.far_shot_check_timer <= 0:
            if random.random() < 0.5:
                self.is_preparing_far_shot = True
                self.prepare_start_time = pygame.time.get_ticks()
                self.velocity_x = 0
                self.velocity_y = 0
                return
            else:
                self.far_shot_check_timer = random.randint(4000, 8000)

        if near_threshold < dist_to_player <= far_threshold:
            self.shoot_timer -= dt
            if self.shoot_timer <= 0:
                self.shoot()
                self.shoot_timer = random.randint(700, 1700)

        self.direction_angle = math.atan2(dy, dx)
        super().update(dt, world_x, world_y, player_rect, enemies)

    def shoot(self, spread_angle=20, fixed_angle=None):
        self.fire_sound.play()

        self.recoil_offset = 0
        self.recoil_velocity = -GUN2_RECOIL
        self.recoil_in_progress = True

        angle = fixed_angle if fixed_angle is not None else self.direction_angle

        spawn_offset = 30
        vertical_offset = 6
        offset_angle = angle + math.radians(90)
        offset_dx = math.cos(offset_angle) * vertical_offset
        offset_dy = math.sin(offset_angle) * vertical_offset

        bullet_world_x = self.world_x + math.cos(angle) * spawn_offset + offset_dx
        bullet_world_y = self.world_y + math.sin(angle) * spawn_offset + offset_dy

        target_world_x = bullet_world_x + math.cos(angle) * 2000
        target_world_y = bullet_world_y + math.sin(angle) * 2000

        new_bullet = Bullet(
            bullet_world_x,
            bullet_world_y,
            target_world_x,
            target_world_y,
            spread_angle,
            self.bullet_image,
            speed=5 * PLAYER_VIEW_SCALE,
            max_distance=2000 * PLAYER_VIEW_SCALE
        )

        self.bullets.append(new_bullet)

        eject_angle = angle + math.radians(90 + random.uniform(-15, 15))
        eject_speed = 1
        vx = math.cos(eject_angle) * eject_speed
        vy = math.sin(eject_angle) * eject_speed

        scatter_x = bullet_world_x
        scatter_y = bullet_world_y

        self.scattered_bullets.append(
            ScatteredBullet(scatter_x, scatter_y, vx, vy, self.player_bullet_image)
        )

    def draw(self, screen, world_x, world_y, shake_offset_x=0, shake_offset_y=0):
        if not self.alive:
            return

        screen_x = self.world_x - world_x
        screen_y = self.world_y - world_y

        # ✅ 빨간선은 무조건 적 ↔ 플레이어로 그린다
        if self.is_preparing_far_shot:
            elapsed = pygame.time.get_ticks() - self.prepare_start_time
            if elapsed < 1500:
                player_pos = self.get_player_center_world_fn(world_x, world_y)
                player_screen_x = player_pos[0] - world_x
                player_screen_y = player_pos[1] - world_y

                line_thickness = max(1, int(2 * PLAYER_VIEW_SCALE))
                pygame.draw.line(
                    screen,
                    (255, 0, 0),
                    (screen_x + shake_offset_x, screen_y + shake_offset_y),
                    (player_screen_x + shake_offset_x, player_screen_y + shake_offset_y),
                    line_thickness
                )

        gun_pos_x = screen_x + math.cos(self.direction_angle) * (self.current_distance + self.recoil_offset)
        gun_pos_y = screen_y + math.sin(self.direction_angle) * (self.current_distance + self.recoil_offset)

        scaled_gun = pygame.transform.smoothscale(
        self.gun_image_original,
            (
                int(self.gun_image_original.get_width() * PLAYER_VIEW_SCALE),
                int(self.gun_image_original.get_height() * PLAYER_VIEW_SCALE)
            )
        )
        rotated_gun = pygame.transform.rotate(
            scaled_gun, -math.degrees(self.direction_angle) + 90
        )

        gun_rect = rotated_gun.get_rect(center=(gun_pos_x, gun_pos_y))
        screen.blit(rotated_gun, gun_rect)

        scaled_img = pygame.transform.smoothscale(
        self.image_original,
            (
                int(self.image_original.get_width() * PLAYER_VIEW_SCALE),
                int(self.image_original.get_height() * PLAYER_VIEW_SCALE)
            )
        )
        rotated_img = pygame.transform.rotate(
            scaled_img, -math.degrees(self.direction_angle) + 90
        )
        rect = rotated_img.get_rect(center=(screen_x, screen_y))
        screen.blit(rotated_img, rect)

        for b in self.bullets:
            b.draw(screen, world_x, world_y)