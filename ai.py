import pygame
import math
import random
from config import *
import config
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

        import config
        config.player_score += getattr(self, "rank", 1)

        config.score_gain_texts.append({
            "text": f"+{getattr(self, 'rank', 1)}",
            "x": 100,
            "y":  SCREEN_HEIGHT - 118,
            "alpha": 255,
            "lifetime": 60,
            "delay": 60 
        })

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
    def __init__(self, world_x, world_y, images, sounds, map_width, map_height, damage_player_fn=None, kill_callback=None, rank=rank):
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
            rank=rank,
        )
        self.hp = 120
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
    def __init__(self, world_x, world_y, images, sounds, map_width, map_height, damage_player_fn=None, kill_callback=None, rank=rank):
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
            rank=rank,
        )
        self.image_original = images["enemy2"]
        self.gun_image_original = pygame.transform.flip(images["gun2"], True, False)
        self.bullet_image = images["enemy_bullet"]
        self.cartridge_image = images["cartridge_case1"]
        self.player_bullet_image = images["bullet1"]
        self.kill_callback = kill_callback
        self.hp = 170
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
    rank=4

    FAR_DISTANCE = 500
    NEAR_DISTANCE = 100
    RADIUS_CLOSE_ATTACK = 120

    DASH_DISTANCE = 250
    DASH_SPEED_MULTIPLIER = 3
    DASH_DAMAGE = 30
    CHARGE_TIME = 1000
    COOLDOWN_MIN = 1000
    COOLDOWN_MAX = 2000

    CLOSE_ATTACK_CHARGE = 1000
    CLOSE_ATTACK_COOLDOWN_MIN = 2000
    CLOSE_ATTACK_COOLDOWN_MAX = 3000
    CLOSE_ATTACK_DAMAGE = 20
    CLOSE_ATTACK_SWEEP_TIME = 200
    CLOSE_ATTACK_SPEED_PENALTY = 0.7

    def __init__(self, world_x, world_y, images, sounds, map_width, map_height,
                 damage_player_fn=None, kill_callback=None, rank=rank):
        self.base_speed = NORMAL_MAX_SPEED * PLAYER_VIEW_SCALE * 0.8
        super().__init__(
            world_x, world_y, images, sounds, map_width, map_height,
            speed=self.base_speed,
            near_threshold=self.NEAR_DISTANCE,
            far_threshold=self.FAR_DISTANCE,
            radius=39,
            push_strength=0.18,
            alert_duration=1000,
            damage_player_fn=damage_player_fn,
            rank=rank,
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
                 damage_player_fn=None, kill_callback=None, rank=rank):
        # 기본 속성 초기화 (이동 속도, 사거리, 경고 지속시간)
        super().__init__(
            world_x, world_y, images, sounds, map_width, map_height,
            speed=self.BASE_SPEED,
            near_threshold=0,
            far_threshold=self.FAR_THRESHOLD,
            radius=30 * 1.2,
            push_strength=0.18,
            alert_duration=self.MIN_ATTACK_PREPARE_TIME,
            damage_player_fn=damage_player_fn,
            rank=rank,
        )

        self.image_original = images["enemy4"]
        self.image = self.image_original
        self.kill_callback = kill_callback
        self.hp = 300

        shield_radius = int(self.radius * 1.2)
        self.shield = ShieldEffect(self, shield_radius, max_hp=200)
        self.shield_break_sound = sounds["enemy4_shield_break"]
        self.shield_charged_sound = sounds["enemy4_shield_charged"]

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
        angle = self.direction_angle + math.radians(random.uniform(-15, 15))
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
            speed=3 * PLAYER_VIEW_SCALE,
            max_distance=2000 * PLAYER_VIEW_SCALE,
            damage=15
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
    rank=3

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
                 damage_player_fn=None, kill_callback=None, rank=rank):
        # 기본 속성 초기화 (속도, 사거리, 경고 시간, 충돌 반경 등)
        super().__init__(
            world_x, world_y, images, sounds, map_width, map_height,
            speed=self.BASE_SPEED,
            near_threshold=150,
            far_threshold=500,
            radius=30,
            push_strength=0.18,
            alert_duration=self.PREPARE_TIME,
            damage_player_fn=damage_player_fn,
            rank=rank,
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

class Enemy6(AIBase):
    rank = 7
    HP_MAX = 700
    SPEED = NORMAL_MAX_SPEED * PLAYER_VIEW_SCALE * 0.85

    FIREBALL_DAMAGE = 45
    FIREBALL_BURN_DMG = 12
    FIREBALL_BURN_DURATION = 2000
    FIREBALL_COOLDOWN = 1500

    PILLAR_DAMAGE_TICK = 25
    PILLAR_RADIUS = 150
    PILLAR_DELAY = 700
    PILLAR_DURATION = 3000
    PILLAR_COOLDOWN = 3500

    TELEPORT_MIN_COOLDOWN = 6000
    TELEPORT_MAX_COOLDOWN = 8000
    TELEPORT_DISTANCE = 550
    TELEPORT_SAFE_DIST = 700
    TELEPORT_INVULN_TIME = 300

    ENRAGE_THRESHOLD = 0.5
    ENRAGE_SPEED_MULT = 1.2
    ENRAGE_PILLAR_EXTRA = 1000
    ENRAGE_TELEPORT_REDUCE = 1000

    def __init__(self, world_x, world_y, images, sounds, map_width, map_height,
                 damage_player_fn=None, kill_callback=None, rank=rank):
        super().__init__(
            world_x, world_y, images, sounds, map_width, map_height,
            speed=self.SPEED,
            near_threshold=200,
            far_threshold=900,
            radius=55,
            push_strength=0.18,
            alert_duration=800,
            damage_player_fn=damage_player_fn,
            rank=rank,
        )
        self.image_original = images["enemy6"]
        self.kill_callback = kill_callback
        self.hp = self.HP_MAX
        self.enraged = False

        now = pygame.time.get_ticks()
        self.next_fireball_time = now + 2000
        self.next_pillar_time = now + 3000
        self.next_teleport_time = now + random.randint(self.TELEPORT_MIN_COOLDOWN, self.TELEPORT_MAX_COOLDOWN)

    def update_goal(self, world_x, world_y, player_rect, enemies):
        # 플레이어 위치와 거리 기반으로 공격, 순간이동, 이동 로직 수행
        px = world_x + player_rect.centerx
        py = world_y + player_rect.centery
        dx = px - self.world_x
        dy = py - self.world_y
        dist_to_player = math.hypot(dx, dy)
        self.direction_angle = math.atan2(dy, dx)
        now = pygame.time.get_ticks()

        if not self.enraged and self.hp <= self.HP_MAX * self.ENRAGE_THRESHOLD:
            self.enraged = True
            self.FIREBALL_COOLDOWN = int(self.FIREBALL_COOLDOWN / self.ENRAGE_SPEED_MULT)
            self.PILLAR_COOLDOWN = int(self.PILLAR_COOLDOWN / self.ENRAGE_SPEED_MULT)
            self.PILLAR_DURATION += self.ENRAGE_PILLAR_EXTRA
            self.TELEPORT_MIN_COOLDOWN -= self.ENRAGE_TELEPORT_REDUCE
            self.TELEPORT_MAX_COOLDOWN -= self.ENRAGE_TELEPORT_REDUCE

        if now >= self.next_teleport_time and dist_to_player <= self.TELEPORT_SAFE_DIST:
            self.teleport_away_from_player((px, py))
            self.next_teleport_time = now + random.randint(self.TELEPORT_MIN_COOLDOWN, self.TELEPORT_MAX_COOLDOWN)
            self.cast_fireball((px, py))

        if now >= self.next_pillar_time:
            self.cast_flame_pillar((px, py))
            self.next_pillar_time = now + self.PILLAR_COOLDOWN

        if now >= self.next_fireball_time:
            self.cast_fireball((px, py))
            self.next_fireball_time = now + self.FIREBALL_COOLDOWN

        if dist_to_player < 600:
            self.goal_pos = (
                self.world_x - math.cos(self.direction_angle) * 200,
                self.world_y - math.sin(self.direction_angle) * 200
            )
        else:
            self.goal_pos = (
                self.world_x + math.cos(self.direction_angle + math.pi / 2) * 150,
                self.world_y + math.sin(self.direction_angle + math.pi / 2) * 150
            )

    def cast_fireball(self, player_pos):
        # 플레이어를 향해 3갈래 화염구 발사
        px, py = player_pos
        base_angle = math.atan2(py - self.world_y, px - self.world_x)
        for offset in (-math.radians(20), 0, math.radians(20)):
            angle = base_angle + offset
            vx = math.cos(angle)
            vy = math.sin(angle)
            from entities import Fireball
            fb = Fireball(
                x=self.world_x,
                y=self.world_y,
                vx=vx * 8,
                vy=vy * 8,
                damage=self.FIREBALL_DAMAGE,
                burn_damage=self.FIREBALL_BURN_DMG,
                burn_duration=self.FIREBALL_BURN_DURATION,
                image=self.images["fireball"]
            )
            fb.owner = self
            config.global_enemy_bullets.append(fb)
        self.sounds["fireball"].play()

    def cast_flame_pillar(self, player_pos):
        # 지연 후 플레이어 위치에 불기둥 생성
        px, py = player_pos
        from entities import FlamePillar
        pillar = FlamePillar(
            center_x=px,
            center_y=py,
            radius=self.PILLAR_RADIUS,
            delay=self.PILLAR_DELAY,
            duration=self.PILLAR_DURATION,
            damage_tick=self.PILLAR_DAMAGE_TICK,
            image=self.images["flame_pillar"],
            warning_color=(255, 0, 0, 128)
        )
        config.effects.append(pillar)
        self.sounds["flame_pillar"].play()

    def teleport_away_from_player(self, player_pos):
        # 플레이어 반대 방향으로 순간이동 (맵 경계/장애물 체크 포함)
        px, py = player_pos
        angle = math.atan2(self.world_y - py, self.world_x - px)
        tx = self.world_x + math.cos(angle) * self.TELEPORT_DISTANCE
        ty = self.world_y + math.sin(angle) * self.TELEPORT_DISTANCE

        margin = 50
        tx = max(margin, min(tx, self.map_width - margin))
        ty = max(margin, min(ty, self.map_height - margin))

        if config.obstacle_manager.check_collision_circle((tx, ty), self.radius):
            return

        self.world_x, self.world_y = tx, ty
        self.invulnerable_until = pygame.time.get_ticks() + self.TELEPORT_INVULN_TIME

        from entities import TeleportFlash
        flash = TeleportFlash(self.world_x, self.world_y, color=(255, 50, 50))
        config.effects.append(flash)

    def die(self, blood_effects):
        if self._already_dropped:
            return
        super().die(blood_effects)
        self.spawn_dropped_items(12, 14)

    def draw(self, screen, world_x, world_y, shake_offset_x=0, shake_offset_y=0):
        if not self.alive:
            return
        screen_x = self.world_x - world_x + shake_offset_x
        screen_y = self.world_y - world_y + shake_offset_y

        self.draw_alert(screen, screen_x, screen_y)

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

class Enemy7(AIBase):
    rank = 1
    HP_MAX = 150
    SPEED = NORMAL_MAX_SPEED * PLAYER_VIEW_SCALE * 1.05

    FIREBALL_DAMAGE = 10
    FIREBALL_BURN_DMG = 5
    FIREBALL_BURN_DURATION = 1000
    FIREBALL_COOLDOWN = 2200

    MIN_SAFE_DIST = 400
    CAST_TIME = 1000

    def __init__(self, world_x, world_y, images, sounds, map_width, map_height,
                 damage_player_fn=None, kill_callback=None, rank=rank):
        super().__init__(
            world_x, world_y, images, sounds, map_width, map_height,
            speed=self.SPEED,
            near_threshold=0,
            far_threshold=9999,
            radius=40,
            push_strength=0.18,
            alert_duration=500,
            damage_player_fn=damage_player_fn,
            rank=rank,
        )
        self.image_original = images["enemy7"]
        self.kill_callback = kill_callback
        self.hp = self.HP_MAX

        now = pygame.time.get_ticks()
        self.next_fireball_time = now + 1000
        self.casting = False
        self.cast_start_time = 0
        self.show_alert = False

    def update_goal(self, world_x, world_y, player_rect, enemies):
        # 플레이어와 일정 거리 유지, 랜덤 무빙 + 화염구 시전
        px = world_x + player_rect.centerx
        py = world_y + player_rect.centery
        dx = px - self.world_x
        dy = py - self.world_y
        dist_to_player = math.hypot(dx, dy)
        self.direction_angle = math.atan2(dy, dx)
        now = pygame.time.get_ticks()

        if self.casting:
            if now - self.cast_start_time >= self.CAST_TIME:
                self.cast_fireball((px, py))
                self.casting = False
                self.show_alert = False
                self.next_fireball_time = now + self.FIREBALL_COOLDOWN
            return

        if now >= self.next_fireball_time:
            self.casting = True
            self.cast_start_time = now
            self.show_alert = True
            return

        if dist_to_player < self.MIN_SAFE_DIST:
            angle = math.atan2(self.world_y - py, self.world_x - px) + random.uniform(-0.5, 0.5)
            move_dist = random.randint(100, 200)
        else:
            angle = random.uniform(0, math.pi * 2)
            move_dist = random.randint(150, 300)

        target_x = px + math.cos(angle) * move_dist
        target_y = py + math.sin(angle) * move_dist
        target_x = max(0, min(target_x, self.map_width))
        target_y = max(0, min(target_y, self.map_height))

        self.goal_pos = (target_x, target_y)

    def cast_fireball(self, player_pos):
        # 단일 화염구 발사
        px, py = player_pos
        angle = math.atan2(py - self.world_y, px - self.world_x)
        vx = math.cos(angle)
        vy = math.sin(angle)
        from entities import Fireball
        fb = Fireball(
            x=self.world_x,
            y=self.world_y,
            vx=vx * 6,
            vy=vy * 6,
            damage=self.FIREBALL_DAMAGE,
            burn_damage=self.FIREBALL_BURN_DMG,
            burn_duration=self.FIREBALL_BURN_DURATION,
            image=self.images["fireball"]
        )
        fb.owner = self
        config.global_enemy_bullets.append(fb)
        self.sounds["fireball"].play()

    def die(self, blood_effects):
        if self._already_dropped:
            return
        super().die(blood_effects)
        self.spawn_dropped_items(4, 4)

    def draw(self, screen, world_x, world_y, shake_offset_x=0, shake_offset_y=0):
        if not self.alive:
            return
        screen_x = self.world_x - world_x + shake_offset_x
        screen_y = self.world_y - world_y + shake_offset_y

        if self.show_alert:
            self.draw_alert(screen, screen_x, screen_y)

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

class Enemy8(AIBase):
    rank = 2

    HP = 220
    BASE_SPEED = NORMAL_MAX_SPEED * PLAYER_VIEW_SCALE * 0.9
    RETREAT_SPEED = BASE_SPEED * 1.2

    GRENADE_SPEED = 4
    GRENADE_EXPLOSION_RADIUS = 150
    GRENADE_DAMAGE = 30
    GRENADE_KNOCKBACK = 120
    GRENADE_EXPLOSION_DELAY = 1500  # ms
    THROW_COOLDOWN = 2500
    PREPARE_TIME = 500
    NEAR_DISTANCE = 300 * PLAYER_VIEW_SCALE
    FAR_DISTANCE = 600 * PLAYER_VIEW_SCALE

    def __init__(self, world_x, world_y, images, sounds, map_width, map_height,
                 damage_player_fn=None, kill_callback=None, rank=rank):
        super().__init__(
            world_x, world_y, images, sounds, map_width, map_height,
            speed=self.BASE_SPEED,
            near_threshold=self.NEAR_DISTANCE,
            far_threshold=self.FAR_DISTANCE,
            radius=30 * PLAYER_VIEW_SCALE,
            push_strength=0.18,
            alert_duration=self.PREPARE_TIME,
            damage_player_fn=damage_player_fn,
            rank=rank,
        )
        self.image_original = images["enemy8"]
        self.kill_callback = kill_callback
        self.hp = self.HP

        self.last_throw_time = -self.THROW_COOLDOWN
        self.prepare_start_time = None
        self.is_preparing_throw = False
        self.show_alert = False

    def update_goal(self, world_x, world_y, player_rect, enemies):
        px = world_x + player_rect.centerx
        py = world_y + player_rect.centery
        dx = px - self.world_x
        dy = py - self.world_y
        dist_to_player = math.hypot(dx, dy)
        self.direction_angle = math.atan2(dy, dx)
        now = pygame.time.get_ticks()

        if self.is_preparing_throw:
            if now - self.prepare_start_time >= self.PREPARE_TIME:
                self.is_preparing_throw = False
                self.show_alert = False
                self.shoot(px, py)
                self.last_throw_time = now
            self.goal_pos = (self.world_x, self.world_y)
            return

        if now - self.last_throw_time >= self.THROW_COOLDOWN:
            self.is_preparing_throw = True
            self.prepare_start_time = now
            self.show_alert = True
            self.goal_pos = (self.world_x, self.world_y)
            return

        if dist_to_player < self.NEAR_DISTANCE:
            angle = self.direction_angle + math.pi
            self.goal_pos = (
                self.world_x + math.cos(angle) * 150,
                self.world_y + math.sin(angle) * 150
            )
            self.speed = self.RETREAT_SPEED
        elif dist_to_player > self.FAR_DISTANCE:
            self.goal_pos = (px, py)
            self.speed = self.BASE_SPEED
        else:
            if self.goal_pos is None or self.move_timer <= 0:
                angle = random.uniform(0, 2 * math.pi)
                dist = random.randint(50, 150)
                self.goal_pos = (
                    self.world_x + math.cos(angle) * dist,
                    self.world_y + math.sin(angle) * dist
                )
                self.move_timer = random.randint(500, 1000)
            self.speed = self.BASE_SPEED

        if not self.aware_of_player and dist_to_player < self.FAR_DISTANCE:
            self.aware_of_player = True

    def shoot(self, target_x, target_y):
        from entities import GrenadeProjectile
        angle = math.atan2(target_y - self.world_y, target_x - self.world_x)
        vx = math.cos(angle)
        vy = math.sin(angle)

        grenade = GrenadeProjectile(
            x=self.world_x,
            y=self.world_y,
            vx=vx,
            vy=vy,
            speed=self.GRENADE_SPEED,
            image=self.images["hand_grenade"],
            explosion_radius=self.GRENADE_EXPLOSION_RADIUS,
            max_damage=self.GRENADE_DAMAGE,
            min_damage=self.GRENADE_DAMAGE,
            explosion_image=self.images["explosion1"],
            explosion_sound=self.sounds["gun20_explosion"],
            explosion_delay=self.GRENADE_EXPLOSION_DELAY,
            owner=self
        )
        config.global_enemy_bullets.append(grenade)

    def die(self, blood_effects):
        if self._already_dropped:
            return
        super().die(blood_effects)
        self.spawn_dropped_items(4, 5)

    def draw(self, screen, world_x, world_y, shake_offset_x=0, shake_offset_y=0):
        if not self.alive:
            return
        screen_x = self.world_x - world_x + shake_offset_x
        screen_y = self.world_y - world_y + shake_offset_y

        if self.show_alert:
            self.draw_alert(screen, screen_x, screen_y)

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

class Enemy9(AIBase):
    rank = 5
    HP = 430
    BASE_SPEED = NORMAL_MAX_SPEED * PLAYER_VIEW_SCALE * 0.85
    RANGED_COOLDOWN = 2500
    RANGED_RANGE = 1000

    def __init__(self, world_x, world_y, images, sounds, map_width, map_height,
                 damage_player_fn=None, kill_callback=None, rank=rank):
        super().__init__(
            world_x, world_y, images, sounds, map_width, map_height,
            speed=self.BASE_SPEED,
            near_threshold=0,
            far_threshold=self.RANGED_RANGE,
            radius=30 * PLAYER_VIEW_SCALE,
            push_strength=0.18,
            alert_duration=500,
            damage_player_fn=damage_player_fn,
            rank=rank,
        )
        self.image_original = images["enemy9"]
        self.kill_callback = kill_callback
        self.hp = self.HP
        self.last_ranged_attack = 0

    def update_goal(self, world_x, world_y, player_rect, enemies):
        # 플레이어 위치 추적 및 사거리 내 진입 시 공격
        px = world_x + player_rect.centerx
        py = world_y + player_rect.centery
        dx = px - self.world_x
        dy = py - self.world_y
        dist_to_player = math.hypot(dx, dy)
        self.direction_angle = math.atan2(dy, dx)
        now = pygame.time.get_ticks()

        if self.goal_pos is None or self.move_timer <= 0:
            angle = random.uniform(0, 2 * math.pi)
            dist = random.randint(50, 200)
            self.goal_pos = (
                self.world_x + math.cos(angle) * dist,
                self.world_y + math.sin(angle) * dist
            )
            self.move_timer = random.randint(500, 1000)

        if dist_to_player <= self.RANGED_RANGE and now - self.last_ranged_attack >= self.RANGED_COOLDOWN:
            self.shoot_ranged(px, py)
            self.last_ranged_attack = now

    def shoot_ranged(self, tx, ty):
        # 산성 투사체 발사
        from entities import AcidProjectile
        angle = math.atan2(ty - self.world_y, tx - self.world_x)
        vx = math.cos(angle)
        vy = math.sin(angle)
        if "acid" in self.sounds:
            self.sounds["acid"].play()
        proj = AcidProjectile(
            self.world_x, self.world_y, vx, vy, 9,
            config.images["acid_projectile"], config.images["acid_pool"],
            max_damage=15, dot_damage=5, dot_duration=3000,
            owner=self, sounds=self.sounds
        )
        config.global_enemy_bullets.append(proj)

    def die(self, blood_effects):
        if self._already_dropped:
            return
        super().die(blood_effects)
        self.spawn_dropped_items(4, 5)

    def draw(self, screen, world_x, world_y, shake_offset_x=0, shake_offset_y=0):
        if not self.alive:
            return
        screen_x = self.world_x - world_x + shake_offset_x
        screen_y = self.world_y - world_y + shake_offset_y
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

class Enemy10(AIBase):
    rank = 6

    DETECT_MIN = 0
    DETECT_MAX = 1400 * PLAYER_VIEW_SCALE
    LASER_TRACK_TIME = 1500
    FIRE_DURATION = 2000
    OVERHEAT_TIME = 1000
    FIRE_INTERVAL = 75
    ROT_SPEED_TRACK = math.radians(100)
    ROT_SPEED_FIRE = math.radians(80)
    BULLET_SPEED = 14 * PLAYER_VIEW_SCALE
    BULLET_RANGE = 700 * PLAYER_VIEW_SCALE
    BULLET_DAMAGE = 7
    LASER_THICKNESS = 3
    LASER_COLOR = (255, 0, 0)

    DEATH_EXPL_RADIUS = 180 * PLAYER_VIEW_SCALE
    DEATH_EXPL_DMG_MAX = 35
    DEATH_EXPL_DMG_MIN = 12

    def __init__(self, world_x, world_y, images, sounds, map_width, map_height,
                 damage_player_fn=None, kill_callback=None, rank=rank):
        super().__init__(
            world_x, world_y, images, sounds, map_width, map_height,
            speed=0.0,
            near_threshold=0,
            far_threshold=self.DETECT_MAX,
            radius=30,
            push_strength=0.18,
            alert_duration=800,
            damage_player_fn=damage_player_fn,
            rank=rank,
        )

        self.image_original = images.get("enemy10", images["enemy2"])
        self.gun_image_original = images.get("gun5", None)

        self.bullet_image = images["enemy_bullet"]
        self.explosion_image = images["explosion1"]

        self.fire_sound      = sounds["gun5_fire"]
        self.preheat_sound   = sounds["gun5_preheat"]
        self.overheat_sound  = sounds["gun5_overheat"]
        self.alert_sound     = sounds["drone_warning"]
        self.explosion_sound = sounds["gun6_explosion"]

        self.state = "IDLE"
        self.state_started_at = pygame.time.get_ticks()
        self.last_update_time = self.state_started_at
        self.last_fire_time = 0
        self.show_alert = False

        self.direction_angle = 0.0
        self.current_distance = 36 * PLAYER_VIEW_SCALE
        self.muzzle_extra    = 12 * PLAYER_VIEW_SCALE

        self.laser_endpoint_world = None
        self._alert_channel = None

        self.smokes = []
        self._last_smoke_time = 0

        self.kill_callback = kill_callback
        self.hp = 350

    def hit(self, damage, blood_effects, force=False):
        if not force:
            damage = int(round(damage * 0.8))
        super().hit(damage, [], force=force) # 기계이므로 피가 안튀김

    def _muzzle_world_pos(self):
        mx = self.world_x + math.cos(self.direction_angle) * (self.current_distance + self.muzzle_extra)
        my = self.world_y + math.sin(self.direction_angle) * (self.current_distance + self.muzzle_extra)
        return mx, my

    @staticmethod
    def _angle_lerp(current, target, max_delta):
        diff = (target - current + math.pi) % (2 * math.pi) - math.pi
        if abs(diff) <= max_delta:
            return target
        return current + (max_delta if diff > 0 else -max_delta)

    def _compute_laser_endpoint(self, player_world_pos):
        start = self._muzzle_world_pos()
        angle = self.direction_angle
        step = 8 * PLAYER_VIEW_SCALE
        max_dist = self.BULLET_RANGE

        px, py = player_world_pos
        last_pt = start

        def hit_player(pt):
            return (pt[0]-px)**2 + (pt[1]-py)**2 <= (25*PLAYER_VIEW_SCALE)**2

        def collides(pt):
            if not hasattr(config, "obstacle_manager") or config.obstacle_manager is None:
                return False
            ox, oy = pt
            r_small = 2 * PLAYER_VIEW_SCALE
            for obs in (config.obstacle_manager.static_obstacles + config.obstacle_manager.combat_obstacles):
                for c in getattr(obs, "colliders", []):
                    if getattr(c, "bullet_passable", False):
                        continue
                    cx = obs.world_x + getattr(c, "center", (0,0))[0]
                    cy = obs.world_y + getattr(c, "center", (0,0))[1]
                    shape = getattr(c, "shape", None)
                    if shape == "circle":
                        if self.check_collision_circle((ox,oy), r_small, (cx,cy), c.size):
                            return True
                    elif shape == "ellipse":
                        try: rx, ry = c.size
                        except: continue
                        if self.check_ellipse_circle_collision((ox,oy), r_small, (cx,cy), rx, ry):
                            return True
                    elif shape == "rectangle":
                        try: w, h = c.size
                        except: continue
                        coll_r = ((w/2)**2 + (h/2)**2) ** 0.5
                        if self.check_collision_circle((ox,oy), r_small, (cx,cy), coll_r):
                            return True
            return False

        dist = 0.0
        while dist <= max_dist:
            pt = (start[0] + math.cos(angle) * dist,
                  start[1] + math.sin(angle) * dist)
            if hit_player(pt):
                return pt
            if collides(pt):
                return last_pt
            last_pt = pt
            dist += step
        return last_pt

    def _spawn_smoke(self, count=1):
        mx, my = self._muzzle_world_pos()
        for _ in range(count):
            a = self.direction_angle + math.pi + random.uniform(-0.6, 0.6)
            spd = random.uniform(0.5, 1.5) * PLAYER_VIEW_SCALE
            self.smokes.append({
                "x": mx, "y": my,
                "vx": math.cos(a)*spd, "vy": math.sin(a)*spd - 0.2*PLAYER_VIEW_SCALE,
                "r": random.uniform(5, 10) * PLAYER_VIEW_SCALE,
                "alpha": 180,
                "decay": random.uniform(2.0, 3.5),
            })

    def _update_smokes(self, dt_ms):
        alive = []
        for s in self.smokes:
            s["x"] += s["vx"]
            s["y"] += s["vy"]
            s["r"] *= 1.01
            s["alpha"] -= s["decay"]
            if s["alpha"] > 5:
                alive.append(s)
        self.smokes = alive

    def _fire_once(self):
        mx, my = self._muzzle_world_pos()
        px = mx + math.cos(self.direction_angle) * self.BULLET_RANGE
        py = my + math.sin(self.direction_angle) * self.BULLET_RANGE
        bullet = Bullet(
            mx, my, px, py,
            spread_angle_degrees=3,
            bullet_image=self.bullet_image,
            speed=self.BULLET_SPEED,
            max_distance=self.BULLET_RANGE,
            damage=self.BULLET_DAMAGE
        )
        bullet.trail_enabled = False
        bullet.owner = self
        config.global_enemy_bullets.append(bullet)

    def update_goal(self, world_x, world_y, player_rect, enemies):
        now = pygame.time.get_ticks()
        dt = now - getattr(self, "last_update_time", now)
        self.last_update_time = now

        player_world_pos = (world_x + player_rect.centerx, world_y + player_rect.centery)
        dx = player_world_pos[0] - self.world_x
        dy = player_world_pos[1] - self.world_y
        dist = math.hypot(dx, dy)
        target_angle = math.atan2(dy, dx)

        if self.state == "IDLE":
            self.show_alert = False
            self.laser_endpoint_world = None
            if dist <= self.DETECT_MAX:
                self.state = "TRACKING"
                self.state_started_at = now
                self.show_alert = True
                try: self.preheat_sound.play()
                except: pass
                try:
                    if self._alert_channel is None or not self._alert_channel.get_busy():
                        ch = pygame.mixer.find_channel()
                        if ch:
                            ch.play(self.alert_sound)
                            self._alert_channel = ch
                except: pass

        if self.state == "TRACKING":
            max_delta = self.ROT_SPEED_TRACK * (dt / 1000.0)
            self.direction_angle = self._angle_lerp(self.direction_angle, target_angle, max_delta)
            self.laser_endpoint_world = self._compute_laser_endpoint(player_world_pos)

            if not (dist <= self.DETECT_MAX):
                self.state = "IDLE"
                self.show_alert = False
                if self._alert_channel and self._alert_channel.get_busy():
                    self._alert_channel.stop()
                self.laser_endpoint_world = None

            elif now - self.state_started_at >= self.LASER_TRACK_TIME:
                self.state = "FIRING"
                self.state_started_at = now
                self.last_fire_time = now
                self.show_alert = False
                if self._alert_channel and self._alert_channel.get_busy():
                    self._alert_channel.stop()

        elif self.state == "FIRING":
            max_delta = self.ROT_SPEED_FIRE * (dt / 1000.0)
            self.direction_angle = self._angle_lerp(self.direction_angle, target_angle, max_delta)

            while now - self.last_fire_time >= self.FIRE_INTERVAL:
                self.last_fire_time += self.FIRE_INTERVAL
                self._fire_once()
                try: self.fire_sound.play()
                except: pass

            if now - self.state_started_at >= self.FIRE_DURATION:
                self.state = "OVERHEAT"
                self.state_started_at = now
                self.laser_endpoint_world = None
                try: self.overheat_sound.play()
                except: pass
                self._spawn_smoke(count=4)

        elif self.state == "OVERHEAT":
            self._update_smokes(dt)
            if now - self._last_smoke_time >= 120:
                self._last_smoke_time = now
                self._spawn_smoke(count=1)
            if now - self.state_started_at >= self.OVERHEAT_TIME:
                self.state = "IDLE"
                self.smokes.clear()
                self.laser_endpoint_world = None

    def draw(self, screen, world_x, world_y, shake_offset_x=0, shake_offset_y=0):
        if not self.alive:
            return
        screen_x = self.world_x - world_x + shake_offset_x
        screen_y = self.world_y - world_y + shake_offset_y

        base_rect = self.image_original.get_rect(center=(screen_x, screen_y))
        screen.blit(self.image_original, base_rect)

        if self.gun_image_original is not None:
            barrel = pygame.transform.rotate(self.gun_image_original, -math.degrees(self.direction_angle) - 90)
            bx = self.world_x + math.cos(self.direction_angle) * self.current_distance
            by = self.world_y + math.sin(self.direction_angle) * self.current_distance
            barrel_rect = barrel.get_rect(center=(bx - world_x + shake_offset_x, by - world_y + shake_offset_y))
            screen.blit(barrel, barrel_rect)

        if self.state == "TRACKING" and self.laser_endpoint_world is not None:
            mx, my = self._muzzle_world_pos()
            sx = int(mx - world_x + shake_offset_x)
            sy = int(my - world_y + shake_offset_y)
            ex = int(self.laser_endpoint_world[0] - world_x + shake_offset_x)
            ey = int(self.laser_endpoint_world[1] - world_y + shake_offset_y)
            pygame.draw.line(screen, self.LASER_COLOR, (sx, sy), (ex, ey), self.LASER_THICKNESS)

        self.draw_alert(screen, screen_x, screen_y)

        if self.state == "OVERHEAT" and self.smokes:
            for s in self.smokes:
                r = max(1, int(s["r"]))
                surf = pygame.Surface((r*2+2, r*2+2), pygame.SRCALPHA)
                pygame.draw.circle(surf, (80,80,80, int(max(0, min(255, s["alpha"])))), (r+1, r+1), r)
                screen.blit(surf, (s["x"] - r - world_x + shake_offset_x, s["y"] - r - world_y + shake_offset_y))

    def die(self, blood_effects):
        if self._already_dropped:
            return

        if self._alert_channel and self._alert_channel.get_busy():
            self._alert_channel.stop()

        try: self.explosion_sound.play()
        except: pass
        config.effects.append(ExplosionEffectPersistent(self.world_x, self.world_y, self.explosion_image))

        if hasattr(config, "player_rect"):
            px = config.world_x + config.player_rect.centerx
            py = config.world_y + config.player_rect.centery
            dist = math.hypot(px - self.world_x, py - self.world_y)
            if dist <= self.DEATH_EXPL_RADIUS and hasattr(config, "damage_player"):
                factor = max(0.0, min(1.0, 1.0 - dist / self.DEATH_EXPL_RADIUS))
                dmg = int(round(self.DEATH_EXPL_DMG_MIN + (self.DEATH_EXPL_DMG_MAX - self.DEATH_EXPL_DMG_MIN) * factor))
                config.damage_player(dmg)

        self.spawn_dropped_items(5, 5)
        super().die([])

    def stop_sounds_on_remove(self):
        if self._alert_channel and self._alert_channel.get_busy():
            self._alert_channel.stop()

class Enemy11(AIBase):
    rank = 5

    DETECT_RADIUS = int(600 * PLAYER_VIEW_SCALE)
    TRIGGER_RADIUS = int(250 * PLAYER_VIEW_SCALE)
    CANCEL_RADIUS = int(300 * PLAYER_VIEW_SCALE)
    PREPARE_MS = 1000

    EXPLOSION_RADIUS = int(220 * PLAYER_VIEW_SCALE)
    EXPLOSION_DAMAGE = 60

    def __init__(self, world_x, world_y, images, sounds, map_width, map_height,
                 damage_player_fn=None, kill_callback=None, is_position_blocked_fn=None, rank=rank):
        super().__init__(
            world_x, world_y, images, sounds, map_width, map_height,
            speed=NORMAL_MAX_SPEED * PLAYER_VIEW_SCALE * 1.0,
            near_threshold=0,
            far_threshold=0,
            radius=int(30 * PLAYER_VIEW_SCALE),
            push_strength=0.18,
            alert_duration=self.PREPARE_MS,
            damage_player_fn=damage_player_fn,
            rank=rank,
        )
        self.hp = 260
        self.image_original = images["enemy11"]
        self.image = self.image_original
        self.rect = self.image.get_rect(center=(0, 0))
        self.explosion_image = images["explosion1"]

        self.warning_sound   = sounds["drone_warning"]
        self.explosion_sound = sounds.get("drone_explosion", None)
        self._warn_channel   = None

        self.state = "WANDER"
        self.countdown_until = None
        self._exploding = False
        self.show_alert = False

        self.wander_timer = 0
        self.wander_interval = random.randint(600, 1200)

    def update_goal(self, world_x, world_y, player_rect, enemies):
        # 플레이어 월드 좌표 및 거리/각도
        px = world_x + player_rect.centerx
        py = world_y + player_rect.centery
        dx = px - self.world_x
        dy = py - self.world_y
        dist_to_player = math.hypot(dx, dy)

        self.direction_angle = math.atan2(dy, dx)

        SAFE_DIST = int(60 * PLAYER_VIEW_SCALE)

        now = pygame.time.get_ticks()

        if self.state == "WANDER":
            # 랜덤 배회
            if self.goal_pos is None or now - self.wander_timer > self.wander_interval:
                ang = random.uniform(0, 2 * math.pi)
                d   = random.randint(100, 240)
                tx  = max(0, min(self.world_x + math.cos(ang) * d, self.map_width))
                ty  = max(0, min(self.world_y + math.sin(ang) * d, self.map_height))
                self.goal_pos = (tx, ty)
                self.wander_timer = now
                self.wander_interval = random.randint(600, 1200)

            # 플레이어 감지 시 추격 전환
            if dist_to_player <= self.DETECT_RADIUS:
                self.state = "CHASE"
                self.goal_pos = (px, py)

        elif self.state == "CHASE":
            # 추격: 항상 최신 플레이어 위치를 목표로
            if dist_to_player > SAFE_DIST:
                self.goal_pos = (px, py)
            else:
                # 안전거리 이내면 멈춤(밀림 방지)
                self.goal_pos = None
                self.velocity_x = 0
                self.velocity_y = 0

            if dist_to_player <= self.TRIGGER_RADIUS:
                # 자폭 카운트다운 시작
                self.state = "COUNTDOWN"
                self.countdown_until = now + self.PREPARE_MS
                self._start_warning()
                self.show_alert = True
                self.goal_pos = None  # 카운트다운 중 제자리
            elif dist_to_player > self.DETECT_RADIUS * 1.2:
                # 충분히 멀어지면 배회로 복귀
                self.state = "WANDER"
                self.goal_pos = None

        elif self.state == "COUNTDOWN":
            # 멀어지면 카운트다운 취소 → 다시 추격/배회
            if dist_to_player > self.CANCEL_RADIUS:
                self._stop_warning()
                self.show_alert = False
                self.countdown_until = None
                self.state = "CHASE" if dist_to_player <= self.DETECT_RADIUS else "WANDER"
                return
            # 시간 경과 시 폭발(자살 폭발)
            if self.countdown_until is not None and now >= self.countdown_until:
                self._explode_and_die()
                return

    def _start_warning(self):
        try:
            if (self._warn_channel is None) or (not self._warn_channel.get_busy()):
                ch = pygame.mixer.find_channel()
                if ch:
                    ch.play(self.warning_sound)
                    self._warn_channel = ch
        except:
            pass

    def _stop_warning(self):
        try:
            if self._warn_channel and self._warn_channel.get_busy():
                self._warn_channel.stop()
        except:
            pass

    def _explode_visual_audio(self):
        # 이펙트 + 폭발음
        try:
            config.effects.append(ExplosionEffectPersistent(self.world_x, self.world_y, self.explosion_image))
        except:
            pass
        try:
            if self.explosion_sound:
                self.explosion_sound.play()
        except:
            pass

    def _explode_damage_aoe(self):
        # 플레이어 피해
        if hasattr(config, "player_rect") and self.damage_player:
            px = config.world_x + config.player_rect.centerx
            py = config.world_y + config.player_rect.centery
            if math.hypot(px - self.world_x, py - self.world_y) <= self.EXPLOSION_RADIUS:
                self.damage_player(self.EXPLOSION_DAMAGE)
        try:
            for other in getattr(config, "all_enemies", [])[:]:
                if other is self or not getattr(other, "alive", True):
                    continue
                if math.hypot(other.world_x - self.world_x, other.world_y - self.world_y) <= self.EXPLOSION_RADIUS:
                    other.hit(self.EXPLOSION_DAMAGE, config.blood_effects, force=True)
        except:
            pass

    def _explode_and_die(self):
        if self._exploding:
            return
        self._exploding = True
        self._stop_warning()
        self.show_alert = False
        self._explode_visual_audio()
        self._explode_damage_aoe()
        self.die(config.blood_effects)

    def die(self, blood_effects):
        if self._already_dropped:
            return
        self._stop_warning()
        self._explode_visual_audio()
        self._explode_damage_aoe()
        super().die(blood_effects)
        self.spawn_dropped_items(4, 5)

    def stop_sounds_on_remove(self):
        self._stop_warning()

    def draw(self, screen, world_x, world_y, shake_offset_x=0, shake_offset_y=0):
        if not self.alive:
            return
        screen_x = int(self.world_x - world_x + shake_offset_x)
        screen_y = int(self.world_y - world_y + shake_offset_y)
        scaled = pygame.transform.smoothscale(
            self.image_original,
            (int(self.image_original.get_width() * PLAYER_VIEW_SCALE),
             int(self.image_original.get_height() * PLAYER_VIEW_SCALE))
        )
        rotated = pygame.transform.rotate(scaled, -math.degrees(self.direction_angle) + 90)
        rect = rotated.get_rect(center=(screen_x, screen_y))
        self.rect = rect
        screen.blit(rotated, rect)
        self.draw_alert(screen, screen_x, screen_y)

class Enemy12(AIBase):
    rank = 6

    HP = 450

    BASE_SPEED = NORMAL_MAX_SPEED * PLAYER_VIEW_SCALE * 0.56

    TURN_SPEED_DEG = 60

    FRONT_GUARD_ARC_DEG = 90
    GUARD_REDUCTION_RATE = 0.9
    STUN_ON_EXPLOSION_MS = 1000

    PELLET_COUNT = 10
    PELLET_SPREAD_DEG = 30
    PELLET_DAMAGE = 7
    PELLET_RANGE = 500 * PLAYER_VIEW_SCALE
    FIRE_INTERVAL = 1800
    SHOT_DISTANCE = 300 * PLAYER_VIEW_SCALE

    PLAYER_RADIUS_EST = int(30 * PLAYER_VIEW_SCALE)
    SAFE_GAP = int(30 * PLAYER_VIEW_SCALE)

    BULLET_SPEED = 12

    def __init__(self, world_x, world_y, images, sounds, map_width, map_height,
                 damage_player_fn=None, kill_callback=None, rank=rank):
        super().__init__(
            world_x, world_y, images, sounds, map_width, map_height,
            speed=self.BASE_SPEED,
            near_threshold=self.SHOT_DISTANCE,
            far_threshold=800,
            radius=32,
            push_strength=0.18,
            alert_duration=0,
            damage_player_fn=damage_player_fn,
            rank=rank,
        )

        self.image_original = images["enemy12"]
        self.gun_image_original = pygame.transform.flip(images["gun3"], True, False)
        self.shield_image_original = images["gun19"]
        self.bullet_image = images["enemy_bullet"]
        self.cartridge_image = images["cartridge_case2"]

        self.fire_sound = sounds["gun3_fire_enemy"]
        self.block_sound = sounds["gun19_defend"]

        self.hp = self.HP
        self.last_shot_time = -self.FIRE_INTERVAL
        self.guard_locked_until = 0
        self.block_flash_until = 0
        self._last_rot_update = pygame.time.get_ticks()

        self.kill_callback = kill_callback

        self.current_distance = 45 * PLAYER_VIEW_SCALE

        self.rect = self.image_original.get_rect(center=(0, 0))

    @staticmethod
    def _normalize_angle(rad):
        while rad > math.pi:
            rad -= 2 * math.pi
        while rad < -math.pi:
            rad += 2 * math.pi
        return rad

    def _rotate_towards(self, target_angle, now_ms):
        # 목표 각도까지 초당 TURN_SPEED_DEG 제한으로 회전
        dt = max(0, now_ms - self._last_rot_update)
        max_step = math.radians(self.TURN_SPEED_DEG) * (dt / 1000.0)
        diff = self._normalize_angle(target_angle - self.direction_angle)
        if abs(diff) <= max_step:
            self.direction_angle = target_angle
        else:
            self.direction_angle += math.copysign(max_step, diff)
            self.direction_angle = self._normalize_angle(self.direction_angle)
        self._last_rot_update = now_ms

    def _is_player_in_front_arc(self, player_pos):
        px, py = player_pos
        angle_to_player = math.atan2(py - self.world_y, px - self.world_x)
        diff = self._normalize_angle(angle_to_player - self.direction_angle)
        return abs(math.degrees(diff)) <= (self.FRONT_GUARD_ARC_DEG * 0.5)

    def update_goal(self, world_x, world_y, player_rect, enemies):
        now = pygame.time.get_ticks()
        player_pos = (world_x + player_rect.centerx, world_y + player_rect.centery)

        # 목표 각도 = 플레이어 방향(느리게 추적)
        angle_to_player = math.atan2(player_pos[1] - self.world_y, player_pos[0] - self.world_x)
        self._rotate_towards(angle_to_player, now)

        dx = player_pos[0] - self.world_x
        dy = player_pos[1] - self.world_y
        dist_to_player = math.hypot(dx, dy)

        # 최소 분리(플레이어를 밀지 않게 거리 유지)
        min_sep = self.radius + self.PLAYER_RADIUS_EST + self.SAFE_GAP
        if dist_to_player < min_sep:
            nx = (dx / dist_to_player) if dist_to_player > 0 else 0.0
            ny = (dy / dist_to_player) if dist_to_player > 0 else 0.0
            back = (min_sep - dist_to_player) + int(18 * PLAYER_VIEW_SCALE)
            self.goal_pos = (
                max(0, min(self.map_width,  self.world_x - nx * back)),
                max(0, min(self.map_height, self.world_y - ny * back))
            )
            self.speed = self.BASE_SPEED * 1.1
            return

        # 기본적으로는 플레이어 쪽으로 접근
        self.goal_pos = player_pos

        # 사거리 내면 샷건 사격
        if dist_to_player <= self.SHOT_DISTANCE:
            if now - self.last_shot_time >= self.FIRE_INTERVAL:
                self.shoot()
                self.last_shot_time = now

    def _muzzle_world_pos(self):
        return (
            self.world_x + math.cos(self.direction_angle) * (self.current_distance),
            self.world_y + math.sin(self.direction_angle) * (self.current_distance),
        )

    def shoot(self):
        # 샷건 펠릿 발사 + 탄피 배출
        mx, my = self._muzzle_world_pos()
        base_angle = self.direction_angle

        for _ in range(self.PELLET_COUNT):
            spread = math.radians(random.uniform(-self.PELLET_SPREAD_DEG, self.PELLET_SPREAD_DEG))
            ang = base_angle + spread
            tx = mx + math.cos(ang) * self.PELLET_RANGE
            ty = my + math.sin(ang) * self.PELLET_RANGE

            bullet = Bullet(
                mx, my,
                tx, ty,
                spread_angle_degrees=0,
                bullet_image=self.bullet_image,
                speed=self.BULLET_SPEED,
                max_distance=self.PELLET_RANGE,
                damage=self.PELLET_DAMAGE
            )

            bullet.owner = self
            config.global_enemy_bullets.append(bullet)

        eject_count = random.randint(1, 2)
        for _ in range(eject_count):
            eject_angle = self.direction_angle + math.radians(90 + random.uniform(-15, 15))
            vx, vy = math.cos(eject_angle), math.sin(eject_angle)
            self.scattered_bullets.append(
                ScatteredBullet(self.world_x, self.world_y, vx, vy, self.cartridge_image)
            )

        try:
            self.fire_sound.play()
        except:
            pass

    def hit(self, damage, blood_effects, force=False):
        # 전방 각도에서 피격 시 90% 경감.
        now = pygame.time.get_ticks()
        if force:
            self.guard_locked_until = now + self.STUN_ON_EXPLOSION_MS

        reduced_damage = damage
        # 플레이어가 전방 원호 내에 있고, 방패가 경직 중이 아니면 경감
        player_pos = (config.world_x + config.player_rect.centerx,
                      config.world_y + config.player_rect.centery)
        if now >= self.guard_locked_until and self._is_player_in_front_arc(player_pos):
            reduced_damage = max(1, int(damage * (1.0 - self.GUARD_REDUCTION_RATE)))
            self.block_flash_until = now + 150
            try:
                self.block_sound.play()
            except:
                pass

        super().hit(reduced_damage, blood_effects, force)

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

        # 총기(샷건)
        gun_cx = screen_x + math.cos(self.direction_angle) * (self.current_distance)
        gun_cy = screen_y + math.sin(self.direction_angle) * (self.current_distance)
        rotated_gun = pygame.transform.rotate(
            self.gun_image_original, -math.degrees(self.direction_angle) - 90
        )
        gun_rect = rotated_gun.get_rect(center=(gun_cx, gun_cy))
        screen.blit(rotated_gun, gun_rect)

        # 본체
        scaled_img = pygame.transform.smoothscale(
            self.image_original,
            (
                int(self.image_original.get_width() * PLAYER_VIEW_SCALE),
                int(self.image_original.get_height() * PLAYER_VIEW_SCALE),
            )
        )
        rotated_img = pygame.transform.rotate(
            scaled_img, -math.degrees(self.direction_angle) + 90
        )
        body_rect = rotated_img.get_rect(center=(screen_x, screen_y))
        self.rect = body_rect
        screen.blit(rotated_img, body_rect)

        # 방패(전방 표시) — 막은 직후 약간 더 진하게
        offset = (self.radius + 10 * PLAYER_VIEW_SCALE)
        shield_cx = screen_x + math.cos(self.direction_angle) * offset
        shield_cy = screen_y + math.sin(self.direction_angle) * offset
        rotated_shield = pygame.transform.rotate(
            self.shield_image_original, -math.degrees(self.direction_angle) - 90
        )
        alpha = 110
        if pygame.time.get_ticks() < self.block_flash_until:
            alpha = 220
        temp = rotated_shield.copy()
        temp.set_alpha(alpha)
        shield_rect = temp.get_rect(center=(shield_cx, shield_cy))
        screen.blit(temp, shield_rect)

        self.draw_alert(screen, screen_x, screen_y)

class Enemy13(AIBase):
    rank = 9

    MAX_HP = 750
    BASE_SPEED = NORMAL_MAX_SPEED * PLAYER_VIEW_SCALE * 0.6

    FRONT_ARC_DEG = 120
    FRONT_REDUCE_RATE = 0.3

    SUMMON_COOLDOWN_MS = 7500
    SUMMON_COOLDOWN_PHASE2_MS = 5000
    TELEGRAPH_MS = 700
    SUMMON_MIN_RADIUS = int(500 * PLAYER_VIEW_SCALE)
    SUMMON_MAX_RADIUS = int(800 * PLAYER_VIEW_SCALE)
    MAX_MINIONS = 4

    NEAR_DISTANCE = int(500 * PLAYER_VIEW_SCALE)
    FAR_DISTANCE  = int(900 * PLAYER_VIEW_SCALE)

    TURN_SPEED_DEG = 80

    ORBIT_DPS = 60
    ORBIT_SPRING = 0.15
    ORBIT_NOISE_PX = int(60 * PLAYER_VIEW_SCALE)
    ORBIT_RADIUS_JITTER = int(80 * PLAYER_VIEW_SCALE)
    STRAFE_SWITCH_MS = 1500

    def __init__(self, world_x, world_y, images, sounds, map_width, map_height,
                 damage_player_fn=None, kill_callback=None, rank=rank):
        super().__init__(
            world_x, world_y, images, sounds, map_width, map_height,
            speed=self.BASE_SPEED,
            near_threshold=0,
            far_threshold=0,
            radius=36,
            push_strength=0.18,
            alert_duration=0,
            damage_player_fn=damage_player_fn,
            rank=rank,
        )
        self.images = images
        self.sounds = sounds

        self.image_original = images["enemy13"]
        self.rect = self.image_original.get_rect(center=(0, 0))
        self.spawn_sound = sounds["spawn_enemy"]

        self.hp = self.MAX_HP
        self._last_rot_update = pygame.time.get_ticks()

        self._last_summon_ms = -self.SUMMON_COOLDOWN_MS
        self._telegraph_active = False
        self._telegraph_pos = (self.world_x, self.world_y)
        self._telegraph_until = 0

        self._strafe_dir = 1
        self._last_strafe_switch = pygame.time.get_ticks()
        self._orbit_angle = None
        self._last_orbit_update = pygame.time.get_ticks()
        self._noise_seed = random.random() * 1000.0

        self._my_minions = []

        self.kill_callback = kill_callback

    @staticmethod
    def _normalize_angle(rad):
        while rad > math.pi:
            rad -= 2 * math.pi
        while rad < -math.pi:
            rad += 2 * math.pi
        return rad

    def _rotate_towards(self, target_angle, now_ms):
        dt = max(0, now_ms - self._last_rot_update)
        max_step = math.radians(self.TURN_SPEED_DEG) * (dt / 1000.0)
        diff = self._normalize_angle(target_angle - self.direction_angle)
        if abs(diff) <= max_step:
            self.direction_angle = target_angle
        else:
            self.direction_angle += math.copysign(max_step, diff)
            self.direction_angle = self._normalize_angle(self.direction_angle)
        self._last_rot_update = now_ms

    def _is_in_front_arc(self, src_x, src_y):
        # 공격원점(src) 기준 전방 ±60° 판정.
        angle_to_src = math.atan2(src_y - self.world_y, src_x - self.world_x)
        diff = self._normalize_angle(angle_to_src - self.direction_angle)
        return abs(math.degrees(diff)) <= (self.FRONT_ARC_DEG * 0.5)

    def _phase2(self):
        return self.hp <= (self.MAX_HP * 0.5)

    def _current_cooldown(self):
        return self.SUMMON_COOLDOWN_PHASE2_MS if self._phase2() else self.SUMMON_COOLDOWN_MS

    def _minion_count_alive(self):
        alive = 0
        for m in self._my_minions[:]:
            if getattr(m, "alive", False):
                alive += 1
            else:
                self._my_minions.remove(m)
        return alive

    def _random_summon_pos(self, player_pos):
        # 플레이어 주변 링(500~800)에서 맵 내 좌표 샘플링.
        px, py = player_pos
        for _ in range(18):
            r = random.randint(self.SUMMON_MIN_RADIUS, self.SUMMON_MAX_RADIUS)
            ang = random.uniform(0, 2 * math.pi)
            x = max(0, min(px + math.cos(ang) * r, self.map_width))
            y = max(0, min(py + math.sin(ang) * r, self.map_height))
            margin = int(30 * PLAYER_VIEW_SCALE)
            if margin <= x <= self.map_width - margin and margin <= y <= self.map_height - margin:
                return (x, y)
        # 실패 시 본체 주변으로 폴백
        r = int(200 * PLAYER_VIEW_SCALE)
        ang = random.uniform(0, 2 * math.pi)
        return (
            max(0, min(self.world_x + math.cos(ang) * r, self.map_width)),
            max(0, min(self.world_y + math.sin(ang) * r, self.map_height))
        )

    def _choose_minion_class(self):
        # Rank1/2/3 가중 랜덤. Phase2에서 Rank3 확률 상승.
        if self._phase2():
            weights = [(Enemy1, 0.35), (Enemy2, 0.35), (Enemy3, 0.30)]
        else:
            weights = [(Enemy1, 0.55), (Enemy2, 0.35), (Enemy3, 0.10)]
        r = random.random()
        acc = 0.0
        for cls, w in weights:
            acc += w
            if r <= acc:
                return cls
        return Enemy1

    def _start_telegraph(self, pos):
        self._telegraph_pos = pos
        self._telegraph_active = True
        self._telegraph_until = pygame.time.get_ticks() + self.TELEGRAPH_MS
        try:
            self.spawn_sound.play()
        except:
            pass

    def _finish_telegraph_and_summon(self):
        # 텔레그래프 종료 시 실제 스폰.
        self._telegraph_active = False
        sx, sy = self._telegraph_pos

        if self._minion_count_alive() >= self.MAX_MINIONS:
            return

        MinionClass = self._choose_minion_class()
        try:
            minion = MinionClass(
                sx, sy, self.images, self.sounds, self.map_width, self.map_height,
                damage_player_fn=self.damage_player, kill_callback=self.kill_callback, rank=MinionClass.rank
            )
        except TypeError:
            minion = MinionClass(
                sx, sy, self.images, self.sounds, self.map_width, self.map_height,
                damage_player_fn=self.damage_player, kill_callback=self.kill_callback
            )

        setattr(minion, "summoned_by", self)

        if not hasattr(config, "all_enemies"):
            config.all_enemies = []
        config.all_enemies.append(minion)
        self._my_minions.append(minion)

    def update_goal(self, world_x, world_y, player_rect, enemies):
        now = pygame.time.get_ticks()
        px, py = world_x + player_rect.centerx, world_y + player_rect.centery

        # 시선: 플레이어 방향으로 천천히 회전(전방 경감 기준)
        self._rotate_towards(math.atan2(py - self.world_y, px - self.world_x), now)

        # 소환 타이밍
        if not self._telegraph_active:
            if (now - self._last_summon_ms) >= self._current_cooldown():
                if self._minion_count_alive() < self.MAX_MINIONS:
                    self._start_telegraph(self._random_summon_pos((px, py)))
                    self._last_summon_ms = now
        else:
            if now >= self._telegraph_until:
                self._finish_telegraph_and_summon()

        # ─ 자유로운 거리 유지: 궤도 + 노이즈 드리프트
        dx, dy = px - self.world_x, py - self.world_y
        dist = math.hypot(dx, dy) + 1e-6

        if self._orbit_angle is None:
            # 플레이어 기준 적의 극좌표 각도
            self._orbit_angle = math.atan2(self.world_y - py, self.world_x - px)
            self._last_orbit_update = now

        # 좌/우 전환
        if now - self._last_strafe_switch >= self.STRAFE_SWITCH_MS:
            self._strafe_dir *= -1
            self._last_strafe_switch = now

        # 목표 반경 설정(근접/과원거리 보정 + 서서히 흔들림)
        mid_r = (self.NEAR_DISTANCE + self.FAR_DISTANCE) * 0.5
        jitter = math.sin((now * 0.003) + self._noise_seed) * self.ORBIT_RADIUS_JITTER
        if dist < self.NEAR_DISTANCE:
            desired_r = self.NEAR_DISTANCE + (40 * PLAYER_VIEW_SCALE)
        elif dist > self.FAR_DISTANCE:
            desired_r = self.FAR_DISTANCE - (40 * PLAYER_VIEW_SCALE)
        else:
            desired_r = mid_r + jitter

        # 스프링으로 현재 거리 → 목표 반경 수렴
        target_r = dist + (desired_r - dist) * self.ORBIT_SPRING

        # 궤도 각도 진행
        dt_s = max(0.0, (now - self._last_orbit_update) / 1000.0)
        self._last_orbit_update = now
        self._orbit_angle += math.radians(self.ORBIT_DPS) * dt_s * self._strafe_dir

        # 궤도 목표점(플레이어 중심 원)
        orbit_tx = px + math.cos(self._orbit_angle) * target_r
        orbit_ty = py + math.sin(self._orbit_angle) * target_r

        # 노이즈 드리프트
        n1 = now * 0.002 + self._noise_seed * 2.13
        n2 = now * 0.0016 + self._noise_seed * 3.77
        nx = math.cos(n1) * self.ORBIT_NOISE_PX
        ny = math.sin(n2) * (self.ORBIT_NOISE_PX * 0.6)

        gx = max(0, min(orbit_tx + nx, self.map_width))
        gy = max(0, min(orbit_ty + ny, self.map_height))
        self.goal_pos = (gx, gy)

    def hit(self, damage, blood_effects, force=False):
        # 전방 ±60°일 때 피해 30% 감소(= 0.7배).
        # 피격 경직 없음: force(넉백/경직) 무시.
        src_x = config.world_x + config.player_rect.centerx
        src_y = config.world_y + config.player_rect.centery

        reduced = damage
        if self._is_in_front_arc(src_x, src_y):
            reduced = max(1, int(round(damage * (1.0 - self.FRONT_REDUCE_RATE))))

        # 경직 무효화를 위해 force=False로 전달
        super().hit(reduced, blood_effects, force=False)

    def die(self, blood_effects):
        if self._already_dropped:
            return
        super().die(blood_effects)
        self.spawn_dropped_items(8, 10)

    def draw(self, screen, world_x, world_y, shake_offset_x=0, shake_offset_y=0):
        if not self.alive:
            return

        sx = self.world_x - world_x + shake_offset_x
        sy = self.world_y - world_y + shake_offset_y

        # 본체
        scaled = pygame.transform.smoothscale(
            self.image_original,
            (
                int(self.image_original.get_width() * PLAYER_VIEW_SCALE),
                int(self.image_original.get_height() * PLAYER_VIEW_SCALE),
            )
        )
        rotated = pygame.transform.rotate(scaled, -math.degrees(self.direction_angle) + 90)
        body_rect = rotated.get_rect(center=(sx, sy))
        self.rect = body_rect
        screen.blit(rotated, body_rect)

        # 소환진(텔레그래프) — 원형 글로우
        if self._telegraph_active:
            tx, ty = self._telegraph_pos
            tsx = tx - world_x + shake_offset_x
            tsy = ty - world_y + shake_offset_y
            remain = max(0, self._telegraph_until - pygame.time.get_ticks())
            t = 1.0 - (remain / float(self.TELEGRAPH_MS + 1))
            radius = int(30 * PLAYER_VIEW_SCALE + 40 * PLAYER_VIEW_SCALE * t)
            alpha = max(60, int(200 * (0.5 + 0.5 * math.sin(t * math.pi))))
            glow = pygame.Surface((radius * 2 + 4, radius * 2 + 4), pygame.SRCALPHA)


            pygame.draw.circle(glow, (220, 30, 30, alpha), (glow.get_width() // 2, glow.get_height() // 2), radius, 6)
            pygame.draw.circle(glow, (255, 60, 60, int(alpha * 0.6)),
                               (glow.get_width() // 2, glow.get_height() // 2),
                               max(2, radius - 8))
            glow_rect = glow.get_rect(center=(tsx, tsy))
            screen.blit(glow, glow_rect)

class Enemy14(AIBase):
    rank = 5

    MAX_HP = 420
    BASE_SPEED = NORMAL_MAX_SPEED * PLAYER_VIEW_SCALE * 0.65

    NEAR_DISTANCE = int(320 * PLAYER_VIEW_SCALE)
    FAR_DISTANCE  = int(820 * PLAYER_VIEW_SCALE)

    TURN_SPEED_DEG = 70

    ORBIT_DPS = 45
    ORBIT_SPRING = 0.15
    ORBIT_NOISE_PX = int(40 * PLAYER_VIEW_SCALE)
    ORBIT_RADIUS_JITTER = int(60 * PLAYER_VIEW_SCALE)
    STRAFE_SWITCH_MS = 2000

    SUMMON_COOLDOWN_MS = 10000
    SUMMON_COOLDOWN_PHASE2_MS = 7000
    TELEGRAPH_MS = 700
    SUMMON_MIN_RADIUS = int(400 * PLAYER_VIEW_SCALE)   # 자기 기준
    SUMMON_MAX_RADIUS = int(600 * PLAYER_VIEW_SCALE)   # 자기 기준
    MAX_MINIONS = 3

    def __init__(self, world_x, world_y, images, sounds, map_width, map_height,
                 damage_player_fn=None, kill_callback=None, rank=rank):
        super().__init__(
            world_x, world_y, images, sounds, map_width, map_height,
            speed=self.BASE_SPEED,
            near_threshold=0,
            far_threshold=0,
            radius=34,
            push_strength=0.18,
            alert_duration=0,
            damage_player_fn=damage_player_fn,
            rank=rank,
        )

        self.images = images
        self.sounds = sounds

        self.image_original = images["enemy14"]
        self.rect = self.image_original.get_rect(center=(0, 0))
        self.spawn_sound = sounds["spawn_enemy"]
        try:
            self.spawn_sound.set_volume(0.5)
        except:
            pass

        self.hp = self.MAX_HP
        self._last_rot_update = pygame.time.get_ticks()

        self._last_summon_ms = -self.SUMMON_COOLDOWN_MS
        self._telegraph_active = False
        self._telegraph_pos = (self.world_x, self.world_y)
        self._telegraph_until = 0

        self._strafe_dir = 1
        self._last_strafe_switch = pygame.time.get_ticks()
        self._orbit_angle = None
        self._last_orbit_update = pygame.time.get_ticks()
        self._noise_seed = random.random() * 1000.0

        self._my_minions = []

        self.kill_callback = kill_callback

    @staticmethod
    def _normalize_angle(rad):
        while rad > math.pi:
            rad -= 2 * math.pi
        while rad < -math.pi:
            rad += 2 * math.pi
        return rad

    def _rotate_towards(self, target_angle, now_ms):
        dt = max(0, now_ms - self._last_rot_update)
        max_step = math.radians(self.TURN_SPEED_DEG) * (dt / 1000.0)
        diff = self._normalize_angle(target_angle - self.direction_angle)
        if abs(diff) <= max_step:
            self.direction_angle = target_angle
        else:
            self.direction_angle += math.copysign(max_step, diff)
            self.direction_angle = self._normalize_angle(self.direction_angle)
        self._last_rot_update = now_ms

    def _phase2(self):
        return self.hp <= (self.MAX_HP * 0.5)

    def _current_cooldown(self):
        return self.SUMMON_COOLDOWN_PHASE2_MS if self._phase2() else self.SUMMON_COOLDOWN_MS

    def _minion_count_alive(self):
        alive = 0
        for m in self._my_minions[:]:
            if getattr(m, "alive", False):
                alive += 1
            else:
                self._my_minions.remove(m)
        return alive

    def _random_summon_pos(self):
        # 자신 기준 링(400~600)에서 맵 내 좌표 샘플링.
        cx, cy = self.world_x, self.world_y
        for _ in range(18):
            r = random.randint(self.SUMMON_MIN_RADIUS, self.SUMMON_MAX_RADIUS)
            ang = random.uniform(0, 2 * math.pi)
            x = max(0, min(cx + math.cos(ang) * r, self.map_width))
            y = max(0, min(cy + math.sin(ang) * r, self.map_height))
            margin = int(30 * PLAYER_VIEW_SCALE)
            if margin <= x <= self.map_width - margin and margin <= y <= self.map_height - margin:
                return (x, y)
        # 실패 시 아주 가까운 원으로 폴백
        r = int(180 * PLAYER_VIEW_SCALE)
        ang = random.uniform(0, 2 * math.pi)
        return (
            max(0, min(cx + math.cos(ang) * r, self.map_width)),
            max(0, min(cy + math.sin(ang) * r, self.map_height))
        )

    def _choose_minion_class(self):
        # Rank1/2만 랜덤. (Phase2에서도 Rank3은 없음)
        if self._phase2():
            weights = [(Enemy1, 0.50), (Enemy2, 0.50)]
        else:
            weights = [(Enemy1, 0.60), (Enemy2, 0.40)]
        r = random.random()
        acc = 0.0
        for cls, w in weights:
            acc += w
            if r <= acc:
                return cls
        return Enemy1

    def _start_telegraph(self, pos):
        self._telegraph_pos = pos
        self._telegraph_active = True
        self._telegraph_until = pygame.time.get_ticks() + self.TELEGRAPH_MS
        try:
            self.spawn_sound.play()
        except:
            pass

    def _finish_telegraph_and_summon(self):
        self._telegraph_active = False
        sx, sy = self._telegraph_pos

        if self._minion_count_alive() >= self.MAX_MINIONS:
            return

        MinionClass = self._choose_minion_class()
        try:
            minion = MinionClass(
                sx, sy, self.images, self.sounds, self.map_width, self.map_height,
                damage_player_fn=self.damage_player, kill_callback=self.kill_callback, rank=MinionClass.rank
            )
        except TypeError:
            minion = MinionClass(
                sx, sy, self.images, self.sounds, self.map_width, self.map_height,
                damage_player_fn=self.damage_player, kill_callback=self.kill_callback
            )

        setattr(minion, "summoned_by", self)

        if not hasattr(config, "all_enemies"):
            config.all_enemies = []
        config.all_enemies.append(minion)
        self._my_minions.append(minion)

    def update_goal(self, world_x, world_y, player_rect, enemies):
        now = pygame.time.get_ticks()
        px, py = world_x + player_rect.centerx, world_y + player_rect.centery

        # 시선: 플레이어 방향으로 천천히 회전(연출/일관성)
        self._rotate_towards(math.atan2(py - self.world_y, px - self.world_x), now)

        # 소환 타이밍
        if not self._telegraph_active:
            if (now - self._last_summon_ms) >= self._current_cooldown():
                if self._minion_count_alive() < self.MAX_MINIONS:
                    self._start_telegraph(self._random_summon_pos())
                    self._last_summon_ms = now
        else:
            if now >= self._telegraph_until:
                self._finish_telegraph_and_summon()

        # ─ 자유로운 거리 유지: 궤도 + 노이즈 드리프트 (Enemy13보다 둔하게)
        dx, dy = px - self.world_x, py - self.world_y
        dist = math.hypot(dx, dy) + 1e-6

        if self._orbit_angle is None:
            # 플레이어 기준 적의 극좌표 각도
            self._orbit_angle = math.atan2(self.world_y - py, self.world_x - px)
            self._last_orbit_update = now

        # 좌/우 전환
        if now - self._last_strafe_switch >= self.STRAFE_SWITCH_MS:
            self._strafe_dir *= -1
            self._last_strafe_switch = now

        # 목표 반경(근접/과원거리 보정 + 서서히 흔들림)
        mid_r = (self.NEAR_DISTANCE + self.FAR_DISTANCE) * 0.5
        jitter = math.sin((now * 0.003) + self._noise_seed) * self.ORBIT_RADIUS_JITTER
        if dist < self.NEAR_DISTANCE:
            desired_r = self.NEAR_DISTANCE + (40 * PLAYER_VIEW_SCALE)
        elif dist > self.FAR_DISTANCE:
            desired_r = self.FAR_DISTANCE - (40 * PLAYER_VIEW_SCALE)
        else:
            desired_r = mid_r + jitter

        # 스프링으로 현재 거리 → 목표 반경 수렴
        target_r = dist + (desired_r - dist) * self.ORBIT_SPRING

        # 궤도 각도 진행
        dt_s = max(0.0, (now - self._last_orbit_update) / 1000.0)
        self._last_orbit_update = now
        self._orbit_angle += math.radians(self.ORBIT_DPS) * dt_s * self._strafe_dir

        # 궤도 목표점(플레이어 중심 원)
        orbit_tx = px + math.cos(self._orbit_angle) * target_r
        orbit_ty = py + math.sin(self._orbit_angle) * target_r

        # 노이즈 드리프트
        n1 = now * 0.002 + self._noise_seed * 2.13
        n2 = now * 0.0016 + self._noise_seed * 3.77
        nx = math.cos(n1) * self.ORBIT_NOISE_PX
        ny = math.sin(n2) * int(self.ORBIT_NOISE_PX * 0.6)

        gx = max(0, min(orbit_tx + nx, self.map_width))
        gy = max(0, min(orbit_ty + ny, self.map_height))
        self.goal_pos = (gx, gy)

    def hit(self, damage, blood_effects, force=False):
        # 방어 보정 없음(전방 경감 X)
        # 피격 경직/넉백 허용: force를 그대로 전달
        super().hit(damage, blood_effects, force)

    def die(self, blood_effects):
        if self._already_dropped:
            return
        super().die(blood_effects)
        self.spawn_dropped_items(4, 5)

    def draw(self, screen, world_x, world_y, shake_offset_x=0, shake_offset_y=0):
        if not self.alive:
            return

        sx = self.world_x - world_x + shake_offset_x
        sy = self.world_y - world_y + shake_offset_y

        # 본체
        scaled = pygame.transform.smoothscale(
            self.image_original,
            (
                int(self.image_original.get_width() * PLAYER_VIEW_SCALE),
                int(self.image_original.get_height() * PLAYER_VIEW_SCALE),
            )
        )
        rotated = pygame.transform.rotate(scaled, -math.degrees(self.direction_angle) + 90)
        body_rect = rotated.get_rect(center=(sx, sy))
        self.rect = body_rect
        screen.blit(rotated, body_rect)

        # 소환진(텔레그래프) — 원형 글로우(더 작고 흐릿함 / Phase2에서 약간만 강화)
        if self._telegraph_active:
            ts = pygame.time.get_ticks()
            tx, ty = self._telegraph_pos
            tsx = tx - world_x + shake_offset_x
            tsy = ty - world_y + shake_offset_y
            remain = max(0, self._telegraph_until - ts)
            t = 1.0 - (remain / float(self.TELEGRAPH_MS + 1))
            base_min = 24 * PLAYER_VIEW_SCALE
            base_add = 12 * PLAYER_VIEW_SCALE
            if self._phase2():
                base_min += 4 * PLAYER_VIEW_SCALE
                base_add += 4 * PLAYER_VIEW_SCALE
            radius = int(base_min + base_add * t)
            base_alpha = 140 if not self._phase2() else 160
            alpha = max(50, int(base_alpha * (0.6 + 0.4 * math.sin(t * math.pi))))
            glow = pygame.Surface((radius * 2 + 4, radius * 2 + 4), pygame.SRCALPHA)
            pygame.draw.circle(glow, (200, 40, 40, alpha), (glow.get_width() // 2, glow.get_height() // 2), radius, 5)
            pygame.draw.circle(glow, (255, 70, 70, int(alpha * 0.55)),
                               (glow.get_width() // 2, glow.get_height() // 2),
                               max(2, radius - 7))
            glow_rect = glow.get_rect(center=(tsx, tsy))
            screen.blit(glow, glow_rect)

class Enemy15(AIBase):
    rank = 7

    MAX_HP = 650
    BASE_SPEED = NORMAL_MAX_SPEED * PLAYER_VIEW_SCALE * 0.80

    TRIGGER_RADIUS = int(200 * PLAYER_VIEW_SCALE)
    TELEGRAPH_MS   = 800
    LUNGE_DISTANCE = int(360 * PLAYER_VIEW_SCALE)
    LUNGE_SPEED    = NORMAL_MAX_SPEED * PLAYER_VIEW_SCALE * 3.0
    LUNGE_MAX_MS   = 600
    RECOVER_MS     = 700
    LUNGE_WIDTH    = int(48 * PLAYER_VIEW_SCALE)

    # 피해
    ONHIT_DAMAGE        = 15
    PROX_TICK_MS        = 750
    PROX_EXTRA_MARGIN   = int(6 * PLAYER_VIEW_SCALE)
    PLAYER_RADIUS_EST   = int(15 * PLAYER_VIEW_SCALE)

    TELEGRAPH_ALPHA = 76

    def __init__(self, world_x, world_y, images, sounds, map_width, map_height,
                 damage_player_fn=None, kill_callback=None, rank=rank):
        super().__init__(
            world_x, world_y, images, sounds, map_width, map_height,
            speed=self.BASE_SPEED,
            near_threshold=0,
            far_threshold=0,
            radius=int(28 * PLAYER_VIEW_SCALE),
            push_strength=0.18,
            alert_duration=0,
            damage_player_fn=damage_player_fn,
            rank=rank,
        )

        self.image_original = images.get("enemy15", images.get("enemy13", images.get("enemy11")))
        self.rect = self.image_original.get_rect(center=(0, 0))

        self.hp = self.MAX_HP
        self.state = "CHASE"  # CHASE → TELEGRAPH → LUNGE → RECOVER → CHASE
        self.state_until = 0

        self.telegraph_origin = (self.world_x, self.world_y)
        self.telegraph_dir = (1.0, 0.0)
        self.telegraph_angle = 0.0

        self.lunge_dir = (1.0, 0.0)
        self.lunge_start_pos = (self.world_x, self.world_y)
        self.lunge_has_hit = False

        self._next_prox_dmg_ms = 0

        self.kill_callback = kill_callback

    @staticmethod
    def _norm(dx, dy):
        d = math.hypot(dx, dy)
        if d == 0:
            return (0.0, 0.0)
        return (dx / d, dy / d)

    def _distance_travelled_from_lunge_start(self):
        x0, y0 = self.lunge_start_pos
        return math.hypot(self.world_x - x0, self.world_y - y0)

    def _apply_proximity_damage(self, now, px, py):
        # 플레이어와 매우 가까우면 0.5초마다 피해를 준다.
        dist = math.hypot(px - self.world_x, py - self.world_y)
        threshold = self.radius + self.PLAYER_RADIUS_EST + self.PROX_EXTRA_MARGIN
        if dist <= threshold and now >= self._next_prox_dmg_ms:
            if self.damage_player:
                self.damage_player(int(self.ONHIT_DAMAGE))
            else:
                try:
                    config.damage_player(int(self.ONHIT_DAMAGE))
                except Exception:
                    pass
            self._next_prox_dmg_ms = now + self.PROX_TICK_MS

    def update_goal(self, world_x, world_y, player_rect, enemies):
        now = pygame.time.get_ticks()
        px, py = world_x + player_rect.centerx, world_y + player_rect.centery
        dx, dy = px - self.world_x, py - self.world_y
        dist   = math.hypot(dx, dy)

        # 시선 처리: TELEGRAPH/LUNGE에선 고정된 각도를 표시
        if self.state == "TELEGRAPH":
            self.direction_angle = self.telegraph_angle
        elif self.state == "LUNGE":
            # 텔레그래프에서 고정한 방향 유지
            self.direction_angle = math.atan2(self.lunge_dir[1], self.lunge_dir[0])
        else:
            if dx or dy:
                self.direction_angle = math.atan2(dy, dx)

        if self.state == "CHASE":
            # 추격
            self.speed = self.BASE_SPEED
            self.goal_pos = (px, py)

            # 근접 틱 데미지(추격 중에도 근접하면 깎임)
            self._apply_proximity_damage(now, px, py)

            if dist <= self.TRIGGER_RADIUS:
                # TELEGRAPH 시작: 현재 위치/각도/방향/원점을 고정
                self.state = "TELEGRAPH"
                self.state_until = now + self.TELEGRAPH_MS
                self.telegraph_origin = (self.world_x, self.world_y)
                dirx, diry = self._norm(dx, dy)
                if dirx == 0 and diry == 0:
                    dirx, diry = 1.0, 0.0
                self.telegraph_dir = (dirx, diry)
                self.telegraph_angle = math.atan2(diry, dirx)
                # 예고 동안은 제자리
                self.goal_pos = (self.world_x, self.world_y)

        elif self.state == "TELEGRAPH":
            # 제자리 대기 + 근접 틱 데미지
            self.goal_pos = (self.world_x, self.world_y)
            self._apply_proximity_damage(now, px, py)

            if now >= self.state_until:
                # LUNGE 시작
                self.state = "LUNGE"
                self.state_until = now + self.LUNGE_MAX_MS
                self.lunge_dir = self.telegraph_dir
                self.lunge_start_pos = (self.world_x, self.world_y)
                self.lunge_has_hit = False
                self.speed = self.LUNGE_SPEED
                # 목표를 끝점 방향으로 멀리 설정해 직진 유도
                end_x = self.world_x + self.lunge_dir[0] * (self.LUNGE_DISTANCE + 200)
                end_y = self.world_y + self.lunge_dir[1] * (self.LUNGE_DISTANCE + 200)
                self.goal_pos = (end_x, end_y)

        elif self.state == "LUNGE":
            # 고정 방향 직진
            end_x = self.world_x + self.lunge_dir[0] * (self.LUNGE_DISTANCE + 200)
            end_y = self.world_y + self.lunge_dir[1] * (self.LUNGE_DISTANCE + 200)
            self.goal_pos = (end_x, end_y)

            # 근접 틱 데미지
            self._apply_proximity_damage(now, px, py)

            # 즉시 ‘명중’ 판정(가까워졌을 때 한 번)
            if not self.lunge_has_hit:
                threshold = self.radius + self.PLAYER_RADIUS_EST + self.PROX_EXTRA_MARGIN
                if dist <= threshold:
                    self.lunge_has_hit = True
                    # 즉시 피해 + 틱 쿨다운 공유(중복 방지)
                    if self.damage_player:
                        self.damage_player(int(self.ONHIT_DAMAGE))
                    else:
                        try:
                            config.damage_player(int(self.ONHIT_DAMAGE))
                        except Exception:
                            pass
                    self._next_prox_dmg_ms = now + self.PROX_TICK_MS
                    # 바로 회복 단계로
                    self.state = "RECOVER"
                    self.state_until = now + self.RECOVER_MS
                    self.speed = self.BASE_SPEED
                    self.goal_pos = (self.world_x, self.world_y)
                    return

            # 거리/시간 조건 충족 시 종료
            if (self._distance_travelled_from_lunge_start() >= self.LUNGE_DISTANCE) or (now >= self.state_until):
                self.state = "RECOVER"
                self.state_until = now + self.RECOVER_MS
                self.speed = self.BASE_SPEED
                self.goal_pos = (self.world_x, self.world_y)

        elif self.state == "RECOVER":
            # 잠깐 숨 고른 뒤 다시 추격 + 근접 틱 데미지
            self.goal_pos = (self.world_x, self.world_y)
            self._apply_proximity_damage(now, px, py)
            if now >= self.state_until:
                self.state = "CHASE"

    def hit(self, damage, blood_effects, force=False):
        super().hit(damage, blood_effects, force)

    def die(self, blood_effects):
        if self._already_dropped:
            return
        super().die(blood_effects)
        try:
            self.spawn_dropped_items(6, 7)
        except:
            pass

    def draw(self, screen, world_x, world_y, shake_offset_x=0, shake_offset_y=0):
        if not self.alive:
            return

        # 본체 드로우
        sx = int(self.world_x - world_x + shake_offset_x)
        sy = int(self.world_y - world_y + shake_offset_y)

        scaled = pygame.transform.smoothscale(
            self.image_original,
            (int(self.image_original.get_width() * PLAYER_VIEW_SCALE),
             int(self.image_original.get_height() * PLAYER_VIEW_SCALE))
        )
        angle_deg = -math.degrees(self.direction_angle) + 90
        rotated = pygame.transform.rotate(scaled, angle_deg)
        rect = rotated.get_rect(center=(sx, sy))
        self.rect = rect
        screen.blit(rotated, rect)

        # 텔레그래프 히트박스(빨간 반투명 회전 사각형)
        if self.state == "TELEGRAPH":
            ox, oy = self.telegraph_origin
            dirx, diry = self.telegraph_dir
            osx = int(ox - world_x + shake_offset_x)
            osy = int(oy - world_y + shake_offset_y)
            ex = ox + dirx * self.LUNGE_DISTANCE
            ey = oy + diry * self.LUNGE_DISTANCE
            esx = int(ex - world_x + shake_offset_x)
            esy = int(ey - world_y + shake_offset_y)

            half_w = self.LUNGE_WIDTH // 2
            nx, ny = -diry, dirx
            p1 = (osx + nx * half_w, osy + ny * half_w)
            p2 = (osx - nx * half_w, osy - ny * half_w)
            p3 = (esx - nx * half_w, esy - ny * half_w)
            p4 = (esx + nx * half_w, esy + ny * half_w)
            poly = [p1, p2, p3, p4]

            alpha = self.TELEGRAPH_ALPHA
            minx = int(min(p[0] for p in poly))
            maxx = int(max(p[0] for p in poly))
            miny = int(min(p[1] for p in poly))
            maxy = int(max(p[1] for p in poly))
            w = max(1, maxx - minx + 4)
            h = max(1, maxy - miny + 4)
            surf = pygame.Surface((w, h), pygame.SRCALPHA)
            lp = [(p[0] - minx + 2, p[1] - miny + 2) for p in poly]
            pygame.draw.polygon(surf, (255, 40, 40, alpha), lp)
            screen.blit(surf, (minx, miny))

class Enemy16(AIBase):
    rank = 6

    MAX_HP = 500
    BASE_SPEED = NORMAL_MAX_SPEED * PLAYER_VIEW_SCALE * 0.90
    RADIUS = int(30 * PLAYER_VIEW_SCALE)

    PREFERRED_MIN = int(600 * PLAYER_VIEW_SCALE)
    PREFERRED_MAX = int(900 * PLAYER_VIEW_SCALE)
    RETREAT_RADIUS = int(300 * PLAYER_VIEW_SCALE)
    STRAFE_SWAY_PX = int(60 * PLAYER_VIEW_SCALE)

    DETECT_MAX   = int(1400 * PLAYER_VIEW_SCALE)
    TELEGRAPH_MS = 1500
    RELOAD_MS    = 2500

    ROT_SPEED_AIM = math.radians(60)
    MOVE_SLOW_AIM = 0.15

    BULLET_DAMAGE = 60
    BULLET_SPEED  = 30 * PLAYER_VIEW_SCALE
    BULLET_RANGE  = int(1400 * PLAYER_VIEW_SCALE)
    SPREAD_DEG    = 0.4

    LASER_THICKNESS = 3
    LASER_COLOR = (255, 0, 0)

    def __init__(self, world_x, world_y, images, sounds, map_width, map_height,
                 damage_player_fn=None, kill_callback=None, rank=rank):
        super().__init__(
            world_x, world_y, images, sounds, map_width, map_height,
            speed=self.BASE_SPEED,
            near_threshold=0,
            far_threshold=0,
            radius=self.RADIUS,
            push_strength=0.18,
            alert_duration=0,
            damage_player_fn=damage_player_fn,
            rank=rank
        )
        self.hp = self.MAX_HP
        self.images = images
        self.sounds = sounds
        self.kill_callback = kill_callback

        self.image_original = images.get("enemy16", images.get("enemy14", images.get("enemy13")))
        self.gun_image_original = images.get("gun22", images.get("gun1"))
        self.bullet_image = images.get("enemy_bullet", images.get("bullet1"))
        self.fire_sound = sounds.get("gun22_fire") or sounds.get("gun22") or sounds.get("gun1_fire_enemy")

        self.rect = self.image_original.get_rect(center=(0, 0))

        self.current_distance = int(42 * PLAYER_VIEW_SCALE)
        self.muzzle_extra    = int(12 * PLAYER_VIEW_SCALE)

        self.state = "SEEK"  # SEEK → AIM → RELOAD
        self.state_until = 0
        self.last_fire_time = 0
        self._last_rot_update_ms = pygame.time.get_ticks()

        self.laser_endpoint_world = None
        self._alert_channel = None

        self._reposition_goal = None

    def _muzzle_world_pos(self):
        mx = self.world_x + math.cos(self.direction_angle) * (self.current_distance + self.muzzle_extra)
        my = self.world_y + math.sin(self.direction_angle) * (self.current_distance + self.muzzle_extra)
        return mx, my

    @staticmethod
    def _angle_lerp(current, target, max_delta):
        diff = (target - current + math.pi) % (2 * math.pi) - math.pi
        if abs(diff) <= max_delta:
            return target
        return current + (max_delta if diff > 0 else -max_delta)

    @staticmethod
    def _norm(dx, dy):
        d = math.hypot(dx, dy)
        if d == 0: return (0.0, 0.0)
        return (dx/d, dy/d)

    def _compute_laser(self, player_world_pos):
        # 레이저 끝점과 '플레이어를 먼저 맞췄는지' 반환(엄폐 충돌 고려).
        start = self._muzzle_world_pos()
        angle = self.direction_angle
        step = 8 * PLAYER_VIEW_SCALE
        max_dist = self.BULLET_RANGE

        px, py = player_world_pos
        last_pt = start

        def hit_player(pt):
            return (pt[0]-px)**2 + (pt[1]-py)**2 <= (25*PLAYER_VIEW_SCALE)**2

        def collides(pt):
            if not hasattr(config, "obstacle_manager") or config.obstacle_manager is None:
                return False
            ox, oy = pt
            r_small = 2 * PLAYER_VIEW_SCALE
            for obs in (config.obstacle_manager.static_obstacles + config.obstacle_manager.combat_obstacles):
                for c in getattr(obs, "colliders", []):
                    if getattr(c, "bullet_passable", False):
                        continue
                    cx = obs.world_x + getattr(c, "center", (0,0))[0]
                    cy = obs.world_y + getattr(c, "center", (0,0))[1]
                    shape = getattr(c, "shape", None)
                    if shape == "circle":
                        if self.check_collision_circle((ox,oy), r_small, (cx,cy), c.size):
                            return True
                    elif shape == "ellipse":
                        try: rx, ry = c.size
                        except: continue
                        if self.check_ellipse_circle_collision((ox,oy), r_small, (cx,cy), rx, ry):
                            return True
                    elif shape == "rectangle":
                        try: w, h = c.size
                        except: continue
                        coll_r = ((w/2)**2 + (h/2)**2) ** 0.5
                        if self.check_collision_circle((ox,oy), r_small, (cx,cy), coll_r):
                            return True
            return False

        dist = 0.0
        while dist < max_dist:
            pt = (start[0] + math.cos(angle) * dist,
                  start[1] + math.sin(angle) * dist)
            if hit_player(pt):
                return pt, True
            if collides(pt):
                return last_pt, False
            last_pt = pt
            dist += step
        return last_pt, False

    def _choose_reposition_goal(self, px, py):
        # 플레이어 기준 좌/우로 짧게 재배치(LOS 회복 목적).
        dx, dy = px - self.world_x, py - self.world_y
        nx, ny = self._norm(dx, dy)
        sx, sy = -ny, nx
        if random.random() < 0.5:
            sx, sy = -sx, -sy
        dist = random.randint(int(140*PLAYER_VIEW_SCALE), int(240*PLAYER_VIEW_SCALE))
        gx = self.world_x + sx * dist
        gy = self.world_y + sy * dist
        gx = max(0, min(self.map_width, gx))
        gy = max(0, min(self.map_height, gy))
        self._reposition_goal = (gx, gy)

    def update_goal(self, world_x, world_y, player_rect, enemies):
        now = pygame.time.get_ticks()
        px, py = world_x + player_rect.centerx, world_y + player_rect.centery
        dx, dy = px - self.world_x, py - self.world_y
        dist   = math.hypot(dx, dy)
        target_angle = math.atan2(dy, dx)

        if self.state == "SEEK":
            self.speed = self.BASE_SPEED
            self.direction_angle = target_angle

            # 거리 유지
            if dist < self.RETREAT_RADIUS:
                nx, ny = self._norm(dx, dy)
                gx = self.world_x - nx * (self.PREFERRED_MIN - dist + 80)
                gy = self.world_y - ny * (self.PREFERRED_MIN - dist + 80)
                self.goal_pos = (max(0, min(self.map_width, gx)),
                                 max(0, min(self.map_height, gy)))
            elif dist > self.PREFERRED_MAX:
                self.goal_pos = (px, py)
            elif dist < self.PREFERRED_MIN:
                nx, ny = self._norm(dx, dy)
                self.goal_pos = (self.world_x - nx * 120, self.world_y - ny * 120)
            else:
                sway = math.sin(now * 0.004 + id(self)*0.001) * self.STRAFE_SWAY_PX
                perp = (-math.sin(target_angle), math.cos(target_angle))
                self.goal_pos = (self.world_x + perp[0]*sway, self.world_y + perp[1]*sway)

            # LOS 확보 시 조준 시작
            if dist <= self.DETECT_MAX:
                endpoint, hits_player = self._compute_laser((px, py))
                self.laser_endpoint_world = endpoint
                if hits_player:
                    self.state = "AIM"
                    self.state_until = now + self.TELEGRAPH_MS
                    self.speed = self.BASE_SPEED * self.MOVE_SLOW_AIM
                    self._update_alert(self.TELEGRAPH_MS)

        elif self.state == "AIM":
            # 회전/이동 느리게
            self.speed = self.BASE_SPEED * self.MOVE_SLOW_AIM
            dt_ms = max(1, now - getattr(self, '_last_rot_update_ms', now))
            self._last_rot_update_ms = now
            self.direction_angle = self._angle_lerp(self.direction_angle, target_angle,
                                                    self.ROT_SPEED_AIM * (dt_ms/1000.0))

            # 레이저 업데이트 + LOS 체크
            endpoint, hits_player = self._compute_laser((px, py))
            self.laser_endpoint_world = endpoint
            if not hits_player:
                # 시야 끊김 → 재배치/재장전
                self.state = "RELOAD"
                self.state_until = now + self.RELOAD_MS
                self._choose_reposition_goal(px, py)
                self._update_alert(None)
            elif now >= self.state_until:
                # 발사
                self._fire_sniper(px, py)
                self.state = "RELOAD"
                self.state_until = now + self.RELOAD_MS
                self._choose_reposition_goal(px, py)
                self._update_alert(None)

        elif self.state == "RELOAD":
            # 재장전/재배치 중
            self.speed = self.BASE_SPEED
            if self._reposition_goal is None:
                self._choose_reposition_goal(px, py)
            self.goal_pos = self._reposition_goal

            # 근접 위협 시 후퇴
            if dist < self.RETREAT_RADIUS:
                nx, ny = self._norm(dx, dy)
                self.goal_pos = (self.world_x - nx * 200, self.world_y - ny * 200)

            if now >= self.state_until:
                self._reposition_goal = None
                self.state = "SEEK"
        else:
            self.state = "SEEK"

    def _fire_sniper(self, px, py):
        # 총구 위치 및 발사 방향(미세 스프레드)
        mx, my = self._muzzle_world_pos()
        angle = self.direction_angle + math.radians(random.uniform(-self.SPREAD_DEG, self.SPREAD_DEG))
        tx = mx + math.cos(angle) * self.BULLET_RANGE
        ty = my + math.sin(angle) * self.BULLET_RANGE

        bullet = Bullet(
            mx, my, tx, ty,
            spread_angle_degrees=0,
            bullet_image=self.bullet_image,
            speed=self.BULLET_SPEED,
            max_distance=self.BULLET_RANGE,
            damage=self.BULLET_DAMAGE
        )
        bullet.owner = self
        bullet.trail_enabled = True
        config.global_enemy_bullets.append(bullet)

        # 사격음
        try:
            if self.fire_sound: self.fire_sound.play()
        except: pass

    def hit(self, damage, blood_effects, force=False):
        super().hit(damage, blood_effects, force)

    def die(self, blood_effects):
        if self._already_dropped:
            return
        super().die(blood_effects)
        try:
            self.spawn_dropped_items(5, 6)
        except: pass

    def draw(self, screen, world_x, world_y, shake_offset_x=0, shake_offset_y=0):
        if not self.alive:
            return

        sx = int(self.world_x - world_x + shake_offset_x)
        sy = int(self.world_y - world_y + shake_offset_y)

        # 레이저(조준 중)
        if self.state == "AIM" and self.laser_endpoint_world is not None:
            mx, my = self._muzzle_world_pos()
            lsx = int(mx - world_x + shake_offset_x)
            lsy = int(my - world_y + shake_offset_y)
            lex = int(self.laser_endpoint_world[0] - world_x + shake_offset_x)
            ley = int(self.laser_endpoint_world[1] - world_y + shake_offset_y)
            pygame.draw.line(screen, self.LASER_COLOR, (lsx, lsy), (lex, ley), self.LASER_THICKNESS)

        # 총기
        gun_pos_x = sx + math.cos(self.direction_angle) * self.current_distance
        gun_pos_y = sy + math.sin(self.direction_angle) * self.current_distance
        gun_rot = pygame.transform.rotate(self.gun_image_original, -math.degrees(self.direction_angle) - 90)
        gun_rect = gun_rot.get_rect(center=(gun_pos_x, gun_pos_y))
        screen.blit(gun_rot, gun_rect)

        # 본체
        scaled = pygame.transform.smoothscale(
            self.image_original,
            (int(self.image_original.get_width() * PLAYER_VIEW_SCALE),
             int(self.image_original.get_height() * PLAYER_VIEW_SCALE))
        )
        body_rot = pygame.transform.rotate(scaled, -math.degrees(self.direction_angle) + 90)
        body_rect = body_rot.get_rect(center=(sx, sy))
        self.rect = body_rect
        screen.blit(body_rot, body_rect)

class Enemy17(AIBase):
    rank = 4

    MAX_HP = 350
    BASE_SPEED = NORMAL_MAX_SPEED * PLAYER_VIEW_SCALE * 0.80
    RADIUS = int(28 * PLAYER_VIEW_SCALE)
    PUSH_STRENGTH = 0.0

    TRIGGER_RADIUS = int(160 * PLAYER_VIEW_SCALE)
    TELEGRAPH_MS = 600
    COOLDOWN_MS = 1200
    R_INNER = int(180 * PLAYER_VIEW_SCALE)
    R_THICK = int(80 * PLAYER_VIEW_SCALE)
    DAMAGE = 20
    TELEGRAPH_ALPHA = 76

    PLAYER_RADIUS_EST = int(15 * PLAYER_VIEW_SCALE)
    SAFE_GAP = int(8 * PLAYER_VIEW_SCALE)
    APPROACH_RING_MARGIN = int(20 * PLAYER_VIEW_SCALE)

    STRAFE_SWAY = int(60 * PLAYER_VIEW_SCALE)
    STRAFE_FREQ = 0.004
    NOISE_PX    = int(18 * PLAYER_VIEW_SCALE)

    def __init__(self, world_x, world_y, images, sounds, map_width, map_height,
                 damage_player_fn=None, kill_callback=None, rank=rank):
        super().__init__(
            world_x, world_y, images, sounds, map_width, map_height,
            speed=self.BASE_SPEED,
            near_threshold=0,
            far_threshold=0,
            radius=self.RADIUS,
            push_strength=self.PUSH_STRENGTH,
            alert_duration=0,
            damage_player_fn=damage_player_fn,
            rank=rank
        )
        self.hp = self.MAX_HP

        self.image_original = images["enemy17"]
        self.rect = self.image_original.get_rect(center=(0, 0))

        self.state = "CHASE"  # CHASE → TELEGRAPH → STRIKE → RECOVER → CHASE
        self.state_until = 0
        self.cooldown_until = 0

        self.snd_tele = sounds.get("spawn_enemy")
        self.snd_blast = sounds.get("explosion") or sounds.get("gun19defend")

        self._noise_seed = random.random() * 1000.0

        self.kill_callback = kill_callback

    def update(self, dt, world_x, world_y, player_rect, enemies=[]):
        # Enemy17만 장애물을 통과: 이 프레임 동안 obstacle 리스트를 비워서
        # AIBase.update의 충돌 보정 루프를 우회한다.
        if not self.alive or not config.combat_state:
            return

        om = getattr(config, "obstacle_manager", None)
        saved = None
        if om is not None:
            saved = (om.static_obstacles, om.combat_obstacles)
            om.static_obstacles = []
            om.combat_obstacles = []

        try:
            super().update(dt, world_x, world_y, player_rect, enemies)
        finally:
            if om is not None and saved is not None:
                om.static_obstacles, om.combat_obstacles = saved

    def update_goal(self, world_x, world_y, player_rect, enemies):
        now = pygame.time.get_ticks()
        px, py = world_x + player_rect.centerx, world_y + player_rect.centery
        dx, dy = px - self.world_x, py - self.world_y
        dist = math.hypot(dx, dy)

        # 시선은 플레이어로
        if dx or dy:
            self.direction_angle = math.atan2(dy, dx)

        # 절대 겹치지 않도록 필요한 최소 분리
        min_sep = self.radius + self.PLAYER_RADIUS_EST + self.SAFE_GAP

        if self.state == "CHASE":
            self.speed = self.BASE_SPEED

            # 너무 가까우면 즉시 후퇴(겹침 방지 → 플레이어 안 밀림)
            if dist < min_sep:
                nx, ny = self._norm(dx, dy)
                back = (min_sep - dist) + int(18 * PLAYER_VIEW_SCALE)
                gx = self.world_x - nx * back
                gy = self.world_y - ny * back
                self.goal_pos = (max(0, min(self.map_width, gx)),
                                 max(0, min(self.map_height, gy)))
            else:
                # '슬금슬금 접근' : 트리거보다 살짝 바깥 링을 목표로 + 좌/우 드리프트 & 노이즈
                desired = max(min_sep + int(10 * PLAYER_VIEW_SCALE),
                              self.TRIGGER_RADIUS - self.APPROACH_RING_MARGIN)
                nx, ny = self._norm(dx, dy)

                # 플레이어 주변 '접근 링'의 목표점(정면에서 바로 박지 않도록 약간 앞당김)
                gx = px - nx * desired
                gy = py - ny * desired

                # 좌우 스트레이프(시각적 슬금슬금)
                sway = math.sin(now * self.STRAFE_FREQ + self._noise_seed) * self.STRAFE_SWAY
                perp = (-ny, nx)
                gx += perp[0] * sway
                gy += perp[1] * sway

                # 소프트 노이즈
                gx += math.cos(now * 0.0023 + self._noise_seed * 2.1) * self.NOISE_PX
                gy += math.sin(now * 0.0017 + self._noise_seed * 3.7) * self.NOISE_PX

                # 맵 경계 클램프
                self.goal_pos = (max(0, min(self.map_width, gx)),
                                 max(0, min(self.map_height, gy)))

            # 텔레그래프 시작(아주 근접 + 쿨다운 완료)
            if now >= self.cooldown_until and dist <= self.TRIGGER_RADIUS:
                self.state = "TELEGRAPH"
                self.state_until = now + self.TELEGRAPH_MS
                try:
                    if self.snd_tele: self.snd_tele.play()
                except: pass
                self.goal_pos = (self.world_x, self.world_y)

        elif self.state == "TELEGRAPH":
            # 제자리에서 예고, 혹시 파고들면 살짝 밀려나기(자기 자신만)
            if dist < min_sep:
                nx, ny = self._norm(dx, dy)
                back = (min_sep - dist) + int(10 * PLAYER_VIEW_SCALE)
                self.world_x = max(0, min(self.map_width, self.world_x - nx * back))
                self.world_y = max(0, min(self.map_height, self.world_y - ny * back))
            self.goal_pos = (self.world_x, self.world_y)

            if now >= self.state_until:
                # 폭발 판정
                self._do_ring_strike(px, py)
                # 후딜
                self.state = "RECOVER"
                self.state_until = now + 300
                self.cooldown_until = now + self.COOLDOWN_MS

        elif self.state == "RECOVER":
            # 회복 중에도 최소 분리 유지
            if dist < min_sep:
                nx, ny = self._norm(dx, dy)
                back = (min_sep - dist) + int(10 * PLAYER_VIEW_SCALE)
                gx = self.world_x - nx * back
                gy = self.world_y - ny * back
                self.goal_pos = (max(0, min(self.map_width, gx)),
                                 max(0, min(self.map_height, gy)))
            else:
                self.goal_pos = (self.world_x, self.world_y)

            if now >= self.state_until:
                self.state = "CHASE"

    def _do_ring_strike(self, px, py):
        # 도넛 링 폭발 판정
        r_inner = self.R_INNER
        r_outer = self.R_INNER + self.R_THICK
        dist = math.hypot(px - self.world_x, py - self.world_y)
        if r_inner <= dist <= r_outer:
            if self.damage_player:
                self.damage_player(int(self.DAMAGE))
            else:
                try:
                    config.damage_player(int(self.DAMAGE))
                except Exception:
                    pass
        try:
            if self.snd_blast: self.snd_blast.play()
        except: pass

    @staticmethod
    def _norm(dx, dy):
        d = math.hypot(dx, dy)
        if d == 0: return (0.0, 0.0)
        return (dx/d, dy/d)

    def hit(self, damage, blood_effects, force=False):
        super().hit(damage, blood_effects, force)

    def die(self, blood_effects):
        if self._already_dropped:
            return
        super().die(blood_effects)
        try:
            self.spawn_dropped_items(3, 4)
        except:
            pass

    def draw(self, screen, world_x, world_y, shake_offset_x=0, shake_offset_y=0):
        if not self.alive:
            return

        sx = int(self.world_x - world_x + shake_offset_x)
        sy = int(self.world_y - world_y + shake_offset_y)

        # 본체
        scaled = pygame.transform.smoothscale(
            self.image_original,
            (int(self.image_original.get_width() * PLAYER_VIEW_SCALE),
             int(self.image_original.get_height() * PLAYER_VIEW_SCALE))
        )
        body = pygame.transform.rotate(scaled, -math.degrees(self.direction_angle) + 90)
        body_rect = body.get_rect(center=(sx, sy))
        self.rect = body_rect
        screen.blit(body, body_rect)

        # 텔레그래프: 도넛(속 빈 원형 띠) - 확대 버전
        if self.state == "TELEGRAPH":
            r_in = self.R_INNER
            r_out = self.R_INNER + self.R_THICK
            size = r_out * 2 + 6
            surf = pygame.Surface((size, size), pygame.SRCALPHA)
            center = (size//2, size//2)
            pygame.draw.circle(surf, (255, 60, 60, self.TELEGRAPH_ALPHA), center, r_out, width=self.R_THICK)
            pygame.draw.circle(surf, (255, 90, 90, self.TELEGRAPH_ALPHA), center, r_in, width=2)
            pygame.draw.circle(surf, (255, 90, 90, self.TELEGRAPH_ALPHA), center, r_out, width=2)
            screen.blit(surf, (sx - size//2, sy - size//2))

class Enemy18(AIBase):
    rank = 2

    MAX_HP = 180
    BASE_SPEED = NORMAL_MAX_SPEED * PLAYER_VIEW_SCALE * 0.90
    RADIUS = int(28 * PLAYER_VIEW_SCALE)

    PREFERRED_MIN = int(500 * PLAYER_VIEW_SCALE)
    PREFERRED_MAX = int(800 * PLAYER_VIEW_SCALE)
    RETREAT_RADIUS = int(300 * PLAYER_VIEW_SCALE)
    DETECT_MAX   = int(1200 * PLAYER_VIEW_SCALE)

    TELEGRAPH_MS = 500
    RELOAD_MS    = 2500
    ROT_SPEED_AIM = math.radians(60)
    MOVE_SLOW_AIM = 0.15

    BULLET_DAMAGE = 30
    BULLET_SPEED  = 14 * PLAYER_VIEW_SCALE
    BULLET_RANGE  = int(1100 * PLAYER_VIEW_SCALE)
    SPREAD_DEG    = 1.0

    LASER_THICKNESS = 2
    LASER_COLOR = (255, 0, 0)

    REPOS_SIDE_MIN = int(160 * PLAYER_VIEW_SCALE)
    REPOS_SIDE_MAX = int(260 * PLAYER_VIEW_SCALE)

    def __init__(self, world_x, world_y, images, sounds, map_width, map_height,
                 damage_player_fn=None, kill_callback=None, rank=rank):
        super().__init__(
            world_x, world_y, images, sounds, map_width, map_height,
            speed=self.BASE_SPEED,
            near_threshold=0,
            far_threshold=0,
            radius=self.RADIUS,
            push_strength=0.18,
            alert_duration=0,
            damage_player_fn=damage_player_fn,
            rank=rank
        )
        self.hp = self.MAX_HP
        self.images = images
        self.sounds = sounds
        self.kill_callback = kill_callback

        self.image_original = images["enemy18"]
        self.gun_image_original = images.get("gun21", images.get("gun1"))
        self.bullet_image = images.get("enemy_bullet", images.get("bullet1"))
        self.fire_sound = sounds.get("gun21_fire") or sounds.get("gun21") or sounds.get("gun1_fire_enemy")

        self.rect = self.image_original.get_rect(center=(0, 0))

        self.current_distance = int(40 * PLAYER_VIEW_SCALE)
        self.muzzle_extra    = int(12 * PLAYER_VIEW_SCALE)

        self.state = "SEEK"  # SEEK → AIM → RELOAD
        self.state_until = 0
        self._last_rot_update_ms = pygame.time.get_ticks()

        self.laser_endpoint_world = None

        self._reposition_goal = None
        self._shots_in_cycle = 0
        self._shots_until_move = random.randint(2, 3)

    def _muzzle_world_pos(self):
        mx = self.world_x + math.cos(self.direction_angle) * (self.current_distance + self.muzzle_extra)
        my = self.world_y + math.sin(self.direction_angle) * (self.current_distance + self.muzzle_extra)
        return mx, my

    @staticmethod
    def _angle_lerp(current, target, max_delta):
        diff = (target - current + math.pi) % (2 * math.pi) - math.pi
        if abs(diff) <= max_delta:
            return target
        return current + (max_delta if diff > 0 else -max_delta)

    @staticmethod
    def _norm(dx, dy):
        d = math.hypot(dx, dy)
        if d == 0: return (0.0, 0.0)
        return (dx/d, dy/d)

    def _compute_laser(self, player_world_pos):
        # 레이저 끝점과 '플레이어를 먼저 맞췄는지' 반환(엄폐 충돌 고려).
        start = self._muzzle_world_pos()
        angle = self.direction_angle
        step = 8 * PLAYER_VIEW_SCALE
        max_dist = self.BULLET_RANGE

        px, py = player_world_pos
        last_pt = start

        def hit_player(pt):
            # 플레이어 원형 추정 반경
            return (pt[0]-px)**2 + (pt[1]-py)**2 <= (25*PLAYER_VIEW_SCALE)**2

        def collides(pt):
            om = getattr(config, "obstacle_manager", None)
            if not om:
                return False
            ox, oy = pt
            r_small = 2 * PLAYER_VIEW_SCALE
            # 두 리스트 모두 본다
            for obs in (om.static_obstacles + om.combat_obstacles):
                for c in getattr(obs, "colliders", []):
                    if getattr(c, "bullet_passable", False):
                        continue
                    cx = obs.world_x + getattr(c, "center", (0,0))[0]
                    cy = obs.world_y + getattr(c, "center", (0,0))[1]
                    shape = getattr(c, "shape", None)
                    if shape == "circle":
                        if self.check_collision_circle((ox,oy), r_small, (cx,cy), c.size):
                            return True
                    elif shape == "ellipse":
                        try: rx, ry = c.size
                        except: continue
                        if self.check_ellipse_circle_collision((ox,oy), r_small, (cx,cy), rx, ry):
                            return True
                    elif shape == "rectangle":
                        try: w, h = c.size
                        except: continue
                        coll_r = ((w/2)**2 + (h/2)**2) ** 0.5
                        if self.check_collision_circle((ox,oy), r_small, (cx,cy), coll_r):
                            return True
            return False

        dist = 0.0
        while dist < max_dist:
            pt = (start[0] + math.cos(angle) * dist,
                  start[1] + math.sin(angle) * dist)
            if hit_player(pt):
                return pt, True
            if collides(pt):
                return last_pt, False
            last_pt = pt
            dist += step
        return last_pt, False

    def _choose_reposition_goal(self, px, py):
        # 플레이어 기준 좌/우로 짧게 재배치.
        dx, dy = px - self.world_x, py - self.world_y
        nx, ny = self._norm(dx, dy)
        sx, sy = -ny, nx
        if random.random() < 0.5:
            sx, sy = -sx, -sy
        dist = random.randint(self.REPOS_SIDE_MIN, self.REPOS_SIDE_MAX)
        gx = self.world_x + sx * dist
        gy = self.world_y + sy * dist
        self._reposition_goal = (max(0, min(self.map_width, gx)),
                                 max(0, min(self.map_height, gy)))

    def update_goal(self, world_x, world_y, player_rect, enemies):
        now = pygame.time.get_ticks()
        px, py = world_x + player_rect.centerx, world_y + player_rect.centery
        dx, dy = px - self.world_x, py - self.world_y
        dist   = math.hypot(dx, dy)
        target_angle = math.atan2(dy, dx)

        if self.state == "SEEK":
            self.speed = self.BASE_SPEED
            self.direction_angle = target_angle

            # 거리 유지/보정
            if dist > self.PREFERRED_MAX:
                self.goal_pos = (px, py)
            elif dist < self.PREFERRED_MIN:
                nx, ny = self._norm(dx, dy)
                self.goal_pos = (self.world_x - nx * 160, self.world_y - ny * 160)
            else:
                # 좌/우 미세 드리프트(정지해 보이지 않게)
                sway = math.sin(now * 0.004 + id(self)*0.001) * int(50 * PLAYER_VIEW_SCALE)
                perp = (-math.sin(target_angle), math.cos(target_angle))
                self.goal_pos = (self.world_x + perp[0]*sway, self.world_y + perp[1]*sway)

            # LOS 확보 시 조준 시작
            if dist <= self.DETECT_MAX:
                endpoint, hits_player = self._compute_laser((px, py))
                self.laser_endpoint_world = endpoint
                if hits_player:
                    self.state = "AIM"
                    self.state_until = now + self.TELEGRAPH_MS
                    self.speed = self.BASE_SPEED * self.MOVE_SLOW_AIM
                    self._update_alert(self.TELEGRAPH_MS)

        elif self.state == "AIM":
            # 회전/이동 느리게
            self.speed = self.BASE_SPEED * self.MOVE_SLOW_AIM
            dt_ms = max(1, now - getattr(self, '_last_rot_update_ms', now))
            self._last_rot_update_ms = now
            self.direction_angle = self._angle_lerp(self.direction_angle, target_angle,
                                                    self.ROT_SPEED_AIM * (dt_ms/1000.0))

            # 레이저 업데이트 + LOS 체크
            endpoint, hits_player = self._compute_laser((px, py))
            self.laser_endpoint_world = endpoint
            if not hits_player:
                # 시야 끊김 → 재장전/재배치
                self.state = "RELOAD"
                self.state_until = now + self.RELOAD_MS
                self._choose_reposition_goal(px, py)
                self._update_alert(None)
            elif now >= self.state_until:
                # 발사
                self._fire_sniper(px, py)
                self._shots_in_cycle += 1
                # 2~3발 쐈으면 강제 재배치
                force_repos = (self._shots_in_cycle >= self._shots_until_move)
                if force_repos:
                    self._shots_in_cycle = 0
                    self._shots_until_move = random.randint(2, 3)
                self.state = "RELOAD"
                self.state_until = now + self.RELOAD_MS
                self._choose_reposition_goal(px, py) if force_repos else self._choose_reposition_goal(px, py)
                self._update_alert(None)

        elif self.state == "RELOAD":
            # 재장전/재배치 중
            self.speed = self.BASE_SPEED
            if self._reposition_goal is None:
                self._choose_reposition_goal(px, py)

            # 근접 위협 시 후퇴 우선
            if dist < self.RETREAT_RADIUS:
                nx, ny = self._norm(dx, dy)
                self.goal_pos = (self.world_x - nx * 220, self.world_y - ny * 220)
            else:
                self.goal_pos = self._reposition_goal

            if now >= self.state_until:
                self._reposition_goal = None
                self.state = "SEEK"
        else:
            self.state = "SEEK"

    def _fire_sniper(self, px, py):
        # 총구 위치 및 발사 방향(미세 스프레드)
        mx, my = self._muzzle_world_pos()
        angle = self.direction_angle + math.radians(random.uniform(-self.SPREAD_DEG, self.SPREAD_DEG))
        tx = mx + math.cos(angle) * self.BULLET_RANGE
        ty = my + math.sin(angle) * self.BULLET_RANGE

        try:
            bullet = Bullet(
                mx, my, tx, ty,
                spread_angle_degrees=0,
                bullet_image=self.bullet_image,
                speed=self.BULLET_SPEED,
                max_distance=self.BULLET_RANGE,
                damage=self.BULLET_DAMAGE
            )
        except NameError:
            from entities import Bullet as _Bullet
            bullet = _Bullet(
                mx, my, tx, ty,
                spread_angle_degrees=0,
                bullet_image=self.bullet_image,
                speed=self.BULLET_SPEED,
                max_distance=self.BULLET_RANGE,
                damage=self.BULLET_DAMAGE
            )
        bullet.owner = self
        bullet.trail_enabled = True

        try:
            config.global_enemy_bullets.append(bullet)
        except Exception:
            pass

        try:
            if self.fire_sound: self.fire_sound.play()
        except: 
            pass

    def hit(self, damage, blood_effects, force=False):
        super().hit(damage, blood_effects, force)

    def die(self, blood_effects):
        if self._already_dropped:
            return
        super().die(blood_effects)
        try:
            self.spawn_dropped_items(2, 3)
        except: 
            pass

    def draw(self, screen, world_x, world_y, shake_offset_x=0, shake_offset_y=0):
        if not self.alive:
            return

        sx = int(self.world_x - world_x + shake_offset_x)
        sy = int(self.world_y - world_y + shake_offset_y)

        # 레이저(조준 중)
        if self.state == "AIM" and self.laser_endpoint_world is not None:
            mx, my = self._muzzle_world_pos()
            lsx = int(mx - world_x + shake_offset_x)
            lsy = int(my - world_y + shake_offset_y)
            lex = int(self.laser_endpoint_world[0] - world_x + shake_offset_x)
            ley = int(self.laser_endpoint_world[1] - world_y + shake_offset_y)
            pygame.draw.line(screen, self.LASER_COLOR, (lsx, lsy), (lex, ley), self.LASER_THICKNESS)

        # 총기
        gun_pos_x = sx + math.cos(self.direction_angle) * self.current_distance
        gun_pos_y = sy + math.sin(self.direction_angle) * self.current_distance
        gun_rot = pygame.transform.rotate(self.gun_image_original, -math.degrees(self.direction_angle) - 90)
        gun_rect = gun_rot.get_rect(center=(gun_pos_x, gun_pos_y))
        screen.blit(gun_rot, gun_rect)

        # 본체
        scaled = pygame.transform.smoothscale(
            self.image_original,
            (int(self.image_original.get_width() * PLAYER_VIEW_SCALE),
             int(self.image_original.get_height() * PLAYER_VIEW_SCALE))
        )
        body_rot = pygame.transform.rotate(scaled, -math.degrees(self.direction_angle) + 90)
        body_rect = body_rot.get_rect(center=(sx, sy))
        self.rect = body_rect
        screen.blit(body_rot, body_rect)

class Enemy19(AIBase):
    rank = 8

    MAX_HP = 650
    BASE_SPEED = NORMAL_MAX_SPEED * PLAYER_VIEW_SCALE * 0.90
    RADIUS = int(32 * PLAYER_VIEW_SCALE)
    PUSH_STRENGTH = 0.0

    CONE_RANGE = int(420 * PLAYER_VIEW_SCALE)
    CONE_HALF_ANGLE_DEG = 35.0

    TRIGGER_RADIUS = int(360 * PLAYER_VIEW_SCALE)
    PREHEAT_MS = 1400
    SPRAY_MS   = 1000
    COOLDOWN_MS = 2800
    BACKOFF_MS   = 350

    SPRAY_TICK_MS = 500
    SPRAY_TICK_DAMAGE = 3

    BURN_DURATION_MS = 3000
    BURN_TICK_MS = 500
    BURN_TICK_DAMAGE = 4

    TELEGRAPH_ALPHA = 76
    SPRAY_ALPHA_MIN = 120
    SPRAY_ALPHA_MAX = 185
    CONE_SEGMENTS = 14

    PLAYER_RADIUS_EST = int(15 * PLAYER_VIEW_SCALE)
    SAFE_GAP = int(10 * PLAYER_VIEW_SCALE)

    WANDER_RECALC_MIN = 1200
    WANDER_RECALC_MAX = 2400
    WANDER_STEP = int(260 * PLAYER_VIEW_SCALE)
    WANDER_PLAYER_BIAS = 0.35

    GUN_DISTANCE = int(38 * PLAYER_VIEW_SCALE)

    def __init__(self, world_x, world_y, images, sounds, map_width, map_height,
                 damage_player_fn=None, kill_callback=None, rank=rank):
        super().__init__(
            world_x, world_y, images, sounds, map_width, map_height,
            speed=self.BASE_SPEED,
            near_threshold=0,
            far_threshold=0,
            radius=self.RADIUS,
            push_strength=self.PUSH_STRENGTH,
            alert_duration=0,
            damage_player_fn=damage_player_fn,
            rank=rank,
        )
        self.hp = self.MAX_HP

        self.image_original = images["enemy19"]
        self.gun_image_original = images.get("gun17", images.get("gun1"))
        self.rect = self.image_original.get_rect(center=(0, 0))
        self.snd_start = sounds.get("flame_start")
        self.snd_loop  = sounds.get("flame_loop")
        self._loop_channel = None

        self.state = "WANDER"  # WANDER → PREHEAT → SPRAY → COOLDOWN → WANDER (+BACKOFF)
        self.state_until = 0
        self.locked_angle = 0.0
        self._next_spray_tick_ms = 0

        self._player_burn_until = 0
        self._player_burn_next  = 0
        self._enemy_burn = {}

        self._wander_goal = (self.world_x, self.world_y)
        self._wander_recalc_at = pygame.time.get_ticks()
        self._wander_seed = random.random() * 1000.0

        self.kill_callback = kill_callback

    @staticmethod
    def _norm(dx, dy):
        d = math.hypot(dx, dy)
        if d == 0: return (0.0, 0.0)
        return (dx/d, dy/d)

    @staticmethod
    def _angle_diff(a, b):
        return (a - b + math.pi) % (2*math.pi) - math.pi  # [-pi, pi]

    def _muzzle_pos(self):
        return (
            self.world_x + math.cos(self.direction_angle) * self.GUN_DISTANCE,
            self.world_y + math.sin(self.direction_angle) * self.GUN_DISTANCE,
        )

    def _line_blocked(self, x0, y0, x1, y1):
        om = getattr(config, "obstacle_manager", None)
        if not om:
            return False
        step = 8 * PLAYER_VIEW_SCALE
        dx, dy = x1 - x0, y1 - y0
        dist = max(1.0, math.hypot(dx, dy))
        vx, vy = dx / dist, dy / dist
        t = 0.0
        r_small = 3 * PLAYER_VIEW_SCALE
        obs_list = getattr(om, "static_obstacles", []) + getattr(om, "combat_obstacles", [])
        while t <= dist:
            ox = x0 + vx * t
            oy = y0 + vy * t
            for obs in obs_list:
                for c in getattr(obs, "colliders", []):
                    if getattr(c, "bullet_passable", False):  # 불/탄환 통과 허용은 스킵
                        continue
                    cx = obs.world_x + getattr(c, "center", (0,0))[0]
                    cy = obs.world_y + getattr(c, "center", (0,0))[1]
                    shape = getattr(c, "shape", None)
                    if shape == "circle":
                        if self.check_collision_circle((ox,oy), r_small, (cx,cy), c.size):
                            return True
                    elif shape == "ellipse":
                        try: rx, ry = c.size
                        except: continue
                        if self.check_ellipse_circle_collision((ox,oy), r_small, (cx,cy), rx, ry):
                            return True
                    elif shape == "rectangle":
                        try: w, h = c.size
                        except: continue
                        coll_r = ((w/2)**2 + (h/2)**2) ** 0.5
                        if self.check_collision_circle((ox,oy), r_small, (cx,cy), coll_r):
                            return True
            t += step
        return False

    def _in_cone_and_visible(self, tx, ty):
        mx, my = self._muzzle_pos()
        dx, dy = tx - mx, ty - my
        dist = math.hypot(dx, dy)
        if dist > self.CONE_RANGE:
            return False
        ang = math.atan2(dy, dx)
        dtheta = abs(self._angle_diff(ang, self.locked_angle))
        if math.degrees(dtheta) > self.CONE_HALF_ANGLE_DEG:
            return False
        if self._line_blocked(mx, my, tx, ty):
            return False
        return True

    def _apply_burn_to_player(self, now):
        if now < self._player_burn_until and now >= self._player_burn_next:
            self._player_burn_next = now + self.BURN_TICK_MS
            try:
                if self.damage_player:
                    self.damage_player(int(self.BURN_TICK_DAMAGE))
                else:
                    config.damage_player(int(self.BURN_TICK_DAMAGE))
            except Exception:
                pass

    def _apply_burn_to_enemies(self, now):
        to_delete = []
        for e, st in list(self._enemy_burn.items()):
            if (not getattr(e, "alive", True)) or now >= st["until"]:
                to_delete.append(e)
                continue
            if now >= st["next"]:
                st["next"] = now + self.BURN_TICK_MS
                try:
                    e.hit(int(self.BURN_TICK_DAMAGE), None, force=True)
                except Exception:
                    pass
        for e in to_delete:
            self._enemy_burn.pop(e, None)

    def _start_loop(self):
        if self.snd_loop and (self._loop_channel is None or not self._loop_channel.get_busy()):
            try:
                self._loop_channel = self.snd_loop.play(loops=-1)
            except Exception:
                self._loop_channel = None

    def _stop_loop(self):
        try:
            if self._loop_channel:
                self._loop_channel.stop()
        except Exception:
            pass
        self._loop_channel = None

    def _recalc_wander_goal(self, px, py):
        # 마구잡이 방황 목표 갱신(플레이어 쪽으로 아주 약한 바이어스).
        now = pygame.time.get_ticks()
        self._wander_recalc_at = now + random.randint(self.WANDER_RECALC_MIN, self.WANDER_RECALC_MAX)
        # 기본 무작위 벡터
        angle = random.uniform(0, 2*math.pi)
        rx = math.cos(angle) * self.WANDER_STEP
        ry = math.sin(angle) * self.WANDER_STEP
        # 플레이어 방향 바이어스
        dx, dy = px - self.world_x, py - self.world_y
        nx, ny = self._norm(dx, dy)
        bx, by = nx * self.WANDER_STEP * self.WANDER_PLAYER_BIAS, ny * self.WANDER_STEP * self.WANDER_PLAYER_BIAS
        gx = self.world_x + rx + bx
        gy = self.world_y + ry + by
        self._wander_goal = (max(0, min(self.map_width, gx)),
                             max(0, min(self.map_height, gy)))

    def update_goal(self, world_x, world_y, player_rect, enemies):
        now = pygame.time.get_ticks()
        px = world_x + player_rect.centerx
        py = world_y + player_rect.centery

        # 시선: WANDER/COOLDOWN/BACKOFF에서는 플레이어를 계속 바라봄
        dx, dy = px - self.world_x, py - self.world_y
        if self.state in ("WANDER", "COOLDOWN", "BACKOFF"):
            if dx or dy:
                self.direction_angle = math.atan2(dy, dx)

        # 화상 DOT 진행
        self._apply_burn_to_player(now)
        self._apply_burn_to_enemies(now)

        # 최소 분리(겹치면 BACKOFF 유도)
        dist_to_player = math.hypot(dx, dy)
        min_sep = self.radius + self.PLAYER_RADIUS_EST + self.SAFE_GAP

        if self.state == "WANDER":
            self.speed = self.BASE_SPEED

            # 너무 가까우면 BACKOFF로 전환
            if dist_to_player < min_sep:
                self.state = "BACKOFF"
                self.state_until = now + self.BACKOFF_MS
                # 목표는 뒤로
                nx, ny = self._norm(dx, dy)
                back = (min_sep - dist_to_player) + int(20 * PLAYER_VIEW_SCALE)
                self.goal_pos = (max(0, min(self.map_width, self.world_x - nx * back)),
                                 max(0, min(self.map_height, self.world_y - ny * back)))
                return

            # 방황 목표 주기적 갱신
            if now >= self._wander_recalc_at:
                self._recalc_wander_goal(px, py)
            self.goal_pos = self._wander_goal

            # 근접하면 예열(PREHEAT)로
            if dist_to_player <= self.TRIGGER_RADIUS:
                self.state = "PREHEAT"
                self.state_until = now + self.PREHEAT_MS
                self.locked_angle = self.direction_angle  # 각도 고정
                self.speed = 0.0
                self.goal_pos = (self.world_x, self.world_y)
                try:
                    if self.snd_start: self.snd_start.play()
                except: pass
                return

        elif self.state == "BACKOFF":
            # 강제 뒷걸음 (속도 약간 증가)
            self.speed = self.BASE_SPEED * 1.15
            nx, ny = self._norm(dx, dy)
            back = (min_sep - dist_to_player) + int(24 * PLAYER_VIEW_SCALE)
            self.goal_pos = (max(0, min(self.map_width, self.world_x - nx * back)),
                             max(0, min(self.map_height, self.world_y - ny * back)))

            if now >= self.state_until:
                self.state = "WANDER"

        elif self.state == "PREHEAT":
            self.speed = 0.0
            self.direction_angle = self.locked_angle
            self.goal_pos = (self.world_x, self.world_y)

            # 예열 중에도 너무 파고들면 살짝 뒤로 밀려남(자기 자신만)
            if dist_to_player < min_sep:
                nx, ny = self._norm(dx, dy)
                shift = (min_sep - dist_to_player) + int(10 * PLAYER_VIEW_SCALE)
                self.world_x = max(0, min(self.map_width, self.world_x - nx * shift))
                self.world_y = max(0, min(self.map_height, self.world_y - ny * shift))

            if now >= self.state_until:
                self.state = "SPRAY"
                self.state_until = now + self.SPRAY_MS
                self._next_spray_tick_ms = now
                self._start_loop()

        elif self.state == "SPRAY":
            self.speed = 0.0
            self.direction_angle = self.locked_angle
            self.goal_pos = (self.world_x, self.world_y)

            if now >= self._next_spray_tick_ms:
                self._next_spray_tick_ms = now + self.SPRAY_TICK_MS

                # 플레이어 피해/화상
                if self._in_cone_and_visible(px, py):
                    try:
                        if self.damage_player:
                            self.damage_player(int(self.SPRAY_TICK_DAMAGE))
                        else:
                            config.damage_player(int(self.SPRAY_TICK_DAMAGE))
                    except Exception:
                        pass
                    self._player_burn_until = max(self._player_burn_until, now + self.BURN_DURATION_MS)
                    if self._player_burn_next < now:
                        self._player_burn_next = now + self.BURN_TICK_MS

                # 아군 피해/화상
                for e in enemies:
                    if e is self or not getattr(e, "alive", True):
                        continue
                    ex, ey = e.world_x, e.world_y
                    if self._in_cone_and_visible(ex, ey):
                        try:
                            e.hit(int(self.SPRAY_TICK_DAMAGE), None, force=True)
                        except Exception:
                            pass
                        st = self._enemy_burn.get(e)
                        until = now + self.BURN_DURATION_MS
                        nextt = now + self.BURN_TICK_MS if (not st or st["next"] < now) else st["next"]
                        self._enemy_burn[e] = {"until": max(until, st["until"]) if st else until,
                                               "next": nextt}

            if now >= self.state_until:
                self._stop_loop()
                self.state = "COOLDOWN"
                self.state_until = now + self.COOLDOWN_MS

        elif self.state == "COOLDOWN":
            self.speed = self.BASE_SPEED

            # 너무 가까우면 BACKOFF로 스냅
            if dist_to_player < min_sep:
                self.state = "BACKOFF"
                self.state_until = now + self.BACKOFF_MS
                nx, ny = self._norm(dx, dy)
                back = (min_sep - dist_to_player) + int(20 * PLAYER_VIEW_SCALE)
                self.goal_pos = (max(0, min(self.map_width, self.world_x - nx * back)),
                                 max(0, min(self.map_height, self.world_y - ny * back)))
                return

            # 방황으로 회귀하기 전, 목표는 느슨히 방황 목표
            if now >= self._wander_recalc_at:
                self._recalc_wander_goal(px, py)
            self.goal_pos = self._wander_goal

            if now >= self.state_until:
                self.state = "WANDER"

    def hit(self, damage, blood_effects, force=False):
        super().hit(damage, blood_effects, force)

    def die(self, blood_effects):
        self._stop_loop()
        if self._already_dropped:
            return
        super().die(blood_effects)
        try:
            self.spawn_dropped_items(7, 8)
        except:
            pass

    def draw(self, screen, world_x, world_y, shake_offset_x=0, shake_offset_y=0):
        if not self.alive:
            return

        sx = int(self.world_x - world_x + shake_offset_x)
        sy = int(self.world_y - world_y + shake_offset_y)

        # 텔레그래프/분사 콘
        state = self.state
        if state in ("PREHEAT", "SPRAY"):
            ang = self.locked_angle
            half = math.radians(self.CONE_HALF_ANGLE_DEG)
            radius = self.CONE_RANGE

            pts = [(sx, sy)]
            start = ang - half
            end   = ang + half
            for i in range(self.CONE_SEGMENTS + 1):
                t = i / self.CONE_SEGMENTS
                a = start + (end - start) * t
                px = sx + math.cos(a) * radius
                py = sy + math.sin(a) * radius
                pts.append((px, py))

            if state == "PREHEAT":
                color = (255, 140, 40, self.TELEGRAPH_ALPHA)
            else:
                pulse = (math.sin(pygame.time.get_ticks() * 0.02) + 1) * 0.5
                alpha = int(self.SPRAY_ALPHA_MIN + (self.SPRAY_ALPHA_MAX - self.SPRAY_ALPHA_MIN) * pulse)
                color = (255, 90, 20, alpha)

            # 서피스에 그려서 합성
            minx = int(min(p[0] for p in pts)); maxx = int(max(p[0] for p in pts))
            miny = int(min(p[1] for p in pts)); maxy = int(max(p[1] for p in pts))
            w = max(1, maxx - minx + 4); h = max(1, maxy - miny + 4)
            surf = pygame.Surface((w, h), pygame.SRCALPHA)
            lp = [(p[0] - minx + 2, p[1] - miny + 2) for p in pts]
            pygame.draw.polygon(surf, color, lp)
            screen.blit(surf, (minx, miny))

        gun_pos_x = sx + math.cos(self.direction_angle) * self.GUN_DISTANCE
        gun_pos_y = sy + math.sin(self.direction_angle) * self.GUN_DISTANCE
        gun_rot = pygame.transform.rotate(self.gun_image_original, -math.degrees(self.direction_angle) - 90)
        gun_rect = gun_rot.get_rect(center=(gun_pos_x, gun_pos_y))
        screen.blit(gun_rot, gun_rect)

        # 본체
        scaled = pygame.transform.smoothscale(
            self.image_original,
            (int(self.image_original.get_width() * PLAYER_VIEW_SCALE),
             int(self.image_original.get_height() * PLAYER_VIEW_SCALE))
        )
        body = pygame.transform.rotate(scaled, -math.degrees(self.direction_angle) + 90)
        body_rect = body.get_rect(center=(sx, sy))
        self.rect = body_rect
        screen.blit(body, body_rect)

class Enemy20(AIBase):
    rank = 8

    MAX_HP = 700
    BASE_SPEED = NORMAL_MAX_SPEED * PLAYER_VIEW_SCALE * 0.75
    RADIUS = int(36 * PLAYER_VIEW_SCALE)
    PUSH_STRENGTH = 0.0

    WINDUP_MS = 700
    MARK_OFFSET = int(150 * PLAYER_VIEW_SCALE)
    MARK_RADIUS = int(176 * PLAYER_VIEW_SCALE)

    DASH_SPEED_MULT = 2.2
    DASH_REACH_EPS = int(18 * PLAYER_VIEW_SCALE)
    DASH_TIMEOUT_MS = 1200
    COOLDOWN_MS = 2200

    DAMAGE = 35
    KNOCKBACK_PX = int(260 * PLAYER_VIEW_SCALE)

    MARK_ALPHA = 76
    MARK_BORDER_ALPHA = 120

    PLAYER_RADIUS_EST = int(15 * PLAYER_VIEW_SCALE)
    SAFE_GAP = int(10 * PLAYER_VIEW_SCALE)
    BACKOFF_MS = 300

    WANDER_RECALC_MIN = 1200
    WANDER_RECALC_MAX = 2400
    WANDER_STEP = int(240 * PLAYER_VIEW_SCALE)
    WANDER_PLAYER_BIAS = 0.30

    def __init__(self, world_x, world_y, images, sounds, map_width, map_height,
                 damage_player_fn=None, kill_callback=None, rank=rank):
        super().__init__(
            world_x, world_y, images, sounds, map_width, map_height,
            speed=self.BASE_SPEED,
            near_threshold=0,
            far_threshold=0,
            radius=self.RADIUS,
            push_strength=self.PUSH_STRENGTH,
            alert_duration=0,
            damage_player_fn=damage_player_fn,
            rank=rank
        )
        self.hp = self.MAX_HP

        self._shockwave_started_at = -9999
        self.SHOCKWAVE_MS = 500

        self.image_original = images.get("enemy20", images.get("enemy19"))
        self.rect = self.image_original.get_rect(center=(0, 0))

        self.snd_mark  = sounds.get("reaver_mark")
        self.snd_dash  = sounds.get("reaver_dash")
        self.snd_slam  = sounds.get("reaver_slam")

        self.state = "WANDER"  # WANDER → TARGETING → DASH → IMPACT → COOLDOWN
        self.state_until = 0
        self.locked_angle = 0.0

        self.mark_cx = self.world_x
        self.mark_cy = self.world_y

        self._wander_goal = (self.world_x, self.world_y)
        self._wander_recalc_at = pygame.time.get_ticks()

        self._backoff_until = 0

        self._dash_started_at = 0

        self.kill_callback = kill_callback

    @staticmethod
    def _norm(dx, dy):
        d = math.hypot(dx, dy)
        if d == 0: return (0.0, 0.0)
        return (dx/d, dy/d)

    def _compute_mark_center(self):
        self.mark_cx = self.world_x + math.cos(self.locked_angle) * self.MARK_OFFSET
        self.mark_cy = self.world_y + math.sin(self.locked_angle) * self.MARK_OFFSET

    def _recalc_wander_goal(self, px, py):
        now = pygame.time.get_ticks()
        self._wander_recalc_at = now + random.randint(self.WANDER_RECALC_MIN, self.WANDER_RECALC_MAX)
        ang = random.uniform(0, 2*math.pi)
        rx, ry = math.cos(ang) * self.WANDER_STEP, math.sin(ang) * self.WANDER_STEP
        dx, dy = px - self.world_x, py - self.world_y
        nx, ny = self._norm(dx, dy)
        bx, by = nx * self.WANDER_STEP * self.WANDER_PLAYER_BIAS, ny * self.WANDER_STEP * self.WANDER_PLAYER_BIAS
        gx = self.world_x + rx + bx
        gy = self.world_y + ry + by
        self._wander_goal = (max(0, min(self.map_width, gx)),
                             max(0, min(self.map_height, gy)))

    def update_goal(self, world_x, world_y, player_rect, enemies):
        now = pygame.time.get_ticks()
        px, py = world_x + player_rect.centerx, world_y + player_rect.centery
        dx, dy = px - self.world_x, py - self.world_y
        dist_to_player = math.hypot(dx, dy)

        # 기본 시선
        if self.state in ("WANDER", "COOLDOWN"):
            if dx or dy:
                self.direction_angle = math.atan2(dy, dx)

        # 최소 분리(플레이어 밀지 않음)
        min_sep = self.radius + self.PLAYER_RADIUS_EST + self.SAFE_GAP
        if dist_to_player < min_sep and self.state in ("WANDER", "COOLDOWN", "TARGETING"):
            self._backoff_until = now + self.BACKOFF_MS
            nx, ny = self._norm(dx, dy)
            back = (min_sep - dist_to_player) + int(18 * PLAYER_VIEW_SCALE)
            self.goal_pos = (max(0, min(self.map_width, self.world_x - nx * back)),
                             max(0, min(self.map_height, self.world_y - ny * back)))
            self.speed = self.BASE_SPEED * 1.05
            return

        if self.state == "WANDER":
            self.speed = self.BASE_SPEED

            # 방황 목표 갱신
            if now >= self._wander_recalc_at:
                self._recalc_wander_goal(px, py)
            self.goal_pos = self._wander_goal

            # 표식 시전 진입(좀 더 멀리서도 시작)
            if dist_to_player <= self.MARK_OFFSET + self.MARK_RADIUS * 0.65:
                self.state = "TARGETING"
                self.state_until = now + self.WINDUP_MS
                self.locked_angle = self.direction_angle
                self._compute_mark_center()
                self.speed = 0.0
                self.goal_pos = (self.world_x, self.world_y)

        elif self.state == "TARGETING":
            # 제자리에서 표식 표시, 시선 고정
            self.speed = 0.0
            self.direction_angle = self.locked_angle
            self.goal_pos = (self.world_x, self.world_y)

            # 예열 중 겹치면 자기 자신만 살짝 물러남
            if dist_to_player < min_sep:
                nx, ny = self._norm(dx, dy)
                shift = (min_sep - dist_to_player) + int(10 * PLAYER_VIEW_SCALE)
                self.world_x = max(0, min(self.map_width, self.world_x - nx * shift))
                self.world_y = max(0, min(self.map_height, self.world_y - ny * shift))

            # 예열 종료 → 대시
            if now >= self.state_until:
                try:
                    if self.snd_dash: self.snd_dash.play()
                except: pass
                self.state = "DASH"
                self._dash_started_at = now
                self._shockwave_started_at = now
                self.speed = self.BASE_SPEED * self.DASH_SPEED_MULT
                self.goal_pos = (self.mark_cx, self.mark_cy)

        elif self.state == "DASH":
            # 표식 중심으로 빠르게 이동(지형에 막힐 수 있음)
            self.speed = self.BASE_SPEED * self.DASH_SPEED_MULT
            self.direction_angle = math.atan2(self.mark_cy - self.world_y, self.mark_cx - self.world_x)
            self.goal_pos = (self.mark_cx, self.mark_cy)

            # 도달/타임아웃 판정
            if math.hypot(self.mark_cx - self.world_x, self.mark_cy - self.world_y) <= self.DASH_REACH_EPS:
                self.state = "IMPACT"
            elif now - self._dash_started_at >= self.DASH_TIMEOUT_MS:
                # 실패: 쿨다운으로
                self.state = "COOLDOWN"
                self.state_until = now + self.COOLDOWN_MS

        elif self.state == "IMPACT":
            # 한 프레임 동안 피해 적용 후 바로 COOLDOWN
            self._do_impact(px, py, enemies)
            self.state = "COOLDOWN"
            self.state_until = now + self.COOLDOWN_MS

        elif self.state == "COOLDOWN":
            self.speed = self.BASE_SPEED
            # 느슨히 방황 계속
            if now >= self._wander_recalc_at:
                self._recalc_wander_goal(px, py)
            self.goal_pos = self._wander_goal

            if now >= self.state_until:
                self.state = "WANDER"

    def _do_impact(self, px, py, enemies):
        # 사운드/화면 연출
        try:
            if self.snd_slam: self.snd_slam.play()
        except: pass
        try:
            if hasattr(config, "add_screen_shake"):
                config.add_screen_shake(6, 320)
        except: pass

        # 플레이어 판정
        if math.hypot(px - self.mark_cx, py - self.mark_cy) <= self.MARK_RADIUS:
            # 피해
            try:
                if self.damage_player:
                    self.damage_player(int(self.DAMAGE))
                else:
                    config.damage_player(int(self.DAMAGE))
            except Exception:
                pass

            # 넉백
            if hasattr(config, "apply_knockback"):
                vx = px - self.mark_cx
                vy = py - self.mark_cy
                nx, ny = self._norm(vx, vy)
                config.apply_knockback(nx * self.KNOCKBACK_PX, ny * self.KNOCKBACK_PX)

        # 아군(다른 적) 판정(친선 피해 ON)
        for e in enemies:
            if e is self or not getattr(e, "alive", True):
                continue
            if math.hypot(e.world_x - self.mark_cx, e.world_y - self.mark_cy) <= self.MARK_RADIUS:
                try:
                    e.hit(int(self.DAMAGE), None, force=True)
                except Exception:
                    pass

        # 자기 자신 (위치 보정) — 표식 중앙에 정렬
        self.world_x = self.mark_cx
        self.world_y = self.mark_cy

        # 더미 충돌 목표 해제
        self.goal_pos = (self.world_x, self.world_y)

        if self.kill_callback:
            try:
                self.kill_callback(self)
            except:
                pass

    def draw(self, screen, world_x, world_y, shake_offset_x=0, shake_offset_y=0):
        if not self.alive:
            return

        sx = int(self.world_x - world_x + shake_offset_x)
        sy = int(self.world_y - world_y + shake_offset_y)

        # 표식 그리기(TARGETING 중에만 표시)
        if self.state == "TARGETING":
            cx = int(self.mark_cx - world_x + shake_offset_x)
            cy = int(self.mark_cy - world_y + shake_offset_y)
            r  = self.MARK_RADIUS

            size = r*2 + 6
            surf = pygame.Surface((size, size), pygame.SRCALPHA)
            center = (size//2, size//2)

            # 채움 + 테두리
            pygame.draw.circle(surf, (255, 60, 60, self.MARK_ALPHA), center, r)
            pygame.draw.circle(surf, (255, 90, 90, self.MARK_BORDER_ALPHA), center, r, width=3)
            screen.blit(surf, (cx - size//2, cy - size//2))

        # 대시 시작 시: 표식 중심에서 하얀 원형 충격파가 퍼짐
        now = pygame.time.get_ticks()
        if self.state in ("DASH", "IMPACT"):
            t = now - getattr(self, "_shockwave_started_at", -9999)
            if 0 <= t <= self.SHOCKWAVE_MS:
                cx = int(self.mark_cx - world_x + shake_offset_x)
                cy = int(self.mark_cy - world_y + shake_offset_y)
                p = t / self.SHOCKWAVE_MS
                rr = max(4, int(self.MARK_RADIUS * p))
                size_sw = rr * 2 + 8
                sw = pygame.Surface((size_sw, size_sw), pygame.SRCALPHA)
                alpha = max(0, int(220 * (1.0 - p)))
                pygame.draw.circle(sw, (255, 255, 255, alpha), (size_sw//2, size_sw//2), rr, width=4)
                screen.blit(sw, (cx - size_sw//2, cy - size_sw//2))

        # 본체
        scaled = pygame.transform.smoothscale(
            self.image_original,
            (int(self.image_original.get_width() * PLAYER_VIEW_SCALE),
             int(self.image_original.get_height() * PLAYER_VIEW_SCALE))
        )
        body = pygame.transform.rotate(scaled, -math.degrees(self.direction_angle) + 90)
        body_rect = body.get_rect(center=(sx, sy))
        self.rect = body_rect
        screen.blit(body, body_rect)

class Enemy21(AIBase):
    rank = 8

    HP = 700
    BASE_SPEED = NORMAL_MAX_SPEED * PLAYER_VIEW_SCALE * 0.90
    RADIUS = int(34 * PLAYER_VIEW_SCALE)
    PUSH_STRENGTH = 0.0

    PULSE_RADIUS = int(300 * PLAYER_VIEW_SCALE)
    DAMAGE = 25
    WINDUP_MS = 1400
    COOLDOWN_MS = 2500

    STUN_MS = 1000
    SLOW_MS = 3000
    SLOW_FACTOR = 0.50

    ORBIT_RADIUS = int(PULSE_RADIUS * 0.75)
    APPROACH_STEP = int(240 * PLAYER_VIEW_SCALE)

    W_APPROACH = 0.55
    W_STRAFE   = 0.45
    W_RADIAL   = 0.20
    W_REPULSE  = 0.20

    STRAFE_SWITCH_MIN = 500
    STRAFE_SWITCH_MAX = 900

    RETREAT_PROB_PER_SEC = 0.18
    RETREAT_DUR_MIN = 200
    RETREAT_DUR_MAX = 320
    RETREAT_CD_MIN  = 900
    RETREAT_CD_MAX  = 1400

    PLAYER_RADIUS_EST = int(15 * PLAYER_VIEW_SCALE)
    SAFE_GAP = int(10 * PLAYER_VIEW_SCALE)

    def __init__(self, world_x, world_y, images, sounds, map_width, map_height,
                 damage_player_fn=None, kill_callback=None, rank=rank):
        super().__init__(
            world_x, world_y, images, sounds, map_width, map_height,
            speed=self.BASE_SPEED, near_threshold=0, far_threshold=0,
            radius=self.RADIUS, push_strength=self.PUSH_STRENGTH, alert_duration=0,
            damage_player_fn=damage_player_fn, rank=rank
        )
        self.hp = self.HP

        self.image_original = images.get("enemy21", images.get("enemy18"))
        self.rect = self.image_original.get_rect(center=(0, 0))

        self.snd_charge = sounds.get("shock_charge")
        self.snd_burst  = sounds.get("shock_burst")

        self.state = "APPROACH"  # APPROACH → WINDUP → DISCHARGE → COOLDOWN → APPROACH
        self.state_until = 0

        now = pygame.time.get_ticks()
        self._strafe_dir = random.choice([-1, 1])
        self._strafe_until = now + random.randint(self.STRAFE_SWITCH_MIN, self.STRAFE_SWITCH_MAX)

        self._retreat_active_until   = 0
        self._retreat_cooldown_until = 0

        self._last_update_ms = now

        self._charge_start_ms = 0
        self._burst_ms = 220
        self._burst_started_ms = -9999

        self.kill_callback = kill_callback

    @staticmethod
    def _norm(dx, dy):
        d = math.hypot(dx, dy)
        return (dx/d, dy/d) if d > 0 else (0.0, 0.0)

    def update_goal(self, world_x, world_y, player_rect, enemies):
        now = pygame.time.get_ticks()
        dt = max(1, now - getattr(self, "_last_update_ms", now))
        self._last_update_ms = now

        px, py = world_x + player_rect.centerx, world_y + player_rect.centery
        dx, dy = px - self.world_x, py - self.world_y
        dist = math.hypot(dx, dy)

        # 시선은 기본적으로 플레이어를 향함
        if dx or dy:
            self.direction_angle = math.atan2(dy, dx)

        # 최소 분리(겹침 방지): 자기 자신이 살짝 뒤로
        min_sep = self.radius + self.PLAYER_RADIUS_EST + self.SAFE_GAP
        repulse_vec = (0.0, 0.0)
        if dist < min_sep:
            nx, ny = self._norm(dx, dy)
            back = (min_sep - dist) + int(18 * PLAYER_VIEW_SCALE)
            self.world_x = max(0, min(self.map_width,  self.world_x - nx * 0.25 * back))
            self.world_y = max(0, min(self.map_height, self.world_y - ny * 0.25 * back))
            repulse_vec = (-nx, -ny)  # 벡터 합성에 약하게 반영(뒤로 밀림 방지용)

        if self.state == "APPROACH":
            self.speed = self.BASE_SPEED * 1.06

            # 좌/우 전환
            if now >= self._strafe_until:
                self._strafe_dir *= -1
                self._strafe_until = now + random.randint(self.STRAFE_SWITCH_MIN, self.STRAFE_SWITCH_MAX)

            nx, ny = self._norm(dx, dy)
            tx, ty = -ny * self._strafe_dir, nx * self._strafe_dir  # 접선

            # ORBIT_RADIUS로 수렴(너무 멀면 당기고, 너무 가까우면 약하게 밀어냄)
            # (ORBIT_RADIUS가 작아져 근본적으로 더 접근하려는 성향 강화)
            radial_err = (self.ORBIT_RADIUS - dist) * 0.008  # +면 바깥으로, -면 안쪽으로
            radial_vec = (nx * radial_err, ny * radial_err)

            # 마이크로 후퇴 확률(감지 범위 근처에서만): 짧게만, 쿨다운 있음
            retreat_vec = (0.0, 0.0)
            retreat_active = now < self._retreat_active_until
            if not retreat_active and dist <= self.PULSE_RADIUS * 1.2 and now >= self._retreat_cooldown_until:
                if random.random() < self.RETREAT_PROB_PER_SEC * (dt / 1000.0):
                    self._retreat_active_until = now + random.randint(self.RETREAT_DUR_MIN, self.RETREAT_DUR_MAX)
                    self._retreat_cooldown_until = now + random.randint(self.RETREAT_CD_MIN, self.RETREAT_CD_MAX)
                    retreat_active = True
            if retreat_active:
                retreat_strength = 0.35
                retreat_vec = (-nx * retreat_strength, -ny * retreat_strength)

            # 가중치 합성(전체적으로는 접근 성향 ↑)
            approach_w = self.W_APPROACH * (0.25 if retreat_active else 1.0)  # 후퇴 중에도 접근 성향 약간 유지
            vx = (nx * approach_w) \
               + (tx * self.W_STRAFE) \
               + (radial_vec[0] * self.W_RADIAL) \
               + (retreat_vec[0]) \
               + (repulse_vec[0] * self.W_REPULSE)
            vy = (ny * approach_w) \
               + (ty * self.W_STRAFE) \
               + (radial_vec[1] * self.W_RADIAL) \
               + (retreat_vec[1]) \
               + (repulse_vec[1] * self.W_REPULSE)

            mvx, mvy = self._norm(vx, vy)
            step = self.APPROACH_STEP * 0.14  # 이전보다 살짝 적극적으로 이동
            gx = self.world_x + mvx * step
            gy = self.world_y + mvy * step
            self.goal_pos = (max(0, min(self.map_width, gx)),
                             max(0, min(self.map_height, gy)))

            # 범위 진입 -> 충전 시작
            if dist <= self.PULSE_RADIUS:
                self.state = "WINDUP"
                self.state_until = now + self.WINDUP_MS
                self._charge_start_ms = now
                self.speed = 0.0
                self.goal_pos = (self.world_x, self.world_y)
                try:
                    if self.snd_charge: self.snd_charge.play()
                except: pass

        elif self.state == "WINDUP":
            self.speed = 0.0
            self.goal_pos = (self.world_x, self.world_y)

            if now >= self.state_until:
                self.state = "DISCHARGE"
                self._burst_started_ms = now
                try:
                    if self.snd_burst: self.snd_burst.play()
                except: pass

                # 판정/디버프
                if dist <= self.PULSE_RADIUS:
                    try:
                        if self.damage_player:
                            self.damage_player(int(self.DAMAGE))
                        else:
                            config.damage_player(int(self.DAMAGE))
                    except Exception:
                        pass
                    try:
                        config.stunned_until_ms = max(getattr(config, "stunned_until_ms", 0), now + self.STUN_MS)
                        config.slow_until_ms = max(getattr(config, "slow_until_ms", 0), now + self.SLOW_MS)
                        config.move_slow_factor = self.SLOW_FACTOR   # -50%
                        config.slow_started_ms = now
                        config.slow_duration_ms = self.SLOW_MS
                    except Exception:
                        pass

        elif self.state == "DISCHARGE":
            self.state = "COOLDOWN"
            self.state_until = now + self.COOLDOWN_MS
            self.speed = self.BASE_SPEED * 0.95
            self.goal_pos = (self.world_x, self.world_y)

        elif self.state == "COOLDOWN":
            # 쿨다운 중에도 가볍게 무빙(다음 사이클 준비)
            self.speed = self.BASE_SPEED
            nx, ny = self._norm(dx, dy)
            tx, ty = -ny * self._strafe_dir, nx * self._strafe_dir
            if now >= self._strafe_until:
                self._strafe_dir *= -1
                self._strafe_until = now + random.randint(self.STRAFE_SWITCH_MIN, self.STRAFE_SWITCH_MAX)
            vx = nx * 0.12 + tx * 0.55
            vy = ny * 0.12 + ty * 0.55
            mvx, mvy = self._norm(vx, vy)
            step = self.APPROACH_STEP * 0.08
            gx = self.world_x + mvx * step
            gy = self.world_y + mvy * step
            self.goal_pos = (max(0, min(self.map_width, gx)),
                             max(0, min(self.map_height, gy)))
            if now >= self.state_until:
                self.state = "APPROACH"

    def draw(self, screen, world_x, world_y, shake_offset_x=0, shake_offset_y=0):
        if not self.alive:
            return

        sx = int(self.world_x - world_x + shake_offset_x)
        sy = int(self.world_y - world_y + shake_offset_y)

        # 충전/방출 테레그래프
        now = pygame.time.get_ticks()
        if self.state in ("WINDUP", "DISCHARGE"):
            r = self.PULSE_RADIUS
            cx = int(self.world_x - world_x + shake_offset_x)
            cy = int(self.world_y - world_y + shake_offset_y)
            size = r * 2 + 8
            surf = pygame.Surface((size, size), pygame.SRCALPHA)
            cen = (size // 2, size // 2)
            if self.state == "WINDUP":
                t = now - self._charge_start_ms
                p = min(1.0, t / max(1, self.WINDUP_MS))
                alpha = int(60 + 80 * (0.5 + 0.5 * math.sin(p * math.pi * 2)))
                pygame.draw.circle(surf, (80, 170, 255, alpha), cen, r, width=4)
                for i in range(3):
                    ang = (p * 6.28 * (i + 1) * 0.8) % (2 * math.pi)
                    rr = int(r * (0.4 + 0.5 * ((i + 1) / 3)))
                    x = cen[0] + int(math.cos(ang) * rr)
                    y = cen[1] + int(math.sin(ang) * rr)
                    pygame.draw.circle(surf, (180, 220, 255, alpha), (x, y), 6)
            else:
                t = now - self._burst_started_ms
                if 0 <= t <= self._burst_ms:
                    p = t / self._burst_ms
                    rr = int(r * (0.9 + 0.2 * p))
                    a = int(220 * (1.0 - p))
                    pygame.draw.circle(surf, (255, 255, 255, a), cen, rr, width=6)
            screen.blit(surf, (cx - size // 2, cy - size // 2))

        # 본체
        scaled = pygame.transform.smoothscale(
            self.image_original,
            (int(self.image_original.get_width() * PLAYER_VIEW_SCALE),
             int(self.image_original.get_height() * PLAYER_VIEW_SCALE))
        )
        body = pygame.transform.rotate(scaled, -math.degrees(self.direction_angle) + 90)
        body_rect = body.get_rect(center=(sx, sy))
        self.rect = body_rect
        screen.blit(body, body_rect)

    def die(self, blood_effects):
        if getattr(self, "_already_dropped", False):
            return
        super().die(blood_effects)
        try:
            self.spawn_dropped_items(8, 9)
        except Exception:
            pass

class Enemy22(AIBase):
    rank = 1

    HP = 110
    BASE_SPEED = NORMAL_MAX_SPEED * PLAYER_VIEW_SCALE * 0.70
    RADIUS = int(30 * PLAYER_VIEW_SCALE)
    PUSH_STRENGTH = 0.10

    HOLD_DIST = int(120 * PLAYER_VIEW_SCALE)
    RING_TOL  = int(40  * PLAYER_VIEW_SCALE)

    STRAFE_STEP       = int(80 * PLAYER_VIEW_SCALE)
    STRAFE_SWITCH_MIN = 600
    STRAFE_SWITCH_MAX = 1000

    WINDUP_MS   = 600
    IMPACT_MS   = 120
    COOLDOWN_MIN = 900
    COOLDOWN_MAX = 1200

    WAVE_LEN = int(220 * PLAYER_VIEW_SCALE)
    WAVE_WID = int(60  * PLAYER_VIEW_SCALE)
    WAVE_GAP = int(25  * PLAYER_VIEW_SCALE)

    DMG = 10
    KNOCKBACK = int(140 * PLAYER_VIEW_SCALE)

    def __init__(self, world_x, world_y, images, sounds, map_width, map_height,
                 damage_player_fn=None, kill_callback=None, rank=rank):
        super().__init__(
            world_x, world_y, images, sounds, map_width, map_height,
            speed=self.BASE_SPEED,
            near_threshold=0, far_threshold=0,
            radius=self.RADIUS,
            push_strength=self.PUSH_STRENGTH,
            alert_duration=self.WINDUP_MS,
            damage_player_fn=damage_player_fn,
            rank=rank,
        )
        self.image_original = images["enemy22"]
        self.kill_callback = kill_callback
        self.hp = self.HP

        self.state = "APPROACH"  # APPROACH / WINDUP / IMPACT / COOLDOWN
        self.state_until = 0
        self.locked_angle = 0.0
        self.locked_pos = None
        self.has_hit = False
        self.show_alert = False

        self._strafe_dir = random.choice([-1, 1])
        self._next_strafe_switch = pygame.time.get_ticks() + random.randint(self.STRAFE_SWITCH_MIN, self.STRAFE_SWITCH_MAX)

    @staticmethod
    def _norm(dx, dy):
        dist = math.hypot(dx, dy)
        return (dx / dist, dy / dist) if dist > 1e-6 else (0.0, 0.0)

    def _player_pos(self, world_x, world_y, player_rect):
        return (world_x + player_rect.centerx, world_y + player_rect.centery)

    def update_goal(self, world_x, world_y, player_rect, enemies):
        now = pygame.time.get_ticks()
        px, py = self._player_pos(world_x, world_y, player_rect)
        dx, dy = px - self.world_x, py - self.world_y
        dist = math.hypot(dx, dy)

        # 항상 플레이어를 바라보게 유지(시전/임팩트 중에는 각도 고정)
        if self.state not in ("WINDUP", "IMPACT"):
            if dx or dy:
                self.direction_angle = math.atan2(dy, dx)

        # 좌우 무빙 타이밍 갱신
        if self.state == "APPROACH" and now >= self._next_strafe_switch:
            self._strafe_dir *= -1
            self._next_strafe_switch = now + random.randint(self.STRAFE_SWITCH_MIN, self.STRAFE_SWITCH_MAX)

        # 상태별 처리
        if self.state == "APPROACH":
            # 링 거리 유지 + 좌우 무빙
            nx, ny = self._norm(dx, dy)
            tx, ty = -ny, nx  # 수직(좌우) 방향

            if dist > self.HOLD_DIST + self.RING_TOL:
                target = (px - nx * self.HOLD_DIST, py - ny * self.HOLD_DIST)
            elif dist < self.HOLD_DIST:
                target = (self.world_x - nx * 40, self.world_y - ny * 40)
            else:
                target = (self.world_x + tx * self.STRAFE_STEP * self._strafe_dir,
                          self.world_y + ty * self.STRAFE_STEP * self._strafe_dir)

            self.goal_pos = target
            self.speed = self.BASE_SPEED

            # 공격 개시 조건
            if dist <= (self.HOLD_DIST + 20 * PLAYER_VIEW_SCALE) and now >= self.state_until:
                self.state = "WINDUP"
                self.state_until = now + self.WINDUP_MS
                self.locked_angle = self.direction_angle
                self.locked_pos = (self.world_x, self.world_y)  # ⛓️ 위치 고정
                self.has_hit = False
                self.show_alert = True

        elif self.state == "WINDUP":
            # 위치/각도 완전 고정
            self.goal_pos = None
            self.speed = 0.0
            self.velocity_x = 0.0
            self.velocity_y = 0.0
            if now >= self.state_until:
                # 슬래시 시작
                self.state = "IMPACT"
                self.state_until = now + self.IMPACT_MS
                self.show_alert = False
                # 판정 1회
                self._do_hit(px, py)

        elif self.state == "IMPACT":
            # 짧은 연출 구간(이동 없음)
            self.goal_pos = None
            self.speed = 0.0
            self.velocity_x = 0.0
            self.velocity_y = 0.0
            if now >= self.state_until:
                self.state = "COOLDOWN"
                self.state_until = now + random.randint(self.COOLDOWN_MIN, self.COOLDOWN_MAX)

        elif self.state == "COOLDOWN":
            # 쿨다운 동안 접근만(공격 시작 제한만 걸림)
            nx, ny = self._norm(dx, dy)
            target = (px - nx * self.HOLD_DIST, py - ny * self.HOLD_DIST)
            self.goal_pos = target
            self.speed = self.BASE_SPEED
            if now >= self.state_until:
                self.state = "APPROACH"

    def _do_hit(self, px, py):
        # IMPACT 시작 시 1회 판정: 정면 직사각형 안에 플레이어가 있으면 피해 + 넉백
        if self.has_hit:
            return
        ang = self.locked_angle
        dx = px - self.world_x
        dy = py - self.world_y
        cos_a = math.cos(-ang)
        sin_a = math.sin(-ang)
        lx = dx * cos_a - dy * sin_a
        ly = dx * sin_a + dy * cos_a
        hit = (self.WAVE_GAP <= lx <= self.WAVE_GAP + self.WAVE_LEN) and (abs(ly) <= self.WAVE_WID * 0.5)
        if hit and callable(self.damage_player):
            self.damage_player(self.DMG)
            # 넉백(정면 방향으로)
            nx, ny = math.cos(ang), math.sin(ang)
            config.apply_knockback(nx * self.KNOCKBACK, ny * self.KNOCKBACK)
        self.has_hit = True

    # WINDUP/IMPACT 동안 위치를 강제로 고정(충돌 보정, 적 간 밀침 등 무시)
    def update(self, dt, world_x, world_y, player_rect, enemies=[]):
        super().update(dt, world_x, world_y, player_rect, enemies)
        if self.state in ("WINDUP", "IMPACT"):
            if self.locked_pos is None:
                self.locked_pos = (self.world_x, self.world_y)
            self.world_x, self.world_y = self.locked_pos
            self.velocity_x = 0.0
            self.velocity_y = 0.0

    def draw(self, screen, world_x, world_y, shake_offset_x=0, shake_offset_y=0):
        if not self.alive:
            return
        sx = int(self.world_x - world_x + shake_offset_x)
        sy = int(self.world_y - world_y + shake_offset_y)

        # 텔레그래프(충격파 범위)
        if self.state in ("WINDUP", "IMPACT"):
            ang = self.locked_angle
            # 빨간 반투명 직사각형
            base_surf = pygame.Surface((self.WAVE_LEN, self.WAVE_WID), pygame.SRCALPHA)
            base_surf.fill((255, 40, 40, 110))
            rotated = pygame.transform.rotate(base_surf, -math.degrees(ang))
            # 직사각형의 중심은 적으로부터 GAP + LEN/2 떨어진 지점
            cx = sx + int(math.cos(ang) * (self.WAVE_GAP + self.WAVE_LEN * 0.5))
            cy = sy + int(math.sin(ang) * (self.WAVE_GAP + self.WAVE_LEN * 0.5))
            rect = rotated.get_rect(center=(cx, cy))
            screen.blit(rotated, rect)

            # 하얀 슬래시 바(임팩트 중 짧게 스윕)
            if self.state == "IMPACT":
                now = pygame.time.get_ticks()
                t = 1.0 - max(0.0, (self.state_until - now)) / max(1.0, self.IMPACT_MS)
                bar_x = self.WAVE_GAP + int(self.WAVE_LEN * t)
                bar_len = int(12 * PLAYER_VIEW_SCALE)
                bar_wid = self.WAVE_WID + 4
                bar_surf = pygame.Surface((bar_len, bar_wid), pygame.SRCALPHA)
                bar_surf.fill((255, 255, 255, 200))
                bar_rot = pygame.transform.rotate(bar_surf, -math.degrees(ang))
                bx = sx + int(math.cos(ang) * (bar_x))
                by = sy + int(math.sin(ang) * (bar_x))
                brect = bar_rot.get_rect(center=(bx, by))
                screen.blit(bar_rot, brect)

        # 본체
        scaled = pygame.transform.smoothscale(
            self.image_original,
            (int(self.image_original.get_width() * PLAYER_VIEW_SCALE),
             int(self.image_original.get_height() * PLAYER_VIEW_SCALE))
        )
        body = pygame.transform.rotate(scaled, -math.degrees(self.direction_angle) + 90)
        body_rect = body.get_rect(center=(sx, sy))
        self.rect = body_rect
        screen.blit(body, body_rect)

        # 경고(!)표시는 WINDUP 중에만
        if self.state == "WINDUP":
            self.draw_alert(screen, sx, sy)

    def die(self, blood_effects):
        if getattr(self, "_already_dropped", False):
            return
        super().die(blood_effects)
        self.spawn_dropped_items(2, 3)

class Enemy23(AIBase):
    rank = 8

    HP = 700
    BASE_SPEED = NORMAL_MAX_SPEED * PLAYER_VIEW_SCALE * 0.85
    RADIUS = int(36 * PLAYER_VIEW_SCALE)
    PUSH_STRENGTH = 0.0

    AIM_MS = 500
    SUPPRESS_MS = 3500
    RELOAD_MS = 1500

    FIRE_INTERVAL_MS = 80
    SPREAD_TOTAL_DEG = 12.0
    BULLET_DAMAGE = 14
    BULLET_SPEED = 8.0 * PLAYER_VIEW_SCALE
    BULLET_RANGE = 1800 * PLAYER_VIEW_SCALE

    ROT_SPEED_DEG_S = 50.0
    FRONT_DR_REDUCTION = 0.20
    FRONT_DR_ANGLE_DEG = 60.0

    KEEP_MIN = int(700 * PLAYER_VIEW_SCALE)
    KEEP_MAX = int(1000 * PLAYER_VIEW_SCALE)
    REPOSITION_DISTANCE = int(400 * PLAYER_VIEW_SCALE)

    POS_CLEARANCE = int(32 * PLAYER_VIEW_SCALE)

    def __init__(self, world_x, world_y, images, sounds, map_width, map_height,
                 damage_player_fn=None, kill_callback=None, rank=rank):
        super().__init__(
            world_x, world_y, images, sounds, map_width, map_height,
            speed=self.BASE_SPEED,
            near_threshold=0, far_threshold=0,
            radius=self.RADIUS,
            push_strength=self.PUSH_STRENGTH,
            alert_duration=self.AIM_MS,
            damage_player_fn=damage_player_fn,
            rank=rank,
        )
        self.image_original = images.get("enemy23", images.get("enemy20"))
        self.gun_image_original = images.get("gun26", images.get("gun1"))
        self.bullet_image = images.get("enemy_bullet", images.get("bullet1"))
        self.fire_sound = sounds.get("gun26_fire")

        self.kill_callback = kill_callback
        self.hp = self.HP

        self.state = "SELECT_POSITION"  # SELECT_POSITION, AIMING, SUPPRESSING, RELOADING
        self.state_until = 0
        self.selected_pos = None
        self.show_alert = False

        now = pygame.time.get_ticks()
        self.next_fire_at = now

        self.aim_angle = self.direction_angle

    @staticmethod
    def _wrap_angle(a):
        while a > math.pi: a -= 2*math.pi
        while a < -math.pi: a += 2*math.pi
        return a

    def _player_pos(self, world_x, world_y, player_rect):
        return (world_x + player_rect.centerx, world_y + player_rect.centery)

    def _is_position_clear(self, x, y):
        if not (0 <= x <= self.map_width and 0 <= y <= self.map_height):
            return False
        if not hasattr(config, "obstacle_manager") or config.obstacle_manager is None:
            return True
        for obs in config.obstacle_manager.static_obstacles + config.obstacle_manager.combat_obstacles:
            for c in obs.colliders:
                if c.check_collision_circle((x, y), self.radius + self.POS_CLEARANCE, (obs.world_x, obs.world_y)):
                    return False
        return True

    def _choose_vantage(self, world_x, world_y, player_rect):
        px, py = self._player_pos(world_x, world_y, player_rect)
        for _ in range(24):
            ang = random.uniform(0, 2*math.pi)
            r = random.uniform(self.KEEP_MIN, self.KEEP_MAX)
            cx = px + math.cos(ang) * r
            cy = py + math.sin(ang) * r
            if self._is_position_clear(cx, cy):
                return (cx, cy)
        return (self.world_x, self.world_y)

    def _count_my_bullets(self):
        try:
            return sum(1 for b in config.global_enemy_bullets if getattr(b, "owner", None) is self)
        except Exception:
            return 0

    def update_goal(self, world_x, world_y, player_rect, enemies):
        now = pygame.time.get_ticks()
        px, py = self._player_pos(world_x, world_y, player_rect)
        dx, dy = px - self.world_x, py - self.world_y
        dist = math.hypot(dx, dy)

        # 너무 붙으면 즉시 재위치
        if dist < self.REPOSITION_DISTANCE and self.state not in ("SELECT_POSITION", "RELOADING"):
            self.state = "SELECT_POSITION"
            self.selected_pos = None
            self.show_alert = False

        desired_angle = math.atan2(dy, dx)
        if self.state == "SUPPRESSING":
            self.aim_angle = desired_angle  # 실제 회전은 update()에서 제한
        else:
            self.aim_angle = desired_angle
            self.direction_angle = desired_angle

        if self.state == "SELECT_POSITION":
            if self.selected_pos is None:
                self.selected_pos = self._choose_vantage(world_x, world_y, player_rect)
            self.goal_pos = self.selected_pos
            self.speed = self.BASE_SPEED
            if math.hypot(self.world_x - self.selected_pos[0], self.world_y - self.selected_pos[1]) < 40:
                self.state = "AIMING"
                self.state_until = now + self.AIM_MS
                self.show_alert = True

        elif self.state == "AIMING":
            self.goal_pos = None
            self.speed = 0.0
            if now >= self.state_until:
                self.state = "SUPPRESSING"
                self.state_until = now + self.SUPPRESS_MS
                self.show_alert = False
                self.next_fire_at = now

        elif self.state == "SUPPRESSING":
            self.goal_pos = None
            self.speed = 0.0
            if now >= self.next_fire_at and self._count_my_bullets() < 80:
                self._fire_bullet()
                self.next_fire_at = now + self.FIRE_INTERVAL_MS
            if now >= self.state_until:
                self.state = "RELOADING"
                self.state_until = now + self.RELOAD_MS

        elif self.state == "RELOADING":
            # 유지 반경 복원용 이동
            if dist > 1e-6:
                nx, ny = (dx / dist, dy / dist)
            else:
                nx, ny = (0.0, 0.0)
            if dist < self.KEEP_MIN:
                target = (self.world_x - nx * (self.KEEP_MIN - dist + 40),
                          self.world_y - ny * (self.KEEP_MIN - dist + 40))
            elif dist > self.KEEP_MAX:
                target = (self.world_x + nx * (dist - self.KEEP_MAX),
                          self.world_y + ny * (dist - self.KEEP_MAX))
            else:
                tx, ty = -ny, nx
                mul = int(120 * PLAYER_VIEW_SCALE) * random.choice([-1, 1])
                target = (self.world_x + tx * mul, self.world_y + ty * mul)
            self.goal_pos = target
            self.speed = self.BASE_SPEED
            if now >= self.state_until:
                self.state = "SELECT_POSITION"
                self.selected_pos = None

    def update(self, dt, world_x, world_y, player_rect, enemies=[]):
        # 사격 중 회전속도 제한
        if self.state == "SUPPRESSING":
            max_delta = math.radians(self.ROT_SPEED_DEG_S) * (dt / 1000.0)
            diff = self._wrap_angle(self.aim_angle - self.direction_angle)
            if abs(diff) > max_delta:
                self.direction_angle += max_delta * (1 if diff > 0 else -1)
            else:
                self.direction_angle = self.aim_angle
        super().update(dt, world_x, world_y, player_rect, enemies)

    def _fire_bullet(self):
        spawn_offset = max(int(32 * PLAYER_VIEW_SCALE), int(self.current_distance))
        bullet_world_x = self.world_x + math.cos(self.direction_angle) * spawn_offset
        bullet_world_y = self.world_y + math.sin(self.direction_angle) * spawn_offset

        target_world_x = bullet_world_x + math.cos(self.direction_angle) * 2000
        target_world_y = bullet_world_y + math.sin(self.direction_angle) * 2000

        new_bullet = Bullet(
            bullet_world_x,
            bullet_world_y,
            target_world_x,
            target_world_y,
            self.SPREAD_TOTAL_DEG,
            self.bullet_image,
            speed=self.BULLET_SPEED,
            max_distance=self.BULLET_RANGE,
            damage=self.BULLET_DAMAGE
        )
        new_bullet.trail_enabled = True
        new_bullet.owner = self
        config.global_enemy_bullets.append(new_bullet)

        # 발사마다 사운드
        if self.fire_sound:
            try:
                self.fire_sound.play()
            except Exception:
                pass

    def hit(self, damage, blood_effects, force=False):
        if not self.alive or (not config.combat_state and not force):
            return
        # 전방 경감(플레이어 현재 위치 기준 근사)
        try:
            px, py = (config.world_x + config.player_rect.centerx, config.world_y + config.player_rect.centery)
            vec_angle = math.atan2(py - self.world_y, px - self.world_x)
            diff = abs(self._wrap_angle(vec_angle - self.direction_angle))
            if diff <= math.radians(self.FRONT_DR_ANGLE_DEG):
                damage = int(math.ceil(damage * (1.0 - self.FRONT_DR_REDUCTION)))
        except Exception:
            pass
        self.hp -= damage
        if self.hp <= 0:
            self.die(blood_effects)

    def die(self, blood_effects):
        if getattr(self, "_already_dropped", False):
            return
        super().die(blood_effects)
        try:
            self.spawn_dropped_items(8, 9)
        except Exception:
            pass

    def draw(self, screen, world_x, world_y, shake_offset_x=0, shake_offset_y=0):
        if not self.alive:
            return
        sx = int(self.world_x - world_x + shake_offset_x)
        sy = int(self.world_y - world_y + shake_offset_y)
        
        # 총 (회전 -90° 보정)
        if self.gun_image_original:
            gun_pos_x = sx + math.cos(self.direction_angle) * (self.current_distance)
            gun_pos_y = sy + math.sin(self.direction_angle) * (self.current_distance)
            rotated_gun = pygame.transform.rotate(self.gun_image_original, -math.degrees(self.direction_angle) - 90)
            gun_rect = rotated_gun.get_rect(center=(gun_pos_x, gun_pos_y))
            screen.blit(rotated_gun, gun_rect)

        # 본체
        scaled = pygame.transform.smoothscale(
            self.image_original,
            (int(self.image_original.get_width() * PLAYER_VIEW_SCALE),
             int(self.image_original.get_height() * PLAYER_VIEW_SCALE))
        )
        body = pygame.transform.rotate(scaled, -math.degrees(self.direction_angle) + 90)
        body_rect = body.get_rect(center=(sx, sy))
        self.rect = body_rect
        screen.blit(body, body_rect)

        # 조준 경고 '!'
        if self.state == "AIMING":
            self.show_alert = True
            self.draw_alert(screen, sx, sy)
        else:
            self.show_alert = False

class Enemy24(AIBase):
    rank = 5

    BASE_SPEED = NORMAL_MAX_SPEED * PLAYER_VIEW_SCALE * 0.90
    RADIUS = int(30 * PLAYER_VIEW_SCALE)
    MIN_KEEP_DIST = int(100 * PLAYER_VIEW_SCALE)
    STRAFE_STEP = int(70 * PLAYER_VIEW_SCALE)
    STRAFE_SWITCH_MIN = 600
    STRAFE_SWITCH_MAX = 1000

    P1_HP = 400
    P1_WINDUP_MS = 250
    P1_IMPACT_MS = 100
    P1_BETWEEN_HITS_MS = 150
    P1_COOLDOWN_MS = 2000
    P1_DMG = 15
    P1_KNOCKBACK = int(80 * PLAYER_VIEW_SCALE)
    P1_WAVE_LEN = int(160 * PLAYER_VIEW_SCALE)
    P1_WAVE_WID = int(50  * PLAYER_VIEW_SCALE)
    P1_WAVE_GAP = int(20  * PLAYER_VIEW_SCALE)

    COCOON_HP = 150
    COCOON_MS = 8000

    P2_HP = 300
    P2_WINDUP_MS = 600
    P2_COOLDOWN_MS = 3500
    P2_DASH_SPEED = BASE_SPEED * 2.4
    P2_DMG = 20
    P2_RADIUS = int(150 * PLAYER_VIEW_SCALE)
    P2_KNOCKBACK = int(220 * PLAYER_VIEW_SCALE)
    P2_MIN_JUMP = int(300 * PLAYER_VIEW_SCALE)
    P2_MAX_JUMP = int(500 * PLAYER_VIEW_SCALE)
    P2_FRONT_DR = 0.15
    P2_FRONT_ANGLE_DEG = 60.0

    def __init__(self, world_x, world_y, images, sounds, map_width, map_height,
                 damage_player_fn=None, kill_callback=None, rank=rank):
        super().__init__(
            world_x, world_y, images, sounds, map_width, map_height,
            speed=self.BASE_SPEED, near_threshold=0, far_threshold=0,
            radius=self.RADIUS, push_strength=0.10,
            alert_duration=self.P1_WINDUP_MS, damage_player_fn=damage_player_fn, rank=rank
        )
        self.image_original = images.get("enemy24", images.get("enemy10"))
        self.image_cocoon  = images.get("enemy24_cocoon", self.image_original)
        self.rect = self.image_original.get_rect(center=(0,0))
        self.snd_stab_hit       = sounds.get("stab_hit")
        self.snd_pulse_tick     = sounds.get("pulse_tick")
        self.snd_cocoon_shatter = sounds.get("cocoon_shatter")
        self.snd_slam           = sounds.get("reaver_slam")

        self.kill_callback = kill_callback

        self.phase = "P1"  # "P1" / "COCOON" / "P2"
        self.hp = self.P1_HP
        self.state = "P1_APPROACH"
        self.state_until = 0
        self.locked_angle = self.direction_angle
        self.locked_pos = (self.world_x, self.world_y)

        self._p1_has_hit = False

        self._cocoon_started_at = -1
        self._cocoon_ends_at = -1
        self._cocoon_hp = 0
        self._next_pulse_at = 0

        self._p2_target = (self.world_x, self.world_y)

        self._strafe_dir = random.choice([-1, 1])
        self._next_strafe_switch = pygame.time.get_ticks() + random.randint(self.STRAFE_SWITCH_MIN, self.STRAFE_SWITCH_MAX)

    @staticmethod
    def _wrap(a):
        while a > math.pi: a -= 2*math.pi
        while a < -math.pi: a += 2*math.pi
        return a

    @staticmethod
    def _norm(dx, dy):
        d = math.hypot(dx, dy)
        return (dx/d, dy/d) if d > 1e-6 else (0.0, 0.0)

    def _player_pos(self, world_x, world_y, player_rect):
        return (world_x + player_rect.centerx, world_y + player_rect.centery)

    def _is_clear(self, x, y):
        if not hasattr(config, "obstacle_manager") or config.obstacle_manager is None:
            return True
        for obs in config.obstacle_manager.static_obstacles + config.obstacle_manager.combat_obstacles:
            for c in obs.colliders:
                if c.check_collision_circle((x, y), self.radius + int(10*PLAYER_VIEW_SCALE),
                                            (obs.world_x, obs.world_y)):
                    return False
        return True

    def _ring_target_with_strafe(self, px, py, desired_dist):
        dx, dy = px - self.world_x, py - self.world_y
        nx, ny = self._norm(dx, dy)
        tx, ty = -ny, nx
        base_x = px - nx * desired_dist
        base_y = py - ny * desired_dist
        # 좌우 진자 무빙
        jitter = self.STRAFE_STEP * 0.7 * self._strafe_dir
        return (base_x + tx * jitter, base_y + ty * jitter)

    def _cocoon_pulse_interval(self, now):
        # 남은 시간 [8s..0s] → 간격 [800..180] ms
        if self._cocoon_ends_at <= 0: return 600
        left = max(0, self._cocoon_ends_at - now)
        t = 1.0 - (left / float(self.COCOON_MS))
        return int(800 - (800 - 180) * t)

    def _do_p1_hit(self, px, py):
        ang = self.locked_angle
        dx = px - self.world_x
        dy = py - self.world_y
        ca = math.cos(-ang); sa = math.sin(-ang)
        lx = dx * ca - dy * sa
        ly = dx * sa + dy * ca
        hit = (self.P1_WAVE_GAP <= lx <= self.P1_WAVE_GAP + self.P1_WAVE_LEN) and (abs(ly) <= self.P1_WAVE_WID * 0.5)
        if hit and callable(self.damage_player):
            try: self.damage_player(self.P1_DMG)
            except: pass
            nx, ny = math.cos(ang), math.sin(ang)
            try: config.apply_knockback(nx * self.P1_KNOCKBACK, ny * self.P1_KNOCKBACK)
            except: pass
            try:
                if self.snd_stab_hit: self.snd_stab_hit.play()
            except: pass

    def _enter_cocoon(self):
        now = pygame.time.get_ticks()
        self.phase = "COCOON"
        self.state = "COCOON_IDLE"
        self._cocoon_started_at = now
        self._cocoon_ends_at = now + self.COCOON_MS
        self._cocoon_hp = self.COCOON_HP
        self.locked_angle = self.direction_angle
        self.locked_pos = (self.world_x, self.world_y)
        self.speed = 0.0
        self.goal_pos = None
        self.push_strength = 0.0     # 코쿤은 자리만 차지(밀치지 않음)
        self._next_pulse_at = now + self._cocoon_pulse_interval(now)

    def _rebirth_to_p2(self):
        self.phase = "P2"
        self.hp = self.P2_HP
        self.state = "P2_APPROACH"
        self.state_until = pygame.time.get_ticks() + 200  # 짧은 전환 보호
        self.speed = self.BASE_SPEED
        self.goal_pos = None
        self.push_strength = 0.10

    def update_goal(self, world_x, world_y, player_rect, enemies):
        if not self.alive:
            return
        now = pygame.time.get_ticks()
        px, py = self._player_pos(world_x, world_y, player_rect)
        dx, dy = px - self.world_x, py - self.world_y
        dist = math.hypot(dx, dy)

        # 좌우 스트레이프 토글(접근/쿨다운 상태에서만)
        if self.state in ("P1_APPROACH", "P1_COOLDOWN", "P2_APPROACH", "P2_COOLDOWN") and now >= self._next_strafe_switch:
            self._strafe_dir *= -1
            self._next_strafe_switch = now + random.randint(self.STRAFE_SWITCH_MIN, self.STRAFE_SWITCH_MAX)

        # 최소거리 보장: 너무 가까우면 목표를 뒤로 잡아 강제 이격
        if dist < self.MIN_KEEP_DIST and self.state not in ("P1_WINDUP1","P1_IMPACT1","P1_WINDUP2","P1_IMPACT2","COCOON","P2_WINDUP","P2_DASH"):
            nx, ny = self._norm(dx, dy)
            back = (self.world_x - nx * (self.MIN_KEEP_DIST - dist + 30),
                    self.world_y - ny * (self.MIN_KEEP_DIST - dist + 30))
            self.goal_pos = back
            self.speed = self.BASE_SPEED * 0.9

        if self.phase == "P1":
            if self.state.startswith("P1_"):
                if self.state in ("P1_WINDUP1", "P1_IMPACT1", "P1_WINDUP2", "P1_IMPACT2"):
                    self.direction_angle = self.locked_angle
                    self.goal_pos = (self.world_x, self.world_y)
                    self.speed = 0.0
                else:
                    if dx or dy:
                        self.direction_angle = math.atan2(dy, dx)

            if self.state == "P1_APPROACH":
                desired = self.P1_WAVE_GAP + int(self.P1_WAVE_LEN * 0.7)
                target = self._ring_target_with_strafe(px, py, desired)
                self.goal_pos = target
                self.speed = self.BASE_SPEED
                if dist <= desired + 12:
                    self.goal_pos = (self.world_x, self.world_y)
                    self.speed = 0.0
                    self.state = "P1_WINDUP1"
                    self.state_until = now + self.P1_WINDUP_MS
                    self.locked_angle = self.direction_angle
                    self._p1_has_hit = False
                    self.show_alert = True

            elif self.state == "P1_WINDUP1":
                if now >= self.state_until:
                    self.state = "P1_IMPACT1"
                    self.state_until = now + self.P1_IMPACT_MS
                    self.show_alert = False
                    self._do_p1_hit(px, py)

            elif self.state == "P1_IMPACT1":
                if now >= self.state_until:
                    self.state = "P1_GAP"
                    self.state_until = now + self.P1_BETWEEN_HITS_MS

            elif self.state == "P1_GAP":
                if now >= self.state_until:
                    self.state = "P1_WINDUP2"
                    self.state_until = now + self.P1_WINDUP_MS
                    self.locked_angle = self.direction_angle
                    self.show_alert = True

            elif self.state == "P1_WINDUP2":
                if now >= self.state_until:
                    self.state = "P1_IMPACT2"
                    self.state_until = now + self.P1_IMPACT_MS
                    self.show_alert = False
                    self._do_p1_hit(px, py)

            elif self.state == "P1_IMPACT2":
                if now >= self.state_until:
                    self.state = "P1_COOLDOWN"
                    self.state_until = now + self.P1_COOLDOWN_MS

            elif self.state == "P1_COOLDOWN":
                desired = self.P1_WAVE_GAP + int(self.P1_WAVE_LEN * 0.7)
                target = self._ring_target_with_strafe(px, py, desired)
                self.goal_pos = target
                self.speed = self.BASE_SPEED * 0.9
                if now >= self.state_until:
                    self.state = "P1_APPROACH"

        elif self.phase == "COCOON":
            self.direction_angle = self.locked_angle
            self.world_x, self.world_y = self.locked_pos
            self.goal_pos = None
            self.speed = 0.0

            if now >= self._next_pulse_at:
                try:
                    if self.snd_pulse_tick:
                        try:
                            self.snd_pulse_tick.stop()
                        except: 
                            pass
                        self.snd_pulse_tick.play(fade_ms=20)
                except:
                    pass
                self._next_pulse_at = now + self._cocoon_pulse_interval(now)

            if now >= self._cocoon_ends_at:
                self._rebirth_to_p2()

        elif self.phase == "P2":
            if dx or dy:
                self.direction_angle = math.atan2(dy, dx)

            if self.state == "P2_APPROACH":
                # 점프 가능한 링(300~500)으로 '슬금슬금'
                if dist < self.P2_MIN_JUMP or dist > self.P2_MAX_JUMP:
                    desired = max(self.P2_MIN_JUMP, min(self.P2_MAX_JUMP, dist))
                    target = self._ring_target_with_strafe(px, py, desired)
                    self.goal_pos = target
                    self.speed = self.BASE_SPEED
                else:
                    # 점프 텔레그래프 시작
                    self.state = "P2_WINDUP"
                    self.state_until = now + self.P2_WINDUP_MS
                    nx, ny = self._norm(dx, dy)
                    jump_dist = max(self.P2_MIN_JUMP, min(dist, self.P2_MAX_JUMP))
                    tx = self.world_x + nx * jump_dist
                    ty = self.world_y + ny * jump_dist
                    if 0 <= tx <= self.map_width and 0 <= ty <= self.map_height and self._is_clear(tx, ty):
                        self._p2_target = (tx, ty)
                    else:
                        self._p2_target = (self.world_x, self.world_y)
                    self.locked_angle = self.direction_angle
                    self.show_alert = True
                    self.goal_pos = None
                    self.speed = 0.0

            elif self.state == "P2_WINDUP":
                # 제자리에서 조준/텔레그래프
                self.goal_pos = None
                self.speed = 0.0
                if now >= self.state_until:
                    # 순간이동 X → 돌진 상태로 전환
                    self.state = "P2_DASH"

            elif self.state == "P2_DASH":
                # 목표 지점으로 빠르게 돌진
                tx, ty = self._p2_target
                self.goal_pos = (tx, ty)
                self.speed = self.P2_DASH_SPEED
                # 도착/근접 시 임팩트 후 쿨다운
                if math.hypot(tx - self.world_x, ty - self.world_y) <= max(12, self.RADIUS):
                    # 슬램 판정
                    if math.hypot(px - self.world_x, py - self.world_y) <= self.P2_RADIUS:
                        try: self.damage_player(self.P2_DMG)
                        except: pass
                        npx, npy = self._norm(px - self.world_x, py - self.world_y)
                        try: config.apply_knockback(npx * self.P2_KNOCKBACK, npy * self.P2_KNOCKBACK)
                        except: pass
                    try:
                        if self.snd_slam: self.snd_slam.play()
                    except: pass
                    self.show_alert = False
                    self.state = "P2_COOLDOWN"
                    self.state_until = now + self.P2_COOLDOWN_MS

            elif self.state == "P2_COOLDOWN":
                # 링 중앙 근처로 복귀 + 살짝 스트레이프(너무 오래 붙어있지 않게)
                desired = 0.5 * (self.P2_MIN_JUMP + self.P2_MAX_JUMP)
                nx, ny = self._norm(dx, dy)
                tx, ty = -ny, nx
                base_x = px - nx * desired
                base_y = py - ny * desired
                wiggle = self.STRAFE_STEP * 0.5 * self._strafe_dir
                self.goal_pos = (base_x + tx * wiggle, base_y + ty * wiggle)
                self.speed = self.BASE_SPEED * 0.9
                if now >= self.state_until:
                    self.state = "P2_APPROACH"


    def hit(self, damage, blood_effects, force=False):
        if not self.alive or (not config.combat_state and not force):
            return

        if self.phase == "COCOON":
            self._cocoon_hp -= damage
            if self._cocoon_hp <= 0:
                try:
                    if self.snd_cocoon_shatter: self.snd_cocoon_shatter.play()
                except: pass
                self._final_die(blood_effects)
            return

        if self.phase == "P2":
            # 전방 경감
            try:
                px, py = (config.world_x + config.player_rect.centerx,
                          config.world_y + config.player_rect.centery)
                vec_angle = math.atan2(py - self.world_y, px - self.world_y)
            except Exception:
                vec_angle = self.direction_angle
            diff = abs(self._wrap(vec_angle - self.direction_angle))
            if diff <= math.radians(self.P2_FRONT_ANGLE_DEG):
                damage = int(math.ceil(damage * (1.0 - self.P2_FRONT_DR)))

        self.hp -= damage
        if self.hp <= 0:
            if self.phase == "P1":
                self._enter_cocoon()
            else:
                self._final_die(blood_effects)

    def _final_die(self, blood_effects):
        if getattr(self, "_already_dropped", False):
            return
        super().die(blood_effects)
        try:
            self.spawn_dropped_items(5, 6)
        except Exception:
            pass

    def draw(self, screen, world_x, world_y, shake_offset_x=0, shake_offset_y=0):
        if not self.alive:
            return
        sx = int(self.world_x - world_x + shake_offset_x)
        sy = int(self.world_y - world_y + shake_offset_y)

        if self.phase == "P1":
            if self.state in ("P1_WINDUP1", "P1_WINDUP2", "P1_IMPACT1", "P1_IMPACT2"):
                ang = self.locked_angle
                base = pygame.Surface((self.P1_WAVE_LEN, self.P1_WAVE_WID), pygame.SRCALPHA)
                base.fill((255, 40, 40, 110))
                rotated = pygame.transform.rotate(base, -math.degrees(ang))
                cx = sx + int(math.cos(ang) * (self.P1_WAVE_GAP + self.P1_WAVE_LEN * 0.5))
                cy = sy + int(math.sin(ang) * (self.P1_WAVE_GAP + self.P1_WAVE_LEN * 0.5))
                rect = rotated.get_rect(center=(cx, cy))
                screen.blit(rotated, rect)

            body = pygame.transform.rotate(self.image_original, -math.degrees(self.direction_angle) + 90)
            body_rect = body.get_rect(center=(sx, sy))
            self.rect = body_rect
            screen.blit(body, body_rect)

            if self.state in ("P1_WINDUP1", "P1_WINDUP2"):
                self.draw_alert(screen, sx, sy)

        elif self.phase == "COCOON":
            now = pygame.time.get_ticks()
            elapsed = now - self._cocoon_started_at
            t = min(1.0, max(0.0, elapsed / float(self.COCOON_MS)))
            freq = 0.6 + (3.0 - 0.6) * t  # Hz
            amp = 0.06
            scale = 1.0 + amp * math.sin(2 * math.pi * freq * (elapsed / 1000.0))
            iw, ih = self.image_cocoon.get_width(), self.image_cocoon.get_height()
            sw = max(2, int(iw * scale))
            sh = max(2, int(ih * scale))
            puls = pygame.transform.smoothscale(self.image_cocoon, (sw, sh))
            rect = puls.get_rect(center=(sx, sy))
            screen.blit(puls, rect)

        elif self.phase == "P2":
            if self.state == "P2_WINDUP":
                cx = int(self._p2_target[0] - world_x + shake_offset_x)
                cy = int(self._p2_target[1] - world_y + shake_offset_y)
                r = self.P2_RADIUS
                size = r*2 + 6
                surf = pygame.Surface((size, size), pygame.SRCALPHA)
                center = (size//2, size//2)
                pygame.draw.circle(surf, (255, 60, 60, 110), center, r)
                pygame.draw.circle(surf, (255, 90, 90, 160), center, r, width=3)
                screen.blit(surf, (cx - size//2, cy - size//2))
                self.draw_alert(screen, sx, sy)

            body = pygame.transform.rotate(self.image_original, -math.degrees(self.direction_angle) + 90)
            body_rect = body.get_rect(center=(sx, sy))
            self.rect = body_rect
            screen.blit(body, body_rect)

class Enemy25(AIBase):
    rank = 8

    HP = 650
    BASE_SPEED = NORMAL_MAX_SPEED * PLAYER_VIEW_SCALE * 0.80
    RADIUS = int(32 * PLAYER_VIEW_SCALE)
    PUSH_STRENGTH = 0.10

    MIN_KEEP_DIST = int(90 * PLAYER_VIEW_SCALE)
    DESIRED_MELEE_DIST = int(120 * PLAYER_VIEW_SCALE)
    STRAFE_STEP = int(70 * PLAYER_VIEW_SCALE)
    STRAFE_SWITCH_MIN = 600
    STRAFE_SWITCH_MAX = 1000

    WINDUP_MS = 260
    IMPACT_MS = 90
    COOLDOWN_MS = 1800
    DMG = 25
    KNOCKBACK = int(110 * PLAYER_VIEW_SCALE)

    WAVE_LEN = int(140 * PLAYER_VIEW_SCALE)
    WAVE_WID = int(58  * PLAYER_VIEW_SCALE)
    WAVE_GAP = int(20  * PLAYER_VIEW_SCALE)

    SWELL_MS = 700
    EXP_RADIUS = int(250 * PLAYER_VIEW_SCALE)
    EXP_DMG = 40
    EXP_KNOCKBACK = int(260 * PLAYER_VIEW_SCALE)

    SPAWN_OFFSET = int(120 * PLAYER_VIEW_SCALE)

    def __init__(self, world_x, world_y, images, sounds, map_width, map_height,
                 damage_player_fn=None, kill_callback=None, rank=rank):
        super().__init__(
            world_x, world_y, images, sounds, map_width, map_height,
            speed=self.BASE_SPEED,
            near_threshold=0, far_threshold=0,
            radius=self.RADIUS,
            push_strength=self.PUSH_STRENGTH,
            alert_duration=self.WINDUP_MS,
            damage_player_fn=damage_player_fn,
            rank=rank,
        )
        self.image_original = images.get("enemy25", images.get("enemy24"))
        self.explosion_sprite = images.get("explosion1")
        self.snd_stab_hit = sounds.get("stab_hit")
        self.snd_explode  = sounds.get("burster_explode")

        self._images_dict = images
        self._sounds_dict = sounds

        self.kill_callback = kill_callback
        self.hp = self.HP

        self.state = "APPROACH"   # APPROACH / WINDUP / IMPACT / COOLDOWN / DEATH_SWELL
        self.state_until = 0
        self.locked_angle = self.direction_angle
        self.locked_pos = (self.world_x, self.world_y)
        self.show_alert = False

        self._strafe_dir = random.choice([-1, 1])
        self._next_strafe_switch = pygame.time.get_ticks() + random.randint(self.STRAFE_SWITCH_MIN, self.STRAFE_SWITCH_MAX)

        self._pending_blood_effects = None
        self._swelling_started_at = -1

    @staticmethod
    def _wrap(a):
        while a > math.pi: a -= 2*math.pi
        while a < -math.pi: a += 2*math.pi
        return a

    @staticmethod
    def _norm(dx, dy):
        d = math.hypot(dx, dy)
        return (dx/d, dy/d) if d > 1e-6 else (0.0, 0.0)

    def _player_pos(self, world_x, world_y, player_rect):
        return (world_x + player_rect.centerx, world_y + player_rect.centery)

    def _ring_target_with_strafe(self, px, py, desired_dist):
        dx, dy = px - self.world_x, py - self.world_y
        nx, ny = self._norm(dx, dy)
        tx, ty = -ny, nx
        base_x = px - nx * desired_dist
        base_y = py - ny * desired_dist
        jitter = self.STRAFE_STEP * 0.7 * self._strafe_dir
        return (base_x + tx * jitter, base_y + ty * jitter)

    def _do_melee_hit(self, px, py):
        # IMPACT 시작 시 1회 판정
        ang = self.locked_angle
        dx = px - self.world_x
        dy = py - self.world_y
        ca = math.cos(-ang); sa = math.sin(-ang)
        lx = dx * ca - dy * sa
        ly = dx * sa + dy * ca
        hit = (self.WAVE_GAP <= lx <= self.WAVE_GAP + self.WAVE_LEN) and (abs(ly) <= self.WAVE_WID * 0.5)
        if hit and callable(self.damage_player):
            try:
                self.damage_player(self.DMG)
                nx, ny = math.cos(ang), math.sin(ang)
                config.apply_knockback(nx * self.KNOCKBACK, ny * self.KNOCKBACK)
            except Exception:
                pass
            # 타격 사운드
            try:
                if self.snd_stab_hit: self.snd_stab_hit.play()
            except Exception:
                pass

    def _spawn_enemy7_pair(self):
        # 좌/우 두 마리 Enemy7 스폰(가능할 때만)
        Enemy7Class = globals().get("Enemy7", None)
        if Enemy7Class is None:
            return
        # 좌/우 오프셋(바라보는 각도에 수직)
        perp = self.direction_angle + math.pi * 0.5
        offx = math.cos(perp) * self.SPAWN_OFFSET
        offy = math.sin(perp) * self.SPAWN_OFFSET
        spawns = [(self.world_x - offx, self.world_y - offy),
                  (self.world_x + offx, self.world_y + offy)]
        for sx, sy in spawns:
            # 맵 경계 보정
            sx = min(max(0, sx), self.map_width)
            sy = min(max(0, sy), self.map_height)
            try:
                enemy = Enemy7Class(sx, sy, self._images_dict, self._sounds_dict,
                                    self.map_width, self.map_height,
                                    damage_player_fn=self.damage_player, rank=7)
                config.all_enemies.append(enemy)
            except Exception:
                # 생성 실패해도 게임 진행에는 영향 없게 무시
                pass

    def _explode_and_die(self):
        # 폭발 판정 + 스폰 + 최종 사망 처리(드랍 포함)
        # 폭발 피해/넉백(플레이어)
        try:
            px, py = (config.world_x + config.player_rect.centerx,
                      config.world_y + config.player_rect.centery)
            dist = math.hypot(px - self.world_x, py - self.world_y)
            if dist <= self.EXP_RADIUS and callable(self.damage_player):
                self.damage_player(self.EXP_DMG)
                nx, ny = self._norm(px - self.world_x, py - self.world_y)
                try:
                    config.apply_knockback(nx * self.EXP_KNOCKBACK, ny * self.EXP_KNOCKBACK)
                except Exception:
                    pass
        except Exception:
            pass

        # 폭발 사운드
        try:
            if self.snd_explode: self.snd_explode.play()
        except Exception:
            pass

        # Enemy7 두 마리 스폰
        self._spawn_enemy7_pair()

        # 최종 사망(드랍 5/5)
        if not getattr(self, "_already_dropped", False):
            super().die(self._pending_blood_effects)
            try:
                self.spawn_dropped_items(5, 5)
            except Exception:
                pass

    def update_goal(self, world_x, world_y, player_rect, enemies):
        if not self.alive:
            return
        now = pygame.time.get_ticks()
        px, py = self._player_pos(world_x, world_y, player_rect)
        dx, dy = px - self.world_x, py - self.world_y
        dist = math.hypot(dx, dy)

        # 스트레이프 토글
        if self.state in ("APPROACH", "COOLDOWN") and now >= self._next_strafe_switch:
            self._strafe_dir *= -1
            self._next_strafe_switch = now + random.randint(self.STRAFE_SWITCH_MIN, self.STRAFE_SWITCH_MAX)

        # 최소 거리 보장(밀착 방지)
        if self.state in ("APPROACH", "COOLDOWN") and dist < self.MIN_KEEP_DIST:
            nx, ny = self._norm(dx, dy)
            back = (self.world_x - nx * (self.MIN_KEEP_DIST - dist + 30),
                    self.world_y - ny * (self.MIN_KEEP_DIST - dist + 30))
            self.goal_pos = back
            self.speed = self.BASE_SPEED * 0.9

        # 공통 회전
        if self.state not in ("WINDUP", "IMPACT", "DEATH_SWELL"):
            if dx or dy:
                self.direction_angle = math.atan2(dy, dx)

        if self.state == "APPROACH":
            target = self._ring_target_with_strafe(px, py, self.DESIRED_MELEE_DIST)
            self.goal_pos = target
            self.speed = self.BASE_SPEED
            if dist <= self.DESIRED_MELEE_DIST + 12:
                self.goal_pos = (self.world_x, self.world_y)
                self.speed = 0.0
                self.state = "WINDUP"
                self.state_until = now + self.WINDUP_MS
                self.locked_angle = self.direction_angle
                self.show_alert = True

        elif self.state == "WINDUP":
            self.goal_pos = None
            self.speed = 0.0
            if now >= self.state_until:
                self.state = "IMPACT"
                self.state_until = now + self.IMPACT_MS
                self.show_alert = False
                self._do_melee_hit(px, py)

        elif self.state == "IMPACT":
            self.goal_pos = None
            self.speed = 0.0
            if now >= self.state_until:
                self.state = "COOLDOWN"
                self.state_until = now + self.COOLDOWN_MS

        elif self.state == "COOLDOWN":
            target = self._ring_target_with_strafe(px, py, self.DESIRED_MELEE_DIST)
            self.goal_pos = target
            self.speed = self.BASE_SPEED * 0.9
            if now >= self.state_until:
                self.state = "APPROACH"

        elif self.state == "DEATH_SWELL":
            # 자리/방향 고정, 팽창 이펙트 표시
            self.goal_pos = None
            self.speed = 0.0
            self.direction_angle = self.locked_angle
            self.world_x, self.world_y = self.locked_pos
            if now >= self.state_until:
                # 폭발 & 최종 사망
                self._explode_and_die()

    def update(self, dt, world_x, world_y, player_rect, enemies=[]):
        super().update(dt, world_x, world_y, player_rect, enemies)
        # DEATH_SWELL 동안에는 물리 고정
        if self.state == "DEATH_SWELL":
            self.world_x, self.world_y = self.locked_pos
            self.velocity_x = 0.0
            self.velocity_y = 0.0

    def hit(self, damage, blood_effects, force=False):
        if not self.alive or (not config.combat_state and not force):
            return
        self.hp -= damage
        if self.hp > 0:
            return

        # 사망 트리거: 팽창 상태로 전환(한 번만)
        if self.state != "DEATH_SWELL":
            self._pending_blood_effects = blood_effects
            self.state = "DEATH_SWELL"
            self.state_until = pygame.time.get_ticks() + self.SWELL_MS
            self.locked_angle = self.direction_angle
            self.locked_pos = (self.world_x, self.world_y)
            self.push_strength = 0.0   # 팽창 중 밀침 없음
            self.show_alert = False

    def draw(self, screen, world_x, world_y, shake_offset_x=0, shake_offset_y=0):
        if not self.alive:
            return

        sx = int(self.world_x - world_x + shake_offset_x)
        sy = int(self.world_y - world_y + shake_offset_y)

        # 근접 텔레그래프
        if self.state in ("WINDUP", "IMPACT"):
            ang = self.locked_angle
            base = pygame.Surface((self.WAVE_LEN, self.WAVE_WID), pygame.SRCALPHA)
            base.fill((255, 40, 40, 110))
            rotated = pygame.transform.rotate(base, -math.degrees(ang))
            cx = sx + int(math.cos(ang) * (self.WAVE_GAP + self.WAVE_LEN * 0.5))
            cy = sy + int(math.sin(ang) * (self.WAVE_GAP + self.WAVE_LEN * 0.5))
            rect = rotated.get_rect(center=(cx, cy))
            screen.blit(rotated, rect)

        # 본체 (DEATH_SWELL 중에는 팽창 스케일)
        if self.state == "DEATH_SWELL":
            now = pygame.time.get_ticks()
            t = 1.0 - max(0.0, (self.state_until - now)) / max(1.0, self.SWELL_MS)
            scale = 1.0 + 0.25 * t   # 1.0 → 1.25
            iw, ih = self.image_original.get_width(), self.image_original.get_height()
            sw = max(2, int(iw * scale))
            sh = max(2, int(ih * scale))
            body = pygame.transform.smoothscale(self.image_original, (sw, sh))
            body = pygame.transform.rotate(body, -math.degrees(self.locked_angle) + 90)
            body_rect = body.get_rect(center=(sx, sy))
            self.rect = body_rect
            screen.blit(body, body_rect)

            # 바닥 폭발 반경 텔레그래프(붉은 원)
            size = self.EXP_RADIUS * 2 + 6
            surf = pygame.Surface((size, size), pygame.SRCALPHA)
            center = (size // 2, size // 2)
            alpha = 90 + int(80 * t)
            pygame.draw.circle(surf, (255, 60, 60, alpha), center, self.EXP_RADIUS)
            pygame.draw.circle(surf, (255, 90, 90, min(180, alpha + 40)), center, self.EXP_RADIUS, width=4)
            screen.blit(surf, (sx - size // 2, sy - size // 2))
        else:
            body = pygame.transform.rotate(self.image_original, -math.degrees(self.direction_angle) + 90)
            body_rect = body.get_rect(center=(sx, sy))
            self.rect = body_rect
            screen.blit(body, body_rect)

            if self.state == "WINDUP":
                self.draw_alert(screen, sx, sy)

class Enemy26(AIBase):
    rank = 1

    HP = 150
    BASE_SPEED = NORMAL_MAX_SPEED * PLAYER_VIEW_SCALE * 0.70
    RADIUS = int(30 * PLAYER_VIEW_SCALE)
    PUSH_STRENGTH = 0.12

    MELEE_RANGE = int(60 * PLAYER_VIEW_SCALE)
    MIN_KEEP_DIST = int(56 * PLAYER_VIEW_SCALE)

    WINDUP_MS = 300
    IMPACT_MS = 100
    COOLDOWN_MS = 2000

    DMG = 15
    KNOCKBACK = int(120 * PLAYER_VIEW_SCALE)

    FRONT_DR = 0.50
    FRONT_ARC_DEG = 70.0
    BLOCK_FLASH_MS = 150

    WAVE_LEN = int(120 * PLAYER_VIEW_SCALE)
    WAVE_WID = int(50  * PLAYER_VIEW_SCALE)
    WAVE_GAP = int(16  * PLAYER_VIEW_SCALE)

    SLASH_THICK = int(12 * PLAYER_VIEW_SCALE)
    SLASH_WIDTH  = int(0.9 * WAVE_WID)

    ROT_SPEED_DEG_S = 120.0

    def __init__(self, world_x, world_y, images, sounds, map_width, map_height,
                 damage_player_fn=None, kill_callback=None, rank=rank):
        super().__init__(
            world_x, world_y, images, sounds, map_width, map_height,
            speed=self.BASE_SPEED,
            near_threshold=0, far_threshold=0,
            radius=self.RADIUS,
            push_strength=self.PUSH_STRENGTH,
            alert_duration=self.WINDUP_MS,
            damage_player_fn=damage_player_fn,
            rank=rank,
        )
        self.image_original = images.get("enemy26", images.get("enemy10"))
        self.shield_image_original = images.get("gun19", None)
        self.block_sound = sounds.get("gun19_defend", None)

        self.kill_callback = kill_callback
        self.hp = self.HP

        self.state = "APPROACH"     # APPROACH → WINDUP → IMPACT → COOLDOWN
        self.state_until = 0
        self.locked_angle = self.direction_angle
        self.show_alert = False

        self._strafe_dir = random.choice([-1, 1])
        self._next_strafe_switch = pygame.time.get_ticks() + random.randint(700, 1100)
        self._strafe_step = int(50 * PLAYER_VIEW_SCALE)

        self.block_flash_until = 0

    @staticmethod
    def _wrap(a):
        while a > math.pi: a -= 2*math.pi
        while a < -math.pi: a += 2*math.pi
        return a

    @staticmethod
    def _norm(dx, dy):
        d = math.hypot(dx, dy)
        return (dx/d, dy/d) if d > 1e-6 else (0.0, 0.0)

    def _player_pos(self, world_x, world_y, player_rect):
        return (world_x + player_rect.centerx, world_y + player_rect.centery)

    def _player_pos_world_now(self):
        # 현재 프레임의 플레이어 월드 좌표(히트 순간 재확인용).
        try:
            return (config.world_x + config.player_rect.centerx,
                    config.world_y + config.player_rect.centery)
        except Exception:
            return (self.world_x, self.world_y)

    def _is_player_in_front_arc(self, px, py):
        angle_to_player = math.atan2(py - self.world_y, px - self.world_x)
        diff = abs(self._wrap(angle_to_player - self.direction_angle))
        return diff <= math.radians(self.FRONT_ARC_DEG)

    def _do_melee_hit(self):
        # IMPACT 시작 시 1회 판정: 정면 직사각형 안이면 피해 + 넉백.
        px, py = self._player_pos_world_now()
        ang = self.locked_angle
        dx = px - self.world_x
        dy = py - self.world_y
        ca = math.cos(-ang); sa = math.sin(-ang)
        lx = dx * ca - dy * sa
        ly = dx * sa + dy * ca
        hit = (self.WAVE_GAP <= lx <= self.WAVE_GAP + self.WAVE_LEN) and (abs(ly) <= self.WAVE_WID * 0.5)
        if hit and callable(self.damage_player):
            try:
                self.damage_player(self.DMG)
            except Exception:
                pass
            # 넉백(정면 방향)
            try:
                nx, ny = math.cos(ang), math.sin(ang)
                config.apply_knockback(nx * self.KNOCKBACK, ny * self.KNOCKBACK)
            except Exception:
                pass

    def update_goal(self, world_x, world_y, player_rect, enemies):
        if not self.alive:
            return
        now = pygame.time.get_ticks()
        px, py = self._player_pos(world_x, world_y, player_rect)
        dx, dy = px - self.world_x, py - self.world_y
        dist = math.hypot(dx, dy)

        desired = math.atan2(dy, dx) if (dx or dy) else self.direction_angle

        # 회전 로직:
        # - WINDUP: 즉시 스냅 회전(바로바로 플레이어를 봄) + 히트박스 각도도 함께 업데이트
        # - IMPACT/APPROACH/COOLDOWN: 느리게 추적 회전
        if self.state == "WINDUP":
            self.direction_angle = desired
            self.locked_angle = desired  # 텔레그래프 직사각형도 함께 따라가도록
        elif self.state in ("IMPACT", "APPROACH", "COOLDOWN"):
            max_delta = math.radians(self.ROT_SPEED_DEG_S) * (getattr(config, "dt", 16) / 1000.0)
            diff = self._wrap(desired - self.direction_angle)
            if abs(diff) > max_delta:
                self.direction_angle += max_delta * (1 if diff > 0 else -1)
            else:
                self.direction_angle = desired

        # 살랑 스트레이프 토글
        if self.state in ("APPROACH", "COOLDOWN") and now >= self._next_strafe_switch:
            self._strafe_dir *= -1
            self._next_strafe_switch = now + random.randint(700, 1100)

        if self.state == "APPROACH":
            # 최소 거리 보장: 너무 가까우면 살짝 후퇴
            if dist < self.MIN_KEEP_DIST:
                nx, ny = self._norm(dx, dy)
                self.goal_pos = (self.world_x - nx * (self.MIN_KEEP_DIST - dist + 20),
                                 self.world_y - ny * (self.MIN_KEEP_DIST - dist + 20))
                self.speed = self.BASE_SPEED * 0.85
            else:
                # 목표 링으로 전진 + 약한 스트레이프
                nx, ny = self._norm(dx, dy)
                tx, ty = -ny, nx
                base_x = px - nx * self.MELEE_RANGE
                base_y = py - ny * self.MELEE_RANGE
                jitter = self._strafe_step * 0.6 * self._strafe_dir
                self.goal_pos = (base_x + tx * jitter, base_y + ty * jitter)
                self.speed = self.BASE_SPEED

            # 공격 개시 조건(사거리 내)
            if dist <= self.MELEE_RANGE + 8:
                self.state = "WINDUP"
                self.state_until = now + self.WINDUP_MS
                self.locked_angle = self.direction_angle  # 직사각형 초기화(이후 WINDUP에서 계속 갱신됨)
                self.show_alert = True
                self.goal_pos = None
                self.speed = 0.0

        elif self.state == "WINDUP":
            self.goal_pos = None
            self.speed = 0.0
            if now >= self.state_until:
                # IMPACT 진입: 시작 순간 사운드 재생 + 스냅 회전 + 1회 판정
                self.direction_angle = desired
                self.locked_angle = desired
                try:
                    if self.block_sound:
                        self.block_sound.play()   # 요청: 밀칠 때 defend 사운드 재생
                except Exception:
                    pass
                self.state = "IMPACT"
                self.state_until = now + self.IMPACT_MS
                self.show_alert = False
                self._do_melee_hit()

        elif self.state == "IMPACT":
            self.goal_pos = None
            self.speed = 0.0
            if now >= self.state_until:
                self.state = "COOLDOWN"
                self.state_until = now + self.COOLDOWN_MS

        elif self.state == "COOLDOWN":
            # 다시 링으로 복귀하며 살짝 스트레이프
            nx, ny = self._norm(dx, dy)
            tx, ty = -ny, nx
            base_x = px - nx * self.MELEE_RANGE
            base_y = py - ny * self.MELEE_RANGE
            jitter = self._strafe_step * 0.4 * self._strafe_dir
            self.goal_pos = (base_x + tx * jitter, base_y + ty * jitter)
            self.speed = self.BASE_SPEED * 0.9
            if now >= self.state_until:
                self.state = "APPROACH"

    def hit(self, damage, blood_effects, force=False):
        if not self.alive or (not config.combat_state and not force):
            return

        # force 피해는 가드 무시
        final_damage = damage
        if not force:
            # 플레이어가 정면 원호 내에 있으면 50% 경감 + 플래시 + 사운드
            px = config.world_x + config.player_rect.centerx
            py = config.world_y + config.player_rect.centery
            if self._is_player_in_front_arc(px, py):
                final_damage = max(1, int(math.ceil(damage * (1.0 - self.FRONT_DR))))
                now = pygame.time.get_ticks()
                self.block_flash_until = now + self.BLOCK_FLASH_MS
                try:
                    if self.block_sound:
                        self.block_sound.play()
                except Exception:
                    pass

        self.hp -= max(1, int(final_damage))
        if self.hp <= 0:
            self.die(blood_effects)

    def die(self, blood_effects):
        if getattr(self, "_already_dropped", False):
            return
        super().die(blood_effects)
        try:
            self.spawn_dropped_items(3, 3)
        except Exception:
            pass

    def draw(self, screen, world_x, world_y, shake_offset_x=0, shake_offset_y=0):
        if not self.alive:
            return
        sx = int(self.world_x - world_x + shake_offset_x)
        sy = int(self.world_y - world_y + shake_offset_y)

        # 텔레그래프(붉은 직사각형) — WINDUP 동안에 표시(각도는 WINDUP에서 실시간 갱신됨)
        if self.state == "WINDUP":
            ang = self.locked_angle
            base = pygame.Surface((self.WAVE_LEN, self.WAVE_WID), pygame.SRCALPHA)
            base.fill((255, 40, 40, 110))
            rotated = pygame.transform.rotate(base, -math.degrees(ang))
            cx = sx + int(math.cos(ang) * (self.WAVE_GAP + self.WAVE_LEN * 0.5))
            cy = sy + int(math.sin(ang) * (self.WAVE_GAP + self.WAVE_LEN * 0.5))
            rect = rotated.get_rect(center=(cx, cy))
            screen.blit(rotated, rect)
            # 경고 아이콘
            self.draw_alert(screen, sx, sy)

        # 본체
        body = pygame.transform.smoothscale(
            self.image_original,
            (int(self.image_original.get_width() * PLAYER_VIEW_SCALE),
             int(self.image_original.get_height() * PLAYER_VIEW_SCALE))
        )
        body = pygame.transform.rotate(body, -math.degrees(self.direction_angle) + 90)
        body_rect = body.get_rect(center=(sx, sy))
        self.rect = body_rect
        screen.blit(body, body_rect)

        # 방패(전방 표시) — 막은 직후 약간 더 진하게
        if self.shield_image_original is not None:
            offset = (self.radius + int(10 * PLAYER_VIEW_SCALE))
            shield_cx = sx + math.cos(self.direction_angle) * offset
            shield_cy = sy + math.sin(self.direction_angle) * offset
            rotated_shield = pygame.transform.rotate(
                self.shield_image_original, -math.degrees(self.direction_angle) - 90
            )
            alpha = 110
            if pygame.time.get_ticks() < self.block_flash_until:
                alpha = 220
            temp = rotated_shield.copy()
            temp.set_alpha(alpha)
            shield_rect = temp.get_rect(center=(shield_cx, shield_cy))
            screen.blit(temp, shield_rect)

        # 임팩트 순간 '하얀 슬래시 바' 연출
        if self.state == "IMPACT":
            now = pygame.time.get_ticks()
            total = max(1, self.IMPACT_MS)
            t = 1.0 - max(0.0, (self.state_until - now) / total)  # 0→1
            ang = self.locked_angle  # 임팩트 시작 각도 기준
            cx = sx + int(math.cos(ang) * (self.WAVE_GAP + int(self.WAVE_LEN * t)))
            cy = sy + int(math.sin(ang) * (self.WAVE_GAP + int(self.WAVE_LEN * t)))
            bar = pygame.Surface((self.SLASH_WIDTH, self.SLASH_THICK), pygame.SRCALPHA)
            bar.fill((255, 255, 255, int(220 * (1.0 - t))))  # 끝으로 갈수록 옅어짐
            rotated_bar = pygame.transform.rotate(bar, -math.degrees(ang) + 90)  # 수직 방향
            bar_rect = rotated_bar.get_rect(center=(cx, cy))
            screen.blit(rotated_bar, bar_rect)

class Enemy27(AIBase):
    rank = 3

    HP = 250
    BASE_SPEED = NORMAL_MAX_SPEED * PLAYER_VIEW_SCALE * 0.85
    RADIUS = int(30 * PLAYER_VIEW_SCALE)
    PUSH_STRENGTH = 0.10

    MELEE_RANGE = int(60 * PLAYER_VIEW_SCALE)
    MIN_KEEP_DIST = int(54 * PLAYER_VIEW_SCALE)

    WINDUP_MS = 280
    IMPACT_MS = 100
    COOLDOWN_MS = 1500

    BASE_DMG = 15
    DMG_PER_STACK = 2

    STRAFE_STEP = int(60 * PLAYER_VIEW_SCALE)
    STRAFE_SWITCH_MIN = 550
    STRAFE_SWITCH_MAX = 950

    WAVE_LEN = int(120 * PLAYER_VIEW_SCALE)
    WAVE_WID = int(50  * PLAYER_VIEW_SCALE)
    WAVE_GAP = int(16  * PLAYER_VIEW_SCALE)

    SLASH_THICK = int(12 * PLAYER_VIEW_SCALE)
    SLASH_WIDTH = int(0.9 * WAVE_WID)

    MAX_STACKS = 10
    SPEED_PER_STACK = 0.02

    def __init__(self, world_x, world_y, images, sounds, map_width, map_height,
                 damage_player_fn=None, kill_callback=None, rank=rank):
        super().__init__(
            world_x, world_y, images, sounds, map_width, map_height,
            speed=self.BASE_SPEED,
            near_threshold=0, far_threshold=0,
            radius=self.RADIUS,
            push_strength=self.PUSH_STRENGTH,
            alert_duration=self.WINDUP_MS,
            damage_player_fn=damage_player_fn,
            rank=rank,
        )
        self.image_original = images.get("enemy27", images.get("enemy10"))
        self.snd_hit   = sounds.get("stab_hit")

        self.kill_callback = kill_callback
        self.hp = self.HP

        self.state = "APPROACH"  # APPROACH / WINDUP / IMPACT / COOLDOWN
        self.state_until = 0
        self.locked_angle = self.direction_angle
        self.show_alert = False

        self._strafe_dir = random.choice([-1, 1])
        self._next_strafe_switch = pygame.time.get_ticks() + random.randint(self.STRAFE_SWITCH_MIN, self.STRAFE_SWITCH_MAX)

        self.stacks = 0

    @staticmethod
    def _wrap(a):
        while a > math.pi: a -= 2*math.pi
        while a < -math.pi: a += 2*math.pi
        return a

    @staticmethod
    def _norm(dx, dy):
        d = math.hypot(dx, dy)
        return (dx/d, dy/d) if d > 1e-6 else (0.0, 0.0)

    def _player_pos(self, world_x, world_y, player_rect):
        return (world_x + player_rect.centerx, world_y + player_rect.centery)

    def _player_pos_world_now(self):
        try:
            return (config.world_x + config.player_rect.centerx,
                    config.world_y + config.player_rect.centery)
        except Exception:
            return (self.world_x, self.world_y)

    def _effective_speed(self):
        return self.BASE_SPEED * (1.0 + self.SPEED_PER_STACK * self.stacks)

    def _effective_damage(self):
        return self.BASE_DMG + self.DMG_PER_STACK * self.stacks

    def _ring_target_with_strafe(self, px, py, desired_dist):
        dx, dy = px - self.world_x, py - self.world_y
        nx, ny = self._norm(dx, dy)
        tx, ty = -ny, nx
        base_x = px - nx * desired_dist
        base_y = py - ny * desired_dist
        jitter = self.STRAFE_STEP * 0.6 * self._strafe_dir
        return (base_x + tx * jitter, base_y + ty * jitter)

    def _do_melee_hit(self):
        # IMPACT 시작 시 1회 판정: 정면 직사각형 안이면 피해 + 약한 넉백.
        px, py = self._player_pos_world_now()
        ang = self.locked_angle
        dx = px - self.world_x
        dy = py - self.world_y
        ca = math.cos(-ang); sa = math.sin(-ang)
        lx = dx * ca - dy * sa
        ly = dx * sa + dy * ca
        hit = (self.WAVE_GAP <= lx <= self.WAVE_GAP + self.WAVE_LEN) and (abs(ly) <= self.WAVE_WID * 0.5)
        if hit and callable(self.damage_player):
            try:
                self.damage_player(self._effective_damage())
            except Exception:
                pass
            # 넉백(정면 방향, 살짝)
            try:
                nx, ny = math.cos(ang), math.sin(ang)
                config.apply_knockback(nx * int(100 * PLAYER_VIEW_SCALE), ny * int(100 * PLAYER_VIEW_SCALE))
            except Exception:
                pass
            # 타격 사운드
            try:
                if self.snd_hit: self.snd_hit.play()
            except Exception:
                pass

    def update_goal(self, world_x, world_y, player_rect, enemies):
        if not self.alive:
            return
        now = pygame.time.get_ticks()
        px, py = self._player_pos(world_x, world_y, player_rect)
        dx, dy = px - self.world_x, py - self.world_y
        dist = math.hypot(dx, dy)

        if dx or dy:
            desired = math.atan2(dy, dx)
            self.direction_angle = desired
            if self.state == "WINDUP":
                # WINDUP 중에는 히트박스 각도도 매 프레임 같이 갱신
                self.locked_angle = desired

        # 스트레이프 토글
        if self.state in ("APPROACH", "COOLDOWN") and now >= self._next_strafe_switch:
            self._strafe_dir *= -1
            self._next_strafe_switch = now + random.randint(self.STRAFE_SWITCH_MIN, self.STRAFE_SWITCH_MAX)

        if self.state == "APPROACH":
            # 최소 거리 보장: 너무 가까우면 약간 후퇴
            if dist < self.MIN_KEEP_DIST:
                nx, ny = self._norm(dx, dy)
                self.goal_pos = (self.world_x - nx * (self.MIN_KEEP_DIST - dist + 20),
                                 self.world_y - ny * (self.MIN_KEEP_DIST - dist + 20))
                self.speed = self._effective_speed() * 0.9
            else:
                target = self._ring_target_with_strafe(px, py, self.MELEE_RANGE)
                self.goal_pos = target
                self.speed = self._effective_speed()

            if dist <= self.MELEE_RANGE + 8:
                self.state = "WINDUP"
                self.state_until = now + self.WINDUP_MS
                self.locked_angle = self.direction_angle
                self.show_alert = True
                self.goal_pos = None
                self.speed = 0.0

        elif self.state == "WINDUP":
            # 준비 중 위치 고정, 각도는 위에서 즉시 스냅 & locked_angle 동기화됨
            self.goal_pos = None
            self.speed = 0.0
            if now >= self.state_until:
                # IMPACT 진입: locked_angle을 현재 각도로 고정하고 1회 판정
                self.locked_angle = self.direction_angle
                self.state = "IMPACT"
                self.state_until = now + self.IMPACT_MS
                self.show_alert = False
                self._do_melee_hit()

        elif self.state == "IMPACT":
            self.goal_pos = None
            self.speed = 0.0
            if now >= self.state_until:
                self.state = "COOLDOWN"
                self.state_until = now + self.COOLDOWN_MS

        elif self.state == "COOLDOWN":
            target = self._ring_target_with_strafe(px, py, self.MELEE_RANGE)
            self.goal_pos = target
            self.speed = self._effective_speed() * 0.95
            if now >= self.state_until:
                self.state = "APPROACH"

    def hit(self, damage, blood_effects, force=False):
        if not self.alive or (not config.combat_state and not force):
            return
        self.hp -= max(1, int(damage))
        if self.hp > 0:
            # 스택 증가
            old = self.stacks
            if self.stacks < self.MAX_STACKS:
                self.stacks += 1
            return
        # 죽음
        self.die(blood_effects)

    def die(self, blood_effects):
        if getattr(self, "_already_dropped", False):
            return
        super().die(blood_effects)
        try:
            self.spawn_dropped_items(4, 5)
        except Exception:
            pass

    def draw(self, screen, world_x, world_y, shake_offset_x=0, shake_offset_y=0):
        if not self.alive:
            return
        sx = int(self.world_x - world_x + shake_offset_x)
        sy = int(self.world_y - world_y + shake_offset_y)

        # 텔레그래프(붉은 직사각형) — WINDUP 동안 표시(각도는 WINDUP에서 매 프레임 갱신됨)
        if self.state == "WINDUP":
            ang = self.locked_angle
            base = pygame.Surface((self.WAVE_LEN, self.WAVE_WID), pygame.SRCALPHA)
            base.fill((255, 40, 40, 110))
            rotated = pygame.transform.rotate(base, -math.degrees(ang))
            cx = sx + int(math.cos(ang) * (self.WAVE_GAP + self.WAVE_LEN * 0.5))
            cy = sy + int(math.sin(ang) * (self.WAVE_GAP + self.WAVE_LEN * 0.5))
            rect = rotated.get_rect(center=(cx, cy))
            screen.blit(rotated, rect)
            self.draw_alert(screen, sx, sy)

        # 본체(회전된 스프라이트)
        body = pygame.transform.smoothscale(
            self.image_original,
            (int(self.image_original.get_width() * PLAYER_VIEW_SCALE),
             int(self.image_original.get_height() * PLAYER_VIEW_SCALE))
        )
        body = pygame.transform.rotate(body, -math.degrees(self.direction_angle) + 90)
        body_rect = body.get_rect(center=(sx, sy))
        self.rect = body_rect
        # 기본 스프라이트 먼저 그림
        screen.blit(body, body_rect)

        if self.stacks > 0:
            add = min(180, 18 * self.stacks)  # 스택에 비례해 붉은 강도 증가
            tinted = body.copy()
            # 색상 채널에 빨강을 더함(알파는 원본 스프라이트의 알파 그대로)
            tinted.fill((add, 0, 0, 0), special_flags=pygame.BLEND_RGBA_ADD)
            screen.blit(tinted, body_rect)

        # IMPACT 슬래시(흰 바) — 빠르게 지나가는 시각 효과
        if self.state == "IMPACT":
            now = pygame.time.get_ticks()
            total = max(1, self.IMPACT_MS)
            t = 1.0 - max(0.0, (self.state_until - now) / total)
            ang = self.locked_angle
            cx = sx + int(math.cos(ang) * (self.WAVE_GAP + int(self.WAVE_LEN * t)))
            cy = sy + int(math.sin(ang) * (self.WAVE_GAP + int(self.WAVE_LEN * t)))
            bar = pygame.Surface((self.SLASH_WIDTH, self.SLASH_THICK), pygame.SRCALPHA)
            bar.fill((255, 255, 255, int(220 * (1.0 - t))))
            rotated_bar = pygame.transform.rotate(bar, -math.degrees(ang) + 90)
            bar_rect = rotated_bar.get_rect(center=(cx, cy))
            screen.blit(rotated_bar, bar_rect)

        # 머리 위 스택 표시(10칸)
        self._draw_stack_hud(screen, sx, sy - int(48 * PLAYER_VIEW_SCALE))

    def _draw_stack_hud(self, screen, cx, cy):
        total = self.MAX_STACKS
        w = int(6 * PLAYER_VIEW_SCALE)
        h = int(5 * PLAYER_VIEW_SCALE)
        gap = int(2 * PLAYER_VIEW_SCALE)
        full = self.stacks
        start_x = cx - (total * w + (total - 1) * gap) // 2
        for i in range(total):
            rect = pygame.Rect(start_x + i * (w + gap), cy, w, h)
            if i < full:
                pygame.draw.rect(screen, (200, 30, 30, 255), rect)
            else:
                pygame.draw.rect(screen, (110, 110, 110, 180), rect, width=1)

class Boss1(AIBase):
    rank=10

    FAR_DISTANCE = 800
    MID_DISTANCE = 500
    CLOSE_DISTANCE = 200
    GUN1_SAFE_MIN = MID_DISTANCE + 80
    GUN1_SAFE_MAX = MID_DISTANCE + 150

    def __init__(self, world_x, world_y, images, sounds, map_width, map_height,
                 damage_player_fn=None, kill_callback=None, is_position_blocked_fn=None, rank=rank):
        super().__init__(
            world_x, world_y, images, sounds, map_width, map_height,
            speed=0.0,
            near_threshold=0,
            far_threshold=0,
            radius=60,
            push_strength=0.18,
            alert_duration=0,
            damage_player_fn=damage_player_fn,
            rank=rank,
        )

        self.image_original = images["boss1"]
        self.gun1_image_original = images["boss1gun1"]
        self.gun2_image_original = images["boss1gun2"]
        self.bullet_image = images["enemy_bullet"]

        self.sound_gun1 = sounds["boss1_gun1_fire"]
        self.sound_gun2 = sounds["boss1_gun2_fire"]

        self.hp = 1250
        self.max_hp = 1250
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

    HP_MAX = 1500
    SPEED = NORMAL_MAX_SPEED * PLAYER_VIEW_SCALE * 0.9
    ORB_DROP_MULTIPLIER = 1.33
    ORB_DROP_ON_HALF_HP_RATIO = 0.5
    GUN1_DAMAGE = 70
    GUN1_RADIUS = 110
    GUN1_COOLDOWN = 2000
    GUN2_DAMAGE = 10
    GUN2_COOLDOWN = 2000
    DRONE_SPEED = 4 * PLAYER_VIEW_SCALE
    DRONE_DAMAGE = 150
    DRONE_RADIUS = int(70 * 1.2)
    DRONE_KNOCKBACK = 150
    DRONE_WARNING_TIME = 500
    DRONE_RESPAWN_TIME = 5000
    DRONE_RESPAWN_TIME_LOW_HP = 3000
    INITIAL_DRONES = 2

    def __init__(self, world_x, world_y, images, sounds, map_width, map_height,
                 damage_player_fn=None, kill_callback=None, rank=rank):
        super().__init__(world_x, world_y, images, sounds, map_width, map_height,
                         speed=self.SPEED, near_threshold=300, far_threshold=700,
                         radius=50, push_strength=0.18, alert_duration=0,
                         damage_player_fn=damage_player_fn,rank=rank,)

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
            max_distance=500
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
            spread = math.radians(random.uniform(-25, 25))
            dx = math.cos(angle + spread)
            dy = math.sin(angle + spread)
            bullet = Bullet(
                self.world_x, self.world_y,
                self.world_x + dx * 100, self.world_y + dy * 100,
                spread_angle_degrees=0,
                bullet_image=red_bullet_img,
                speed=6 * PLAYER_VIEW_SCALE,
                max_distance=500 * PLAYER_VIEW_SCALE,
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

class Boss3(AIBase):
    rank = 10

    HP_MAX = 2000
    SPEED = NORMAL_MAX_SPEED * PLAYER_VIEW_SCALE * 0.8
    RADIUS = 50

    SPRITE_ANGLE_OFFSET_DEG = +90
    HAMMER_ANGLE_OFFSET_DEG = +270

    MELEE_RANGE = int(170 * 1.5 * PLAYER_VIEW_SCALE)
    MELEE_ARC = math.radians(120)
    MELEE_DAMAGE = 35
    MELEE_COOLDOWN = 1800
    MELEE_WINDUP_MS = 500
    MELEE_ATTACK_SHOW_MS = 120

    THROW_COOLDOWN = 2200
    THROW_SPEED = 18 * PLAYER_VIEW_SCALE
    THROW_MAX_DIST = 1200 * PLAYER_VIEW_SCALE
    THROW_DAMAGE = 26

    CYCLONE_LINES = 8
    CYCLONE_CHARGE_MS = 2000
    CYCLONE_SWEEP_MS = 120
    CYCLONE_LINE_THICKNESS = int(42 * PLAYER_VIEW_SCALE)
    CYCLONE_SWEEP_DAMAGE = 55
    CYCLONE_ROT_SPEED = math.radians(60)
    CYCLONE_DR = 0.5

    ANVIL_HP = 200
    ANVIL_COUNT = 4
    ANVIL_RADIUS = int(26 * 1.5 * PLAYER_VIEW_SCALE)
    ANVIL_DRAW_SCALE = 1.5
    ANVIL_BUFF_PER = 0.12
    ANVIL_SPEED_PER = 0.04
    ANVIL_BEAM_SHAKE = True

    HOLD_DIST = 170
    MIN_KEEP_DIST = 70
    PUSH_STRENGTH = 0.05

    def __init__(self, world_x, world_y, images, sounds, map_width, map_height,
                 damage_player_fn=None, kill_callback=None, rank=rank):
        super().__init__(
            world_x, world_y, images, sounds, map_width, map_height,
            speed=self.SPEED, near_threshold=300, far_threshold=700,
            radius=self.RADIUS, push_strength=self.PUSH_STRENGTH, alert_duration=0,
            damage_player_fn=damage_player_fn, rank=rank
        )
        self.hp = self.HP_MAX
        self.max_hp = self.HP_MAX
        self.kill_callback = kill_callback

        self.image_original = images["boss3"]
        self.hammer_img = images["hammer"]
        self.anvil_img = images["anvil"]

        self.direction_angle = 0.0
        self.vx = 0.0
        self.vy = 0.0

        self.bullets = []
        self.scattered_bullets = []

        self.last_melee_time = 0
        self.last_throw_time = 0

        self.melee_windup_end = 0
        self.melee_center_angle = 0.0
        self.melee_attack_show_start = 0
        self.melee_attack_show_end = 0
        self.melee_swing_from = 0.0
        self.melee_swing_to = 0.0

        self.hammers = []

        self.cyclone_state = "idle"
        self.cyclone_start_ms = 0
        self.cyclone_base_angle = 0.0
        self.spin_thresholds = [int(self.HP_MAX * r) for r in (0.8, 0.6, 0.4, 0.2)]
        self.spin_used = set()

        self.anvils = []
        self.anvils_spawned = False

        self.mid_drop_done = False

    # 유틸
    def _sound(self, *keys):
        if not self.sounds:
            return
        for k in keys:
            if k in self.sounds:
                try: self.sounds[k].play()
                except: pass
                return

    def _player_world_pos(self, world_x, world_y, player_rect):
        return (world_x + player_rect.centerx, world_y + player_rect.centery)

    def _add_player_knockback(self, px, py, from_x, from_y, strength):
        dx, dy = px - from_x, py - from_y
        d = math.hypot(dx, dy) or 1.0
        nx, ny = dx / d, dy / d
        if not hasattr(config, "knockback_impulse_x"): config.knockback_impulse_x = 0.0
        if not hasattr(config, "knockback_impulse_y"): config.knockback_impulse_y = 0.0
        config.knockback_impulse_x = max(-30.0, min(30.0, config.knockback_impulse_x + nx * strength))
        config.knockback_impulse_y = max(-30.0, min(30.0, config.knockback_impulse_y + ny * strength))

    def get_damage_multiplier(self):
        return 1.0 + sum(1 for a in self.anvils if a.alive) * self.ANVIL_BUFF_PER

    def get_speed_bonus(self):
        return sum(1 for a in self.anvils if a.alive) * self.ANVIL_SPEED_PER

    # 드랍/피격
    def hit(self, damage, blood_effects, force=False):
        if self.cyclone_state in ("charge", "sweep"):
            damage = int(damage * (1.0 - self.CYCLONE_DR))
        prev = self.hp
        super().hit(damage, blood_effects, force)
        if (not self.mid_drop_done) and prev > self.HP_MAX // 2 and self.hp <= self.HP_MAX // 2 and self.alive:
            self.spawn_dropped_items(3, 4)
            self.mid_drop_done = True

    def die(self, blood_effects):
        if self._already_dropped:
            return
        super().die(blood_effects)
        for a in self.anvils:
            a.alive = False
        self.spawn_dropped_items(10, 15)

    # 모루
    class AnvilObj:
        def __init__(self, boss, x, y, img):
            self.boss = boss
            self.world_x = x
            self.world_y = y
            self.image = img
            self.hp = boss.ANVIL_HP
            self.radius = boss.ANVIL_RADIUS
            self.alive = True
            self.bullets = []
            self.scattered_bullets = []

        def update(self, dt, world_x, world_y, player_rect, enemies=[]):
            return

        def hit(self, damage, blood_effects, force=False):
            if not self.alive: return
            self.hp -= damage
            if self.hp <= 0:
                self.alive = False
                self.boss._sound("anvil_break", "AnvilBreak")
                self.boss.spawn_dropped_items(1, 2)

        def draw(self, screen, world_x, world_y, sx=0, sy=0):
            if not self.alive: return
            cx = self.world_x - world_x + sx
            cy = self.world_y - world_y + sy
            img = pygame.transform.rotozoom(self.image, 0, self.boss.ANVIL_DRAW_SCALE)
            screen.blit(img, img.get_rect(center=(int(cx), int(cy))))
            if self.boss.ANVIL_BEAM_SHAKE and self.boss.alive:
                bx = self.boss.world_x - world_x + sx
                by = self.boss.world_y - world_y + sy
                self._draw_wobbly_beam(screen, (cx, cy), (bx, by))

        def _draw_wobbly_beam(self, screen, p1, p2):
            (x1, y1), (x2, y2) = p1, p2
            t = pygame.time.get_ticks() * 0.006
            segs = 14
            pts = []
            ang = math.atan2(y2 - y1, x2 - x1)
            nx, ny = -math.sin(ang), math.cos(ang)
            for i in range(segs + 1):
                s = i / segs
                x = x1 + (x2 - x1) * s
                y = y1 + (y2 - y1) * s
                amp = 2 + 4 * abs(math.sin(s * math.pi))
                off = math.sin(t + s * 12.0) * amp
                pts.append((int(x + nx * off), int(y + ny * off)))
            pygame.draw.lines(screen, (255, 80, 80), False, pts, 6)
            pygame.draw.lines(screen, (255, 255, 255), False, pts, 2)

    def spawn_anvils(self, enemies_list):
        if self.anvils_spawned: return
        self.anvils_spawned = True
        self._sound("anvil_spawn", "AnvilSpawn")
        margin = 120 * PLAYER_VIEW_SCALE
        for _ in range(self.ANVIL_COUNT):
            ax = random.uniform(margin, self.map_width - margin)
            ay = random.uniform(margin, self.map_height - margin)
            anvil = Boss3.AnvilObj(self, ax, ay, self.anvil_img)
            self.anvils.append(anvil)
            enemies_list.append(anvil)

    # 투척 해머
    class ThrownHammer:
        def __init__(self, boss, angle):
            self.boss = boss
            self.x = boss.world_x
            self.y = boss.world_y
            self.angle = angle
            self.state = 'out'
            self.dist_travelled = 0.0
            self.v = Boss3.THROW_SPEED
            self.alive = True

        def update(self, dt):
            if not self.alive: return
            if self.state == 'out':
                dx = math.cos(self.angle) * self.v
                dy = math.sin(self.angle) * self.v
                self.x += dx; self.y += dy
                self.dist_travelled += math.hypot(dx, dy)
                if self.dist_travelled >= Boss3.THROW_MAX_DIST:
                    self.state = 'return'
            else:
                ang = math.atan2(self.boss.world_y - self.y, self.boss.world_x - self.x)
                self.angle = ang
                self.x += math.cos(self.angle) * self.v
                self.y += math.sin(self.angle) * self.v
                if math.hypot(self.boss.world_x - self.x, self.boss.world_y - self.y) < 40:
                    self.alive = False

        def try_hit_player(self, px, py, boss):
            if not self.alive: return False
            if math.hypot(px - self.x, py - self.y) <= 40 * PLAYER_VIEW_SCALE:
                dmg = int(Boss3.THROW_DAMAGE * boss.get_damage_multiplier())
                if boss.damage_player: boss.damage_player(dmg)
                boss._add_player_knockback(px, py, self.x, self.y, 12.0)
                boss._sound("stab_hit", "Stab_Hit")
                self.alive = False
                return True
            return False

        def draw(self, screen, world_x, world_y):
            if not self.alive: return
            sx, sy = self.x - world_x, self.y - world_y
            img = pygame.transform.rotozoom(
                self.boss.hammer_img,
                -math.degrees(self.angle) + self.boss.HAMMER_ANGLE_OFFSET_DEG,
                1.0
            )
            screen.blit(img, img.get_rect(center=(int(sx), int(sy))))

    # 사이클론
    def _start_cyclone(self):
        self.cyclone_state = "charge"
        self.cyclone_start_ms = pygame.time.get_ticks()
        self.cyclone_base_angle = random.uniform(0, math.pi * 2)
        self._sound("ShieldCharged", "shield_charged")

    def _update_cyclone(self, now_ms):
        if self.cyclone_state == "charge":
            if now_ms - self.cyclone_start_ms >= self.CYCLONE_CHARGE_MS:
                self.cyclone_state = "sweep"
                self.cyclone_start_ms = now_ms
                self._sound("ShockBurst", "shock_burst")
        elif self.cyclone_state == "sweep":
            if now_ms - self.cyclone_start_ms >= self.CYCLONE_SWEEP_MS:
                self.cyclone_state = "idle"

    def _draw_cyclone_and_hit(self, screen, world_x, world_y, px, py):
        if self.cyclone_state not in ("charge", "sweep"):
            return
        now = pygame.time.get_ticks()
        t = (now - self.cyclone_start_ms) / 1000.0
        angle = self.cyclone_base_angle + self.CYCLONE_ROT_SPEED * t
        cx = self.world_x - world_x
        cy = self.world_y - world_y
        N = self.CYCLONE_LINES
        L = max(self.map_width, self.map_height)
        W = self.CYCLONE_LINE_THICKNESS

        for i in range(N):
            th = angle + (2 * math.pi) * i / N
            x2 = cx + math.cos(th) * L
            y2 = cy + math.sin(th) * L
            color = (255, 0, 0) if self.cyclone_state == "charge" else (255, 255, 255)
            width = W if self.cyclone_state == "charge" else max(2, W // 4)
            pygame.draw.line(screen, color, (cx, cy), (x2, y2), width)

        if self.cyclone_state == "sweep":
            for i in range(N):
                th = angle + (2 * math.pi) * i / N
                x1w, y1w = self.world_x, self.world_y
                x2w, y2w = self.world_x + math.cos(th) * L, self.world_y + math.sin(th) * L
                vx, vy = x2w - x1w, y2w - y1w
                wx, wy = px - x1w, py - y1w
                v2 = vx * vx + vy * vy
                if v2 <= 1e-6: continue
                tproj = max(0.0, min(1.0, (wx * vx + wy * vy) / v2))
                nx = x1w + vx * tproj
                ny = y1w + vy * tproj
                d = math.hypot(px - nx, py - ny)
                if d <= self.CYCLONE_LINE_THICKNESS / 2:
                    dmg = int(self.CYCLONE_SWEEP_DAMAGE * self.get_damage_multiplier())
                    if self.damage_player: self.damage_player(dmg)
                    self._add_player_knockback(px, py, self.world_x, self.world_y, 14.0)
                    break

    # 근접(텔레그래프 → 빠른 스윕)
    def _start_melee(self, now, center_angle):
        self.melee_windup_end = now + self.MELEE_WINDUP_MS
        self.melee_center_angle = center_angle

    def _update_melee(self, now, px, py):
        # 텔레그래프 끝 → 판정 + 스윕 애니 시작
        if self.melee_windup_end and now >= self.melee_windup_end:
            self.melee_windup_end = 0
            self.melee_attack_show_start = now
            self.melee_attack_show_end = now + self.MELEE_ATTACK_SHOW_MS
            self.melee_swing_from = self.melee_center_angle - self.MELEE_ARC * 0.5
            self.melee_swing_to   = self.melee_center_angle + self.MELEE_ARC * 0.5

            dx, dy = px - self.world_x, py - self.world_y
            dist = math.hypot(dx, dy)
            if dist <= self.MELEE_RANGE:
                ang = math.atan2(dy, dx)
                diff = (ang - self.melee_center_angle + 3*math.pi) % (2*math.pi) - math.pi
                if abs(diff) <= self.MELEE_ARC * 0.5:
                    dmg = int(self.MELEE_DAMAGE * self.get_damage_multiplier())
                    if self.damage_player: self.damage_player(dmg)
                    self._add_player_knockback(px, py, self.world_x, self.world_y, 12.0)
                    self._sound("stab_hit", "Stab_Hit")

        # 스윙 애니 종료
        if self.melee_attack_show_end and now >= self.melee_attack_show_end:
            self.melee_attack_show_start = 0
            self.melee_attack_show_end = 0

    def _draw_melee(self, screen, world_x, world_y):
        # 텔레그래프(붉은 반투명 부채꼴)
        if self.melee_windup_end:
            cx = self.world_x - world_x
            cy = self.world_y - world_y
            r = self.MELEE_RANGE
            steps = 32
            pts = [(cx, cy)]
            start = self.melee_center_angle - self.MELEE_ARC * 0.5
            end   = self.melee_center_angle + self.MELEE_ARC * 0.5
            for i in range(steps + 1):
                a = start + (end - start) * (i / steps)
                pts.append((cx + math.cos(a) * r, cy + math.sin(a) * r))
            srf = pygame.Surface((self.map_width, self.map_height), pygame.SRCALPHA)
            pygame.draw.polygon(srf, (255, 50, 50, 110), pts)
            screen.blit(srf, (0, 0))

        # 공격 프레임: 해머가 부채꼴을 빠르게 스윕(모션블러 2~3장)
        if self.melee_attack_show_end:
            now = pygame.time.get_ticks()
            cx = self.world_x - world_x
            cy = self.world_y - world_y
            dur = max(1, self.MELEE_ATTACK_SHOW_MS)
            prog = max(0.0, min(1.0, (now - self.melee_attack_show_start) / dur))
            # 현재 각도
            ang = self.melee_swing_from + (self.melee_swing_to - self.melee_swing_from) * prog

            # 모션블러용 과거 샘플(2개)
            samples = [prog, max(0.0, prog - 0.4), max(0.0, prog - 0.7)]
            alphas = [255, 140, 80]
            for s, a in zip(samples, alphas):
                a_ang = self.melee_swing_from + (self.melee_swing_to - self.melee_swing_from) * s
                hx = cx + math.cos(a_ang) * (self.MELEE_RANGE * 0.55)
                hy = cy + math.sin(a_ang) * (self.MELEE_RANGE * 0.55)
                img = pygame.transform.rotozoom(
                    self.hammer_img,
                    -math.degrees(a_ang) + self.HAMMER_ANGLE_OFFSET_DEG,
                    1.0
                )
                # 반투명 블렌딩
                img2 = img.copy()
                img2.set_alpha(a)
                screen.blit(img2, img2.get_rect(center=(int(hx), int(hy))))

    # 이동
    def _update_motion(self, dt, px, py):
        dx, dy = px - self.world_x, py - self.world_y
        dist = math.hypot(dx, dy) + 1e-6
        base_speed = (self.SPEED + self.get_speed_bonus())

        if dist > self.HOLD_DIST:
            t = pygame.time.get_ticks() * 0.004
            strafe = base_speed * 0.6 * math.sin(t)
            nx, ny = -dy / dist, dx / dist
            vx_des = (dx / dist) * base_speed + nx * strafe
            vy_des = (dy / dist) * base_speed + ny * strafe
        elif dist < self.MIN_KEEP_DIST:
            vx_des = -(dx / dist) * (base_speed * 0.6)
            vy_des = -(dy / dist) * (base_speed * 0.6)
        else:
            orbit = 1 if ((pygame.time.get_ticks() // 800) % 2) == 0 else -1
            ang = math.atan2(dy, dx) + orbit * math.pi / 2
            vx_des = math.cos(ang) * base_speed * 0.75
            vy_des = math.sin(ang) * base_speed * 0.75

        lerp = 0.18
        self.vx += (vx_des - self.vx) * lerp
        self.vy += (vy_des - self.vy) * lerp

        if self.cyclone_state == "idle":
            self.world_x += self.vx
            self.world_y += self.vy

        self.direction_angle = math.atan2(dy, dx)

    # 업데이트 / 드로잉
    def update(self, dt, world_x, world_y, player_rect, enemies=[]):
        if not self.alive or not config.combat_state:
            return

        px, py = self._player_world_pos(world_x, world_y, player_rect)
        now = pygame.time.get_ticks()

        for th in self.spin_thresholds:
            if self.hp <= th and th not in self.spin_used:
                self.spin_used.add(th)
                self._start_cyclone()
                break

        if not self.anvils_spawned and self.hp <= self.HP_MAX * 0.5:
            self.spawn_anvils(enemies)
            self.anvils_spawned = True

        self._update_motion(dt, px, py)

        self._update_melee(now, px, py)
        if (not self.melee_windup_end) and (not self.melee_attack_show_end):
            if now - self.last_melee_time >= self.MELEE_COOLDOWN:
                if math.hypot(px - self.world_x, py - self.world_y) <= self.MELEE_RANGE * 0.9:
                    self._start_melee(now, self.direction_angle)
                    self.last_melee_time = now

        if now - self.last_throw_time >= self.THROW_COOLDOWN and self.cyclone_state == "idle":
            dist = math.hypot(px - self.world_x, py - self.world_y)
            if dist >= 350:
                self.hammers.append(Boss3.ThrownHammer(self, self.direction_angle))
                self.last_throw_time = now
                self._sound("stab_hit", "Stab_Hit")

        for h in self.hammers:
            h.update(dt)
            h.try_hit_player(px, py, self)
        self.hammers = [h for h in self.hammers if h.alive]

        if self.cyclone_state != "idle":
            self._update_cyclone(now)

    def draw(self, screen, world_x, world_y, sx=0, sy=0):
        if not self.alive:
            return

        player_px = config.world_x + config.player_rect.centerx
        player_py = config.world_y + config.player_rect.centery
        self._draw_cyclone_and_hit(screen, world_x, world_y, player_px, player_py)

        scr_x = self.world_x - world_x + sx
        scr_y = self.world_y - world_y + sy
        scaled = pygame.transform.smoothscale(
            self.image_original,
            (int(self.image_original.get_width() * PLAYER_VIEW_SCALE),
             int(self.image_original.get_height() * PLAYER_VIEW_SCALE))
        )
        rotated = pygame.transform.rotate(
            scaled,
            -math.degrees(self.direction_angle) + self.SPRITE_ANGLE_OFFSET_DEG
        )
        screen.blit(rotated, rotated.get_rect(center=(int(scr_x), int(scr_y))))

        self._draw_melee(screen, world_x, world_y)

        for h in self.hammers:
            h.draw(screen, world_x, world_y)

class Boss4(AIBase):
    rank = 10

    HP_MAX = 2200
    BASE_SPEED = NORMAL_MAX_SPEED * PLAYER_VIEW_SCALE * 0.75
    RADIUS = 46

    SPRITE_ANGLE_OFFSET_DEG = +90

    HOLD_DIST = int(260 * PLAYER_VIEW_SCALE)
    MIN_KEEP_DIST = int(60 * PLAYER_VIEW_SCALE)

    TURN_SPEED_DEG = 30.0
    TURN_SPEED_BASH = 360.0

    GUARD_DR = 0.70
    GUARD_FOV_DEG = 120
    SHIELD_SCALE = 1.6
    SHIELD_OFFSET = 40
    SHIELD_PUNCH_AMP = 32
    SHIELD_PUNCH_MS = 180

    CHARGE_WINDUP_MS = 500
    CHARGE_RUN_MS = 800
    CHARGE_SPEED_MUL = 2.0
    CHARGE_DAMAGE = 30
    CHARGE_KNOCKBACK = 18.0
    CHARGE_STUN_MS = 1000
    CHARGE_COOLDOWN_MS = 6000
    CHARGE_HIT_RADIUS = int(42 * PLAYER_VIEW_SCALE)
    CHARGE_TELEGRAPH_ALPHA = 120

    BASH_RANGE = int(260 * PLAYER_VIEW_SCALE)
    BASH_ARC_DEG = 110
    BASH_WINDUP_MS = 450
    BASH_DAMAGE = 22
    BASH_KNOCKBACK = 24.0
    BASH_COOLDOWN_MS = 900

    SMG_BULLETS = 8
    SMG_PER_SHOT_MS = 70
    SMG_DAMAGE = 10
    SMG_SPREAD_DEG = 12
    SMG_BULLET_SPEED = 18 * PLAYER_VIEW_SCALE
    SMG_RANGE = 700 * PLAYER_VIEW_SCALE
    SMG_MUZZLE_FLASH_MS = 80
    SMG_FAR_TRIGGER_DIST = int(560 * PLAYER_VIEW_SCALE)
    SMG_EXTRA_COOLDOWN_MS = 2500
    GUN_ANGLE_OFFSET_DEG = +90

    GRENADE_COOLDOWN_MS = 3000
    GRENADE_SPEED = 18 * PLAYER_VIEW_SCALE
    GRENADE_THROW_DISTANCE = int(500 * PLAYER_VIEW_SCALE)
    GRENADE_RADIUS = int(160 * PLAYER_VIEW_SCALE)
    GRENADE_STUN_MS = 1500
    GRENADE_DAMAGE_BLAST = 10
    GRENADE_SLOW_MS = 1200
    GRENADE_SLOW_FACTOR = 0.5
    GRENADE_SPIN_DEG_PER_MS = 0.25
    GRENADE_IMPACT_DAMAGE = 6
    GRENADE_IMPACT_STUN_MS = 600
    GRENADE_IMPACT_KNOCKBACK = 6.0
    GRENADE_IMPACT_RADIUS = int(28 * PLAYER_VIEW_SCALE)
    GRENADE_BLAST_KNOCKBACK = 10.0

    PUSH_STRENGTH = 0.00

    def __init__(self, world_x, world_y, images, sounds, map_width, map_height,
                 damage_player_fn=None, kill_callback=None, rank=rank):
        super().__init__(
            world_x, world_y, images, sounds, map_width, map_height,
            speed=self.BASE_SPEED,
            near_threshold=0,
            far_threshold=0,
            radius=self.RADIUS,
            push_strength=self.PUSH_STRENGTH,
            alert_duration=0,
            damage_player_fn=damage_player_fn,
            rank=rank,
        )
        self.hp = self.HP_MAX
        self.max_hp = self.HP_MAX
        self.kill_callback = kill_callback

        self.body_img = images["boss4"]
        self.grenade_img = images["electric_grenade"]
        self.shield_img = images.get("gun19")
        self.enemy_bullet_img = images.get("enemy_bullet", images.get("bullet1"))
        self.gun_img = images.get("gun2")

        self.block_sound = sounds.get("gun19_defend")
        self.gun_sound = sounds.get("gun2_fire") or sounds.get("gun2")
        self.stab_hit_sound = sounds.get("stab_hit") or sounds.get("Stab_Hit")
        self.shock_burst_snd = sounds.get("shock_burst") or sounds.get("ShockBurst")

        self.state = "CHASE"   # CHASE / CHARGE_WINDUP / CHARGE_RUN / SMG_BURST / BASH_WINDUP
        self.state_until = 0
        self.charge_dir = 0.0
        self.charge_hit_done = False

        self.smg_shots_left = 0
        self.smg_next_shot_at = 0
        self.last_muzzle_at = 0
        self.smg_ready_at = 0

        self.bash_angle = 0.0
        self.bash_ready_at = 0

        self.shield_punch_end = 0

        self.guard_active = False
        self._last_block_sfx_at = 0

        self._last_rot_update = pygame.time.get_ticks()

        now = pygame.time.get_ticks()
        self.charge_ready_at = now
        self.grenade_ready_at = now

        self.grenades = []

        self.half_drop_done = False

    # 유틸
    def _sound(self, snd):
        try:
            if snd: snd.play()
        except:
            pass

    def _player_world(self, world_x, world_y, player_rect):
        return (world_x + player_rect.centerx, world_y + player_rect.centery)

    def _add_knockback(self, px, py, from_x, from_y, strength):
        dx, dy = px - from_x, py - from_y
        d = math.hypot(dx, dy) or 1.0
        nx, ny = dx/d, dy/d
        if not hasattr(config, "knockback_impulse_x"): config.knockback_impulse_x = 0.0
        if not hasattr(config, "knockback_impulse_y"): config.knockback_impulse_y = 0.0
        config.knockback_impulse_x = max(-30.0, min(30.0, config.knockback_impulse_x + nx*strength))
        config.knockback_impulse_y = max(-30.0, min(30.0, config.knockback_impulse_y + ny*strength))

    def _stun_player_soft(self, ms):
        now = pygame.time.get_ticks()
        for fn_name in ("stun_player", "apply_player_stun", "request_player_stun"):
            fn = getattr(config, fn_name, None)
            if callable(fn):
                try: fn(ms)
                except: pass
                return
        try:
            config.player_stun_until = max(getattr(config, "player_stun_until", 0), now + ms)
            config.player_is_stunned = True
        except:
            pass

    def _apply_electric_explosion(self, ex, ey):
        # enemy21 규격 전기충격: 피해/스턴/슬로우/넉백
        now = pygame.time.get_ticks()
        px, py = config.world_x + config.player_rect.centerx, config.world_y + config.player_rect.centery
        dist = math.hypot(px - ex, py - ey)
        if dist <= self.GRENADE_RADIUS:
            try:
                if self.damage_player:
                    self.damage_player(int(self.GRENADE_DAMAGE_BLAST))
                else:
                    config.damage_player(int(self.GRENADE_DAMAGE_BLAST))
            except Exception:
                pass
            try:
                config.stunned_until_ms = max(getattr(config, "stunned_until_ms", 0), now + self.GRENADE_STUN_MS)
                config.slow_until_ms    = max(getattr(config, "slow_until_ms", 0), now + self.GRENADE_SLOW_MS)
                config.move_slow_factor = self.GRENADE_SLOW_FACTOR
                config.slow_started_ms  = now
                config.slow_duration_ms = self.GRENADE_SLOW_MS
            except Exception:
                pass
            self._add_knockback(px, py, ex, ey, self.GRENADE_BLAST_KNOCKBACK)

    # 각도 보간
    def _normalize_angle(self, a):
        return (a + math.pi) % (2 * math.pi) - math.pi

    def _rotate_towards_speed(self, target_angle, now_ms, deg_per_sec, instant=False):
        if instant:
            self.direction_angle = target_angle
            self._last_rot_update = now_ms
            return
        dt = max(0, now_ms - self._last_rot_update)
        max_step = math.radians(deg_per_sec) * (dt / 1000.0)
        diff = self._normalize_angle(target_angle - self.direction_angle)
        if abs(diff) <= max_step:
            self.direction_angle = target_angle
        else:
            self.direction_angle = self._normalize_angle(self.direction_angle + math.copysign(max_step, diff))
        self._last_rot_update = now_ms

    def _rotate_towards(self, target_angle, now_ms, instant=False):
        self._rotate_towards_speed(target_angle, now_ms, self.TURN_SPEED_DEG, instant)

    # 방패 전방 판정/감소
    def _is_in_front(self, from_x, from_y):
        dx, dy = from_x - self.world_x, from_y - self.world_y
        a = math.atan2(dy, dx)
        diff = (a - self.direction_angle + math.pi*3) % (math.pi*2) - math.pi
        return abs(math.degrees(diff)) <= self.GUARD_FOV_DEG * 0.5

    def hit(self, damage, blood_effects, force=False):
        # 전방 가드 적용
        self.guard_active = (self.state in ("CHASE", "CHARGE_WINDUP", "CHARGE_RUN", "BASH_WINDUP"))
        if self.guard_active:
            px = config.world_x + config.player_rect.centerx
            py = config.world_y + config.player_rect.centery
            if self._is_in_front(px, py):
                damage = int(damage * (1.0 - self.GUARD_DR))
                now = pygame.time.get_ticks()
                if self.block_sound and now - self._last_block_sfx_at > 120:
                    self._sound(self.block_sound)
                    self._last_block_sfx_at = now

        # 실제 체력 감소 처리
        super().hit(damage, blood_effects, force)

        if (not self.half_drop_done) and self.alive and self.hp <= (self.max_hp * 0.5):
            self.half_drop_done = True
            try:
                self.spawn_dropped_items(7, 7)
            except Exception:
                pass

    def die(self, blood_effects):
        super().die(blood_effects)
        self.spawn_dropped_items(10, 12)

    # 보조
    def _charge_length_exact(self):
        return int(self.BASE_SPEED * self.CHARGE_SPEED_MUL * (self.CHARGE_RUN_MS / 1000.0))

    def _compute_grenade_travel_ms(self):
        # 던지는 거리(px)를 기준으로 퓨즈(ms) 계산.
        dt_ms = max(1, int(getattr(config, "dt_ms", 16)))
        return int(self.GRENADE_THROW_DISTANCE * dt_ms / max(1.0, self.GRENADE_SPEED))

    # FSM 보조
    def _maybe_start_charge(self, now, dist):
        if now < self.charge_ready_at:
            return False
        if int(260 * PLAYER_VIEW_SCALE) <= dist <= int(900 * PLAYER_VIEW_SCALE):
            self.state = "CHARGE_WINDUP"
            self.state_until = now + self.CHARGE_WINDUP_MS
            self.charge_dir = self.direction_angle
            self.charge_hit_done = False
            return True
        return False

    def _start_smg_burst(self, now):
        self.state = "SMG_BURST"
        self.smg_shots_left = self.SMG_BULLETS
        self.smg_next_shot_at = now
        self.last_muzzle_at = 0
        self.smg_ready_at = now + self.SMG_EXTRA_COOLDOWN_MS

    def _throw_grenade(self, now, px, py):
        if now < self.grenade_ready_at:
            return
        ang = math.atan2(py - self.world_y, px - self.world_x)
        vx = math.cos(ang) * self.GRENADE_SPEED
        vy = math.sin(ang) * self.GRENADE_SPEED
        travel_ms = self._compute_grenade_travel_ms()
        self.grenades.append(Boss4.ElecGrenade(self, self.world_x, self.world_y, vx, vy, now + travel_ms))
        self.grenade_ready_at = now + self.GRENADE_COOLDOWN_MS
        self._sound(self.stab_hit_sound)

    def _maybe_start_bash(self, now, dist, ang_to_player):
        if now < self.bash_ready_at:
            return False
        if dist <= self.BASH_RANGE:
            self.state = "BASH_WINDUP"
            self.state_until = now + self.BASH_WINDUP_MS
            self.bash_angle = ang_to_player
            return True
        return False

    # 목표/행동
    def update_goal(self, world_x, world_y, player_rect, enemies):
        if not self.alive or not config.combat_state:
            return

        now = pygame.time.get_ticks()
        px, py = self._player_world(world_x, world_y, player_rect)
        dx, dy = px - self.world_x, py - self.world_y
        dist = math.hypot(dx, dy)
        desired_ang = math.atan2(dy, dx) if (dx or dy) else self.direction_angle

        # 상태별 회전 정책
        if self.state == "SMG_BURST":
            self._rotate_towards_speed(desired_ang, now, deg_per_sec=720.0, instant=True)
        elif self.state == "BASH_WINDUP":
            self._rotate_towards_speed(desired_ang, now, deg_per_sec=self.TURN_SPEED_BASH, instant=False)
        elif self.state in ("CHASE", "CHARGE_WINDUP"):
            self._rotate_towards(desired_ang, now, instant=False)
        elif self.state == "CHARGE_RUN":
            self.direction_angle = self.charge_dir
            self._last_rot_update = now

        # 접근 중 방패 활성
        self.guard_active = (self.state in ("CHASE", "CHARGE_WINDUP", "CHARGE_RUN", "BASH_WINDUP"))

        if self.state == "CHASE":
            base = self.BASE_SPEED
            self.speed = base
            if dist > self.HOLD_DIST:
                t = now * 0.002
                strafe = base * 0.25 * math.sin(t)
                nx, ny = -dy/(dist+1e-6), dx/(dist+1e-6)
                gx = self.world_x + (dx/(dist+1e-6)) * 140 + nx * 60 * strafe
                gy = self.world_y + (dy/(dist+1e-6)) * 140 + ny * 60 * strafe
                self.goal_pos = (gx, gy)
            elif dist < self.MIN_KEEP_DIST:
                ang = self.direction_angle + math.pi
                self.goal_pos = (self.world_x + math.cos(ang) * 140,
                                 self.world_y + math.sin(ang) * 140)
            else:
                orbit = 1 if ((now//800)%2)==0 else -1
                ang = self.direction_angle + orbit*math.pi/2
                self.goal_pos = (self.world_x + math.cos(ang) * 100,
                                 self.world_y + math.sin(ang) * 100)

            if dist >= self.SMG_FAR_TRIGGER_DIST and now >= self.smg_ready_at:
                self._start_smg_burst(now)
            elif self._maybe_start_charge(now, dist):
                pass
            elif self._maybe_start_bash(now, dist, self.direction_angle):
                pass

            if now >= self.grenade_ready_at and dist > int(220 * PLAYER_VIEW_SCALE):
                self._throw_grenade(now, px, py)

        elif self.state == "CHARGE_WINDUP":
            self.speed = 0.0
            self.goal_pos = (self.world_x, self.world_y)
            if now >= self.state_until:
                self.state = "CHARGE_RUN"
                self.state_until = now + self.CHARGE_RUN_MS
                self.charge_hit_done = False
                self.charge_ready_at = now + self.CHARGE_COOLDOWN_MS
                L = self._charge_length_exact()
                end_x = self.world_x + math.cos(self.charge_dir) * L
                end_y = self.world_y + math.sin(self.charge_dir) * L
                self.speed = self.BASE_SPEED * self.CHARGE_SPEED_MUL
                self.goal_pos = (end_x, end_y)

        elif self.state == "CHARGE_RUN":
            self.speed = self.BASE_SPEED * self.CHARGE_SPEED_MUL
            L = self._charge_length_exact()
            end_x = self.world_x + math.cos(self.charge_dir) * L
            end_y = self.world_y + math.sin(self.charge_dir) * L
            self.goal_pos = (end_x, end_y)

            if (not self.charge_hit_done) and (math.hypot(px - self.world_x, py - self.world_y) <= self.CHARGE_HIT_RADIUS):
                self.charge_hit_done = True
                if self.damage_player:
                    self.damage_player(self.CHARGE_DAMAGE)
                self._add_knockback(px, py, self.world_x, self.world_y, self.CHARGE_KNOCKBACK)
                self._stun_player_soft(self.CHARGE_STUN_MS)
                self._start_smg_burst(now)
                self._sound(self.stab_hit_sound)

            if now >= self.state_until:
                if self.state != "SMG_BURST":
                    self.state = "CHASE"

        elif self.state == "SMG_BURST":
            self.speed = 0.0
            self.goal_pos = (self.world_x, self.world_y)
            if self.smg_shots_left > 0 and now >= self.smg_next_shot_at:
                self.smg_shots_left -= 1
                self.smg_next_shot_at = now + self.SMG_PER_SHOT_MS
                self.last_muzzle_at = now
                if self.gun_sound:
                    self._sound(self.gun_sound)
                spread = math.radians(random.uniform(-self.SMG_SPREAD_DEG, self.SMG_SPREAD_DEG))
                ang = self.direction_angle + spread
                mx = self.world_x + math.cos(ang) * 30
                my = self.world_y + math.sin(ang) * 30
                tx = mx + math.cos(ang) * 2000
                ty = my + math.sin(ang) * 2000
                from entities import Bullet
                b = Bullet(mx, my, tx, ty, 0, self.enemy_bullet_img,
                           speed=self.SMG_BULLET_SPEED,
                           max_distance=self.SMG_RANGE,
                           damage=self.SMG_DAMAGE)
                b.owner = self
                config.global_enemy_bullets.append(b)
            if self.smg_shots_left <= 0:
                self.state = "CHASE"

        elif self.state == "BASH_WINDUP":
            self.speed = 0.0
            self.goal_pos = (self.world_x, self.world_y)
            # 붉은 부채꼴 텔레그래프가 시선과 동기화되도록 고속 선회
            self._rotate_towards_speed(math.atan2(dy, dx) if (dx or dy) else self.direction_angle,
                                       now, deg_per_sec=self.TURN_SPEED_BASH, instant=False)
            self.bash_angle = self.direction_angle
            if now >= self.state_until:
                ang_to_player = math.atan2(dy, dx) if (dx or dy) else self.direction_angle
                diff = self._normalize_angle(ang_to_player - self.bash_angle)
                in_arc = abs(math.degrees(diff)) <= (self.BASH_ARC_DEG * 0.5)
                if dist <= self.BASH_RANGE and in_arc:
                    if self.damage_player:
                        self.damage_player(self.BASH_DAMAGE)
                    self._add_knockback(px, py, self.world_x, self.world_y, self.BASH_KNOCKBACK)
                    self._sound(self.stab_hit_sound)
                self.bash_ready_at = now + self.BASH_COOLDOWN_MS
                self.shield_punch_end = now + self.SHIELD_PUNCH_MS
                self.state = "CHASE"

        # 수류탄 갱신
        for g in self.grenades[:]:
            g.update(world_x, world_y)
            if (not g.exploding):
                if math.hypot(px - g.world_x, py - g.world_y) <= self.GRENADE_IMPACT_RADIUS:
                    if self.damage_player and self.GRENADE_IMPACT_DAMAGE > 0:
                        self.damage_player(self.GRENADE_IMPACT_DAMAGE)
                    self._stun_player_soft(self.GRENADE_IMPACT_STUN_MS)
                    self._add_knockback(px, py, g.world_x, g.world_y, self.GRENADE_IMPACT_KNOCKBACK)
                    if self.shock_burst_snd: self._sound(self.shock_burst_snd)
                    self._apply_electric_explosion(g.world_x, g.world_y)
                    g.start_explosion()
            if g.should_explode():
                self._apply_electric_explosion(g.world_x, g.world_y)
                if self.shock_burst_snd: self._sound(self.shock_burst_snd)
                g.start_explosion()
            if g.done:
                self.grenades.remove(g)

    # 드로잉
    def draw(self, screen, world_x, world_y, shake_offset_x=0, shake_offset_y=0):
        if not self.alive:
            return
        now = pygame.time.get_ticks()
        cx = self.world_x - world_x + shake_offset_x
        cy = self.world_y - world_y + shake_offset_y

        # CHASE 상태 사전 예고 텔레그래프
        if self.state == "CHASE":
            px = config.world_x + config.player_rect.centerx
            py = config.world_y + config.player_rect.centery
            dist = math.hypot(px - self.world_x, py - self.world_y)
            if now >= self.charge_ready_at and int(260 * PLAYER_VIEW_SCALE) <= dist <= int(900 * PLAYER_VIEW_SCALE):
                self._draw_charge_rect(screen, cx, cy, self.direction_angle)

        # 돌진 WINDUP 예고
        if self.state == "CHARGE_WINDUP":
            self._draw_charge_rect(screen, cx, cy, self.charge_dir)

        # 밀치기 텔레그래프(붉은 부채꼴)
        if self.state == "BASH_WINDUP":
            self._draw_fan(screen, cx, cy, self.bash_angle, self.BASH_ARC_DEG, self.BASH_RANGE, (255, 0, 0, 100))

        # 방패(보스 뒤에 먼저 그리기)
        if self.guard_active or now < self.shield_punch_end:
            if self.shield_img:
                extra = 0.0
                if now < self.shield_punch_end:
                    t = 1.0 - max(0.0, (self.shield_punch_end - now) / float(self.SHIELD_PUNCH_MS))
                    extra = math.sin(t * math.pi) * self.SHIELD_PUNCH_AMP
                ang_deg = -math.degrees(self.direction_angle) + 270  # 180° 보정
                icon = pygame.transform.rotozoom(self.shield_img, ang_deg, self.SHIELD_SCALE)
                ix = cx + math.cos(self.direction_angle) * (self.SHIELD_OFFSET + extra)
                iy = cy + math.sin(self.direction_angle) * (self.SHIELD_OFFSET + extra)
                screen.blit(icon, icon.get_rect(center=(int(ix), int(iy))))

        # 본체(방패 위에 덮음)
        scaled = pygame.transform.smoothscale(
            self.body_img,
            (int(self.body_img.get_width() * PLAYER_VIEW_SCALE),
             int(self.body_img.get_height() * PLAYER_VIEW_SCALE))
        )
        rotated = pygame.transform.rotate(scaled, -math.degrees(self.direction_angle) + self.SPRITE_ANGLE_OFFSET_DEG)
        screen.blit(rotated, rotated.get_rect(center=(int(cx), int(cy))))

        # SMG 총 이미지/플래시
        show_gun = (self.state == "SMG_BURST") or (self.last_muzzle_at and now - self.last_muzzle_at <= self.SMG_MUZZLE_FLASH_MS)
        if show_gun and self.gun_img:
            gx = cx + math.cos(self.direction_angle) * 26
            gy = cy + math.sin(self.direction_angle) * 26
            gun = pygame.transform.rotozoom(self.gun_img, -math.degrees(self.direction_angle) + self.GUN_ANGLE_OFFSET_DEG, 0.8)
            screen.blit(gun, gun.get_rect(center=(int(gx), int(gy))))
        if self.last_muzzle_at and now - self.last_muzzle_at <= self.SMG_MUZZLE_FLASH_MS:
            fx = cx + math.cos(self.direction_angle) * 38
            fy = cy + math.sin(self.direction_angle) * 38
            pygame.draw.circle(screen, (255,255,255), (int(fx), int(fy)), 6)
            ex = fx + math.cos(self.direction_angle) * 16
            ey = fy + math.sin(self.direction_angle) * 16
            pygame.draw.line(screen, (255,255,255), (int(fx), int(fy)), (int(ex), int(ey)), 3)

        # 수류탄
        for g in self.grenades:
            g.draw(screen, world_x, world_y, shake_offset_x, shake_offset_y)

    def _draw_charge_rect(self, screen, cx, cy, ang):
        L = max(1, self._charge_length_exact())
        T = max(1, int(self.radius * 2))
        dx = math.cos(ang)
        dy = math.sin(ang)
        nx, ny = -dy, dx
        hx, hy = dx * (L * 0.5), dy * (L * 0.5)
        tx, ty = nx * (T * 0.5), ny * (T * 0.5)
        p1 = (int(cx - hx - tx), int(cy - hy - ty))
        p2 = (int(cx - hx + tx), int(cy - hy + ty))
        p3 = (int(cx + hx + tx), int(cy + hy + ty))
        p4 = (int(cx + hx - tx), int(cy + hy - ty))
        srf = pygame.Surface((self.map_width, self.map_height), pygame.SRCALPHA)
        pygame.draw.polygon(srf, (255, 0, 0, self.CHARGE_TELEGRAPH_ALPHA), [p1, p2, p3, p4])
        screen.blit(srf, (0, 0))

    def _draw_fan(self, screen, cx, cy, center_ang, fov_deg, radius, color_rgba):
        steps = 28
        start = center_ang - math.radians(fov_deg*0.5)
        end = center_ang + math.radians(fov_deg*0.5)
        pts = [(cx, cy)]
        for i in range(steps+1):
            a = start + (end-start) * (i/steps)
            pts.append((cx + math.cos(a)*radius, cy + math.sin(a)*radius))
        srf = pygame.Surface((self.map_width, self.map_height), pygame.SRCALPHA)
        pygame.draw.polygon(srf, color_rgba, pts)
        screen.blit(srf, (0, 0))

    # 내부: 전기 수류탄
    class ElecGrenade:
        def __init__(self, boss, x, y, vx, vy, explode_at_ms):
            self.boss = boss
            self.world_x = x
            self.world_y = y
            self.vx = vx
            self.vy = vy
            self.explode_at = explode_at_ms
            self.exploding = False
            self.explode_end = 0
            self.done = False
            self.angle_deg = 0.0

        def should_explode(self):
            return (not self.exploding) and pygame.time.get_ticks() >= self.explode_at

        def start_explosion(self):
            self.exploding = True
            self.explode_end = pygame.time.get_ticks() + 280
            self.vx = self.vy = 0

        def update(self, world_x, world_y):
            if self.done:
                return
            if not self.exploding:
                self.world_x += self.vx
                self.world_y += self.vy
                dt_ms = getattr(config, "dt_ms", 16)
                self.angle_deg = (self.angle_deg + self.boss.GRENADE_SPIN_DEG_PER_MS * dt_ms) % 360
            else:
                if pygame.time.get_ticks() >= self.explode_end:
                    self.done = True

        def draw(self, screen, world_x, world_y, shake_offset_x=0, shake_offset_y=0):
            if self.done:
                return
            cx = int(self.world_x - world_x + shake_offset_x)
            cy = int(self.world_y - world_y + shake_offset_y)
            if not self.exploding:
                img = pygame.transform.rotozoom(self.boss.grenade_img, -self.angle_deg, 1.0)
                screen.blit(img, img.get_rect(center=(cx, cy)))
            else:
                t = 1.0 - max(0.0, (self.explode_end - pygame.time.get_ticks()) / 280.0)
                r = int(self.boss.GRENADE_RADIUS * t)
                pygame.draw.circle(screen, (255,255,255), (cx, cy), max(6, r), 4)
                pygame.draw.circle(screen, (160,200,255), (cx, cy), max(4, int(r*0.65)), 3)

class Boss5(AIBase):
    rank = 10

    HP_MAX   = 4000
    SPEED    = NORMAL_MAX_SPEED * PLAYER_VIEW_SCALE * 0.8
    RADIUS   = 50
    KEEP_MIN = int(220 * PLAYER_VIEW_SCALE)
    KEEP_MAX = int(320 * PLAYER_VIEW_SCALE)

    ORIENT_OFFSET_DEG = 270 

    ORB_DROP_ON_HALF_HP = (8, 10)
    ORB_DROP_ON_DEATH   = (16, 20)

    CHAIN_RANGE         = int(1600 * PLAYER_VIEW_SCALE)
    CHAIN_SPEED_BASE    = 36 * PLAYER_VIEW_SCALE
    CHAIN_OUT_FACTOR    = 2.0
    CHAIN_REEL_FACTOR   = 2.0
    CHAIN_HIT_REEL_FAC  = 0.5
    CHAIN_WIDTH         = int(26 * PLAYER_VIEW_SCALE)
    CHAIN_HIT_RADIUS    = int(34 * PLAYER_VIEW_SCALE)
    CHAIN_HIT_STUN      = 1000
    CHAIN_DRAG_MS       = 900                             
    CHAIN_PULL_STRENGTH = 26.0                            
    CHAIN_FOLLOW_DMG    = 40
    CHAIN_COOLDOWN      = 3500
    CHAIN_TEL_MS        = 700
    CHAIN_TEL_FREEZE_MS = 300
    CHAIN_TEL_ROT_SPEED = 0.6 * math.pi
    CHAIN_FAN_COUNT     = 20

    WHIRL_RADIUS        = int(300 * PLAYER_VIEW_SCALE)
    WHIRL_DMG           = 35
    WHIRL_TEL_MS        = 650
    WHIRL_COOLDOWN      = 4500
    WHIRL_SPIN_MS       = 300
    WHIRL_CHAIN_W       = 10
    WHIRL_PUSH_STRENGTH = 27.5

    SLAM_DMG            = 20
    SLAM_PULL_STRENGTH  = 40.0
    SLAM_LINE_W         = int(48 * PLAYER_VIEW_SCALE)
    SLAM_TEL_MS         = 750
    SLAM_COOLDOWN       = 4000
    SLAM_LEN            = int(900 * PLAYER_VIEW_SCALE)
    SLAM_OUT_MS         = 200
    SLAM_REEL_MS        = 200

    ENRAGE_COOLDOWN_FACTOR = 0.8
    DOT_DMG_PER_SEC        = 5
    DOT_DURATION_MS        = 3000

    CHAIN_COLOR_OUTER = (24, 24, 24)
    CHAIN_COLOR_INNER = (70, 70, 70)
    CHAIN_COLOR_HIGHL = (125, 125, 125)

    def __init__(self, world_x, world_y, images, sounds, map_width, map_height,
                 damage_player_fn=None, kill_callback=None, rank=rank):
        super().__init__(
            world_x, world_y, images, sounds, map_width, map_height,
            speed=self.SPEED, near_threshold=0, far_threshold=0,
            radius=self.RADIUS, push_strength=0.10, alert_duration=0,
            damage_player_fn=damage_player_fn, rank=rank
        )
        self.image_original = images["boss5"]
        self.image = self.image_original

        self.hp = self.HP_MAX
        self.max_hp = self.HP_MAX
        self.enraged = False
        self.half_hp_triggered = False
        self.kill_callback = kill_callback

        now = pygame.time.get_ticks()
        self.last_chain = now - 1500
        self.last_whirl = now - 2000
        self.last_slam  = now - 2000

        self.hooks = []
        self.chain_prep_until = 0

        self.chain_tel_start = 0
        self.chain_tel_freeze_at = 0
        self.chain_tel_angle0 = 0.0
        self.chain_tel_angle_frozen = None

        self._dragging = False
        self.drag_until = 0
        self._drag_channel = None
        self._drag_sound_end_ms = 0
        self._drag_last_play_ms = 0

        self.whirl_prep_until = 0
        self.whirl_spin_until = 0
        self._whirl_base_angle = 0.0

        self.slam_prep_until  = 0
        self.slam_aim_angle   = 0.0
        self.slam_phase       = "idle"
        self.slam_phase_t0    = 0
        self.slam_done_damage = False

        self.facing_angle = 0.0

        self._strafe_dir = 1
        self._boss5_drop_done = False

    # 유틸
    def _cool(self, base_ms):
        return int(base_ms * (self.ENRAGE_COOLDOWN_FACTOR if self.enraged else 1.0))
    def _ready(self, last_ts, base_cd):
        return pygame.time.get_ticks() - last_ts >= self._cool(base_cd)
    def _player_center(self, player_rect, world_x, world_y):
        return (world_x + player_rect.centerx, world_y + player_rect.centery)

    def _ensure_impulse_vars(self):
        if not hasattr(config, "knockback_impulse_x"): config.knockback_impulse_x = 0.0
        if not hasattr(config, "knockback_impulse_y"): config.knockback_impulse_y = 0.0

    def _apply_impulse(self, px, py, from_x, from_y, strength, direction="away"):
        # direction: "toward"(끌기) / "away"(밀기)
        self._ensure_impulse_vars()
        dx, dy = px - from_x, py - from_y
        d = math.hypot(dx, dy) or 1.0
        nx, ny = dx / d, dy / d
        if direction == "away":
            config.knockback_impulse_x = max(-30.0, min(30.0, config.knockback_impulse_x + nx * strength))
            config.knockback_impulse_y = max(-30.0, min(30.0, config.knockback_impulse_y + ny * strength))
        else:
            config.knockback_impulse_x = max(-30.0, min(30.0, config.knockback_impulse_x - nx * strength))
            config.knockback_impulse_y = max(-30.0, min(30.0, config.knockback_impulse_y - ny * strength))

    # 체인 훅
    class ChainHook:
        __slots__ = ("x","y","ux","uy","phase","alive","hit_applied","out_speed","reel_speed")
        def __init__(self, x, y, ang, out_speed, reel_speed):
            self.x = x; self.y = y
            self.ux = math.cos(ang); self.uy = math.sin(ang)
            self.phase = "out"
            self.alive = True
            self.hit_applied = False
            self.out_speed  = out_speed
            self.reel_speed = reel_speed

        def update(self, boss_x, boss_y):
            if not self.alive: return
            if self.phase == "out":
                self.x += self.ux * self.out_speed
                self.y += self.uy * self.out_speed
            else:
                dx, dy = boss_x - self.x, boss_y - self.y
                d = math.hypot(dx, dy) or 1.0
                self.x += (dx / d) * self.reel_speed
                self.y += (dy / d) * self.reel_speed
                if d <= self.reel_speed + 2:
                    self.alive = False

    # 드랍/사망
    def die(self, blood_effects):
        if not self._boss5_drop_done:
            self.spawn_dropped_items(*self.ORB_DROP_ON_DEATH)
            self._boss5_drop_done = True
        super().die(blood_effects)

    def stop_sounds_on_remove(self):
        # 장면에서 제거 시 드래그 사운드 정리
        try:
            if self._drag_channel and self._drag_channel.get_busy():
                self._drag_channel.stop()
        except Exception:
            pass
        self._drag_channel = None

    # 메인 업데이트
    def update(self, dt, world_x, world_y, player_rect, enemies=[]):
        if not self.alive:
            return

        # 플레이어 각도
        px, py = self._player_center(player_rect, world_x, world_y)
        self.facing_angle = math.atan2(py - self.world_y, px - self.world_x)

        # 분노 진입
        if not self.enraged and self.hp <= self.HP_MAX // 2:
            self.enraged = True
            if not self.half_hp_triggered:
                self.spawn_dropped_items(*self.ORB_DROP_ON_HALF_HP)
                self.half_hp_triggered = True

        dist = math.hypot(px - self.world_x, py - self.world_y)
        now = pygame.time.get_ticks()

        # 스핀 만료
        if self.whirl_spin_until and now >= self.whirl_spin_until:
            self.whirl_spin_until = 0

        # 끌기(toward) 유지 + 사운드 관리(루프 없음)
        if self._dragging and now < self.drag_until:
            self._apply_impulse(px, py, self.world_x, self.world_y, strength=self.CHAIN_PULL_STRENGTH, direction="toward")
            # 빈 채널이면 0.8s 단발 재생(최대 5초 세이프티)
            if "chain_drag" in self.sounds and now < self._drag_sound_end_ms:
                if (self._drag_channel is None) or (not self._drag_channel.get_busy()):
                    try:
                        self._drag_channel = self.sounds["chain_drag"].play(loops=0)
                        self._drag_last_play_ms = now
                    except Exception:
                        self._drag_channel = None
        else:
            self._dragging = False
            # 즉시 정리
            if self._drag_channel:
                try:
                    if self._drag_channel.get_busy():
                        self._drag_channel.stop()
                except Exception:
                    pass
                self._drag_channel = None

        # 훅 업데이트 & 충돌 (아웃/리턴 모두 히트)
        if self.hooks:
            rng2 = (self.CHAIN_RANGE * self.CHAIN_RANGE)
            for h in self.hooks:
                if not h.alive: continue
                dx, dy = h.x - self.world_x, h.y - self.world_y
                if h.phase == "out" and (dx*dx + dy*dy) >= rng2:
                    h.phase = "reel"
                h.update(self.world_x, self.world_y)

                # 히트 판정 (1회)
                if not h.hit_applied and math.hypot(px - h.x, py - h.y) <= self.CHAIN_HIT_RADIUS:
                    h.hit_applied = True
                    if "chain_hit" in self.sounds: self.sounds["chain_hit"].play()
                    # 드래그 시작(사운드 세이프티)
                    self._dragging = True
                    self.drag_until = max(self.drag_until, now + self.CHAIN_DRAG_MS)
                    self._drag_sound_end_ms = now + 5000
                    if self.enraged:
                        try:
                            config.active_dots.append({"end_time": now + self.DOT_DURATION_MS,
                                                       "damage": self.DOT_DMG_PER_SEC})
                        except Exception: pass
                    if self.damage_player:
                        try: self.damage_player(int(self.CHAIN_FOLLOW_DMG))
                        except Exception: pass
                    # 즉시 리턴 + 느린 회수
                    h.phase = "reel"
                    h.reel_speed = self.CHAIN_SPEED_BASE * self.CHAIN_HIT_REEL_FAC
            self.hooks = [h for h in self.hooks if h.alive]

        # 슬램 FSM 전환
        if self.slam_phase == "out" and (now - self.slam_phase_t0) >= self.SLAM_OUT_MS:
            self.slam_phase = "reel"
            self.slam_phase_t0 = now
        elif self.slam_phase == "reel" and (now - self.slam_phase_t0) >= self.SLAM_REEL_MS:
            self.slam_phase = "idle"
            self.slam_done_damage = False

        # 패턴 스케줄
        # 근접: 회전 우선
        if dist <= int(180 * PLAYER_VIEW_SCALE) and self.whirl_prep_until == 0 and self.whirl_spin_until == 0:
            if self._ready(self.last_whirl, self.WHIRL_COOLDOWN):
                self.whirl_prep_until = now + self.WHIRL_TEL_MS

        # 중거리: 내려찍기(시전 중 각도 갱신)
        if self.slam_prep_until == 0 and self.whirl_prep_until == 0 and not self.chain_prep_until:
            if int(300 * PLAYER_VIEW_SCALE) <= dist <= int(600 * PLAYER_VIEW_SCALE):
                if self._ready(self.last_slam, self.SLAM_COOLDOWN):
                    self.slam_prep_until = now + self.SLAM_TEL_MS
                    self.slam_aim_angle = self.facing_angle
        if self.slam_prep_until and now < self.slam_prep_until:
            self.slam_aim_angle = self.facing_angle

        # 원거리/기타: 전방향 사슬 (텔레그래프 회전 시작)
        if self.chain_prep_until == 0 and self.whirl_prep_until == 0 and self.slam_prep_until == 0:
            if self._ready(self.last_chain, self.CHAIN_COOLDOWN) and not self.hooks:
                self.chain_prep_until = now + self.CHAIN_TEL_MS
                self.chain_tel_start = now
                self.chain_tel_freeze_at = self.chain_prep_until - self.CHAIN_TEL_FREEZE_MS
                self.chain_tel_angle0 = ((now * 0.003) % (2 * math.pi))  # 간단 의사랜덤 시드
                self.chain_tel_angle_frozen = None

        # -텔레그래프 종료 → 발사/실행
        # 회전 발사
        if self.whirl_prep_until and now >= self.whirl_prep_until:
            if "whirl" in self.sounds: self.sounds["whirl"].play()
            if math.hypot(px - self.world_x, py - self.world_y) <= self.WHIRL_RADIUS:
                try: self.damage_player(int(self.WHIRL_DMG))
                except Exception: pass
                self._apply_impulse(px, py, self.world_x, self.world_y,
                                    strength=self.WHIRL_PUSH_STRENGTH, direction="away")
                if self.enraged:
                    try: config.active_dots.append({"end_time": now + self.DOT_DURATION_MS,
                                                    "damage": self.DOT_DMG_PER_SEC})
                    except Exception: pass
            self.last_whirl = now
            self.whirl_prep_until = 0
            self.whirl_spin_until = now + self.WHIRL_SPIN_MS
            self._whirl_base_angle = self.facing_angle

        # 내려찍기 발사
        if self.slam_prep_until and now >= self.slam_prep_until:
            self.last_slam = now
            self.slam_prep_until = 0
            self.slam_aim_angle = self.facing_angle
            self.slam_phase = "out"
            self.slam_phase_t0 = now
            self.slam_done_damage = False
            if "chain_throw" in self.sounds: self.sounds["chain_throw"].play()

        # 내려찍기 피해(애니 중 1회, toward)
        if self.slam_phase in ("out","reel") and not self.slam_done_damage:
            if self.slam_phase == "out":
                prog = min(1.0, (now - self.slam_phase_t0) / max(1, self.SLAM_OUT_MS))
            else:
                prog = max(0.0, 1.0 - (now - self.slam_phase_t0) / max(1, self.SLAM_REEL_MS))
            cur_len = self.SLAM_LEN * prog
            x1, y1 = self.world_x, self.world_y
            x2 = x1 + math.cos(self.slam_aim_angle) * cur_len
            y2 = y1 + math.sin(self.slam_aim_angle) * cur_len

            def _pt_seg(px_, py_, x1_, y1_, x2_, y2_):
                vx, vy = x2_ - x1_, y2_ - y1_
                wx, wy = px_ - x1_, py_ - y1_
                c1 = vx * wx + vy * wy
                if c1 <= 0:   return math.hypot(px_ - x1_, py_ - y1_)
                c2 = vx * vx + vy * vy
                if c2 <= c1:  return math.hypot(px_ - x2_, py_ - y2_)
                b = c1 / c2
                bx, by = x1_ + b * vx, y1_ + b * vy
                return math.hypot(px_ - bx, py_ - by)

            if _pt_seg(px, py, x1, y1, x2, y2) <= self.SLAM_LINE_W * 0.5:
                try: self.damage_player(int(self.SLAM_DMG))
                except Exception: pass
                self._apply_impulse(px, py, self.world_x, self.world_y,
                                    strength=self.SLAM_PULL_STRENGTH, direction="toward")
                self.slam_done_damage = True

        # 전방향 사슬 발사(회전 정지 각도로 생성)
        if self.chain_prep_until and now >= self.chain_prep_until:
            # 정지 각 계산
            if self.chain_tel_angle_frozen is None:
                freeze_angle = self.chain_tel_angle0 + self.CHAIN_TEL_ROT_SPEED * max(0.0, (self.chain_tel_freeze_at - self.chain_tel_start)) / 1000.0
            else:
                freeze_angle = self.chain_tel_angle_frozen
            angle_step = (2 * math.pi) / float(self.CHAIN_FAN_COUNT)
            out_spd  = self.CHAIN_SPEED_BASE * self.CHAIN_OUT_FACTOR
            reel_spd = self.CHAIN_SPEED_BASE * self.CHAIN_REEL_FACTOR
            for i in range(self.CHAIN_FAN_COUNT):
                ang = freeze_angle + angle_step * i
                self.hooks.append(Boss5.ChainHook(self.world_x, self.world_y, ang, out_spd, reel_spd))
            self.last_chain = now
            self.chain_prep_until = 0
            self.chain_tel_start = 0
            self.chain_tel_freeze_at = 0
            self.chain_tel_angle_frozen = None
            if "chain_throw" in self.sounds: self.sounds["chain_throw"].play()

        # 포지셔닝
        if (not self._dragging and self.slam_prep_until == 0 and self.slam_phase == "idle"
            and not self.chain_prep_until and not self.hooks):
            dx, dy = px - self.world_x, py - self.world_y
            d = math.hypot(dx, dy) or 1.0
            nx, ny = dx / d, dy / d
            if dist < self.KEEP_MIN:
                self.world_x -= nx * self.speed
                self.world_y -= ny * self.speed
            elif dist > self.KEEP_MAX:
                self.world_x += nx * self.speed
                self.world_y += ny * self.speed
            else:
                ortho = (-ny, nx) if self._strafe_dir > 0 else (ny, -nx)
                self.world_x += ortho[0] * (self.speed * 0.6)
                self.world_y += ortho[1] * (self.speed * 0.6)
                if now % 1200 < 20: self._strafe_dir *= -1

        # 경계
        self.world_x = max(0, min(self.map_width,  self.world_x))
        self.world_y = max(0, min(self.map_height, self.world_y))

    # 체인 드로잉
    def _draw_chain_segment(self, surface, x1, y1, x2, y2, width, period=28, duty=0.55):
        dx, dy = x2 - x1, y2 - y1
        L = math.hypot(dx, dy)
        if L < 1: return
        nx, ny = dx / L, dy / L
        filled = period * duty
        t = 0.0
        while t < L:
            seg_len = min(filled, L - t)
            sx = x1 + nx * t; sy = y1 + ny * t
            ex = x1 + nx * (t + seg_len); ey = y1 + ny * (t + seg_len)
            pygame.draw.line(surface, self.CHAIN_COLOR_OUTER, (sx, sy), (ex, ey), width + 4)
            pygame.draw.line(surface, self.CHAIN_COLOR_INNER, (sx, sy), (ex, ey), width)
            pygame.draw.line(surface, self.CHAIN_COLOR_HIGHL, (sx, sy), (ex, ey), max(1, width - 6))
            t += period

    def _draw_chain_line(self, surface, x1, y1, x2, y2, width):
        self._draw_chain_segment(surface, x1, y1, x2, y2, width=width, period=28, duty=0.55)

    def _draw_spoke(self, surface, cx, cy, radius, angle, width):
        x2 = cx + math.cos(angle) * radius
        y2 = cy + math.sin(angle) * radius
        self._draw_chain_line(surface, cx, cy, x2, y2, width)

    # 드로우
    def draw(self, surface, world_x, world_y, shake_offset_x=0, shake_offset_y=0):
        if not self.alive and self.hp <= 0:
            return

        sx = self.world_x - world_x
        sy = self.world_y - world_y
        now = pygame.time.get_ticks()

        # 본체 회전 렌더
        ang_deg = math.degrees(self.facing_angle) + self.ORIENT_OFFSET_DEG
        if self.enraged:
            glow_r = max(self.image_original.get_width(), self.image_original.get_height()) // 2 + 20
            glow = pygame.Surface((glow_r*2, glow_r*2), pygame.SRCALPHA)
            pygame.draw.circle(glow, (255, 60, 40, 70), (glow_r, glow_r), glow_r)
            surface.blit(glow, glow.get_rect(center=(sx, sy)).topleft)
        rotated = pygame.transform.rotate(self.image_original, -ang_deg)
        surface.blit(rotated, rotated.get_rect(center=(sx, sy)).topleft)

        # 텔레그래프(반투명)
        if self.whirl_prep_until and now < self.whirl_prep_until:
            r = self.WHIRL_RADIUS
            s = pygame.Surface((r*2, r*2), pygame.SRCALPHA)
            pygame.draw.circle(s, (255, 40, 40, 60), (r, r), r)
            surface.blit(s, (sx - r, sy - r))

        if self.slam_prep_until and now < self.slam_prep_until:
            tel = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            x1, y1 = sx, sy
            x2 = x1 + math.cos(self.slam_aim_angle) * self.SLAM_LEN
            y2 = y1 + math.sin(self.slam_aim_angle) * self.SLAM_LEN
            pygame.draw.line(tel, (255, 60, 60, 90), (x1, y1), (x2, y2), self.SLAM_LINE_W)
            surface.blit(tel, (0, 0))

        # 전방향 사슬: 회전 텔레그래프 (종료 0.3초 전 정지)
        if self.chain_prep_until and now < self.chain_prep_until:
            if now < self.chain_tel_freeze_at:
                current_angle = self.chain_tel_angle0 + self.CHAIN_TEL_ROT_SPEED * ((now - self.chain_tel_start) / 1000.0)
            else:
                if self.chain_tel_angle_frozen is None:
                    self.chain_tel_angle_frozen = self.chain_tel_angle0 + self.CHAIN_TEL_ROT_SPEED * ((self.chain_tel_freeze_at - self.chain_tel_start) / 1000.0)
                current_angle = self.chain_tel_angle_frozen

            tel = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            angle_step = (2 * math.pi) / float(self.CHAIN_FAN_COUNT)
            length = self.CHAIN_RANGE
            for i in range(self.CHAIN_FAN_COUNT):
                a = current_angle + angle_step * i
                x2 = sx + math.cos(a) * length
                y2 = sy + math.sin(a) * length
                pygame.draw.line(tel, (255, 60, 60, 80), (sx, sy), (x2, y2), self.CHAIN_WIDTH)
            surface.blit(tel, (0, 0))

        # 휘두르기 이펙트(스포크 1바퀴)
        if self.whirl_spin_until and now < self.whirl_spin_until:
            t = (now - (self.whirl_spin_until - self.WHIRL_SPIN_MS)) / max(1, self.WHIRL_SPIN_MS)
            base_angle = self._whirl_base_angle + 2 * math.pi * t
            self._draw_spoke(surface, sx, sy, self.WHIRL_RADIUS, base_angle, self.WHIRL_CHAIN_W)
            # 잔상
            lag1 = base_angle - 0.20
            lag2 = base_angle - 0.40
            self._draw_spoke(surface, sx, sy, self.WHIRL_RADIUS, lag1, max(4, self.WHIRL_CHAIN_W-4))
            self._draw_spoke(surface, sx, sy, self.WHIRL_RADIUS, lag2, max(3, self.WHIRL_CHAIN_W-6))

        # 내려찍기(out→reel) 체인
        if self.slam_phase in ("out","reel"):
            if self.slam_phase == "out":
                prog = min(1.0, (now - self.slam_phase_t0) / max(1, self.SLAM_OUT_MS))
            else:
                prog = max(0.0, 1.0 - (now - self.slam_phase_t0) / max(1, self.SLAM_REEL_MS))
            cur_len = self.SLAM_LEN * prog
            x1, y1 = sx, sy
            x2 = x1 + math.cos(self.slam_aim_angle) * cur_len
            y2 = y1 + math.sin(self.slam_aim_angle) * cur_len
            self._draw_chain_line(surface, x1, y1, x2, y2, width=max(8, self.SLAM_LINE_W//4))

        # 실제 사슬(멀티 훅)
        if self.hooks:
            for h in self.hooks:
                if not h.alive: continue
                hx = h.x - world_x
                hy = h.y - world_y
                self._draw_chain_line(surface, sx, sy, hx, hy, width=max(6, self.CHAIN_WIDTH//3))
                pygame.draw.circle(surface, self.CHAIN_COLOR_OUTER, (int(hx), int(hy)), 10)
                pygame.draw.circle(surface, self.CHAIN_COLOR_INNER, (int(hx), int(hy)), 8)

class Boss6(AIBase):
    rank = 10

    HP_MAX   = 3500
    SPEED    = NORMAL_MAX_SPEED * PLAYER_VIEW_SCALE * 0.72
    RADIUS   = int(48 * PLAYER_VIEW_SCALE)
    KEEP_MIN = int(260 * PLAYER_VIEW_SCALE)
    KEEP_MAX = int(420 * PLAYER_VIEW_SCALE)
    ORIENT_OFFSET_DEG = 270

    MINION_CAP_BASE   = 4
    MINION_CAP_ENRAGE = 5
    SUMMON_BURST      = 2
    SUMMON_CD_BASE    = 8000
    SUMMON_CD_ENRAGE  = 6000
    SUMMON_CAST_MS    = 1500
    SUMMON_RING_MIN   = int(260 * PLAYER_VIEW_SCALE)
    SUMMON_RING_MAX   = int(520 * PLAYER_VIEW_SCALE)

    LASER_TICK_MS  = 200
    SWEEP_DOT      = 8
    GRID_DOT       = 7
    ROTOR_DOT      = 9
    CF_DOT         = 12
    ARC_DOT        = 8
    ZZ_DOT         = 8
    LAT_DOT        = 9
    IGN_DOT        = 9
    FAN_DOT        = 11

    SWEEP_TELE_MS      = 1000
    SWEEP_LANES        = 5
    SWEEP_SPACING      = int(230 * PLAYER_VIEW_SCALE)
    SWEEP_WIDTH        = int(40  * PLAYER_VIEW_SCALE)
    SWEEP_RESIDUAL_MS  = 1800
    SWEEP_DIRS         = ("H", "V")

    CF_TELE_MS   = 650
    CF_WIDTH     = int(56 * PLAYER_VIEW_SCALE)
    CF_PERSIST   = 800

    GRID_TELE_MS   = 1000
    GRID_CELL      = int(350 * PLAYER_VIEW_SCALE)
    GRID_WIDTH     = int(30  * PLAYER_VIEW_SCALE)
    GRID_PERSIST   = 2200

    ROTOR_TELE_MS   = 900
    ROTOR_SPOKES    = 6
    ROTOR_WIDTH     = int(28  * PLAYER_VIEW_SCALE)
    ROTOR_SPIN_MS   = 5400
    ROTOR_ANG_SPD   = 0.2 * math.pi

    ZZ_TELE_MS      = 850
    ZZ_SEGS         = 6
    ZZ_SEG_LEN      = int(240 * PLAYER_VIEW_SCALE)
    ZZ_WIDTH        = int(38  * PLAYER_VIEW_SCALE)
    ZZ_RESIDUAL_MS  = 1700

    FAN_TELE_MS     = 800
    FAN_COUNT       = 5
    FAN_SPREAD_DEG  = 60
    FAN_WIDTH       = int(44 * PLAYER_VIEW_SCALE)
    FAN_RESIDUAL_MS = 1700

    ARC_TELE_MS     = 900
    ARC_COUNT       = 3
    ARC_RADIUS_BASE = int(220 * PLAYER_VIEW_SCALE)
    ARC_RADIUS_STEP = int(120 * PLAYER_VIEW_SCALE)
    ARC_SPAN_DEG    = 60
    ARC_WIDTH       = int(36  * PLAYER_VIEW_SCALE)
    ARC_RESIDUAL_MS = 1700

    LAT_TELE_MS     = 900
    LAT_CELL        = int(180 * PLAYER_VIEW_SCALE)
    LAT_WIDTH       = int(30  * PLAYER_VIEW_SCALE)
    LAT_OFFSET      = int(80  * PLAYER_VIEW_SCALE)
    LAT_PERSIST     = 2000

    IGN_TELE_MS     = 800
    IGN_WIDTH       = int(40 * PLAYER_VIEW_SCALE)
    IGN_IGNITE_MS   = 500
    IGN_RESIDUAL_MS = 1500

    ENRAGE_AT_FRAC  = 0.5
    DROP_2_3_THRESH = 2/3
    DROP_1_3_THRESH = 1/3

    BEAM_JITTER_MAX = 10
    BEAM_SEG_LEN    = int(240 * PLAYER_VIEW_SCALE)
    BEAM_PULSE_MS   = 420
    COL_OUTER = (255, 40, 40, 70)
    COL_GLOW  = (255, 90, 90, 110)
    COL_CORE  = (255, 240, 240, 220)

    BASE_IDLE_GAP_MS = 1100
    PATTERN_COOLDOWN_MS = {
        "SWEEP": 500,
        "CF":    250,
        "GRID":  350,
        "ROTOR": 500,
        "ZZ":    300,
        "FAN":   250,
        "ARC":   300,
        "LAT":   350,
        "IGN":   250,
    }
    ENRAGE_CD_SCALE = 1.0

    def __init__(self, world_x, world_y, images, sounds, map_width, map_height,
                 damage_player_fn=None, kill_callback=None, rank=rank):
        import pygame
        super().__init__(world_x, world_y, images, sounds, map_width, map_height,
                         speed=self.SPEED, near_threshold=0, far_threshold=0,
                         radius=self.RADIUS, push_strength=0.10, alert_duration=0,
                         damage_player_fn=damage_player_fn, rank=rank)

        self.image_original = images["boss6"]
        self.image = self.image_original

        self.hp = self.HP_MAX
        self.max_hp = self.HP_MAX
        self.enraged = False

        self._my_minions = []
        self._next_summon = pygame.time.get_ticks() + 1200
        self._pending_summons = []

        self._state = "IDLE"      # IDLE / TELE / RECOVER
        self._pattern = None
        self._state_t0 = pygame.time.get_ticks()
        self._tele_data = None
        self._hazards  = []
        self._last_tick_damage = 0
        self._laser_damage_accum = 0.0

        self.facing_angle = 0.0
        self._strafe_dir = 1
        self.kill_callback = kill_callback

        self._seed = random.random() * 1000.0
        self._images_dict = images
        self._sounds_dict = sounds

        self._drop_2_3_done = False
        self._drop_1_3_done = False

        self._fx_rings = []

        self._next_pattern_ready_at = 0

        self._last_summon_ms = pygame.time.get_ticks() + 2000

    # 사운드
    def _play_sound(self, key, volume=1.0):
        s = self._sounds_dict.get(key) if hasattr(self, "_sounds_dict") else None
        if not s: return
        try: s.set_volume(volume)
        except Exception: pass
        try: s.play()
        except Exception: pass

    # 유틸
    def _player_center(self, player_rect, world_x, world_y):
        return (world_x + player_rect.centerx, world_y + player_rect.centery)

    def _alive_minions(self):
        alive = 0
        for m in list(self._my_minions):
            if getattr(m, "alive", False) and getattr(m, "hp", 1) > 0:
                alive += 1
            else:
                try: self._my_minions.remove(m)
                except Exception: pass
        return alive

    def _iter_enemy_classes(self):
        # ENEMY_CLASSES가 dict/list/tuple로 존재하는 경우 우선 사용
        try:
            from ai import ENEMY_CLASSES
        except Exception:
            ENEMY_CLASSES = None
        cand = []
        if ENEMY_CLASSES:
            if isinstance(ENEMY_CLASSES, dict):
                cand.extend([v for v in ENEMY_CLASSES.values() if v])
            elif isinstance(ENEMY_CLASSES, (list, tuple)):
                cand.extend([v for v in ENEMY_CLASSES if v])
        # 백업: 전역 네임스페이스에서 Enemy* 수집
        g = globals()
        for k, v in g.items():
            if isinstance(v, type) and k.startswith("Enemy"):
                cand.append(v)
        return cand

    def _choose_minion_class(self, low_rank, high_rank):
        candidates = []
        for cls in self._iter_enemy_classes():
            try:
                r = getattr(cls, "rank", 1)
                if getattr(cls, "__name__", "").startswith("Boss"): 
                    continue
                if low_rank <= r <= high_rank:
                    candidates.append(cls)
            except Exception:
                continue
        return random.choice(candidates) if candidates else None

    def _spawn_minion_at(self, x, y, low_r, high_r):
        cls = self._choose_minion_class(low_r, high_r)
        if not cls: return None
        m = None
        # 다양한 생성자 시그니처 대응
        try:
            m = cls(x, y, self._images_dict, self._sounds_dict,
                    self.map_width, self.map_height,
                    damage_player_fn=self.damage_player)
        except Exception:
            try:
                m = cls(x, y, self._images_dict, self._sounds_dict,
                        self.map_width, self.map_height)
            except Exception:
                try:
                    m = cls(x, y, self._images_dict, self._sounds_dict)
                except Exception:
                    return None
        try: setattr(m, "summoned_by", self)
        except Exception: pass
        try:
            if not hasattr(config, "all_enemies"): config.all_enemies = []
            config.all_enemies.append(m)
        except Exception:
            pass
        self._my_minions.append(m)
        return m

    def _schedule_summons(self, count, low_r, high_r):
        import pygame
        slots = max(0, (self.MINION_CAP_ENRAGE if self.enraged else self.MINION_CAP_BASE)
                       - (self._alive_minions() + len(self._pending_summons)))
        if slots <= 0: return
        n = min(count, slots)
        px, py = self.world_x, self.world_y
        now = pygame.time.get_ticks()
        for _ in range(n):
            r = random.randint(self.SUMMON_RING_MIN, self.SUMMON_RING_MAX)
            ang = random.uniform(0, 2*math.pi)
            sx = min(max(0, px + math.cos(ang)*r), self.map_width)
            sy = min(max(0, py + math.sin(ang)*r), self.map_height)
            self._pending_summons.append({"x":sx, "y":sy, "t0": now, "low":low_r, "high":high_r})
            # 텔레 이펙트 시작(화려한 링)
            self._fx_rings.append((sx, sy, now, self.SUMMON_CAST_MS))

    def _process_pending_summons(self):
        import pygame
        now = pygame.time.get_ticks()
        rest = []
        for s in self._pending_summons:
            if now - s["t0"] >= self.SUMMON_CAST_MS:
                self._spawn_minion_at(s["x"], s["y"], s["low"], s["high"])
                self._play_sound("spawn_enemy", 0.9)
                # 여운 링
                self._fx_rings.append((s["x"], s["y"], now, 600))
            else:
                rest.append(s)
        self._pending_summons = rest

    # 드랍
    def _heavy_drop(self, scale=1):
        try:
            if hasattr(self, "spawn_dropped_items"):
                self.spawn_dropped_items(8*scale, 10*scale)
            elif hasattr(config, "spawn_heavy_orbs"):
                config.spawn_heavy_orbs(self.world_x, self.world_y, count=max(1, scale))
            elif hasattr(config, "spawn_orbs"):
                config.spawn_orbs(self.world_x, self.world_y, amount=15*max(1,scale))
        except Exception:
            pass

    # 기하 유틸
    @staticmethod
    def _dist_point_to_segment(px, py, x1, y1, x2, y2):
        vx, vy = x2 - x1, y2 - y1
        wx, wy = px - x1, py - y1
        c1 = vx * wx + vy * wy
        if c1 <= 0:   return math.hypot(px - x1, py - y1)
        c2 = vx * vx + vy * vy
        if c2 <= c1:  return math.hypot(px - x2, py - y2)
        b = c1 / c2
        bx, by = x1 + b * vx, y1 + b * vy
        return math.hypot(px - bx, py - by)

    @staticmethod
    def _dist_point_to_polyline(px, py, pts):
        dmin = 1e9
        for i in range(len(pts)-1):
            x1,y1 = pts[i]; x2,y2 = pts[i+1]
            d = Boss6._dist_point_to_segment(px,py,x1,y1,x2,y2)
            if d < dmin: dmin = d
        return dmin

    @staticmethod
    def _clamp_angle(a):
        while a < -math.pi: a += 2*math.pi
        while a >  math.pi: a -= 2*math.pi
        return a

    @staticmethod
    def _dist_point_to_arc(px, py, cx, cy, r, a0, a1):
        ang = math.atan2(py - cy, px - cx)
        a0n = Boss6._clamp_angle(a0); a1n = Boss6._clamp_angle(a1)
        def ang_in(ang, a, b):
            ang = Boss6._clamp_angle(ang)
            a = Boss6._clamp_angle(a); b = Boss6._clamp_angle(b)
            if a <= b: return a <= ang <= b
            return ang >= a or ang <= b
        if ang_in(ang, a0n, a1n):
            nearest_ang = ang
        else:
            d0 = abs(Boss6._clamp_angle(ang - a0n))
            d1 = abs(Boss6._clamp_angle(ang - a1n))
            nearest_ang = a0n if d0 < d1 else a1n
        qx = cx + math.cos(nearest_ang)*r
        qy = cy + math.sin(nearest_ang)*r
        return math.hypot(px - qx, py - qy)

    def _max_ray_len(self):
        return math.hypot(self.map_width, self.map_height) + 200

    # 패턴 빌더
    def _build_sweep(self):
        orientation = random.choice(self.SWEEP_DIRS)
        lanes = self.SWEEP_LANES
        spacing = self.SWEEP_SPACING
        width = self.SWEEP_WIDTH
        if orientation == "H":
            base = random.randint(int(120*PLAYER_VIEW_SCALE), self.map_height - int(120*PLAYER_VIEW_SCALE))
            lanes_vals = [base + (i - lanes//2)*spacing for i in range(lanes)]
        else:
            base = random.randint(int(120*PLAYER_VIEW_SCALE), self.map_width - int(120*PLAYER_VIEW_SCALE))
            lanes_vals = [base + (i - lanes//2)*spacing for i in range(lanes)]
        return {"type":"SWEEP","ori":orientation,"lanes":lanes_vals,"width":width,"tele_ms":self.SWEEP_TELE_MS}

    def _build_crossfire(self, cx, cy):
        return {"type":"CF","cx":cx,"cy":cy,"width":self.CF_WIDTH,"tele_ms":self.CF_TELE_MS}

    def _build_grid(self):
        ang0 = random.uniform(0, 2*math.pi)
        return {"type":"GRID","cx":self.world_x,"cy":self.world_y,"ang":ang0,
                "cell":self.GRID_CELL,"width":self.GRID_WIDTH,
                "tele_ms":self.GRID_TELE_MS,"persist":self.GRID_PERSIST}

    def _build_rotors(self, cx, cy):
        return {"type":"ROTOR","cx":cx,"cy":cy,"r":self._max_ray_len(),
                "spokes":self.ROTOR_SPOKES,"width":self.ROTOR_WIDTH,
                "tele_ms":self.ROTOR_TELE_MS,"spin_ms":self.ROTOR_SPIN_MS,
                "ang_spd":self.ROTOR_ANG_SPD,"ang0":random.uniform(0, 2*math.pi)}

    def _build_zigzag(self):
        orient = random.choice(("H","V"))
        pts = []
        if orient == "H":
            y = random.randint(int(150*PLAYER_VIEW_SCALE), self.map_height - int(150*PLAYER_VIEW_SCALE))
            x = 0
            dir_y = 1
            pts.append((x, y))
            for _ in range(self.ZZ_SEGS):
                x = min(self.map_width, x + self.ZZ_SEG_LEN)
                y = max(int(80*PLAYER_VIEW_SCALE),
                        min(self.map_height - int(80*PLAYER_VIEW_SCALE), y + dir_y*self.ZZ_SEG_LEN//2))
                pts.append((x, y))
                dir_y *= -1
        else:
            x = random.randint(int(150*PLAYER_VIEW_SCALE), self.map_width - int(150*PLAYER_VIEW_SCALE))
            y = 0
            dir_x = 1
            pts.append((x, y))
            for _ in range(self.ZZ_SEGS):
                y = min(self.map_height, y + self.ZZ_SEG_LEN)
                x = max(int(80*PLAYER_VIEW_SCALE),
                        min(self.map_width - int(80*PLAYER_VIEW_SCALE), x + dir_x*self.ZZ_SEG_LEN//2))
                pts.append((x, y))
                dir_x *= -1
        return {"type":"ZZ","pts":pts,"width":self.ZZ_WIDTH,"tele_ms":self.ZZ_TELE_MS}

    def _build_fan(self):
        count = self.FAN_COUNT
        spread = math.radians(self.FAN_SPREAD_DEG)
        base_ang = random.uniform(0, 2*math.pi)
        if count <= 1:
            angs = [base_ang]
        else:
            step = spread / (count - 1)
            angs = [base_ang - spread*0.5 + i*step for i in range(count)]
        return {"type":"FAN","cx":self.world_x,"cy":self.world_y,"angs":angs,
                "width":self.FAN_WIDTH,"tele_ms":self.FAN_TELE_MS}

    def _build_arcs(self):
        base_ang = random.uniform(0, 2*math.pi)
        span = math.radians(self.ARC_SPAN_DEG)
        arcs = []
        for i in range(self.ARC_COUNT):
            r = self.ARC_RADIUS_BASE + i*self.ARC_RADIUS_STEP
            a0 = base_ang - span*0.5
            a1 = base_ang + span*0.5
            arcs.append((r, a0, a1))
        return {"type":"ARC","cx":self.world_x,"cy":self.world_y,
                "arcs":arcs,"width":self.ARC_WIDTH,"tele_ms":self.ARC_TELE_MS}

    def _build_lattice(self):
        ang = random.choice((0, math.pi/2))
        return {"type":"LAT","cx":self.world_x,"cy":self.world_y,"ang":ang,
                "cell":self.LAT_CELL,"offset":self.LAT_OFFSET,
                "width":self.LAT_WIDTH,"tele_ms":self.LAT_TELE_MS,"persist":self.LAT_PERSIST}

    def _build_ignite(self):
        ori = random.choice(("H","V"))
        if ori == "H":
            y = random.randint(int(120*PLAYER_VIEW_SCALE), self.map_height - int(120*PLAYER_VIEW_SCALE))
            return {"type":"IGN","x1":0,"y1":y,"x2":self.map_width,"y2":y,
                    "width":self.IGN_WIDTH,"tele_ms":self.IGN_TELE_MS}
        else:
            x = random.randint(int(120*PLAYER_VIEW_SCALE), self.map_width - int(120*PLAYER_VIEW_SCALE))
            return {"type":"IGN","x1":x,"y1":0,"x2":x,"y2":self.map_height,
                    "width":self.IGN_WIDTH,"tele_ms":self.IGN_TELE_MS}

    # 상태 전이
    def _enter(self, state, pattern=None, tele_data=None):
        import pygame
        self._state = state
        if pattern is not None:
            self._pattern = pattern
        now = pygame.time.get_ticks()
        self._state_t0 = now
        if tele_data is not None:
            self._tele_data = tele_data
        # RECOVER로 진입하는 시점에 다음 패턴 허용 시간을 산출
        if state == "RECOVER":
            base = self.BASE_IDLE_GAP_MS
            extra = self.PATTERN_COOLDOWN_MS.get(self._pattern or "", 0)
            scale = (self.ENRAGE_CD_SCALE if self.enraged else 1.0)
            self._next_pattern_ready_at = now + int((base + extra) * scale)

    def _ready_new_pattern(self):
        import pygame
        # IDLE 상태이면서, 계산된 '다음 패턴 허용 시각'에 도달해야 시작
        return (self._state == "IDLE") and (pygame.time.get_ticks() >= self._next_pattern_ready_at)

    # 발동
    def _fire_pattern(self):
        import pygame
        now = pygame.time.get_ticks()
        t = self._tele_data
        if not t:
            self._enter("RECOVER")
            return

        # 발사 사운드(패턴당 1회)
        self._play_sound("shock_burst", 0.9)

        if t["type"] == "SWEEP":
            hazards = []
            w = t["width"]
            if t["ori"] == "H":
                for y in t["lanes"]:
                    hazards.append({"kind":"line_static","x1":0,"y1":y,"x2":self.map_width,"y2":y,
                                    "w":w,"expire":now + self.SWEEP_RESIDUAL_MS,"dps":self.SWEEP_DOT,"t0":now})
            else:
                for x in t["lanes"]:
                    hazards.append({"kind":"line_static","x1":x,"y1":0,"x2":x,"y2":self.map_height,
                                    "w":w,"expire":now + self.SWEEP_RESIDUAL_MS,"dps":self.SWEEP_DOT,"t0":now})
            self._hazards.extend(hazards)

        elif t["type"] == "CF":
            w = t["width"]; cx, cy = t["cx"], t["cy"]
            self._hazards.append({"kind":"line_static","x1":0,"y1":cy,"x2":self.map_width,"y2":cy,
                                  "w":w,"expire":now + self.CF_PERSIST,"dps":self.CF_DOT,"t0":now})
            self._hazards.append({"kind":"line_static","x1":cx,"y1":0,"x2":cx,"y2":self.map_height,
                                  "w":w,"expire":now + self.CF_PERSIST,"dps":self.CF_DOT,"t0":now})

        elif t["type"] == "GRID":
            ang = t["ang"]; cell = t["cell"]; w = t["width"]; expire = now + t["persist"]
            lines = []
            L = self._max_ray_len()
            for axis in (ang, ang + math.pi/2):
                step = cell
                for offset in range(-max(self.map_width, self.map_height),
                                    max(self.map_width, self.map_height)+1, step):
                    cx, cy = t["cx"], t["cy"]
                    nx, ny = math.cos(axis + math.pi/2), math.sin(axis + math.pi/2)
                    ox, oy = cx + nx*offset, cy + ny*offset
                    dx, dy = math.cos(axis), math.sin(axis)
                    x1, y1 = ox - dx*L, oy - dy*L
                    x2, y2 = ox + dx*L, oy + dy*L
                    lines.append({"kind":"line_static","x1":x1,"y1":y1,"x2":x2,"y2":y2,
                                  "w":w,"expire":expire,"dps":self.GRID_DOT,"t0":now})
            self._hazards.extend(lines)

        elif t["type"] == "ROTOR":
            self._hazards.append({
                "kind":"rotor","cx":t["cx"],"cy":t["cy"],"r":t["r"],
                "w":t["width"],"spokes":t["spokes"],"ang0":t["ang0"],"ang_spd":t["ang_spd"],
                "t0":now,"duration":t["spin_ms"],"dps":self.ROTOR_DOT
            })

        elif t["type"] == "ZZ":
            self._hazards.append({
                "kind":"polyline_static","pts":t["pts"],"w":t["width"],
                "expire":now + self.ZZ_RESIDUAL_MS,"dps":self.ZZ_DOT,"t0":now
            })

        elif t["type"] == "FAN":
            L = self._max_ray_len()
            for ang in t["angs"]:
                x2 = t["cx"] + math.cos(ang)*L
                y2 = t["cy"] + math.sin(ang)*L
                self._hazards.append({
                    "kind":"line_static","x1":t["cx"],"y1":t["cy"],"x2":x2,"y2":y2,
                    "w":t["width"],"expire":now + self.FAN_RESIDUAL_MS,"dps":self.FAN_DOT,"t0":now
                })

        elif t["type"] == "ARC":
            for (r, a0, a1) in t["arcs"]:
                self._hazards.append({
                    "kind":"arc_static","cx":t["cx"],"cy":t["cy"],"r":r,
                    "a0":a0,"a1":a1,"w":t["width"],
                    "expire":now + self.ARC_RESIDUAL_MS,"dps":self.ARC_DOT,"t0":now
                })

        elif t["type"] == "LAT":
            ang = t["ang"]; cell = t["cell"]; off = t["offset"]; w = t["width"]
            expire = now + self.LAT_PERSIST
            lines = []
            L = self._max_ray_len()
            step = cell
            for axis in (ang, ang + math.pi/2):
                for k, offset in enumerate(range(-max(self.map_width, self.map_height),
                                                 max(self.map_width, self.map_height)+1, step)):
                    cx, cy = t["cx"], t["cy"]
                    nx, ny = math.cos(axis + math.pi/2), math.sin(axis + math.pi/2)
                    ox, oy = cx + nx*offset, cy + ny*offset
                    dx, dy = math.cos(axis), math.sin(axis)
                    if axis != ang:
                        ox += (-dy) * off * (1 if (k % 2 == 0) else -1)
                        oy += ( dx) * off * (1 if (k % 2 == 0) else -1)
                    x1, y1 = ox - dx*L, oy - dy*L
                    x2, y2 = ox + dx*L, oy + dy*L
                    lines.append({"kind":"line_static","x1":x1,"y1":y1,"x2":x2,"y2":y2,
                                  "w":w,"expire":expire,"dps":self.LAT_DOT,"t0":now})
            self._hazards.extend(lines)

        elif t["type"] == "IGN":
            self._hazards.append({
                "kind":"ignite_line","x1":t["x1"],"y1":t["y1"],"x2":t["x2"],"y2":t["y2"],
                "w":t["width"],"ignite_ms":self.IGN_IGNITE_MS,
                "expire": now + self.IGN_IGNITE_MS + self.IGN_RESIDUAL_MS,
                "dps": self.IGN_DOT, "t0": now
            })

        self._enter("RECOVER")

    # 업데이트
    def update(self, dt, world_x, world_y, player_rect, enemies=[]):
        import pygame
        if not self.alive: return

        px, py = self._player_center(player_rect, world_x, world_y)
        self.facing_angle = math.atan2(py - self.world_y, px - self.world_x)

        # 중간 드랍
        if not self._drop_2_3_done and self.hp <= int(self.HP_MAX * self.DROP_2_3_THRESH):
            self._heavy_drop(scale=1); self._drop_2_3_done = True
        if not self._drop_1_3_done and self.hp <= int(self.HP_MAX * self.DROP_1_3_THRESH):
            self._heavy_drop(scale=1); self._drop_1_3_done = True

        if not self.enraged and self.hp <= self.HP_MAX * self.ENRAGE_AT_FRAC:
            self.enraged = True

        now = pygame.time.get_ticks()

        # 소환: 쿨타임 도달 시 예약
        cap = self.MINION_CAP_ENRAGE if self.enraged else self.MINION_CAP_BASE
        if (self._alive_minions() + len(self._pending_summons)) < cap and now >= self._next_summon:
            low, high = (3,5) if self.enraged else (1,4)
            self._schedule_summons(self.SUMMON_BURST, low, high)
            cd = self.SUMMON_CD_ENRAGE if self.enraged else self.SUMMON_CD_BASE
            self._next_summon = now + cd
        self._process_pending_summons()

        # 해저드 피해 처리 (프레임 단위로 부드럽게 적용)
        dt_ms = max(1, now - self._last_tick_damage)
        self._last_tick_damage = now
        frame_accum = 0.0

        new_haz = []
        for hz in self._hazards:
            alive = True
            kind = hz['kind']

            if kind == 'line_static':
                if now <= hz['expire']:
                    d = self._dist_point_to_segment(px, py, hz['x1'], hz['y1'], hz['x2'], hz['y2'])
                    if d <= hz['w'] * 0.5:
                        frame_accum += hz['dps'] * (dt_ms / 1000.0)
                else:
                    alive = False

            elif kind == 'polyline_static':
                if now <= hz['expire']:
                    d = self._dist_point_to_polyline(px, py, hz['pts'])
                    if d <= hz['w'] * 0.5:
                        frame_accum += hz['dps'] * (dt_ms / 1000.0)
                else:
                    alive = False

            elif kind == 'arc_static':
                if now <= hz['expire']:
                    d = self._dist_point_to_arc(px, py, hz['cx'], hz['cy'], hz['r'], hz['a0'], hz['a1'])
                    if d <= hz['w'] * 0.5:
                        frame_accum += hz['dps'] * (dt_ms / 1000.0)
                else:
                    alive = False

            elif kind == 'ignite_line':
                if now <= hz['expire']:
                    # 점화 전에는 피해 없음
                    if (now - hz['t0']) >= hz.get('ignite_ms', 0):
                        d = self._dist_point_to_segment(px, py, hz['x1'], hz['y1'], hz['x2'], hz['y2'])
                        if d <= hz['w'] * 0.5:
                            frame_accum += hz['dps'] * (dt_ms / 1000.0)
                else:
                    alive = False

            elif kind == 'rotor':
                tfrac = (now - hz['t0']) / max(1, hz['duration'])
                if tfrac <= 1.0:
                    cur_ang = hz['ang0'] + hz['ang_spd'] * ((now - hz['t0'])/1000.0)
                    for i in range(hz['spokes']):
                        ang = cur_ang + (2*math.pi/float(hz['spokes'])) * i
                        x2 = hz['cx'] + math.cos(ang)*hz['r']
                        y2 = hz['cy'] + math.sin(ang)*hz['r']
                        d = self._dist_point_to_segment(px, py, hz['cx'], hz['cy'], x2, y2)
                        if d <= hz['w'] * 0.5:
                            frame_accum += hz['dps'] * (dt_ms / 1000.0)
                            break
                else:
                    alive = False

            if alive:
                new_haz.append(hz)
        self._hazards = new_haz

        # 누적된 소수 피해를 정수로 적용 (조금만 스쳐도 데미지 들어가도록)
        self._laser_damage_accum += frame_accum
        apply_int = int(self._laser_damage_accum)
        if apply_int > 0:
            try:
                self.damage_player(apply_int)
            except Exception:
                pass
            self._laser_damage_accum -= apply_int

        # 패턴 스케줄
        if self._ready_new_pattern():
            choices = ["SWEEP","CF","GRID","ROTOR","ZZ","FAN","ARC","LAT","IGN"]
            weights = [2, 3, 3, 2, 2, 3, 3, 3, 3]
            pat = random.choices(choices, weights=weights, k=1)[0]
            if     pat == "SWEEP": tele = self._build_sweep()
            elif   pat == "CF":    tele = self._build_crossfire(self.world_x, self.world_y)
            elif   pat == "GRID":  tele = self._build_grid()
            elif   pat == "ROTOR": tele = self._build_rotors(self.world_x, self.world_y)
            elif   pat == "ZZ":    tele = self._build_zigzag()
            elif   pat == "FAN":   tele = self._build_fan()
            elif   pat == "ARC":   tele = self._build_arcs()
            elif   pat == "LAT":   tele = self._build_lattice()
            else:                   tele = self._build_ignite()
            self._enter("TELE", pattern=pat, tele_data=tele)

        # 텔레 → 발동 (tele_ms 누락 대비 기본값 800ms)
        if self._state == "TELE":
            t = self._tele_data
            if t and (now - self._state_t0) >= t.get("tele_ms", 800):
                self._fire_pattern()
        elif self._state == "RECOVER":
            if (now - self._state_t0) >= 400:
                self._enter("IDLE")

        # 포지셔닝
        dist = math.hypot(px - self.world_x, py - self.world_y)
        dx, dy = px - self.world_x, py - self.world_y
        d = dist or 1.0; nx, ny = dx/d, dy/d
        if dist < self.KEEP_MIN:
            self.world_x -= nx * self.speed
            self.world_y -= ny * self.speed
        elif dist > self.KEEP_MAX:
            self.world_x += nx * self.speed
            self.world_y += ny * self.speed
        else:
            ortho = (-ny, nx) if self._strafe_dir > 0 else (ny, -nx)
            self.world_x += ortho[0] * (self.speed * 0.55)
            self.world_y += ortho[1] * (self.speed * 0.55)
            if now % 1200 < 20: self._strafe_dir *= -1

        self.world_x = max(0, min(self.map_width,  self.world_x))
        self.world_y = max(0, min(self.map_height, self.world_y))

    # 레이저 도형(시각효과)
    def _beam_points(self, x1, y1, x2, y2, jitter_amp, seg_len, tsec, seed=0.0):
        dx, dy = x2 - x1, y2 - y1
        L = max(1.0, math.hypot(dx, dy))
        nx, ny = dx / L, dy / L
        px, py = -ny, nx  # 법선
        nseg = max(3, int(L / max(60.0, seg_len)))
        pts = [(x1, y1)]
        for i in range(1, nseg):
            u = i / float(nseg)
            bx = x1 + dx * u
            by = y1 + dy * u
            w = (math.sin((u + seed) * 7.5 + tsec * 5.0) +
                 math.cos((u*1.7 + seed*0.7) * 9.0 - tsec * 3.5)) * 0.5
            off = w * jitter_amp
            pts.append((bx + px * off, by + py * off))
        pts.append((x2, y2))
        return pts

    def _draw_polyline(self, surf, pts, color, width):
        import pygame
        if len(pts) < 2: return
        for i in range(len(pts)-1):
            pygame.draw.line(surf, color, pts[i], pts[i+1], max(1, int(width)))

    def _draw_beam_layered(self, lay, x1, y1, x2, y2, base_w, born_ms):
        import pygame
        now = pygame.time.get_ticks()
        tsec = now * 0.001
        jitter = min(self.BEAM_JITTER_MAX, base_w * 0.45)
        pts = self._beam_points(x1, y1, x2, y2, jitter_amp=jitter,
                                seg_len=self.BEAM_SEG_LEN, tsec=tsec,
                                seed=(born_ms % 997) * 0.001)
        pulse = 0.5 + 0.5 * math.sin((now - born_ms) * (2*math.pi / max(60, self.BEAM_PULSE_MS)))
        core_w  = max(1, int(base_w * (0.55 + 0.15*pulse)))
        glow_w  = max(core_w+2, int(base_w * 1.15))
        outer_w = max(glow_w+2, int(base_w * 1.7))
        self._draw_polyline(lay, pts, self.COL_OUTER, outer_w)
        self._draw_polyline(lay, pts, self.COL_GLOW,  glow_w)
        self._draw_polyline(lay, pts, self.COL_CORE,  core_w)

    def _draw_arc_beam(self, lay, cx, cy, r, a0, a1, base_w, born_ms, seg_ang=0.12):
        ang = a0
        while True:
            anext = min(a1, ang + seg_ang)
            x1 = cx + math.cos(ang)*r
            y1 = cy + math.sin(ang)*r
            x2 = cx + math.cos(anext)*r
            y2 = cy + math.sin(anext)*r
            self._draw_beam_layered(lay, x1, y1, x2, y2, base_w, born_ms)
            if anext >= a1 - 1e-6: break
            ang = anext

    # 드로우
    def draw(self, surface, world_x, world_y, shake_offset_x=0, shake_offset_y=0):
        import pygame
        if not self.alive and self.hp <= 0: return

        W, H = surface.get_width(), surface.get_height()
        sx = self.world_x - world_x
        sy = self.world_y - world_y
        now = pygame.time.get_ticks()

        # 본체
        ang_deg = math.degrees(self.facing_angle) + self.ORIENT_OFFSET_DEG
        rotated = pygame.transform.rotate(self.image_original, -ang_deg)
        surface.blit(rotated, rotated.get_rect(center=(sx, sy)).topleft)

        # 소환 텔레 이펙트(화려한 링/펄스)
        if self._fx_rings:
            fx = pygame.Surface((W, H), pygame.SRCALPHA)
            keep = []
            for (x,y,t0,dur) in self._fx_rings:
                life = (now - t0) / max(1, dur)
                if life <= 1.0:
                    r = int(20 + 80 * life)
                    alpha = int(200 * (1.0 - life))
                    pygame.draw.circle(fx, (80,120,255, max(40,alpha//2)), (int(x - world_x), int(y - world_y)), r, width=3)
                    pygame.draw.circle(fx, (180,220,255, max(30,alpha//3)), (int(x - world_x), int(y - world_y)), max(1,r//2), width=2)
                    keep.append((x,y,t0,dur))
            self._fx_rings = keep
            surface.blit(fx, (0,0))

        # 텔레그래프(정지 표시)
        if self._state == "TELE" and self._tele_data:
            t = self._tele_data
            tel = pygame.Surface((W, H), pygame.SRCALPHA)
            if t["type"] == "SWEEP":
                if t["ori"] == "H":
                    for y in t["lanes"]:
                        pygame.draw.line(tel, (255, 60, 60, 70),
                                         (0, y - world_y), (W, y - world_y),
                                         max(4, t["width"]//2))
                else:
                    for x in t["lanes"]:
                        pygame.draw.line(tel, (255, 60, 60, 70),
                                         (x - world_x, 0), (x - world_x, H),
                                         max(4, t["width"]//2))

            elif t["type"] == "CF":
                w = t["width"]
                pygame.draw.rect(tel, (255, 60, 60, 75),
                                 pygame.Rect(0, t["cy"] - w*0.5 - world_y, W, w))
                pygame.draw.rect(tel, (255, 60, 60, 75),
                                 pygame.Rect(t["cx"] - w*0.5 - world_x, 0, w, H))

            elif t["type"] == "GRID":
                a = t["ang"]; cx = t["cx"] - world_x; cy = t["cy"] - world_y
                L = self._max_ray_len()
                for axis in (a, a + math.pi/2):
                    step = t["cell"]
                    for offset in range(-max(self.map_width, self.map_height),
                                        max(self.map_width, self.map_height)+1, step):
                        nx, ny = math.cos(axis + math.pi/2), math.sin(axis + math.pi/2)
                        ox, oy = cx + nx*offset, cy + ny*offset
                        dx, dy = math.cos(axis), math.sin(axis)
                        x1, y1 = ox - dx*L, oy - dy*L
                        x2, y2 = ox + dx*L, oy + dy*L
                        pygame.draw.line(tel, (255, 60, 60, 70), (x1,y1), (x2,y2), max(4, t["width"]//2))

            elif t["type"] == "ROTOR":
                cx = t["cx"] - world_x; cy = t["cy"] - world_y
                a = t["ang0"]
                L = t["r"]
                for i in range(t["spokes"]):
                    ang = a + (2*math.pi/float(t["spokes"])) * i
                    x2 = cx + math.cos(ang)*L
                    y2 = cy + math.sin(ang)*L
                    pygame.draw.line(tel, (255, 60, 60, 70), (cx, cy), (x2, y2), max(4, t["width"]//2))

            elif t["type"] == "ZZ":
                for i in range(len(t["pts"]) - 1):
                    x1,y1 = t["pts"][i]
                    x2,y2 = t["pts"][i+1]
                    pygame.draw.line(tel, (255, 60, 60, 70),
                                     (x1 - world_x, y1 - world_y),
                                     (x2 - world_x, y2 - world_y),
                                     max(4, t["width"]//2))

            elif t["type"] == "FAN":
                cx = t["cx"] - world_x; cy = t["cy"] - world_y
                L = self._max_ray_len()
                for ang in t["angs"]:
                    x2 = cx + math.cos(ang)*L
                    y2 = cy + math.sin(ang)*L
                    pygame.draw.line(tel, (255,60,60,70), (cx,cy), (x2,y2), max(4, t["width"]//2))

            elif t["type"] == "ARC":
                cx = t["cx"] - world_x; cy = t["cy"] - world_y
                for (r,a0,a1) in t["arcs"]:
                    ang = a0
                    while True:
                        anext = min(a1, ang + 0.18)
                        x1 = cx + math.cos(ang)*r
                        y1 = cy + math.sin(ang)*r
                        x2 = cx + math.cos(anext)*r
                        y2 = cy + math.sin(anext)*r
                        pygame.draw.line(tel, (255,60,60,70), (x1,y1), (x2,y2), max(4, t["width"]//2))
                        if anext >= a1 - 1e-6: break
                        ang = anext

            elif t["type"] == "LAT":
                a = t["ang"]; cx = t["cx"] - world_x; cy = t["cy"] - world_y
                L = self._max_ray_len()
                step = t["cell"]; off = t["offset"]
                for axis in (a, a + math.pi/2):
                    for k, offset in enumerate(range(-max(self.map_width, self.map_height),
                                                     max(self.map_width, self.map_height)+1, step)):
                        nx, ny = math.cos(axis + math.pi/2), math.sin(axis + math.pi/2)
                        ox, oy = cx + nx*offset, cy + ny*offset
                        dx, dy = math.cos(axis), math.sin(axis)
                        if axis != a:
                            ox += (-dy) * off * (1 if (k % 2 == 0) else -1)
                            oy += ( dx) * off * (1 if (k % 2 == 0) else -1)
                        x1, y1 = ox - dx*L, oy - dy*L
                        x2, y2 = ox + dx*L, oy + dy*L
                        pygame.draw.line(tel, (255,60,60,70), (x1,y1), (x2,y2), max(4, t["width"]//2))

            elif t["type"] == "IGN":
                x1,y1,x2,y2 = t["x1"]-world_x, t["y1"]-world_y, t["x2"]-world_x, t["y2"]-world_y
                L = max(1.0, math.hypot(x2-x1, y2-y1))
                seg = 40; gap = 30
                vx, vy = (x2-x1)/L, (y2-y1)/L
                s = 0.0
                while s < L:
                    e = min(L, s + seg)
                    sx1, sy1 = x1 + vx*s, y1 + vy*s
                    sx2, sy2 = x1 + vx*e, y1 + vy*e
                    pygame.draw.line(tel, (255,60,60,70), (sx1,sy1), (sx2,sy2), max(4,  self.IGN_WIDTH//2))
                    s = e + gap

            surface.blit(tel, (0, 0))

        # 실제 레이저(3중 레이어 + 지그재그 궤적)
        if self._hazards:
            lay = pygame.Surface((W, H), pygame.SRCALPHA)
            for hz in self._hazards:
                k = hz["kind"]
                if k == "line_static":
                    x1 = hz["x1"] - world_x; y1 = hz["y1"] - world_y
                    x2 = hz["x2"] - world_x; y2 = hz["y2"] - world_y
                    self._draw_beam_layered(lay, x1, y1, x2, y2, base_w=hz["w"], born_ms=hz.get("t0", now))

                elif k == "polyline_static":
                    pts = [(x-world_x, y-world_y) for (x,y) in hz["pts"]]
                    for i in range(len(pts)-1):
                        x1,y1 = pts[i]; x2,y2 = pts[i+1]
                        self._draw_beam_layered(lay, x1, y1, x2, y2, base_w=hz["w"], born_ms=hz.get("t0", now))

                elif k == "arc_static":
                    cx = hz["cx"] - world_x; cy = hz["cy"] - world_y
                    self._draw_arc_beam(lay, cx, cy, hz["r"], hz["a0"], hz["a1"], hz["w"], hz.get("t0", now))

                elif k == "ignite_line":
                    x1 = hz["x1"] - world_x; y1 = hz["y1"] - world_y
                    x2 = hz["x2"] - world_x; y2 = hz["y2"] - world_y
                    Lx = x2 - x1; Ly = y2 - y1
                    L = max(1.0, math.hypot(Lx, Ly))
                    frac = min(1.0, max(0.0, (now - hz["t0"]) / max(1, hz["ignite_ms"])))
                    vx, vy = Lx / L, Ly / L
                    tx = x1 + vx * (L * frac)
                    ty = y1 + vy * (L * frac)
                    self._draw_beam_layered(lay, x1, y1, tx, ty, base_w=hz["w"], born_ms=hz["t0"])

                elif k == "rotor":
                    cur_ang = hz["ang0"] + hz["ang_spd"] * ((now - hz["t0"])/1000.0)
                    cx = hz["cx"] - world_x; cy = hz["cy"] - world_y
                    for i in range(hz["spokes"]):
                        ang = cur_ang + (2*math.pi/float(hz["spokes"])) * i
                        x2 = cx + math.cos(ang)*hz["r"]
                        y2 = cy + math.sin(ang)*hz["r"]
                        self._draw_beam_layered(lay, cx, cy, x2, y2, base_w=hz["w"], born_ms=hz["t0"])

            surface.blit(lay, (0, 0))

    # 피격/드랍/사망
    def hit(self, damage, blood_effects, force=False):
        prev_hp = self.hp
        thr66 = self.max_hp * (2.0/3.0)
        thr33 = self.max_hp * (1.0/3.0)
        super().hit(damage, blood_effects, force)
        if self.alive:
            if (not self._drop_2_3_done) and prev_hp > thr66 and self.hp <= thr66:
                self._drop_2_3_done = True
                self._heavy_drop(scale=1)
            if (not self._drop_1_3_done) and prev_hp > thr33 and self.hp <= thr33:
                self._drop_1_3_done = True
                self._heavy_drop(scale=1)

    def die(self, blood_effects):
        self._hazards.clear()
        self._heavy_drop(scale=2)
        super().die(blood_effects)

class Boss7(AIBase):

    rank   = 10
    HP_MAX = 4500
    RADIUS = int(52 * PLAYER_VIEW_SCALE)
    SPEED  = 0.0
    ORIENT_OFFSET_DEG = 270

    MINION_CAP_BASE   = 5
    MINION_CAP_ENRAGE = 7
    SUMMON_BURST      = 2
    SUMMON_CD_BASE    = 8000 + 5000
    SUMMON_CD_ENRAGE  = 6000 + 5000
    SUMMON_CAST_MS    = 1200
    SUMMON_RING_MIN   = int(300 * PLAYER_VIEW_SCALE)
    SUMMON_RING_MAX   = int(520 * PLAYER_VIEW_SCALE)

    PHASE2_AT_FRAC = 0.70
    PHASE3_AT_FRAC = 0.35
    ENRAGE_AT_FRAC = PHASE3_AT_FRAC

    BASE_IDLE_GAP_MS = 900
    PATTERN_COOLDOWN_MS = {
        "X_SWEEP": 300, "CHECKER": 350, "RING1": 300,
        "SWEEP8": 350, "CHECKER2": 350, "RING2": 350,
        "CUTS": 400,   "WEDGE": 400,   "CATA": 500,
        "TRIDENT_S": 400, "TRIDENT": 450,
        "RIPPLE": 350, "CROSS": 320, "TRIDENT5_S": 420, "TRIDENT5": 460,
        "ZZ_ROTOR": 380, "BARS": 380, "WAVE_RECT": 360, "SNIPER": 420,
    }
    ENRAGE_CD_SCALE = 1.0

    LASER_TICK_MS = 200
    DOT_WEAK = 7
    DOT_MED  = 11
    DOT_STR  = 14
    DOT_SNIPER = 22

    BEAM_WIDTH_S  = int(34 * PLAYER_VIEW_SCALE)
    BEAM_WIDTH_M  = int(44 * PLAYER_VIEW_SCALE)
    BEAM_WIDTH_L  = int(56 * PLAYER_VIEW_SCALE)
    BEAM_WIDTH_XL = int(72 * PLAYER_VIEW_SCALE)
    RING_WIDTH_S  = int(24 * PLAYER_VIEW_SCALE)
    RING_WIDTH_M  = int(32 * PLAYER_VIEW_SCALE)
    RING_WIDTH_L  = int(40 * PLAYER_VIEW_SCALE)

    CHECKER_ROWS = 4
    CHECKER_COLS = 6
    CHECKER_TEL_MS = 4600
    CHECKER_BLAST_ONETIME = 35
    CHECKER_RESIDUAL_DOT  = 5

    RING_TEL_MS = 500
    RING1_MS    = 2500
    RING2_MS    = 2800
    RING3_MS    = 3200
    RING_SPEED_SCALE = 1.6667

    COL_OUTER = (255, 60, 60, 70)
    COL_GLOW  = (140, 190, 255, 110)
    COL_CORE  = (10, 10, 10, 220)

    BEAM_PULSE_MS   = 2600
    BEAM_JITTER_MAX = int(20 * PLAYER_VIEW_SCALE)
    BEAM_SEG_LEN    = int(180 * PLAYER_VIEW_SCALE)

    LASER_FADE_IN_MS  = 180
    LASER_FADE_OUT_MS = 240

    SAFE_TINT_ACTIVE = (100, 210, 255, 26)
    SAFE_TINT_TELE   = (100, 210, 255, 18)

    MAX_ACTIVE_BEAMS = 48
    EXCLUSIVE_KINDS  = {"line_static", "rotor", "ring_expand"}
    HEAVY_PATTERNS   = {
        "ROTOR","RING","CUTS","WEDGE","CATA","SWEEP8","X_SWEEP","TRIDENT","TRIDENT_S",
        "CROSS","TRIDENT5","TRIDENT5_S","ZZ_ROTOR","BARS","RIPPLE"
    }

    SPAWN_TELE_MS   = 900
    SPAWN_RING_MS   = 700
    MAX_FX          = 64
    SPAWN_TELE_GLOW = (120, 200, 255, 120)
    SPAWN_TELE_RING = (255, 80, 60, 160)

    DROP_2_3_THRESH = 2/3
    DROP_1_3_THRESH = 1/3

    def __init__(self, world_x, world_y, images, sounds, map_width, map_height,
                 damage_player_fn=None, kill_callback=None, rank=rank):
        import pygame
        super().__init__(world_x, world_y, images, sounds, map_width, map_height,
                         speed=self.SPEED, near_threshold=0, far_threshold=0,
                         radius=self.RADIUS, push_strength=0.0, alert_duration=0,
                         damage_player_fn=damage_player_fn, rank=rank)
        self.world_x = map_width  * 0.5
        self.world_y = map_height * 0.5

        self.image_original = images.get("boss7")
        if self.image_original is None:
            self.image_original = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(self.image_original, (180, 0, 0, 180), (60, 60), 58, width=6)
            pygame.draw.circle(self.image_original, (30, 30, 30, 220), (60, 60), 42)
        self.image = self.image_original

        self._images_dict = images
        self._sounds_dict = sounds

        self.hp = self.HP_MAX
        self.max_hp = self.HP_MAX
        self.enraged = False

        self._state = "IDLE"
        self._pattern = None
        self._state_t0 = pygame.time.get_ticks()
        self._next_pattern_ready_at = self._state_t0 + self.BASE_IDLE_GAP_MS
        self._tele_data = None

        self._hazards = []
        self._last_tick_damage = 0
        self._fx_rings = []

        self._my_minions = []
        self._pending_summons = []
        self._next_summon = pygame.time.get_ticks() + 2000

        self.facing_angle = 0.0

        self._drop_2_3_done = False
        self._drop_1_3_done = False

        self.kill_callback = kill_callback

    # 사운드
    def _play_sound(self, key, volume=1.0):
        s = self._sounds_dict.get(key) if hasattr(self, "_sounds_dict") else None
        if not s: return
        try: s.set_volume(volume)
        except Exception: pass
        try: s.play()
        except Exception: pass

    # 유틸
    def _deal(self, amount):
        try: dmg = int(round(amount))
        except Exception: return
        if dmg <= 0: return
        try:
            if self.damage_player:
                self.damage_player(dmg); return
        except Exception: pass
        try:
            if hasattr(config, "damage_player"):
                config.damage_player(dmg)
        except Exception: pass

    def _player_center(self, player_rect, world_x, world_y):
        return (world_x + player_rect.centerx, world_y + player_rect.centery)

    def _max_ray_len(self):
        import math
        return math.hypot(self.map_width, self.map_height) + 200

    @staticmethod
    def _dist_point_to_segment(px, py, x1, y1, x2, y2):
        import math
        vx, vy = x2 - x1, y2 - y1
        wx, wy = px - x1, py - y1
        c1 = vx * wx + vy * wy
        if c1 <= 0:   return math.hypot(px - x1, py - y1)
        c2 = vx * vx + vy * vy
        if c2 <= c1:  return math.hypot(px - x2, py - y2)
        b = c1 / c2
        bx, by = x1 + b * vx, y1 + b * vy
        return math.hypot(px - bx, py - by)

    # 해저드 GC/정리
    def _gc_hazards(self, now=None):
        import pygame
        now = now or pygame.time.get_ticks()
        new = []
        for hz in self._hazards:
            start = hz.get("start", hz.get("t0", now))
            if now < start: new.append(hz); continue
            k = hz["kind"]
            if k == "line_static" and now <= hz.get("expire", now):
                new.append(hz)
            elif k == "rotor" and (now - hz["t0"]) <= hz["duration"]:
                new.append(hz)
            elif k == "ring_expand" and (now - hz["t0"]) <= hz["duration"]:
                new.append(hz)
            elif k == "rect_pulse" and now <= hz["expire"]:
                new.append(hz)
        if len(new) > self.MAX_ACTIVE_BEAMS:
            new = new[-self.MAX_ACTIVE_BEAMS:]
        self._hazards = new

        # FX 정리
        fx_new = []
        for fx in getattr(self, "_fx_rings", []):
            if now - fx.get("t0", now) <= fx.get("dur", self.SPAWN_RING_MS):
                fx_new.append(fx)
        self._fx_rings = fx_new[-self.MAX_FX:]

    def _clear_heavy_hazards(self):
        # 새 무거운 패턴 전: 기존 레이저/링/대형 직사각형을 페이드아웃.
        import pygame
        now = pygame.time.get_ticks()
        for hz in self._hazards:
            k = hz["kind"]
            if k in ("line_static","rotor","ring_expand"):
                if k == "line_static":
                    hz["expire"] = now + self.LASER_FADE_OUT_MS
                else:
                    elapsed = max(0, now - hz.get("t0", now))
                    hz["duration"] = min(hz.get("duration", elapsed + self.LASER_FADE_OUT_MS),
                                         elapsed + self.LASER_FADE_OUT_MS)
            elif k == "rect_pulse":
                # 화면의 대부분을 덮는 큰 장판이면 빠르게 정리
                big_w = hz.get("w",0) >= 0.8 * self.map_width
                big_h = hz.get("h",0) >= 0.8 * self.map_height
                if big_w or big_h:
                    hz["expire"] = now + self.LASER_FADE_OUT_MS

    # 빔/장판 렌더 유틸
    def _mul_alpha(self, rgba, scale):
        try:
            return (rgba[0], rgba[1], rgba[2], max(0, min(255, int(rgba[3] * scale))))
        except Exception:
            return rgba

    def _beam_points(self, x1, y1, x2, y2, jitter_amp, seg_len, tsec, seed=0.0):
        import math
        dx, dy = x2 - x1, y2 - y1
        L = max(1.0, math.hypot(dx, dy))
        nx, ny = dx / L, dy / L
        px, py = -ny, nx
        nseg = max(3, int(L / max(60.0, seg_len)))
        pts = [(x1, y1)]
        for i in range(1, nseg):
            u = i / float(nseg)
            bx = x1 + dx * u
            by = y1 + dy * u
            w = (math.sin((u + seed) * 7.5 + tsec * 5.0) +
                 math.cos((u*1.7 + seed*0.7) * 9.0 - tsec * 3.5)) * 0.5
            off = w * jitter_amp
            pts.append((bx + px*off, by + py*off))
        pts.append((x2, y2))
        return pts

    def _draw_polyline(self, surf, pts, color, width):
        import pygame
        for i in range(len(pts)-1):
            pygame.draw.line(surf, color, pts[i], pts[i+1], width)

    def _draw_beam_layered(self, lay, x1, y1, x2, y2, base_w, born_ms, alpha=1.0):
        import pygame, math
        now = pygame.time.get_ticks()
        tsec = now * 0.001
        jitter = min(self.BEAM_JITTER_MAX, base_w * 0.45)
        pts = self._beam_points(x1, y1, x2, y2, jitter_amp=jitter,
                                seg_len=self.BEAM_SEG_LEN, tsec=tsec,
                                seed=(born_ms % 997) * 0.001)
        pulse = 0.5 + 0.5 * math.sin((now - born_ms) * (2*math.pi / max(60, self.BEAM_PULSE_MS)))
        core_w  = max(1, int(base_w * (0.55 + 0.15*pulse)))
        glow_w  = max(core_w+2, int(base_w * 1.15))
        outer_w = max(glow_w+2, int(base_w * 1.7))
        col_outer = self._mul_alpha(self.COL_OUTER, alpha)
        col_glow  = self._mul_alpha(self.COL_GLOW,  alpha)
        col_core  = self._mul_alpha(self.COL_CORE,  alpha)
        self._draw_polyline(lay, pts, col_outer, outer_w)
        self._draw_polyline(lay, pts, col_glow,  glow_w)
        self._draw_polyline(lay, pts, col_core,  core_w)

    def _draw_arc_beam(self, lay, cx, cy, r, a0, a1, base_w, born_ms, alpha=1.0):
        import math
        seg_ang = max(math.radians(6), 2.0 / max(1.0, r))
        ang = a0
        while True:
            anext = min(a1, ang + seg_ang)
            x1 = cx + math.cos(ang)*r
            y1 = cy + math.sin(ang)*r
            x2 = cx + math.cos(anext)*r
            y2 = cy + math.sin(anext)*r
            self._draw_beam_layered(lay, x1, y1, x2, y2, base_w, born_ms, alpha=alpha)
            if anext >= a1 - 1e-6: break
            ang = anext

    # 장판 임팩트 & 이징
    def _ease_out_quad(self, x):
        x = max(0.0, min(1.0, x))
        return 1.0 - (1.0 - x) * (1.0 - x)

    def _draw_rect_impact(self, lay, rx, ry, rw, rh, start_ms, expire_ms, now):
        import pygame, math
        life = max(1, expire_ms - start_ms)
        t = max(0.0, min(1.0, (now - start_ms) / float(life)))
        # 바닥 채움 + 펄스
        intensity = 0.5 + 0.5 * math.sin(now * 0.012)
        base_a = int(110 + 70 * intensity)
        base_col = (255, 60, 60, base_a)
        pygame.draw.rect(lay, base_col, pygame.Rect(int(rx), int(ry), int(rw), int(rh)))
        # 외곽 글로우 2중 링
        edge_a  = int(160 * (0.8 + 0.2*math.sin(now*0.01)))
        glow1 = (140, 190, 255, max(40, int(edge_a*0.70)))
        glow2 = (255, 220, 180, max(30, int(edge_a*0.45)))
        w1 = max(2, int(3 + 2*intensity))
        w2 = max(2, int(6 + 4*intensity))
        pygame.draw.rect(lay, glow1, pygame.Rect(int(rx), int(ry), int(rw), int(rh)), width=w1)
        pygame.draw.rect(lay, glow2, pygame.Rect(int(rx)-2, int(ry)-2, int(rw)+4, int(rh)+4), width=w2)
        # 대각 스캔라인 스윕
        step = 10
        slope = 1
        sweep = (now // 35) % step
        col_scan = (255, 140, 110, 90)
        x0 = int(rx) - int(rh)
        x1 = int(rx + rw)
        for k in range(x0, x1, step):
            kk = k + sweep
            x_start = kk
            x_end   = kk + int(rh) * slope
            xs = max(int(rx), min(int(rx+rw), x_start))
            xe = max(int(rx), min(int(rx+rw), x_end))
            pygame.draw.line(lay, col_scan, (xs, int(ry)), (xe, int(ry + rh)), 1)
        # 코너 플레어
        flare_len = int(16 + 18 * self._ease_out_quad(t))
        flare_a = int(180 * (1.0 - 0.6*t))
        flare_col = (255, 220, 160, max(0, flare_a))
        corners = [(rx, ry), (rx+rw, ry), (rx+rw, ry+rh), (rx, ry+rh)]
        for (cx, cy) in corners:
            pygame.draw.line(lay, flare_col, (int(cx), int(cy)), (int(cx+flare_len), int(cy)), 2)
            pygame.draw.line(lay, flare_col, (int(cx), int(cy)), (int(cx), int(cy+flare_len)), 2)
        # 초반 쇼크 웨이브(0~220ms)
        shock_ms = 220
        if now < start_ms + shock_ms:
            u = self._ease_out_quad((now - start_ms) / float(shock_ms))
            margin = int(6 + 22*u)
            ring_a = int(140 * (1.0 - u))
            ring_col = (255, 200, 160, max(0, ring_a))
            pygame.draw.ellipse(lay, ring_col,
                                pygame.Rect(int(rx - margin), int(ry - margin),
                                            int(rw + 2*margin), int(rh + 2*margin)), width=2)
        # 엣지 스파크
        perim = 2*(rw + rh)
        spark_n = 12
        for i in range(spark_n):
            u = ((now*0.0007) + i / float(spark_n)) % 1.0
            pos = u * perim
            if pos < rw:
                x = rx + pos;      y = ry;         dx, dy = 0, 1
            elif pos < rw + rh:
                x = rx + rw;       y = ry + (pos - rw); dx, dy = -1, 0
            elif pos < rw + rh + rw:
                x = rx + (rw - (pos - rw - rh)); y = ry + rh; dx, dy = 0, -1
            else:
                x = rx; y = ry + (rh - (pos - rw - rh - rw)); dx, dy = 1, 0
            ln = 8
            pygame.draw.line(lay, (255, 240, 200, 150), (int(x), int(y)), (int(x+dx*ln), int(y+dy*ln)), 2)
        # 중앙 박동
        cx = int(rx + rw*0.5); cy = int(ry + rh*0.5)
        r0 = int(10 + 18*(0.5 + 0.5*math.sin(now*0.012)))
        pygame.draw.circle(lay, (255, 200, 140, 80), (cx, cy), r0, width=2)

    # 상태 전환
    def _enter(self, state, pattern=None, tele_data=None):
        import pygame
        self._state = state
        if pattern is not None:
            self._pattern = pattern
        now = pygame.time.get_ticks()
        self._state_t0 = now
        if tele_data is not None:
            self._tele_data = tele_data
        if state == "RECOVER":
            base = self.BASE_IDLE_GAP_MS
            extra = self.PATTERN_COOLDOWN_MS.get(self._pattern or "", 0)
            scale = (self.ENRAGE_CD_SCALE if self.enraged else 1.0)
            self._next_pattern_ready_at = now + int((base + extra) * scale)

    def _ready_new_pattern(self):
        import pygame
        ready_at = getattr(self, "_next_pattern_ready_at", 0)
        return (self._state == "IDLE") and (pygame.time.get_ticks() >= ready_at)

    # 패턴 빌더
    def _build_x_sweep(self):
        import math, random
        return {"type":"ROTOR","spokes":4,"width":self.BEAM_WIDTH_M,
                "spin_ms":5000,"ang_spd":math.radians(40),
                "cx":self.world_x,"cy":self.world_y,"tele_ms":700,
                "ang0":random.uniform(0, 2*math.pi), "lock_ms":300}

    def _build_checker(self, layers=1):
        return {"type":"CHECKER","rows":self.CHECKER_ROWS,"cols":self.CHECKER_COLS,
                "layers":layers, "tele_ms":self.CHECKER_TEL_MS}

    def _build_ring(self, count=1):
        return {"type":"RING","count":count,"tele_ms":self.RING_TEL_MS}

    def _build_sweep8(self):
        import math, random
        return {"type":"ROTOR","spokes":8,"width":self.BEAM_WIDTH_S,
                "spin_ms":5400,"ang_spd":math.radians(55),
                "cx":self.world_x,"cy":self.world_y,"tele_ms":650,
                "ang0":random.uniform(0, 2*math.pi), "lock_ms":300}

    def _build_cuts(self):
        import math, random
        angs = []
        base = random.uniform(0, 2*math.pi)
        for _ in range(random.randint(3,4)):
            angs.append(base + random.uniform(0.4, 1.9))
        return {"type":"CUTS","angs":angs,"width":self.BEAM_WIDTH_L, "persist":2000, "tele_ms":600}

    def _build_wedge(self):
        return {"type":"WEDGE","safe_deg":35, "jumps":6, "jump_ms":700,
                "width":self.BEAM_WIDTH_S, "persist":6000, "tele_ms":800}

    def _build_cata(self):
        import math, random
        return {"type":"CATA","fan_deg":24, "fan_ms":1800, "tele_ms":1800,
                "ang_spd":math.radians(18), "ang0":random.uniform(0, 2*math.pi), "lock_ms":300}

    def _build_trident(self, weak=False):
        return {"type":"TRIDENT", "weak": bool(weak), "tele_ms":700}

    def _build_ripple(self, count=3, gap_ms=220, big=False):
        return {"type":"RIPPLE","count":count,"gap":gap_ms,"big":bool(big),"tele_ms":600}

    def _build_cross(self, slow_deg=25):
        import math, random
        return {"type":"CROSS","spokes":4,"width":self.BEAM_WIDTH_M,
                "spin_ms":4600,"ang_spd":math.radians(slow_deg),
                "cx":self.world_x,"cy":self.world_y,"tele_ms":650,
                "ang0":random.uniform(0, 2*math.pi), "lock_ms":300}

    def _build_trident5(self, weak=True):
        return {"type":"TRIDENT5","weak":bool(weak),"tele_ms":700}

    def _build_zz_rotor(self, spokes=6, ang_spd_deg=65, zig_ms=500):
        import math, random
        return {"type":"ZZ_ROTOR","spokes":spokes,"width":self.BEAM_WIDTH_S,
                "spin_ms":5200,"ang_spd":math.radians(ang_spd_deg),"zig_ms":int(zig_ms),
                "cx":self.world_x,"cy":self.world_y,"tele_ms":650,
                "ang0":random.uniform(0, 2*math.pi), "lock_ms":300}

    def _build_bars(self, lines=3, angle_deg=None, persist=1800, width=None):
        import math, random
        if angle_deg is None:
            angle_deg = random.uniform(0, 180)
        if width is None:
            width = self.BEAM_WIDTH_S
        return {"type":"BARS","lines":int(lines),"angle":math.radians(angle_deg),
                "persist":int(persist),"width":width,"tele_ms":700}

    def _build_wave_rect(self, axis="row", bands=5, period_ms=900, duty=0.22):
        return {"type":"WAVE_RECT","axis":axis,"bands":int(bands),
                "period":int(period_ms), "duty":float(duty), "tele_ms":2800}

    def _build_sniper(self):
        return {"type":"SNIPER","tele_ms":700}

    # 발사
    def _fire_pattern(self):
        import pygame, math, random
        now = pygame.time.get_ticks()
        t = self._tele_data
        if not t: self._enter("RECOVER"); return

        self._play_sound("boss7_fire", 0.9)
        if t["type"] in self.HEAVY_PATTERNS:
            self._clear_heavy_hazards()

        if t["type"] == "ROTOR":
            self._hazards.append({
                "kind":"rotor","cx":t["cx"],"cy":t["cy"],"r":self._max_ray_len(),
                "w":t["width"],"spokes":t["spokes"],
                "ang0":t.get("ang0", 0.0),"ang_spd":t["ang_spd"],"lock_ms":t.get("lock_ms",0),
                "t0":now,"duration":t["spin_ms"],"dps":self.DOT_MED
            })

        elif t["type"] == "CHECKER":
            rows, cols = t["rows"], t["cols"]
            cw = self.map_width  / float(cols)
            ch = self.map_height / float(rows)
            for layer in range(t.get("layers",1)):
                delay = layer * 280
                for r in range(rows):
                    for c in range(cols):
                        if (r*cols + c + layer) % 2 == 0:
                            x = c*cw; y = r*ch
                            self._hazards.append({
                                "kind":"rect_pulse","x":x,"y":y,"w":cw,"h":ch,
                                "start": now + delay, "expire": now + delay + 300,
                                "once": True, "dmg": self.CHECKER_BLAST_ONETIME,
                                "residual": {"dur": 1500, "dot": self.CHECKER_RESIDUAL_DOT}
                            })

        elif t["type"] == "RING":
            cnt = t.get("count",1)
            for i in range(cnt):
                dur0 = [self.RING1_MS, self.RING2_MS, self.RING3_MS][min(i,2)]
                wid = [self.RING_WIDTH_S, self.RING_WIDTH_M, self.RING_WIDTH_L][min(i,2)]
                dur = int(dur0 * self.RING_SPEED_SCALE)
                r0 = int(60*PLAYER_VIEW_SCALE); r1 = int(1200*PLAYER_VIEW_SCALE)
                v = (r1 - r0) / float(dur) if dur > 0 else (r1 - r0)
                self._hazards.append({
                    "kind":"ring_expand","cx":self.world_x,"cy":self.world_y,
                    "r0": r0, "r1": r1, "r": float(r0), "v": v, "last": now,
                    "w": wid, "t0":now, "duration":dur, "dps": self.DOT_MED
                })

        elif t["type"] == "CUTS":
            w = t["width"]; cx, cy = self.world_x, self.world_y
            L = self._max_ray_len()
            expire = now + t["persist"]
            for ang in t["angs"]:
                x2 = cx + math.cos(ang)*L
                y2 = cy + math.sin(ang)*L
                self._hazards.append({
                    "kind":"line_static","x1":cx,"y1":cy,"x2":x2,"y2":y2,
                    "w":w,"expire":expire,"dps":self.DOT_STR,"t0":now
                })

        elif t["type"] == "WEDGE":
            jumps = t["jumps"]; gap = math.radians(t["safe_deg"])
            base = random.uniform(0, 2*math.pi)
            L = self._max_ray_len()
            for j in range(jumps):
                start = now + j * t["jump_ms"]
                center = base + random.uniform(-math.pi, math.pi)
                for k in range(0, 360, 12):
                    ang = math.radians(k)
                    da = (ang - center + math.pi) % (2*math.pi) - math.pi
                    if abs(da) <= gap*0.5: continue
                    x2 = self.world_x + math.cos(ang)*L
                    y2 = self.world_y + math.sin(ang)*L
                    self._hazards.append({
                        "kind":"line_static","x1":self.world_x,"y1":self.world_y,
                        "x2":x2,"y2":y2,"w":self.BEAM_WIDTH_S,
                        "start":start, "expire":start + t["persist"], "dps":self.DOT_MED, "t0":start
                    })

        elif t["type"] == "CATA":
            L = self._max_ray_len()
            self._hazards.append({
                "kind":"rotor","cx":self.world_x,"cy":self.world_y,"r":L,
                "w":self.BEAM_WIDTH_S,"spokes":t["fan_deg"],
                "ang0":t.get("ang0", 0.0),"ang_spd":t["ang_spd"],"lock_ms":t.get("lock_ms",300),
                "t0":now,"duration":t["fan_ms"],"dps":self.DOT_WEAK
            })
            for i, dur0 in enumerate([self.RING1_MS, self.RING2_MS, self.RING3_MS]):
                wid = [self.RING_WIDTH_S, self.RING_WIDTH_M, self.RING_WIDTH_L][i]
                dur = int(dur0 * self.RING_SPEED_SCALE)
                r0 = int(80*PLAYER_VIEW_SCALE); r1 = int(1300*PLAYER_VIEW_SCALE)
                v = (r1 - r0) / float(dur) if dur > 0 else (r1 - r0)
                self._hazards.append({
                    "kind":"ring_expand","cx":self.world_x,"cy":self.world_y,
                    "r0": r0, "r1": r1, "r": float(r0), "v": v, "last": now,
                    "w": wid, "t0":now, "duration":dur, "dps": self.DOT_MED
                })

        elif t["type"] == "TRIDENT":
            ang0 = self.facing_angle
            offsets = [-math.radians(14), 0.0, math.radians(14)]
            L = self._max_ray_len()
            weak = t.get("weak", False)
            wid  = self.BEAM_WIDTH_M if weak else self.BEAM_WIDTH_L
            dps  = self.DOT_MED if weak else self.DOT_STR
            dur  = 1300 if weak else 1800
            for off in offsets:
                ang = ang0 + off
                x2 = self.world_x + math.cos(ang)*L
                y2 = self.world_y + math.sin(ang)*L
                self._hazards.append({
                    "kind":"line_static","x1":self.world_x,"y1":self.world_y,"x2":x2,"y2":y2,
                    "w":wid,"expire":now + dur,"dps":dps,"t0":now
                })

        elif t["type"] == "RIPPLE":
            cnt = max(1, int(t.get("count",3)))
            gap = int(t.get("gap",220))
            for i in range(cnt):
                delay = i * gap
                dur0 = self.RING1_MS + 300*i
                dur = int(dur0 * self.RING_SPEED_SCALE)
                r0 = int((80 if t.get("big") else 60)*PLAYER_VIEW_SCALE)
                r1 = int((1300 if t.get("big") else 1100)*PLAYER_VIEW_SCALE)
                v = (r1 - r0) / float(dur) if dur > 0 else (r1 - r0)
                self._hazards.append({
                    "kind":"ring_expand","cx":self.world_x,"cy":self.world_y,
                    "r0": r0, "r1": r1, "r": float(r0), "v": v, "last": now + delay,
                    "w": self.RING_WIDTH_M, "t0": now + delay,
                    "duration": dur, "dps": self.DOT_MED, "start": now + delay
                })

        elif t["type"] == "CROSS":
            self._hazards.append({
                "kind":"rotor","cx":t["cx"],"cy":t["cy"],"r":self._max_ray_len(),
                "w":t["width"],"spokes":4,
                "ang0":t.get("ang0", 0.0),"ang_spd":t["ang_spd"],"lock_ms":t.get("lock_ms",300),
                "t0":now,"duration":t["spin_ms"],"dps":self.DOT_MED
            })

        elif t["type"] == "TRIDENT5":
            ang0 = self.facing_angle
            offs_deg = [-24,-12,0,12,24]
            L = self._max_ray_len()
            weak = t.get("weak", True)
            wid  = self.BEAM_WIDTH_M if weak else self.BEAM_WIDTH_L
            dps  = self.DOT_MED if weak else self.DOT_STR
            dur  = 1200 if weak else 1700
            for od in offs_deg:
                ang = ang0 + math.radians(od)
                x2 = self.world_x + math.cos(ang)*L
                y2 = self.world_y + math.sin(ang)*L
                self._hazards.append({
                    "kind":"line_static","x1":self.world_x,"y1":self.world_y,"x2":x2,"y2":y2,
                    "w":wid,"expire":now + dur,"dps":dps,"t0":now
                })

        elif t["type"] == "ZZ_ROTOR":
            self._hazards.append({
                "kind":"rotor","cx":t["cx"],"cy":t["cy"],"r":self._max_ray_len(),
                "w":t["width"],"spokes":t["spokes"],
                "ang0":t.get("ang0", 0.0),"ang_spd":t["ang_spd"],"lock_ms":t.get("lock_ms",300),
                "zig_ms":int(t.get("zig_ms",500)),
                "t0":now,"duration":t["spin_ms"],"dps":self.DOT_MED
            })

        elif t["type"] == "BARS":
            ang = t["angle"]; lines = max(1, int(t["lines"]))
            w = t.get("width", self.BEAM_WIDTH_S); dur = int(t.get("persist",1600))
            L = self._max_ray_len()
            nx, ny = -math.sin(ang), math.cos(ang)
            gap = max(60, int(120 * PLAYER_VIEW_SCALE))
            start_offset = -((lines-1)//2)
            for i in range(lines):
                d = (start_offset + i)*gap
                bx = self.world_x + nx*d
                by = self.world_y + ny*d
                dx, dy = math.cos(ang), math.sin(ang)
                x1 = bx - dx*L; y1 = by - dy*L
                x2 = bx + dx*L; y2 = by + dy*L
                self._hazards.append({
                    "kind":"line_static","x1":x1,"y1":y1,"x2":x2,"y2":y2,
                    "w":w,"expire":now + dur,"dps":self.DOT_MED,"t0":now
                })

        elif t["type"] == "WAVE_RECT":
            axis = t.get("axis","row")
            bands = max(3, int(t.get("bands",5)))
            period = max(600, int(t.get("period",900)))
            duty = max(0.10, min(0.35, float(t.get("duty", 0.22))))
            on_ms = int(period * duty)
            if axis == "row":
                band_h = self.map_height / float(bands)
                for b in range(bands):
                    start = now + int((b / float(bands)) * period)
                    self._hazards.append({
                        "kind":"rect_pulse","x":0,"y":b*band_h,"w":self.map_width,"h":band_h,
                        "start": start, "expire": start + on_ms, "once": False
                    })
            else:
                band_w = self.map_width / float(bands)
                for b in range(bands):
                    start = now + int((b / float(bands)) * period)
                    self._hazards.append({
                        "kind":"rect_pulse","x":b*band_w,"y":0,"w":band_w,"h":self.map_height,
                        "start": start, "expire": start + on_ms, "once": False
                    })

        elif t["type"] == "SNIPER":
            ang = self.facing_angle
            L = self._max_ray_len()
            x2 = self.world_x + math.cos(ang)*L
            y2 = self.world_y + math.sin(ang)*L
            self._hazards.append({
                "kind":"line_static","x1":self.world_x,"y1":self.world_y,"x2":x2,"y2":y2,
                "w":self.BEAM_WIDTH_XL,"expire":now + 420,"dps":self.DOT_SNIPER,"t0":now
            })

        self._enter("RECOVER")

    # 업데이트
    def update(self, dt, world_x, world_y, player_rect, enemies=[]):
        import pygame, math
        if not self.alive: return

        px, py = self._player_center(player_rect, world_x, world_y)
        self.facing_angle = math.atan2(py - self.world_y, px - self.world_x)

        # 중간 드랍
        if not self._drop_2_3_done and self.hp <= int(self.HP_MAX * self.DROP_2_3_THRESH):
            self._drop_medium_orbs(1); self._drop_2_3_done = True
        if not self._drop_1_3_done and self.hp <= int(self.HP_MAX * self.DROP_1_3_THRESH):
            self._drop_medium_orbs(1); self._drop_1_3_done = True

        if not self.enraged and self.hp <= self.HP_MAX * self.ENRAGE_AT_FRAC:
            self.enraged = True

        now = pygame.time.get_ticks()

        # 미니언
        cap = self.MINION_CAP_ENRAGE if self.enraged else self.MINION_CAP_BASE
        if (self._alive_minions() + len(self._pending_summons)) < cap and now >= self._next_summon:
            low, high = (3,5) if self.enraged else (1,4)
            self._schedule_summons(self.SUMMON_BURST, low, high)
            cd = self.SUMMON_CD_ENRAGE if self.enraged else self.SUMMON_CD_BASE
            self._next_summon = now + cd
        self._process_pending_summons()

        # 해저드 처리/피해
        do_tick = (now - self._last_tick_damage) >= self.LASER_TICK_MS
        if do_tick: self._last_tick_damage = now
        new_haz = []
        for hz in self._hazards:
            alive = True
            deal = 0
            start = hz.get("start", hz.get("t0", now))
            if now < start: new_haz.append(hz); continue
            kind = hz["kind"]

            if kind == "line_static":
                if now <= hz.get("expire", now):
                    d = self._dist_point_to_segment(px, py, hz["x1"], hz["y1"], hz["x2"], hz["y2"])
                    if d <= hz["w"] * 0.5 and do_tick:
                        deal = hz["dps"] * (self.LASER_TICK_MS / 1000.0)
                else:
                    alive = False

            elif kind == "rotor":
                t0 = hz["t0"]; dur = hz["duration"]
                tfrac = (now - t0) / max(1, dur)
                if tfrac <= 1.0:
                    lock_ms = hz.get("lock_ms", 0)
                    sign = 1
                    if now - t0 > lock_ms and "zig_ms" in hz:
                        zig = max(1, int(hz["zig_ms"]))
                        phase = ((now - t0 - lock_ms) // zig) % 2
                        sign = 1 if phase == 0 else -1
                    if now - t0 <= lock_ms:
                        cur_ang = hz["ang0"]
                    else:
                        cur_ang = hz["ang0"] + sign * hz["ang_spd"] * ((now - t0 - lock_ms)/1000.0)
                    for i in range(hz["spokes"]):
                        ang = cur_ang + (2*math.pi/float(hz["spokes"])) * i
                        x2 = hz["cx"] + math.cos(ang)*hz["r"]
                        y2 = hz["cy"] + math.sin(ang)*hz["r"]
                        d = self._dist_point_to_segment(px, py, hz["cx"], hz["cy"], x2, y2)
                        if d <= hz["w"] * 0.5 and do_tick:
                            deal = max(deal, hz["dps"] * (self.LASER_TICK_MS / 1000.0))
                else:
                    alive = False

            elif kind == "ring_expand":
                # 적분식 확장(순간이동 방지)
                last = hz.get("last", now); dt_ms = max(0, now - last); hz["last"] = now
                hz["r"] = min(hz["r1"], hz["r"] + hz["v"] * dt_ms)
                r = hz["r"]
                if now - hz["t0"] <= hz["duration"]:
                    dist = abs(math.hypot(px - hz["cx"], py - hz["cy"]) - r)
                    if dist <= hz["w"] * 0.5 and do_tick:
                        deal = hz["dps"] * (self.LASER_TICK_MS / 1000.0)
                else:
                    alive = False

            elif kind == "rect_pulse":
                if now <= hz["expire"]:
                    if hz.get("hit_once", False):
                        alive = False
                    else:
                        inside = (hz["x"] <= px <= hz["x"]+hz["w"]) and (hz["y"] <= py <= hz["y"]+hz["h"])
                        if inside:
                            if hz.get("once", False):
                                self._deal(self.CHECKER_BLAST_ONETIME); hz["hit_once"] = True
                                try:
                                    from entities import AcidPool
                                    img = self._images_dict.get("acid_pool")
                                    pool = AcidPool(hz["x"]+hz["w"]*0.5, hz["y"]+hz["h"]*0.5,
                                                    img, radius=int(80*PLAYER_VIEW_SCALE),
                                                    dot_damage=self.CHECKER_RESIDUAL_DOT,
                                                    duration=1500,
                                                    sounds=self._sounds_dict)
                                    if not hasattr(config, "acid_pools"): config.acid_pools = []
                                    config.acid_pools.append(pool)
                                except Exception: pass
                            else:
                                if do_tick: self._deal(self.DOT_WEAK * (self.LASER_TICK_MS/1000.0))
                else:
                    alive = False

            if deal > 0: self._deal(deal)
            if alive: new_haz.append(hz)
        self._hazards = new_haz

        self._gc_hazards(now)

        if self._state == "RECOVER" and now >= getattr(self, "_next_pattern_ready_at", 0):
            self._enter("IDLE")

        # 패턴 스케줄링
        if self._ready_new_pattern():
            import random
            phase = (3 if self.hp <= self.max_hp*self.PHASE3_AT_FRAC
                        else 2 if self.hp <= self.max_hp*self.PHASE2_AT_FRAC
                        else 1)
            if phase == 1:
                pool = ["X_SWEEP","CHECKER","RING1","RIPPLE","CROSS"]
                w    = [3,3,2,2,2]
            elif phase == 2:
                pool = ["SWEEP8","CHECKER2","RING2","TRIDENT_S",
                        "ZZ_ROTOR","TRIDENT5_S","BARS","WAVE_RECT","SNIPER"]
                w    = [3,3,3,2,  2,2,2,2,1]
            else:
                pool = ["CUTS","WEDGE","CATA","TRIDENT",
                        "TRIDENT5","RIPPLE","ZZ_ROTOR","BARS","SNIPER"]
                w    = [3,3,2,3,  2,2,2,2,1]

            pat = random.choices(pool, weights=w, k=1)[0]
            if   pat == "X_SWEEP":    tele = self._build_x_sweep()
            elif pat == "CHECKER":    tele = self._build_checker(layers=1)
            elif pat == "RING1":      tele = self._build_ring(count=1)
            elif pat == "SWEEP8":     tele = self._build_sweep8()
            elif pat == "CHECKER2":   tele = self._build_checker(layers=2)
            elif pat == "RING2":      tele = self._build_ring(count=2)
            elif pat == "CUTS":       tele = self._build_cuts()
            elif pat == "WEDGE":      tele = self._build_wedge()
            elif pat == "TRIDENT_S":  tele = self._build_trident(weak=True)
            elif pat == "TRIDENT":    tele = self._build_trident(weak=False)
            elif pat == "CATA":       tele = self._build_cata()
            elif pat == "RIPPLE":     tele = self._build_ripple(count=3 if phase==1 else (3 if phase==2 else 4),
                                                                gap_ms=220 if phase<3 else 180,
                                                                big=(phase==3))
            elif pat == "CROSS":      tele = self._build_cross(slow_deg=25 if phase<3 else 30)
            elif pat == "TRIDENT5_S": tele = self._build_trident5(weak=True)
            elif pat == "TRIDENT5":   tele = self._build_trident5(weak=False)
            elif pat == "ZZ_ROTOR":   tele = self._build_zz_rotor(spokes=(6 if phase<3 else 8),
                                                                  ang_spd_deg=(55 if phase==2 else 70),
                                                                  zig_ms=(520 if phase==2 else 420))
            elif pat == "BARS":       tele = self._build_bars(lines=(3 if phase<3 else 4),
                                                              angle_deg=None,
                                                              persist=(1600 if phase<3 else 2000),
                                                              width=self.BEAM_WIDTH_S if phase<3 else self.BEAM_WIDTH_M)
            elif pat == "WAVE_RECT":  tele = self._build_wave_rect(axis=("row" if phase==2 else "col"),
                                                                   bands=(5 if phase==2 else 6),
                                                                   period_ms=(900 if phase==2 else 800),
                                                                   duty=0.22)
            elif pat == "SNIPER":     tele = self._build_sniper()
            else:                     tele = self._build_x_sweep()

            self._play_sound("boss7_charge", 0.6)
            self._enter("TELE", pattern=pat, tele_data=tele)

        # 텔레 만료 → 발사
        if self._state == "TELE" and self._tele_data:
            if now - self._state_t0 >= self._tele_data.get("tele_ms", 600):
                self._fire_pattern()

    # 드로우
    def draw(self, surface, world_x, world_y, shake_offset_x=0, shake_offset_y=0):
        import pygame, math
        if not self.alive and self.hp <= 0: return
        W, H = surface.get_width(), surface.get_height()
        sx = self.world_x - world_x
        sy = self.world_y - world_y
        now = pygame.time.get_ticks()

        # 본체
        ang_deg = math.degrees(self.facing_angle) + self.ORIENT_OFFSET_DEG
        rotated = pygame.transform.rotate(self.image_original, -ang_deg)
        surface.blit(rotated, rotated.get_rect(center=(sx, sy)).topleft)

        # 텔레그래프
        if self._state == "TELE" and self._tele_data:
            t = self._tele_data
            tel = pygame.Surface((W, H), pygame.SRCALPHA)
            color = (255, 60, 60, 70)

            # 안전지대 프리뷰(행/열/웨이브류)
            if t["type"] in ("WAVE_RECT",):
                tel.fill(self.SAFE_TINT_TELE)

            if t["type"] in ("ROTOR","CATA","CROSS","ZZ_ROTOR"):
                cx = int(self.world_x - world_x); cy = int(self.world_y - world_y)
                L = self._max_ray_len()
                ang0 = t.get("ang0", 0.0)
                spokes = t.get("spokes", t.get("fan_deg", 4))
                width  = t.get("width", self.BEAM_WIDTH_S)
                for i in range(spokes):
                    ang = ang0 + (2*math.pi/spokes) * i
                    x2 = cx + math.cos(ang)*L
                    y2 = cy + math.sin(ang)*L
                    pygame.draw.line(tel, color, (cx,cy), (x2,y2), max(4, width//2))

            elif t["type"] == "CHECKER":
                rows, cols = t["rows"], t["cols"]
                cw = self.map_width  / float(cols)
                ch = self.map_height / float(rows)
                for r in range(rows):
                    for c in range(cols):
                        if (r*cols + c) % 2 == 0:
                            rx = c*cw - world_x; ry = r*ch - world_y
                            pygame.draw.rect(tel, (255,60,60,60),
                                             pygame.Rect(int(rx), int(ry), int(cw), int(ch)))

            elif t["type"] == "RING":
                cx = int(self.world_x - world_x); cy = int(self.world_y - world_y)
                pygame.draw.circle(tel, (255,60,60,70), (cx,cy), int(90*PLAYER_VIEW_SCALE), width=3)

            elif t["type"] == "RIPPLE":
                cx = int(self.world_x - world_x); cy = int(self.world_y - world_y)
                for r in (80, 140, 210):
                    pygame.draw.circle(tel, (255,60,60,60), (cx,cy), int(r*PLAYER_VIEW_SCALE), width=2)

            elif t["type"] == "BARS":
                cx = self.world_x - world_x; cy = self.world_y - world_y
                L = self._max_ray_len()
                ang = t["angle"]; nx, ny = -math.sin(ang), math.cos(ang)
                gap = max(60, int(120 * PLAYER_VIEW_SCALE))
                start_offset = -((t["lines"]-1)//2)
                for i in range(t["lines"]):
                    d = (start_offset + i)*gap
                    bx = cx + nx*d; by = cy + ny*d
                    dx, dy = math.cos(ang), math.sin(ang)
                    x1 = bx - dx*L; y1 = by - dy*L
                    x2 = bx + dx*L; y2 = by + dy*L
                    pygame.draw.line(tel, color, (x1,y1), (x2,y2), max(4, t.get("width", self.BEAM_WIDTH_S)//2))

            elif t["type"] == "WAVE_RECT":
                axis = t.get("axis","row"); bands = t.get("bands",5)
                if axis == "row":
                    band_h = self.map_height / float(bands)
                    for b in range(bands):
                        ry = b*band_h - world_y
                        pygame.draw.rect(tel, (255,60,60,70), pygame.Rect(0, int(ry), W, int(band_h)))
                else:
                    band_w = self.map_width / float(bands)
                    for b in range(bands):
                        rx = b*band_w - world_x
                        pygame.draw.rect(tel, (255,60,60,70), pygame.Rect(int(rx), 0, int(band_w), H))

            elif t["type"] in ("TRIDENT","TRIDENT5","TRIDENT5_S","SNIPER"):
                cx = int(self.world_x - world_x); cy = int(self.world_y - world_y)
                L = self._max_ray_len(); ang0 = self.facing_angle
                offs = (-math.radians(14), 0.0, math.radians(14)) if t["type"]=="TRIDENT" else \
                       [math.radians(a) for a in (-24,-12,0,12,24)] if "TRIDENT5" in t["type"] else (0.0,)
                if t["type"] == "SNIPER": offs = (0.0,)
                for off in offs:
                    ang = ang0 + off
                    x2 = cx + math.cos(ang)*L; y2 = cy + math.sin(ang)*L
                    pygame.draw.line(tel, (255,60,60,70), (cx,cy), (x2,y2), 6)
            surface.blit(tel, (0, 0))

        # 해저드/스폰 VFX 레이어
        lay = pygame.Surface((W, H), pygame.SRCALPHA)

        # 소환 예정 텔레그래프
        for s in getattr(self, "_pending_summons", []):
            p = max(0.0, min(1.0, (now - s["t0"]) / float(self.SUMMON_CAST_MS)))
            cx = int(s["x"] - world_x); cy = int(s["y"] - world_y)
            r1 = int(28 * PLAYER_VIEW_SCALE + 64 * PLAYER_VIEW_SCALE * p)
            r2 = int(12 * PLAYER_VIEW_SCALE + 42 * PLAYER_VIEW_SCALE * (0.5 + 0.5*math.sin(now*0.01)))
            try:
                pygame.draw.circle(lay, self.SPAWN_TELE_GLOW, (cx, cy), r1, width=3)
                pygame.draw.circle(lay, self.SPAWN_TELE_RING, (cx, cy), r2, width=2)
                arm = int(20 * PLAYER_VIEW_SCALE + 55 * PLAYER_VIEW_SCALE * p)
                for k in range(6):
                    ang = p*6.0 + k * (math.pi/3.0)
                    x2 = cx + int(math.cos(ang) * arm)
                    y2 = cy + int(math.sin(ang) * arm)
                    pygame.draw.line(lay, self.SPAWN_TELE_RING, (cx, cy), (x2, y2), 2)
            except Exception: pass

        # 활성 rect가 하나라도 있으면, 안전지대 하늘색 틴트를 먼저 깔기
        active_rect_exists = False
        for hz in self._hazards:
            if hz["kind"] == "rect_pulse":
                start = hz.get("start", hz.get("t0", now))
                if start <= now <= hz.get("expire", now-1):
                    active_rect_exists = True; break
        if active_rect_exists:
            safe = pygame.Surface((W, H), pygame.SRCALPHA)
            safe.fill(self.SAFE_TINT_ACTIVE)
            lay.blit(safe, (0,0))

        # 해저드 렌더(페이드 인/아웃)
        def fade_alpha(start_ms, end_ms, now_ms):
            a_in = 1.0
            if now_ms >= start_ms:
                a_in = min(1.0, (now_ms - start_ms) / float(self.LASER_FADE_IN_MS))
            a_out = 1.0
            remain = end_ms - now_ms
            if remain <= self.LASER_FADE_OUT_MS:
                a_out = max(0.0, remain / float(self.LASER_FADE_OUT_MS))
            return max(0.0, min(1.0, a_in * a_out))

        for hz in self._hazards:
            start = hz.get("start", hz.get("t0", now))
            if now < start: continue
            k = hz["kind"]
            if k == "line_static":
                end = hz.get("expire", now)
                alpha = fade_alpha(start, end, now)
                x1 = hz["x1"] - world_x; y1 = hz["y1"] - world_y
                x2 = hz["x2"] - world_x; y2 = hz["y2"] - world_y
                self._draw_beam_layered(lay, x1, y1, x2, y2, hz["w"], hz.get("t0", now), alpha)

            elif k == "rotor":
                end = hz["t0"] + hz["duration"]; alpha = fade_alpha(hz["t0"], end, now)
                t0 = hz["t0"]; lock_ms = hz.get("lock_ms", 0)
                sign = 1
                if now - t0 > lock_ms and "zig_ms" in hz:
                    zig = max(1, int(hz["zig_ms"]))
                    phase = ((now - t0 - lock_ms) // zig) % 2
                    sign = 1 if phase == 0 else -1
                if now - t0 <= lock_ms:
                    cur_ang = hz["ang0"]
                else:
                    cur_ang = hz["ang0"] + sign * hz["ang_spd"] * ((now - t0 - lock_ms)/1000.0)
                cx = hz["cx"] - world_x; cy = hz["cy"] - world_y
                for i in range(hz["spokes"]):
                    import math
                    ang = cur_ang + (2*math.pi/float(hz["spokes"])) * i
                    x2 = cx + math.cos(ang)*hz["r"]
                    y2 = cy + math.sin(ang)*hz["r"]
                    self._draw_beam_layered(lay, cx, cy, x2, y2, hz["w"], hz["t0"], alpha)

            elif k == "ring_expand":
                end = hz["t0"] + hz["duration"]; alpha = fade_alpha(hz["t0"], end, now)
                r = hz.get("r", hz["r0"])
                cx = hz["cx"] - world_x; cy = hz["cy"] - world_y
                self._draw_arc_beam(lay, cx, cy, r, 0.0, 2*math.pi, hz["w"], hz["t0"], alpha)

            elif k == "rect_pulse":
                if now <= hz["expire"]:
                    rx = hz["x"] - world_x; ry = hz["y"] - world_y
                    rw = int(hz["w"]); rh = int(hz["h"])
                    self._draw_rect_impact(lay, rx, ry, rw, rh, start, hz["expire"], now)

        surface.blit(lay, (0, 0))

    # 피격/드랍/사망
    def hit(self, damage, blood_effects, force=False):
        prev = self.hp
        thr66 = self.max_hp * (2.0/3.0)
        thr33 = self.max_hp * (1.0/3.0)
        super().hit(damage, blood_effects, force)
        if self.alive:
            if (not self._drop_2_3_done) and prev > thr66 and self.hp <= thr66:
                self._drop_medium_orbs(1); self._drop_2_3_done = True
            if (not self._drop_1_3_done) and prev > thr33 and self.hp <= thr33:
                self._drop_medium_orbs(1); self._drop_1_3_done = True

    def die(self, blood_effects):
        self._hazards.clear()
        self._drop_massive_orbs()
        super().die(blood_effects)

    # 드랍 유틸
    def _drop_medium_orbs(self, times=1):
        try:
            if hasattr(config, "spawn_heavy_orbs"):
                config.spawn_heavy_orbs(self.world_x, self.world_y, count=max(1, 2*times)); return
        except Exception: pass
        try:
            if hasattr(config, "spawn_orbs"):
                config.spawn_orbs(self.world_x, self.world_y, amount=55*max(1,times))
        except Exception: pass

    def _drop_massive_orbs(self):
        ok = False
        try:
            if hasattr(config, "spawn_heavy_orbs"):
                config.spawn_heavy_orbs(self.world_x, self.world_y, count=6); ok = True
        except Exception: pass
        try:
            if hasattr(config, "spawn_orbs"):
                config.spawn_orbs(self.world_x, self.world_y, amount=220 if ok else 300)
        except Exception: pass

    # 미니언
    def _alive_minions(self):
        alive = 0
        for m in list(self._my_minions):
            if getattr(m, "alive", False) and getattr(m, "hp", 1) > 0:
                alive += 1
            else:
                try: self._my_minions.remove(m)
                except Exception: pass
        return alive

    def _iter_enemy_classes(self):
        try:
            cand = []
            if isinstance(ENEMY_CLASSES, (list, tuple)):
                cand.extend([v for v in ENEMY_CLASSES if v])
            g = globals()
            for k, v in g.items():
                if isinstance(v, type) and k.startswith("Enemy"):
                    cand.append(v)
            return cand
        except Exception:
            return []

    def _choose_minion_class(self, low_rank, high_rank):
        import random
        candidates = []
        for cls in self._iter_enemy_classes():
            try:
                r = getattr(cls, "rank", 1)
                if getattr(cls, "__name__", "").startswith("Boss"): continue
                if low_rank <= r <= high_rank:
                    candidates.append(cls)
            except Exception: pass
        if not candidates: return None
        return random.choice(candidates)

    def _spawn_minion_at(self, x, y, low_r, high_r):
        cls = self._choose_minion_class(low_r, high_r)
        if not cls: return None
        m = None
        try:
            m = cls(x, y, self._images_dict, self._sounds_dict,
                    self.map_width, self.map_height,
                    damage_player_fn=self.damage_player)
        except Exception:
            try:
                m = cls(x, y, self._images_dict, self._sounds_dict,
                        self.map_width, self.map_height)
            except Exception:
                try:
                    m = cls(x, y, self._images_dict, self._sounds_dict)
                except Exception:
                    return None
        try: setattr(m, "summoned_by", self)
        except Exception: pass
        try:
            if not hasattr(config, "all_enemies"): config.all_enemies = []
            config.all_enemies.append(m)
        except Exception: pass
        self._my_minions.append(m)
        return m

    def _schedule_summons(self, count, low_r, high_r):
        import pygame, random, math
        slots = max(0, (self.MINION_CAP_ENRAGE if self.enraged else self.MINION_CAP_BASE)
                       - (self._alive_minions() + len(self._pending_summons)))
        if slots <= 0: return
        n = min(count, slots)
        px, py = self.world_x, self.world_y
        now = pygame.time.get_ticks()
        for _ in range(n):
            r = random.randint(self.SUMMON_RING_MIN, self.SUMMON_RING_MAX)
            ang = random.uniform(0, 2*math.pi)
            sx = min(max(0, px + math.cos(ang)*r), self.map_width)
            sy = min(max(0, py + math.sin(ang)*r), self.map_height)
            self._pending_summons.append({"x":sx, "y":sy, "t0": now, "low":low_r, "high":high_r})
            self._play_sound("spawn_charge", 0.5)

    def _process_pending_summons(self):
        import pygame
        now = pygame.time.get_ticks()
        rest = []
        for s in self._pending_summons:
            if now - s["t0"] >= self.SUMMON_CAST_MS:
                self._spawn_minion_at(s["x"], s["y"], s["low"], s["high"])
                self._play_sound("spawn_enemy", 0.9)
                self._play_sound("spawn_burst", 0.9)
                self._fx_rings.append({"x": s["x"], "y": s["y"], "t0": now, "dur": self.SPAWN_RING_MS})
            else:
                rest.append(s)
        self._pending_summons = rest
