import pygame
import math
import random
from config import *
import config
import asset_manager
from entities import ScatteredBullet, Bullet, ParticleBlood, DroppedItem, ShieldEffect, ExplosionEffectPersistent, HomingMissile

ENEMY_CLASSES = []

class EnemyMeta(type):
    def __init__(cls, name, bases, clsdict):
        if name not in ("AIBase", "EnemyBase"):
            ENEMY_CLASSES.append(cls)
        super().__init__(name, bases, clsdict)

class AIBase(metaclass=EnemyMeta):
    def __init__(
        self, world_x, world_y, images, sounds, map_width, map_height,
        speed=3.0, near_threshold=150, far_threshold=500, radius=30, push_strength=0.18, alert_duration=1000,
        damage_player_fn=None, rank=1
    ):
        # 기본 AI 속성 초기화
        self.world_x = world_x
        self.world_y = world_y
        self.images = images
        self.sounds = sounds
        self.map_width = map_width
        self.map_height = map_height
        self.damage_player = damage_player_fn
        self.rank = rank

        self.alive = True
        self._already_dropped = False
        self.scattered_bullets = []
        self.hp = 100
        self.radius = radius * PLAYER_VIEW_SCALE
        self.kill_callback = None

        self.speed = speed
        self.near_threshold = near_threshold * PLAYER_VIEW_SCALE
        self.far_threshold = far_threshold * PLAYER_VIEW_SCALE
        self.push_strength = push_strength
        self.ALERT_DURATION = alert_duration

        self.direction_angle = random.uniform(0, 2 * math.pi)
        self.velocity_x = 0.0
        self.velocity_y = 0.0
        self.goal_pos = None
        self.stuck_timer = 0
        self.last_pos = (self.world_x, self.world_y)
        self.move_timer = 0
        self.move_delay = random.randint(600, 1200)
        self.stuck_count = 0

        self.aware_of_player = False
        self.shoot_delay_min = 1200
        self.shoot_delay_max = 1500
        self.shoot_delay = random.randint(self.shoot_delay_min, self.shoot_delay_max)
        self.shoot_timer = None
        self.show_alert = False

        self.rect = images.get("enemy1", pygame.Surface((60,60))).get_rect(center=(0,0))

        self.current_distance = 45 * PLAYER_VIEW_SCALE
        self.recoil_strength = 6
        self.recoil_offset = 0
        self.recoil_velocity = 0
        self.recoil_in_progress = False

    def check_collision_circle(self, center1, radius1, center2, radius2):
        # 원-원 충돌 체크
        try:
            radius1 = float(radius1)
            radius2 = float(radius2)
        except (ValueError, TypeError):
            return False

        if radius1 <= 0 or radius2 <= 0:
            return False

        dx = center1[0] - center2[0]
        dy = center1[1] - center2[1]
        dist_sq = dx * dx + dy * dy
        r_sum = radius1 + radius2
        return dist_sq <= r_sum * r_sum


    def check_ellipse_circle_collision(self, circle_center, circle_radius, ellipse_center, rx, ry):
        # 타원-원 충돌 체크
        try:
            rx = float(rx)
            ry = float(ry)
            circle_radius = float(circle_radius)
        except (ValueError, TypeError):
            return False

        if rx <= 0 or ry <= 0 or circle_radius <= 0:
            return False

        dx = circle_center[0] - ellipse_center[0]
        dy = circle_center[1] - ellipse_center[1]

        try:
            test = (dx ** 2) / ((rx + circle_radius) ** 2) + \
                (dy ** 2) / ((ry + circle_radius) ** 2)
        except ZeroDivisionError:
            return False

        return test <= 1.0

    def hit(self, damage, blood_effects, force=False):
        # 피격 처리
        if not self.alive or (not config.combat_state and not force):
            return
        self.hp -= damage
        if self.hp <= 0:
            self.die(blood_effects)

    def die(self, blood_effects):
        # 사망 처리
        if self._already_dropped:
            return
        self._already_dropped = True
        self.hp = 0
        self.alive = False
        if hasattr(self.sounds, "__getitem__") and "enemy_die" in self.sounds:
            self.sounds["enemy_die"].play()
        if blood_effects is not None:
            blood = ParticleBlood(self.world_x, self.world_y, scale=PLAYER_VIEW_SCALE)
            blood_effects.append(blood)
        if self.kill_callback:
            self.kill_callback()

    def spawn_dropped_items(self, health_count, ammo_count):
        # 아이템 드랍 생성
        get_player_pos = lambda: (config.world_x + config.player_rect.centerx, config.world_y + config.player_rect.centery)
        AMMO_COLOR = (255, 191, 193)
        HEALTH_COLOR = (181, 255, 146)
        for _ in range(health_count):
            item = DroppedItem(self.world_x, self.world_y, config.images["health_up"], "health", 10, get_player_pos, color=HEALTH_COLOR)
            config.dropped_items.append(item)
        for _ in range(ammo_count):
            item = DroppedItem(self.world_x, self.world_y, config.images["ammo_gauge_up"], "ammo", 20, get_player_pos, color=AMMO_COLOR)
            config.dropped_items.append(item)

    def update(self, dt, world_x, world_y, player_rect, enemies=[]):
        # 매 프레임마다 이동, 충돌, 공격 처리
        if not self.alive or not config.combat_state:
            return
        
        if not hasattr(config, "obstacle_manager") or config.obstacle_manager is None:
            return

        self.update_goal(world_x, world_y, player_rect, enemies)

        dist = math.hypot(self.world_x - self.last_pos[0], self.world_y - self.last_pos[1])

        # 목표 위치로 이동 벡터 계산
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
        for obs in config.obstacle_manager.static_obstacles + config.obstacle_manager.combat_obstacles:
            # 장애물 충돌 보정
            for c in obs.colliders:
                penetration = c.compute_penetration_circle(
                    (self.world_x, self.world_y),
                    self.radius,
                    (obs.world_x, obs.world_y)
                )
                if penetration:
                    penetration_total[0] += penetration[0]
                    penetration_total[1] += penetration[1]

        for other in enemies:
            # 다른 적과 충돌 시 밀어내기
            if other == self or not other.alive:
                continue
            dx = self.world_x - other.world_x
            dy = self.world_y - other.world_y
            dist_sq = dx * dx + dy * dy
            r_sum = self.radius + other.radius
            if dist_sq < r_sum * r_sum:
                dist = math.sqrt(dist_sq) if dist_sq > 0 else 0.0001
                penetration = r_sum - dist
                penetration_total[0] += (dx / dist) * penetration * self.push_strength
                penetration_total[1] += (dy / dist) * penetration * self.push_strength

        if math.hypot(*penetration_total) > 0.001:
            # 충돌 회피를 위한 목표 재설정
            self.world_x += penetration_total[0]
            self.world_y += penetration_total[1]
            if self.goal_pos is not None:
                angle = math.atan2(self.goal_pos[1] - self.world_y, self.goal_pos[0] - self.world_x)
                angle_options = [
                    angle + math.radians(60),
                    angle - math.radians(60),
                    angle + math.radians(120),
                    angle - math.radians(120),
                ]
                random.shuffle(angle_options)
                for try_angle in angle_options:
                    test_x = self.world_x + math.cos(try_angle) * 100
                    test_y = self.world_y + math.sin(try_angle) * 100
                    if 0 <= test_x <= self.map_width and 0 <= test_y <= self.map_height:
                        self.goal_pos = (test_x, test_y)
                        break
        else:
            # 목표를 향해 이동
            self.world_x += self.velocity_x
            self.world_y += self.velocity_y

        self.world_x = max(0, min(self.world_x, self.map_width))
        self.world_y = max(0, min(self.world_y, self.map_height))

        # 일정 시간 멈추면 탈출 시도
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

        # 발사 타이머 갱신
        if self.aware_of_player and self.shoot_timer is not None:
            self._update_alert(self.shoot_timer)
            self.shoot_timer -= dt
            if self.shoot_timer <= 0:
                self.shoot()
                self.shoot_delay = random.randint(self.shoot_delay_min, self.shoot_delay_max)
                self.shoot_timer = self.shoot_delay

        for s in self.scattered_bullets[:]:
            # 탄피 등 파편 업데이트
            s.update()
            if s.alpha <= 0:
                self.scattered_bullets.remove(s)

        if hasattr(self, "knockback_steps") and self.knockback_steps > 0:
            # 넉백 적용
            self.world_x += getattr(self, "knockback_velocity_x", 0)
            self.world_y += getattr(self, "knockback_velocity_y", 0)
            self.knockback_steps -= 1

    def update_goal(self, world_x, world_y, player_rect, enemies):
        pass

    def _escape_stuck(self):
        # 장애물에 끼였을 때 이동 방향 변경
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

            if not (0 <= test_x <= self.map_width and 0 <= test_y <= self.map_height):
                continue

            collided = False
            for obs in config.obstacle_manager.static_obstacles + config.obstacle_manager.combat_obstacles:
                for c in obs.colliders:
                    collider_world_center = (
                        obs.world_x + getattr(c, "center", (0, 0))[0],
                        obs.world_y + getattr(c, "center", (0, 0))[1]
                    )

                    if getattr(c, "shape", None) == "circle":
                        try:
                            collider_radius = float(c.size)
                        except (ValueError, TypeError):
                            continue
                        if self.check_collision_circle((test_x, test_y), self.radius, collider_world_center, collider_radius):
                            collided = True
                            break

                    elif getattr(c, "shape", None) == "ellipse":
                        try:
                            rx, ry = c.size
                        except (ValueError, TypeError):
                            continue
                        if self.check_ellipse_circle_collision((test_x, test_y), self.radius, collider_world_center, rx, ry):
                            collided = True
                            break

                    elif getattr(c, "shape", None) == "rectangle":
                        try:
                            w, h = c.size
                        except (ValueError, TypeError):
                            continue
                        collider_radius = math.sqrt((w / 2) ** 2 + (h / 2) ** 2)
                        if self.check_collision_circle((test_x, test_y), self.radius, collider_world_center, collider_radius):
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

    def _update_alert(self, time_until_attack):
        # 경고 아이콘 표시 여부 갱신
        if time_until_attack is not None and time_until_attack <= self.ALERT_DURATION:
            self.show_alert = True
        else:
            self.show_alert = False

    def draw_alert(self, screen, screen_x, screen_y):
        if self.show_alert:
            ey = screen_y - self.rect.height // 2 + 5
            ex = screen_x
            line_rect = pygame.Rect(ex - 3, ey - 12, 6, 16)
            pygame.draw.rect(screen, (255, 0, 0), line_rect)
            dot_rect = pygame.Rect(ex - 3, ey + 6, 6, 6)
            pygame.draw.ellipse(screen, (255, 0, 0), dot_rect)

    def draw(self, screen, world_x, world_y, shake_offset_x=0, shake_offset_y=0):
        pass

    def shoot(self):
        pass

class Enemy1(AIBase):
    rank=1
    def __init__(self, world_x, world_y, images, sounds, map_width, map_height, damage_player_fn=None, kill_callback=None):
        # 플레이어와의 거리 기반 목표 위치 설정
        super().__init__(
            world_x, world_y, images, sounds, map_width, map_height,
            speed=NORMAL_MAX_SPEED * PLAYER_VIEW_SCALE * 0.7,
            near_threshold=150,
            far_threshold=500,
            radius=30,
            push_strength=0.18,
            alert_duration=1000,
            damage_player_fn=damage_player_fn,
        )
        self.image_original = images["enemy1"]
        self.gun_image_original = pygame.transform.flip(images["gun1"], True, False)
        self.bullet_image = images["enemy_bullet"]
        self.cartridge_image = images["cartridge_case1"]
        self.player_bullet_image = images["bullet1"]
        self.kill_callback = kill_callback
        self.fire_sound = self.sounds["gun1_fire_enemy"]
        self.current_distance = 45 * PLAYER_VIEW_SCALE
        self.recoil_strength = 6
        self.recoil_offset = 0
        self.recoil_velocity = 0
        self.recoil_in_progress = False

    def update_goal(self, world_x, world_y, player_rect, enemies):
        player_world_pos = (world_x + player_rect.centerx, world_y + player_rect.centery)
        dx = player_world_pos[0] - self.world_x
        dy = player_world_pos[1] - self.world_y
        dist_to_player = math.hypot(dx, dy)
        self.direction_angle = math.atan2(dy, dx)
        near = self.near_threshold
        far = self.far_threshold

        if dist_to_player > far:
            self.goal_pos = player_world_pos
        elif dist_to_player < near:
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

        if not self.aware_of_player and dist_to_player < far:
            self.aware_of_player = True
            self.shoot_delay = random.randint(self.shoot_delay_min, self.shoot_delay_max)
            self.shoot_timer = self.shoot_delay

    def die(self, blood_effects):
        if self._already_dropped:
            return
        super().die(blood_effects)
        self.spawn_dropped_items(3, 4)

    def shoot(self):
        # 권총 발사, 탄피 배출
        self.fire_sound.play()
        self.recoil_offset = 0
        self.recoil_velocity = -self.recoil_strength
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
            speed=10 * PLAYER_VIEW_SCALE,
            max_distance=2000 * PLAYER_VIEW_SCALE,
            damage=15
        )
        config.global_enemy_bullets.append(new_bullet)

        eject_angle = self.direction_angle + math.radians(90 + random.uniform(-15, 15))
        eject_speed = 1
        vx = math.cos(eject_angle) * eject_speed
        vy = math.sin(eject_angle) * eject_speed
        scatter_x = bullet_world_x
        scatter_y = bullet_world_y
        self.scattered_bullets.append(
            ScatteredBullet(scatter_x, scatter_y, vx, vy, self.cartridge_image)
        )

    def draw(self, screen, world_x, world_y, shake_offset_x=0, shake_offset_y=0):
        if not self.alive:
            return
        screen_x = self.world_x - world_x + shake_offset_x
        screen_y = self.world_y - world_y + shake_offset_y
        self.draw_alert(screen, screen_x, screen_y)
        gun_pos_x = screen_x + math.cos(self.direction_angle) * (self.current_distance + self.recoil_offset)
        gun_pos_y = screen_y + math.sin(self.direction_angle) * (self.current_distance + self.recoil_offset)
        rotated_gun = pygame.transform.rotate(
            self.gun_image_original, -math.degrees(self.direction_angle) - 90
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

class Enemy2(AIBase):
    rank=2
    def __init__(self, world_x, world_y, images, sounds, map_width, map_height, damage_player_fn=None, kill_callback=None):
        # 플레이어와의 거리 기반 목표 위치 및 원거리 공격 준비
        super().__init__(
            world_x, world_y, images, sounds, map_width, map_height,
            speed=NORMAL_MAX_SPEED * PLAYER_VIEW_SCALE * 0.5,
            near_threshold=200,
            far_threshold=700,
            radius=30,
            push_strength=0.18,
            alert_duration=1000,
            damage_player_fn=damage_player_fn,
        )
        self.image_original = images["enemy2"]
        self.gun_image_original = pygame.transform.flip(images["gun2"], True, False)
        self.bullet_image = images["enemy_bullet"]
        self.cartridge_image = images["cartridge_case1"]
        self.player_bullet_image = images["bullet1"]
        self.kill_callback = kill_callback
        self.hp = 150
        self.fire_sound = self.sounds["gun2_fire_enemy"]
        self.current_distance = 50 * PLAYER_VIEW_SCALE
        self.recoil_strength = 8
        self.recoil_offset = 0
        self.recoil_velocity = 0
        self.recoil_in_progress = False
        self.shoot_delay_min = 1250
        self.shoot_delay_max = 2000
        self.shoot_delay = random.randint(self.shoot_delay_min, self.shoot_delay_max)
        self.shoot_timer = None

        self.is_preparing_far_shot = False
        self.prepare_start_time = 0
        self.far_shot_step = 0
        self.far_shot_timer = 0
        self.far_shot_check_timer = random.randint(4000, 8000)
        self.fixed_far_shot_angle = None

    def update_goal(self, world_x, world_y, player_rect, enemies):
        player_world_pos = (world_x + player_rect.centerx, world_y + player_rect.centery)
        dx = player_world_pos[0] - self.world_x
        dy = player_world_pos[1] - self.world_y
        dist_to_player = math.hypot(dx, dy)
        self.direction_angle = math.atan2(dy, dx)
        near = 200 * PLAYER_VIEW_SCALE
        far = 700 * PLAYER_VIEW_SCALE

        if self.is_preparing_far_shot:
            elapsed = pygame.time.get_ticks() - self.prepare_start_time
            if elapsed < 1500:
                self.direction_angle = math.atan2(dy, dx)
            else:
                if self.fixed_far_shot_angle is None:
                    self.fixed_far_shot_angle = self.direction_angle
                now = pygame.time.get_ticks()
                if self.far_shot_step < 3:
                    if now >= self.far_shot_timer:
                        self.shoot(
                            spread_angle=0,
                            fixed_angle=self.fixed_far_shot_angle,
                            bullet_speed=12.5 * PLAYER_VIEW_SCALE
                        )
                        self.far_shot_step += 1
                        self.far_shot_timer = now + 200
                else:
                    self.is_preparing_far_shot = False
                    self.far_shot_step = 0
                    self.fixed_far_shot_angle = None
                    self.far_shot_check_timer = random.randint(4000, 8000)
            return

        self.far_shot_check_timer -= pygame.time.get_ticks() % 16
        if self.far_shot_check_timer <= 0:
            if random.random() < 0.5:
                self.is_preparing_far_shot = True
                self.prepare_start_time = pygame.time.get_ticks()
                self.velocity_x = 0
                self.velocity_y = 0
                return
            else:
                self.far_shot_check_timer = random.randint(4000, 8000)

        if dist_to_player > far:
            self.goal_pos = player_world_pos
        elif dist_to_player < near:
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

        if not self.aware_of_player and dist_to_player < far:
            self.aware_of_player = True
            self.shoot_delay = random.randint(self.shoot_delay_min, self.shoot_delay_max)
            self.shoot_timer = self.shoot_delay

    def die(self, blood_effects):
        if self._already_dropped:
            return
        super().die(blood_effects)
        self.spawn_dropped_items(4, 5)

    def shoot(self, spread_angle=20, fixed_angle=None, bullet_speed=None):
        # 소총 발사, 탄피 배출
        self.fire_sound.play()
        self.recoil_offset = 0
        self.recoil_velocity = -self.recoil_strength
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
            speed=(bullet_speed if bullet_speed is not None else 10 * PLAYER_VIEW_SCALE),
            max_distance=2000 * PLAYER_VIEW_SCALE,
            damage=20
        )
        config.global_enemy_bullets.append(new_bullet)

        eject_angle = angle + math.radians(90 + random.uniform(-15, 15))
        eject_speed = 1
        vx = math.cos(eject_angle) * eject_speed
        vy = math.sin(eject_angle) * eject_speed
        scatter_x = bullet_world_x
        scatter_y = bullet_world_y
        self.scattered_bullets.append(
            ScatteredBullet(scatter_x, scatter_y, vx, vy, self.cartridge_image)
        )

    def draw(self, screen, world_x, world_y, shake_offset_x=0, shake_offset_y=0):
        if not self.alive:
            return
        screen_x = self.world_x - world_x + shake_offset_x
        screen_y = self.world_y - world_y + shake_offset_y
        self.draw_alert(screen, screen_x, screen_y)
        gun_pos_x = screen_x + math.cos(self.direction_angle) * (self.current_distance + self.recoil_offset)
        gun_pos_y = screen_y + math.sin(self.direction_angle) * (self.current_distance + self.recoil_offset)
        rotated_gun = pygame.transform.rotate(
            self.gun_image_original, -math.degrees(self.direction_angle) - 90
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

class Enemy3(AIBase):
    rank=3

    FAR_DISTANCE = 500
    NEAR_DISTANCE = 100
    RADIUS_CLOSE_ATTACK = 120

    DASH_DISTANCE = 200
    DASH_SPEED_MULTIPLIER = 3
    DASH_DAMAGE = 30
    CHARGE_TIME = 1000
    COOLDOWN_MIN = 1000
    COOLDOWN_MAX = 2000

    CLOSE_ATTACK_CHARGE = 1000
    CLOSE_ATTACK_COOLDOWN_MIN = 2000
    CLOSE_ATTACK_COOLDOWN_MAX = 3000
    CLOSE_ATTACK_DAMAGE = 30
    CLOSE_ATTACK_SWEEP_TIME = 200
    CLOSE_ATTACK_SPEED_PENALTY = 0.7

    def __init__(self, world_x, world_y, images, sounds, map_width, map_height,
                 damage_player_fn=None, kill_callback=None):
        self.base_speed = NORMAL_MAX_SPEED * PLAYER_VIEW_SCALE * 0.8
        super().__init__(
            world_x, world_y, images, sounds, map_width, map_height,
            speed=self.base_speed,
            near_threshold=self.NEAR_DISTANCE,
            far_threshold=self.FAR_DISTANCE,
            radius=39,
            push_strength=0.0,
            alert_duration=1000,
            damage_player_fn=damage_player_fn,
        )
        self.image_original = images["enemy3"]
        self.kill_callback = kill_callback
        self.hp = 300
        self.damage_player_fn = damage_player_fn

        self.move_dir = random.choice([-1, 1])
        self.move_change_interval = 800
        self.last_move_change_time = pygame.time.get_ticks()

        self.state = "normal"
        self.fixed_angle = None
        self.charge_start_time = 0
        self.dash_start_x = 0
        self.dash_start_y = 0
        self.dash_cooldown_timer = random.randint(self.COOLDOWN_MIN, self.COOLDOWN_MAX)

        self.close_state = "idle"
        self.close_charge_start = 0
        self.close_cooldown_timer = 0
        self.close_sweep_start = 0
        self.close_attack_angle = 0

    def update_goal(self, world_x, world_y, player_rect, enemies):
        # 돌진, 근접 공격, 회피 패턴 처리
        player_world_pos = (world_x + player_rect.centerx, world_y + player_rect.centery)
        dx = player_world_pos[0] - self.world_x
        dy = player_world_pos[1] - self.world_y
        dist_to_player = math.hypot(dx, dy)
        now = pygame.time.get_ticks()

        if self.dash_cooldown_timer > 0:
            self.dash_cooldown_timer -= 16
        if self.close_cooldown_timer > 0:
            self.close_cooldown_timer -= 16

        if self.close_state == "idle" and dist_to_player <= self.NEAR_DISTANCE and self.close_cooldown_timer <= 0:
            self.close_state = "charging"
            self.close_charge_start = now
            self.close_attack_angle = math.atan2(dy, dx)
            self.speed = self.base_speed * self.CLOSE_ATTACK_SPEED_PENALTY

        elif self.close_state == "charging":
            self.close_attack_angle = math.atan2(dy, dx)
            if now - self.close_charge_start >= self.CLOSE_ATTACK_CHARGE:
                px, py = player_world_pos
                if self.damage_player_fn:
                    rel_angle = math.atan2(py - self.world_y, px - self.world_x)
                    angle_diff = (rel_angle - self.close_attack_angle + math.pi * 3) % (2 * math.pi) - math.pi
                    dist = math.hypot(px - self.world_x, py - self.world_y)
                    if abs(angle_diff) <= math.pi / 2 and dist <= self.RADIUS_CLOSE_ATTACK:
                        self.damage_player_fn(self.CLOSE_ATTACK_DAMAGE)

                self.close_state = "firing"
                self.close_sweep_start = now
                self.speed = self.base_speed

        elif self.close_state == "firing":
            self.close_attack_angle = math.atan2(dy, dx)
            if now - self.close_sweep_start >= self.CLOSE_ATTACK_SWEEP_TIME:
                self.close_state = "idle"
                self.close_cooldown_timer = random.randint(self.CLOSE_ATTACK_COOLDOWN_MIN, self.CLOSE_ATTACK_COOLDOWN_MAX)

        if self.state == "normal":
            self.direction_angle = math.atan2(dy, dx)

            if dist_to_player >= self.FAR_DISTANCE and self.dash_cooldown_timer <= 0 and self.close_state == "idle":
                self.state = "charging_dash"
                self.charge_start_time = now
                self.fixed_angle = self.direction_angle
                self.dash_start_x = self.world_x
                self.dash_start_y = self.world_y
                return

            if now - self.last_move_change_time > self.move_change_interval:
                self.move_dir = random.choice([-1, 1])
                self.last_move_change_time = now

            if dist_to_player > self.FAR_DISTANCE:
                self.goal_pos = player_world_pos
            elif self.NEAR_DISTANCE < dist_to_player <= self.FAR_DISTANCE:
                angle_to_player = self.direction_angle
                perp = angle_to_player + math.pi / 2
                self.goal_pos = (
                    self.world_x + math.cos(angle_to_player) * 100 + math.cos(perp) * 50 * self.move_dir,
                    self.world_y + math.sin(angle_to_player) * 100 + math.sin(perp) * 50 * self.move_dir
                )
            else:
                angle_to_player = self.direction_angle
                perp = angle_to_player + math.pi / 2
                self.goal_pos = (
                    self.world_x + math.cos(perp) * 100 * self.move_dir,
                    self.world_y + math.sin(perp) * 100 * self.move_dir
                )

        elif self.state == "charging_dash":
            self.direction_angle = self.fixed_angle
            self.goal_pos = (self.world_x, self.world_y)
            if now - self.charge_start_time >= self.CHARGE_TIME:
                self.state = "dashing"

        elif self.state == "dashing":
            dash_speed = self.speed * self.DASH_SPEED_MULTIPLIER
            self.world_x += math.cos(self.fixed_angle) * dash_speed
            self.world_y += math.sin(self.fixed_angle) * dash_speed

            px, py = player_world_pos
            if self.damage_player_fn:
                if self.check_collision_circle((self.world_x, self.world_y), self.radius, (px, py), 15):
                    self.damage_player_fn(self.DASH_DAMAGE)
                    self.end_dash()
                    return

            if math.hypot(self.world_x - self.dash_start_x, self.world_y - self.dash_start_y) >= self.DASH_DISTANCE:
                self.end_dash()

    def end_dash(self):
        # 돌진 종료 및 쿨타임 설정
        self.state = "normal"
        self.dash_cooldown_timer = random.randint(self.COOLDOWN_MIN, self.COOLDOWN_MAX)

    def die(self, blood_effects):
        if self._already_dropped:
            return
        super().die(blood_effects)
        self.spawn_dropped_items(5, 6)

    def draw(self, screen, world_x, world_y, shake_offset_x=0, shake_offset_y=0):
        if not self.alive:
            return
        screen_x = self.world_x - world_x + shake_offset_x
        screen_y = self.world_y - world_y + shake_offset_y

        if self.close_state == "charging":
            arc_surf = pygame.Surface((self.RADIUS_CLOSE_ATTACK * 2, self.RADIUS_CLOSE_ATTACK * 2), pygame.SRCALPHA)
            center = (self.RADIUS_CLOSE_ATTACK, self.RADIUS_CLOSE_ATTACK)
            start_angle = self.close_attack_angle - math.pi / 2
            end_angle = self.close_attack_angle + math.pi / 2
            points = [center]
            steps = 30
            for i in range(steps + 1):
                ang = start_angle + (end_angle - start_angle) * (i / steps)
                x = center[0] + math.cos(ang) * self.RADIUS_CLOSE_ATTACK
                y = center[1] + math.sin(ang) * self.RADIUS_CLOSE_ATTACK
                points.append((x, y))
            pygame.draw.polygon(arc_surf, (255, 0, 0, 76), points)
            screen.blit(arc_surf, (screen_x - self.RADIUS_CLOSE_ATTACK, screen_y - self.RADIUS_CLOSE_ATTACK))

        if self.close_state == "firing":
            progress = (pygame.time.get_ticks() - self.close_sweep_start) / self.CLOSE_ATTACK_SWEEP_TIME
            line_angle = self.close_attack_angle - math.pi / 2 + math.pi * progress
            line_surf = pygame.Surface((self.RADIUS_CLOSE_ATTACK * 2, self.RADIUS_CLOSE_ATTACK * 2), pygame.SRCALPHA)
            pygame.draw.line(line_surf, (255, 255, 255, 150),
                             (self.RADIUS_CLOSE_ATTACK, self.RADIUS_CLOSE_ATTACK),
                             (self.RADIUS_CLOSE_ATTACK + math.cos(line_angle) * self.RADIUS_CLOSE_ATTACK,
                              self.RADIUS_CLOSE_ATTACK + math.sin(line_angle) * self.RADIUS_CLOSE_ATTACK),
                             14)
            screen.blit(line_surf, (screen_x - self.RADIUS_CLOSE_ATTACK, screen_y - self.RADIUS_CLOSE_ATTACK))

        if self.state == "charging_dash":
            elapsed = pygame.time.get_ticks() - self.charge_start_time
            rect_length = int((elapsed / self.CHARGE_TIME) * self.DASH_DISTANCE)
            rect_width = 40
            dx = math.cos(self.fixed_angle)
            dy = math.sin(self.fixed_angle)
            rect_surface = pygame.Surface((rect_length, rect_width), pygame.SRCALPHA)
            rect_surface.fill((255, 0, 0, 76))
            rect_surface = pygame.transform.rotate(rect_surface, -math.degrees(self.fixed_angle))
            rect_rect = rect_surface.get_rect(center=(screen_x + dx * rect_length / 2, screen_y + dy * rect_length / 2))
            screen.blit(rect_surface, rect_rect)

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

class Enemy4(AIBase):
    rank=4

    BASE_SPEED = NORMAL_MAX_SPEED * PLAYER_VIEW_SCALE * 0.6
    CLOSE_THRESHOLD = 200
    FAR_THRESHOLD = 800
    STRAFE_SPEED = BASE_SPEED * 0.7
    MIN_ATTACK_PREPARE_TIME = 2000
    PREHEAT_SOUND_DELAY = 1000

    def __init__(self, world_x, world_y, images, sounds, map_width, map_height,
                 damage_player_fn=None, kill_callback=None):
        # 기본 속성 초기화 (이동 속도, 사거리, 경고 지속시간)
        super().__init__(
            world_x, world_y, images, sounds, map_width, map_height,
            speed=self.BASE_SPEED,
            near_threshold=0,
            far_threshold=self.FAR_THRESHOLD,
            radius=30 * 1.2,
            push_strength=0.0,
            alert_duration=self.MIN_ATTACK_PREPARE_TIME,
            damage_player_fn=damage_player_fn,
        )

        self.image_original = images["enemy4"]
        self.image = self.image_original
        self.kill_callback = kill_callback
        self.hp = 400

        shield_radius = int(self.radius * 1.2)
        self.shield = ShieldEffect(self, shield_radius, max_hp=200)
        self.shield_break_sound = sounds["enemy4_shield_break"]
        self.shield_charged_sound = sounds["enemy4_shield_chared"]

        self.gun_image_original = images["gun5"]
        self.bullet_image = images["enemy_bullet"]
        self.fire_sound = sounds["enemy4_fire"]
        self.preheat_sound = sounds["enemy4_preheat"]

        self.is_firing = False
        self.fire_start_time = 0
        self.fire_duration = 1000
        self.fire_interval = 80
        self.last_fire_time = 0

        self.next_attack_time = 0
        self.attack_cooldown_min = 4000
        self.attack_cooldown_max = 6000
        self.attack_prepare_start = None
        self.preheat_played = False

        self.strafe_dir = random.choice([-1, 1])
        self.strafe_change_time = pygame.time.get_ticks()
        self.strafe_interval = 1000

        self.move_change_time = 0
        self.move_change_interval = 1000
        self.current_lateral_distance = 0
        self.current_forward_distance = 0
        self.current_forward_angle = 0

        self.alert_offset_y = -10

    def update_goal(self, world_x, world_y, player_rect, enemies):
        # 보호막 상태 갱신
        self.shield.update()

        px = world_x + player_rect.centerx
        py = world_y + player_rect.centery
        dx = px - self.world_x
        dy = py - self.world_y
        dist_to_player = math.hypot(dx, dy)
        self.direction_angle = math.atan2(dy, dx)

        now = pygame.time.get_ticks()

        if self.is_firing:
            # 난사 중 이동 정지
            self.goal_pos = (self.world_x, self.world_y)
            if now - self.fire_start_time >= self.fire_duration:
                self.is_firing = False
                self.next_attack_time = now + random.randint(self.attack_cooldown_min, self.attack_cooldown_max)
                self.speed = self.BASE_SPEED
            else:
                if now - self.last_fire_time >= self.fire_interval:
                    self.shoot()
                    self.last_fire_time = now
                self.speed = 0.0
        else:
            if dist_to_player <= self.FAR_THRESHOLD and now >= self.next_attack_time:
                if self.attack_prepare_start is None:
                    self.attack_prepare_start = now
                    self.preheat_played = False
                    self.show_alert = True
                else:
                    elapsed_prep = now - self.attack_prepare_start
                    if not self.preheat_played and elapsed_prep >= self.PREHEAT_SOUND_DELAY:
                        self.preheat_sound.play()
                        self.preheat_played = True
                    if elapsed_prep >= self.MIN_ATTACK_PREPARE_TIME:
                        self.is_firing = True
                        self.fire_start_time = now
                        self.last_fire_time = 0
                        self.attack_prepare_start = None
                        self.show_alert = False
            else:
                self.attack_prepare_start = None
                self.show_alert = False

            # 거리별 무빙 패턴
            if dist_to_player < self.CLOSE_THRESHOLD:
                # 너무 가까우면 후퇴
                angle = self.direction_angle + math.pi
                offset_angle = angle + math.radians(random.uniform(-15, 15))
                self.goal_pos = (
                    self.world_x + math.cos(offset_angle) * 150,
                    self.world_y + math.sin(offset_angle) * 150
                )
            elif self.CLOSE_THRESHOLD <= dist_to_player <= self.FAR_THRESHOLD:
                # 중거리 무빙 (좌우 + 앞뒤)
                if now - self.move_change_time > self.move_change_interval:
                    self.move_change_time = now
                    self.current_lateral_distance = random.uniform(80, 150)
                    if random.random() < 0.5:
                        self.current_forward_angle = self.direction_angle
                    else:
                        self.current_forward_angle = self.direction_angle + math.pi
                    self.current_forward_distance = random.uniform(80, 200)

                perp = self.direction_angle + math.pi / 2 * self.strafe_dir
                self.goal_pos = (
                    self.world_x + math.cos(perp) * self.current_lateral_distance +
                    math.cos(self.current_forward_angle) * self.current_forward_distance,
                    self.world_y + math.sin(perp) * self.current_lateral_distance +
                    math.sin(self.current_forward_angle) * self.current_forward_distance
                )
            else:
                # 멀면 접근
                perp = self.direction_angle + math.pi / 2 * self.strafe_dir
                forward = self.direction_angle
                self.goal_pos = (
                    self.world_x + math.cos(forward) * 120 + math.cos(perp) * random.uniform(40, 60),
                    self.world_y + math.sin(forward) * 120 + math.sin(perp) * random.uniform(40, 60)
                )

        if now - self.strafe_change_time > self.strafe_interval:
            self.strafe_dir *= -1
            self.strafe_change_time = now

        if not self.aware_of_player and dist_to_player < self.FAR_THRESHOLD:
            self.aware_of_player = True

    def shoot(self):
        # 난사 발사 처리
        if not self.is_firing:
            return
        self.fire_sound.play()

        spawn_offset = 30
        vertical_offset = 6
        angle = self.direction_angle + math.radians(random.uniform(-25, 25))
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
            0,
            self.bullet_image,
            speed=2.5 * PLAYER_VIEW_SCALE,
            max_distance=2000 * PLAYER_VIEW_SCALE,
            damage=40
        )
        config.global_enemy_bullets.append(new_bullet)

    def hit(self, damage, blood_effects, force=False):
        # 피격 시 보호막 우선 처리, 파괴 시 타이머 갱신
        if not self.alive:
            return
        prev_broken = self.shield.hp <= 0
        if self.shield.hp > 0:
            self.shield.take_damage(damage)
            if not prev_broken and self.shield.hp <= 0:
                self.shield_break_sound.play()
        else:
            self.shield.last_hit_time = pygame.time.get_ticks()
            super().hit(damage, blood_effects, force)

    def die(self, blood_effects):
        # 사망 시 아이템 드랍
        if self._already_dropped:
            return
        super().die(blood_effects)
        self.spawn_dropped_items(8, 8)

    def draw(self, screen, world_x, world_y, shake_offset_x=0, shake_offset_y=0):
        # 경고 아이콘, 총, 본체, 보호막 순서로 그림
        if not self.alive:
            return
        screen_x = self.world_x - world_x + shake_offset_x
        screen_y = self.world_y - world_y + shake_offset_y

        gun_pos_x = screen_x + math.cos(self.direction_angle) * 45
        gun_pos_y = screen_y + math.sin(self.direction_angle) * 45
        rotated_gun = pygame.transform.rotate(
            self.gun_image_original, -math.degrees(self.direction_angle) - 90
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

        self.shield.draw(screen, world_x - shake_offset_x, world_y - shake_offset_y)

        if self.show_alert:
            self.draw_alert(screen, screen_x, screen_y + self.alert_offset_y)

class Enemy5(AIBase):
    rank=5

    STATE_IDLE = 0
    STATE_PREPARE_ATTACK = 1
    STATE_ATTACK = 2

    HP = 150
    BASE_SPEED = NORMAL_MAX_SPEED * PLAYER_VIEW_SCALE * 0.7
    APPROACH_SPEED = BASE_SPEED * 0.5
    BULLET_SPEED = 12 * PLAYER_VIEW_SCALE
    PELLET_COUNT = 8
    PELLET_SPREAD_DEG = 30
    PELLET_DAMAGE = 10
    PELLET_RANGE = 500 * PLAYER_VIEW_SCALE
    MIN_COOLDOWN = 2000
    MAX_COOLDOWN = 5000
    PREPARE_TIME = 1000
    IDLE_MOVE_CHANGE_INTERVAL = (800, 1200)
    MIN_DISTANCE = 100 * PLAYER_VIEW_SCALE

    def __init__(self, world_x, world_y, images, sounds, map_width, map_height,
                 damage_player_fn=None, kill_callback=None):
        # 기본 속성 초기화 (속도, 사거리, 경고 시간, 충돌 반경 등)
        super().__init__(
            world_x, world_y, images, sounds, map_width, map_height,
            speed=self.BASE_SPEED,
            near_threshold=150,
            far_threshold=500,
            radius=30 * PLAYER_VIEW_SCALE,
            push_strength=0.0,
            alert_duration=self.PREPARE_TIME,
            damage_player_fn=damage_player_fn,
        )
        self.image_original = images["enemy5"]
        self.gun_image_original = pygame.transform.flip(images["gun3"], True, False)
        self.bullet_image = images["enemy_bullet"]
        self.fire_sound = sounds["enemy5_fire"]
        self.kill_callback = kill_callback
        self.hp = self.HP
        self.state = self.STATE_IDLE
        self.last_attack_time = -self.MAX_COOLDOWN
        self.prepare_start_time = 0
        self.random_idle_dir = pygame.Vector2(0, 0)
        self.last_idle_change = pygame.time.get_ticks()
        self.next_idle_change_interval = random.randint(*self.IDLE_MOVE_CHANGE_INTERVAL)
        self.current_distance = 45 * PLAYER_VIEW_SCALE

    def update_goal(self, world_x, world_y, player_rect, enemies):
        player_pos = (world_x + player_rect.centerx, world_y + player_rect.centery)
        dx = player_pos[0] - self.world_x
        dy = player_pos[1] - self.world_y
        dist_to_player = math.hypot(dx, dy)
        now = pygame.time.get_ticks()
        self.direction_angle = math.atan2(dy, dx)

        if self.state == self.STATE_IDLE:
            # 일정 주기마다 랜덤 무빙 방향 변경
            if now - self.last_idle_change >= self.next_idle_change_interval:
                angle_to_player = math.atan2(dy, dx)
                random_angle = angle_to_player + math.radians(random.uniform(-20, 20))
                self.random_idle_dir = pygame.Vector2(math.cos(random_angle), math.sin(random_angle))
                self.last_idle_change = now
                self.next_idle_change_interval = random.randint(*self.IDLE_MOVE_CHANGE_INTERVAL)

            # 거리별 이동 목표 및 속도 설정
            if dist_to_player > self.far_threshold:
                target = self._keep_min_distance(player_pos, dist_to_player)
                self.goal_pos = target
                self.speed = self.BASE_SPEED
            elif dist_to_player < self.near_threshold:
                target = self._keep_min_distance(player_pos, dist_to_player)
                self.goal_pos = target
                self.speed = self.APPROACH_SPEED
            else:
                self.goal_pos = (
                    self.world_x + self.random_idle_dir.x * 80,
                    self.world_y + self.random_idle_dir.y * 80
                )
                self.speed = self.BASE_SPEED

            # 공격 개시 조건
            time_since_last_attack = now - self.last_attack_time
            if time_since_last_attack >= self.MIN_COOLDOWN:
                if dist_to_player <= self.near_threshold:
                    self.enter_prepare_attack(now)
                elif time_since_last_attack >= self.MAX_COOLDOWN:
                    self.enter_prepare_attack(now)
                elif random.random() < 0.0015:
                    self.enter_prepare_attack(now)

        elif self.state == self.STATE_PREPARE_ATTACK:
            # 공격 준비 상태: 최소 거리 유지하며 접근
            if dist_to_player > self.MIN_DISTANCE:
                move_dir = pygame.Vector2(dx, dy)
                if move_dir.length() > 0:
                    move_dir.normalize_ip()
                target = self._keep_min_distance(player_pos, dist_to_player)
                self.goal_pos = target
                self.speed = self.APPROACH_SPEED
            else:
                self.goal_pos = (self.world_x, self.world_y)
                self.speed = 0

            # 준비 시간 경과 시 공격
            if now - self.prepare_start_time >= self.PREPARE_TIME:
                self.state = self.STATE_ATTACK
                self.shoot()
                self.last_attack_time = now
                self.state = self.STATE_IDLE

    def _keep_min_distance(self, player_pos, dist_to_player):
        # 플레이어와의 최소 거리 유지
        if dist_to_player < self.MIN_DISTANCE:
            angle_away = math.atan2(self.world_y - player_pos[1], self.world_x - player_pos[0])
            return (
                player_pos[0] + math.cos(angle_away) * self.MIN_DISTANCE,
                player_pos[1] + math.sin(angle_away) * self.MIN_DISTANCE
            )
        return player_pos

    def enter_prepare_attack(self, now):
        # 공격 준비 상태 진입
        self.state = self.STATE_PREPARE_ATTACK
        self.prepare_start_time = now
        self.show_alert = True

    def shoot(self):
        # 샷건 펠릿 발사
        for _ in range(self.PELLET_COUNT):
            spread = math.radians(random.uniform(-self.PELLET_SPREAD_DEG, self.PELLET_SPREAD_DEG))
            angle = self.direction_angle + spread
            vx = math.cos(angle)
            vy = math.sin(angle)
            bullet = Bullet(
                self.world_x,
                self.world_y,
                self.world_x + vx * self.PELLET_RANGE,
                self.world_y + vy * self.PELLET_RANGE,
                spread_angle_degrees=0,
                bullet_image=self.bullet_image,
                speed=self.BULLET_SPEED,
                max_distance=self.PELLET_RANGE,
                damage=self.PELLET_DAMAGE
            )
            config.global_enemy_bullets.append(bullet)
        self.fire_sound.play()

    def die(self, blood_effects):
        # 사망 시 드랍 아이템 생성
        if self._already_dropped:
            return
        super().die(blood_effects)
        self.spawn_dropped_items(4, 5)

    def draw(self, screen, world_x, world_y, shake_offset_x=0, shake_offset_y=0):
        if not self.alive:
            return
        screen_x = self.world_x - world_x + shake_offset_x
        screen_y = self.world_y - world_y + shake_offset_y
        if self.state == self.STATE_PREPARE_ATTACK:
            self.draw_alert(screen, screen_x, screen_y)
        gun_pos_x = screen_x + math.cos(self.direction_angle) * self.current_distance
        gun_pos_y = screen_y + math.sin(self.direction_angle) * self.current_distance
        rotated_gun = pygame.transform.rotate(
            self.gun_image_original, -math.degrees(self.direction_angle) - 90
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

class Boss1(AIBase):
    rank=10

    FAR_DISTANCE = 800
    MID_DISTANCE = 500
    CLOSE_DISTANCE = 200
    GUN1_SAFE_MIN = MID_DISTANCE + 80
    GUN1_SAFE_MAX = MID_DISTANCE + 150

    def __init__(self, world_x, world_y, images, sounds, map_width, map_height,
                 damage_player_fn=None, kill_callback=None, is_position_blocked_fn=None):
        super().__init__(
            world_x, world_y, images, sounds, map_width, map_height,
            speed=0.0,
            near_threshold=0,
            far_threshold=0,
            radius=60,
            push_strength=0.0,
            alert_duration=0,
            damage_player_fn=damage_player_fn,
        )

        self.image_original = images["boss1"]
        self.gun1_image_original = images["boss1gun1"]
        self.gun2_image_original = images["boss1gun2"]
        self.bullet_image = images["enemy_bullet"]

        self.sound_gun1 = sounds["boss1_gun1_fire"]
        self.sound_gun2 = sounds["boss1_gun2_fire"]

        self.hp = 1000
        self.max_hp = 1000
        self.kill_callback = kill_callback

        self.half_phase_drop_done = False

        # 은신 관련
        self.is_hidden = False
        self.hide_start_time = 0
        self.hiding_transition = 0.0
        self.unhiding_transition = 0.0
        self.hide_speed = 1 / 0.5
        self.unhide_speed = 1 / 0.5
        self.base_speed = NORMAL_MAX_SPEED * PLAYER_VIEW_SCALE

        # 긴급 은신
        self.emergency_hide_active = False
        self.emergency_hide_timer = 0
        self.emergency_hide_duration = 2000

        self.last_hp_after_unhide = self.hp
        self.last_unhide_time = 0

        self.state = "far"
        self.current_weapon = None
        self.state_timer = 0
        self.mid_hold_timer = 0
        self.far_hold_timer = 0
        self.close_hold_timer = 0
        self.lock_weapon_until = 0
        self.target_pos = (self.world_x, self.world_y)
        self.target_timer = 0
        self.target_duration = 1000
        self.last_dist = None

        self.shoot_cooldown = 0
        self.shoot_interval_gun1 = 300
        self.shoot_interval_gun2 = 500

        self.is_position_blocked_fn = is_position_blocked_fn

    def update_goal(self, world_x, world_y, player_rect, enemies):
        # 매 프레임마다 이동/공격 상태를 결정
        # 은신 상태 유지/해제, 긴급 은신 발동 조건 체크
        # 플레이어와 거리 기반으로 상태(Far, Mid, Close, Retreat) 전환
        # 은신 중엔 마구잡이 이동 후 추격, 해제 시 공격 상태 복귀
        now = pygame.time.get_ticks()
        player_pos = (world_x + player_rect.centerx, world_y + player_rect.centery)
        dx, dy = player_pos[0] - self.world_x, player_pos[1] - self.world_y
        dist = math.hypot(dx, dy)
        self.direction_angle = math.atan2(dy, dx)
        self.state_timer += 16

        if self.emergency_hide_active and now - self.emergency_hide_timer >= self.emergency_hide_duration:
            self.emergency_hide_active = False

        if not self.is_hidden and now - self.last_unhide_time >= 5000:
            self._hide(emergency=True)

        # 목표 갱신
        self.target_timer += 16
        if self.target_timer >= self.target_duration:
            self.target_timer = 0
            self.target_duration = random.randint(500, 1500)
            self.target_pos = self._choose_target(player_pos)

        if self.last_dist is not None:
            if self.last_dist - dist > 200 and dist <= self.CLOSE_DISTANCE:
                if random.random() < 0.5:
                    self._hide(emergency=True)
        self.last_dist = dist

        if self.state in ("mid_gun1", "mid_gun2") and self.mid_hold_timer >= 3000:
            if random.random() < 0.4:
                self._hide(emergency=True)

        # 상태 로직
        if self.is_hidden:
            elapsed_hide = now - self.hide_start_time
            if elapsed_hide < 2000:  # 2초 동안 마구잡이 이동
                self.speed = self.base_speed * 3.0
                self.goal_pos = self._random_move_mid_or_more(player_pos)
            else:  # 이후 추격
                self.speed = self.base_speed * 1.5
                self.goal_pos = player_pos
            if elapsed_hide >= 2000 and dist <= self.CLOSE_DISTANCE:
                self._unhide("gun2")
        else:
            if dist >= self.FAR_DISTANCE:
                self._set_far_state()
            elif dist >= self.MID_DISTANCE:
                self._set_mid_state(dist, player_pos, now)
            else:
                self._set_close_state(player_pos, now)

        if self.state == "retreat":
            self.goal_pos = self._strafe_target(player_pos, retreat=True)
            if self.state_timer >= 1500:
                self.state = "far"

    def _random_move_mid_or_more(self, player_pos):
        # 은신 시 마구잡이 이동 목표 설정 (플레이어와 중거리 이상 유지)
        px, py = player_pos
        for _ in range(5):
            angle = random.uniform(0, math.pi * 2)
            dist = random.uniform(self.MID_DISTANCE, self.MID_DISTANCE + 200)
            tx = px + math.cos(angle) * dist
            ty = py + math.sin(angle) * dist
            if not self.is_position_blocked_fn or not self.is_position_blocked_fn(tx, ty):
                return (tx, ty)
        return (self.world_x, self.world_y)

    def _set_far_state(self):
        # 플레이어와 멀 때: 천천히 접근, 일정 시간 지나면 은신
        self.far_hold_timer += 16
        self.mid_hold_timer = 0
        self.close_hold_timer = 0
        if self.state != "far":
            self.state = "far"
            self.state_timer = 0
        if self.far_hold_timer >= 1000:
            self._hide()
        else:
            self.speed = self.base_speed
            self.goal_pos = self.target_pos

    def _set_mid_state(self, dist, player_pos, now):
        # 플레이어와 중간 거리일 때: Gun1 또는 Gun2 사용해 교전
        # 거리 조건에 따라 무기 선택 및 사격
        self.far_hold_timer = 0
        self.close_hold_timer = 0
        self.mid_hold_timer += 16
        if dist >= self.GUN1_SAFE_MIN:
            if dist < self.GUN1_SAFE_MIN:
                self.goal_pos = self._strafe_target(player_pos, retreat=True)
            else:
                self.state = "mid_gun1"
                self.current_weapon = "gun1"
                self._shoot_if_ready("gun1", player_pos, now)
                self.goal_pos = self.target_pos
        else:
            self.state = "mid_gun2"
            self.current_weapon = "gun2"
            self._shoot_if_ready("gun2", player_pos, now)
            self.goal_pos = player_pos

    def _set_close_state(self, player_pos, now):
        # 플레이어와 가까울 때: Gun2로 공격 후 일정 시간 지나면 후퇴 상태로 전환
        self.far_hold_timer = 0
        self.mid_hold_timer = 0
        self.close_hold_timer += 16
        self.state = "close"
        self.current_weapon = "gun2"
        self._shoot_if_ready("gun2", player_pos, now)
        self.goal_pos = self._strafe_target(player_pos, retreat=True)
        if self.close_hold_timer >= random.randint(1500, 2000):
            self.state = "retreat"
            self.state_timer = 0

    def _choose_target(self, player_pos):
        # 현재 상태에 맞는 목표 좌표 계산 (회피/접근)
        if self.state in ("mid_gun1", "mid_gun2", "close"):
            return self._strafe_target(player_pos)
        else:
            return self._approach_target(player_pos)

    def _approach_target(self, target_pos, sideways=True):
        # 목표에 접근하는 좌표 계산 (좌우무빙 포함 가능)
        tx, ty = target_pos
        if sideways:
            base_angle = math.atan2(ty - self.world_y, tx - self.world_x)
            side_angle = base_angle + math.pi / 2
            offset = random.choice([-1, 1]) * random.uniform(30, 60)
            tx += math.cos(side_angle) * offset
            ty += math.sin(side_angle) * offset
        return (tx, ty)

    def _strafe_target(self, target_pos, retreat=False):
        # 좌우로 무빙하며 목표 좌표 계산, 후퇴 시 뒤로 이동
        tx, ty = target_pos
        base_angle = math.atan2(ty - self.world_y, tx - self.world_x)
        if retreat:
            base_angle += math.pi
        forward = random.uniform(50, 100)
        tx = self.world_x + math.cos(base_angle) * forward
        ty = self.world_y + math.sin(base_angle) * forward
        side_angle = base_angle + math.pi / 2
        side_offset = random.choice([-1, 1]) * random.uniform(50, 100)
        tx += math.cos(side_angle) * side_offset
        ty += math.sin(side_angle) * side_offset
        return (tx, ty)

    def _hide(self, emergency=False):
        # 은신 시작, 무기 숨기기, 긴급 은신 플래그 설정 가능
        now = pygame.time.get_ticks()
        self.is_hidden = True
        self.hide_start_time = now
        self.hiding_transition = 0.0
        self.current_weapon = None
        if emergency:
            self.emergency_hide_active = True
            self.emergency_hide_timer = now

    def _unhide(self, weapon):
        # 은신 해제, 무기 장착
        self.is_hidden = False
        self.unhiding_transition = 0.0
        self.current_weapon = weapon
        self.last_hp_after_unhide = self.hp
        self.last_unhide_time = pygame.time.get_ticks()

    def _shoot_if_ready(self, weapon_type, player_pos, now):
        # 무기 쿨타임 확인 후 사격
        if self.state == "far" or self.is_hidden:
            return
        interval = self.shoot_interval_gun1 if weapon_type == "gun1" else self.shoot_interval_gun2
        if now >= self.shoot_cooldown:
            self.shoot(weapon_type, player_pos)
            self.shoot_cooldown = now + interval

    def shoot(self, weapon_type, player_pos):
        # Gun1 또는 Gun2 발사, 탄환 생성, 사운드 재생
        if weapon_type == "gun1":
            self.sound_gun1.play()
            bullet_speed, damage = 12 * PLAYER_VIEW_SCALE, 15
        else:
            self.sound_gun2.play()
            bullet_speed, damage = 16 * PLAYER_VIEW_SCALE, 25
        spawn_offset = 30
        vertical_offset = 6
        offset_angle = self.direction_angle + math.radians(90)
        ox = math.cos(offset_angle) * vertical_offset
        oy = math.sin(offset_angle) * vertical_offset
        bx = self.world_x + math.cos(self.direction_angle) * spawn_offset + ox
        by = self.world_y + math.sin(self.direction_angle) * spawn_offset + oy
        config.global_enemy_bullets.append(
            Bullet(bx, by, player_pos[0], player_pos[1], 0, self.bullet_image,
                   speed=bullet_speed, max_distance=2000 * PLAYER_VIEW_SCALE, damage=damage)
        )

    def hit(self, damage, blood_effects, force=False):
        # 피격 처리, HP 절반 이하 진입 시 오브 드랍
        # 일정 HP 감소 시 긴급 은신 발동
        if not self.half_phase_drop_done and self.hp - damage <= self.max_hp * 0.5:
            self.spawn_dropped_items(5, 7)
            self.half_phase_drop_done = True
        if not self.is_hidden and not self.emergency_hide_active:
            if self.last_hp_after_unhide - self.hp >= 200:
                self._hide(emergency=True)
        if self.is_hidden and not self.emergency_hide_active:
            self._unhide("gun2")
        super().hit(damage, blood_effects, force)

    def die(self, blood_effects):
        # 사망 시 오브 드랍
        if self._already_dropped:
            return
        super().die(blood_effects)
        self.spawn_dropped_items(10, 15)

    def draw(self, screen, world_x, world_y, sx=0, sy=0):
        # 은신 시 투명도 처리
        if not self.alive:
            return

        screen_x = self.world_x - world_x + sx
        screen_y = self.world_y - world_y + sy

        if not self.is_hidden and self.current_weapon:
            gun_img = self.gun1_image_original if self.current_weapon == "gun1" else self.gun2_image_original
            rotated_gun = pygame.transform.rotate(gun_img, -math.degrees(self.direction_angle) + 90)
            gx = screen_x + math.cos(self.direction_angle) * 45
            gy = screen_y + math.sin(self.direction_angle) * 45
            screen.blit(rotated_gun, rotated_gun.get_rect(center=(gx, gy)))

        alpha = 255
        if self.is_hidden:
            self.hiding_transition = min(1.0, self.hiding_transition + self.hide_speed / 60)
            alpha = int(255 * (1 - self.hiding_transition) * 0.25)
        elif self.unhiding_transition < 1.0:
            self.unhiding_transition = min(1.0, self.unhiding_transition + self.unhide_speed / 60)
            alpha = int(255 * self.unhiding_transition)

        rotated_img = pygame.transform.rotate(self.image_original, -math.degrees(self.direction_angle) + 90)
        rotated_img.set_alpha(alpha)
        screen.blit(rotated_img, rotated_img.get_rect(center=(screen_x, screen_y)))

class Boss2(AIBase):
    rank=10

    HP_MAX = 2000
    SPEED = NORMAL_MAX_SPEED * PLAYER_VIEW_SCALE * 0.9
    ORB_DROP_MULTIPLIER = 1.33
    ORB_DROP_ON_HALF_HP_RATIO = 0.5
    GUN1_DAMAGE = 120
    GUN1_RADIUS = 110
    GUN1_COOLDOWN = 2000
    GUN2_DAMAGE = 10
    GUN2_COOLDOWN = 1500
    DRONE_SPEED = 4 * PLAYER_VIEW_SCALE
    DRONE_DAMAGE = 150
    DRONE_RADIUS = int(70 * 1.2)
    DRONE_KNOCKBACK = 150
    DRONE_WARNING_TIME = 500
    DRONE_RESPAWN_TIME = 5000
    DRONE_RESPAWN_TIME_LOW_HP = 3000
    INITIAL_DRONES = 2

    def __init__(self, world_x, world_y, images, sounds, map_width, map_height,
                 damage_player_fn=None, kill_callback=None):
        super().__init__(world_x, world_y, images, sounds, map_width, map_height,
                         speed=self.SPEED, near_threshold=300, far_threshold=700,
                         radius=50, push_strength=0.0, alert_duration=0,
                         damage_player_fn=damage_player_fn)

        self.hp = self.HP_MAX
        self.max_hp = self.HP_MAX
        self.kill_callback = kill_callback
        self.half_hp_triggered = False
        self.current_gun = 1

        self.image_original = images["boss2"]
        self.gun1_image_original = images["gun8"]
        self.gun2_image_original = images["gun3"]
        self.bullet_image = images["bullet1"]
        self.warhead_image = images["warhead1"]
        self.explosion_image = images["explosion1"]
        self.cartridge_image = images["cartridge_case1"]

        self.sound_gun1_fire = sounds["boss2_gun1_fire"]
        self.sound_gun1_explosion = sounds["boss2_gun1_explosion"]
        self.sound_gun2_fire = sounds["boss2_gun2_fire"]

        self.drone_img = images["drone"]
        self.sound_drone_spawn = sounds["drone_spawn"]
        self.sound_drone_warning = sounds["drone_warning"]
        self.sound_drone_explosion = sounds["drone_explosion"]
        self.drones = []
        self.last_drone_spawn_time = 0

        self.direction_angle = 0
        self.current_distance = 45 * PLAYER_VIEW_SCALE

        self.last_gun1_time = 0
        self.last_gun2_time = 0

        for _ in range(self.INITIAL_DRONES):
            self.spawn_drone()

    class DroneChaser:
        # 소환하는 추격 드론 클래스
        def __init__(self, boss, spawn_x, spawn_y):
            self.boss = boss
            self.x = spawn_x
            self.y = spawn_y
            self.state = "chasing"
            self.warning_start = None
            self.angle = 0

        def update(self, player_x, player_y):
            # 플레이어 추격 및 폭발 준비 상태로 전환
            if self.state == "dead":
                return
            dx, dy = player_x - self.x, player_y - self.y
            dist = math.hypot(dx, dy)
            self.angle = math.atan2(dy, dx)

            if self.state == "chasing":
                if dist > 0:
                    self.x += (dx / dist) * Boss2.DRONE_SPEED
                    self.y += (dy / dist) * Boss2.DRONE_SPEED
                if dist < 60:
                    self.state = "warning"
                    self.warning_start = pygame.time.get_ticks()
                    self.boss.sound_drone_warning.play()
            elif self.state == "warning":
                if pygame.time.get_ticks() - self.warning_start >= Boss2.DRONE_WARNING_TIME:
                    self.explode()

        def explode(self, no_damage=False):
            # 드론 폭발 처리, 범위 내 플레이어에게 피해
            self.boss.sound_drone_warning.stop()
            config.effects.append(ExplosionEffectPersistent(self.x, self.y, self.boss.explosion_image))
            self.boss.sound_drone_explosion.play()
            if not no_damage and self.boss.damage_player:
                px, py = config.world_x + config.player_rect.centerx, config.world_y + config.player_rect.centery
                if math.hypot(px - self.x, py - self.y) <= Boss2.DRONE_RADIUS:
                    self.boss.damage_player(Boss2.DRONE_DAMAGE)
            self.state = "dead"

        def draw(self, screen, world_x, world_y):
            # 드론 그리기, 폭발 경고 상태일 경우 빨간색 필터
            if self.state == "dead":
                return
            img = self.boss.drone_img.copy()
            if self.state == "warning":
                img.fill((255, 0, 0), special_flags=pygame.BLEND_RGB_ADD)
            rotated = pygame.transform.rotate(img, -math.degrees(self.angle) - 90)
            rect = rotated.get_rect(center=(self.x - world_x, self.y - world_y))
            screen.blit(rotated, rect)

    def spawn_drone(self):
        # 드론 소환
        sx = self.world_x + random.randint(-100, 100)
        sy = self.world_y + random.randint(-100, 100)
        self.drones.append(self.DroneChaser(self, sx, sy))
        self.sound_drone_spawn.play()

    def update_goal(self, world_x, world_y, player_rect, enemies):
        # 보스 AI 메인 루프: 드론 갱신/소환, 체력 상태별 아이템 드랍, 무기 선택
        px = world_x + player_rect.centerx
        py = world_y + player_rect.centery
        dx, dy = px - self.world_x, py - self.world_y
        dist = math.hypot(dx, dy)
        self.direction_angle = math.atan2(dy, dx)

        for drone in self.drones:
            drone.update(px, py)
        self.drones = [d for d in self.drones if d.state != "dead"]

        respawn_time = self.DRONE_RESPAWN_TIME_LOW_HP if self.hp <= self.HP_MAX // 2 else self.DRONE_RESPAWN_TIME
        if len(self.drones) < self.INITIAL_DRONES and pygame.time.get_ticks() - self.last_drone_spawn_time >= respawn_time:
            self.spawn_drone()
            self.last_drone_spawn_time = pygame.time.get_ticks()

        if not self.half_hp_triggered and self.hp <= self.HP_MAX // 2:
            self.spawn_dropped_items(int(5 * self.ORB_DROP_MULTIPLIER), int(7 * self.ORB_DROP_MULTIPLIER))
            self.half_hp_triggered = True

        now = pygame.time.get_ticks()
        if dist > 700:
            if now - self.last_gun1_time >= self.GUN1_COOLDOWN:
                self.attack_gun1()
        elif dist > 300:
            if now - self.last_gun2_time >= self.GUN2_COOLDOWN:
                self.attack_gun2(px, py)
        else:
            self.evade(px, py)

    def attack_gun1(self):
        self.current_gun = 1
        self.last_gun1_time = pygame.time.get_ticks()
        self.sound_gun1_fire.play()

        red_warhead = self.warhead_image.copy()
        red_warhead.fill((255, 0, 0, 255), special_flags=pygame.BLEND_RGBA_MULT)

        missile = HomingMissile(
            x=self.world_x,
            y=self.world_y,
            target=None,
            image=red_warhead,
            explosion_radius=self.GUN1_RADIUS,
            damage=self.GUN1_DAMAGE,
            explosion_image=self.explosion_image,
            explosion_sound=self.sound_gun1_explosion,
            live_tracking=True,
            turn_rate=0.03,
            max_distance=600
        )
        missile.owner = self
        config.global_enemy_bullets.append(missile)

    def attack_gun2(self, px, py):
        self.current_gun = 2
        self.last_gun2_time = pygame.time.get_ticks()
        self.sound_gun2_fire.play()

        red_bullet_img = self.bullet_image.copy()
        red_bullet_img.fill((255, 0, 0, 255), special_flags=pygame.BLEND_RGBA_MULT)

        angle = math.atan2(py - self.world_y, px - self.world_x)
        for _ in range(15):
            spread = math.radians(random.uniform(-30, 30))
            dx = math.cos(angle + spread)
            dy = math.sin(angle + spread)
            bullet = Bullet(
                self.world_x, self.world_y,
                self.world_x + dx * 100, self.world_y + dy * 100,
                spread_angle_degrees=0,
                bullet_image=red_bullet_img,
                speed=11.25 * PLAYER_VIEW_SCALE,
                max_distance=600 * PLAYER_VIEW_SCALE,
                damage=self.GUN2_DAMAGE
            )
            bullet.trail_enabled = False
            bullet.owner = self
            config.global_enemy_bullets.append(bullet)

        eject_angle = self.direction_angle + math.radians(90 + random.uniform(-15, 15))
        vx, vy = math.cos(eject_angle), math.sin(eject_angle)
        big_case = pygame.transform.smoothscale(
            self.cartridge_image,
            (int(self.cartridge_image.get_width() * 1.5),
             int(self.cartridge_image.get_height() * 1.5))
        )
        self.scattered_bullets.append(
            ScatteredBullet(self.world_x, self.world_y, vx, vy, big_case)
        )

    def evade(self, px, py):
        # 플레이어와 근접 시 후퇴 동작
        dx, dy = self.world_x - px, self.world_y - py
        dist = math.hypot(dx, dy)
        if dist < 80:
            self.world_x += math.cos(self.direction_angle + math.pi) * self.SPEED
            self.world_y += math.sin(self.direction_angle + math.pi) * self.SPEED
        elif dist > 0:
            self.world_x += (dx / dist) * self.SPEED
            self.world_y += (dy / dist) * self.SPEED

    def die(self, blood_effects):
        # 보스 사망 시 드론 폭발, 아이템 드랍
        if self._already_dropped:
            return
        super().die(blood_effects)
        for drone in self.drones:
            drone.explode(no_damage=True)
        self.drones.clear()
        self.spawn_dropped_items(int(10 * self.ORB_DROP_MULTIPLIER), int(15 * self.ORB_DROP_MULTIPLIER))

    def draw(self, screen, world_x, world_y, sx=0, sy=0):
        # 무기/본체/드론 그리기
        if not self.alive:
            return
        scr_x = self.world_x - world_x + sx
        scr_y = self.world_y - world_y + sy
        if self.current_gun == 1:
            gun_img = self.gun1_image_original
        else:
            gun_img = self.gun2_image_original
        gun_rot = pygame.transform.rotate(gun_img, -math.degrees(self.direction_angle) - 90)
        gun_rect = gun_rot.get_rect(center=(scr_x + math.cos(self.direction_angle) * self.current_distance,
                                            scr_y + math.sin(self.direction_angle) * self.current_distance))
        screen.blit(gun_rot, gun_rect)
        scaled_img = pygame.transform.smoothscale(self.image_original,
                                                  (int(self.image_original.get_width() * PLAYER_VIEW_SCALE),
                                                   int(self.image_original.get_height() * PLAYER_VIEW_SCALE)))
        boss_rot = pygame.transform.rotate(scaled_img, -math.degrees(self.direction_angle) + 90)
        rect = boss_rot.get_rect(center=(scr_x, scr_y))
        screen.blit(boss_rot, rect)
        for drone in self.drones:
            drone.draw(screen, world_x, world_y)
