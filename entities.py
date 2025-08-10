import pygame
import math
import time
import random
from collider import Collider
from config import PLAYER_VIEW_SCALE
import config
from ui import KOREAN_FONT_28

PARTICLE_COUNT = 30
PARTICLE_SIZE = int(6 * PLAYER_VIEW_SCALE)
PARTICLE_SPEED_MIN = 4
PARTICLE_SPEED_MAX = 12
PARTICLE_LIFETIME = 2000
PARTICLE_FADE_TIME = 500

class MerchantNPC:
    def __init__(self, image, x, y, dialogue):
        self.image = image
        self.x = x
        self.y = y
        self.dialogue = dialogue
        self.rect = self.image.get_rect(center=(x, y))
        iw, ih = self.rect.size
        rx = iw * 0.30
        ry = ih * 0.30
        self.collider = Collider(
            shape="ellipse",
            center=(0.0, 0.0),
            size=(rx, ry),
            bullet_passable=True
        )

    def draw(self, screen, world_x, world_y):
        screen_x = self.x - world_x
        screen_y = self.y - world_y
        screen.blit(self.image, (screen_x - self.rect.width // 2, screen_y - self.rect.height // 2))

    def is_player_near(self, player_center_x, player_center_y, distance=80):
        dx = self.x - player_center_x
        dy = self.y - player_center_y
        return (dx * dx + dy * dy) <= distance * distance

class DroneNPC:
    def __init__(self, image, world_x, world_y, dialogue):
        self.image = image
        self.world_x = world_x
        self.world_y = world_y
        self.dialogue = dialogue
        self.near_radius = 120

    def is_player_near(self, player_world_x, player_world_y):
        dx = player_world_x - self.world_x
        dy = player_world_y - self.world_y
        return (dx*dx + dy*dy) <= (self.near_radius * self.near_radius)

    def draw(self, screen, world_offset_x, world_offset_y):
        if not self.image:
            return
        rect = self.image.get_rect(center=(self.world_x - world_offset_x,
                                           self.world_y - world_offset_y))
        screen.blit(self.image, rect)
        
class DoctorNFNPC:
    def __init__(self, image, x, y, dialogue):
        self.image = image
        self.x = x
        self.y = y
        self.dialogue = dialogue
        self.rect = self.image.get_rect(center=(x, y))
        iw, ih = self.rect.size
        rx = iw * 0.30
        ry = ih * 0.30
        self.collider = Collider(
            shape="ellipse",
            center=(0.0, 0.0),
            size=(rx, ry),
            bullet_passable=True
        )

    def draw(self, screen, world_x, world_y):
        screen_x = self.x - world_x
        screen_y = self.y - world_y
        screen.blit(self.image, (screen_x - self.rect.width // 2, screen_y - self.rect.height // 2))

    def is_player_near(self, player_center_x, player_center_y, distance=80):
        dx = self.x - player_center_x
        dy = self.y - player_center_y
        return (dx * dx + dy * dy) <= distance * distance

    def get_dialogue(self):
        return self.dialogue
    
class FieldWeapon:
    # 필드에 놓여있는 무기
    def __init__(self, weapon_class, world_x, world_y, weapon_assets, sounds, max_width=80):
        self.weapon_class = weapon_class
        temp_weapon = weapon_class.create_instance(
            weapon_assets,
            sounds,
            0,
            lambda *_: None,
            lambda *_: (0, 0)
        )
        image = temp_weapon.front_image
        iw, ih = image.get_size()
        scale = min(max_width / iw, max_width / ih)
        new_w = int(iw * scale)
        new_h = int(ih * scale)
        self.image = pygame.transform.smoothscale(image, (new_w, new_h))
        self.world_x = world_x
        self.world_y = world_y
        self.pickup_radius = 80 * PLAYER_VIEW_SCALE
        self.weapon_name = temp_weapon.name

    def is_player_near(self, player_x, player_y):
        dist = math.hypot(player_x - self.world_x, player_y - self.world_y)
        return dist <= self.pickup_radius

    def draw(self, screen, world_offset_x, world_offset_y, player_near=False):
        # 무기 이미지
        screen.blit(
            self.image,
            (
                self.world_x - world_offset_x - self.image.get_width() // 2,
                self.world_y - world_offset_y - self.image.get_height() // 2
            )
        )

        if player_near:
            tri_x = self.world_x - world_offset_x
            base_tri_y = self.world_y - world_offset_y - self.image.get_height() // 2 + 5

            time_ms = pygame.time.get_ticks()
            phase = (time_ms // 500) % 2
            anim_offset = 5 if phase == 1 else 0
            tri_y = base_tri_y + anim_offset

            text_surf = KOREAN_FONT_28.render(self.weapon_name, True, (255, 255, 255))

            padding_x = 6
            padding_y = 4
            bg_rect = pygame.Rect(0, 0, text_surf.get_width() + padding_x * 2, text_surf.get_height() + padding_y * 2)
            bg_rect.center = (tri_x, base_tri_y - 40)
            pygame.draw.rect(screen, (0, 0, 0), bg_rect, border_radius=4)

            text_rect = text_surf.get_rect(center=bg_rect.center)
            screen.blit(text_surf, text_rect)

            points = [
                (tri_x, tri_y),
                (tri_x - 10, tri_y - 15),
                (tri_x + 10, tri_y - 15)
            ]
            pygame.draw.polygon(screen, (255, 255, 255), points)

class Portal:
    # 보스 처치 후 등장하는 포탈
    def __init__(self, x, y, image):
        self.x = x
        self.y = y
        self.image = image
        self.spawn_ms = pygame.time.get_ticks()
        self.appear_duration = 600
        self.scale_start = 0.6
        self.scale_end = 3.0
        self.alpha_target = 200
        self.angle = 0.0
        self.rot_speed = 120.0
        self.near_radius = 150 * PLAYER_VIEW_SCALE

    def is_player_near(self, player_x, player_y):
        dx = player_x - self.x
        dy = player_y - self.y
        return (dx * dx + dy * dy) <= (self.near_radius * self.near_radius)

    def _appear_lerp(self):
        # 0~1로 보간 비율 반환
        elapsed = pygame.time.get_ticks() - self.spawn_ms
        if elapsed <= 0:
            return 0.0
        if elapsed >= self.appear_duration:
            return 1.0
        return elapsed / self.appear_duration

    def update(self, dt_seconds):
        # 회전만 지속
        self.angle = (self.angle + self.rot_speed * dt_seconds) % 360.0

    def draw(self, screen, world_offset_x, world_offset_y, player_near=False):
        t = self._appear_lerp()
        scale = self.scale_start + (self.scale_end - self.scale_start) * t
        alpha = int(self.alpha_target * t)

        # 스케일 → 회전
        base = self.image
        w = max(1, int(base.get_width() * scale))
        h = max(1, int(base.get_height() * scale))
        scaled = pygame.transform.smoothscale(base, (w, h))
        rotated = pygame.transform.rotate(scaled, -self.angle)  # 시계 방향
        rotated.set_alpha(alpha)

        screen_x = int(self.x - world_offset_x)
        screen_y = int(self.y - world_offset_y)
        rect = rotated.get_rect(center=(screen_x, screen_y))
        screen.blit(rotated, rect)

        if player_near:
            # 안내 텍스트: "다음 스테이지 이동\n(Space)"
            line1 = KOREAN_FONT_28.render("다음 스테이지 이동", True, (255, 255, 255))
            line2 = KOREAN_FONT_28.render("(Space)", True, (200, 200, 255))
            padding_x, padding_y = 8, 6
            width = max(line1.get_width(), line2.get_width()) + padding_x * 2
            height = line1.get_height() + line2.get_height() + padding_y * 3
            bg = pygame.Surface((width, height), pygame.SRCALPHA)
            pygame.draw.rect(bg, (0, 0, 0, 160), bg.get_rect(), border_radius=6)
            # 텍스트 배치
            bg.blit(line1, ( (width - line1.get_width())//2, padding_y ))
            bg.blit(line2, ( (width - line2.get_width())//2, padding_y + line1.get_height() + 6 ))
            # 포탈 위로 살짝 띄워서 표기
            screen.blit(bg, (screen_x - width//2, screen_y - h//2 - height - 10))

class ParticleBlood:
    # 피가 튀는 파티클 이펙트
    def __init__(self, x, y, scale=1.0):
        # 파티클 초기 생성
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
        # 파티클 이동 및 알파값 감소 처리
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
        # 화면에 파티클 그리기
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
    # 플레이어가 획득할 수 있는 드롭 아이템
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
        # 상태별 이동 처리 (spread, idle, magnet)
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
        # 플레이어 근처인지 확인
        px, py = self.get_player_pos()
        return math.hypot(self.x - px, self.y - py) < 30

    def draw(self, screen, world_x, world_y):
        # 아이템 및 궤적(trail) 그리기
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

class ShieldEffect:
    def __init__(self, owner, radius, max_hp, regen_delay_ms=5000):
        self.owner = owner
        self.radius = radius
        self.max_hp = max_hp
        self.hp = max_hp
        self.regen_delay_ms = regen_delay_ms
        self.last_hit_time = 0
        self.is_broken = False  # 쉴드 파괴 여부

    def take_damage(self, damage):
        now = pygame.time.get_ticks()

        if self.hp > 0:
            self.hp -= damage
            if self.hp <= 0:
                self.hp = 0
                self.is_broken = True
                if hasattr(self.owner, "shield_break_sound"):
                    self.owner.shield_break_sound.play()
        # 쉴드가 깨진 상태에서도 타이머 무조건 갱신
        self.last_hit_time = now

    def update(self):
        now = pygame.time.get_ticks()

        # 보호막이 남아있고, 완충이 필요한 경우
        if self.hp > 0 and self.hp < self.max_hp:
            if now - self.last_hit_time >= self.regen_delay_ms:
                self.hp = self.max_hp
                if hasattr(self.owner, "shield_charged_sound"):
                    self.owner.shield_charged_sound.play()

        # 보호막이 깨진 경우, 재생성 조건
        elif self.hp <= 0 and self.is_broken:
            if now - self.last_hit_time >= self.regen_delay_ms:
                self.hp = self.max_hp
                self.is_broken = False
                if hasattr(self.owner, "shield_charged_sound"):
                    self.owner.shield_charged_sound.play()

    def draw(self, screen, world_offset_x, world_offset_y):
        if self.hp <= 0:
            return

        ratio = self.hp / self.max_hp
        if ratio > 0.5:
            t = (ratio - 0.5) * 2
            r = int(128 * (1 - t) + 0 * t)  # 파랑 → 보라
            g = 0
            b = int(128 * (1 - t) + 255 * t)
        else:
            t = ratio * 2
            r = int(255 * (1 - t) + 80 * t)  # 보라 → 빨강
            g = 0
            b = int(0 * (1 - t) + 80 * t)

        shield_color = (r, g, b, 128)  # 투명도 50%
        px = int(self.owner.world_x - world_offset_x)
        py = int(self.owner.world_y - world_offset_y)
        draw_radius = int(self.radius * 1.3)

        shield_surf = pygame.Surface((draw_radius * 2, draw_radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(shield_surf, shield_color, (draw_radius, draw_radius), draw_radius)
        screen.blit(shield_surf, (px - draw_radius, py - draw_radius))

class Bullet:
    # 직선으로 날아가는 기본 탄환
    def __init__(self, world_x, world_y, target_world_x, target_world_y,
                 spread_angle_degrees, bullet_image, speed=30, max_distance=500, damage=10):
        # 탄환 초기 위치, 속도, 충돌체 설정
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
        # 탄환 이동 및 충돌 처리
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
        # 탄환 궤적 및 본체 그리기
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

class Grenade:
    # 발사 후 일정 거리 또는 충돌 시 폭발하는 유탄/로켓
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
        # 비행 중 이동, 충돌 시 폭발 처리
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
        # 폭발 처리, 피해 적용
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
                enemy.hit(damage, config.blood_effects)

                if not enemy.alive:
                    if enemy in config.all_enemies:
                        config.all_enemies.remove(enemy)
                    config.blood_effects.append(
                        ScatteredBlood(enemy.world_x, enemy.world_y)
                    )

    def draw(self, screen, world_x, world_y):
        # 비행 중 유탄 또는 폭발 이펙트 그리기
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

class PressureBullet:
    # 폭발과 넉백 효과를 주는 특수 탄환
    def __init__(self, x, y, vx, vy, image, explosion_radius, damage, knockback_distance, explosion_sound):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.image = image
        self.rect = self.image.get_rect(center=(x, y))
        self.explosion_radius = explosion_radius
        self.damage = damage
        self.knockback_distance = knockback_distance
        self.explosion_sound = explosion_sound

        self.speed = 10 * config.PLAYER_VIEW_SCALE
        self.max_distance = 1000 * config.PLAYER_VIEW_SCALE
        self.travelled_distance = 0

        self.to_remove = False
        self.trail_enabled = True

        from collider import Collider
        radius = max(self.image.get_width(), self.image.get_height()) // 2
        self.collider = Collider(
            shape="circle",
            center=(self.rect.width / 2, self.rect.height / 2),
            size=radius,
            bullet_passable=True
        )

    def update(self, obstacle_manager):
        # 탄환 이동 및 충돌 시 폭발
        self.x += self.vx * self.speed
        self.y += self.vy * self.speed
        self.travelled_distance += math.hypot(self.vx * self.speed, self.vy * self.speed)
        self.rect.center = (self.x, self.y)

        for obs in obstacle_manager.static_obstacles + obstacle_manager.combat_obstacles:
            for collider in obs.colliders:
                if getattr(collider, "bullet_passable", False):
                    continue
                if collider.check_collision_circle((self.x, self.y), self.rect.width / 2, (obs.world_x, obs.world_y)):
                    self.explode()
                    return

        if self.travelled_distance >= self.max_distance:
            self.explode()
            return

        for enemy in config.all_enemies:
            if not enemy.alive:
                continue
            dx = enemy.world_x - self.x
            dy = enemy.world_y - self.y
            dist = math.hypot(dx, dy)
            if dist <= enemy.radius:
                self.explode()
                return

    def explode(self):
        # 폭발 처리 및 넉백 적용
        if self.explosion_sound:
            self.explosion_sound.play()

        for enemy in list(config.all_enemies):
            if not enemy.alive:
                continue

            dx = enemy.world_x - self.x
            dy = enemy.world_y - self.y
            dist = math.hypot(dx, dy)

            if dist <= self.explosion_radius:
                enemy.hit(self.damage, config.blood_effects)

                if enemy.hp <= 0:
                    enemy.alive = False
                    enemy.radius = 0
                    if hasattr(enemy, "colliders"):
                        enemy.colliders = []
                    if enemy in config.all_enemies:
                        config.all_enemies.remove(enemy)
                    continue

                if config.combat_state:
                    if dist > 0:
                        nx = dx / dist
                        ny = dy / dist
                    else:
                        nx, ny = 0, 0

                    enemy.knockback_velocity_x = nx * (self.knockback_distance / 10)
                    enemy.knockback_velocity_y = ny * (self.knockback_distance / 10)
                    enemy.knockback_steps = 10

        self.to_remove = True

    def draw(self, screen, world_offset_x, world_offset_y):
        screen.blit(
            self.image,
            (self.x - world_offset_x - self.image.get_width() / 2,
             self.y - world_offset_y - self.image.get_height() / 2)
        )

class Fireball:
    # 화염구 투사체: 직격 피해와 짧은 화상 DOT를 주는 발사체
    def __init__(self, x, y, vx, vy, damage, burn_damage, burn_duration, image):
        self.x = x
        self.y = y
        self.vx = vx * PLAYER_VIEW_SCALE
        self.vy = vy * PLAYER_VIEW_SCALE
        self.damage = damage
        self.burn_damage = burn_damage
        self.burn_duration = burn_duration
        self.image = image
        self.angle_degrees = math.degrees(math.atan2(vy, vx))
        self.collider = Collider("circle", center=(x, y), size=image.get_width() // 4)
        self.owner = None
        self.to_remove = False

        self.hit_player = False
        self.hit_start_time = 0
        self.last_burn_tick = 0

    def update(self, obstacle_manager):
        # 비행, 충돌 판정, 플레이어 명중 시 DOT 처리
        if not self.hit_player:
            self.x += self.vx
            self.y += self.vy
            self.collider.center = (self.x, self.y)

            px, py = config.world_x + config.player_rect.centerx, config.world_y + config.player_rect.centery
            if math.hypot(px - self.x, py - self.y) <= self.collider.size:
                if self.owner and hasattr(self.owner, "damage_player"):
                    self.owner.damage_player(self.damage)
                self.hit_player = True
                self.hit_start_time = pygame.time.get_ticks()
                self.last_burn_tick = self.hit_start_time
                return

            for obs in obstacle_manager.static_obstacles + obstacle_manager.combat_obstacles:
                for c in obs.colliders:
                    if c.check_collision_circle((self.x, self.y), self.collider.size, (obs.world_x, obs.world_y)):
                        if not getattr(c, "bullet_passable", False):
                            self.to_remove = True
                            return
        else:
            now = pygame.time.get_ticks()
            if now - self.hit_start_time <= self.burn_duration:
                if now - self.last_burn_tick >= 500:
                    if self.owner and hasattr(self.owner, "damage_player"):
                        self.owner.damage_player(self.burn_damage)
                    self.last_burn_tick = now
            else:
                self.to_remove = True

    def draw(self, screen, world_x, world_y):
        scale_factor = 50 / self.image.get_width()
        scaled_w = int(self.image.get_width() * scale_factor)
        scaled_h = int(self.image.get_height() * scale_factor)
        scaled_img = pygame.transform.smoothscale(self.image, (scaled_w, scaled_h))
        rotated = pygame.transform.rotate(scaled_img, -self.angle_degrees)
        rect = rotated.get_rect(center=(self.x - world_x, self.y - world_y))
        screen.blit(rotated, rect)

class FlamePillar:
    # 지연 후 활성화되어 범위 피해를 주는 불기둥
    def __init__(self, center_x, center_y, radius, delay, duration, damage_tick, image, warning_color):
        self.cx = center_x
        self.cy = center_y
        self.radius = int(radius * 0.8)
        self.delay = delay
        self.duration = int(duration * 1.5)
        self.damage_tick = damage_tick
        self.image = image
        self.warning_color = warning_color
        self.spawn_time = pygame.time.get_ticks()
        self.active = False
        self.finished = False
        self.last_damage_time = 0
        self.start_time = None

        self.grow_time = 50
        self.fade_time = 50

    def update(self):
        # 활성화/지속 시간 관리, 범위 내 플레이어 피해 적용
        now = pygame.time.get_ticks()
        elapsed = now - self.spawn_time

        if not self.active:
            if elapsed >= self.delay:
                self.active = True
                self.start_time = now
        else:
            life_elapsed = now - self.start_time
            if life_elapsed >= self.duration:
                self.finished = True
                return

            px, py = config.world_x + config.player_rect.centerx, config.world_y + config.player_rect.centery
            if math.hypot(px - self.cx, py - self.cy) <= self.radius:
                if now - self.last_damage_time >= 500:
                    if hasattr(config, "damage_player"):
                        config.damage_player(self.damage_tick)
                    self.last_damage_time = now

    def draw(self, screen, world_x, world_y):
        # 경고 원과 불기둥 이미지를 상황에 맞게 표시
        if not self.active:
            warn_surf = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(warn_surf, self.warning_color, (self.radius, self.radius), self.radius)
            screen.blit(warn_surf, (self.cx - self.radius - world_x, self.cy - self.radius - world_y))
        else:
            now = pygame.time.get_ticks()
            life_elapsed = now - self.start_time
            progress = life_elapsed / self.duration

            if life_elapsed < self.grow_time:
                scale_factor = life_elapsed / self.grow_time
                alpha = int(255 * scale_factor)
            elif self.duration - life_elapsed < self.fade_time:
                scale_factor = (self.duration - life_elapsed) / self.fade_time
                alpha = int(255 * scale_factor)
            else:
                scale_factor = 1.0
                alpha = 255

            size = max(1, int(self.radius * 2 * scale_factor))
            scaled_img = pygame.transform.smoothscale(self.image, (size, size))
            scaled_img.set_alpha(alpha)

            rect = scaled_img.get_rect(center=(self.cx - world_x, self.cy - world_y))
            screen.blit(scaled_img, rect)

class TeleportFlash:
    # 순간이동 시 잠깐 표시되는 붉은 번쩍임 효과
    def __init__(self, x, y, color=(255, 50, 50), duration=250):
        self.x = x
        self.y = y
        self.color = color
        self.duration = duration
        self.start_time = pygame.time.get_ticks()
        self.finished = False

    def update(self):
        if pygame.time.get_ticks() - self.start_time >= self.duration:
            self.finished = True

    def draw(self, screen, world_x, world_y):
        alpha = max(0, 255 - int(255 * ((pygame.time.get_ticks() - self.start_time) / self.duration)))
        surf = pygame.Surface((80, 80), pygame.SRCALPHA)
        pygame.draw.circle(surf, (*self.color, alpha), (40, 40), 40)
        screen.blit(surf, (self.x - 40 - world_x, self.y - 40 - world_y))

class GrenadeProjectile:
    # 발사 후 일정 시간 뒤 폭발하는 수류탄 투사체
    def __init__(self, x, y, vx, vy, speed, image, explosion_radius, max_damage, min_damage,
                 explosion_image, explosion_sound, explosion_delay=1500, owner=None):
        self.x = x
        self.y = y
        self.vx = vx * speed * config.PLAYER_VIEW_SCALE
        self.vy = vy * speed * config.PLAYER_VIEW_SCALE
        if owner is not None:
            self.image = image.copy()
            self.image.fill((255, 0, 0, 255), special_flags=pygame.BLEND_RGBA_MULT)
        else:
            self.image = image
        self.start_time = pygame.time.get_ticks()
        self.explosion_delay = explosion_delay
        self.owner = owner
        self.scale = 1.0
        self.explosion_radius = explosion_radius
        self.max_damage = max_damage
        self.min_damage = min_damage
        self.damage = max_damage
        self.explosion_image = explosion_image
        self.explosion_sound = explosion_sound
        self.collider = Collider("circle", center=(x, y), size=image.get_width() // 2)
        self.alive = True

    def update(self, obstacle_manager):
        # 투사체 이동 및 폭발 타이머 관리
        if not self.alive:
            return

        elapsed = pygame.time.get_ticks() - self.start_time

        self.x += self.vx
        self.y += self.vy
        self.collider.center = (self.x, self.y)

        t = (elapsed % 500) / 500
        self.scale = 1.0 + 0.3 * math.sin(t * math.pi)

        if elapsed >= self.explosion_delay:
            if not getattr(self, "ignore_enemy_collision", False):
                for enemy in config.all_enemies:
                    if enemy is self.owner:
                        continue
                    if not getattr(enemy, "alive", True):
                        continue
                    dist = math.hypot(enemy.world_x - self.x, enemy.world_y - self.y)
                    if dist <= self.collider.size:
                        self.explode()
                        return
            if obstacle_manager:
                for obs in obstacle_manager.placed_obstacles + obstacle_manager.static_obstacles + obstacle_manager.combat_obstacles:
                    for c in obs.colliders:
                        if c.check_collision_circle((self.x, self.y), self.collider.size, (obs.world_x, obs.world_y)):
                            if not getattr(c, "bullet_passable", False):
                                self.explode()
                                return
            self.explode()

    def explode(self):
        # 폭발 처리 및 범위 피해 적용
        if not self.alive:
            return
        self.alive = False
        self.explosion_sound.play()
        config.bullets.append(ExplosionEffectPersistent(self.x, self.y, self.explosion_image))

        if not config.combat_state:
            return
        
        px, py = config.world_x + config.player_rect.centerx, config.world_y + config.player_rect.centery
        dist_player = math.hypot(px - self.x, py - self.y)
        if dist_player <= self.explosion_radius:
            factor = max(0, min(1, 1 - dist_player / self.explosion_radius))
            damage = self.min_damage + (self.max_damage - self.min_damage) * factor
            if hasattr(config, "damage_player"):
                config.damage_player(damage)

        for enemy in config.all_enemies[:]:
            if not getattr(enemy, "alive", True):
                continue
            dist = math.hypot(enemy.world_x - self.x, enemy.world_y - self.y)
            if dist <= self.explosion_radius:
                factor = max(0, min(1, 1 - dist / self.explosion_radius))
                damage = self.min_damage + (self.max_damage - self.min_damage) * factor
                enemy.hit(damage, config.blood_effects)
                if not enemy.alive:
                    if enemy in config.all_enemies:
                        config.all_enemies.remove(enemy)
                    config.blood_effects.append(ScatteredBlood(enemy.world_x, enemy.world_y))

    def draw(self, screen, world_x, world_y):
        # 화면에 수류탄 투사체를 크기 변화와 함께 그림
        if not self.alive:
            return
        size = int(self.image.get_width() * self.scale)
        img_scaled = pygame.transform.smoothscale(self.image, (size, size))
        rect = img_scaled.get_rect(center=(self.x - world_x, self.y - world_y))
        screen.blit(img_scaled, rect)

class AcidPool:
    # 일정 시간 동안 DOT 피해를 주는 산성 웅덩이
    def __init__(self, x, y, image, radius, dot_damage, duration, sounds=None):
        self.x = x
        self.y = y
        self.base_image = image
        self.radius = radius
        self.dot_damage = dot_damage
        self.start_time = pygame.time.get_ticks()
        self.duration = duration
        self.alive = True
        self.sounds = sounds
        self.last_dot_time = 0

    def update(self):
        # DOT 적용 주기 체크 및 플레이어 범위 판정
        elapsed = pygame.time.get_ticks() - self.start_time
        if elapsed > self.duration:
            self.alive = False
            return
        px, py = config.world_x + config.player_rect.centerx, config.world_y + config.player_rect.centery
        if math.hypot(px - self.x, py - self.y) <= self.radius:
            now = pygame.time.get_ticks()
            if now - self.last_dot_time >= 100:
                config.active_dots.append({"damage": self.dot_damage, "end_time": now + 100})
                self.last_dot_time = now

    def draw(self, screen, world_x, world_y):
        # 페이드 인/아웃 + 크기 변화 이펙트로 웅덩이 렌더링
        elapsed = pygame.time.get_ticks() - self.start_time
        progress = elapsed / self.duration
        if progress < 0.2:
            alpha = int(255 * (progress / 0.2))
            scale_factor = 0.5 + 0.5 * (progress / 0.2)
        elif progress > 0.8:
            alpha = int(255 * ((1 - progress) / 0.2))
            scale_factor = 1.0 - 0.5 * ((progress - 0.8) / 0.2)
        else:
            alpha = 255
            scale_factor = 1.0

        new_width = int(self.base_image.get_width() * scale_factor)
        new_height = int(self.base_image.get_height() * scale_factor)
        scaled_img = pygame.transform.smoothscale(self.base_image, (new_width, new_height)).copy()
        scaled_img.set_alpha(alpha)

        rect = scaled_img.get_rect(center=(self.x - world_x, self.y - world_y))
        screen.blit(scaled_img, rect)

class AcidProjectile:
    # 비행 후 충돌 시 산성 웅덩이를 생성하는 투사체
    def __init__(self, x, y, vx, vy, speed, image, pool_image, max_damage, dot_damage, dot_duration, owner=None, sounds=None):
        self.x = x
        self.y = y
        self.vx = vx * speed * PLAYER_VIEW_SCALE
        self.vy = vy * speed * PLAYER_VIEW_SCALE
        self.image = image.copy()
        self.image.fill((0, 100, 0, 255), special_flags=pygame.BLEND_RGBA_MULT)
        self.pool_image = pool_image.copy()
        self.pool_image.fill((0, 100, 0, 255), special_flags=pygame.BLEND_RGBA_MULT)
        self.max_damage = max_damage
        self.damage = max_damage
        self.dot_damage = dot_damage
        self.dot_duration = dot_duration
        self.owner = owner
        self.sounds = sounds
        self.radius = image.get_width() // 2
        self.collider = Collider("circle", center=(x, y), size=self.radius)
        self.to_remove = False
        self.direction_angle = math.atan2(vy, vx)

    def update(self, obstacle_manager):
        # 이동 및 충돌 처리
        if self.to_remove:
            return
        self.x += self.vx
        self.y += self.vy
        self.collider.center = (self.x, self.y)

        # 플레이어 명중 시 피해 + DOT 부여 + 웅덩이 생성
        px, py = config.world_x + config.player_rect.centerx, config.world_y + config.player_rect.centery
        if math.hypot(px - self.x, py - self.y) <= self.radius:
            config.damage_player(self.max_damage)
            config.active_dots.append({"damage": self.dot_damage, "end_time": pygame.time.get_ticks() + self.dot_duration})
            pool = AcidPool(self.x, self.y, self.pool_image, 150, self.dot_damage, 3000)
            if self.sounds:
                pool.sounds = self.sounds
            config.effects.append(pool)
            self.to_remove = True
            return

        # 장애물 충돌 시 웅덩이 생성
        for obs in obstacle_manager.static_obstacles + obstacle_manager.combat_obstacles:
            for c in obs.colliders:
                if c.compute_penetration_circle((self.x, self.y), self.radius, (obs.world_x, obs.world_y)):
                    pool = AcidPool(self.x, self.y, self.pool_image, 150, self.dot_damage, 3000)
                    if self.sounds:
                        pool.sounds = self.sounds
                    config.effects.append(pool)
                    self.to_remove = True
                    return

    # 진행 방향 회전 이미지로 투사체 렌더링
    def draw(self, screen, world_x, world_y):
        rotated_img = pygame.transform.rotate(self.image, -math.degrees(self.direction_angle))
        rect = rotated_img.get_rect(center=(self.x - world_x, self.y - world_y))
        screen.blit(rotated_img, rect)

class ExplosionEffectPersistent:
    # 일정 시간 지속되는 폭발 시각 효과
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

        self._pause_total = 0.0
        self._pause_start = None

    def pause(self):
        if self._pause_start is None:
            self._pause_start = time.time()

    def resume(self):
        self._pause_start = None
        self.finished = True

    def update(self):
        # 크기, 투명도 업데이트
        if self._pause_start is not None:
            return

        elapsed = (time.time() - self.start_time) - self._pause_total

        if elapsed >= self.duration:
            self.finished = True
            return

        ratio = 1 - (elapsed / self.duration)
        self.alpha = int(255 * ratio)
        self.scale = 1.5 * ratio

    def draw(self, screen, world_x, world_y):
        # 폭발 이미지를 화면에 그림
        self.drawn_once = True
        size = int(self.image.get_width() * self.scale)
        scaled = pygame.transform.smoothscale(self.image, (size, size)).copy()
        scaled.set_alpha(self.alpha)
        screen.blit(scaled, (self.x - size // 2 - world_x, self.y - size // 2 - world_y))

class HomingMissile:
    # 유도 기능이 있는 미사일 투사체
    def __init__(self, x, y, target, image, explosion_radius, damage, explosion_image, explosion_sound,
                 live_tracking=False, turn_rate=0.02, max_distance=500):
        self.x = x
        self.y = y
        self.image = image
        self.target = target
        self.explosion_radius = explosion_radius
        self.damage = damage
        self.explosion_image = explosion_image
        self.explosion_sound = explosion_sound

        self.live_tracking = live_tracking
        self.speed = 6 * config.PLAYER_VIEW_SCALE
        self.turn_rate = turn_rate
        self.angle = math.atan2(
            (target[1] - y) if target else 0,
            (target[0] - x) if target else 1
        )

        self.start_time = pygame.time.get_ticks()
        self.straight_time = 500
        self.spawn_protect_time = 300

        self.start_x = x
        self.start_y = y
        self.max_distance = max_distance

        self.collider = Collider("circle", center=(x, y), size=image.get_width() // 2)
        self.to_remove = False
        self.drawn_once = False
        self.owner = None

    def update(self, obstacle_manager=None):
        # 목표 추적, 회전 각도 변경, 충돌 및 사거리 초과 시 폭발
        now = pygame.time.get_ticks()

        if self.live_tracking:
            self.target = (
                config.world_x + config.player_rect.centerx,
                config.world_y + config.player_rect.centery
            )

        if now - self.start_time > self.straight_time and self.target:
            desired_angle = math.atan2(self.target[1] - self.y, self.target[0] - self.x)
            diff = (desired_angle - self.angle + math.pi) % (2 * math.pi) - math.pi
            self.angle += max(-self.turn_rate, min(self.turn_rate, diff))

        self.x += math.cos(self.angle) * self.speed
        self.y += math.sin(self.angle) * self.speed
        self.collider.center = (self.x, self.y)

        if math.hypot(self.x - self.start_x, self.y - self.start_y) >= self.max_distance:
            self.explode()
            return

        if now - self.start_time >= self.spawn_protect_time:
            px, py = config.world_x + config.player_rect.centerx, config.world_y + config.player_rect.centery
            if math.hypot(px - self.x, py - self.y) <= self.image.get_width() / 2:
                self.explode()
                return
            
        if obstacle_manager:
            for obs in obstacle_manager.placed_obstacles + obstacle_manager.static_obstacles + obstacle_manager.combat_obstacles:
                for c in obs.colliders:
                    if c.check_collision_circle((self.x, self.y), self.image.get_width() / 2, (obs.world_x, obs.world_y)):
                        if not getattr(c, "bullet_passable", False):
                            self.explode()
                            return

    def explode(self):
        # 폭발 처리, 폭발 이펙트 생성 및 범위 피해 적용
        effect = ExplosionEffectPersistent(self.x, self.y, self.explosion_image)
        config.bullets.append(effect)

        px, py = config.world_x + config.player_rect.centerx, config.world_y + config.player_rect.centery
        if math.hypot(px - self.x, py - self.y) <= self.explosion_radius:
            if self.owner and hasattr(self.owner, "damage_player"):
                self.owner.damage_player(self.damage)
        self.explosion_sound.play()

        self.to_remove = True

    def draw(self, screen, world_x, world_y):
        # 미사일 회전 이미지 그리기
        rotated = pygame.transform.rotate(self.image, -math.degrees(self.angle))
        rect = rotated.get_rect(center=(self.x - world_x, self.y - world_y))
        screen.blit(rotated, rect)
        self.drawn_once = True

class ScatteredBullet:
    # 발사 시 배출되는 탄피/파편 이펙트
    def __init__(self, x, y, vx, vy, bullet_image, scale=1.0):
        w, h = bullet_image.get_size()
        self.image_original = pygame.transform.smoothscale(
            bullet_image,
            (int(w * scale), int(h * scale))
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
        # 이동, 회전, 알파값 업데이트
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
        # 탄피/파편을 화면에 그림
        if self.alpha > 0:
            screen_x = self.pos[0] - world_x
            screen_y = self.pos[1] - world_y
            rect = self.image.get_rect(center=(screen_x, screen_y))
            screen.blit(self.image, rect)


class ScatteredBlood:
    # 적 피가 사방으로 튀는 이펙트
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
        # 파편 이동 및 알파값 감소
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
        # 피 파편 그리기
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
    # 맵 상의 장애물(나무, 바위 등)
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
        # 투명 처리 여부 계산 후 이미지 그리기
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