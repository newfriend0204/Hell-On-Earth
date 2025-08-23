import pygame
import random
import math
from entities import Bullet, ScatteredBullet
import config
import os

class MeleeController:
    # V키로 발동하는 근접 공격. 총기와 별도(현재 무기 유지).
    DAMAGE = 20
    ARC_DEG = 30
    RANGE = int(100 * config.PLAYER_VIEW_SCALE)
    DURATION = 220
    HIT_MOMENT = 0.45
    OUT_OFFSET = 42

    def __init__(self, images, sounds, get_player_world_pos_fn):
        import pygame
        self.images = images
        self.sounds = sounds
        self.get_player_world_pos = get_player_world_pos_fn
        self.active = False
        self._start_ms = 0
        self._hit_done = False

    def try_start(self, is_switching_weapon=False):
        # 무기 교체 중엔 금지.
        if self.active or is_switching_weapon:
            return False
        self.active = True
        self._start_ms = pygame.time.get_ticks()
        self._hit_done = False
        s = self.sounds
        if isinstance(s, dict) and "knife_use" in s:
            try:
                s["knife_use"].play()
            except:
                pass
        return True

    def _unit_from_mouse(self):
        import pygame, math
        mx, my = pygame.mouse.get_pos()
        dx = mx - config.player_rect.centerx
        dy = my - config.player_rect.centery
        d = math.hypot(dx, dy)
        if d < 1e-6:
            return (1.0, 0.0), 0.0
        return (dx / d, dy / d), math.atan2(dy, dx)

    def _hit_test(self, enemies, blood_effects):
        # 가장 가까운 한 명만 피격.
        import math
        (px, py) = self.get_player_world_pos()
        (fx, fy), aim = self._unit_from_mouse()
        half = math.radians(self.ARC_DEG / 2)

        nearest = None
        nearest_dist = 1e9
        for e in enemies:
            if not getattr(e, "alive", False):
                continue
            ex, ey = getattr(e, "world_x", None), getattr(e, "world_y", None)
            if ex is None:
                continue
            dx, dy = (ex - px), (ey - py)
            dist = math.hypot(dx, dy)
            if dist > self.RANGE + getattr(e, "radius", 0):
                continue
            ang = math.atan2(dy, dx)
            diff = (ang - aim + math.pi * 3) % (2 * math.pi) - math.pi
            if abs(diff) > half:
                continue
            if dist < nearest_dist:
                nearest, nearest_dist = e, dist

        if nearest is None:
            return

        was_alive = getattr(nearest, "alive", False)
        if hasattr(nearest, "hit"):
            nearest.hit(self.DAMAGE, blood_effects, force=True)
        else:
            hp = getattr(nearest, "hp", 20)
            setattr(nearest, "hp", max(0, hp - self.DAMAGE))
            if getattr(nearest, "hp", 0) <= 0:
                setattr(nearest, "alive", False)

        try:
            if hasattr(nearest, "spawn_dropped_items"):
                nearest.spawn_dropped_items(0, 1)
            else:
                from entities import DroppedItem
                get_player_pos = lambda: (config.world_x + config.player_rect.centerx,
                                          config.world_y + config.player_rect.centery)
                img = config.images["ammo_gauge_up"]
                for _ in range(2):
                    config.dropped_items.append(
                        DroppedItem(nearest.world_x, nearest.world_y, img, "ammo", 20, get_player_pos)
                    )
        except Exception:
            pass

        if was_alive and not getattr(nearest, "alive", True):
            if isinstance(self.sounds, dict) and "knife_kill" in self.sounds:
                try:
                    self.sounds["knife_kill"].play()
                except:
                    pass

    def update(self, enemies, blood_effects):
        if not self.active:
            return
        import pygame
        t = (pygame.time.get_ticks() - self._start_ms) / self.DURATION
        if (not self._hit_done) and t >= self.HIT_MOMENT:
            self._hit_done = True
            self._hit_test(enemies, blood_effects)
        if t >= 1.0:
            self.active = False

    def draw(self, screen, world_offset_xy):
        # 칼 스프라이트를 플레이어 중심에서 마우스 방향으로 전진->복귀.
        if not self.active:
            return
        import pygame, math
        (px, py) = self.get_player_world_pos()
        (_, _), ang = self._unit_from_mouse()
        now = pygame.time.get_ticks()
        t = max(0.0, min(1.0, (now - self._start_ms) / self.DURATION))
        off = self.OUT_OFFSET * (1 - abs(2 * t - 1))
        nx = px - world_offset_xy[0] + math.cos(ang) * off
        ny = py - world_offset_xy[1] + math.sin(ang) * off
        img = self.images.get("knife")
        if img is None:
            return
        rot = pygame.transform.rotate(img, -math.degrees(ang) - 90)
        rect = rot.get_rect(center=(nx, ny))
        screen.blit(rot, rect)

class WeaponBase:
    # 모든 무기 클래스의 공통 부모 클래스
    # 발사 속도, 탄약 소모, 반동, 스프레드, 발사 사운드, 탄피 배출 등 기본 기능 제공
    def __init__(
        self,
        name,
        front_image,
        topdown_image,
        uses_bullets,
        bullet_images,
        uses_cartridges,
        cartridge_images,
        can_left_click,
        can_right_click,
        left_click_ammo_cost,
        right_click_ammo_cost,
        tier,
        sounds_dict,
        get_ammo_gauge_fn,
        reduce_ammo_fn,
        bullet_has_trail,
        get_player_world_position_fn,
        exclusive_inputs=False,
    ):
        self.name = name
        self.front_image = front_image
        self.topdown_image = topdown_image
        self.uses_bullets = uses_bullets
        self.bullet_images = bullet_images or []
        self.uses_cartridges = uses_cartridges
        self.cartridge_images = cartridge_images or []
        self.can_left_click = can_left_click
        self.can_right_click = can_right_click
        self.left_click_ammo_cost = left_click_ammo_cost
        self.right_click_ammo_cost = right_click_ammo_cost
        self.tier = tier
        self.sounds = sounds_dict
        self.get_ammo_gauge = get_ammo_gauge_fn
        self.reduce_ammo = reduce_ammo_fn
        self.bullet_has_trail = bullet_has_trail
        self.last_shot_time = 0
        self.fire_delay = 300
        self.get_player_world_position = get_player_world_position_fn
        self.shake_strength = 10
        self.exclusive_inputs = bool(exclusive_inputs)
        self._active_button = None   # 'L' | 'R' | None
        self._prev_left_down = False
        self._prev_right_down = False

    def _filter_inputs(self, left_down: bool, right_down: bool):
        # 배타 입력 규칙을 적용해 이번 프레임에 허용되는 (left, right) 입력을 리턴.
        # active 버튼이 잡혀 있으면 그 버튼만 허용
        # 둘 다 눌렸을 때는 '먼저 눌린' 버튼을 유지(동시 에지는 좌 우선)
        if not self.exclusive_inputs:
            # 배타 처리 비활성: 그대로 통과
            self._prev_left_down, self._prev_right_down = left_down, right_down
            return left_down, right_down
        
        # 에지(이번 프레임에 새로 눌림) 계산
        left_edge = left_down and not self._prev_left_down
        right_edge = right_down and not self._prev_right_down

        # 상태 결정
        if self._active_button is None:
            left_edge = left_down and not self._prev_left_down
            right_edge = right_down and not self._prev_right_down
            if left_down and not right_down:
                self._active_button = 'L'
            elif right_down and not left_down:
                self._active_button = 'R'
            elif left_down and right_down:
                # 동시 입력: 에지가 있으면 그쪽, 없으면 좌 우선
                if left_edge and not right_edge:
                    self._active_button = 'L'
                elif right_edge and not left_edge:
                    self._active_button = 'R'
                else:
                    self._active_button = 'L'
        else:
            # 반대쪽이 "새로 눌리면" 즉시 전환
            if self._active_button == 'L' and right_edge:
                self._active_button = 'R'
            elif self._active_button == 'R' and left_edge:
                self._active_button = 'L'

            # 잡혀있던 버튼이 떼지면, 반대 버튼이 눌려있으면 전환, 아니면 해제
            if self._active_button == 'L' and not left_down:
                self._active_button = 'R' if right_down else None
            elif self._active_button == 'R' and not right_down:
                self._active_button = 'L' if left_down else None

        allow_left = left_down and (self._active_button == 'L')
        allow_right = right_down and (self._active_button == 'R')
        self._prev_left_down, self._prev_right_down = left_down, right_down
        return allow_left, allow_right

    OVERLAY_VISIBLE_WHEN_INACTIVE = False
    overlay_force_visible = False

    def should_draw_overlay(self, active_weapon):
        # 바(HEAT/CHARGE 등) 표시 여부만 판단하는 함수.
        import config
        if getattr(config, "player_dead", False):
            return False
        if getattr(config, "is_switching_weapon", False):
            return False
        if getattr(self, "overlay_force_visible", False) or getattr(self, "OVERLAY_VISIBLE_WHEN_INACTIVE", False):
            return True
        return (self is active_weapon)

    def draw_overlay(self, screen):
        # 무기 전용 HUD를 그릴 때 오버라이드
        return

    def draw_world(self, screen):
        # 월드 비주얼 훅(탄/필드/파편 등). 기본적으로 아무것도 하지 않음.
        return
    
    def on_left_click(self):
        # 좌클릭 발사 동작 (하위 클래스에서 구현)
        pass

    def on_right_click(self):
        # 우클릭 발사 동작 (하위 클래스에서 구현)
        pass
    
    def on_update(self, mouse_left_down, mouse_right_down):
        # 매 프레임마다 발사 입력을 처리 (기본 좌클릭만 담당)
        left_allowed, _ = self._filter_inputs(mouse_left_down, mouse_right_down)
        if self.can_left_click and left_allowed and pygame.time.get_ticks() - self.last_shot_time >= self.fire_delay:
            # 탄약이 충분할 때만 발사 및 반동 처리
            if self.get_ammo_gauge() >= self.left_click_ammo_cost:
                self.on_left_click()
                self.last_shot_time = pygame.time.get_ticks()
    
class Gun1(WeaponBase):
    TIER = 1
    AMMO_COST = 5
    DAMAGE = 28
    SPREAD = 8
    FIRE_DELAY = 350

    @staticmethod
    def create_instance(weapon_assets, sounds, ammo_gauge, consume_ammo, get_player_world_position):
        return Gun1(
            name="M1911",
            front_image=weapon_assets["gun1"]["front"],
            topdown_image=weapon_assets["gun1"]["topdown"],
            uses_bullets=True,
            bullet_images=weapon_assets["gun1"]["bullets"],
            uses_cartridges=True,
            cartridge_images=weapon_assets["gun1"]["cartridges"],
            can_left_click=True,
            can_right_click=False,
            left_click_ammo_cost=Gun1.AMMO_COST,
            right_click_ammo_cost=0,
            tier=Gun1.TIER,
            sounds_dict={
                "fire": sounds["gun1_fire"],
            },
            get_ammo_gauge_fn=ammo_gauge,
            reduce_ammo_fn=consume_ammo,
            bullet_has_trail=False,
            get_player_world_position_fn=get_player_world_position
        )

    def __init__(self, name, front_image, topdown_image, **kwargs):
        super().__init__(name, front_image, topdown_image, **kwargs)
        self.fire_delay = Gun1.FIRE_DELAY
        self.recoil_strength = 7
        self.speed_penalty = 0
        self.distance_from_center = config.PLAYER_VIEW_SCALE * 45
        self.shake_strength = 10

    def on_left_click(self):
        if not self.can_left_click or self.get_ammo_gauge() < self.left_click_ammo_cost:
            return

        self.reduce_ammo(self.left_click_ammo_cost)
        self.sounds["fire"].play()

        mouse_x, mouse_y = pygame.mouse.get_pos()
        player_center_x, player_center_y = self.get_player_world_position()

        dx = mouse_x - config.player_rect.centerx
        dy = mouse_y - config.player_rect.centery
        angle = math.atan2(dy, dx)
        spread = math.radians(random.uniform(-self.SPREAD / 2, self.SPREAD / 2))
        final_angle = angle + spread
        vx = math.cos(final_angle)
        vy = math.sin(final_angle)

        offset_x = vx * 30 * config.PLAYER_VIEW_SCALE
        offset_y = vy * 30 * config.PLAYER_VIEW_SCALE

        bullet_x = player_center_x + offset_x
        bullet_y = player_center_y + offset_y

        if self.bullet_images:
            # 총알 생성 및 config.bullets에 추가
            bullet = Bullet(
                bullet_x,
                bullet_y,
                bullet_x + vx * 2000,
                bullet_y + vy * 2000,
                self.SPREAD,
                self.bullet_images[0],
                speed=10 * config.PLAYER_VIEW_SCALE,
                max_distance=2000 * config.PLAYER_VIEW_SCALE,
                damage=self.DAMAGE
            )
            bullet.trail_enabled = self.bullet_has_trail
            config.bullets.append(bullet)

        if self.uses_cartridges and self.cartridge_images:
            # 탄피 배출 효과 생성
            eject_angle = angle + math.radians(90 + random.uniform(-15, 15))
            vx = math.cos(eject_angle) * 1.2
            vy = math.sin(eject_angle) * 1.2
            player_center_x, player_center_y = self.get_player_world_position()
            scatter = ScatteredBullet(
                player_center_x,
                player_center_y,
                vx,
                vy,
                self.cartridge_images[0]
            )
            config.scattered_bullets.append(scatter)

class Gun2(WeaponBase):
    TIER = 1
    AMMO_COST = 3
    DAMAGE = 18
    SPREAD = 9
    FIRE_DELAY = 150

    @staticmethod
    def create_instance(weapon_assets, sounds, ammo_gauge, consume_ammo, get_player_world_position):
        return Gun2(
            name="AK47",
            front_image=weapon_assets["gun2"]["front"],
            topdown_image=weapon_assets["gun2"]["topdown"],
            uses_bullets=True,
            bullet_images=weapon_assets["gun2"]["bullets"],
            uses_cartridges=True,
            cartridge_images=weapon_assets["gun2"]["cartridges"],
            can_left_click=True,
            can_right_click=False,
            left_click_ammo_cost=Gun2.AMMO_COST,
            right_click_ammo_cost=0,
            tier=Gun2.TIER,
            sounds_dict={
                "fire": sounds["gun2_fire"],
            },
            get_ammo_gauge_fn=ammo_gauge,
            reduce_ammo_fn=consume_ammo,
            bullet_has_trail=False,
            get_player_world_position_fn=get_player_world_position
        )

    def __init__(self, name, front_image, topdown_image, **kwargs):
        super().__init__(name, front_image, topdown_image, **kwargs)
        self.fire_delay = Gun2.FIRE_DELAY
        self.recoil_strength = 8
        self.speed_penalty = 0.10
        self.distance_from_center = config.PLAYER_VIEW_SCALE * 50
        self.shake_strength = 15

    def on_left_click(self):
        if not self.can_left_click or self.get_ammo_gauge() < self.left_click_ammo_cost:
            return
        
        # 탄약 차감 및 발사음
        self.reduce_ammo(self.left_click_ammo_cost)
        self.sounds["fire"].play()

        mouse_x, mouse_y = pygame.mouse.get_pos()
        player_center_x, player_center_y = self.get_player_world_position()
        dx = mouse_x - config.player_rect.centerx
        dy = mouse_y - config.player_rect.centery
        angle = math.atan2(dy, dx)
        spread = math.radians(random.uniform(-self.SPREAD / 2, self.SPREAD / 2))
        final_angle = angle + spread
        vx = math.cos(final_angle)
        vy = math.sin(final_angle)

        offset_x = vx * 30 * config.PLAYER_VIEW_SCALE
        offset_y = vy * 30 * config.PLAYER_VIEW_SCALE

        bullet_x = player_center_x + offset_x
        bullet_y = player_center_y + offset_y

        if self.bullet_images:
            bullet = Bullet(
                bullet_x,
                bullet_y,
                bullet_x + vx * 2000,
                bullet_y + vy * 2000,
                self.SPREAD,
                self.bullet_images[0],
                speed=10 * config.PLAYER_VIEW_SCALE,
                max_distance=2000 * config.PLAYER_VIEW_SCALE,
                damage=self.DAMAGE
            )
            bullet.trail_enabled = self.bullet_has_trail
            config.bullets.append(bullet)

        if self.uses_cartridges and self.cartridge_images:
            eject_angle = angle + math.radians(90 + random.uniform(-15, 15))
            vx = math.cos(eject_angle) * 1.2
            vy = math.sin(eject_angle) * 1.2
            scatter = ScatteredBullet(
                player_center_x,
                player_center_y,
                vx,
                vy,
                self.cartridge_images[0]
            )
            config.scattered_bullets.append(scatter)

class Gun3(WeaponBase):
    TIER = 2
    AMMO_COST = 8
    DAMAGE = 6
    FIRE_DELAY = 750
    NUM_BULLETS = 12
    SPREAD_DEGREES = 30

    @staticmethod
    def create_instance(weapon_assets, sounds, ammo_gauge, consume_ammo, get_player_world_position):
        return Gun3(
            name="Remington 870",
            front_image=weapon_assets["gun3"]["front"],
            topdown_image=weapon_assets["gun3"]["topdown"],
            uses_bullets=True,
            bullet_images=weapon_assets["gun3"]["bullets"],
            uses_cartridges=True,
            cartridge_images=weapon_assets["gun3"]["cartridges"],
            can_left_click=True,
            can_right_click=False,
            left_click_ammo_cost=Gun3.AMMO_COST,
            right_click_ammo_cost=0,
            tier=Gun3.TIER,
            sounds_dict={
                "fire": sounds["gun3_fire"],
            },
            get_ammo_gauge_fn=ammo_gauge,
            reduce_ammo_fn=consume_ammo,
            bullet_has_trail=False,
            get_player_world_position_fn=get_player_world_position
        )

    def __init__(self, name, front_image, topdown_image, **kwargs):
        super().__init__(name, front_image, topdown_image, **kwargs)
        self.fire_delay = Gun3.FIRE_DELAY
        self.recoil_strength = 9
        self.speed_penalty = 0.10
        self.distance_from_center = config.PLAYER_VIEW_SCALE * 35
        self.shake_strength = 20

    def on_left_click(self):
        if not self.can_left_click or self.get_ammo_gauge() < self.left_click_ammo_cost:
            return
        
        # 탄약 차감 및 발사음
        self.reduce_ammo(self.left_click_ammo_cost)
        self.sounds["fire"].play()

        mouse_x, mouse_y = pygame.mouse.get_pos()
        player_center_x, player_center_y = self.get_player_world_position()
        angle = math.atan2(mouse_y - config.player_rect.centery, mouse_x - config.player_rect.centerx)

        for _ in range(self.NUM_BULLETS):
            # 각 총알마다 랜덤 각도로 퍼지게 발사
            spread = math.radians(random.uniform(-self.SPREAD_DEGREES, self.SPREAD_DEGREES))
            dx = math.cos(angle + spread)
            dy = math.sin(angle + spread)

            offset_x = dx * 30 * config.PLAYER_VIEW_SCALE
            offset_y = dy * 30 * config.PLAYER_VIEW_SCALE
            bullet_x = player_center_x + offset_x
            bullet_y = player_center_y + offset_y

            if self.bullet_images:
                bullet = Bullet(
                    bullet_x,
                    bullet_y,
                    bullet_x + dx * 100,
                    bullet_y + dy * 100,
                    spread_angle_degrees=0,
                    bullet_image=self.bullet_images[0],
                    speed=7.5 * config.PLAYER_VIEW_SCALE,
                    max_distance=500 * config.PLAYER_VIEW_SCALE,
                    damage=self.DAMAGE
                )
                bullet.trail_enabled = self.bullet_has_trail
                config.bullets.append(bullet)

        if self.uses_cartridges and self.cartridge_images:
            # 샷건 탄피 배출 (크기 확대)
            eject_angle = angle + math.radians(90 + random.uniform(-15, 15))
            vx = math.cos(eject_angle) * 1.2
            vy = math.sin(eject_angle) * 1.2
            player_center_x, player_center_y = self.get_player_world_position()
            scatter = ScatteredBullet(
                player_center_x,
                player_center_y,
                vx,
                vy,
                self.cartridge_images[0],
                scale=1.0
            )
            config.scattered_bullets.append(scatter)

class Gun4(WeaponBase):
    TIER = 3
    AMMO_COST = 15
    DAMAGE_MAX = 80
    DAMAGE_MIN = 15
    SPREAD = 0
    FIRE_DELAY = 1000
    EXPLOSION_RADIUS = 190

    @staticmethod
    def create_instance(weapon_assets, sounds, ammo_gauge, consume_ammo, get_player_world_position):
        return Gun4(
            name="유탄 발사기",
            front_image=weapon_assets["gun4"]["front"],
            topdown_image=weapon_assets["gun4"]["topdown"],
            uses_bullets=True,
            bullet_images=weapon_assets["gun4"]["bullets"],
            explosion_image=weapon_assets["gun4"]["explosion"],
            uses_cartridges=False,
            cartridge_images=[],
            can_left_click=True,
            can_right_click=False,
            left_click_ammo_cost=Gun4.AMMO_COST,
            right_click_ammo_cost=0,
            tier=Gun4.TIER,
            sounds_dict={
                "fire": sounds["gun4_fire"],
                "explosion": sounds["gun4_explosion"],
            },
            get_ammo_gauge_fn=ammo_gauge,
            reduce_ammo_fn=consume_ammo,
            bullet_has_trail=False,
            get_player_world_position_fn=get_player_world_position
        )

    def __init__(self, name, front_image, topdown_image, explosion_image, **kwargs):
        super().__init__(name, front_image, topdown_image, **kwargs)
        self.fire_delay = Gun4.FIRE_DELAY
        self.recoil_strength = 10
        self.speed_penalty = 0.15
        self.distance_from_center = config.PLAYER_VIEW_SCALE * 55
        self.explosion_image = explosion_image
        self.shake_strength = 15

    def on_left_click(self):
        if not self.can_left_click or self.get_ammo_gauge() < self.left_click_ammo_cost:
            return

        # 탄약 차감, 발사음 재생
        self.reduce_ammo(self.left_click_ammo_cost)
        self.sounds["fire"].play()

        mouse_x, mouse_y = pygame.mouse.get_pos()
        player_center_x, player_center_y = self.get_player_world_position()

        dx = mouse_x - config.player_rect.centerx
        dy = mouse_y - config.player_rect.centery
        angle = math.atan2(dy, dx)

        vx = math.cos(angle)
        vy = math.sin(angle)

        offset_x = vx * 30 * config.PLAYER_VIEW_SCALE
        offset_y = vy * 30 * config.PLAYER_VIEW_SCALE

        bullet_x = player_center_x + offset_x
        bullet_y = player_center_y + offset_y

        if self.bullet_images:
            # Grenade(유탄) 객체 생성 및 config.bullets에 추가
            from entities import Grenade

            grenade = Grenade(
                x=bullet_x,
                y=bullet_y,
                vx=vx,
                vy=vy,
                image=self.bullet_images[0],
                explosion_radius=Gun4.EXPLOSION_RADIUS,
                max_damage=Gun4.DAMAGE_MAX,
                min_damage=Gun4.DAMAGE_MIN,
                explosion_image=self.explosion_image,
                explosion_sound=self.sounds["explosion"]
            )
            config.bullets.append(grenade)

class Gun5(WeaponBase):
    TIER = 2
    AMMO_COST = 6
    DAMAGE = 14
    FIRE_INTERVAL = 80
    PREHEAT_DURATION = 800
    COOLDOWN_DURATION = 1000

    @staticmethod
    def create_instance(weapon_assets, sounds, ammo_gauge, consume_ammo, get_player_world_position):
        return Gun5(
            name="미니건",
            front_image=weapon_assets["gun5"]["front"],
            topdown_image=weapon_assets["gun5"]["topdown"],
            uses_bullets=True,
            bullet_images=weapon_assets["gun5"]["bullets"],
            uses_cartridges=True,
            cartridge_images=weapon_assets["gun5"]["cartridges"],
            can_left_click=True,
            can_right_click=False,
            left_click_ammo_cost=Gun5.AMMO_COST,
            right_click_ammo_cost=0,
            tier=Gun5.TIER,
            sounds_dict={
                "preheat": sounds["gun5_preheat"],
                "fire": sounds["gun5_fire"],
                "overheat": sounds["gun5_overheat"]
            },
            get_ammo_gauge_fn=ammo_gauge,
            reduce_ammo_fn=consume_ammo,
            bullet_has_trail=False,
            get_player_world_position_fn=get_player_world_position
        )

    def __init__(self, name, front_image, topdown_image, **kwargs):
        super().__init__(name, front_image, topdown_image, **kwargs)
        self.state = "idle"
        self.preheat_start_time = 0
        self.cooldown_start_time = 0
        self.last_shot_time = 0
        self.distance_from_center = config.PLAYER_VIEW_SCALE * 60
        self.recoil_strength = 6
        self.base_speed_penalty = 0.10
        self.firing_speed_penalty = 0.30
        self.speed_penalty = self.base_speed_penalty
        self.shake_strength = 13

    def on_update(self, mouse_left_down, mouse_right_down):
        # 미니건 상태 머신 (idle, preheat, firing, cooldown)
        now = pygame.time.get_ticks()

        if self.state == "idle":
            self.speed_penalty = self.base_speed_penalty
            if mouse_left_down:
                self.state = "preheat"
                self.preheat_start_time = now
                self.sounds["preheat"].play()

        elif self.state == "preheat":
            if not mouse_left_down:
                self.state = "cooldown"
                self.cooldown_start_time = now
                self.sounds["preheat"].stop()
                self.sounds["overheat"].play()
            elif now - self.preheat_start_time >= self.PREHEAT_DURATION:
                self.state = "firing"
                self.last_shot_time = now
                self.speed_penalty = self.firing_speed_penalty

        elif self.state == "firing":
            self.speed_penalty = self.firing_speed_penalty
            if not mouse_left_down:
                self.state = "cooldown"
                self.cooldown_start_time = now
                self.sounds["overheat"].play()
            elif now - self.last_shot_time >= self.FIRE_INTERVAL:
                if self.get_ammo_gauge() >= self.AMMO_COST:
                    self.last_shot_time = now
                    self.reduce_ammo(self.AMMO_COST)
                    self.fire_bullet()

        elif self.state == "cooldown":
            self.speed_penalty = self.base_speed_penalty
            if now - self.cooldown_start_time >= self.COOLDOWN_DURATION:
                self.state = "idle"

    def fire_bullet(self):
        # 미니건 탄환 생성 및 발사 사운드 재생
        mouse_x, mouse_y = pygame.mouse.get_pos()
        player_x, player_y = self.get_player_world_position()

        dx = mouse_x - config.player_rect.centerx
        dy = mouse_y - config.player_rect.centery
        angle = math.atan2(dy, dx)

        vx = math.cos(angle)
        vy = math.sin(angle)

        offset_x = vx * 30 * config.PLAYER_VIEW_SCALE
        offset_y = vy * 30 * config.PLAYER_VIEW_SCALE

        bullet_x = player_x + offset_x
        bullet_y = player_y + offset_y

        bullet = Bullet(
            bullet_x,
            bullet_y,
            bullet_x + vx * 2000,
            bullet_y + vy * 2000,
            spread_angle_degrees=5,
            bullet_image=self.bullet_images[0],
            speed=10 * config.PLAYER_VIEW_SCALE,
            max_distance=2000 * config.PLAYER_VIEW_SCALE,
            damage=self.DAMAGE
        )
        config.bullets.append(bullet)

        if self.uses_cartridges and self.cartridge_images:
            eject_angle = angle + math.radians(90 + random.uniform(-15, 15))
            vx = math.cos(eject_angle) * 1.2
            vy = math.sin(eject_angle) * 1.2
            scatter = ScatteredBullet(
                player_x,
                player_y,
                vx,
                vy,
                self.cartridge_images[0]
            )
            config.scattered_bullets.append(scatter)

        channel = pygame.mixer.find_channel()
        if channel:
            channel.play(self.sounds["fire"])

    def on_weapon_switch(self):
        # 무기 변경 시 모든 사운드 정지, 상태 idle로 초기화
        if self.state == "preheat":
            self.sounds["preheat"].stop()
        elif self.state == "firing":
            self.sounds["fire"].stop()
        elif self.state == "cooldown":
            self.sounds["overheat"].stop()
        self.state = "idle"
        self.speed_penalty = self.base_speed_penalty

class Gun6(WeaponBase):
    TIER = 3
    LEFT_AMMO_COST = 7
    RIGHT_AMMO_COST = 15
    LEFT_FIRE_DELAY = 150
    RIGHT_FIRE_DELAY = 1000
    BULLET_DAMAGE = 20
    BULLET_SPREAD = 8
    GRENADE_DAMAGE_CENTER = 80
    GRENADE_DAMAGE_EDGE = 30
    GRENADE_RADIUS = int(Gun4.EXPLOSION_RADIUS * 0.8)

    @staticmethod
    def create_instance(weapon_assets, sounds, ammo_gauge, consume_ammo, get_player_world_position):
        return Gun6(
            name="개조된 기관단총",
            front_image=weapon_assets["gun6"]["front"],
            topdown_image=weapon_assets["gun6"]["topdown"],
            uses_bullets=True,
            bullet_images=weapon_assets["gun1"]["bullets"],
            uses_cartridges=True,
            cartridge_images=weapon_assets["gun1"]["cartridges"],
            can_left_click=True,
            can_right_click=True,
            left_click_ammo_cost=Gun6.LEFT_AMMO_COST,
            right_click_ammo_cost=Gun6.RIGHT_AMMO_COST,
            tier=Gun6.TIER,
            sounds_dict={
                "left_fire": sounds["gun6_leftfire"],
                "right_fire": sounds["gun6_rightfire"],
                "explosion": sounds["gun6_explosion"]
            },
            get_ammo_gauge_fn=ammo_gauge,
            reduce_ammo_fn=consume_ammo,
            bullet_has_trail=False,
            get_player_world_position_fn=get_player_world_position,
            exclusive_inputs=True,
            explosion_image=weapon_assets["gun6"]["explosion"],
            grenade_image=weapon_assets["gun6"]["grenade"],
        )

    def __init__(self, name, front_image, topdown_image, **kwargs):
        self.explosion_image = kwargs.pop("explosion_image", None)
        self.grenade_image = kwargs.pop("grenade_image", None)
        super().__init__(name, front_image, topdown_image, **kwargs)
        self.fire_delay = Gun6.LEFT_FIRE_DELAY
        self.right_fire_delay = Gun6.RIGHT_FIRE_DELAY
        self.last_right_click_time = 0
        self.recoil_strength = 7
        self.speed_penalty = 0.15
        self.distance_from_center = config.PLAYER_VIEW_SCALE * 48
        self.shake_strength = 10

    def on_update(self, mouse_left_down, mouse_right_down):
        # 좌/우클릭 상호 배타 + 각각 쿨타임 관리
        left_allowed, right_allowed = self._filter_inputs(mouse_left_down, mouse_right_down)
        now = pygame.time.get_ticks()

        if self.can_left_click and left_allowed and now - self.last_shot_time >= self.fire_delay:
            if self.get_ammo_gauge() >= self.left_click_ammo_cost:
                self.on_left_click()
                self.last_shot_time = now

        if self.can_right_click and right_allowed and now - self.last_right_click_time >= self.right_fire_delay:
            if self.get_ammo_gauge() >= self.right_click_ammo_cost:
                self.on_right_click()
                self.last_right_click_time = now

    def on_left_click(self):
        # 소총 탄환 발사, 탄피 배출
        if self.get_ammo_gauge() < self.left_click_ammo_cost:
            return

        self.reduce_ammo(self.left_click_ammo_cost)
        self.sounds["left_fire"].play()

        mouse_x, mouse_y = pygame.mouse.get_pos()
        px, py = self.get_player_world_position()

        dx = mouse_x - config.player_rect.centerx
        dy = mouse_y - config.player_rect.centery
        angle = math.atan2(dy, dx)
        spread = math.radians(random.uniform(-self.BULLET_SPREAD / 2, self.BULLET_SPREAD / 2))
        angle += spread
        vx = math.cos(angle)
        vy = math.sin(angle)

        offset_x = vx * 30 * config.PLAYER_VIEW_SCALE
        offset_y = vy * 30 * config.PLAYER_VIEW_SCALE
        bullet_x = px + offset_x
        bullet_y = py + offset_y

        bullet = Bullet(
            bullet_x,
            bullet_y,
            bullet_x + vx * 2000,
            bullet_y + vy * 2000,
            spread_angle_degrees=self.BULLET_SPREAD,
            bullet_image=self.bullet_images[0],
            speed=10 * config.PLAYER_VIEW_SCALE,
            max_distance=2000 * config.PLAYER_VIEW_SCALE,
            damage=self.BULLET_DAMAGE
        )
        bullet.trail_enabled = self.bullet_has_trail
        config.bullets.append(bullet)

        if self.uses_cartridges and self.cartridge_images:
            eject_angle = angle + math.radians(90 + random.uniform(-15, 15))
            vx = math.cos(eject_angle) * 1.2
            vy = math.sin(eject_angle) * 1.2
            scatter = ScatteredBullet(
                px,
                py,
                vx,
                vy,
                self.cartridge_images[0]
            )
            config.scattered_bullets.append(scatter)

    def on_right_click(self):
        # 유탄 발사
        if self.get_ammo_gauge() < self.right_click_ammo_cost:
            return

        self.reduce_ammo(self.right_click_ammo_cost)
        self.sounds["right_fire"].play()

        self.last_shot_time = pygame.time.get_ticks()

        mouse_x, mouse_y = pygame.mouse.get_pos()
        px, py = self.get_player_world_position()

        dx = mouse_x - config.player_rect.centerx
        dy = mouse_y - config.player_rect.centery
        angle = math.atan2(dy, dx)
        vx = math.cos(angle)
        vy = math.sin(angle)

        offset_x = vx * 30 * config.PLAYER_VIEW_SCALE
        offset_y = vy * 30 * config.PLAYER_VIEW_SCALE
        gx = px + offset_x
        gy = py + offset_y

        from entities import Grenade
        grenade = Grenade(
            x=gx,
            y=gy,
            vx=vx,
            vy=vy,
            image=self.grenade_image,
            explosion_radius=self.GRENADE_RADIUS,
            max_damage=self.GRENADE_DAMAGE_CENTER,
            min_damage=self.GRENADE_DAMAGE_EDGE,
            explosion_image=self.explosion_image,
            explosion_sound=self.sounds["explosion"]
        )
        config.bullets.append(grenade)

class Gun7(WeaponBase):
    TIER = 2
    NAME = "C8-SFW"
    LEFT_FIRE_DELAY = 110
    RIGHT_FIRE_DELAY = 700

    LEFT_AMMO_COST = 4
    RIGHT_AMMO_COST = 10

    @staticmethod
    def create_instance(weapon_assets, sounds, ammo_gauge, consume_ammo, get_player_world_position):
        return Gun7(
            name=Gun7.NAME,
            front_image=weapon_assets["gun7"]["front"],
            topdown_image=weapon_assets["gun7"]["topdown"],
            uses_bullets=True,
            bullet_images=weapon_assets["gun7"]["bullets"],
            uses_cartridges=True,
            cartridge_images=weapon_assets["gun7"]["cartridges"],
            can_left_click=True,
            can_right_click=True,
            left_click_ammo_cost=Gun7.LEFT_AMMO_COST,
            right_click_ammo_cost=Gun7.RIGHT_AMMO_COST,
            tier=Gun7.TIER,
            sounds_dict={
                "left_fire": sounds["gun7_leftfire"],
                "right_fire": sounds["gun7_rightfire"]
            },
            get_ammo_gauge_fn=ammo_gauge,
            reduce_ammo_fn=consume_ammo,
            bullet_has_trail=True,
            get_player_world_position_fn=get_player_world_position,
            exclusive_inputs=True
        )

    def __init__(self, name, front_image, topdown_image, **kwargs):
        super().__init__(name, front_image, topdown_image, **kwargs)
        self.fire_delay = Gun7.LEFT_FIRE_DELAY
        self.right_fire_delay = Gun7.RIGHT_FIRE_DELAY
        self.last_right_click_time = 0

        self.recoil_strength = 4.5
        self.speed_penalty = 0.10
        self.distance_from_center = config.PLAYER_VIEW_SCALE * 48
        self.shake_strength = 12

    def on_update(self, mouse_left_down, mouse_right_down):
        # 좌/우클릭 상호 배타 + 쿨타임 체크
        left_allowed, right_allowed = self._filter_inputs(mouse_left_down, mouse_right_down)
        now = pygame.time.get_ticks()

        if self.can_left_click and left_allowed and now - self.last_shot_time >= self.fire_delay:
            if self.get_ammo_gauge() >= self.left_click_ammo_cost:
                self.on_left_click()
                self.last_shot_time = now

        if self.can_right_click and right_allowed and now - self.last_right_click_time >= self.right_fire_delay:
            if self.get_ammo_gauge() >= self.right_click_ammo_cost:
                self.on_right_click()
                self.last_right_click_time = now

    def on_left_click(self):
        # 소총 탄환 발사, 탄피 배출
        if self.get_ammo_gauge() < self.left_click_ammo_cost:
            return

        self.reduce_ammo(self.left_click_ammo_cost)
        self.sounds["left_fire"].play()

        mouse_x, mouse_y = pygame.mouse.get_pos()
        px, py = self.get_player_world_position()

        dx = mouse_x - config.player_rect.centerx
        dy = mouse_y - config.player_rect.centery
        angle = math.atan2(dy, dx)
        spread = math.radians(random.uniform(-6, 6))
        angle += spread

        vx = math.cos(angle)
        vy = math.sin(angle)

        offset_x = vx * 30 * config.PLAYER_VIEW_SCALE
        offset_y = vy * 30 * config.PLAYER_VIEW_SCALE
        bullet_x = px + offset_x
        bullet_y = py + offset_y

        bullet = Bullet(
            bullet_x,
            bullet_y,
            bullet_x + vx * 2000,
            bullet_y + vy * 2000,
            spread_angle_degrees=6,
            bullet_image=self.bullet_images[0],
            speed=13 * config.PLAYER_VIEW_SCALE,
            max_distance=1800 * config.PLAYER_VIEW_SCALE,
            damage=25
        )
        bullet.trail_enabled = self.bullet_has_trail
        config.bullets.append(bullet)

        if self.uses_cartridges and self.cartridge_images:
            eject_angle = angle + math.radians(90 + random.uniform(-15, 15))
            vx = math.cos(eject_angle) * 1.2
            vy = math.sin(eject_angle) * 1.2
            scatter = ScatteredBullet(
                px,
                py,
                vx,
                vy,
                self.cartridge_images[0],
                scale=1.0
            )
            config.scattered_bullets.append(scatter)

    def on_right_click(self):
        # 산탄 발사, 탄피 배출
        if self.get_ammo_gauge() < self.right_click_ammo_cost:
            return

        self.reduce_ammo(self.right_click_ammo_cost)
        self.sounds["right_fire"].play()

        px, py = self.get_player_world_position()
        mouse_x, mouse_y = pygame.mouse.get_pos()

        base_angle = math.atan2(mouse_y - config.player_rect.centery, mouse_x - config.player_rect.centerx)
        spread = 15
        pellet_count = 5

        for _ in range(pellet_count):
            angle = base_angle + math.radians(random.uniform(-spread, spread))
            vx = math.cos(angle)
            vy = math.sin(angle)

            offset_x = vx * 30 * config.PLAYER_VIEW_SCALE
            offset_y = vy * 30 * config.PLAYER_VIEW_SCALE
            bullet_x = px + offset_x
            bullet_y = py + offset_y

            pellet = Bullet(
                bullet_x,
                bullet_y,
                bullet_x + vx * 700,
                bullet_y + vy * 700,
                spread_angle_degrees=0,
                bullet_image=self.bullet_images[0],
                speed=10 * config.PLAYER_VIEW_SCALE,
                max_distance=700 * config.PLAYER_VIEW_SCALE,
                damage=17
            )
            pellet.trail_enabled = False
            config.bullets.append(pellet)

        if self.uses_cartridges and self.cartridge_images:
            eject_angle = base_angle + math.radians(90 + random.uniform(-15, 15))
            vx = math.cos(eject_angle) * 1.2
            vy = math.sin(eject_angle) * 1.2
            scatter = ScatteredBullet(
                px,
                py,
                vx,
                vy,
                self.cartridge_images[1],
                scale=1.0
            )
            config.scattered_bullets.append(scatter)

class Gun8(WeaponBase):
    TIER = 3
    AMMO_COST = 29
    DAMAGE_MAX = 120
    DAMAGE_MIN = 40
    FIRE_DELAY = 1100
    EXPLOSION_RADIUS = 300

    BULLET_SPEED = 0.4
    MAX_DISTANCE = 1000

    @staticmethod
    def create_instance(weapon_assets, sounds, ammo_gauge, consume_ammo, get_player_world_position):
        return Gun8(
            name="RPG",
            front_image=weapon_assets["gun8"]["front"],
            topdown_image=weapon_assets["gun8"]["topdown"],
            uses_bullets=True,
            bullet_images=weapon_assets["gun8"]["bullets"],
            uses_cartridges=False,
            cartridge_images=[],
            can_left_click=True,
            can_right_click=False,
            left_click_ammo_cost=Gun8.AMMO_COST,
            right_click_ammo_cost=0,
            tier=Gun8.TIER,
            sounds_dict={
                "fire": sounds["gun8_fire"],
                "explosion": sounds["gun8_explosion"],
            },
            get_ammo_gauge_fn=ammo_gauge,
            reduce_ammo_fn=consume_ammo,
            bullet_has_trail=False,
            get_player_world_position_fn=get_player_world_position,
            explosion_image=weapon_assets["gun8"]["explosion"]
        )

    def __init__(self, name, front_image, topdown_image, explosion_image, **kwargs):
        super().__init__(name, front_image, topdown_image, **kwargs)
        self.fire_delay = Gun8.FIRE_DELAY
        self.recoil_strength = 14
        self.speed_penalty = 0.22
        self.distance_from_center = config.PLAYER_VIEW_SCALE * 60
        self.explosion_image = explosion_image
        self.shake_strength = 20

    def on_update(self, mouse_left_down, mouse_right_down):
        # 좌클릭 쿨타임 체크 후 발사
        now = pygame.time.get_ticks()
        
        if self.can_left_click and mouse_left_down and now - self.last_shot_time >= self.fire_delay:
            if self.get_ammo_gauge() >= self.left_click_ammo_cost:
                self.on_left_click()
                self.last_shot_time = now

    def on_left_click(self):
        # 로켓 발사
        if not self.can_left_click or self.get_ammo_gauge() < self.left_click_ammo_cost:
            return

        self.reduce_ammo(self.left_click_ammo_cost)
        self.sounds["fire"].play()

        mouse_x, mouse_y = pygame.mouse.get_pos()
        player_center_x, player_center_y = self.get_player_world_position()

        dx = mouse_x - config.player_rect.centerx
        dy = mouse_y - config.player_rect.centery
        angle = math.atan2(dy, dx)

        vx = math.cos(angle)
        vy = math.sin(angle)

        offset_x = vx * 15 * config.PLAYER_VIEW_SCALE
        offset_y = vy * 15 * config.PLAYER_VIEW_SCALE

        bullet_x = player_center_x + offset_x
        bullet_y = player_center_y + offset_y

        if self.bullet_images:
            # Grenade 객체로 로켓 생성
            from entities import Grenade
            grenade = Grenade(
                x=bullet_x,
                y=bullet_y,
                vx=vx * Gun8.BULLET_SPEED,
                vy=vy * Gun8.BULLET_SPEED,
                image=self.bullet_images[0],
                explosion_radius=Gun8.EXPLOSION_RADIUS,
                max_damage=Gun8.DAMAGE_MAX,
                min_damage=Gun8.DAMAGE_MIN,
                explosion_image=self.explosion_image,
                explosion_sound=self.sounds["explosion"]
            )
            grenade.max_distance = Gun8.MAX_DISTANCE * config.PLAYER_VIEW_SCALE
            config.bullets.append(grenade)

class Gun9(WeaponBase):
    TIER = 4
    LEFT_AMMO_COST = 8
    RIGHT_AMMO_COST = 18
    LEFT_FIRE_DELAY = 150
    RIGHT_FIRE_DELAY = 1000
    LEFT_DAMAGE = 25
    RIGHT_DAMAGE = 10
    RIGHT_EXPLOSION_RADIUS = 150
    RIGHT_KNOCKBACK = 200
    LEFT_SPREAD = 6
    RIGHT_SPREAD = 0

    @staticmethod
    def create_instance(weapon_assets, sounds, ammo_gauge, consume_ammo, get_player_world_position):
        return Gun9(
            name="ARX200",
            front_image=weapon_assets["gun9"]["front"],
            topdown_image=weapon_assets["gun9"]["topdown"],
            uses_bullets=True,
            bullet_images=weapon_assets["gun9"]["bullets"],
            uses_cartridges=True,
            cartridge_images=weapon_assets["gun9"]["cartridges"],
            can_left_click=True,
            can_right_click=True,
            left_click_ammo_cost=Gun9.LEFT_AMMO_COST,
            right_click_ammo_cost=Gun9.RIGHT_AMMO_COST,
            tier=Gun9.TIER,
            sounds_dict={
                "left_fire": sounds["gun9_leftfire"],
                "right_fire": sounds["gun9_rightfire"],
                "explosion": sounds["gun9_explosion"],
            },
            get_ammo_gauge_fn=ammo_gauge,
            reduce_ammo_fn=consume_ammo,
            bullet_has_trail=False,
            get_player_world_position_fn=get_player_world_position,
            exclusive_inputs=True
        )

    def __init__(self, name, front_image, topdown_image, **kwargs):
        super().__init__(name, front_image, topdown_image, **kwargs)
        self.fire_delay = Gun9.LEFT_FIRE_DELAY
        self.right_fire_delay = Gun9.RIGHT_FIRE_DELAY
        self.last_right_click_time = 0
        self.recoil_strength = 6
        self.speed_penalty = 0.12
        self.distance_from_center = config.PLAYER_VIEW_SCALE * 50
        self.shake_strength = 14

    def on_update(self, mouse_left_down, mouse_right_down):
        # 좌/우클릭 상호 배타 + 쿨타임 체크
        left_allowed, right_allowed = self._filter_inputs(mouse_left_down, mouse_right_down)
        now = pygame.time.get_ticks()

        if self.can_left_click and left_allowed and now - self.last_shot_time >= self.fire_delay:
            if self.get_ammo_gauge() >= self.left_click_ammo_cost:
                self.on_left_click()
                self.last_shot_time = now

        if self.can_right_click and right_allowed and now - self.last_right_click_time >= self.right_fire_delay:
            if self.get_ammo_gauge() >= self.right_click_ammo_cost:
                self.on_right_click()
                self.last_right_click_time = now

    def on_left_click(self):
        # 소총 탄환 발사, 탄피 배출
        if self.get_ammo_gauge() < self.left_click_ammo_cost:
            return

        self.reduce_ammo(self.left_click_ammo_cost)
        self.sounds["left_fire"].play()

        mouse_x, mouse_y = pygame.mouse.get_pos()
        px, py = self.get_player_world_position()

        dx = mouse_x - config.player_rect.centerx
        dy = mouse_y - config.player_rect.centery
        angle = math.atan2(dy, dx)
        spread = math.radians(random.uniform(-self.LEFT_SPREAD / 2, self.LEFT_SPREAD / 2))
        angle += spread

        vx = math.cos(angle)
        vy = math.sin(angle)

        offset_x = vx * 30 * config.PLAYER_VIEW_SCALE
        offset_y = vy * 30 * config.PLAYER_VIEW_SCALE
        bullet_x = px + offset_x
        bullet_y = py + offset_y

        bullet = Bullet(
            bullet_x,
            bullet_y,
            bullet_x + vx * 2000,
            bullet_y + vy * 2000,
            spread_angle_degrees=self.LEFT_SPREAD,
            bullet_image=self.bullet_images[0][0],
            speed=11 * config.PLAYER_VIEW_SCALE,
            max_distance=2000 * config.PLAYER_VIEW_SCALE,
            damage=self.LEFT_DAMAGE
        )
        bullet.trail_enabled = False
        config.bullets.append(bullet)

        if self.uses_cartridges and self.cartridge_images:
            eject_angle = angle + math.radians(90 + random.uniform(-15, 15))
            vx_c = math.cos(eject_angle) * 1.2
            vy_c = math.sin(eject_angle) * 1.2
            scatter = ScatteredBullet(
                px,
                py,
                vx_c,
                vy_c,
                self.cartridge_images[0]
            )
            config.scattered_bullets.append(scatter)

    def on_right_click(self):
        # 기압탄 발사
        if self.get_ammo_gauge() < self.right_click_ammo_cost:
            return

        self.reduce_ammo(self.right_click_ammo_cost)
        self.sounds["right_fire"].play()

        mouse_x, mouse_y = pygame.mouse.get_pos()
        px, py = self.get_player_world_position()

        dx = mouse_x - config.player_rect.centerx
        dy = mouse_y - config.player_rect.centery
        angle = math.atan2(dy, dx)

        vx = math.cos(angle)
        vy = math.sin(angle)

        offset_x = vx * 30 * config.PLAYER_VIEW_SCALE
        offset_y = vy * 30 * config.PLAYER_VIEW_SCALE
        gx = px + offset_x
        gy = py + offset_y

        from entities import PressureBullet
        bullet = PressureBullet(
            x=gx,
            y=gy,
            vx=vx,
            vy=vy,
            image=self.bullet_images[1][0],
            explosion_radius=self.RIGHT_EXPLOSION_RADIUS,
            damage=self.RIGHT_DAMAGE,
            knockback_distance=self.RIGHT_KNOCKBACK,
            explosion_sound=self.sounds["explosion"]
        )
        bullet.trail_enabled = True
        config.bullets.append(bullet)

class Gun10(WeaponBase):
    TIER = 2
    LEFT_AMMO_COST = 5
    RIGHT_AMMO_COST = 6
    LEFT_FIRE_DELAY = 120
    RIGHT_FIRE_DELAY = 100
    LEFT_DAMAGE = 16
    RIGHT_DAMAGE = 20
    LEFT_SPREAD = 12
    RIGHT_SPREAD = 8
    RANGE = 1800
    SPEED = 11 * config.PLAYER_VIEW_SCALE

    @staticmethod
    def create_instance(weapon_assets, sounds, ammo_gauge, consume_ammo, get_player_world_position):
        return Gun10(
            name="Mx4 Storm",
            front_image=weapon_assets["gun10"]["front"],
            topdown_image=weapon_assets["gun10"]["topdown"],
            uses_bullets=True,
            bullet_images=weapon_assets["gun10"]["bullets"],
            uses_cartridges=True,
            cartridge_images=weapon_assets["gun10"]["cartridges"],
            can_left_click=True,
            can_right_click=True,
            left_click_ammo_cost=Gun10.LEFT_AMMO_COST,
            right_click_ammo_cost=Gun10.RIGHT_AMMO_COST,
            tier=Gun10.TIER,
            sounds_dict={
                "fire": sounds["gun10_fire"],
            },
            get_ammo_gauge_fn=ammo_gauge,
            reduce_ammo_fn=consume_ammo,
            bullet_has_trail=False,
            get_player_world_position_fn=get_player_world_position
        )

    def __init__(self, name, front_image, topdown_image, **kwargs):
        super().__init__(name, front_image, topdown_image, **kwargs)
        self.fire_delay = Gun10.LEFT_FIRE_DELAY
        self.right_fire_delay = Gun10.RIGHT_FIRE_DELAY
        self.last_right_click_time = 0
        self.recoil_strength = 5
        self.speed_penalty = 0.05
        self.distance_from_center = config.PLAYER_VIEW_SCALE * 50
        self.shake_strength = 10
        self.ads_mode = False

    def on_update(self, mouse_left_down, mouse_right_down):
        now = pygame.time.get_ticks()

        # 우클릭 시 ADS 모드 진입, 좌클릭 시 기본 모드
        if mouse_right_down:
            self.ads_mode = True
            self.fire_delay = Gun10.RIGHT_FIRE_DELAY
            self.recoil_strength = 6
            self.speed_penalty = 0.50
            self.shake_strength = 12
        else:
            self.ads_mode = False
            self.fire_delay = Gun10.LEFT_FIRE_DELAY
            self.recoil_strength = 5
            self.speed_penalty = 0.05
            self.shake_strength = 10

        # 발사 처리
        if mouse_left_down and now - self.last_shot_time >= self.fire_delay:
            if self.get_ammo_gauge() >= (self.right_click_ammo_cost if self.ads_mode else self.left_click_ammo_cost):
                if self.ads_mode:
                    self.on_right_click()
                else:
                    self.on_left_click()
                self.last_shot_time = now

    def on_left_click(self):
        # 기본 모드 사격
        self._fire_bullet(self.LEFT_DAMAGE, self.LEFT_SPREAD, self.left_click_ammo_cost)

    def on_right_click(self):
        # ADS 모드 사격
        self._fire_bullet(self.RIGHT_DAMAGE, self.RIGHT_SPREAD, self.right_click_ammo_cost)

    def _fire_bullet(self, damage, spread_deg, ammo_cost):
        if self.get_ammo_gauge() < ammo_cost:
            return
        self.reduce_ammo(ammo_cost)
        self.sounds["fire"].play()

        mouse_x, mouse_y = pygame.mouse.get_pos()
        px, py = self.get_player_world_position()

        dx = mouse_x - config.player_rect.centerx
        dy = mouse_y - config.player_rect.centery
        angle = math.atan2(dy, dx)
        spread = math.radians(random.uniform(-spread_deg / 2, spread_deg / 2))
        angle += spread

        vx = math.cos(angle)
        vy = math.sin(angle)
        offset_x = vx * 30 * config.PLAYER_VIEW_SCALE
        offset_y = vy * 30 * config.PLAYER_VIEW_SCALE
        bullet_x = px + offset_x
        bullet_y = py + offset_y

        bullet = Bullet(
            bullet_x,
            bullet_y,
            bullet_x + vx * self.RANGE,
            bullet_y + vy * self.RANGE,
            spread_angle_degrees=spread_deg,
            bullet_image=self.bullet_images[0],
            speed=self.SPEED,
            max_distance=self.RANGE * config.PLAYER_VIEW_SCALE,
            damage=damage
        )
        bullet.trail_enabled = self.bullet_has_trail
        config.bullets.append(bullet)

        if self.uses_cartridges and self.cartridge_images:
            eject_angle = angle + math.radians(90 + random.uniform(-15, 15))
            vx_c = math.cos(eject_angle) * 1.2
            vy_c = math.sin(eject_angle) * 1.2
            scatter = ScatteredBullet(px, py, vx_c, vy_c, self.cartridge_images[0])
            config.scattered_bullets.append(scatter)

class Gun11(WeaponBase):
    TIER = 2
    AMMO_COST = 10
    DAMAGE = 8
    FIRE_DELAY = 350
    NUM_BULLETS = 6
    SPREAD_DEGREES = 60
    RANGE = 650
    SPEED = 8 * config.PLAYER_VIEW_SCALE

    @staticmethod
    def create_instance(weapon_assets, sounds, ammo_gauge, consume_ammo, get_player_world_position):
        return Gun11(
            name="SPAS-15",
            front_image=weapon_assets["gun11"]["front"],
            topdown_image=weapon_assets["gun11"]["topdown"],
            uses_bullets=True,
            bullet_images=weapon_assets["gun11"]["bullets"],
            uses_cartridges=True,
            cartridge_images=weapon_assets["gun11"]["cartridges"],
            can_left_click=True,
            can_right_click=False,
            left_click_ammo_cost=Gun11.AMMO_COST,
            right_click_ammo_cost=0,
            tier=Gun11.TIER,
            sounds_dict={
                "fire": sounds["gun11_fire"],
            },
            get_ammo_gauge_fn=ammo_gauge,
            reduce_ammo_fn=consume_ammo,
            bullet_has_trail=False,
            get_player_world_position_fn=get_player_world_position
        )

    def __init__(self, name, front_image, topdown_image, **kwargs):
        super().__init__(name, front_image, topdown_image, **kwargs)
        self.fire_delay = Gun11.FIRE_DELAY
        self.recoil_strength = 7
        self.speed_penalty = 0.10
        self.distance_from_center = config.PLAYER_VIEW_SCALE * 35
        self.shake_strength = 15

    def on_left_click(self):
        # 샷건 사격 (12펠릿, 펠릿당 DAMAGE)
        if not self.can_left_click or self.get_ammo_gauge() < self.left_click_ammo_cost:
            return

        # 탄약 차감 및 발사음 재생
        self.reduce_ammo(self.left_click_ammo_cost)
        self.sounds["fire"].play()

        mouse_x, mouse_y = pygame.mouse.get_pos()
        player_center_x, player_center_y = self.get_player_world_position()
        base_angle = math.atan2(mouse_y - config.player_rect.centery, mouse_x - config.player_rect.centerx)

        for _ in range(self.NUM_BULLETS):
            # 각 펠릿별로 랜덤 스프레드 적용
            spread = math.radians(random.uniform(-self.SPREAD_DEGREES / 2, self.SPREAD_DEGREES / 2))
            angle = base_angle + spread

            vx = math.cos(angle)
            vy = math.sin(angle)

            offset_x = vx * 30 * config.PLAYER_VIEW_SCALE
            offset_y = vy * 30 * config.PLAYER_VIEW_SCALE
            bullet_x = player_center_x + offset_x
            bullet_y = player_center_y + offset_y

            if self.bullet_images:
                bullet = Bullet(
                    bullet_x,
                    bullet_y,
                    bullet_x + vx * self.RANGE,
                    bullet_y + vy * self.RANGE,
                    spread_angle_degrees=0,
                    bullet_image=self.bullet_images[0],
                    speed=self.SPEED,
                    max_distance=self.RANGE * config.PLAYER_VIEW_SCALE,
                    damage=self.DAMAGE
                )
                bullet.trail_enabled = self.bullet_has_trail
                config.bullets.append(bullet)

        if self.uses_cartridges and self.cartridge_images:
            # 탄피 배출 (cartridge_case2)
            eject_angle = base_angle + math.radians(90 + random.uniform(-15, 15))
            vx = math.cos(eject_angle) * 1.2
            vy = math.sin(eject_angle) * 1.2
            scatter = ScatteredBullet(
                player_center_x,
                player_center_y,
                vx,
                vy,
                self.cartridge_images[0],
                scale=1.0
            )
            config.scattered_bullets.append(scatter)

class Gun12(WeaponBase):
    TIER = 2
    AMMO_COST = 8
    DAMAGE = 70
    FIRE_DELAY = 200
    SPREAD_DEGREES = 6
    RANGE = 2000
    SPEED = 12 * config.PLAYER_VIEW_SCALE

    @staticmethod
    def create_instance(weapon_assets, sounds, ammo_gauge, consume_ammo, get_player_world_position):
        # bullet1 이미지를 1.5배 확대
        bullet_img = weapon_assets["gun12"]["bullets"][0]
        w, h = bullet_img.get_size()
        bullet_img_scaled = pygame.transform.smoothscale(bullet_img, (int(w * 1.5), int(h * 1.5)))

        return Gun12(
            name="DP-27",
            front_image=weapon_assets["gun12"]["front"],
            topdown_image=weapon_assets["gun12"]["topdown"],
            uses_bullets=True,
            bullet_images=[bullet_img_scaled],
            uses_cartridges=False,
            cartridge_images=[],
            can_left_click=True,
            can_right_click=False,
            left_click_ammo_cost=Gun12.AMMO_COST,
            right_click_ammo_cost=0,
            tier=Gun12.TIER,
            sounds_dict={
                "fire": sounds["gun12_fire"],
            },
            get_ammo_gauge_fn=ammo_gauge,
            reduce_ammo_fn=consume_ammo,
            bullet_has_trail=True,
            get_player_world_position_fn=get_player_world_position
        )

    def __init__(self, name, front_image, topdown_image, **kwargs):
        super().__init__(name, front_image, topdown_image, **kwargs)
        self.fire_delay = Gun12.FIRE_DELAY
        self.recoil_strength = 9
        self.speed_penalty = 0.20
        self.distance_from_center = config.PLAYER_VIEW_SCALE * 50
        self.shake_strength = 16

    def on_left_click(self):
        # 강력한 단발 사격
        if not self.can_left_click or self.get_ammo_gauge() < self.left_click_ammo_cost:
            return

        # 탄약 차감, 발사음 재생
        self.reduce_ammo(self.left_click_ammo_cost)
        self.sounds["fire"].play()

        mouse_x, mouse_y = pygame.mouse.get_pos()
        px, py = self.get_player_world_position()

        dx = mouse_x - config.player_rect.centerx
        dy = mouse_y - config.player_rect.centery
        angle = math.atan2(dy, dx)

        # 스프레드 적용
        spread = math.radians(random.uniform(-self.SPREAD_DEGREES / 2, self.SPREAD_DEGREES / 2))
        angle += spread

        vx = math.cos(angle)
        vy = math.sin(angle)

        offset_x = vx * 30 * config.PLAYER_VIEW_SCALE
        offset_y = vy * 30 * config.PLAYER_VIEW_SCALE
        bullet_x = px + offset_x
        bullet_y = py + offset_y

        # 총알 생성
        bullet = Bullet(
            bullet_x,
            bullet_y,
            bullet_x + vx * self.RANGE,
            bullet_y + vy * self.RANGE,
            spread_angle_degrees=self.SPREAD_DEGREES,
            bullet_image=self.bullet_images[0],
            speed=self.SPEED,
            max_distance=self.RANGE * config.PLAYER_VIEW_SCALE,
            damage=self.DAMAGE
        )
        bullet.trail_enabled = True
        config.bullets.append(bullet)

class Gun13(WeaponBase):
    TIER = 1
    LEFT_AMMO_COST = 4
    RIGHT_AMMO_COST = 5
    LEFT_FIRE_DELAY = 170
    RIGHT_FIRE_DELAY = 150
    LEFT_DAMAGE = 18
    RIGHT_DAMAGE = 22
    LEFT_SPREAD = 10
    RIGHT_SPREAD = 8
    RANGE = 1800
    SPEED = 11 * config.PLAYER_VIEW_SCALE

    @staticmethod
    def create_instance(weapon_assets, sounds, ammo_gauge, consume_ammo, get_player_world_position):
        return Gun13(
            name="MPX",
            front_image=weapon_assets["gun13"]["front"],
            topdown_image=weapon_assets["gun13"]["topdown"],
            uses_bullets=True,
            bullet_images=weapon_assets["gun13"]["bullets"],
            uses_cartridges=True,
            cartridge_images=weapon_assets["gun13"]["cartridges"],
            can_left_click=True,
            can_right_click=True,
            left_click_ammo_cost=Gun13.LEFT_AMMO_COST,
            right_click_ammo_cost=Gun13.RIGHT_AMMO_COST,
            tier=Gun13.TIER,
            sounds_dict={
                "fire": sounds["gun13_fire"],
            },
            get_ammo_gauge_fn=ammo_gauge,
            reduce_ammo_fn=consume_ammo,
            bullet_has_trail=False,
            get_player_world_position_fn=get_player_world_position
        )

    def __init__(self, name, front_image, topdown_image, **kwargs):
        super().__init__(name, front_image, topdown_image, **kwargs)
        self.fire_delay = Gun13.LEFT_FIRE_DELAY
        self.right_fire_delay = Gun13.RIGHT_FIRE_DELAY
        self.last_right_click_time = 0
        self.recoil_strength = 10
        self.speed_penalty = 0.05  # 기본 장착 시
        self.distance_from_center = config.PLAYER_VIEW_SCALE * 48
        self.shake_strength = 9
        self.ads_mode = False

    def on_update(self, mouse_left_down, mouse_right_down):
        now = pygame.time.get_ticks()

        # 우클릭 시 ADS 모드 진입, 좌클릭 시 기본 모드
        if mouse_right_down:
            self.ads_mode = True
            self.fire_delay = Gun13.RIGHT_FIRE_DELAY
            self.recoil_strength = 10
            self.speed_penalty = 0.12
            self.shake_strength = 10
        else:
            self.ads_mode = False
            self.fire_delay = Gun13.LEFT_FIRE_DELAY
            self.recoil_strength = 8
            self.speed_penalty = 0.05
            self.shake_strength = 9

        # 발사 처리
        if mouse_left_down and now - self.last_shot_time >= self.fire_delay:
            if self.get_ammo_gauge() >= (self.right_click_ammo_cost if self.ads_mode else self.left_click_ammo_cost):
                if self.ads_mode:
                    self.on_right_click()
                else:
                    self.on_left_click()
                self.last_shot_time = now

    def on_left_click(self):
        # 기본 모드 사격
        self._fire_bullet(self.LEFT_DAMAGE, self.LEFT_SPREAD, self.left_click_ammo_cost)

    def on_right_click(self):
        # ADS 모드 사격
        self._fire_bullet(self.RIGHT_DAMAGE, self.RIGHT_SPREAD, self.right_click_ammo_cost)

    def _fire_bullet(self, damage, spread_deg, ammo_cost):
        if self.get_ammo_gauge() < ammo_cost:
            return
        self.reduce_ammo(ammo_cost)
        self.sounds["fire"].play()

        mouse_x, mouse_y = pygame.mouse.get_pos()
        px, py = self.get_player_world_position()

        dx = mouse_x - config.player_rect.centerx
        dy = mouse_y - config.player_rect.centery
        angle = math.atan2(dy, dx)
        spread = math.radians(random.uniform(-spread_deg / 2, spread_deg / 2))
        angle += spread

        vx = math.cos(angle)
        vy = math.sin(angle)
        offset_x = vx * 30 * config.PLAYER_VIEW_SCALE
        offset_y = vy * 30 * config.PLAYER_VIEW_SCALE
        bullet_x = px + offset_x
        bullet_y = py + offset_y

        bullet = Bullet(
            bullet_x,
            bullet_y,
            bullet_x + vx * self.RANGE,
            bullet_y + vy * self.RANGE,
            spread_angle_degrees=spread_deg,
            bullet_image=self.bullet_images[0],
            speed=self.SPEED,
            max_distance=self.RANGE * config.PLAYER_VIEW_SCALE,
            damage=damage
        )
        bullet.trail_enabled = self.bullet_has_trail
        config.bullets.append(bullet)

        if self.uses_cartridges and self.cartridge_images:
            eject_angle = angle + math.radians(90 + random.uniform(-15, 15))
            vx_c = math.cos(eject_angle) * 1.2
            vy_c = math.sin(eject_angle) * 1.2
            scatter = ScatteredBullet(px, py, vx_c, vy_c, self.cartridge_images[0])
            config.scattered_bullets.append(scatter)

class Gun14(WeaponBase):
    TIER = 2
    LEFT_AMMO_COST = 4
    RIGHT_AMMO_COST = 5
    LEFT_FIRE_DELAY = 140
    RIGHT_FIRE_DELAY = 120
    LEFT_DAMAGE = 20
    RIGHT_DAMAGE = 24
    LEFT_SPREAD = 9
    RIGHT_SPREAD = 8
    RANGE = 1850
    SPEED = 11 * config.PLAYER_VIEW_SCALE

    @staticmethod
    def create_instance(weapon_assets, sounds, ammo_gauge, consume_ammo, get_player_world_position):
        return Gun14(
            name="MP5",
            front_image=weapon_assets["gun14"]["front"],
            topdown_image=weapon_assets["gun14"]["topdown"],
            uses_bullets=True,
            bullet_images=weapon_assets["gun14"]["bullets"],
            uses_cartridges=True,
            cartridge_images=weapon_assets["gun14"]["cartridges"],
            can_left_click=True,
            can_right_click=True,
            left_click_ammo_cost=Gun14.LEFT_AMMO_COST,
            right_click_ammo_cost=Gun14.RIGHT_AMMO_COST,
            tier=Gun14.TIER,
            sounds_dict={
                "fire": sounds["gun14_fire"],
            },
            get_ammo_gauge_fn=ammo_gauge,
            reduce_ammo_fn=consume_ammo,
            bullet_has_trail=False,
            get_player_world_position_fn=get_player_world_position
        )

    def __init__(self, name, front_image, topdown_image, **kwargs):
        super().__init__(name, front_image, topdown_image, **kwargs)
        self.fire_delay = Gun14.LEFT_FIRE_DELAY
        self.right_fire_delay = Gun14.RIGHT_FIRE_DELAY
        self.last_right_click_time = 0
        self.recoil_strength = 10
        self.speed_penalty = 0.06  # 기본 장착 시
        self.distance_from_center = config.PLAYER_VIEW_SCALE * 48
        self.shake_strength = 10
        self.ads_mode = False

    def on_update(self, mouse_left_down, mouse_right_down):
        now = pygame.time.get_ticks()

        # 우클릭 시 ADS 모드 진입, 좌클릭 시 기본 모드
        if mouse_right_down:
            self.ads_mode = True
            self.fire_delay = Gun14.RIGHT_FIRE_DELAY
            self.recoil_strength = 8
            self.speed_penalty = 0.14
            self.shake_strength = 11
        else:
            self.ads_mode = False
            self.fire_delay = Gun14.LEFT_FIRE_DELAY
            self.recoil_strength = 10
            self.speed_penalty = 0.06
            self.shake_strength = 10

        # 발사 처리
        if mouse_left_down and now - self.last_shot_time >= self.fire_delay:
            if self.get_ammo_gauge() >= (self.right_click_ammo_cost if self.ads_mode else self.left_click_ammo_cost):
                if self.ads_mode:
                    self.on_right_click()
                else:
                    self.on_left_click()
                self.last_shot_time = now

    def on_left_click(self):
        # 기본 모드 사격
        self._fire_bullet(self.LEFT_DAMAGE, self.LEFT_SPREAD, self.left_click_ammo_cost)

    def on_right_click(self):
        # ADS 모드 사격
        self._fire_bullet(self.RIGHT_DAMAGE, self.RIGHT_SPREAD, self.right_click_ammo_cost)

    def _fire_bullet(self, damage, spread_deg, ammo_cost):
        if self.get_ammo_gauge() < ammo_cost:
            return
        self.reduce_ammo(ammo_cost)
        self.sounds["fire"].play()

        mouse_x, mouse_y = pygame.mouse.get_pos()
        px, py = self.get_player_world_position()

        dx = mouse_x - config.player_rect.centerx
        dy = mouse_y - config.player_rect.centery
        angle = math.atan2(dy, dx)
        spread = math.radians(random.uniform(-spread_deg / 2, spread_deg / 2))
        angle += spread

        vx = math.cos(angle)
        vy = math.sin(angle)
        offset_x = vx * 30 * config.PLAYER_VIEW_SCALE
        offset_y = vy * 30 * config.PLAYER_VIEW_SCALE
        bullet_x = px + offset_x
        bullet_y = py + offset_y

        bullet = Bullet(
            bullet_x,
            bullet_y,
            bullet_x + vx * self.RANGE,
            bullet_y + vy * self.RANGE,
            spread_angle_degrees=spread_deg,
            bullet_image=self.bullet_images[0],
            speed=self.SPEED,
            max_distance=self.RANGE * config.PLAYER_VIEW_SCALE,
            damage=damage
        )
        bullet.trail_enabled = self.bullet_has_trail
        config.bullets.append(bullet)

        if self.uses_cartridges and self.cartridge_images:
            eject_angle = angle + math.radians(90 + random.uniform(-15, 15))
            vx_c = math.cos(eject_angle) * 1.2
            vy_c = math.sin(eject_angle) * 1.2
            scatter = ScatteredBullet(px, py, vx_c, vy_c, self.cartridge_images[0])
            config.scattered_bullets.append(scatter)

class Gun15(WeaponBase):
    TIER = 5
    LEFT_AMMO_COST = 10
    LEFT_FIRE_DELAY = 120
    LEFT_DAMAGE = 24
    LEFT_SPREAD = 10
    LEFT_RANGE = 2000
    LEFT_SPEED = 14 * config.PLAYER_VIEW_SCALE

    RIGHT_FIRE_DELAY = 1000
    RIGHT_CONE_ANGLE = 120
    RIGHT_RANGE = 500
    BASE_DAMAGE = 30
    MAX_DAMAGE = 150
    BASE_KNOCKBACK = 100
    MAX_KNOCKBACK = 500
    MAX_CHARGE = 50

    @staticmethod
    def create_instance(weapon_assets, sounds, ammo_gauge, consume_ammo, get_player_world_position):
        return Gun15(
            name="플라즈마 라이플",
            front_image=weapon_assets["gun15"]["front"],
            topdown_image=weapon_assets["gun15"]["topdown"],
            uses_bullets=True,
            bullet_images=weapon_assets["gun15"]["bullets"],
            uses_cartridges=False,
            cartridge_images=[],
            can_left_click=True,
            can_right_click=True,
            left_click_ammo_cost=Gun15.LEFT_AMMO_COST,
            right_click_ammo_cost=0,
            tier=Gun15.TIER,
            sounds_dict={
                "left_fire": sounds["gun15_leftfire"],
                "right_fire": sounds["gun15_rightfire"],
            },
            get_ammo_gauge_fn=ammo_gauge,
            reduce_ammo_fn=consume_ammo,
            bullet_has_trail=False,
            get_player_world_position_fn=get_player_world_position,
            exclusive_inputs=True
        )

    def __init__(self, name, front_image, topdown_image, **kwargs):
        super().__init__(name, front_image, topdown_image, **kwargs)
        self.fire_delay = Gun15.LEFT_FIRE_DELAY
        self.right_fire_delay = Gun15.RIGHT_FIRE_DELAY
        self.last_right_click_time = 0
        self.plasma_charge = 0
        self.recoil_strength = 3
        self.speed_penalty = 0.08
        self.distance_from_center = config.PLAYER_VIEW_SCALE * 55
        self.shake_strength = 7

    def on_update(self, mouse_left_down, mouse_right_down):
        left_allowed, right_allowed = self._filter_inputs(mouse_left_down, mouse_right_down)
        now = pygame.time.get_ticks()

        if self.can_left_click and left_allowed and now - self.last_shot_time >= self.fire_delay:
            if self.get_ammo_gauge() >= self.left_click_ammo_cost:
                self.on_left_click()
                self.last_shot_time = now

        if self.can_right_click and right_allowed and now - self.last_right_click_time >= self.RIGHT_FIRE_DELAY:
            if self.plasma_charge >= 1:
                self.on_right_click()
                self.last_right_click_time = now

    def on_left_click(self):
        self.reduce_ammo(self.left_click_ammo_cost)
        self.sounds["left_fire"].play()

        config.shake_timer = 5
        config.shake_strength = self.shake_strength

        self.plasma_charge += 1

        mouse_x, mouse_y = pygame.mouse.get_pos()
        px, py = self.get_player_world_position()

        dx = mouse_x - config.player_rect.centerx
        dy = mouse_y - config.player_rect.centery
        angle = math.atan2(dy, dx)
        spread = math.radians(random.uniform(-self.LEFT_SPREAD / 2, self.LEFT_SPREAD / 2))
        angle += spread

        vx = math.cos(angle)
        vy = math.sin(angle)
        offset_x = vx * 30 * config.PLAYER_VIEW_SCALE
        offset_y = vy * 30 * config.PLAYER_VIEW_SCALE
        bullet_x = px + offset_x
        bullet_y = py + offset_y

        bullet = Bullet(
            bullet_x,
            bullet_y,
            bullet_x + vx * self.LEFT_RANGE,
            bullet_y + vy * self.LEFT_RANGE,
            spread_angle_degrees=self.LEFT_SPREAD,
            bullet_image=self.bullet_images[0],
            speed=self.LEFT_SPEED,
            max_distance=self.LEFT_RANGE * config.PLAYER_VIEW_SCALE,
            damage=self.LEFT_DAMAGE
        )
        bullet.trail_enabled = self.bullet_has_trail
        config.bullets.append(bullet)

    def on_right_click(self):
        self.sounds["right_fire"].play()

        config.shake_timer = 8
        config.shake_strength = self.shake_strength + 3

        charge_ratio = min(self.plasma_charge, self.MAX_CHARGE) / self.MAX_CHARGE
        damage = self.BASE_DAMAGE + (self.MAX_DAMAGE - self.BASE_DAMAGE) * charge_ratio
        knockback = self.BASE_KNOCKBACK + (self.MAX_KNOCKBACK - self.BASE_KNOCKBACK) * charge_ratio

        px, py = self.get_player_world_position()
        mouse_x, mouse_y = pygame.mouse.get_pos()
        dir_angle = math.atan2(mouse_y - config.player_rect.centery, mouse_x - config.player_rect.centerx)

        for enemy in list(config.all_enemies):
            if not getattr(enemy, "alive", True):
                continue

            dx = enemy.world_x - px
            dy = enemy.world_y - py
            dist = math.hypot(dx, dy)
            if dist <= self.RIGHT_RANGE:
                angle_to_enemy = math.degrees(math.atan2(dy, dx) - dir_angle)
                angle_to_enemy = (angle_to_enemy + 360) % 360
                if angle_to_enemy > 180:
                    angle_to_enemy -= 360
                if abs(angle_to_enemy) <= self.RIGHT_CONE_ANGLE / 2:
                    enemy.hit(damage, None)

                    if enemy.hp <= 0:
                        enemy.alive = False
                        enemy.radius = 0
                        if hasattr(enemy, "colliders"):
                            enemy.colliders = []
                        if enemy in config.all_enemies:
                            config.all_enemies.remove(enemy)
                        continue

                    if dist > 0:
                        nx = dx / dist
                        ny = dy / dist
                    else:
                        nx, ny = 0, 0
                    enemy.knockback_velocity_x = nx * (knockback / 10)
                    enemy.knockback_velocity_y = ny * (knockback / 10)
                    enemy.knockback_steps = 10

        self.plasma_charge = 0

class Gun16(WeaponBase):
    TIER = 1
    LEFT_AMMO_COST = 3
    RIGHT_AMMO_COST = 4
    LEFT_FIRE_DELAY = 100
    RIGHT_FIRE_DELAY = 85
    LEFT_DAMAGE = 12
    RIGHT_DAMAGE = 14
    LEFT_SPREAD = 15
    RIGHT_SPREAD = 9
    RANGE = 1700
    SPEED = 11 * config.PLAYER_VIEW_SCALE

    @staticmethod
    def create_instance(weapon_assets, sounds, ammo_gauge, consume_ammo, get_player_world_position):
        return Gun16(
            name="P90",
            front_image=weapon_assets["gun16"]["front"],
            topdown_image=weapon_assets["gun16"]["topdown"],
            uses_bullets=True,
            bullet_images=weapon_assets["gun16"]["bullets"],
            uses_cartridges=True,
            cartridge_images=weapon_assets["gun16"]["cartridges"],
            can_left_click=True,
            can_right_click=True,
            left_click_ammo_cost=Gun16.LEFT_AMMO_COST,
            right_click_ammo_cost=Gun16.RIGHT_AMMO_COST,
            tier=Gun16.TIER,
            sounds_dict={
                "fire": sounds["gun16_fire"],
            },
            get_ammo_gauge_fn=ammo_gauge,
            reduce_ammo_fn=consume_ammo,
            bullet_has_trail=False,
            get_player_world_position_fn=get_player_world_position
        )

    def __init__(self, name, front_image, topdown_image, **kwargs):
        super().__init__(name, front_image, topdown_image, **kwargs)
        self.fire_delay = Gun16.LEFT_FIRE_DELAY
        self.right_fire_delay = Gun16.RIGHT_FIRE_DELAY
        self.last_right_click_time = 0
        self.recoil_strength = 4
        self.speed_penalty = 0.04
        self.distance_from_center = config.PLAYER_VIEW_SCALE * 48
        self.shake_strength = 8
        self.ads_mode = False

    def on_update(self, mouse_left_down, mouse_right_down):
        now = pygame.time.get_ticks()

        # ADS 모드 토글
        if mouse_right_down:
            self.ads_mode = True
            self.fire_delay = Gun16.RIGHT_FIRE_DELAY
            self.recoil_strength = 5
            self.speed_penalty = 0.12
            self.shake_strength = 9
        else:
            self.ads_mode = False
            self.fire_delay = Gun16.LEFT_FIRE_DELAY
            self.recoil_strength = 4
            self.speed_penalty = 0.04
            self.shake_strength = 8

        # 발사 처리
        if mouse_left_down and now - self.last_shot_time >= self.fire_delay:
            if self.get_ammo_gauge() >= (self.right_click_ammo_cost if self.ads_mode else self.left_click_ammo_cost):
                if self.ads_mode:
                    self.on_right_click()
                else:
                    self.on_left_click()
                self.last_shot_time = now

    def on_left_click(self):
        # 기본 모드 사격
        self._fire_bullet(self.LEFT_DAMAGE, self.LEFT_SPREAD, self.left_click_ammo_cost)

    def on_right_click(self):
        # ADS 모드 사격
        self._fire_bullet(self.RIGHT_DAMAGE, self.RIGHT_SPREAD, self.right_click_ammo_cost)

    def _fire_bullet(self, damage, spread_deg, ammo_cost):
        if self.get_ammo_gauge() < ammo_cost:
            return
        self.reduce_ammo(ammo_cost)
        self.sounds["fire"].play()

        mouse_x, mouse_y = pygame.mouse.get_pos()
        px, py = self.get_player_world_position()

        dx = mouse_x - config.player_rect.centerx
        dy = mouse_y - config.player_rect.centery
        angle = math.atan2(dy, dx)
        spread = math.radians(random.uniform(-spread_deg / 2, spread_deg / 2))
        angle += spread

        vx = math.cos(angle)
        vy = math.sin(angle)
        offset_x = vx * 30 * config.PLAYER_VIEW_SCALE
        offset_y = vy * 30 * config.PLAYER_VIEW_SCALE
        bullet_x = px + offset_x
        bullet_y = py + offset_y

        bullet = Bullet(
            bullet_x,
            bullet_y,
            bullet_x + vx * self.RANGE,
            bullet_y + vy * self.RANGE,
            spread_angle_degrees=spread_deg,
            bullet_image=self.bullet_images[0],
            speed=self.SPEED,
            max_distance=self.RANGE * config.PLAYER_VIEW_SCALE,
            damage=damage
        )
        bullet.trail_enabled = self.bullet_has_trail
        config.bullets.append(bullet)

        if self.uses_cartridges and self.cartridge_images:
            eject_angle = angle + math.radians(90 + random.uniform(-15, 15))
            vx_c = math.cos(eject_angle) * 1.2
            vy_c = math.sin(eject_angle) * 1.2
            scatter = ScatteredBullet(px, py, vx_c, vy_c, self.cartridge_images[0])
            config.scattered_bullets.append(scatter)

class Gun17(WeaponBase):
    TIER = 1
    AMMO_COST = 5
    BULLETS_PER_BURST = 3
    BURST_INTERVAL = 70
    FIRE_DELAY = 600
    DAMAGE = 30
    SPREAD = 0
    RANGE = 1900
    SPEED = 12 * config.PLAYER_VIEW_SCALE

    @staticmethod
    def create_instance(weapon_assets, sounds, ammo_gauge, consume_ammo, get_player_world_position):
        return Gun17(
            name="FAMAS",
            front_image=weapon_assets["gun17"]["front"],
            topdown_image=weapon_assets["gun17"]["topdown"],
            uses_bullets=True,
            bullet_images=weapon_assets["gun17"]["bullets"],
            uses_cartridges=True,
            cartridge_images=weapon_assets["gun17"]["cartridges"],
            can_left_click=True,
            can_right_click=False,
            left_click_ammo_cost=Gun17.AMMO_COST,
            right_click_ammo_cost=0,
            tier=Gun17.TIER,
            sounds_dict={
                "fire": sounds["gun17_fire"],
            },
            get_ammo_gauge_fn=ammo_gauge,
            reduce_ammo_fn=consume_ammo,
            bullet_has_trail=False,
            get_player_world_position_fn=get_player_world_position
        )

    def __init__(self, name, front_image, topdown_image, **kwargs):
        super().__init__(name, front_image, topdown_image, **kwargs)
        self.fire_delay = Gun17.FIRE_DELAY
        self.recoil_strength = 6
        self.speed_penalty = 0.08
        self.distance_from_center = config.PLAYER_VIEW_SCALE * 50
        self.shake_strength = 12

        self.burst_shots_remaining = 0
        self.last_burst_shot_time = 0

    def on_update(self, mouse_left_down, mouse_right_down):
        now = pygame.time.get_ticks()

        # 점사 발사 처리
        if self.burst_shots_remaining > 0:
            if now - self.last_burst_shot_time >= self.BURST_INTERVAL:
                self._fire_single_bullet()
                self.burst_shots_remaining -= 1
                self.last_burst_shot_time = now
            return  # 점사 중에는 새로운 발사 입력 무시

        # 점사 시작 조건
        if mouse_left_down and now - self.last_shot_time >= self.fire_delay:
            if self.get_ammo_gauge() >= self.AMMO_COST:
                self.on_left_click()
                self.last_shot_time = now

    def on_left_click(self):
        self.reduce_ammo(self.AMMO_COST)
        self.sounds["fire"].play()

        config.shake_timer = 5
        config.shake_strength = self.shake_strength

        self.burst_shots_remaining = self.BULLETS_PER_BURST
        self.last_burst_shot_time = 0

    def _fire_single_bullet(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        px, py = self.get_player_world_position()

        dx = mouse_x - config.player_rect.centerx
        dy = mouse_y - config.player_rect.centery
        angle = math.atan2(dy, dx)

        vx = math.cos(angle)
        vy = math.sin(angle)
        offset_x = vx * 30 * config.PLAYER_VIEW_SCALE
        offset_y = vy * 30 * config.PLAYER_VIEW_SCALE
        bullet_x = px + offset_x
        bullet_y = py + offset_y

        bullet = Bullet(
            bullet_x,
            bullet_y,
            bullet_x + vx * self.RANGE,
            bullet_y + vy * self.RANGE,
            spread_angle_degrees=self.SPREAD,
            bullet_image=self.bullet_images[0],
            speed=self.SPEED,
            max_distance=self.RANGE * config.PLAYER_VIEW_SCALE,
            damage=self.DAMAGE
        )
        bullet.trail_enabled = self.bullet_has_trail
        config.bullets.append(bullet)

        if self.uses_cartridges and self.cartridge_images:
            eject_angle = angle + math.radians(90 + random.uniform(-15, 15))
            vx_c = math.cos(eject_angle) * 1.2
            vy_c = math.sin(eject_angle) * 1.2
            scatter = ScatteredBullet(px, py, vx_c, vy_c, self.cartridge_images[0])
            config.scattered_bullets.append(scatter)

class Gun18(WeaponBase):
    TIER = 1
    AMMO_COST = 7
    FIRE_DELAY = 80
    DAMAGE = 13
    SPREAD = 30
    RANGE = 2000
    SPEED = 11 * config.PLAYER_VIEW_SCALE

    @staticmethod
    def create_instance(weapon_assets, sounds, ammo_gauge, consume_ammo, get_player_world_position):
        return Gun18(
            name="SMG-11",
            front_image=weapon_assets["gun18"]["front"],
            topdown_image=weapon_assets["gun18"]["topdown"],
            uses_bullets=True,
            bullet_images=weapon_assets["gun18"]["bullets"],
            uses_cartridges=True,
            cartridge_images=weapon_assets["gun18"]["cartridges"],
            can_left_click=True,
            can_right_click=False,
            left_click_ammo_cost=Gun18.AMMO_COST,
            right_click_ammo_cost=0,
            tier=Gun18.TIER,
            sounds_dict={
                "fire": sounds["gun18_fire"],
            },
            get_ammo_gauge_fn=ammo_gauge,
            reduce_ammo_fn=consume_ammo,
            bullet_has_trail=False,
            get_player_world_position_fn=get_player_world_position
        )

    def __init__(self, name, front_image, topdown_image, **kwargs):
        super().__init__(name, front_image, topdown_image, **kwargs)
        self.fire_delay = Gun18.FIRE_DELAY
        self.recoil_strength = 5
        self.speed_penalty = 0.03
        self.distance_from_center = config.PLAYER_VIEW_SCALE * 45
        self.shake_strength = 8

    def on_update(self, mouse_left_down, mouse_right_down):
        now = pygame.time.get_ticks()

        # 좌클릭 자동사격
        if mouse_left_down and now - self.last_shot_time >= self.fire_delay:
            if self.get_ammo_gauge() >= self.left_click_ammo_cost:
                self.on_left_click()
                self.last_shot_time = now

    def on_left_click(self):
        self._fire_bullet(self.DAMAGE, self.SPREAD, self.left_click_ammo_cost)

    def _fire_bullet(self, damage, spread_deg, ammo_cost):
        if self.get_ammo_gauge() < ammo_cost:
            return
        self.reduce_ammo(ammo_cost)
        self.sounds["fire"].play()

        mouse_x, mouse_y = pygame.mouse.get_pos()
        px, py = self.get_player_world_position()

        dx = mouse_x - config.player_rect.centerx
        dy = mouse_y - config.player_rect.centery
        angle = math.atan2(dy, dx)
        spread = math.radians(random.uniform(-spread_deg / 2, spread_deg / 2))
        angle += spread

        vx = math.cos(angle)
        vy = math.sin(angle)
        offset_x = vx * 30 * config.PLAYER_VIEW_SCALE
        offset_y = vy * 30 * config.PLAYER_VIEW_SCALE
        bullet_x = px + offset_x
        bullet_y = py + offset_y

        bullet = Bullet(
            bullet_x,
            bullet_y,
            bullet_x + vx * self.RANGE,
            bullet_y + vy * self.RANGE,
            spread_angle_degrees=spread_deg,
            bullet_image=self.bullet_images[0],
            speed=self.SPEED,
            max_distance=self.RANGE * config.PLAYER_VIEW_SCALE,
            damage=damage
        )
        bullet.trail_enabled = self.bullet_has_trail
        config.bullets.append(bullet)

        if self.uses_cartridges and self.cartridge_images:
            eject_angle = angle + math.radians(90 + random.uniform(-15, 15))
            vx_c = math.cos(eject_angle) * 1.2
            vy_c = math.sin(eject_angle) * 1.2
            scatter = ScatteredBullet(px, py, vx_c, vy_c, self.cartridge_images[0])
            config.scattered_bullets.append(scatter)

class Gun19(WeaponBase):
    TIER = 4
    AMMO_COST_DEFEND = 8
    DEFEND_ANGLE = 120
    DEFEND_DISTANCE = 80 * config.PLAYER_VIEW_SCALE
    DEPLOY_DURATION = 100

    @staticmethod
    def create_instance(weapon_assets, sounds, ammo_gauge, consume_ammo, get_player_world_position):
        return Gun19(
            name="방패",
            front_image=weapon_assets["gun19"]["front"],
            topdown_image=weapon_assets["gun19"]["topdown"],
            uses_bullets=False,
            bullet_images=[],
            uses_cartridges=False,
            cartridge_images=[],
            can_left_click=True,
            can_right_click=False,
            left_click_ammo_cost=0,
            right_click_ammo_cost=0,
            tier=Gun19.TIER,
            sounds_dict={
                "defend": sounds["gun19_defend"],
            },
            get_ammo_gauge_fn=ammo_gauge,
            reduce_ammo_fn=consume_ammo,
            bullet_has_trail=False,
            get_player_world_position_fn=get_player_world_position
        )

    def __init__(self, name, front_image, topdown_image, **kwargs):
        super().__init__(name, front_image, topdown_image, **kwargs)
        self.state = "idle"
        self.deploy_start_time = 0
        self.recoil_strength = 0
        self.speed_penalty = 0.05
        self.distance_from_center_idle = config.PLAYER_VIEW_SCALE * 0
        self.distance_from_center_deployed = config.PLAYER_VIEW_SCALE * 45
        self.current_distance = self.distance_from_center_idle
        self.distance_from_center = self.current_distance
        self.shake_strength = 0

    def on_update(self, mouse_left_down, mouse_right_down):
        # 방패 상태 머신: idle → deploying → defending
        now = pygame.time.get_ticks()

        if self.state == "idle":
            self.current_distance = self.distance_from_center_idle
            if mouse_left_down:
                self.state = "deploying"
                self.deploy_start_time = now

        elif self.state == "deploying":
            progress = (now - self.deploy_start_time) / self.DEPLOY_DURATION
            if progress >= 1.0:
                self.state = "defending"
                self.current_distance = self.distance_from_center_deployed
            else:
                self.current_distance = self.distance_from_center_idle + \
                    (self.distance_from_center_deployed - self.distance_from_center_idle) * progress

            if not mouse_left_down:
                self.state = "idle"

        elif self.state == "defending":
            self.current_distance = self.distance_from_center_deployed
            if not mouse_left_down:
                self.state = "idle"

        self.distance_from_center = self.current_distance

    def is_defending(self):
        return self.state == "defending"

    def try_block_bullet(self, bullet):
        # 현재 방어 상태일 때 총알을 막을 수 있는지 판정
        if not self.is_defending():
            return False

        px, py = self.get_player_world_position()
        if hasattr(bullet, "world_x") and hasattr(bullet, "world_y"):
            bx, by = bullet.world_x, bullet.world_y
        elif hasattr(bullet, "x") and hasattr(bullet, "y"):
            bx, by = bullet.x, bullet.y
        else:
            return False

        dx = bx - px
        dy = by - py
        dist = math.hypot(dx, dy)
        if dist > self.DEFEND_DISTANCE:
            return False
        if dist <= 1e-6:
            return False        

        facing_dx = math.cos(math.atan2(
            pygame.mouse.get_pos()[1] - config.player_rect.centery,
            pygame.mouse.get_pos()[0] - config.player_rect.centerx))
        facing_dy = math.sin(math.atan2(
            pygame.mouse.get_pos()[1] - config.player_rect.centery,
            pygame.mouse.get_pos()[0] - config.player_rect.centerx))

        dot = (dx / dist) * facing_dx + (dy / dist) * facing_dy
        angle_diff = math.degrees(math.acos(max(min(dot, 1.0), -1.0)))
        if angle_diff <= self.DEFEND_ANGLE / 2:
            if self.get_ammo_gauge() >= self.AMMO_COST_DEFEND:
                self.reduce_ammo(self.AMMO_COST_DEFEND)
                self.sounds["defend"].play()
                return True

        return False

class Gun20(WeaponBase):
    TIER = 4
    FIRE_DELAY = 300
    AMMO_COST = 35
    GRENADE_SPEED = 2.5
    EXPLOSION_RADIUS = 150
    DAMAGE_MAX = 80
    DAMAGE_MIN = 30
    THROW_DELAY = 400
    EXPLOSION_DELAY = 800

    @staticmethod
    def create_instance(weapon_assets, sounds, ammo_gauge, consume_ammo, get_player_world_position):
        return Gun20(
            name="수류탄",
            front_image=weapon_assets["gun20"]["front"],
            topdown_image=weapon_assets["gun20"]["topdown"],
            uses_bullets=True,
            bullet_images=weapon_assets["gun20"]["bullets"],
            explosion_image=weapon_assets["gun20"]["explosion"],
            uses_cartridges=False,
            cartridge_images=[],
            can_left_click=True,
            can_right_click=False,
            left_click_ammo_cost=Gun20.AMMO_COST,
            right_click_ammo_cost=0,
            tier=Gun20.TIER,
            sounds_dict={
                "fire": sounds["gun20_fire"],
                "explosion": sounds["gun20_explosion"],
            },
            get_ammo_gauge_fn=ammo_gauge,
            reduce_ammo_fn=consume_ammo,
            bullet_has_trail=False,
            get_player_world_position_fn=get_player_world_position
        )

    def __init__(self, name, front_image, topdown_image, explosion_image, **kwargs):
        super().__init__(name, front_image, topdown_image, **kwargs)
        self.explosion_image = explosion_image
        self.fire_delay = Gun20.FIRE_DELAY
        self.recoil_strength = 5
        self.speed_penalty = 0.08
        self.distance_from_center = config.PLAYER_VIEW_SCALE * 35
        self.shake_strength = 10
        self.pending_throw_time = None

    def on_update(self, mouse_left_down, mouse_right_down):
        # 발사 예약 및 실행 처리
        now = pygame.time.get_ticks()

        if self.pending_throw_time and now >= self.pending_throw_time:
            self._do_throw_grenade()
            self.pending_throw_time = None
            self.last_shot_time = now

        if mouse_left_down and now - self.last_shot_time >= self.fire_delay and self.pending_throw_time is None:
            if self.get_ammo_gauge() >= self.left_click_ammo_cost:
                self.reduce_ammo(self.left_click_ammo_cost)
                self.sounds["fire"].play()
                self.pending_throw_time = now + self.THROW_DELAY

    def _do_throw_grenade(self, target_pos=None):
        # 실제 수류탄 발사 로직 (3발 부채꼴)
        if target_pos:
            mouse_x, mouse_y = target_pos
        else:
            mouse_x, mouse_y = pygame.mouse.get_pos()

        px, py = self.get_player_world_position()
        base_angle = math.atan2(mouse_y - config.player_rect.centery, mouse_x - config.player_rect.centerx)

        from entities import GrenadeProjectile

        for offset_deg in (-15, 0, 15):
            angle = base_angle + math.radians(offset_deg)
            vx = math.cos(angle)
            vy = math.sin(angle)

            offset_x = vx * self.distance_from_center
            offset_y = vy * self.distance_from_center

            grenade = GrenadeProjectile(
                x=px + offset_x,
                y=py + offset_y,
                vx=vx,
                vy=vy,
                speed=self.GRENADE_SPEED,
                image=self.bullet_images[0],
                explosion_radius=self.EXPLOSION_RADIUS,
                max_damage=self.DAMAGE_MAX,
                min_damage=self.DAMAGE_MIN,
                explosion_image=self.explosion_image,
                explosion_sound=self.sounds["explosion"],
                explosion_delay=self.EXPLOSION_DELAY
            )
            grenade.ignore_enemy_collision = True
            config.bullets.append(grenade)

class Gun21(WeaponBase):
    TIER = 3
    AMMO_COST = 12
    DAMAGE = 80
    SPREAD = 2
    FIRE_DELAY = 550
    RANGE = 2200
    SPEED = 14 * config.PLAYER_VIEW_SCALE

    @staticmethod
    def create_instance(weapon_assets, sounds, ammo_gauge, consume_ammo, get_player_world_position):
        return Gun21(
            name="AR 15.50",
            front_image=weapon_assets["gun21"]["front"],
            topdown_image=weapon_assets["gun21"]["topdown"],
            uses_bullets=True,
            bullet_images=weapon_assets["gun21"]["bullets"],
            uses_cartridges=True,
            cartridge_images=weapon_assets["gun21"]["cartridges"],
            can_left_click=True,
            can_right_click=False,
            left_click_ammo_cost=Gun21.AMMO_COST,
            right_click_ammo_cost=0,
            tier=Gun21.TIER,
            sounds_dict={
                "fire": sounds["gun21_fire"],
            },
            get_ammo_gauge_fn=ammo_gauge,
            reduce_ammo_fn=consume_ammo,
            bullet_has_trail=False,
            get_player_world_position_fn=get_player_world_position
        )

    def __init__(self, name, front_image, topdown_image, **kwargs):
        super().__init__(name, front_image, topdown_image, **kwargs)
        self.fire_delay = Gun21.FIRE_DELAY
        self.recoil_strength = 10
        self.speed_penalty = 0.12
        self.distance_from_center = config.PLAYER_VIEW_SCALE * 55
        self.shake_strength = 15

    def on_left_click(self):
        if not self.can_left_click or self.get_ammo_gauge() < self.left_click_ammo_cost:
            return

        self.reduce_ammo(self.left_click_ammo_cost)
        try:
            self.sounds["fire"].play()
        except:
            pass

        mouse_x, mouse_y = pygame.mouse.get_pos()
        px, py = self.get_player_world_position()

        dx = mouse_x - config.player_rect.centerx
        dy = mouse_y - config.player_rect.centery
        base_angle = math.atan2(dy, dx)
        spread = math.radians(random.uniform(-self.SPREAD / 2, self.SPREAD / 2))
        angle = base_angle + spread

        vx = math.cos(angle)
        vy = math.sin(angle)

        offset_x = vx * 30 * config.PLAYER_VIEW_SCALE
        offset_y = vy * 30 * config.PLAYER_VIEW_SCALE
        bullet_x = px + offset_x
        bullet_y = py + offset_y

        if self.bullet_images:
            bullet = Bullet(
                bullet_x,
                bullet_y,
                bullet_x + vx * self.RANGE,
                bullet_y + vy * self.RANGE,
                spread_angle_degrees=self.SPREAD,
                bullet_image=self.bullet_images[0],
                speed=self.SPEED,
                max_distance=self.RANGE * config.PLAYER_VIEW_SCALE,
                damage=self.DAMAGE
            )
            bullet.trail_enabled = self.bullet_has_trail
            config.bullets.append(bullet)

        if self.uses_cartridges and self.cartridge_images:
            eject_angle = base_angle + math.radians(90 + random.uniform(-15, 15))
            vx_c = math.cos(eject_angle) * 1.2
            vy_c = math.sin(eject_angle) * 1.2
            scatter = ScatteredBullet(
                px,
                py,
                vx_c,
                vy_c,
                self.cartridge_images[0]
            )
            config.scattered_bullets.append(scatter)

class Gun22(WeaponBase):
    TIER = 4
    AMMO_COST = 20
    DAMAGE = 200
    SPREAD = 0
    FIRE_DELAY = 1750
    RANGE = 3000
    SPEED = 18 * config.PLAYER_VIEW_SCALE

    @staticmethod
    def create_instance(weapon_assets, sounds, ammo_gauge, consume_ammo, get_player_world_position):
        return Gun22(
            name="CSRX 300",
            front_image=weapon_assets["gun22"]["front"],
            topdown_image=weapon_assets["gun22"]["topdown"],
            uses_bullets=True,
            bullet_images=weapon_assets["gun22"]["bullets"],
            uses_cartridges=True,
            cartridge_images=weapon_assets["gun22"]["cartridges"],
            can_left_click=True,
            can_right_click=False,
            left_click_ammo_cost=Gun22.AMMO_COST,
            right_click_ammo_cost=0,
            tier=Gun22.TIER,
            sounds_dict={
                "fire": sounds["gun22_fire"],
            },
            get_ammo_gauge_fn=ammo_gauge,
            reduce_ammo_fn=consume_ammo,
            bullet_has_trail=True,
            get_player_world_position_fn=get_player_world_position
        )

    def __init__(self, name, front_image, topdown_image, **kwargs):
        super().__init__(name, front_image, topdown_image, **kwargs)
        self.fire_delay = Gun22.FIRE_DELAY
        self.recoil_strength = 10
        self.speed_penalty = 0.18
        self.distance_from_center = config.PLAYER_VIEW_SCALE * 58
        self.shake_strength = 22

    def on_left_click(self):
        if not self.can_left_click or self.get_ammo_gauge() < self.left_click_ammo_cost:
            return

        self.reduce_ammo(self.left_click_ammo_cost)
        try:
            self.sounds["fire"].play()
        except:
            pass

        mouse_x, mouse_y = pygame.mouse.get_pos()
        player_cx, player_cy = self.get_player_world_position()

        dx = mouse_x - config.player_rect.centerx
        dy = mouse_y - config.player_rect.centery
        angle = math.atan2(dy, dx)

        vx = math.cos(angle)
        vy = math.sin(angle)

        offset_x = vx * 32 * config.PLAYER_VIEW_SCALE
        offset_y = vy * 32 * config.PLAYER_VIEW_SCALE
        bullet_x = player_cx + offset_x
        bullet_y = player_cy + offset_y

        if self.bullet_images:
            bullet = Bullet(
                bullet_x,
                bullet_y,
                bullet_x + vx * self.RANGE,
                bullet_y + vy * self.RANGE,
                spread_angle_degrees=self.SPREAD,
                bullet_image=self.bullet_images[0],
                speed=self.SPEED,
                max_distance=self.RANGE * config.PLAYER_VIEW_SCALE,
                damage=self.DAMAGE
            )
            bullet.trail_enabled = self.bullet_has_trail
            config.bullets.append(bullet)

        if self.uses_cartridges and self.cartridge_images:
            eject_angle = angle + math.radians(90 + random.uniform(-10, 10))
            evx = math.cos(eject_angle) * 1.4
            evy = math.sin(eject_angle) * 1.4
            scatter = ScatteredBullet(
                player_cx,
                player_cy,
                evx,
                evy,
                self.cartridge_images[0]
            )
            config.scattered_bullets.append(scatter)

class Gun23(WeaponBase):
    TIER = 3
    AMMO_COST = 6
    DAMAGE = 45
    SPREAD = 5
    FIRE_DELAY = 350
    RANGE = 1900
    SPEED = 13 * config.PLAYER_VIEW_SCALE

    @staticmethod
    def create_instance(weapon_assets, sounds, ammo_gauge, consume_ammo, get_player_world_position):
        return Gun23(
            name="Mk 14 EBR",
            front_image=weapon_assets["gun23"]["front"],
            topdown_image=weapon_assets["gun23"]["topdown"],
            uses_bullets=True,
            bullet_images=weapon_assets["gun23"]["bullets"],
            uses_cartridges=True,
            cartridge_images=weapon_assets["gun23"]["cartridges"],
            can_left_click=True,
            can_right_click=False,
            left_click_ammo_cost=Gun23.AMMO_COST,
            right_click_ammo_cost=0,
            tier=Gun23.TIER,
            sounds_dict={
                "fire": sounds["gun23_fire"],
            },
            get_ammo_gauge_fn=ammo_gauge,
            reduce_ammo_fn=consume_ammo,
            bullet_has_trail=False,
            get_player_world_position_fn=get_player_world_position
        )

    def __init__(self, name, front_image, topdown_image, **kwargs):
        super().__init__(name, front_image, topdown_image, **kwargs)
        self.fire_delay = Gun23.FIRE_DELAY
        self.recoil_strength = 6
        self.speed_penalty = 0.1
        self.distance_from_center = config.PLAYER_VIEW_SCALE * 52
        self.shake_strength = 10

    def on_left_click(self):
        if not self.can_left_click or self.get_ammo_gauge() < self.left_click_ammo_cost:
            return

        self.reduce_ammo(self.left_click_ammo_cost)
        try:
            self.sounds["fire"].play()
        except:
            pass

        mouse_x, mouse_y = pygame.mouse.get_pos()
        player_cx, player_cy = self.get_player_world_position()

        dx = mouse_x - config.player_rect.centerx
        dy = mouse_y - config.player_rect.centery
        base_angle = math.atan2(dy, dx)
        spread = math.radians(random.uniform(-self.SPREAD / 2, self.SPREAD / 2))
        angle = base_angle + spread

        vx = math.cos(angle)
        vy = math.sin(angle)

        offset_x = vx * 28 * config.PLAYER_VIEW_SCALE
        offset_y = vy * 28 * config.PLAYER_VIEW_SCALE
        bullet_x = player_cx + offset_x
        bullet_y = player_cy + offset_y

        if self.bullet_images:
            bullet = Bullet(
                bullet_x,
                bullet_y,
                bullet_x + vx * self.RANGE,
                bullet_y + vy * self.RANGE,
                spread_angle_degrees=self.SPREAD,
                bullet_image=self.bullet_images[0],
                speed=self.SPEED,
                max_distance=self.RANGE * config.PLAYER_VIEW_SCALE,
                damage=self.DAMAGE
            )
            bullet.trail_enabled = self.bullet_has_trail
            config.bullets.append(bullet)

        if self.uses_cartridges and self.cartridge_images:
            eject_angle = base_angle + math.radians(90 + random.uniform(-15, 15))
            evx = math.cos(eject_angle) * 1.0
            evy = math.sin(eject_angle) * 1.0
            scatter = ScatteredBullet(
                player_cx,
                player_cy,
                evx,
                evy,
                self.cartridge_images[0]
            )
            config.scattered_bullets.append(scatter)

class Gun24(WeaponBase):
    TIER = 2

    LEFT_AMMO_COST = 5
    LEFT_DAMAGE = 12
    LEFT_SPREAD = 20
    LEFT_FIRE_DELAY = 90
    LEFT_RANGE = 1700
    LEFT_SPEED = 12 * config.PLAYER_VIEW_SCALE

    BURST_COUNT = 4
    BURST_INTERVAL = 70
    BURST_DAMAGE = 11
    BURST_SPREAD = 6
    BURST_RANGE = 1700
    BURST_SPEED = 12 * config.PLAYER_VIEW_SCALE
    BURST_AMMO_TOTAL = 12

    @staticmethod
    def create_instance(weapon_assets, sounds, ammo_gauge, consume_ammo, get_player_world_position):
        return Gun24(
            name="스팅어",
            front_image=weapon_assets["gun24"]["front"],
            topdown_image=weapon_assets["gun24"]["topdown"],
            uses_bullets=True,
            bullet_images=weapon_assets["gun24"]["bullets"],
            uses_cartridges=True,
            cartridge_images=weapon_assets["gun24"]["cartridges"],
            can_left_click=True,
            can_right_click=True,
            left_click_ammo_cost=Gun24.LEFT_AMMO_COST,
            right_click_ammo_cost=0,
            tier=Gun24.TIER,
            sounds_dict={
                "fire": sounds["gun24_fire"],
            },
            get_ammo_gauge_fn=ammo_gauge,
            reduce_ammo_fn=consume_ammo,
            bullet_has_trail=False,
            get_player_world_position_fn=get_player_world_position,
            exclusive_inputs=True
        )

    def __init__(self, name, front_image, topdown_image, **kwargs):
        super().__init__(name, front_image, topdown_image, **kwargs)
        self.fire_delay = Gun24.LEFT_FIRE_DELAY
        self.recoil_strength = 6
        self.speed_penalty = 0.08
        self.distance_from_center = config.PLAYER_VIEW_SCALE * 52
        self.shake_strength = 10

        self.right_fire_delay = Gun24.BURST_COUNT * Gun24.BURST_INTERVAL + 150
        self.last_right_click_time = 0

        self._burst_active = False
        self._burst_remaining = 0
        self._burst_next_time = 0
        self._burst_base_angle = 0.0

    def _fire_one(self, angle_rad, damage, speed, max_range, spread_deg_for_record):
        px, py = self.get_player_world_position()
        vx = math.cos(angle_rad)
        vy = math.sin(angle_rad)
        muzzle_offset = 28 * config.PLAYER_VIEW_SCALE
        bx = px + vx * muzzle_offset
        by = py + vy * muzzle_offset

        if self.bullet_images:
            bullet = Bullet(
                bx, by,
                bx + vx * max_range,
                by + vy * max_range,
                spread_angle_degrees=spread_deg_for_record,
                bullet_image=self.bullet_images[0],
                speed=speed,
                max_distance=max_range * config.PLAYER_VIEW_SCALE,
                damage=damage
            )
            bullet.trail_enabled = self.bullet_has_trail
            config.bullets.append(bullet)

        if self.uses_cartridges and self.cartridge_images:
            eject_angle = angle_rad + math.radians(90 + random.uniform(-15, 15))
            evx = math.cos(eject_angle) * 1.0
            evy = math.sin(eject_angle) * 1.0
            scatter = ScatteredBullet(px, py, evx, evy, self.cartridge_images[0])
            config.scattered_bullets.append(scatter)

        self.sounds["fire"].play()

    def on_left_click(self):
        if not self.can_left_click or self.get_ammo_gauge() < self.left_click_ammo_cost:
            return

        self.reduce_ammo(self.left_click_ammo_cost)

        mx, my = pygame.mouse.get_pos()
        dx = mx - config.player_rect.centerx
        dy = my - config.player_rect.centery
        base_angle = math.atan2(dy, dx)
        spread = math.radians(random.uniform(-Gun24.LEFT_SPREAD / 2, Gun24.LEFT_SPREAD / 2))
        angle = base_angle + spread

        self._fire_one(
            angle_rad=angle,
            damage=Gun24.LEFT_DAMAGE,
            speed=Gun24.LEFT_SPEED,
            max_range=Gun24.LEFT_RANGE,
            spread_deg_for_record=Gun24.LEFT_SPREAD
        )

    def on_right_click(self):
        if self._burst_active:
            return
        if self.get_ammo_gauge() < Gun24.BURST_AMMO_TOTAL:
            return

        self.reduce_ammo(Gun24.BURST_AMMO_TOTAL)

        mx, my = pygame.mouse.get_pos()
        dx = mx - config.player_rect.centerx
        dy = my - config.player_rect.centery
        self._burst_base_angle = math.atan2(dy, dx)

        self._burst_active = True
        self._burst_remaining = Gun24.BURST_COUNT
        self._burst_next_time = pygame.time.get_ticks()

    def on_update(self, mouse_left_down, mouse_right_down):
        super().on_update(mouse_left_down, mouse_right_down)

        now = pygame.time.get_ticks()
        right_allowed = (
            (not self.exclusive_inputs and mouse_right_down) or
            (self.exclusive_inputs and self._active_button == 'R' and mouse_right_down)
        )

        if self.can_right_click and right_allowed and not self._burst_active:
            if (now - self.last_right_click_time) >= self.right_fire_delay and \
               self.get_ammo_gauge() >= Gun24.BURST_AMMO_TOTAL:
                self.on_right_click()
                self.last_right_click_time = now

        if self._burst_active and self._burst_remaining > 0:
            if now >= self._burst_next_time:
                angle = self._burst_base_angle + math.radians(
                    random.uniform(-Gun24.BURST_SPREAD / 2, Gun24.BURST_SPREAD / 2)
                )
                self._fire_one(
                    angle_rad=angle,
                    damage=Gun24.BURST_DAMAGE,
                    speed=Gun24.BURST_SPEED,
                    max_range=Gun24.BURST_RANGE,
                    spread_deg_for_record=Gun24.BURST_SPREAD
                )
                self._burst_remaining -= 1
                self._burst_next_time = now + Gun24.BURST_INTERVAL

            if self._burst_remaining <= 0:
                self._burst_active = False

class Gun25(WeaponBase):
    TIER = 2
    AMMO_COST = 9
    DAMAGE = 6
    NUM_PELLETS = 10
    SPREAD_DEGREES = 26
    FIRE_DELAY_PAIR = 820
    DOUBLE_INTERVAL = 130
    RANGE = 1700

    @staticmethod
    def create_instance(weapon_assets, sounds, ammo_gauge, consume_ammo, get_player_world_position):
        return Gun25(
            name="더블 배럴 샷건",
            front_image=weapon_assets["gun25"]["front"],
            topdown_image=weapon_assets["gun25"]["topdown"],
            uses_bullets=True,
            bullet_images=weapon_assets["gun25"]["bullets"],
            uses_cartridges=True,
            cartridge_images=weapon_assets["gun25"]["cartridges"],
            can_left_click=True,
            can_right_click=False,
            left_click_ammo_cost=Gun25.AMMO_COST,
            right_click_ammo_cost=0,
            tier=Gun25.TIER,
            sounds_dict={
                "fire": sounds["gun25_fire"],
            },
            get_ammo_gauge_fn=ammo_gauge,
            reduce_ammo_fn=consume_ammo,
            bullet_has_trail=False,
            get_player_world_position_fn=get_player_world_position
        )

    def __init__(self, name, front_image, topdown_image, **kwargs):
        super().__init__(name, front_image, topdown_image, **kwargs)
        self.fire_delay = Gun25.FIRE_DELAY_PAIR
        self.recoil_strength = 11
        self.speed_penalty = 0.11
        self.distance_from_center = config.PLAYER_VIEW_SCALE * 36
        self.shake_strength = 22

        self._double_active = False
        self._double_remaining = 0
        self._double_next_time = 0

    def _fire_one_shot(self):
        if self.get_ammo_gauge() < self.left_click_ammo_cost:
            return False
        self.reduce_ammo(self.left_click_ammo_cost)
        self.sounds["fire"].play()

        mx, my = pygame.mouse.get_pos()
        base_dx = mx - config.player_rect.centerx
        base_dy = my - config.player_rect.centery
        base_angle = math.atan2(base_dy, base_dx)

        px, py = self.get_player_world_position()
        for _ in range(self.NUM_PELLETS):
            spread = math.radians(random.uniform(-self.SPREAD_DEGREES, self.SPREAD_DEGREES))
            ang = base_angle + spread
            dx, dy = math.cos(ang), math.sin(ang)
            muzzle = 30 * config.PLAYER_VIEW_SCALE
            bx = px + dx * muzzle
            by = py + dy * muzzle
            if self.bullet_images:
                b = Bullet(
                    bx, by,
                    bx + dx * 100, by + dy * 100,
                    0,
                    self.bullet_images[0][0] if isinstance(self.bullet_images[0], list) else self.bullet_images[0],
                    speed=12 * config.PLAYER_VIEW_SCALE,
                    max_distance=self.RANGE * config.PLAYER_VIEW_SCALE,
                    damage=self.DAMAGE
                )
                b.trail_enabled = self.bullet_has_trail
                config.bullets.append(b)

        if self.uses_cartridges and self.cartridge_images:
            eject_angle = base_angle + math.radians(90 + random.uniform(-15, 15))
            vx = math.cos(eject_angle) * 1.2
            vy = math.sin(eject_angle) * 1.2
            scatter = ScatteredBullet(
                px, py, vx, vy,
                self.cartridge_images[0],
                scale=1.0
            )
            config.scattered_bullets.append(scatter)
        return True

    def on_update(self, mouse_left_down, mouse_right_down):
        left_allowed, _ = self._filter_inputs(mouse_left_down, mouse_right_down)
        now = pygame.time.get_ticks()

        if self._double_active:
            if self._double_remaining > 0 and now >= self._double_next_time:
                if self._fire_one_shot():
                    self._double_remaining -= 1
                    self._double_next_time = now + self.DOUBLE_INTERVAL
                else:
                    self._double_remaining = 0
            if self._double_remaining <= 0:
                self._double_active = False
                self.last_shot_time = now
            return

        if self.can_left_click and left_allowed and (now - self.last_shot_time >= self.fire_delay):
            shots_possible = min(2, self.get_ammo_gauge() // self.left_click_ammo_cost)
            if shots_possible >= 1:
                self._double_active = True
                self._double_remaining = shots_possible
                self._double_next_time = now

class Gun26(WeaponBase):
    TIER = 3
    AMMO_COST = 6
    FIRE_DELAY = 110
    DAMAGE = 17
    SPREAD = 9 
    RANGE = 2000
    SPEED = 12 * config.PLAYER_VIEW_SCALE

    @staticmethod
    def create_instance(weapon_assets, sounds, ammo_gauge, consume_ammo, get_player_world_position):
        return Gun26(
            name="M249",
            front_image=weapon_assets["gun26"]["front"],
            topdown_image=weapon_assets["gun26"]["topdown"],
            uses_bullets=True,
            bullet_images=weapon_assets["gun26"]["bullets"],
            uses_cartridges=True,
            cartridge_images=weapon_assets["gun26"]["cartridges"],
            can_left_click=True,
            can_right_click=False,
            left_click_ammo_cost=Gun26.AMMO_COST,
            right_click_ammo_cost=0,
            tier=Gun26.TIER,
            sounds_dict={"fire": sounds["gun26_fire"]},
            get_ammo_gauge_fn=ammo_gauge,
            reduce_ammo_fn=consume_ammo,
            bullet_has_trail=False,
            get_player_world_position_fn=get_player_world_position
        )

    def __init__(self, name, front_image, topdown_image, **kwargs):
        super().__init__(name, front_image, topdown_image, **kwargs)
        self.fire_delay = Gun26.FIRE_DELAY
        self.recoil_strength = 9
        self.speed_penalty = 0.10
        self.distance_from_center = config.PLAYER_VIEW_SCALE * 48
        self.shake_strength = 14

    def on_left_click(self):
        if not self.can_left_click or self.get_ammo_gauge() < self.left_click_ammo_cost:
            return
        self.reduce_ammo(self.left_click_ammo_cost)
        self.sounds["fire"].play()

        mx, my = pygame.mouse.get_pos()
        dx = mx - config.player_rect.centerx
        dy = my - config.player_rect.centery
        base_angle = math.atan2(dy, dx)
        spread = math.radians(random.uniform(-self.SPREAD/2, self.SPREAD/2))
        ang = base_angle + spread
        vx, vy = math.cos(ang), math.sin(ang)

        px, py = self.get_player_world_position()
        muzzle = 30 * config.PLAYER_VIEW_SCALE
        bx = px + vx * muzzle
        by = py + vy * muzzle

        if self.bullet_images:
            bullet = Bullet(
                bx, by,
                bx + vx * 2000, by + vy * 2000,
                self.SPREAD,
                self.bullet_images[0],
                speed=self.SPEED,
                max_distance=self.RANGE * config.PLAYER_VIEW_SCALE,
                damage=self.DAMAGE
            )
            bullet.trail_enabled = self.bullet_has_trail
            config.bullets.append(bullet)

        if self.uses_cartridges and self.cartridge_images:
            ej = base_angle + math.radians(90 + random.uniform(-15, 15))
            evx = math.cos(ej) * 1.2
            evy = math.sin(ej) * 1.2
            scatter = ScatteredBullet(px, py, evx, evy, self.cartridge_images[0])
            config.scattered_bullets.append(scatter)

class Gun27(WeaponBase):
    TIER = 5
    CHARGE_TIME_MS = 800
    LEFT_DAMAGE = 120
    RIGHT_DAMAGE = 50

    LEFT_AMMO_COST = 35
    RIGHT_AMMO_COST = 18

    RANGE_LEFT  = int(4600 * config.PLAYER_VIEW_SCALE)
    RANGE_RIGHT = int(3800 * config.PLAYER_VIEW_SCALE)
    BEAM_VIS_LEFT_MS  = 120
    BEAM_VIS_RIGHT_MS = 80
    LEFT_WIDTH = 10
    RIGHT_WIDTH = 6

    HEAT_PER_LEFT = 50
    HEAT_PER_RIGHT = 14
    HEAT_COOL_PER_SEC = 40
    OVERHEAT_THRESHOLD = 100
    OVERHEAT_LOCK_MS = 1000

    LEFT_COOLDOWN = 350
    RIGHT_COOLDOWN = 200

    @staticmethod
    def create_instance(weapon_assets, sounds, ammo_gauge, consume_ammo, get_player_world_position):
        return Gun27(
            name="레일 랜서",
            front_image=weapon_assets["gun27"]["front"],
            topdown_image=weapon_assets["gun27"]["topdown"],
            uses_bullets=False, bullet_images=weapon_assets["gun27"]["bullets"],
            uses_cartridges=False, cartridge_images=weapon_assets["gun27"]["cartridges"],
            can_left_click=True, can_right_click=True,
            left_click_ammo_cost=Gun27.LEFT_AMMO_COST, right_click_ammo_cost=Gun27.RIGHT_AMMO_COST,
            tier=Gun27.TIER,
            sounds_dict={
                "left_fire":   sounds["gun27_leftfire"],
                "right_fire":  sounds["gun27_rightfire"],
                "charge_loop": sounds["gun27_charge_loop"],
                "overheat": sounds.get("gun5_overheat"),
            },
            get_ammo_gauge_fn=ammo_gauge, reduce_ammo_fn=consume_ammo,
            bullet_has_trail=False, get_player_world_position_fn=get_player_world_position,
            exclusive_inputs=True
        )

    def __init__(self, name, front_image, topdown_image, **kwargs):
        super().__init__(name, front_image, topdown_image, **kwargs)
        self.fire_delay = 120
        self.recoil_strength = 10
        self.speed_penalty = 0.0
        self.distance_from_center = 48 * config.PLAYER_VIEW_SCALE
        self.shake_strength = 12

        self.state = "idle"  # idle / charging / overheat
        self.charge_start_ms = 0
        self.last_left_fire_time = 0
        self.last_right_click_time = 0

        self.heat = 0.0
        self.overheat_until_ms = 0

        self._charge_channel = None

        self.left_fire_delay = self.LEFT_COOLDOWN
        self.right_fire_delay = self.RIGHT_COOLDOWN
        self._last_cool_ms = pygame.time.get_ticks()

        self._beam_until_ms = 0
        self._beam_width_px = 0
        self._beam_is_left = True
        self._beam_ang = 0.0

        self._no_ammo_flash_until = 0

        self._prev_left_down = False
        self._prev_right_down = False

        self.last_shot_time = 0

    # 사운드 제어
    def _start_charge_sound(self):
        try:
            s = self.sounds.get("charge_loop")
            if not s:
                return
            ch = pygame.mixer.find_channel()
            if ch:
                ch.play(s, loops=-1, fade_ms=80)
                self._charge_channel = ch
        except Exception:
            self._charge_channel = None

    def _stop_charge_sound(self):
        if self._charge_channel:
            try:
                self._charge_channel.fadeout(120)
            except Exception:
                pass
        self._charge_channel = None

    # 유틸
    def get_heat_ratio(self):
        return max(0.0, min(1.0, self.heat / float(self.OVERHEAT_THRESHOLD)))

    def _apply_overheat_if_needed(self, add_heat):
        self.heat += add_heat
        if self.heat >= self.OVERHEAT_THRESHOLD:
            self.state = "overheat"
            self.overheat_until_ms = pygame.time.get_ticks() + self.OVERHEAT_LOCK_MS
            s = self.sounds.get("overheat")
            if s:
                try: s.play()
                except Exception: pass
            self._stop_charge_sound()
            return True
        return False

    def _cool_heat(self, now_ms):
        if self.state != "overheat" and self.heat > 0:
            dt = max(0, now_ms - self._last_cool_ms)
            self.heat = max(0.0, self.heat - self.HEAT_COOL_PER_SEC * (dt / 1000.0))
        self._last_cool_ms = now_ms

    def _unit_from_mouse(self):
        mx, my = pygame.mouse.get_pos()
        dx = mx - config.player_rect.centerx
        dy = my - config.player_rect.centery
        ang = math.atan2(dy, dx)
        return (math.cos(ang), math.sin(ang)), ang

    # 히트스캔 + 내부 빔 비주얼 기록
    def _raycast_and_damage(self, width_px, damage, is_left):
        # 월드 기준 시작/끝점
        px, py = self.get_player_world_position()
        (vx, vy), ang = self._unit_from_mouse()
        sx, sy = px + vx * 30 * config.PLAYER_VIEW_SCALE, py + vy * 30 * config.PLAYER_VIEW_SCALE
        rng = self.RANGE_LEFT if is_left else self.RANGE_RIGHT
        ex, ey = sx + vx * rng, sy + vy * rng

        # 빔 비주얼(overlay에서 화면좌표로 직접 그림)
        now = pygame.time.get_ticks()
        self._beam_until_ms = now + (self.BEAM_VIS_LEFT_MS if is_left else self.BEAM_VIS_RIGHT_MS)
        self._beam_width_px = width_px
        self._beam_is_left = is_left
        self._beam_ang = ang

        # 판정: 선분-원 최소거리
        def point_segment_distance(px0, py0, x1, y1, x2, y2):
            vx0 = x2 - x1; vy0 = y2 - y1
            wx = px0 - x1; wy = py0 - y1
            seg_len2 = vx0*vx0 + vy0*vy0
            if seg_len2 <= 1e-6:
                return math.hypot(wx, wy)
            t = max(0.0, min(1.0, (wx*vx0 + wy*vy0) / seg_len2))
            projx = x1 + t * vx0
            projy = y1 + t * vy0
            return math.hypot(px0 - projx, py0 - projy)

        enemies_list = getattr(config, "all_enemies", getattr(config, "enemies", []))
        hit_count = 0
        for e in list(enemies_list):
            if not getattr(e, "alive", False):
                continue
            ex0 = getattr(e, "world_x", getattr(e, "x", None))
            ey0 = getattr(e, "world_y", getattr(e, "y", None))
            if ex0 is None or ey0 is None:
                continue
            rad = int(getattr(e, "radius", 26))
            if point_segment_distance(ex0, ey0, sx, sy, ex, ey) <= (rad + width_px // 2):
                try:
                    if hasattr(e, "hit"):
                        e.hit(damage, None)
                    elif hasattr(e, "on_hit"):
                        e.on_hit(damage, knockback=0, hit_type="laser")
                    else:
                        e.hp = getattr(e, "hp", 0) - damage
                        if e.hp <= 0:
                            e.alive = False
                except Exception:
                    pass
                hit_count += 1

        # 카메라 흔들림(좌가 우보다 더 강하게)
        base = self.shake_strength + (2 if is_left else 0)
        try:
            config.shake_strength = max(getattr(config, "shake_strength", 0), base + min(8, int(hit_count * 1.5)))
            config.shake_timer = max(getattr(config, "shake_timer", 0), 8)
        except Exception:
            pass

    # 입력/상태
    def on_update(self, mouse_left_down, mouse_right_down):
        now = pygame.time.get_ticks()
        self._cool_heat(now)

        if self.state == "overheat":
            if now >= self.overheat_until_ms:
                self.state = "idle"
            return

        left_down  = mouse_left_down
        right_down = mouse_right_down

        # 좌클릭: '쿨다운에 상관없이' 차지는 바로 시작 → 완료 시점에 발사 조건 확인
        if self.can_left_click:
            if (not self._prev_left_down) and left_down and self.state == "idle":
                self.state = "charging"
                self.charge_start_ms = now
                self.speed_penalty = 0.10
                self._start_charge_sound()
            elif left_down and self.state == "charging":
                # 차지 완료 → 쿨/탄약 검사 후 즉시 발사, 아니면 유지
                if (now - self.charge_start_ms) >= self.CHARGE_TIME_MS:
                    can_cd   = (now - self.last_left_fire_time) >= self.left_fire_delay
                    has_ammo = self.get_ammo_gauge() >= self.left_click_ammo_cost
                    if can_cd and has_ammo:
                        self._fire(mode="left")
                        self.last_left_fire_time = now
                        self.state = "idle"
                        self._stop_charge_sound()
                        self.speed_penalty = 0.05
                    elif not has_ammo:
                        self._no_ammo_flash_until = now + 500
                        # 유지하다가 떼면 취소
            elif self._prev_left_down and (not left_down) and self.state == "charging":
                # 차지 중 취소
                self.state = "idle"
                self._stop_charge_sound()
                self.speed_penalty = 0.05

        # 우클릭: 즉발(차지 중엔 무시)
        if self.can_right_click and self.state != "charging":
            if right_down and (now - self.last_right_click_time) >= self.right_fire_delay:
                if self.get_ammo_gauge() >= self.right_click_ammo_cost:
                    self._fire(mode="right")
                    self.last_right_click_time = now
                else:
                    self._no_ammo_flash_until = now + 500

        self._prev_left_down  = left_down
        self._prev_right_down = right_down

    def _fire(self, mode="left"):
        if mode == "left":
            dmg = self.LEFT_DAMAGE
            width_px = self.LEFT_WIDTH
            heat_add = self.HEAT_PER_LEFT
            cost = self.left_click_ammo_cost
            is_left = True
            shake_boost = 4
        else:
            dmg = self.RIGHT_DAMAGE
            width_px = self.RIGHT_WIDTH
            heat_add = self.HEAT_PER_RIGHT
            cost = self.right_click_ammo_cost
            is_left = False
            shake_boost = 2

        # 자원 소모
        self.reduce_ammo(cost)

        self.last_shot_time = pygame.time.get_ticks()

        # 사운드
        key = "left_fire" if mode == "left" else "right_fire"
        s = self.sounds.get(key)
        if s:
            try: s.play()
            except Exception: pass

        # 판정 + 내부 빔 비주얼 세팅
        self._raycast_and_damage(width_px, dmg, is_left)

        # 열 처리/과열
        was_overheated = self._apply_overheat_if_needed(heat_add)

        # 발사 순간에도 보정 흔들림(중첩 허용)
        try:
            base = self.shake_strength + (shake_boost if is_left else shake_boost - 1)
            config.shake_strength = max(getattr(config, "shake_strength", 0), base)
            config.shake_timer = max(getattr(config, "shake_timer", 0), 8)
        except Exception:
            pass

        # 좌클릭 발사 순간에는 차지음 정리
        if is_left:
            self._stop_charge_sound()

    def on_weapon_switch(self):
        # 무기 변경 시 상태/사운드/빔 모두 리셋
        self._stop_charge_sound()
        self.state = "idle"
        self.speed_penalty = 0.1
        self._beam_until_ms = 0

    # HUD/오버레이: 플레이어 위에 HEAT/CHARGE/빔
    def draw_overlay(self, screen):
        sw, sh = screen.get_size()
        cx, cy = config.player_rect.centerx, config.player_rect.centery
        now = pygame.time.get_ticks()

        if now <= self._beam_until_ms and self._beam_width_px > 0:
            ang = self._beam_ang
            vx, vy = math.cos(ang), math.sin(ang)
            sx = cx + vx * (30 * config.PLAYER_VIEW_SCALE)
            sy = cy + vy * (30 * config.PLAYER_VIEW_SCALE)
            rng = self.RANGE_LEFT if self._beam_is_left else self.RANGE_RIGHT
            ex = sx + vx * min(rng, 9999)
            ey = sy + vy * min(rng, 9999)

            beam_surf = pygame.Surface((sw, sh), pygame.SRCALPHA)
            w = self._beam_width_px

            pygame.draw.line(beam_surf, (80, 220, 255, 90),   (sx, sy), (ex, ey), max(1, int(w * 2.5)))
            pygame.draw.line(beam_surf, (140, 240, 255, 140), (sx, sy), (ex, ey), max(1, int(w * 1.6)))
            pygame.draw.line(beam_surf, (255, 255, 255, 220), (sx, sy), (ex, ey), max(1, int(w)))
            screen.blit(beam_surf, (0, 0))

        bar_w = 120
        bar_h = 8
        gap = 6
        base_y = cy - 56

        heat_ratio = self.get_heat_ratio()
        heat_col = (255, 90, 90) if self.state == "overheat" else (90, 210, 255)
        bg = pygame.Rect(cx - bar_w // 2, base_y, bar_w, bar_h)
        pygame.draw.rect(screen, (35, 35, 45), bg, border_radius=6)
        pygame.draw.rect(screen, heat_col, (bg.x, bg.y, int(bar_w * heat_ratio), bar_h), border_radius=6)
        pygame.draw.rect(screen, (120, 140, 180), bg, width=2, border_radius=6)

        if self.state == "charging":
            t = max(0, now - self.charge_start_ms) / float(self.CHARGE_TIME_MS)
            t = max(0.0, min(1.0, t))
            cbg = pygame.Rect(cx - bar_w // 2, base_y - (bar_h + gap), bar_w, bar_h)
            pygame.draw.rect(screen, (30, 30, 38), cbg, border_radius=6)
            pygame.draw.rect(screen, (120, 240, 255), (cbg.x, cbg.y, int(bar_w * t), bar_h), border_radius=6)
            pygame.draw.rect(screen, (120, 160, 200), cbg, width=2, border_radius=6)

        if now <= self._no_ammo_flash_until:
            try:
                font = pygame.font.SysFont(None, 18)
                txt = font.render("NO AMMO", True, (255, 200, 80))
                screen.blit(txt, (cx - txt.get_width() // 2, base_y - (bar_h + gap) - 18))
            except Exception:
                pass

class Gun28(WeaponBase):
    TIER = 5

    LEFT_AMMO_COST = 40
    RIGHT_AMMO_COST = 0
    LEFT_COOLDOWN = 1200
    RIGHT_COOLDOWN = 250

    ORB_SPEED = 8 * config.PLAYER_VIEW_SCALE
    ORB_MAX_TRAVEL = 2400 * config.PLAYER_VIEW_SCALE
    ORB_RADIUS_HIT = 14

    FIELD_RADIUS = 180
    FIELD_DURATION_MS = 1600
    FIELD_TICKS = 8
    FIELD_TICK_DAMAGE = 20
    FIELD_TICK_INTERVAL_MS = FIELD_DURATION_MS // FIELD_TICKS

    FIELD_PULL_SPEED_MAX = 220.0
    FIELD_SWIRL_SPEED     = 160.0
    FIELD_CORE_EPS        = 6.0
    FIELD_SHAKE_ON_SPAWN  = 10

    ORB_GLOW_COLOR   = (130, 120, 250, 140)
    FIELD_COLOR_OUT  = (90, 110, 255,  70)
    FIELD_COLOR_IN   = (180, 220, 255, 110)

    PRTCL_COUNT = 36
    PRTCL_MIN_R = 40
    PRTCL_MAX_R = 180
    PRTCL_MIN_SZ = 2
    PRTCL_MAX_SZ = 5
    PRTCL_ANG_SPD = 4.2
    PRTCL_RAD_SPD = -90.0
    PULSE_RING_COUNT = 2
    PULSE_RING_SPD   = 220.0

    @staticmethod
    def create_instance(weapon_assets, sounds, ammo_gauge, consume_ammo, get_player_world_position):
        return Gun28(
            name="심연 특이점 발사기",
            front_image=weapon_assets["gun28"]["front"],
            topdown_image=weapon_assets["gun28"]["topdown"],
            uses_bullets=False, bullet_images=weapon_assets["gun28"]["bullets"],
            uses_cartridges=False, cartridge_images=weapon_assets["gun28"]["cartridges"],
            can_left_click=True, can_right_click=True,
            left_click_ammo_cost=Gun28.LEFT_AMMO_COST, right_click_ammo_cost=Gun28.RIGHT_AMMO_COST,
            tier=Gun28.TIER,
            sounds_dict={
                "left_fire":  sounds["gun28_leftfire"],
                "right_fire": sounds["gun28_rightfire"],
                "singularity_loop": sounds.get("gun28_singularity_loop"),
                "orb_pop": sounds.get("gun28_pop"),
            },
            get_ammo_gauge_fn=ammo_gauge, reduce_ammo_fn=consume_ammo,
            bullet_has_trail=False, get_player_world_position_fn=get_player_world_position,
            exclusive_inputs=True
        )

    def __init__(self, name, front_image, topdown_image, **kwargs):
        super().__init__(name, front_image, topdown_image, **kwargs)
        self.fire_delay = self.LEFT_COOLDOWN
        self.recoil_strength = 8
        self.speed_penalty = 0.1
        self.distance_from_center = 48 * config.PLAYER_VIEW_SCALE
        self.shake_strength = 10

        self.last_left_fire_time = 0
        self.last_right_fire_time = 0

        self._last_update_ms = pygame.time.get_ticks()

        self._orbs = []
        self._fields = []

        self.last_shot_time = 0

        self._prev_left_down = False
        self._prev_right_down = False

    # 내부 유틸
    def _unit_from_mouse(self):
        # 마우스 방향 단위 벡터와 각도(라디안)를 반환.
        mx, my = pygame.mouse.get_pos()
        dx = mx - config.player_rect.centerx
        dy = my - config.player_rect.centery
        ang = math.atan2(dy, dx)
        return (math.cos(ang), math.sin(ang)), ang

    def _world_to_screen(self, wx, wy):
        # 플레이어를 스크린 중앙 기준으로 월드->스크린 좌표 변환(상대좌표).
        cx, cy = config.player_rect.centerx, config.player_rect.centery
        px, py = self.get_player_world_position()
        return (cx + (wx - px), cy + (wy - py))

    def _apply_shake(self, strength, timer=8):
        try:
            config.shake_strength = max(getattr(config, "shake_strength", 0), strength)
            config.shake_timer = max(getattr(config, "shake_timer", 0), timer)
        except Exception:
            pass

    # 구체/특이점 제어
    def _spawn_orb(self):
        # 발사 방향(마우스)
        (ux, uy), ang = self._unit_from_mouse()
        px, py = self.get_player_world_position()
        sx = px + ux * 30 * config.PLAYER_VIEW_SCALE
        sy = py + uy * 30 * config.PLAYER_VIEW_SCALE
        vx = ux * self.ORB_SPEED
        vy = uy * self.ORB_SPEED
        self._orbs.append({
            "x": sx, "y": sy, "vx": vx, "vy": vy,
            "spawn_ms": pygame.time.get_ticks(),
            "traveled": 0.0
        })

    def _make_particles_for_field(self, x, y, radius):
        # 특이점 연출용 파티클/펄스 생성.
        now = pygame.time.get_ticks()
        particles = []
        for i in range(self.PRTCL_COUNT):
            ang = random.random() * math.tau
            r = random.uniform(self.PRTCL_MIN_R, min(self.PRTCL_MAX_R, radius))
            size = random.randint(self.PRTCL_MIN_SZ, self.PRTCL_MAX_SZ)
            # 살짝 제각각 돌도록 각속도에 난수
            ang_spd = self.PRTCL_ANG_SPD * random.uniform(0.7, 1.3)
            rad_spd = self.PRTCL_RAD_SPD * random.uniform(0.7, 1.3)
            particles.append({
                "ang": ang, "r": r, "size": size,
                "ang_spd": ang_spd, "rad_spd": rad_spd,
                "born_ms": now
            })
        # 펄스 링(외곽에서 퍼지는 동심원)
        pulses = []
        for k in range(self.PULSE_RING_COUNT):
            pulses.append({
                "r": max(30, radius * 0.6),
                "alpha": 160,
                "born_ms": now + k * 60
            })
        return particles, pulses

    def _detonate_orb_to_field(self, orb):
        now = pygame.time.get_ticks()
        particles, pulses = self._make_particles_for_field(orb["x"], orb["y"], self.FIELD_RADIUS)
        field = {
            "x": orb["x"], "y": orb["y"], "radius": self.FIELD_RADIUS,
            "end_ms": now + self.FIELD_DURATION_MS,
            "next_tick_ms": now + self.FIELD_TICK_INTERVAL_MS,
            "ticks_done": 0,
            "loop_ch": None,
            "particles": particles,
            "pulses": pulses
        }
        if self.sounds.get("orb_pop"):
            try: self.sounds["orb_pop"].play()
            except Exception: pass
        # 화면 흔들림
        self._apply_shake(self.FIELD_SHAKE_ON_SPAWN, timer=10)

        # 루프음(선택)
        if self.sounds.get("singularity_loop"):
            try:
                ch = pygame.mixer.find_channel()
                if ch:
                    ch.play(self.sounds["singularity_loop"], loops=-1, fade_ms=60)
                    field["loop_ch"] = ch
            except Exception:
                field["loop_ch"] = None

        self._fields.append(field)

    def _remote_detonate(self):
        if not self._orbs:
            return False
        # 가장 최근 구체를 기폭
        orb = self._orbs.pop(-1)
        self._detonate_orb_to_field(orb)
        return True

    def _update_orbs(self, dt_ms):
        # 구체 이동 및 충돌/도달 처리.
        to_det = []
        enemies_list = getattr(config, "all_enemies", getattr(config, "enemies", []))
        for i, o in enumerate(self._orbs):
            # 이동(프레임 기반)
            o["x"] += o["vx"]
            o["y"] += o["vy"]
            o["traveled"] += (abs(o["vx"]) + abs(o["vy"])) * 0.5

            # 적 충돌 체크
            hit = False
            for e in list(enemies_list):
                if not getattr(e, "alive", False): continue
                ex0 = getattr(e, "world_x", getattr(e, "x", None))
                ey0 = getattr(e, "world_y", getattr(e, "y", None))
                if ex0 is None or ey0 is None: continue
                if math.hypot(ex0 - o["x"], ey0 - o["y"]) <= (self.ORB_RADIUS_HIT + int(getattr(e, "radius", 26))):
                    hit = True
                    break

            # 최대거리 도달
            if o["traveled"] >= self.ORB_MAX_TRAVEL:
                hit = True

            if hit:
                to_det.append(i)

        # 뒤에서부터 제거/전환
        for idx in reversed(to_det):
            orb = self._orbs.pop(idx)
            self._detonate_orb_to_field(orb)

    def _apply_field_forces(self, f, dt_sec):
        # 매 프레임 부드러운 흡인 + 소용돌이(접선) 성분을 적용.
        enemies_list = getattr(config, "all_enemies", getattr(config, "enemies", []))
        cx, cy, r = f["x"], f["y"], f["radius"]
        for e in list(enemies_list):
            if not getattr(e, "alive", False): continue
            ex0 = getattr(e, "world_x", getattr(e, "x", None))
            ey0 = getattr(e, "world_y", getattr(e, "y", None))
            if ex0 is None or ey0 is None: continue
            dx, dy = cx - ex0, cy - ey0
            dist = math.hypot(dx, dy)
            if dist <= r and dist > self.FIELD_CORE_EPS:
                ux, uy = dx / dist, dy / dist  # 중심 방향
                # 가중치: 안쪽으로 갈수록 강(0.15~1.0)
                w = max(0.15, (1.0 - dist / r))
                pull_speed = self.FIELD_PULL_SPEED_MAX * w
                swirl_speed = self.FIELD_SWIRL_SPEED * w
                # 접선 벡터(시계 방향)
                tx, ty = -uy, ux
                # 이동량 = (흡인 + 소용돌이) * dt
                mvx = (ux * pull_speed + tx * swirl_speed) * dt_sec
                mvy = (uy * pull_speed + ty * swirl_speed) * dt_sec
                # 적용(엔티티 위치계가 world_x/y 또는 x/y 중 무엇이든 대응)
                if hasattr(e, "world_x"): e.world_x += mvx
                if hasattr(e, "world_y"): e.world_y += mvy
                if hasattr(e, "x"): e.x += mvx
                if hasattr(e, "y"): e.y += mvy

    def _tick_field_damage(self, f):
        # 대미지 틱만 담당(움직임은 프레임마다 _apply_field_forces).
        enemies_list = getattr(config, "all_enemies", getattr(config, "enemies", []))
        cx, cy, r = f["x"], f["y"], f["radius"]
        for e in list(enemies_list):
            if not getattr(e, "alive", False): continue
            ex0 = getattr(e, "world_x", getattr(e, "x", None))
            ey0 = getattr(e, "world_y", getattr(e, "y", None))
            if ex0 is None or ey0 is None: continue
            if math.hypot(cx - ex0, cy - ey0) <= r:
                try:
                    if hasattr(e, "hit"): e.hit(self.FIELD_TICK_DAMAGE, None)
                    elif hasattr(e, "on_hit"): e.on_hit(self.FIELD_TICK_DAMAGE, knockback=0, hit_type="singularity")
                    else:
                        e.hp = getattr(e, "hp", 0) - self.FIELD_TICK_DAMAGE
                        if e.hp <= 0: e.alive = False
                except Exception:
                    pass

    def _update_fields(self, now, dt_ms):
        # 필드 수명/틱/입자 업데이트 + 루프음 정리.
        dt_sec = max(0.0, dt_ms / 1000.0)
        for f in list(self._fields):
            # 매 프레임 부드러운 흡인 적용
            self._apply_field_forces(f, dt_sec)

            # 대미지 틱
            if now >= f["next_tick_ms"] and f["ticks_done"] < self.FIELD_TICKS:
                self._tick_field_damage(f)
                f["ticks_done"] += 1
                f["next_tick_ms"] += self.FIELD_TICK_INTERVAL_MS

            # 파티클/펄스 업데이트
            self._update_field_fx(f, dt_sec)

            # 수명 종료
            if now >= f["end_ms"]:
                ch = f.get("loop_ch")
                if ch:
                    try: ch.fadeout(120)
                    except Exception: pass
                self._fields.remove(f)

    def _update_field_fx(self, f, dt_sec):
        # 특이점 파티클 소용돌이 + 펄스 링 확장.
        # 파티클
        for p in f["particles"]:
            p["ang"] += p["ang_spd"] * dt_sec
            p["r"]   += p["rad_spd"] * dt_sec
            # 반경이 너무 작아지면 살짝 튕기듯 유지
            if p["r"] < self.PRTCL_MIN_R * 0.4:
                p["r"] = self.PRTCL_MIN_R * 0.4
                p["rad_spd"] *= -0.6
        # 펄스 링
        for ring in f["pulses"]:
            ring["r"] += self.PULSE_RING_SPD * dt_sec
            ring["alpha"] = max(0, ring["alpha"] - 140 * dt_sec)

    # 입력/프레임
    def on_update(self, mouse_left_down, mouse_right_down):
        now = pygame.time.get_ticks()
        dt = now - self._last_update_ms
        self._last_update_ms = now

        # 구체/필드 업데이트(먼저)
        self._update_orbs(dt)
        self._update_fields(now, dt)

        # 입력
        left_down, right_down = mouse_left_down, mouse_right_down

        # 좌클릭: 구체 생성(쿨/탄 약 검사)
        if left_down and (now - self.last_left_fire_time) >= self.LEFT_COOLDOWN:
            if self.get_ammo_gauge() >= self.left_click_ammo_cost:
                self._fire_orb()
                self.last_left_fire_time = now

        # 우클릭: 원격 기폭
        if right_down and (now - self.last_right_fire_time) >= self.RIGHT_COOLDOWN:
            if self._remote_detonate():
                # 우클릭 사운드/반동/흔들림
                s = self.sounds.get("right_fire")
                if s:
                    try: s.play()
                    except Exception: pass
                self.last_right_fire_time = now
                self.last_shot_time = now
                self._apply_shake(self.shake_strength + 2, timer=8)

    def _fire_orb(self):
        # 자원
        self.reduce_ammo(self.left_click_ammo_cost)
        self.last_shot_time = pygame.time.get_ticks()

        # 사운드
        s = self.sounds.get("left_fire")
        if s:
            try: s.play()
            except Exception: pass

        # 구체 생성
        self._spawn_orb()

        # 반동/흔들림
        self._apply_shake(self.shake_strength + 1, timer=8)

    # 렌더/HUD
    def draw_world(self, screen):
        sw, sh = screen.get_size()

        # 구체 표시(글로우)
        if getattr(self, "_orbs", None):
            orb_surf = pygame.Surface((sw, sh), pygame.SRCALPHA)
            for o in self._orbs:
                sx, sy = self._world_to_screen(o["x"], o["y"])
                pygame.draw.circle(orb_surf, (80, 70, 200, 70), (int(sx), int(sy)), 24)
                pygame.draw.circle(orb_surf, self.ORB_GLOW_COLOR, (int(sx), int(sy)), 14)
                pygame.draw.circle(orb_surf, (255, 255, 255, 200), (int(sx), int(sy)), 6)
            screen.blit(orb_surf, (0, 0))

        # 특이점 표시(이중 링 + 채움 + 파티클 + 펄스)
        if getattr(self, "_fields", None):
            f_surf = pygame.Surface((sw, sh), pygame.SRCALPHA)
            for f in self._fields:
                sx, sy = self._world_to_screen(f["x"], f["y"])
                r = int(f["radius"])
                pygame.draw.circle(f_surf, self.FIELD_COLOR_OUT, (int(sx), int(sy)), int(r * 1.02), width=3)
                pygame.draw.circle(f_surf, self.FIELD_COLOR_IN,  (int(sx), int(sy)), int(r * 0.82), width=2)
                pygame.draw.circle(f_surf, (60, 80, 160, 35),    (int(sx), int(sy)), int(r * 0.78))
                # 파티클
                for p in f["particles"]:
                    px = sx + math.cos(p["ang"]) * p["r"]
                    py = sy + math.sin(p["ang"]) * p["r"]
                    pygame.draw.circle(f_surf, (180, 220, 255, 120), (int(px), int(py)), p["size"])
                # 펄스 링
                for ring in f["pulses"]:
                    a  = int(max(0, ring.get("alpha", 0)))
                    rr = ring.get("r", 0)
                    if a > 0 and rr > 0:
                        pygame.draw.circle(
                            f_surf, (150, 200, 255, a),
                            (int(sx), int(sy)), int(rr), width=2)
            screen.blit(f_surf, (0, 0))

    def draw_overlay(self, screen):
        return

class Gun29(WeaponBase):
    TIER = 5

    PRIMARY_DAMAGE = 90
    CHAIN_DAMAGE   = 40

    LEFT_AMMO_COST  = 20
    RIGHT_AMMO_COST = 28
    LEFT_COOLDOWN   = 250
    RIGHT_COOLDOWN  = 320

    CHAIN_MAX_LEFT     = 5
    CHAIN_RADIUS_LEFT  = 260
    CHAIN_MAX_RIGHT    = 7
    CHAIN_RADIUS_RIGHT = 360

    PROJ_SPEED = 22 * config.PLAYER_VIEW_SCALE
    PROJ_MAX_TRAVEL = 2400 * config.PLAYER_VIEW_SCALE
    PROJ_RADIUS_HIT = 10

    ARC_LIFETIME_MS   = 180
    ARC_SEGMENTS      = 10
    ARC_W_LEFT        = 4
    ARC_W_RIGHT       = 6
    TRACER_LIFETIME_MS = 140
    SPARK_FLASH_MS    = 160
    SPARK_RADIUS_IN   = 14 
    SPARK_RADIUS_OUT  = 24

    SHAKE_BASE = 11
    SHAKE_RIGHT_BOOST = 3

    HOMING_ANGLE_DEG_LEFT  = 10
    HOMING_ANGLE_DEG_RIGHT = 10
    HOMING_RANGE_LEFT      = 900
    HOMING_RANGE_RIGHT     = 1100

    @staticmethod
    def create_instance(weapon_assets, sounds, ammo_gauge, consume_ammo, get_player_world_position):
        return Gun29(
            name="천둥 연쇄 번개",
            front_image=weapon_assets["gun29"]["front"],
            topdown_image=weapon_assets["gun29"]["topdown"],
            uses_bullets=False, bullet_images=weapon_assets["gun29"]["bullets"],
            uses_cartridges=False, cartridge_images=weapon_assets["gun29"]["cartridges"],
            can_left_click=True, can_right_click=True,
            left_click_ammo_cost=Gun29.LEFT_AMMO_COST, right_click_ammo_cost=Gun29.RIGHT_AMMO_COST,
            tier=Gun29.TIER,
            sounds_dict={"fire": sounds["gun29_fire"]},
            get_ammo_gauge_fn=ammo_gauge, reduce_ammo_fn=consume_ammo,
            bullet_has_trail=False, get_player_world_position_fn=get_player_world_position,
            exclusive_inputs=True
        )

    def __init__(self, name, front_image, topdown_image, **kwargs):
        super().__init__(name, front_image, topdown_image, **kwargs)
        self.distance_from_center = 48 * config.PLAYER_VIEW_SCALE

        self.speed_penalty = 0.05
        self.recoil_strength = 8

        self.last_left_fire_time = 0
        self.last_right_fire_time = 0
        self.last_shot_time = 0
        self._last_update_ms = pygame.time.get_ticks()

        self._shots = []
        self._arcs = []
        self._sparks = []
        self._tracers = []

    # 유틸
    def _unit_from_mouse(self):
        mx, my = pygame.mouse.get_pos()
        dx = mx - config.player_rect.centerx
        dy = my - config.player_rect.centery
        ang = math.atan2(dy, dx)
        return (math.cos(ang), math.sin(ang)), ang

    def _world_to_screen(self, wx, wy):
        cx, cy = config.player_rect.centerx, config.player_rect.centery
        px, py = self.get_player_world_position()
        return (cx + (wx - px), cy + (wy - py))

    def _shake(self, strength, timer=8):
        try:
            config.shake_strength = max(getattr(config, "shake_strength", 0), strength)
            config.shake_timer = max(getattr(config, "shake_timer", 0), timer)
        except Exception:
            pass

    # 입력/업데이트
    def on_update(self, mouse_left_down, mouse_right_down):
        now = pygame.time.get_ticks()
        dt = now - self._last_update_ms
        self._last_update_ms = now

        # 투사체 이동/충돌
        self._update_shots()

        # 비주얼 만료 정리
        self._arcs[:] = [a for a in self._arcs if now <= a["until_ms"]]
        self._sparks[:] = [s for s in self._sparks if now <= s["until_ms"]]
        self._tracers[:] = [t for t in self._tracers if now <= t["until_ms"]]

        # 입력 처리
        if mouse_left_down and (now - self.last_left_fire_time) >= self.LEFT_COOLDOWN:
            if self.get_ammo_gauge() >= self.left_click_ammo_cost:
                self._fire(overcharge=False)
                self.last_left_fire_time = now

        if mouse_right_down and (now - self.last_right_fire_time) >= self.RIGHT_COOLDOWN:
            if self.get_ammo_gauge() >= self.right_click_ammo_cost:
                self._fire(overcharge=True)
                self.last_right_fire_time = now

    # 발사/효과
    def _fire(self, overcharge=False):
        # 자원
        cost = self.right_click_ammo_cost if overcharge else self.left_click_ammo_cost
        self.reduce_ammo(cost)
        self.last_shot_time = pygame.time.get_ticks()

        # 사운드
        s = self.sounds.get("fire")
        if s:
            try: s.play()
            except Exception: pass

        # 시작 위치/방향
        (ux, uy), _ = self._unit_from_mouse()
        px, py = self.get_player_world_position()
        sx = px + ux * 30 * config.PLAYER_VIEW_SCALE
        sy = py + uy * 30 * config.PLAYER_VIEW_SCALE

        # ▶ 에임 보조(초기 유도): ±10°/사거리 내 적에게 방향 보정
        ux, uy = self._apply_aim_assist(sx, sy, ux, uy, overcharge)

        # 투사체 생성
        vx = ux * self.PROJ_SPEED
        vy = uy * self.PROJ_SPEED
        self._shots.append({"x": sx, "y": sy, "vx": vx, "vy": vy, "traveled": 0.0, "overcharge": overcharge})

        # ▶ 머즐 FX: 항상 보임
        self._spawn_muzzle_fx(sx, sy, ux, uy, overcharge)

        # 흔들림(우클릭 보정)
        shake = self.SHAKE_BASE + (self.SHAKE_RIGHT_BOOST if overcharge else 0)
        self._shake(shake, timer=8)

    def _apply_aim_assist(self, sx, sy, ux, uy, overcharge):
        # 가장 각도 차가 작은 적(콘 내부) 선택
        enemies_list = getattr(config, "all_enemies", getattr(config, "enemies", []))
        max_deg = self.HOMING_ANGLE_DEG_RIGHT if overcharge else self.HOMING_ANGLE_DEG_LEFT
        max_rad = math.radians(max_deg)
        max_dist = self.HOMING_RANGE_RIGHT if overcharge else self.HOMING_RANGE_LEFT
        best = None
        best_ang = None
        for e in list(enemies_list):
            if not getattr(e, "alive", False): continue
            ex = getattr(e, "world_x", getattr(e, "x", None))
            ey = getattr(e, "world_y", getattr(e, "y", None))
            if ex is None or ey is None: continue
            dx, dy = ex - sx, ey - sy
            dist = math.hypot(dx, dy)
            if dist <= 1e-3 or dist > max_dist: 
                continue
            vx, vy = dx / dist, dy / dist
            # 전방 콘 체크
            dot = max(-1.0, min(1.0, ux * vx + uy * vy))
            ang = math.acos(dot)
            if ang <= max_rad:
                if best is None or ang < best_ang:
                    best, best_ang = (vx, vy), ang
        if best:
            return best
        return ux, uy

    def _spawn_muzzle_fx(self, sx, sy, ux, uy, overcharge):
        import random
        # 짧은 가지 아크 다발
        forks = 3 if not overcharge else 5
        base_len = 80 if not overcharge else 120
        w = self.ARC_W_LEFT if not overcharge else self.ARC_W_RIGHT
        for i in range(forks):
            t = (i + 1) / (forks + 1)
            # 진행 방향 약간의 각도 랜덤
            ang_off = (random.random() - 0.5) * 0.35  # rad
            ca, sa = math.cos(ang_off), math.sin(ang_off)
            fux, fuy = ux * ca - uy * sa, ux * sa + uy * ca
            L = base_len * (0.7 + 0.6 * random.random())
            ex, ey = sx + fux * L, sy + fuy * L
            self._add_arc(sx, sy, ex, ey, width=w)
        # 스파크(머즐 플래시)
        self._sparks.append({"x": sx, "y": sy, "until_ms": pygame.time.get_ticks() + self.SPARK_FLASH_MS})
        # 짧은 트레이서
        self._tracers.append({"a": (sx, sy), "b": (sx + ux * 90, sy + uy * 90),
                              "until_ms": pygame.time.get_ticks() + self.TRACER_LIFETIME_MS})

    def _air_burst_fx(self, x, y, overcharge):
        import random
        # 끝점에서 방사형 스파크 + 짧은 가지 아크
        branches = 6 if not overcharge else 9
        radius = 120 if not overcharge else 160
        w = self.ARC_W_LEFT if not overcharge else self.ARC_W_RIGHT
        for i in range(branches):
            ang = random.random() * math.tau
            L = radius * (0.6 + 0.5 * random.random())
            ex = x + math.cos(ang) * L
            ey = y + math.sin(ang) * L
            self._add_arc(x, y, ex, ey, width=w)
        # 중앙 스파크 더 크게
        self._sparks.append({"x": x, "y": y, "until_ms": pygame.time.get_ticks() + self.SPARK_FLASH_MS})

    # 투사체/체인
    def _update_shots(self):
        enemies_list = getattr(config, "all_enemies", getattr(config, "enemies", []))
        for i in reversed(range(len(self._shots))):
            s = self._shots[i]
            # 이동
            s["x"] += s["vx"]
            s["y"] += s["vy"]
            s["traveled"] += (abs(s["vx"]) + abs(s["vy"])) * 0.5

            # 충돌 검사
            hit_enemy = None
            for e in list(enemies_list):
                if not getattr(e, "alive", False): continue
                ex0 = getattr(e, "world_x", getattr(e, "x", None))
                ey0 = getattr(e, "world_y", getattr(e, "y", None))
                if ex0 is None or ey0 is None: continue
                rad = int(getattr(e, "radius", 26))
                if math.hypot(ex0 - s["x"], ey0 - s["y"]) <= (self.PROJ_RADIUS_HIT + rad):
                    hit_enemy = e
                    break

            out = s["traveled"] >= self.PROJ_MAX_TRAVEL

            if hit_enemy or out:
                # 트레이서 꼬리
                tail_len = 160  # 120 -> 160 (좀 더 길게)
                L = max(1e-6, math.hypot(s["vx"], s["vy"]))
                ux, uy = s["vx"] / L, s["vy"] / L
                self._tracers.append({"a": (s["x"] - ux * tail_len, s["y"] - uy * tail_len),
                                      "b": (s["x"], s["y"]),
                                      "until_ms": pygame.time.get_ticks() + self.TRACER_LIFETIME_MS})
                if hit_enemy:
                    self._on_primary_hit(s, hit_enemy)
                else:
                    # ▶ 에어버스트(빈 공간 피니시 연출)
                    self._air_burst_fx(s["x"], s["y"], overcharge=s["overcharge"])
                self._shots.pop(i)

    def _on_primary_hit(self, shot, first_enemy):
        # 본탄 대미지
        self._damage_enemy(first_enemy, self.PRIMARY_DAMAGE)

        # 첫 히트 스파크(조금 더 크게)
        self._sparks.append({
            "x": getattr(first_enemy, "world_x", getattr(first_enemy, "x", 0)),
            "y": getattr(first_enemy, "world_y", getattr(first_enemy, "y", 0)),
            "until_ms": pygame.time.get_ticks() + self.SPARK_FLASH_MS
        })

        # 체인 파라미터
        if shot["overcharge"]:
            max_hops = self.CHAIN_MAX_RIGHT
            radius   = self.CHAIN_RADIUS_RIGHT
            arc_w    = self.ARC_W_RIGHT
        else:
            max_hops = self.CHAIN_MAX_LEFT
            radius   = self.CHAIN_RADIUS_LEFT
            arc_w    = self.ARC_W_LEFT

        hit_set = {first_enemy}
        prev_e = first_enemy

        # hop-by-hop: 가장 가까운 적을 찾아 연쇄
        for _ in range(max_hops):
            next_e = self._find_next_target(prev_e, hit_set, radius)
            if not next_e:
                break
            # 대미지
            self._damage_enemy(next_e, self.CHAIN_DAMAGE)
            # 아크 비주얼
            ax = getattr(prev_e, "world_x", getattr(prev_e, "x", 0))
            ay = getattr(prev_e, "world_y", getattr(prev_e, "y", 0))
            bx = getattr(next_e, "world_x", getattr(next_e, "x", 0))
            by = getattr(next_e, "world_y", getattr(next_e, "y", 0))
            self._add_arc(ax, ay, bx, by, width=arc_w)
            # 스파크
            self._sparks.append({"x": bx, "y": by, "until_ms": pygame.time.get_ticks() + self.SPARK_FLASH_MS})

            hit_set.add(next_e)
            prev_e = next_e

    def _find_next_target(self, from_enemy, already, radius):
        enemies_list = getattr(config, "all_enemies", getattr(config, "enemies", []))
        fx = getattr(from_enemy, "world_x", getattr(from_enemy, "x", 0))
        fy = getattr(from_enemy, "world_y", getattr(from_enemy, "y", 0))
        best, best_d2 = None, None
        for e in list(enemies_list):
            if e in already or not getattr(e, "alive", False):
                continue
            ex = getattr(e, "world_x", getattr(e, "x", None))
            ey = getattr(e, "world_y", getattr(e, "y", None))
            if ex is None or ey is None:
                continue
            dx, dy = ex - fx, ey - fy
            d2 = dx*dx + dy*dy
            if d2 <= radius*radius and (best is None or d2 < best_d2):
                best, best_d2 = e, d2
        return best

    def _damage_enemy(self, e, dmg):
        try:
            if hasattr(e, "hit"):
                e.hit(dmg, None)
            elif hasattr(e, "on_hit"):
                e.on_hit(dmg, knockback=0, hit_type="electric")
            else:
                e.hp = getattr(e, "hp", 0) - dmg
                if e.hp <= 0:
                    e.alive = False
        except Exception:
            pass

    # 비주얼 생성
    def _add_arc(self, ax, ay, bx, by, width=3):
        # 지그재그 번개 폴리라인 생성.
        import random
        pts = []
        segs = max(3, self.ARC_SEGMENTS)
        dx, dy = bx - ax, by - ay
        L = math.hypot(dx, dy) + 1e-6
        nx, ny = -dy / L, dx / L
        for i in range(segs + 1):
            t = i / float(segs)
            x = ax + dx * t
            y = ay + dy * t
            # 수직 방향 난수 흔들림(길수록 진폭 증가)
            amp = 9 + 0.03 * L   # 6->9, 길수록 좀 더 출렁
            jitter = (random.random() - 0.5) * amp
            pts.append((x + nx * jitter, y + ny * jitter))
        self._arcs.append({"points": pts,
                           "until_ms": pygame.time.get_ticks() + self.ARC_LIFETIME_MS,
                           "width": width})

    # 렌더
    def draw_overlay(self, screen):
        sw, sh = screen.get_size()

        # 트레이서
        if self._tracers:
            surf = pygame.Surface((sw, sh), pygame.SRCALPHA)
            for t in self._tracers:
                ax, ay = self._world_to_screen(*t["a"])
                bx, by = self._world_to_screen(*t["b"])
                pygame.draw.line(surf, (120, 200, 255, 90), (ax, ay), (bx, by), 8)
                pygame.draw.line(surf, (255, 255, 255, 200), (ax, ay), (bx, by), 3)
            screen.blit(surf, (0, 0))

        # 아크(지그재그 번개)
        if self._arcs:
            surf = pygame.Surface((sw, sh), pygame.SRCALPHA)
            for a in self._arcs:
                pts = [self._world_to_screen(px, py) for (px, py) in a["points"]]
                w = a["width"]
                if len(pts) >= 2:
                    # 글로우 3겹(굵기 전반 상향)
                    pygame.draw.lines(surf, (80, 190, 255, 100), False, pts, max(1, int(w * 3.2)))
                    pygame.draw.lines(surf, (150, 230, 255, 160), False, pts, max(1, int(w * 1.9)))
                    pygame.draw.lines(surf, (255, 255, 255, 230), False, pts, max(1, int(w)))
            screen.blit(surf, (0, 0))

        # 스파크 플래시(크기 ↑)
        if self._sparks:
            surf = pygame.Surface((sw, sh), pygame.SRCALPHA)
            for s in self._sparks:
                sx, sy = self._world_to_screen(s["x"], s["y"])
                pygame.draw.circle(surf, (200, 240, 255, 180), (int(sx), int(sy)), self.SPARK_RADIUS_IN)
                pygame.draw.circle(surf, (120, 200, 255, 110), (int(sx), int(sy)), self.SPARK_RADIUS_OUT, width=3)
            screen.blit(surf, (0, 0))

class Gun30(WeaponBase):
    TIER = 5

    TICK_MS = 80
    DAMAGE_PER_TICK = 20
    AMMO_PER_SEC = 25.0
    AMMO_PER_TICK = AMMO_PER_SEC * (TICK_MS / 1000.0)
    HEAT_PER_TICK = 2.0
    HEAT_COOL_PER_SEC_IDLE = 35.0
    HEAT_COOL_PER_SEC_FIRING = 5.0
    OVERHEAT_THRESHOLD = 100.0
    OVERHEAT_LOCK_MS = 2500

    SPECTRUM_DURATION_MS = 400
    SPLIT_ANGLE_DEG = 12.0
    SPLIT_DAMAGE_FACTOR = 0.45
    SPLIT_RESOURCE_MULT = 1.35

    RANGE = int(4200 * config.PLAYER_VIEW_SCALE)
    WIDTH_MAIN = 8
    WIDTH_SIDE = 6

    RING_LIFETIME_MS = 70
    STARBURST_LIFETIME_MS = 120
    MUZZLE_ARC_LIFETIME_MS = 110
    TRACER_LIFETIME_MS = 90

    SHAKE_BASE = 8
    SHAKE_SPECTRUM_BOOST = 3
    SPEED_PENALTY_ON = 0.35

    ZIGZAG_SEGS = 18 
    ZIGZAG_CYCLES = 9.0
    ZIGZAG_SCROLL_CPS = 1.8
    ZIGZAG_AMP_MAIN = 6.0
    ZIGZAG_AMP_SIDE = 4.0
    ZIGZAG_WOBBLE = 0.35

    HEAT_BAR_W = 120
    HEAT_BAR_H = 8
    HEAT_BAR_GAP_Y = 56

    @staticmethod
    def create_instance(weapon_assets, sounds, ammo_gauge, consume_ammo, get_player_world_position):
        return Gun30(
            name="프리즘 발사기",
            front_image=weapon_assets["gun30"]["front"],
            topdown_image=weapon_assets["gun30"]["topdown"],
            uses_bullets=False, bullet_images=weapon_assets["gun30"]["bullets"],
            uses_cartridges=False, cartridge_images=weapon_assets["gun30"]["cartridges"],
            can_left_click=True, can_right_click=True,
            left_click_ammo_cost=0, right_click_ammo_cost=0,
            tier=Gun30.TIER,
            sounds_dict={"fire": sounds["gun30_fire"], "overheat": sounds["gun5_overheat"]},
            get_ammo_gauge_fn=ammo_gauge, reduce_ammo_fn=consume_ammo,
            bullet_has_trail=False, get_player_world_position_fn=get_player_world_position,
            exclusive_inputs=True
        )

    LEFT_COOLDOWN = 0
    RIGHT_COOLDOWN = 0
    LEFT_AMMO_COST = 0
    RIGHT_AMMO_COST = 0

    def __init__(self, name, front_image, topdown_image, **kwargs):
        super().__init__(name, front_image, topdown_image, **kwargs)
        self.distance_from_center = 48 * config.PLAYER_VIEW_SCALE
        self.recoil_strength = 6
        self.speed_penalty = 0.1

        self._left_hold = False
        self._overheated_until = 0
        self._heat = 0.0
        self._tick_next_ms = pygame.time.get_ticks()
        self._ammo_accum = 0.0

        self._spectrum_until = 0
        self._prev_right_down = False

        self._loop_ch = None

        self._last_dirs = []
        self._beam_active = False
        self._last_update_ms = pygame.time.get_ticks()
        self.last_shot_time = 0

        self._rings = []
        self._starbursts = []
        self._muzzle_arcs = []
        self._tracers = []

        import random
        self._jseed = random.random() * 1000.0

    # 유틸
    def _unit_from_mouse(self):
        mx, my = pygame.mouse.get_pos()
        dx = mx - config.player_rect.centerx
        dy = my - config.player_rect.centery
        ang = math.atan2(dy, dx)
        return (math.cos(ang), math.sin(ang)), ang

    def _world_to_screen(self, wx, wy):
        cx, cy = config.player_rect.centerx, config.player_rect.centery
        px, py = self.get_player_world_position()
        return (cx + (wx - px), cy + (wy - py))

    def _apply_shake(self, extra=0, timer=6):
        try:
            strength = self.SHAKE_BASE + extra
            config.shake_strength = max(getattr(config, "shake_strength", 0), strength)
            config.shake_timer = max(getattr(config, "shake_timer", 0), timer)
        except Exception:
            pass

    def _start_loop(self):
        if self._loop_ch:
            return
        s = self.sounds.get("fire")
        if not s:
            return
        ch = pygame.mixer.find_channel()
        if ch:
            try: ch.play(s, loops=-1, fade_ms=80)
            except Exception: pass
            self._loop_ch = ch

    def _stop_loop(self):
        if self._loop_ch:
            try: self._loop_ch.fadeout(120)
            except Exception: pass
            self._loop_ch = None
        self._force_kill_loop_channels()
 
    def _force_kill_loop_channels(self):
        # gun30_fire가 재생 중인 채널이 있으면 모두 정지(유령 루프 방지).
        try:
            s = self.sounds.get("fire")
            if not s:
                return
            # 캐싱된 채널이 있어도 한 번 더 안전하게 정지
            if self._loop_ch:
                try: self._loop_ch.stop()
                except Exception: pass
                self._loop_ch = None
            # mixer 전체 채널을 스윕하며 동일 Sound 인스턴스면 정지
            num = pygame.mixer.get_num_channels()
            for i in range(num):
                ch = pygame.mixer.Channel(i)
                try:
                    if ch.get_sound() is s:
                        ch.stop()
                except Exception:
                    pass
        except Exception:
            pass

    def _cool_heat(self, now_ms, dt_ms, firing: bool):
        if now_ms < self._overheated_until:
            return
        rate = self.HEAT_COOL_PER_SEC_FIRING if firing else self.HEAT_COOL_PER_SEC_IDLE
        if self._heat > 0.0:
            self._heat = max(0.0, self._heat - rate * (dt_ms / 1000.0))

    def _overheat_trip(self):
        self._overheated_until = pygame.time.get_ticks() + self.OVERHEAT_LOCK_MS
        self._stop_loop()
        s = self.sounds.get("overheat")
        if s:
            try: s.play()
            except Exception: pass
        self._apply_shake(extra=3, timer=10)
        self._beam_active = False
        self._last_dirs = []

    def _is_overheated(self):
        return pygame.time.get_ticks() < self._overheated_until

    # 입력/업데이트
    def on_update(self, mouse_left_down, mouse_right_down):
        now = pygame.time.get_ticks()
        dt = now - self._last_update_ms
        self._last_update_ms = now

        # 우클릭(분광) — 홀드 중 0.4s 윈도우 갱신
        if mouse_right_down and not self._is_overheated():
            if not self._prev_right_down:
                self._spawn_prism_pulse()
                self._apply_shake(extra=self.SHAKE_SPECTRUM_BOOST, timer=8)
            self._spectrum_until = now + self.SPECTRUM_DURATION_MS
        self._prev_right_down = mouse_right_down

        # 좌클릭 홀드
        self._left_hold = bool(mouse_left_down)

        # 출력 의지/가능
        want_output = self._left_hold or (now < self._spectrum_until)
        can_output = want_output and (not self._is_overheated())

        # 냉각(사격 여부 반영)
        self._cool_heat(now, dt, firing=can_output)

        # 사운드/패널티
        if can_output and self.get_ammo_gauge() > 0:
            self.speed_penalty = self.SPEED_PENALTY_ON
            self._start_loop()
        else:
            self.speed_penalty = 0.05
            self._stop_loop()
            self._beam_active = False
            self._last_dirs = []
            return

        # 빔 방향(분광 포함)
        (ux, uy), _ = self._unit_from_mouse()
        dirs = [(ux, uy, self.WIDTH_MAIN, False)]
        if now < self._spectrum_until:
            off = math.radians(self.SPLIT_ANGLE_DEG)
            ca, sa = math.cos(off), math.sin(off)
            # 좌(-off), 우(+off)
            lx, ly = (ux * math.cos(-off) - uy * math.sin(-off)), (ux * math.sin(-off) + uy * math.cos(-off))
            rx, ry = (ux * ca - uy * sa), (ux * sa + uy * ca)
            lL = math.hypot(lx, ly); rL = math.hypot(rx, ry)
            dirs.append((lx / max(1e-6, lL), ly / max(1e-6, lL), self.WIDTH_SIDE, True))
            dirs.append((rx / max(1e-6, rL), ry / max(1e-6, rL), self.WIDTH_SIDE, True))

        self._beam_active = True
        self._last_dirs = dirs

        # 틱(80ms)
        if now >= self._tick_next_ms:
            self._tick_next_ms = now + self.TICK_MS
            self._do_tick(dirs)
            self.last_shot_time = now

    # 틱 처리
    def _do_tick(self, dirs):
        # 자원 소모 (분광시 배수)
        mult = (self.SPLIT_RESOURCE_MULT if any(d[3] for d in dirs) else 1.0)
        if not self._consume_resources(mult):
            self._beam_active = False
            self._stop_loop()
            return

        # 히트스캔
        px, py = self.get_player_world_position()
        enemies_list = getattr(config, "all_enemies", getattr(config, "enemies", []))

        for (dx, dy, width, is_side) in dirs:
            sx = px + dx * 30 * config.PLAYER_VIEW_SCALE
            sy = py + dy * 30 * config.PLAYER_VIEW_SCALE
            ex = sx + dx * self.RANGE
            ey = sy + dy * self.RANGE

            dmg = self.DAMAGE_PER_TICK * (self.SPLIT_DAMAGE_FACTOR if is_side else 1.0)

            nearest_t = None
            nearest_hit_pos = None

            for e in list(enemies_list):
                if not getattr(e, "alive", False): continue
                ex0 = getattr(e, "world_x", getattr(e, "x", None))
                ey0 = getattr(e, "world_y", getattr(e, "y", None))
                if ex0 is None or ey0 is None: continue
                t, dist = self._segment_dist_with_t(ex0, ey0, sx, sy, ex, ey)
                if dist <= (int(getattr(e, "radius", 26)) + width * 0.5):
                    self._damage_enemy(e, int(dmg))
                    if nearest_t is None or t < nearest_t:
                        nearest_t = t
                        hx = sx + (ex - sx) * t
                        hy = sy + (ey - sy) * t
                        nearest_hit_pos = (hx, hy)

            if nearest_hit_pos:
                self._spawn_ring(*nearest_hit_pos)
            else:
                self._spawn_starburst(ex, ey)

        # 열 누적/과열
        self._heat += self.HEAT_PER_TICK * mult
        if self._heat >= self.OVERHEAT_THRESHOLD:
            self._overheat_trip()

        # 화면 미세 흔들림
        extra = self.SHAKE_SPECTRUM_BOOST if any(d[3] for d in dirs) else 0
        self._apply_shake(extra=extra, timer=6)

    def _consume_resources(self, mult) -> bool:
        need = self.AMMO_PER_TICK * mult
        self._ammo_accum += need
        deduct = int(self._ammo_accum)
        if deduct > 0:
            have = self.get_ammo_gauge()
            if have <= 0:
                self._ammo_accum = 0.0
                return False
            take = min(deduct, have)
            self.reduce_ammo(take)
            self._ammo_accum -= take
        return True

    # 기하
    def _segment_dist_with_t(self, px0, py0, x1, y1, x2, y2):
        vx = x2 - x1; vy = y2 - y1
        wx = px0 - x1; wy = py0 - y1
        L2 = vx * vx + vy * vy
        if L2 <= 1e-6:
            return 0.0, math.hypot(wx, wy)
        t = (wx * vx + wy * vy) / L2
        t = 0.0 if t < 0.0 else (1.0 if t > 1.0 else t)
        projx = x1 + t * vx
        projy = y1 + t * vy
        return t, math.hypot(px0 - projx, py0 - projy)

    def _damage_enemy(self, e, dmg):
        try:
            if hasattr(e, "hit"):
                e.hit(dmg, None)
            elif hasattr(e, "on_hit"):
                e.on_hit(dmg, knockback=0, hit_type="laser")
            else:
                e.hp = getattr(e, "hp", 0) - dmg
                if e.hp <= 0:
                    e.alive = False
        except Exception:
            pass

    # FX
    def _spawn_ring(self, x, y):
        self._rings.append({"x": x, "y": y, "until_ms": pygame.time.get_ticks() + self.RING_LIFETIME_MS})

    def _spawn_starburst(self, x, y):
        self._starbursts.append({"x": x, "y": y, "until_ms": pygame.time.get_ticks() + self.STARBURST_LIFETIME_MS})

    def _spawn_prism_pulse(self):
        (ux, uy), _ = self._unit_from_mouse()
        px, py = self.get_player_world_position()
        sx = px + ux * 30 * config.PLAYER_VIEW_SCALE
        sy = py + uy * 30 * config.PLAYER_VIEW_SCALE
        import random
        forks = 4
        base_len = 70
        for i in range(forks):
            ang = (random.random() - 0.5) * 0.4
            ca, sa = math.cos(ang), math.sin(ang)
            fx, fy = ux * ca - uy * sa, ux * sa + uy * ca
            L = base_len * (0.7 + 0.6 * random.random())
            ex, ey = sx + fx * L, sy + fy * L
            self._muzzle_arcs.append({"a": (sx, sy), "b": (ex, ey),
                                      "until_ms": pygame.time.get_ticks() + self.MUZZLE_ARC_LIFETIME_MS})
        self._tracers.append({"a": (sx, sy), "b": (sx + ux * 100, sy + uy * 100),
                              "until_ms": pygame.time.get_ticks() + self.TRACER_LIFETIME_MS})

    def on_weapon_switch(self):
        self._stop_loop()
        self._force_kill_loop_channels()
        self._beam_active = False
        self._last_dirs = []
        self._spectrum_until = 0
        self.speed_penalty = 0.2

    # 지그재그 폴리라인
    def _zigzag_polyline(self, a, b, amp_px, segs, now_ms):
        # a-b 직선을 '지그재그'로 꺾은 폴리라인으로 변환.
        # - ZIGZAG_CYCLES 만큼 톱니가 생김
        # - ZIGZAG_SCROLL_CPS 속도로 시간에 따라 패턴이 흐름(모양이 계속 바뀜)
        # - 사각파 기반 좌/우 번갈이 오프셋 + 약간의 sine wobble 섞기
        ax, ay = a; bx, by = b
        dx, dy = bx - ax, by - ay
        L = math.hypot(dx, dy) + 1e-6
        nx, ny = -dy / L, dx / L  # unit normal (좌측)
        pts = []
        # 시간 기반 스크롤 (초 단위)
        phase = (now_ms / 1000.0) * self.ZIGZAG_SCROLL_CPS + self._jseed
        for i in range(segs + 1):
            t = i / float(segs)
            x = ax + dx * t
            y = ay + dy * t
            u = t * self.ZIGZAG_CYCLES + phase
            frac = u - math.floor(u)         # [0,1)
            sign = 1.0 if frac < 0.5 else -1.0
            wobble = self.ZIGZAG_WOBBLE * amp_px * math.sin(u * math.tau * 0.65)
            off = (amp_px * sign) + wobble
            pts.append((x + nx * off, y + ny * off))
        return pts

    # 렌더
    def draw_overlay(self, screen):
        sw, sh = screen.get_size()
        now = pygame.time.get_ticks()

        # 오래된 FX 정리
        self._rings[:] = [r for r in self._rings if now <= r["until_ms"]]
        self._starbursts[:] = [s for s in self._starbursts if now <= s["until_ms"]]
        self._muzzle_arcs[:] = [m for m in self._muzzle_arcs if now <= m["until_ms"]]
        self._tracers[:] = [t for t in self._tracers if now <= t["until_ms"]]

        # 레이저 본체 — 지그재그 폴리라인
        if self._beam_active and self._last_dirs:
            surf = pygame.Surface((sw, sh), pygame.SRCALPHA)
            px, py = self.get_player_world_position()
            for (dx, dy, width, is_side) in self._last_dirs:
                sx = px + dx * 30 * config.PLAYER_VIEW_SCALE
                sy = py + dy * 30 * config.PLAYER_VIEW_SCALE
                ex = sx + dx * self.RANGE
                ey = sy + dy * self.RANGE
                a = self._world_to_screen(sx, sy)
                b = self._world_to_screen(ex, ey)

                amp = self.ZIGZAG_AMP_SIDE if is_side else self.ZIGZAG_AMP_MAIN
                pts = self._zigzag_polyline(a, b, amp, self.ZIGZAG_SEGS, now)

                # 글로우 3겹
                pygame.draw.lines(surf, (90, 220, 255, 90),  False, pts, max(1, int(width * 2.8)))
                pygame.draw.lines(surf, (160, 240, 255, 170), False, pts, max(1, int(width * 1.7)))
                pygame.draw.lines(surf, (255, 255, 255, 230), False, pts, max(1, int(width)))

                # 크로마틱 가장자리 1px
                # 평균 노멀로 좌우 offset
                ax, ay = a; bx, by = b
                dx0, dy0 = bx - ax, by - ay
                L0 = math.hypot(dx0, dy0) + 1e-6
                nx, ny = -dy0 / L0, dx0 / L0
                off = 1
                pts_r = [(x + nx * off, y + ny * off) for (x, y) in pts]
                pts_g = [(x - nx * off, y - ny * off) for (x, y) in pts]
                pygame.draw.lines(surf, (255, 80, 80, 110),  False, pts_r, 1)
                pygame.draw.lines(surf, (80, 255, 120, 110), False, pts_g, 1)

            screen.blit(surf, (0, 0))

        # 링 FX
        if self._rings:
            surf = pygame.Surface((sw, sh), pygame.SRCALPHA)
            for r in self._rings:
                t = 1.0 - (r["until_ms"] - now) / float(self.RING_LIFETIME_MS)
                rad = 22 + int(18 * t)
                cx, cy = self._world_to_screen(r["x"], r["y"])
                pygame.draw.circle(surf, (150, 220, 255, 150), (int(cx), int(cy)), rad, width=3)
                pygame.draw.circle(surf, (255, 255, 255, 120), (int(cx), int(cy)), max(1, rad - 6), width=1)
            screen.blit(surf, (0, 0))

        # 스타버스트 FX
        if self._starbursts:
            surf = pygame.Surface((sw, sh), pygame.SRCALPHA)
            for s in self._starbursts:
                cx, cy = self._world_to_screen(s["x"], s["y"])
                life = (s["until_ms"] - now) / float(self.STARBURST_LIFETIME_MS)
                life = max(0.0, min(1.0, life))
                alpha = int(200 * life)
                r1 = 12 + int(20 * (1 - life))
                r2 = r1 + 8
                pygame.draw.circle(surf, (200, 240, 255, alpha), (int(cx), int(cy)), r1, width=2)
                pygame.draw.circle(surf, (120, 200, 255, int(alpha * 0.6)), (int(cx), int(cy)), r2, width=2)
                for k in range(6):
                    ang = (math.tau / 6) * k
                    ex = cx + math.cos(ang) * (r2 + 10)
                    ey = cy + math.sin(ang) * (r2 + 10)
                    pygame.draw.line(surf, (255, 255, 255, alpha), (cx, cy), (ex, ey), 2)
            screen.blit(surf, (0, 0))

        # 머즐 아크/트레이서
        if self._muzzle_arcs or self._tracers:
            surf = pygame.Surface((sw, sh), pygame.SRCALPHA)
            for m in self._muzzle_arcs:
                a = self._world_to_screen(*m["a"])
                b = self._world_to_screen(*m["b"])
                pygame.draw.line(surf, (120, 220, 255, 120), a, b, 4)
                pygame.draw.line(surf, (255, 255, 255, 200), a, b, 2)
            for t in self._tracers:
                a = self._world_to_screen(*t["a"])
                b = self._world_to_screen(*t["b"])
                pygame.draw.line(surf, (120, 220, 255, 90), a, b, 6)
                pygame.draw.line(surf, (255, 255, 255, 200), a, b, 2)
            screen.blit(surf, (0, 0))

        # HEAT 바(플레이어 머리 위)
        cx, cy = config.player_rect.centerx, config.player_rect.centery
        bx = cx - self.HEAT_BAR_W // 2
        by = cy - self.HEAT_BAR_GAP_Y
        ratio = max(0.0, min(1.0, self._heat / self.OVERHEAT_THRESHOLD))
        bg = pygame.Rect(bx, by, self.HEAT_BAR_W, self.HEAT_BAR_H)
        pygame.draw.rect(screen, (35, 35, 45), bg, border_radius=6)
        if self._is_overheated() and ((now // 120) % 2 == 0):
            fill_col = (255, 90, 90)
        else:
            fill_col = (90, 210, 255)
        pygame.draw.rect(screen, fill_col, (bx, by, int(self.HEAT_BAR_W * ratio), self.HEAT_BAR_H), border_radius=6)
        pygame.draw.rect(screen, (120, 140, 180), bg, width=2, border_radius=6)

class Gun31(WeaponBase):
    TIER = 5

    MAX_LOCKS = 6
    LOCK_TIME_MS = 750
    LOCK_CONE_DEG = 28
    LOCK_RANGE = int(820 * config.PLAYER_VIEW_SCALE)
    LOCK_LOST_GRACE_MS = 450

    AMMO_PER_MISSILE = 17
    COOLDOWN_MS = 1200

    DAMAGE_PER_MISSILE = 80
    SPLASH_RADIUS = 40
    SPLASH_FACTOR = 0.3

    MISSILE_SPEED_START = 14.0
    MISSILE_SPEED_MAX = 24.0
    MISSILE_ACCEL_TIME = 250.0
    MISSILE_TURN_DEG_PER_S = 240.0
    MISSILE_LIFETIME_MS = 2800
    MISSILE_MAX_TRAVEL = int(2400 * config.PLAYER_VIEW_SCALE)
    MISSILE_HIT_RADIUS = 10

    TRAIL_LIFE_MS = 220
    TRAIL_STEP_PX = 18
    RING_LIFETIME_MS = 120
    EXPLOSION_RING_MS = 100

    @staticmethod
    def create_instance(weapon_assets, sounds, ammo_gauge, consume_ammo, get_player_world_position):
        return Gun31(
            name="마이크로미사일 벌집기",
            front_image=weapon_assets["gun31"]["front"],
            topdown_image=weapon_assets["gun31"]["topdown"],
            uses_bullets=True, bullet_images=weapon_assets["gun31"]["bullets"],
            uses_cartridges=False, cartridge_images=weapon_assets["gun31"]["cartridges"],
            can_left_click=True, can_right_click=False,
            left_click_ammo_cost=0, right_click_ammo_cost=0,
            tier=Gun31.TIER,
            sounds_dict={
                "fire": sounds["gun31_fire"],
                "explosion": sounds["gun31_explosion"],
                "lock": sounds.get("button_click")
            },
            get_ammo_gauge_fn=ammo_gauge, reduce_ammo_fn=consume_ammo,
            bullet_has_trail=False,
            get_player_world_position_fn=get_player_world_position,
            exclusive_inputs=True
        )

    def __init__(self, name, front_image, topdown_image, **kwargs):
        super().__init__(name, front_image, topdown_image, **kwargs)
        self.distance_from_center = 48 * config.PLAYER_VIEW_SCALE
        self.recoil_strength = 7
        self.speed_penalty = 0.2

        self._locks = []
        self._prev_left = False

        self._next_fire_ms = 0

        self._missiles = []

        self._rings = []
        self.last_shot_time = 0

        self._missile_img = self.bullet_images[0] if self.bullet_images else None

        self._last_explo_snd_ms = 0

    # 기본 유틸
    def _now(self): return pygame.time.get_ticks()

    def _world_to_screen(self, wx, wy):
        cx, cy = config.player_rect.centerx, config.player_rect.centery
        px, py = self.get_player_world_position()
        return (cx + (wx - px), cy + (wy - py))

    def _unit_from_mouse(self):
        mx, my = pygame.mouse.get_pos()
        dx = mx - config.player_rect.centerx
        dy = my - config.player_rect.centery
        ang = math.atan2(dy, dx)
        return (math.cos(ang), math.sin(ang)), ang

    def _enemies(self):
        return getattr(config, "all_enemies", getattr(config, "enemies", []))

    # 메인 업데이트
    def on_update(self, mouse_left_down, mouse_right_down):
        now = self._now()
        dt = now - getattr(self, "_last_update_ms", now)
        self._last_update_ms = now

        # 좌클릭: 락온 진행
        if mouse_left_down:
            self._update_locks(dt)
        # 릴리즈 엣지 → 발사 시도
        if (not mouse_left_down) and self._prev_left:
            self._release_and_fire()

        self._prev_left = mouse_left_down

        # 미사일 갱신
        self._update_missiles(dt)

        # 오래된 FX 정리
        self._rings[:] = [r for r in self._rings if now <= r["until_ms"]]

    # 락온 로직
    def _update_locks(self, dt):
        now = self._now()
        (ux, uy), _ = self._unit_from_mouse()
        px, py = self.get_player_world_position()

        # 후보 수집
        cand = []
        for e in list(self._enemies()):
            if not getattr(e, "alive", False): continue
            ex = getattr(e, "world_x", getattr(e, "x", None))
            ey = getattr(e, "world_y", getattr(e, "y", None))
            if ex is None or ey is None: continue
            dx, dy = ex - px, ey - py
            dist = math.hypot(dx, dy)
            if dist > self.LOCK_RANGE or dist < 1e-3: continue
            vx, vy = dx / dist, dy / dist
            dot = max(-1.0, min(1.0, ux * vx + uy * vy))
            ang = math.degrees(math.acos(dot))
            if ang <= self.LOCK_CONE_DEG:      # ← 여유각 적용
                cand.append((ang, dist, e))

        cand.sort(key=lambda x: (x[0], x[1]))  # 각도 우선, 그다음 거리

        # 기존 락 유지 & 진행 업데이트
        for L in list(self._locks):
            e = L["e"]
            if not getattr(e, "alive", False):
                self._locks.remove(L)
                continue
            # 현재 위치/거리
            ex = getattr(e, "world_x", getattr(e, "x", None))
            ey = getattr(e, "world_y", getattr(e, "y", None))
            if ex is None or ey is None:
                self._locks.remove(L)
                continue
            dx_e, dy_e = ex - px, ey - py
            dist_e = math.hypot(dx_e, dy_e)
            # 콘 내에 있나?
            in_cone = any(e is c[2] for c in cand)
            # 한 번 후보에 들어오면 에임이 벗어나도 사정거리(×1.3) 내면 게이지 지속
            if in_cone or dist_e <= self.LOCK_RANGE * 1.3:
                L["t"] += dt
                if in_cone:
                    L["last_seen_ms"] = now
            else:
                if not L["locked"] and (now - L["last_seen_ms"] > self.LOCK_LOST_GRACE_MS):
                    self._locks.remove(L)
                    continue
            # 잠금 완료 처리(사운드 1회)
            if (not L["locked"]) and L["t"] >= self.LOCK_TIME_MS:
                L["locked"] = True
                if not L.get("clicked", False):
                    s = self.sounds.get("lock")
                    if s:
                        try: s.play()
                        except Exception: pass
                    L["clicked"] = True

        # 새 후보 추가(빈자리만, 최대 6)
        have = {L["e"] for L in self._locks}
        for _, _, e in cand:
            if len(self._locks) >= self.MAX_LOCKS:
                break
            if e in have:
                continue
            self._locks.append({"e": e, "t": 0.0, "locked": False, "last_seen_ms": now, "clicked": False})
            have.add(e)

        # 초과 제거(오래된 것부터)
        if len(self._locks) > self.MAX_LOCKS:
            self._locks = self._locks[:self.MAX_LOCKS]

    def _release_and_fire(self):
        now = self._now()
        if now < self._next_fire_ms:
            self._locks.clear()
            return

        # 잠근 타겟만 발사
        targets = [L["e"] for L in self._locks if L["locked"] and getattr(L["e"], "alive", False)]
        self._locks.clear()
        if not targets:
            return

        # 탄 확인 → 발사 수 결정
        have = self.get_ammo_gauge()
        can = max(0, int(have // self.AMMO_PER_MISSILE))
        n = min(len(targets), self.MAX_LOCKS, can)
        if n <= 0:
            return

        # 발사 & 자원 소모
        self._spawn_guided_salvo(targets[:n])
        self.reduce_ammo(self.AMMO_PER_MISSILE * n)
        self._after_fire_common()

    def _after_fire_common(self):
        now = self._now()
        self._next_fire_ms = now + self.COOLDOWN_MS
        self.last_shot_time = now
        # 사운드/반동/쉐이크
        s = self.sounds.get("fire")
        if s:
            try: s.play()
            except Exception: pass
        try:
            config.shake_strength = max(getattr(config, "shake_strength", 0), 8)
            config.shake_timer = max(getattr(config, "shake_timer", 0), 10)
        except Exception:
            pass

    # 발사
    def _spawn_guided_salvo(self, targets):
        (ux, uy), _ = self._unit_from_mouse()
        px, py = self.get_player_world_position()

        # 발사 포트 좌우 오프셋 + 미세 퍼짐
        offsets = [(-8, -4), (8, -4), (-8, 4), (8, 4), (-10, 0), (10, 0)]
        for i, e in enumerate(targets):
            if i >= self.MAX_LOCKS: break
            ox, oy = offsets[i % len(offsets)]
            sx = px + ux * 28 + ox
            sy = py + uy * 28 + oy
            # 초기 방향: 타겟 방향
            ex = getattr(e, "world_x", getattr(e, "x", None))
            ey = getattr(e, "world_y", getattr(e, "y", None))
            if ex is None or ey is None:
                ex, ey = sx + ux * 50, sy + uy * 50
            ang = math.atan2(ey - sy, ex - sx)
            self._spawn_missile(sx, sy, ang, seek=True, target=e)

    def _spawn_straight_salvo(self, n):
        (ux, uy), ang = self._unit_from_mouse()
        px, py = self.get_player_world_position()
        base_offsets = [(-10, -4), (10, -4), (-10, 4), (10, 4), (-12, 0), (12, 0)]
        for i in range(n):
            ox, oy = base_offsets[i % len(base_offsets)]
            sx = px + ux * 28 + ox
            sy = py + uy * 28 + oy
            spread = math.radians((i - n // 2) * 3.0)
            self._spawn_missile(sx, sy, ang + spread, seek=False, target=None)

    def _spawn_missile(self, sx, sy, ang, seek, target):
        now = self._now()
        self._missiles.append({
            "x": sx, "y": sy,
            "dir": ang, "spd": self.MISSILE_SPEED_START,
            "seek": seek, "target": target,
            "spawn_ms": now, "life_ms": 0, "dist": 0.0,
            "trail": [], "last_trail_pos": (sx, sy)
        })

    # 미사일 갱신/충돌
    def _update_missiles(self, dt):
        enemies = list(self._enemies())
        turn_rad_per_ms = math.radians(self.MISSILE_TURN_DEG_PER_S) / 1000.0

        for i in reversed(range(len(self._missiles))):
            m = self._missiles[i]

            # 가속
            if m["life_ms"] < self.MISSILE_ACCEL_TIME:
                t = m["life_ms"] / self.MISSILE_ACCEL_TIME
                m["spd"] = self.MISSILE_SPEED_START + (self.MISSILE_SPEED_MAX - self.MISSILE_SPEED_START) * t
            else:
                m["spd"] = self.MISSILE_SPEED_MAX

            # 호밍
            if m["seek"] and m["target"] and getattr(m["target"], "alive", False):
                tx = getattr(m["target"], "world_x", getattr(m["target"], "x", m["x"]))
                ty = getattr(m["target"], "world_y", getattr(m["target"], "y", m["y"]))
                des = math.atan2(ty - m["y"], tx - m["x"])
                # 각도 차 클램프
                delta = (des - m["dir"] + math.pi) % (2 * math.pi) - math.pi
                max_turn = turn_rad_per_ms * dt
                if delta > max_turn: delta = max_turn
                elif delta < -max_turn: delta = -max_turn
                m["dir"] += delta
            else:
                wob = 0.015 * math.sin((m["life_ms"] + i * 37) * 0.01)
                m["dir"] += wob

            # 이동
            vx, vy = math.cos(m["dir"]) * m["spd"], math.sin(m["dir"]) * m["spd"]
            m["x"] += vx
            m["y"] += vy
            m["life_ms"] += dt
            m["dist"] += abs(vx) + abs(vy)

            # 트레일
            lx, ly = m["last_trail_pos"]
            if math.hypot(m["x"] - lx, m["y"] - ly) >= self.TRAIL_STEP_PX:
                m["trail"].append((m["x"], m["y"], self._now() + self.TRAIL_LIFE_MS))
                m["last_trail_pos"] = (m["x"], m["y"])
            m["trail"][:] = [(x, y, t) for (x, y, t) in m["trail"] if self._now() <= t]

            # === 충돌 검사 ===
            # 벽/장애물 관통: 의도적으로 '장애물 충돌'은 검사하지 않음
            # (맵/투명벽 등과의 충돌 무시. 오직 '적 충돌' 또는 '수명/최대거리'로만 소멸)
            hit_enemy = None
            for e in enemies:
                if not getattr(e, "alive", False): continue
                ex = getattr(e, "world_x", getattr(e, "x", None))
                ey = getattr(e, "world_y", getattr(e, "y", None))
                if ex is None or ey is None: continue
                rad = int(getattr(e, "radius", 26))
                if math.hypot(ex - m["x"], ey - m["y"]) <= (rad + self.MISSILE_HIT_RADIUS):
                    hit_enemy = e
                    break

            # 수명/충돌/최대거리
            expired = (m["life_ms"] >= self.MISSILE_LIFETIME_MS) or (m["dist"] >= self.MISSILE_MAX_TRAVEL)
            if hit_enemy or expired:
                x, y = m["x"], m["y"]
                self._explode_at(x, y, hit_enemy)
                self._missiles.pop(i)

    def _explode_at(self, x, y, primary_enemy):
        # 피해
        if primary_enemy:
            self._damage_enemy(primary_enemy, self.DAMAGE_PER_MISSILE)
        # 스플래시
        if self.SPLASH_RADIUS > 0 and self.SPLASH_FACTOR > 0:
            r2 = self.SPLASH_RADIUS * self.SPLASH_RADIUS
            for e in list(self._enemies()):
                if e is primary_enemy or not getattr(e, "alive", False): continue
                ex = getattr(e, "world_x", getattr(e, "x", None))
                ey = getattr(e, "world_y", getattr(e, "y", None))
                if ex is None or ey is None: continue
                if (ex - x) * (ex - x) + (ey - y) * (ey - y) <= r2:
                    self._damage_enemy(e, int(self.DAMAGE_PER_MISSILE * self.SPLASH_FACTOR))

        # 사운드(중첩 재생 디바운스로 '깨짐' 방지)
        s = self.sounds.get("explosion")
        if s:
            try:
                now_ms = self._now()
                if now_ms - getattr(self, "_last_explo_snd_ms", 0) >= 80:
                    s.play()
                    self._last_explo_snd_ms = now_ms
            except Exception:
                pass

        # 링 FX
        self._rings.append({"x": x, "y": y, "until_ms": self._now() + self.EXPLOSION_RING_MS, "kind": "boom"})

    def _damage_enemy(self, e, dmg):
        try:
            if hasattr(e, "hit"):
                e.hit(dmg, None)
            elif hasattr(e, "on_hit"):
                e.on_hit(dmg, knockback=0, hit_type="explosion")
            else:
                e.hp = getattr(e, "hp", 0) - dmg
                if e.hp <= 0:
                    e.alive = False
        except Exception:
            pass

    # 렌더
    def draw_overlay(self, screen):
        sw, sh = screen.get_size()
        now = self._now()

        # 락온 HUD
        if self._locks:
            surf = pygame.Surface((sw, sh), pygame.SRCALPHA)
            for L in self._locks:
                e = L["e"]
                if not getattr(e, "alive", False): continue
                x = getattr(e, "world_x", getattr(e, "x", None))
                y = getattr(e, "world_y", getattr(e, "y", None))
                if x is None or y is None: continue
                sx, sy = self._world_to_screen(x, y)

                # 외곽 원
                col = (90, 210, 255, 180) if not L["locked"] else (255, 255, 255, 220)
                pygame.draw.circle(surf, col, (int(sx), int(sy)), 26, width=2)

                # 진행도 호(게이지)
                prog = max(0.0, min(1.0, L["t"] / self.LOCK_TIME_MS))
                if not L["locked"]:
                    end_ang = -math.pi / 2 + prog * 2 * math.pi
                    rect = pygame.Rect(int(sx - 28), int(sy - 28), 56, 56)
                    pygame.draw.arc(surf, (150, 230, 255, 200), rect, -math.pi/2, end_ang, 3)

                # 점선 연결 (플레이어 → 타겟)
                px, py = self.get_player_world_position()
                ax, ay = self._world_to_screen(px, py)
                self._dotted_line(surf, (ax, ay), (sx, sy), (120, 200, 255, 120), 6, 6)

            # 잠금 최대 텍스트
            if len([1 for L in self._locks if L["locked"]]) >= self.MAX_LOCKS:
                mx, my = pygame.mouse.get_pos()
                self._draw_text(surf, "LOCK MAX", (mx + 14, my - 18), (255, 255, 255, 220))

            screen.blit(surf, (0, 0))

        # 미사일 + 트레일
        if self._missiles:
            surf = pygame.Surface((sw, sh), pygame.SRCALPHA)
            for m in self._missiles:
                # 트레일
                for (tx, ty, until_ms) in m["trail"]:
                    a = max(0, min(255, int(255 * (until_ms - now) / self.TRAIL_LIFE_MS)))
                    sx, sy = self._world_to_screen(tx, ty)
                    pygame.draw.circle(surf, (120, 200, 255, a), (int(sx), int(sy)), 3)

                # 본체
                sx, sy = self._world_to_screen(m["x"], m["y"])
                if self._missile_img:
                    deg = -math.degrees(m["dir"])
                    img = pygame.transform.rotate(self._missile_img, deg)
                    rect = img.get_rect(center=(int(sx), int(sy)))
                    surf.blit(img, rect)
                else:
                    ang = m["dir"]; ca, sa = math.cos(ang), math.sin(ang)
                    pts = [(sx + ca * 10, sy + sa * 10),
                           (sx - ca * 8 - sa * 5, sy - sa * 8 + ca * 5),
                           (sx - ca * 8 + sa * 5, sy - sa * 8 - ca * 5)]
                    pygame.draw.polygon(surf, (230, 240, 255, 220), [(int(x), int(y)) for x, y in pts])
            screen.blit(surf, (0, 0))

        # 링 FX (폭발 등)
        if self._rings:
            surf = pygame.Surface((sw, sh), pygame.SRCALPHA)
            for r in self._rings:
                rx, ry = r["x"], r["y"]
                sx, sy = self._world_to_screen(rx, ry)
                life = r["until_ms"] - now
                if life <= 0: continue
                t = 1.0 - life / self.EXPLOSION_RING_MS
                rad = int(32 + 40 * t)
                a = int(220 * (1.0 - t))
                pygame.draw.circle(surf, (255, 230, 180, a), (int(sx), int(sy)), rad, width=2)
            screen.blit(surf, (0, 0))

    # 유틸 렌더
    def _draw_text(self, surf, text, pos, color):
        try:
            font = pygame.font.Font(os.path.join(config.ASSET_DIR, "Font", "SUIT-Bold.ttf"), 14)
        except Exception:
            font = pygame.font.SysFont(None, 14)
        img = font.render(text, True, color[:3])
        surf.blit(img, pos)

    def _dotted_line(self, surf, a, b, color, seg_len=8, gap_len=5):
        ax, ay = a; bx, by = b
        dx, dy = bx - ax, by - ay
        L = math.hypot(dx, dy)
        if L < 1e-3: return
        ux, uy = dx / L, dy / L
        t = 0.0
        while t < L:
            l = min(seg_len, L - t)
            x1, y1 = ax + ux * t, ay + uy * t
            x2, y2 = ax + ux * (t + l), ay + uy * (t + l)
            pygame.draw.line(surf, color, (int(x1), int(y1)), (int(x2), int(y2)), 2)
            t += seg_len + gap_len

class Gun32(WeaponBase):
    TIER = 4

    PELLETS = 18
    PELLET_DAMAGE = 15
    PELLET_SPREAD_DEG = 28
    PELLET_RANGE = int(720 * config.PLAYER_VIEW_SCALE)
    PELLET_HIT_RADIUS = 6
    PELLET_SPEED = 21.0
    PELLET_PIERCE = 1
    PELLET_SPLASH_RADIUS = 26
    PELLET_SPLASH_FACTOR = 0.40

    LEFT_COOLDOWN_MS = 550
    LEFT_AMMO_COST = 25

    SLUGS_PER_BURST = 3
    SLUG_DAMAGE = 70
    SLUG_SPREAD_DEG = 1.5
    SLUG_RANGE = int(1500 * config.PLAYER_VIEW_SCALE)
    SLUG_HIT_RADIUS = 8
    SLUG_SPEED = 28.0
    SLUG_PIERCE = 2
    SLUG_SPLASH_RADIUS = 34
    SLUG_SPLASH_FACTOR = 0.35

    RIGHT_COOLDOWN_MS = 800
    RIGHT_AMMO_COST = 30
    BURST_INTERVAL_MS = 85

    RING_MS = 100

    @staticmethod
    def create_instance(weapon_assets, sounds, ammo_gauge, consume_ammo, get_player_world_position):
        return Gun32(
            name="오메가 쇼트건",
            front_image=weapon_assets["gun32"]["front"],
            topdown_image=weapon_assets["gun32"]["topdown"],
            uses_bullets=True, bullet_images=weapon_assets["gun32"]["bullets"],
            uses_cartridges=False, cartridge_images=weapon_assets["gun32"]["cartridges"],
            can_left_click=True, can_right_click=True,
            left_click_ammo_cost=0, right_click_ammo_cost=0,
            tier=Gun32.TIER,
            sounds_dict={
                "fire": sounds.get("gun32_fire"),
            },
            get_ammo_gauge_fn=ammo_gauge, reduce_ammo_fn=consume_ammo,
            bullet_has_trail=False,
            get_player_world_position_fn=get_player_world_position,
            exclusive_inputs=True
        )

    def __init__(self, name, front_image, topdown_image, **kwargs):
        super().__init__(name, front_image, topdown_image, **kwargs)
        self.distance_from_center = 48 * config.PLAYER_VIEW_SCALE
        self.recoil_strength = 8
        self.speed_penalty = 0.15

        self._next_left_ms = 0
        self._next_right_ms = 0

        self._burst_active = False
        self._burst_fired = 0
        self._burst_next_ms = 0

        self._shots = []
        self._rings = []

        self._prev_left = False
        self._prev_right = False

        self._bullet_img_raw = self.bullet_images[0] if (self.bullet_images and self.bullet_images[0]) else None
        self._bullet_img_cache = {}

    # 유틸
    def _now(self): return pygame.time.get_ticks()

    def _world_to_screen(self, wx, wy):
        cx, cy = config.player_rect.centerx, config.player_rect.centery
        px, py = self.get_player_world_position()
        return (cx + (wx - px), cy + (wy - py))

    def _unit_from_mouse(self):
        mx, my = pygame.mouse.get_pos()
        dx = mx - config.player_rect.centerx
        dy = my - config.player_rect.centery
        ang = math.atan2(dy, dx)
        return (math.cos(ang), math.sin(ang)), ang

    def _enemies(self):
        return getattr(config, "all_enemies", getattr(config, "enemies", []))

    def _play_fire(self):
        s = self.sounds.get("fire")
        if s:
            try: s.play()
            except Exception: pass

    def _fire_kick(self, strength=8, timer=10):
        # 화면 흔들림 + 반동 트리거
        now = self._now()
        self.last_shot_time = now
        try:
            config.shake_strength = max(getattr(config, "shake_strength", 0), strength)
            config.shake_timer = max(getattr(config, "shake_timer", 0), timer)
        except Exception:
            pass

    # 가능한 범용 '벽 충돌' 확인 (프로젝트 환경에 따라 존재 유무 다름)
    def _is_solid(self, x, y):
        try:
            if hasattr(config, "is_solid_at"):
                return bool(config.is_solid_at(int(x), int(y)))
        except Exception:
            pass
        try:
            import collider
            if hasattr(collider, "point_blocked"):
                return bool(collider.point_blocked(int(x), int(y)))
        except Exception:
            pass
        return False

    def _damage_enemy(self, e, dmg):
        try:
            if hasattr(e, "hit"):
                e.hit(dmg, None)
            elif hasattr(e, "on_hit"):
                e.on_hit(dmg, knockback=0, hit_type="bullet")
            else:
                e.hp = getattr(e, "hp", 0) - dmg
                if e.hp <= 0:
                    e.alive = False
        except Exception:
            pass

    # 입력/업데이트
    def on_update(self, mouse_left_down, mouse_right_down):
        now = self._now()

        # 버스트(우클릭) 진행
        if self._burst_active and now >= self._burst_next_ms:
            if self._burst_fired < self.SLUGS_PER_BURST:
                self._spawn_slug()
                self._burst_fired += 1
                self._burst_next_ms = now + self.BURST_INTERVAL_MS
                self._play_fire()
                self._fire_kick(strength=9, timer=12)
            if self._burst_fired >= self.SLUGS_PER_BURST:
                self._burst_active = False

        block_left = self._burst_active or mouse_right_down
        block_right_start = mouse_left_down

        # 좌클릭: 홀드 자동 연사
        if (mouse_left_down and not block_left and now >= self._next_left_ms):
            if self.get_ammo_gauge() >= self.LEFT_AMMO_COST:
                self.reduce_ammo(self.LEFT_AMMO_COST)
                self._spawn_pellet_salvo()
                self._play_fire()
                self._fire_kick(strength=8, timer=10)
                self._next_left_ms = now + self.LEFT_COOLDOWN_MS

        # 우클릭: 홀드 시 쿨타임마다 버스트 시작(버스트 중복 방지)
        if (mouse_right_down and not self._burst_active and not block_right_start and now >= self._next_right_ms):
            if self.get_ammo_gauge() >= self.RIGHT_AMMO_COST:
                self.reduce_ammo(self.RIGHT_AMMO_COST)
                self._burst_active = True
                self._burst_fired = 0
                self._burst_next_ms = now  # 즉시 첫 발
                self._next_right_ms = now + self.RIGHT_COOLDOWN_MS

        self._prev_left = mouse_left_down
        self._prev_right = mouse_right_down

        # 탄환 갱신
        self._update_shots()

        # FX 정리
        self._rings[:] = [r for r in self._rings if now <= r["until_ms"]]

    # 발사
    def _spawn_pellet_salvo(self):
        (ux, uy), ang = self._unit_from_mouse()
        px, py = self.get_player_world_position()

        for i in range(self.PELLETS):
            spread_deg = (random.random() * 2 - 1) * self.PELLET_SPREAD_DEG
            a = ang + math.radians(spread_deg)
            self._shots.append({
                "type": "pellet",
                "x": px, "y": py,
                "dir": a, "spd": self.PELLET_SPEED,
                "dist": 0.0, "max": self.PELLET_RANGE,
                "pierce": self.PELLET_PIERCE,
                "visited": set(),
                "hit_r": self.PELLET_HIT_RADIUS,
                "dmg": self.PELLET_DAMAGE,
                "splash_r": self.PELLET_SPLASH_RADIUS,
                "splash_d": max(1, int(self.PELLET_DAMAGE * self.PELLET_SPLASH_FACTOR)),
            })

    def _spawn_slug(self):
        (ux, uy), ang = self._unit_from_mouse()
        px, py = self.get_player_world_position()

        spread_deg = (random.random() * 2 - 1) * self.SLUG_SPREAD_DEG
        a = ang + math.radians(spread_deg)
        self._shots.append({
            "type": "slug",
            "x": px, "y": py,
            "dir": a, "spd": self.SLUG_SPEED,
            "dist": 0.0, "max": self.SLUG_RANGE,
            "pierce": self.SLUG_PIERCE,
            "visited": set(),
            "hit_r": self.SLUG_HIT_RADIUS,
            "dmg": self.SLUG_DAMAGE,
            "splash_r": self.SLUG_SPLASH_RADIUS,
            "splash_d": max(1, int(self.SLUG_DAMAGE * self.SLUG_SPLASH_FACTOR)),
        })

    # 탄환/충돌
    def _update_shots(self):
        enemies = list(self._enemies())

        for i in reversed(range(len(self._shots))):
            b = self._shots[i]
            # 이동
            vx, vy = math.cos(b["dir"]) * b["spd"], math.sin(b["dir"]) * b["spd"]
            b["x"] += vx
            b["y"] += vy
            b["dist"] += abs(vx) + abs(vy)

            # 맵/장애물 충돌 → 소멸 (미니 폭발 없음)
            if self._is_solid(b["x"], b["y"]):
                self._shots.pop(i)
                continue

            # 사거리 초과
            if b["dist"] >= b["max"]:
                self._shots.pop(i)
                continue

            # 적 충돌
            hit_enemy = None
            for e in enemies:
                if not getattr(e, "alive", False): continue
                if id(e) in b["visited"]: continue
                ex = getattr(e, "world_x", getattr(e, "x", None))
                ey = getattr(e, "world_y", getattr(e, "y", None))
                if ex is None or ey is None: continue
                rad = int(getattr(e, "radius", 26))
                if math.hypot(ex - b["x"], ey - b["y"]) <= (rad + b["hit_r"]):
                    hit_enemy = e
                    break

            if hit_enemy:
                # 주 데미지
                self._damage_enemy(hit_enemy, b["dmg"])
                b["visited"].add(id(hit_enemy))

                # 미니 폭발(주 대상 제외하고 스플래시)
                if b["splash_r"] > 0 and b["splash_d"] > 0:
                    r2 = b["splash_r"] * b["splash_r"]
                    for e in enemies:
                        if e is hit_enemy or not getattr(e, "alive", False): continue
                        ex = getattr(e, "world_x", getattr(e, "x", None))
                        ey = getattr(e, "world_y", getattr(e, "y", None))
                        if ex is None or ey is None: continue
                        if (ex - b["x"]) * (ex - b["x"]) + (ey - b["y"]) * (ey - b["y"]) <= r2:
                            self._damage_enemy(e, b["splash_d"])

                    # 링 FX
                    self._rings.append({"x": b["x"], "y": b["y"], "until_ms": self._now() + self.RING_MS})

                # 관통 소비
                if b["pierce"] > 0:
                    b["pierce"] -= 1
                else:
                    self._shots.pop(i)
                    continue

    # 렌더
    def draw_overlay(self, screen):
        sw, sh = screen.get_size()
        now = self._now()

        # 탄 시각화: bullet1 사용(회전 블릿)
        if self._shots:
            layer = pygame.Surface((sw, sh), pygame.SRCALPHA)
            for b in self._shots:
                sx, sy = self._world_to_screen(b["x"], b["y"])
                if self._bullet_img_raw:
                    # 각도 정수화해서 캐시 사용(부하 완화)
                    deg = int(-math.degrees(b["dir"])) % 360
                    img = self._bullet_img_cache.get(deg)
                    if img is None:
                        img = pygame.transform.rotate(self._bullet_img_raw, deg)
                        self._bullet_img_cache[deg] = img
                    rect = img.get_rect(center=(int(sx), int(sy)))
                    layer.blit(img, rect)
                else:
                    # 폴백: 점
                    r = 3 if b["type"] == "pellet" else 4
                    pygame.draw.circle(layer, (255, 245, 220, 230), (int(sx), int(sy)), r)
            screen.blit(layer, (0, 0))

        # 미니 폭발 링
        if self._rings:
            layer = pygame.Surface((sw, sh), pygame.SRCALPHA)
            for r in self._rings:
                if now > r["until_ms"]: continue
                life = r["until_ms"] - now
                t = 1.0 - life / self.RING_MS
                rad = int(12 + 10 * t)
                alpha = int(220 * (1.0 - t))
                sx, sy = self._world_to_screen(r["x"], r["y"])
                pygame.draw.circle(layer, (255, 230, 180, alpha), (int(sx), int(sy)), rad, width=2)
            screen.blit(layer, (0, 0))

class Gun33(WeaponBase):
    TIER = 4

    LEFT_DAMAGE = 55
    RIGHT_DAMAGE = 70
    LEFT_COOLDOWN_MS = 190
    RIGHT_COOLDOWN_MS = 350
    LEFT_AMMO_COST = 10
    RIGHT_AMMO_COST = 15

    LEFT_SPEED = 22.0
    RIGHT_SPEED = 16.0
    LEFT_RANGE = int(3600 * config.PLAYER_VIEW_SCALE)
    RIGHT_RANGE = int(5000 * config.PLAYER_VIEW_SCALE)
    LEFT_HIT_RADIUS = 8
    RIGHT_HIT_RADIUS = 10

    @staticmethod
    def create_instance(weapon_assets, sounds, ammo_gauge, consume_ammo, get_player_world_position):
        return Gun33(
            name="리코셰 카빈",
            front_image=weapon_assets.get("gun33", {}).get("front"),
            topdown_image=weapon_assets.get("gun33", {}).get("topdown"),
            uses_bullets=False, bullet_images=[],
            uses_cartridges=False, cartridge_images=[],
            can_left_click=True, can_right_click=True,
            left_click_ammo_cost=0, right_click_ammo_cost=0,
            tier=Gun33.TIER,
            sounds_dict={
                "fire": sounds.get("gun33_fire"),
            },
            get_ammo_gauge_fn=ammo_gauge, reduce_ammo_fn=consume_ammo,
            bullet_has_trail=False,
            get_player_world_position_fn=get_player_world_position,
            exclusive_inputs=True
        )

    def __init__(self, name, front_image, topdown_image, **kwargs):
        super().__init__(name, front_image, topdown_image, **kwargs)
        self.distance_from_center = 46 * config.PLAYER_VIEW_SCALE
        self.recoil_strength = 7
        self.speed_penalty = 0.1

        self._next_left_ms = 0
        self._next_right_ms = 0

        self._shots = []
        self._rings = []

        self._prev_left = False
        self._prev_right = False

        self._bubble_palette = [
            ((255, 140, 200, 235), (255, 170, 220, 200)),
            ((140, 200, 255, 235), (170, 220, 255, 200)),
            ((180, 160, 255, 235), (210, 190, 255, 200)),
            ((160, 255, 200, 235), (190, 255, 220, 200)),
            ((255, 190, 140, 235), (255, 210, 170, 200)),
            ((255, 150, 220, 235), (255, 200, 240, 200)),
        ]
        self._bubble_styles = []
        for oc, ic in self._bubble_palette:
            surf = self._make_bubble_surface(20, oc, ic)
            ring_col = (min(255, ic[0]), min(255, ic[1]), min(255, ic[2]))
            self._bubble_styles.append({"surf": surf, "ring_col": ring_col})

    # 공통 유틸
    def _now(self): 
        return pygame.time.get_ticks()

    def _world_to_screen(self, wx, wy):
        cx, cy = config.player_rect.centerx, config.player_rect.centery
        px, py = self.get_player_world_position()
        return (cx + (wx - px), cy + (wy - py))

    def _unit_from_mouse(self):
        mx, my = pygame.mouse.get_pos()
        dx = mx - config.player_rect.centerx
        dy = my - config.player_rect.centery
        ang = math.atan2(dy, dx)
        return (math.cos(ang), math.sin(ang)), ang

    def _enemies(self):
        return getattr(config, "all_enemies", getattr(config, "enemies", []))

    def _fire_kick(self, strength=8, timer=10):
        now = self._now()
        self.last_shot_time = now
        try:
            config.shake_strength = max(getattr(config, "shake_strength", 0), strength)
            config.shake_timer   = max(getattr(config, "shake_timer", 0),   timer)
        except Exception:
            pass

    def _damage_enemy(self, e, dmg):
        try:
            if hasattr(e, "hit"):
                e.hit(dmg, None)
            elif hasattr(e, "on_hit"):
                e.on_hit(dmg, knockback=0, hit_type="bullet")
            else:
                e.hp = getattr(e, "hp", 0) - dmg
                if e.hp <= 0:
                    e.alive = False
        except Exception:
            pass

    def _make_bubble_surface(self, r, outer_rgba, inner_rgba):
        s = pygame.Surface((r*2, r*2), pygame.SRCALPHA)
        center = (r, r)
        pygame.draw.circle(s, outer_rgba, center, r)
        pygame.draw.circle(s, inner_rgba, center, int(r*0.78))
        pygame.draw.circle(s, (255, 255, 255, 160), (int(r*1.25), int(r*0.80)), int(r*0.35))
        return s

    def _all_obstacles(self):
        om = getattr(config, "obstacle_manager", None)
        if not om: 
            return []
        # 시작방 포함: placed + static + combat
        return list(getattr(om, "placed_obstacles", [])) + \
               list(getattr(om, "static_obstacles", [])) + \
               list(getattr(om, "combat_obstacles", []))

    def _enemy_radius(self, e):
        return max(10, int(getattr(e, "radius", 28) * 0.9))

    def _reflect(self, vx, vy, nx, ny):
        dot = vx*nx + vy*ny
        return vx - 2*dot*nx, vy - 2*dot*ny

    def _spawn_ring(self, x, y, color=(255,230,245), ms=140):
        self._rings.append({"x": x, "y": y, "color": color, "until_ms": self._now() + ms})

    # 메인 루프
    def on_update(self, mouse_left_down, mouse_right_down):
        now = self._now()
        self._update_shots()

        ldown, rdown = self._filter_inputs(mouse_left_down, mouse_right_down)

        if ldown and now >= self._next_left_ms:
            if self.get_ammo_gauge() >= self.LEFT_AMMO_COST:
                self.reduce_ammo(self.LEFT_AMMO_COST)
                self._fire(shoot_right=False)
                self._next_left_ms = now + self.LEFT_COOLDOWN_MS

        if rdown and now >= self._next_right_ms:
            if self.get_ammo_gauge() >= self.RIGHT_AMMO_COST:
                self.reduce_ammo(self.RIGHT_AMMO_COST)
                self._fire(shoot_right=True)
                self._next_right_ms = now + self.RIGHT_COOLDOWN_MS

        self._prev_left = ldown
        self._prev_right = rdown

    def _fire(self, shoot_right=False):
        now = self._now()
        (ux, uy), _ = self._unit_from_mouse()
        px, py = self.get_player_world_position()
        sx = px + ux * (30 * config.PLAYER_VIEW_SCALE)
        sy = py + uy * (30 * config.PLAYER_VIEW_SCALE)

        if shoot_right:
            dmg, spd, rng, hr, shake = self.RIGHT_DAMAGE, self.RIGHT_SPEED, self.RIGHT_RANGE, self.RIGHT_HIT_RADIUS, 12
        else:
            dmg, spd, rng, hr, shake = self.LEFT_DAMAGE, self.LEFT_SPEED, self.LEFT_RANGE, self.LEFT_HIT_RADIUS, 9

        style = random.choice(self._bubble_styles)
        vx, vy = ux * spd, uy * spd

        self._shots.append({
            "x": sx, "y": sy, "vx": vx, "vy": vy, "spd": spd,
            "damage": dmg, "range": rng, "hit_r": hr,
            "dist": 0.0, "born": now, "phase": random.random()*math.tau,
            "surf": style["surf"], "ring_col": style["ring_col"]
        })

        s = self.sounds.get("fire")
        if s:
            try: s.play()
            except Exception: pass
        self._fire_kick(strength=shake, timer=10)

    def _update_shots(self):
        enemies = list(self._enemies())
        obstacles = self._all_obstacles()

        for i in reversed(range(len(self._shots))):
            b = self._shots[i]

            # 프레임 이동량(속도)와 CCD용 분할 이동
            move_len = math.hypot(b["vx"], b["vy"])
            if move_len <= 0.0:
                continue

            remaining = move_len
            # 한 번에 이동하는 최대 길이(작을수록 충돌 누락 줄어듦)
            max_step = max(4.0, b["hit_r"] * 0.6)

            removed = False
            while remaining > 0.0:
                step = remaining if remaining < max_step else max_step
                ux = b["vx"] / move_len
                uy = b["vy"] / move_len

                # 위치 이동 + 누적 거리
                b["x"] += ux * step
                b["y"] += uy * step
                b["dist"] += step

                # 사거리 초과 -> 제거
                if b["dist"] >= b["range"]:
                    self._shots.pop(i)
                    removed = True
                    break

                # 적 피격
                hit_enemy = None
                for e in enemies:
                    if not getattr(e, "alive", False):
                        continue
                    ex = getattr(e, "world_x", getattr(e, "x", None))
                    ey = getattr(e, "world_y", getattr(e, "y", None))
                    if ex is None or ey is None:
                        continue
                    rr = self._enemy_radius(e) + b["hit_r"]
                    if (b["x"]-ex)**2 + (b["y"]-ey)**2 <= rr*rr:
                        hit_enemy = e
                        break
                if hit_enemy:
                    self._damage_enemy(hit_enemy, b["damage"])
                    self._spawn_ring(b["x"], b["y"], color=b["ring_col"], ms=160)
                    self._shots.pop(i)
                    removed = True
                    break

                # 장애물 충돌 → 반사(횟수 제한 없음)
                collided = False
                for obs in obstacles:
                    for c in getattr(obs, "colliders", []):
                        if getattr(c, "bullet_passable", False):
                            continue
                        pen = c.compute_penetration_circle(
                            (b["x"], b["y"]), b["hit_r"], (obs.world_x, obs.world_y)
                        )
                        if not pen:
                            continue

                        px, py = pen
                        nlen = math.hypot(px, py)
                        nx, ny = (0.0, -1.0) if nlen == 0 else (px/nlen, py/nlen)

                        # 충돌면에서 살짝 분리(끼임 방지)
                        b["x"] += nx * (abs(nlen) + 0.8)
                        b["y"] += ny * (abs(nlen) + 0.8)

                        # 반사
                        b["vx"], b["vy"] = self._reflect(b["vx"], b["vy"], nx, ny)
                        vmag = math.hypot(b["vx"], b["vy"]) or 1.0
                        # 속도 크기 유지
                        b["vx"], b["vy"] = (b["vx"]/vmag)*b["spd"], (b["vy"]/vmag)*b["spd"]

                        # 링 + 소리(볼륨 30%)
                        self._spawn_ring(b["x"], b["y"], color=b["ring_col"], ms=120)
                        s = self.sounds.get("fire")
                        if s:
                            try:
                                ch = s.play()
                                if ch: ch.set_volume(0.3)  # 리코셰는 30%
                            except Exception:
                                pass
                        collided = True
                        break
                    if collided:
                        break

                # 다음 분할 이동
                remaining -= step

            if removed:
                continue

    def draw_overlay(self, screen):
        sw, sh = screen.get_size()
        now = self._now()

        # 버블탄 (스쿼시&스트레치 + 진행방향 회전)
        if self._shots:
            layer = pygame.Surface((sw, sh), pygame.SRCALPHA)
            for b in self._shots:
                sx, sy = self._world_to_screen(b["x"], b["y"])
                age = (now - b["born"]) * 0.001
                wobble = 0.22*math.sin(8.0*age + b["phase"])
                sx_scale = max(0.75, 1.0 + wobble + random.uniform(-0.03, 0.03))
                sy_scale = max(0.65, 1.0 / sx_scale)
                base = b["surf"]
                w = max(12, int(base.get_width() * sx_scale))
                h = max(12, int(base.get_height() * sy_scale))
                deformed = pygame.transform.smoothscale(base, (w, h))
                ang_deg = math.degrees(math.atan2(b["vy"], b["vx"]))
                img = pygame.transform.rotate(deformed, -ang_deg)
                rect = img.get_rect(center=(int(sx), int(sy)))
                layer.blit(img, rect)
                # 아주 짧은 잔광 점
                pygame.draw.circle(layer, (255, 200, 230, 90), (int(sx), int(sy)), 2)
            screen.blit(layer, (0, 0))

        # 반짝 링 이펙트(만료 정리)
        if self._rings:
            layer2 = pygame.Surface((sw, sh), pygame.SRCALPHA)
            alive = []
            for r in self._rings:
                if now > r["until_ms"]:
                    continue
                t = 1.0 - (r["until_ms"] - now) / 140.0
                rad = int(8 + 12 * t)
                alpha = int(220 * (1.0 - t))
                rx, ry = self._world_to_screen(r["x"], r["y"])
                col = (*r["color"][:3], alpha)
                pygame.draw.circle(layer2, col, (int(rx), int(ry)), rad, width=2)
                alive.append(r)
            screen.blit(layer2, (0, 0))
            self._rings = alive

class Gun34(WeaponBase):
    TIER = 4

    PELLETS = 12
    PELLET_DAMAGE = 14
    PELLET_SPREAD_DEG = 30
    PELLET_RANGE = int(440 * config.PLAYER_VIEW_SCALE)
    PELLET_HIT_RADIUS = int(6 * config.PLAYER_VIEW_SCALE)
    PELLET_SPEED = 19.0
    PELLET_PIERCE = 0

    LEFT_COOLDOWN_MS = 600
    LEFT_AMMO_COST = 18

    CONE_DAMAGE = 60
    CONE_ARC_DEG = 60
    CONE_RANGE = int(400 * config.PLAYER_VIEW_SCALE)
    RIGHT_COOLDOWN_MS = 900
    RIGHT_AMMO_COST = 30

    SLOW_DURATION_MS = 1500
    VULN_DURATION_MS = 2000
    VULN_BONUS = 0.20

    RING_MS = 120
    CONE_FLASH_MS = 120
    SHARD_LIFETIME_MS = 220
    SWEEP_MS = 140

    @staticmethod
    def create_instance(weapon_assets, sounds, ammo_gauge, consume_ammo, get_player_world_position):
        a = weapon_assets.get("gun34", {})
        front = a.get("front")
        top   = a.get("topdown")
        bullets = a.get("bullets") or []
        if not bullets:
            for _, wa in weapon_assets.items():
                if isinstance(wa, dict) and wa.get("bullets"):
                    bullets = wa["bullets"]; break

        return Gun34(
            name="크라이오 거스트 샷건",
            front_image=front, topdown_image=top,
            uses_bullets=True, bullet_images=bullets,
            uses_cartridges=True,  cartridge_images=weapon_assets.get("gun34", {}).get("cartridges", []),
            can_left_click=True, can_right_click=True,
            left_click_ammo_cost=0, right_click_ammo_cost=0,
            tier=Gun34.TIER,
            sounds_dict={
                "leftfire":  sounds.get("gun34_leftfire"),
                "rightfire": sounds.get("gun34_rightfire"),
            },
            get_ammo_gauge_fn=ammo_gauge, reduce_ammo_fn=consume_ammo,
            bullet_has_trail=False,
            get_player_world_position_fn=get_player_world_position,
            exclusive_inputs=True
        )

    def __init__(self, name, front_image, topdown_image, **kwargs):
        super().__init__(name, front_image, topdown_image, **kwargs)
        self.distance_from_center = 48 * config.PLAYER_VIEW_SCALE
        self.recoil_strength = 10
        self.speed_penalty = 0.1

        self._next_left_ms = 0
        self._next_right_ms = 0

        self._pellets = []
        self._rings = []
        self._bullet_img_raw = self.bullet_images[0] if (self.bullet_images and self.bullet_images[0]) else None
        self._bullet_img_cache = {}

        self._cone_fx = None
        self._cone_sweeps = []
        self._cone_shards = []

    # 공통 유틸
    def _now(self): return pygame.time.get_ticks()

    def _world_to_screen(self, wx, wy):
        cx, cy = config.player_rect.centerx, config.player_rect.centery
        px, py = self.get_player_world_position()
        return (cx + (wx - px), cy + (wy - py))

    def _unit_from_mouse(self):
        mx, my = pygame.mouse.get_pos()
        dx = mx - config.player_rect.centerx
        dy = my - config.player_rect.centery
        ang = math.atan2(dy, dx)
        return (math.cos(ang), math.sin(ang)), ang

    def _enemies(self):
        return getattr(config, "all_enemies", getattr(config, "enemies", []))

    def _play(self, key):
        s = self.sounds.get(key)
        if s:
            try: s.play()
            except Exception: pass

    def _fire_kick(self, strength=8, timer=10):
        # 발사 시 반동 + 화면 흔들림 트리거
        now = self._now()
        self.last_shot_time = now
        try:
            config.shake_strength = max(getattr(config, "shake_strength", 0), strength)
            config.shake_timer   = max(getattr(config, "shake_timer", 0),   timer)
        except Exception:
            pass

    def _is_solid(self, x, y):
        # 간단 벽 충돌(환경별 훅 사용)
        try:
            if hasattr(config, "is_solid_at"):
                return bool(config.is_solid_at(int(x), int(y)))
        except Exception:
            pass
        try:
            import collider
            if hasattr(collider, "point_blocked"):
                return bool(collider.point_blocked(int(x), int(y)))
        except Exception:
            pass
        return False

    def _damage_enemy(self, e, dmg, hit_type="bullet", knockback=0):
        # 취약 보정(+20%)은 이 무기에서만 적용
        now = self._now()
        if getattr(e, "_cryo_vulnerable_until", 0) > now:
            dmg = int(round(dmg * (1.0 + self.VULN_BONUS)))
        try:
            if hasattr(e, "on_hit"):
                e.on_hit(dmg, knockback=knockback, hit_type=hit_type)
            elif hasattr(e, "hit"):
                e.hit(dmg, None)
            else:
                e.hp = getattr(e, "hp", 0) - dmg
                if e.hp <= 0: e.alive = False
        except Exception:
            pass

    # 입력 처리/업데이트
    def on_update(self, left_down, right_down):
        now = self._now()
        l_allow, r_allow = self._filter_inputs(left_down, right_down)

        # 좌클릭(산탄)
        if l_allow and now >= self._next_left_ms:
            if self.get_ammo_gauge() >= self.LEFT_AMMO_COST:
                self.reduce_ammo(self.LEFT_AMMO_COST)
                self._spawn_pellet_salvo()
                self._play("leftfire")
                self._fire_kick(strength=17, timer=10)
                self._next_left_ms = now + self.LEFT_COOLDOWN_MS

        # 우클릭(빙결 콘)
        if r_allow and now >= self._next_right_ms:
            if self.get_ammo_gauge() >= self.RIGHT_AMMO_COST:
                self.reduce_ammo(self.RIGHT_AMMO_COST)
                self._cast_ice_cone()
                self._play("rightfire")
                self._fire_kick(strength=11, timer=12)
                self._next_right_ms = now + self.RIGHT_COOLDOWN_MS

        # 산탄 이동/충돌
        self._update_pellets()

        # 콘 스윕/파편 갱신
        self._update_sweep_and_shards()

        # 링 FX 만료 정리
        self._rings[:] = [r for r in self._rings if now <= r["until_ms"]]

    # 좌클릭: 산탄
    def _spawn_pellet_salvo(self):
        (ux, uy), ang = self._unit_from_mouse()
        px, py = self.get_player_world_position()
        muzzle_x = px + ux * (30 * config.PLAYER_VIEW_SCALE)
        muzzle_y = py + uy * (30 * config.PLAYER_VIEW_SCALE)

        half = math.radians(self.PELLET_SPREAD_DEG * 0.5)
        for _ in range(self.PELLETS):
            d = random.uniform(-half, half)
            dir_ang = ang + d
            vx, vy = math.cos(dir_ang), math.sin(dir_ang)
            self._pellets.append({
                "x": muzzle_x, "y": muzzle_y,
                "dir": dir_ang, "vx": vx, "vy": vy,
                "spd": self.PELLET_SPEED, "dmg": self.PELLET_DAMAGE,
                "dist": 0.0, "max": self.PELLET_RANGE,
                "pierce": self.PELLET_PIERCE
            })

        # 사출 링
        self._rings.append({
            "x": muzzle_x, "y": muzzle_y,
            "radius": 14 * config.PLAYER_VIEW_SCALE,
            "until_ms": self._now() + self.RING_MS
        })

        # 샷건 탄피 배출
        if self.uses_cartridges and self.cartridge_images:
            eject_angle = ang + math.radians(90 + random.uniform(-15, 15))
            evx = math.cos(eject_angle) * 1.2
            evy = math.sin(eject_angle) * 1.2
            try:
                scatter = ScatteredBullet(px, py, evx, evy, self.cartridge_images[0])
                config.scattered_bullets.append(scatter)
            except Exception:
                pass

    def _update_pellets(self):
        if not self._pellets: return

        enemies = list(self._enemies())
        i = 0
        while i < len(self._pellets):
            b = self._pellets[i]
            moved = 0.0; hit_end = False
            # 터널링 방지: 짧은 스텝으로 분할 이동
            while moved < b["spd"]:
                step = min(3.5, b["spd"] - moved)
                b["x"] += b["vx"] * step
                b["y"] += b["vy"] * step
                b["dist"] += step
                moved += step

                # 사거리 종료
                if b["dist"] >= b["max"]:
                    hit_end = True; break

                # 벽 충돌
                if self._is_solid(b["x"], b["y"]):
                    hit_end = True; break

                # 적 충돌
                hit_enemy = None
                for e in enemies:
                    if not getattr(e, "alive", False): continue
                    ex = getattr(e, "world_x", getattr(e, "x", None))
                    ey = getattr(e, "world_y", getattr(e, "y", None))
                    if ex is None or ey is None: continue
                    rr = getattr(e, "radius", 16) + self.PELLET_HIT_RADIUS
                    if (ex - b["x"])**2 + (ey - b["y"])**2 <= rr*rr:
                        hit_enemy = e; break

                if hit_enemy:
                    now = self._now()
                    # 슬로우 1.5s (호환 속성 부여)
                    try:
                        hit_enemy._cryo_slow_until  = max(getattr(hit_enemy, "_cryo_slow_until", 0), now + self.SLOW_DURATION_MS)
                        hit_enemy._cryo_slow_factor = 0.6
                    except Exception:
                        pass
                    # 피해(취약 보정 포함)
                    self._damage_enemy(hit_enemy, b["dmg"], hit_type="pellet", knockback=2)
                    # 관통 처리
                    b["pierce"] -= 1
                    if b["pierce"] < 0:
                        hit_end = True

                if hit_end: break

            if hit_end:
                self._pellets.pop(i)
            else:
                i += 1

    # 우클릭: 빙결 콘(강화 연출)
    def _cast_ice_cone(self):
        now = self._now()
        (ux, uy), ang = self._unit_from_mouse()
        px, py = self.get_player_world_position()

        half = math.radians(self.CONE_ARC_DEG * 0.5)
        hit_any = False

        # 즉발 부채꼴 판정
        for e in self._enemies():
            if not getattr(e, "alive", False): continue
            ex = getattr(e, "world_x", getattr(e, "x", None))
            ey = getattr(e, "world_y", getattr(e, "y", None))
            if ex is None or ey is None: continue
            dx, dy = ex - px, ey - py
            dist = math.hypot(dx, dy)
            if dist > self.CONE_RANGE + getattr(e, "radius", 16): continue
            dang = (math.atan2(dy, dx) - ang + math.pi) % (2*math.pi) - math.pi
            if abs(dang) <= half:
                try:
                    e._cryo_vulnerable_until = max(getattr(e, "_cryo_vulnerable_until", 0), now + self.VULN_DURATION_MS)
                except Exception:
                    pass
                # 즉발 피해
                self._damage_enemy(e, self.CONE_DAMAGE, hit_type="cryo_cone", knockback=3)
                hit_any = True

        # 콘 베이스 플래시
        self._cone_fx = {"until": now + self.CONE_FLASH_MS, "ang": ang, "px": px, "py": py, "start": now}

        # 스윕 라인 2~3개 생성(좌->우, 우->좌 랜덤)
        sweep_count = random.randint(2, 3)
        self._cone_sweeps.clear()
        for _ in range(sweep_count):
            self._cone_sweeps.append({"start": now, "dir": random.choice([-1, 1])})

        # 설편 파티클 생성(콘 안쪽으로 흩날림)
        shards = 26
        for _ in range(shards):
            a = ang + random.uniform(-half*0.9, half*0.9)
            spd = random.uniform(6.0, 10.5)
            self._cone_shards.append({
                "x": px + ux * (26 * config.PLAYER_VIEW_SCALE),
                "y": py + uy * (26 * config.PLAYER_VIEW_SCALE),
                "vx": math.cos(a) * spd,
                "vy": math.sin(a) * spd,
                "born": now
            })

        # 사출 링
        self._rings.append({
            "x": px + ux * (28 * config.PLAYER_VIEW_SCALE),
            "y": py + uy * (28 * config.PLAYER_VIEW_SCALE),
            "radius": 16 * config.PLAYER_VIEW_SCALE,
            "until_ms": now + self.RING_MS
        })

    def _update_sweep_and_shards(self):
        now = self._now()
        # 스윕: 시간 경과에 따라 offset 0→1 이동, 수명 끝나면 제거
        alive_sweeps = []
        for s in self._cone_sweeps:
            t = (now - s["start"]) / float(self.SWEEP_MS)
            if t <= 1.0:
                s["offset"] = t * s["dir"]
                alive_sweeps.append(s)
        self._cone_sweeps = alive_sweeps

        # 설편: 직선 이동 + 수명 체크
        alive_shards = []
        for p in self._cone_shards:
            if now - p["born"] > self.SHARD_LIFETIME_MS: continue
            p["x"] += p["vx"]; p["y"] += p["vy"]
            alive_shards.append(p)
        self._cone_shards = alive_shards

    # 렌더
    def draw_overlay(self, screen):
        sw, sh = screen.get_size()
        now = self._now()

        # 산탄(bullet1) 렌더
        if self._pellets:
            layer = pygame.Surface((sw, sh), pygame.SRCALPHA)
            for b in self._pellets:
                sx, sy = self._world_to_screen(b["x"], b["y"])
                if self._bullet_img_raw:
                    deg = int(-math.degrees(b["dir"])) % 360
                    img = self._bullet_img_cache.get(deg)
                    if img is None:
                        img = pygame.transform.rotate(self._bullet_img_raw, deg)
                        self._bullet_img_cache[deg] = img
                    layer.blit(img, img.get_rect(center=(int(sx), int(sy))))
                else:
                    pygame.draw.circle(layer, (240,240,240,220), (int(sx), int(sy)), max(2, self.PELLET_HIT_RADIUS//2))
            screen.blit(layer, (0, 0))

        # 콘 베이스 플래시 + 스윕 라인 + 설편
        if self._cone_fx and now <= self._cone_fx["until"]:
            px, py, ang = self._cone_fx["px"], self._cone_fx["py"], self._cone_fx["ang"]
            cx, cy = self._world_to_screen(px, py)
            half = math.radians(self.CONE_ARC_DEG * 0.5)
            base = pygame.Surface((sw, sh), pygame.SRCALPHA)

            # 부채꼴 베이스(연한 사이언 그라데이션 느낌 두 겹)
            def fan_points(radius):
                pts = [(int(cx), int(cy))]
                steps = 18
                a0 = ang - half; a1 = ang + half
                for i in range(steps + 1):
                    aa = a0 + (a1 - a0) * (i / steps)
                    pts.append((int(cx + math.cos(aa) * radius), int(cy + math.sin(aa) * radius)))
                return pts

            alpha1 = int(90 * (self._cone_fx["until"] - now) / self.CONE_FLASH_MS)
            alpha2 = min(140, alpha1 + 40)
            pygame.draw.polygon(base, (160, 220, 255, alpha1), fan_points(self.CONE_RANGE))
            pygame.draw.polygon(base, (200, 245, 255, alpha2), fan_points(int(self.CONE_RANGE*0.85)), width=2)

            # 스윕 라인(좌↔우로 흐르는 선)
            for s in self._cone_sweeps:
                # offset(-1~1)을 각도로 매핑해서 선을 긋는다
                a = ang + half * s["offset"]
                x1 = int(cx + math.cos(a) * (self.CONE_RANGE*0.25))
                y1 = int(cy + math.sin(a) * (self.CONE_RANGE*0.25))
                x2 = int(cx + math.cos(a) * (self.CONE_RANGE*0.95))
                y2 = int(cy + math.sin(a) * (self.CONE_RANGE*0.95))
                pygame.draw.line(base, (220, 250, 255, 120), (x1, y1), (x2, y2), 2)

            screen.blit(base, (0, 0))

        # 설편 파티클(하얀 얼음알갱이들이 퍼져나감)
        if self._cone_shards:
            shard_layer = pygame.Surface((sw, sh), pygame.SRCALPHA)
            for p in self._cone_shards:
                sx, sy = self._world_to_screen(p["x"], p["y"])
                pygame.draw.circle(shard_layer, (240, 255, 255, 180), (int(sx), int(sy)), 2)
            screen.blit(shard_layer, (0, 0))

        # 링 FX
        if self._rings:
            ring = pygame.Surface((sw, sh), pygame.SRCALPHA)
            for r in self._rings:
                sx, sy = self._world_to_screen(r["x"], r["y"])
                pygame.draw.circle(ring, (200,220,255,140), (int(sx), int(sy)), int(r["radius"]), width=2)
            screen.blit(ring, (0, 0))

        # 취약(파란 필터) 오버레이: 적 머리/몸통에 푸른빛을 얹어 시각화
        enemies = list(self._enemies())
        if enemies:
            fx = pygame.Surface((sw, sh), pygame.SRCALPHA)
            for e in enemies:
                until = getattr(e, "_cryo_vulnerable_until", 0)
                if until <= now: 
                    continue
                ex = getattr(e, "world_x", getattr(e, "x", None))
                ey = getattr(e, "world_y", getattr(e, "y", None))
                if ex is None or ey is None: 
                    continue
                sx, sy = self._world_to_screen(ex, ey)
                rad = int(max(12, getattr(e, "radius", 16) * 1.25))
                # 중심부는 연한 파란 필터, 외곽은 밝은 테두리
                pygame.draw.circle(fx, (120, 200, 255, 70), (int(sx), int(sy)), rad)
                pygame.draw.circle(fx, (200, 240, 255, 140), (int(sx), int(sy)), rad, width=2)
                # 살짝의 얼음 균열 라인(2~3개)
                for _ in range(2):
                    a = random.uniform(0, math.tau)
                    r1 = int(rad*0.4); r2 = int(rad*0.9)
                    x1 = int(sx + math.cos(a)*r1); y1 = int(sy + math.sin(a)*r1)
                    x2 = int(sx + math.cos(a)*r2); y2 = int(sy + math.sin(a)*r2)
                    pygame.draw.line(fx, (180, 230, 255, 120), (x1, y1), (x2, y2), 1)
            screen.blit(fx, (0, 0))

class Gun35(WeaponBase):
    TIER = 4

    LEFT_COOLDOWN_MS = 900
    LEFT_AMMO_COST   = 35

    SHELL_SPEED      = 15.0
    SHELL_MAX_RANGE  = 450.0
    SHELL_RADIUS     = 10
    SHELL_AOE_RADIUS = 90
    SHELL_DAMAGE     = 80

    CLUSTER_COUNT        = 6
    CLUSTER_SPEED_MIN    = 8.0
    CLUSTER_SPEED_MAX    = 11.0
    CLUSTER_RADIUS       = 6
    CLUSTER_AOE_RADIUS   = 60
    CLUSTER_DAMAGE       = 40
    CLUSTER_FUSE_MIN_MS  = 0
    CLUSTER_FUSE_MAX_MS  = 360
    CLUSTER_LIFETIME_MS  = 1200

    RIGHT_COOLDOWN_MS    = 250
    RIGHT_AMMO_COST      = 0

    SLOW_DURATION_MS     = 1200
    SLOW_FACTOR          = 0.70

    EXPLOSION_RING_MS    = 140
    EXPLOSION_SHAKE_MAIN = (12, 10)
    EXPLOSION_SHAKE_CHILD= (6, 6)
    TRAIL_POINTS         = 4

    HEARING_RADIUS_MAIN  = 900.0
    HEARING_RADIUS_CHILD = 700.0
    CLUSTER_BOOM_FRAME_LIMIT = 2
    CLUSTER_BOOM_MIN_GAP_MS  = 60
    PITCH_VARIANTS        = [-0.06, -0.03, 0.0, +0.03, +0.06]

    @staticmethod
    def create_instance(weapon_assets, sounds, ammo_gauge, consume_ammo, get_player_world_position):
        wa = weapon_assets.get("gun35", {})
        bullets = wa.get("bullets") or []
        if not bullets:
            for _, ent in weapon_assets.items():
                if isinstance(ent, dict) and ent.get("bullets"):
                    bullets = ent["bullets"]; break
        front   = wa.get("front")
        topdown = wa.get("topdown")

        return Gun35(
            name="분열 유탄 발사기",
            front_image=front, topdown_image=topdown,
            uses_bullets=True, bullet_images=bullets,
            uses_cartridges=False, cartridge_images=[],
            can_left_click=True, can_right_click=True,
            left_click_ammo_cost=0, right_click_ammo_cost=0,
            tier=Gun35.TIER,
            sounds_dict={
                "fire": sounds.get("gun35_fire"),
                "boom": sounds.get("gun35_explosion"),
            },
            get_ammo_gauge_fn=ammo_gauge, reduce_ammo_fn=consume_ammo,
            bullet_has_trail=False,
            get_player_world_position_fn=get_player_world_position,
            exclusive_inputs=True
        )

    def __init__(self, name, front_image, topdown_image, **kwargs):
        super().__init__(name, front_image, topdown_image, **kwargs)
        self.distance_from_center = 54 * config.PLAYER_VIEW_SCALE
        self.recoil_strength      = 8
        self.speed_penalty        = 0.05

        self._next_left_ms  = 0
        self._next_right_ms = 0
        self._prev_left     = False
        self._prev_right    = False

        self._shells      = []
        self._clusters    = []
        self._explosions  = []
        self._sparks      = []
        self._trails      = []

        self._grenade_img = self.bullet_images[0] if (self.bullet_images and self.bullet_images[0]) else None
        self._rot_cache   = {}

        self._boom_variants = []
        self._prepare_boom_variants()
        self._last_boom_ms  = 0
        self._boom_count_this_frame = 0

        self._obstacle_manager = getattr(config, "obstacle_manager", None)

        self._arm_hint_active = False

    # 유틸
    def _now(self): return pygame.time.get_ticks()

    def _world_to_screen(self, wx, wy):
        cx, cy = config.player_rect.centerx, config.player_rect.centery
        px, py = self.get_player_world_position()
        return (cx + (wx - px), cy + (wy - py))

    def _unit_from_mouse(self):
        mx, my = pygame.mouse.get_pos()
        dx = mx - config.player_rect.centerx
        dy = my - config.player_rect.centery
        ang = math.atan2(dy, dx)
        return (math.cos(ang), math.sin(ang)), ang

    def _enemies(self):
        return getattr(config, "all_enemies", getattr(config, "enemies", []))

    def _all_obstacles(self):
        om = getattr(config, "obstacle_manager", None)
        if not om:
            return []
        return list(getattr(om, "placed_obstacles", [])) \
             + list(getattr(om, "static_obstacles", [])) \
             + list(getattr(om, "combat_obstacles", []))

    def _collides_obstacle_circle(self, x, y, r):
        # 원형 히트가 어떤 장애물 콜라이더와라도 맞닿으면 True 반환.
        for obs in self._all_obstacles():
            for c in getattr(obs, "colliders", []):
                if getattr(c, "bullet_passable", False):
                    continue
                try:
                    if hasattr(c, "check_collision_circle"):
                        if c.check_collision_circle((x, y), r, (obs.world_x, obs.world_y)):
                            return True
                    elif hasattr(c, "compute_penetration_circle"):
                        pen = c.compute_penetration_circle((x, y), r, (obs.world_x, obs.world_y))
                        if pen:
                            return True
                except Exception:
                    return True
        return False

    # 반동/쉐이크
    def _fire_kick(self, strength=8, timer=10):
        # 무기 반동(WeaponBase offset) + 카메라 흔들림
        self.last_shot_time = self._now()
        try:
            config.shake_strength = max(getattr(config, "shake_strength", 0), strength)
            config.shake_timer    = max(getattr(config, "shake_timer", 0),   timer)
        except Exception:
            pass

    # 사운드: 피치 변조 + 거리감쇠 + 팬
    def _prepare_boom_variants(self):
        # boom 사운드를 ±6% 범위에서 몇 개 변조해 캐시. numpy가 없으면 폴백.
        base = self.sounds.get("boom")
        self._boom_variants = [base] if base else []
        if not base: return
        try:
            import numpy as np
            import pygame.sndarray as snd
            arr = snd.array(base)  # shape: (n,) or (n,2)
            if arr is None: return
            for pitch in self.PITCH_VARIANTS:
                if abs(pitch) < 1e-6: 
                    continue
                scale = 1.0 + pitch   # >1이면 pitch up(샘플 수 감소)
                n = arr.shape[0]
                new_len = max(1, int(n / scale))
                # 선형 보간 리샘플
                idx = (np.arange(new_len) * scale).clip(0, n-1)
                idx0 = np.floor(idx).astype(np.int32)
                idx1 = np.minimum(idx0 + 1, n-1)
                frac = idx - idx0
                new_arr = (arr[idx0] * (1.0 - frac) + arr[idx1] * frac).astype(arr.dtype)
                snd_obj = snd.make_sound(new_arr)
                self._boom_variants.append(snd_obj)
        except Exception:
            # 폴백: 변조 실패 시 원본만 사용(볼륨 랜덤으로 디코릴레이션)
            pass

    def _play_positional(self, key_or_variant, wx, wy, base_volume=1.0, hearing_radius=900.0):
        # 월드 좌표 기준 거리감쇠 + 좌우 팬 적용해서 재생
        if isinstance(key_or_variant, str):
            s = self.sounds.get(key_or_variant)
        else:
            s = key_or_variant
        if not s: return None

        # 거리 감쇠
        px, py = self.get_player_world_position()
        dx, dy = wx - px, wy - py
        dist = math.hypot(dx, dy)
        atten = max(0.0, min(1.0, 1.0 - (dist / max(1.0, hearing_radius))))
        vol = base_volume * (0.25 + 0.75 * atten)  # 너무 작아지지 않게 베이스 유지

        # 좌/우 팬: dx를 기반으로 약하게 이동(-1..1)
        pan = max(-1.0, min(1.0, dx / (hearing_radius * 0.8)))
        left  = max(0.0, min(1.0, vol * (1.0 - 0.6 * pan)))
        right = max(0.0, min(1.0, vol * (1.0 + 0.6 * pan)))

        try:
            ch = s.play()
            if ch:
                # pygame은 set_volume(left, right) 지원(스테레오일 때)
                try:
                    ch.set_volume(left, right)
                except TypeError:
                    ch.set_volume(vol)
            return ch
        except Exception:
            return None

    # 상태이상/피해
    def _apply_slow(self, enemy, dur_ms=None, factor=None):
        now = self._now()
        d = dur_ms if dur_ms is not None else self.SLOW_DURATION_MS
        f = factor if factor is not None else self.SLOW_FACTOR
        try:
            enemy._cluster_slow_until  = max(getattr(enemy, "_cluster_slow_until", 0), now + d)
            enemy._cluster_slow_factor = f
        except Exception:
            pass

    def _damage_enemy(self, e, dmg, hit_type="explosion"):
        try:
            if hasattr(e, "on_hit"):
                e.on_hit(dmg, knockback=4, hit_type=hit_type)
            elif hasattr(e, "hit"):
                e.hit(dmg, None)
            else:
                e.hp = getattr(e, "hp", 0) - dmg
                if e.hp <= 0: e.alive = False
        except Exception:
            pass

    # 입력/업데이트
    def on_update(self, left_down, right_down):
        now = self._now()
        l_allow, r_allow = self._filter_inputs(left_down, right_down)

        # 프레임 시작: 소탄 폭발음 스로틀 카운터 리셋
        self._boom_count_this_frame = 0

        # 좌클릭: 발사(엣지 기준으로 쿨다운)
        left_edge = l_allow and (not self._prev_left) and now >= self._next_left_ms
        if left_edge:
            if self.get_ammo_gauge() >= self.LEFT_AMMO_COST:
                self.reduce_ammo(self.LEFT_AMMO_COST)
                self._fire_shell()
                # 발사음(거리/팬 적용)
                (ux, uy), _ = self._unit_from_mouse()
                px, py = self.get_player_world_position()
                sx = px + ux * (30 * config.PLAYER_VIEW_SCALE)
                sy = py + uy * (30 * config.PLAYER_VIEW_SCALE)
                self._play_positional("fire", sx, sy, base_volume=0.95, hearing_radius=self.HEARING_RADIUS_MAIN)
                # 반동/쉐이크
                self._fire_kick(strength=7, timer=9)
                self._next_left_ms = now + self.LEFT_COOLDOWN_MS

        # 우클릭: 누르는 동안 '예고 링'만 표시, '떼는 순간' 실제 폭발
        # 예고 링 표시 상태
        self._arm_hint_active = bool(right_down and self._shells)
        # 우클릭 릴리즈 엣지에서 기폭
        right_released = (self._prev_right and not right_down) and now >= self._next_right_ms
        if right_released and self._shells:
            self._remote_detonate()
            self._next_right_ms = now + self.RIGHT_COOLDOWN_MS

        # 본탄/소탄 이동 & 충돌/퓨즈
        self._update_shells()
        self._update_clusters()

        # 폭발/트레일/스파크 만료 정리
        self._explosions[:] = [e for e in self._explosions if now <= e["until_ms"]]
        for t in self._trails:
            t["ttl"] -= 1
        self._trails[:] = [t for t in self._trails if t["ttl"] > 0]
        self._update_sparks()

        # 엣지 저장
        self._prev_left  = bool(left_down)
        self._prev_right = bool(right_down)

    # 발사/폭발
    def _fire_shell(self):
        (ux, uy), ang = self._unit_from_mouse()
        px, py = self.get_player_world_position()
        sx = px + ux * (30 * config.PLAYER_VIEW_SCALE)
        sy = py + uy * (30 * config.PLAYER_VIEW_SCALE)
        vx, vy = ux * self.SHELL_SPEED, uy * self.SHELL_SPEED
        self._shells.append({
            "x": sx, "y": sy,
            "vx": vx, "vy": vy,
            "dir_deg": int(-math.degrees(ang)) % 360,
            "dist": 0.0
        })

    def _remote_detonate(self):
        if not self._shells: return
        s = self._shells.pop(0)
        self._explode_main(s["x"], s["y"])

    def _explode_main(self, x, y):
        # 피해+슬로우
        self._apply_aoe_damage_and_slow(x, y, self.SHELL_AOE_RADIUS, self.SHELL_DAMAGE, main=True)
        # VFX/사운드/쉐이크
        self._spawn_explosion_fx(x, y, main=True)
        self._play_positional(self._pick_boom_variant(), x, y, base_volume=1.0, hearing_radius=self.HEARING_RADIUS_MAIN)
        self._fire_kick(*self.EXPLOSION_SHAKE_MAIN)
        # 미세 스파크 몇 개
        self._spawn_sparks(x, y, count=6)
        # 분열 소탄 생성(직선)
        base_ang = random.random() * math.tau
        for i in range(self.CLUSTER_COUNT):
            a = base_ang + (math.tau * i / self.CLUSTER_COUNT) + math.radians(random.uniform(-10, 10))
            spd = random.uniform(self.CLUSTER_SPEED_MIN, self.CLUSTER_SPEED_MAX)
            self._clusters.append({
                "x": x, "y": y,
                "vx": math.cos(a) * spd,
                "vy": math.sin(a) * spd,
                "born_ms": self._now(),
                "fuse_ms": random.randint(self.CLUSTER_FUSE_MIN_MS, self.CLUSTER_FUSE_MAX_MS),
            })

    def _explode_cluster(self, x, y):
        # 피해+슬로우
        self._apply_aoe_damage_and_slow(x, y, self.CLUSTER_AOE_RADIUS, self.CLUSTER_DAMAGE, main=False)
        # VFX/사운드(스로틀/볼륨↓)/쉐이크
        self._spawn_explosion_fx(x, y, main=False)
        now = self._now()
        if self._boom_count_this_frame < self.CLUSTER_BOOM_FRAME_LIMIT and (now - self._last_boom_ms) >= self.CLUSTER_BOOM_MIN_GAP_MS:
            self._play_positional(self._pick_boom_variant(), x, y, base_volume=0.55, hearing_radius=self.HEARING_RADIUS_CHILD)
            self._last_boom_ms = now
            self._boom_count_this_frame += 1
        self._fire_kick(*self.EXPLOSION_SHAKE_CHILD)
        # 미세 스파크 소량
        self._spawn_sparks(x, y, count=4)

    def _apply_aoe_damage_and_slow(self, x, y, radius, damage, main=True):
        r2 = radius * radius
        for e in list(self._enemies()):
            if not getattr(e, "alive", False): 
                continue
            ex = getattr(e, "world_x", getattr(e, "x", None))
            ey = getattr(e, "world_y", getattr(e, "y", None))
            if ex is None or ey is None: continue
            if (ex - x)**2 + (ey - y)**2 <= (r2 + getattr(e, "radius", 16)**2):
                self._damage_enemy(e, damage, hit_type="cluster_main" if main else "cluster_child")
                self._apply_slow(e, self.SLOW_DURATION_MS, self.SLOW_FACTOR)

    def _spawn_explosion_fx(self, x, y, main=True):
        self._explosions.append({
            "x": x, "y": y,
            "until_ms": self._now() + self.EXPLOSION_RING_MS,
            "main": main
        })

    def _pick_boom_variant(self):
        # 피치 변조된 사운드 중 하나 선택(없으면 기본)
        if self._boom_variants:
            return random.choice(self._boom_variants)
        return self.sounds.get("boom")

    # 이동/충돌
    def _update_shells(self):
        if not self._shells: return
        i = 0
        while i < len(self._shells):
            s = self._shells[i]
            # CCD: 짧은 스텝 분할 이동(직선)
            moved = 0.0
            step_max = 4.0
            speed = math.hypot(s["vx"], s["vy"]) or 0.01
            while moved < speed:
                step = min(step_max, speed - moved)
                ux = s["vx"] / speed; uy = s["vy"] / speed
                s["x"] += ux * step; s["y"] += uy * step
                s["dist"] += step

                # 장애물/적 충돌 → 즉시 폭발
                if self._collides_obstacle_circle(s["x"], s["y"], self.SHELL_RADIUS):
                    self._shells.pop(i); self._explode_main(s["x"], s["y"]); break
                hit_enemy = None
                for e in self._enemies():
                    if not getattr(e, "alive", False): continue
                    ex = getattr(e, "world_x", getattr(e, "x", None))
                    ey = getattr(e, "world_y", getattr(e, "y", None))
                    if ex is None or ey is None: continue
                    rr = getattr(e, "radius", 16) + self.SHELL_RADIUS
                    if (ex - s["x"])**2 + (ey - s["y"])**2 <= rr*rr:
                        hit_enemy = e; break
                if hit_enemy:
                    self._shells.pop(i); self._explode_main(s["x"], s["y"]); break

                # 최대 사거리 초과 → 자동 폭발
                if s["dist"] >= self.SHELL_MAX_RANGE:
                    self._shells.pop(i); self._explode_main(s["x"], s["y"]); break

                moved += step
            else:
                # 트레일 포인트
                self._trails.append({"x": s["x"], "y": s["y"], "ttl": self.TRAIL_POINTS})
                i += 1

    def _update_clusters(self):
        if not self._clusters: return
        i = 0
        while i < len(self._clusters):
            c = self._clusters[i]
            # 퓨즈 만료 → 폭발
            if self._now() - c["born_ms"] >= min(self.CLUSTER_LIFETIME_MS, c["fuse_ms"]):
                self._clusters.pop(i); self._explode_cluster(c["x"], c["y"]); continue

            # CCD 직선 이동
            moved = 0.0
            step_max = 4.0
            speed = math.hypot(c["vx"], c["vy"]) or 0.01
            while moved < speed:
                step = min(step_max, speed - moved)
                ux = c["vx"] / speed; uy = c["vy"] / speed
                c["x"] += ux * step; c["y"] += uy * step

                # 장애물/적 충돌 시 즉발
                if self._collides_obstacle_circle(c["x"], c["y"], self.CLUSTER_RADIUS):
                    self._clusters.pop(i); self._explode_cluster(c["x"], c["y"]); break
                hit_enemy = None
                for e in self._enemies():
                    if not getattr(e, "alive", False): continue
                    ex = getattr(e, "world_x", getattr(e, "x", None))
                    ey = getattr(e, "world_y", getattr(e, "y", None))
                    if ex is None or ey is None: continue
                    rr = getattr(e, "radius", 16) + self.CLUSTER_RADIUS
                    if (ex - c["x"])**2 + (ey - c["y"])**2 <= rr*rr:
                        hit_enemy = e; break
                if hit_enemy:
                    self._clusters.pop(i); self._explode_cluster(c["x"], c["y"]); break

                moved += step
            else:
                i += 1

    # VFX
    def _spawn_sparks(self, x, y, count=5):
        # 미세 스파크 VFX: 데미지 없음, 짧게 흩어짐
        for _ in range(count):
            ang = random.random() * math.tau
            spd = random.uniform(4.0, 7.0)
            self._sparks.append({
                "x": x, "y": y,
                "vx": math.cos(ang) * spd,
                "vy": math.sin(ang) * spd,
                "born": self._now(),
                "life": random.randint(90, 140)
            })

    def _update_sparks(self):
        now = self._now()
        alive = []
        for s in self._sparks:
            if now - s["born"] > s["life"]:
                continue
            s["x"] += s["vx"]; s["y"] += s["vy"]
            alive.append(s)
        self._sparks = alive

    # 렌더
    def draw_overlay(self, screen):
        sw, sh = screen.get_size()
        now = self._now()

        # 본탄 + 트레일
        if self._shells or self._trails:
            layer = pygame.Surface((sw, sh), pygame.SRCALPHA)
            # 트레일
            for t in self._trails:
                sx, sy = self._world_to_screen(t["x"], t["y"])
                alpha = 60 + int(40 * (t["ttl"] / float(self.TRAIL_POINTS)))
                pygame.draw.circle(layer, (255, 240, 200, alpha), (int(sx), int(sy)), 2)
            # 본탄
            for s in self._shells:
                sx, sy = self._world_to_screen(s["x"], s["y"])
                if self._grenade_img:
                    deg = s["dir_deg"]
                    img = self._rot_cache.get(deg)
                    if img is None:
                        img = pygame.transform.rotate(self._grenade_img, deg)
                        self._rot_cache[deg] = img
                    layer.blit(img, img.get_rect(center=(int(sx), int(sy))))
                else:
                    pygame.draw.circle(layer, (180,180,180,230), (int(sx), int(sy)), self.SHELL_RADIUS)
                    pygame.draw.circle(layer, (255,255,255,200), (int(sx)+2, int(sy)-2), 2)
            screen.blit(layer, (0,0))

        # 소탄(버블렛)
        if self._clusters:
            bl = pygame.Surface((sw, sh), pygame.SRCALPHA)
            for c in self._clusters:
                sx, sy = self._world_to_screen(c["x"], c["y"])
                pygame.draw.circle(bl, (255, 180, 90, 230), (int(sx), int(sy)), self.CLUSTER_RADIUS)
                pygame.draw.circle(bl, (255, 220, 120, 200), (int(sx), int(sy)), int(self.CLUSTER_RADIUS*0.72))
                pygame.draw.circle(bl, (255, 255, 255, 170), (int(sx)+2, int(sy)-2), 2)
            screen.blit(bl, (0,0))

        # 폭발 링
        if self._explosions:
            fx = pygame.Surface((sw, sh), pygame.SRCALPHA)
            for e in self._explosions:
                sx, sy = self._world_to_screen(e["x"], e["y"])
                t = 1.0 - (e["until_ms"] - now) / float(self.EXPLOSION_RING_MS)
                t = max(0.0, min(1.0, t))
                rad = int((self.SHELL_AOE_RADIUS if e["main"] else self.CLUSTER_AOE_RADIUS) * (0.75 + 0.35*t))
                alpha = int(200 * (1.0 - t))
                color_fill = (255, 210, 140, max(50, alpha//2))
                color_line = (255, 240, 200, alpha)
                pygame.draw.circle(fx, color_fill, (int(sx), int(sy)), int(rad*0.65))
                pygame.draw.circle(fx, color_line, (int(sx), int(sy)), rad, width=3)
            screen.blit(fx, (0,0))

        # 미세 스파크
        if self._sparks:
            sp = pygame.Surface((sw, sh), pygame.SRCALPHA)
            for s in self._sparks:
                sx, sy = self._world_to_screen(s["x"], s["y"])
                pygame.draw.circle(sp, (255, 240, 200, 180), (int(sx), int(sy)), 2)
            screen.blit(sp, (0,0))

        # UX - 본탄 연결선(점선: 항상 표시) & 우클릭 홀드 예고 링
        if self._shells:
            # 가장 오래된 본탄
            target = self._shells[0]
            px, py = self.get_player_world_position()
            sx0, sy0 = self._world_to_screen(px, py)
            sx1, sy1 = self._world_to_screen(target["x"], target["y"])

            # 점선(시안) 항상 표시 (깜빡임 제거)
            guide = pygame.Surface((sw, sh), pygame.SRCALPHA)
            segs = 14
            for i in range(segs):
                t0 = i / float(segs)
                t1 = (i + 0.5) / float(segs)
                x0 = int(sx0 + (sx1 - sx0) * t0)
                y0 = int(sy0 + (sy1 - sy0) * t0)
                x1 = int(sx0 + (sx1 - sx0) * t1)
                y1 = int(sy0 + (sy1 - sy0) * t1)
                pygame.draw.line(guide, (130, 230, 255, 140), (x0, y0), (x1, y1), 2)
            screen.blit(guide, (0,0))

            # 우클릭 홀드 중 예고 링(폭발 반경)
            if self._arm_hint_active:
                hint = pygame.Surface((sw, sh), pygame.SRCALPHA)
                pygame.draw.circle(hint, (140, 220, 255, 90), (int(sx1), int(sy1)), self.SHELL_AOE_RADIUS, width=2)
                screen.blit(hint, (0,0))

class Gun36(WeaponBase):
    TIER = 4

    LEFT_AMMO_COST      = 20
    LEFT_COOLDOWN_MS    = 450
    RIGHT_COOLDOWN_MS   = 0

    MAX_MINES           = 6
    AUTO_FUSE_MS        = 10_000
    MINE_SPEED          = 14.5
    MINE_MAX_RANGE      = 2000.0
    MINE_RADIUS         = 20
    MINE_STUCK_NUDGE    = 2.0

    EXPLOSION_RADIUS    = 90
    EXPLOSION_DAMAGE    = 75

    EXPLOSION_RING_MS   = 520
    EXPLOSION_RAYS      = 12
    FLASH_MS            = 120

    @staticmethod
    def create_instance(weapon_assets, sounds, ammo_gauge, consume_ammo, get_player_world_position):
        wa = weapon_assets.get("gun36", {})
        bullets = wa.get("bullets") or []

        if not bullets:
            for _, ent in weapon_assets.items():
                if isinstance(ent, dict) and ent.get("bullets"):
                    bullets = ent["bullets"]; break
        front   = wa.get("front")
        topdown = wa.get("topdown")

        return Gun36(
            name="점착 지뢰 발사기",
            front_image=front, topdown_image=topdown,
            uses_bullets=True, bullet_images=bullets,
            uses_cartridges=False, cartridge_images=[],
            can_left_click=True, can_right_click=True,
            left_click_ammo_cost=Gun36.LEFT_AMMO_COST,
            right_click_ammo_cost=0,
            tier=Gun36.TIER,
            sounds_dict={
                "leftfire":  sounds.get("gun36_leftfire"),
                "rightfire": sounds.get("gun36_rightfire"),
                "explosion": sounds.get("gun36_rightfire"),
            },
            get_ammo_gauge_fn=ammo_gauge, reduce_ammo_fn=consume_ammo,
            bullet_has_trail=False,
            get_player_world_position_fn=get_player_world_position,
            exclusive_inputs=True
        )

    def __init__(self, name, front_image, topdown_image, **kwargs):
        super().__init__(name, front_image, topdown_image, **kwargs)
        self.distance_from_center = 52 * config.PLAYER_VIEW_SCALE
        self.recoil_strength      = 7
        self.speed_penalty        = 0.08
        self.shake_strength       = 10

        self._next_left_ms  = 0
        self._next_right_ms = 0
        self._prev_left     = False
        self._prev_right    = False

        self._mines            = []
        self._explosions       = []
        self._explosion_rays   = []
        self._explosion_flash  = []

        self._mine_img        = self.bullet_images[0] if (self.bullet_images and self.bullet_images[0]) else None
        self._rot_cache       = {}

        self._last_room_pos = self._get_room_pos()

    # 유틸리티
    def _now(self):
        return pygame.time.get_ticks()

    def _get_main(self):
        # __main__ 모듈 접근(현재 방 좌표/카메라 흔들림 오프셋 획득용)
        try:
            import __main__ as g
            return g
        except Exception:
            return None

    def _get_shake_offset(self):
        # 카메라 흔들림 오프셋을 지뢰 렌더에 반영
        g = self._get_main()
        if g is None:
            return 0, 0
        return getattr(g, "shake_offset_x", 0), getattr(g, "shake_offset_y", 0)

    def _get_room_pos(self):
        # 현재 방 좌표(맵 그리드 좌표) 획득
        g = self._get_main()
        if g is None:
            return None
        return getattr(g, "current_room_pos", None)

    def _check_room_transition_clear(self):
        # 방 이동 감지 시 남아있는 지뢰/이펙트를 즉시 제거(폭발 처리 없이 깔끔히 정리)
        cur = self._get_room_pos()
        if cur is None:
            return
        if getattr(self, "_last_room_pos", None) is None:
            self._last_room_pos = cur
            return
        if cur != self._last_room_pos:
            self._mines.clear()
            self._explosions.clear()
            self._explosion_rays.clear()
            self._explosion_flash.clear()
            self._last_room_pos = cur

    def _world_to_screen(self, wx, wy):
        # 월드좌표 → 화면좌표 변환(플레이어 기준) + 개선: 카메라 흔들림 오프셋 적용
        cx, cy = config.player_rect.centerx, config.player_rect.centery
        px, py = self.get_player_world_position()
        sx = cx + (wx - px)
        sy = cy + (wy - py)
        ox, oy = self._get_shake_offset()  # 카메라 흔들림 보정
        return (sx + ox, sy + oy)

    def _unit_from_mouse(self):
        # 플레이어 중심 → 마우스 방향 단위벡터/각도
        mx, my = pygame.mouse.get_pos()
        dx = mx - config.player_rect.centerx
        dy = my - config.player_rect.centery
        ang = math.atan2(dy, dx)
        return (math.cos(ang), math.sin(ang)), ang

    def _enemies(self):
        # 적 목록(프로젝트 컨벤션상 all_enemies 우선)
        return getattr(config, "all_enemies", getattr(config, "enemies", []))

    def _all_obstacles(self):
        # 항상 최신 obstacle_manager 사용(맵 전환/전투벽 즉시 반영)
        om = getattr(config, "obstacle_manager", None)
        if not om:
            return []
        return list(getattr(om, "placed_obstacles", [])) + \
               list(getattr(om, "static_obstacles", [])) + \
               list(getattr(om, "combat_obstacles", []))

    def _collides_obstacle_circle(self, x, y, r):
        # 원형 콜라이더(지뢰)와 장애물 충돌 검사
        for obs in self._all_obstacles():
            for c in getattr(obs, "colliders", []):
                if getattr(c, "bullet_passable", False):
                    continue
                try:
                    if hasattr(c, "check_collision_circle"):
                        if c.check_collision_circle((x, y), r, (obs.world_x, obs.world_y)):
                            return True
                    elif hasattr(c, "compute_penetration_circle"):
                        pen = c.compute_penetration_circle((x, y), r, (obs.world_x, obs.world_y))
                        if pen:
                            return True
                except Exception:
                    # 예외시 보수적으로 '충돌' 처리하여 관통 방지
                    return True
        return False

    def _enemy_radius(self, e):
        # 적 반지름 폴백(없으면 기본 28)
        return max(10, int(getattr(e, "radius", 28)))

    def _damage_enemy(self, e, dmg, hit_type="explosion"):
        # 적에게 피해 적용(프로젝트 전역 컨벤션 우선 사용)
        try:
            if hasattr(e, "on_hit"):
                e.on_hit(dmg, knockback=4, hit_type=hit_type)
            elif hasattr(e, "hit"):
                e.hit(dmg, None)
            else:
                e.hp = getattr(e, "hp", 0) - dmg
                if e.hp <= 0:
                    e.alive = False
        except Exception:
            pass

    def _play(self, key):
        s = self.sounds.get(key)
        if s:
            try:
                s.play()
            except Exception:
                pass

    def _fire_kick(self, strength=8, timer=10):
        # 카메라 흔들림은 메인 루프가 self.last_shot_time과 self.shake_strength를 읽어 처리
        self.last_shot_time = self._now()

    # 입력/업데이트 루프
    def on_update(self, left_down, right_down):
        now = self._now()

        # 방 이동 감지 → 자동 정리(개선 사항 반영)
        self._check_room_transition_clear()

        # 무기 공통 필터(입력 배타/스위칭 중 차단 등)
        l_allow, r_allow = self._filter_inputs(left_down, right_down)

        if l_allow and now >= self._next_left_ms:
            if self.get_ammo_gauge() >= self.LEFT_AMMO_COST:
                self.reduce_ammo(self.LEFT_AMMO_COST)
                self._fire_mine()
                self._play("leftfire")
                self._fire_kick(strength=8, timer=10)
                self._next_left_ms = now + self.LEFT_COOLDOWN_MS

        right_edge = r_allow and (not self._prev_right) and now >= self._next_right_ms
        if right_edge and self._mines:
            self._remote_detonate_all()
            self._next_right_ms = now + self.RIGHT_COOLDOWN_MS

        self._prev_left, self._prev_right = l_allow, r_allow

        # 지뢰 상태 갱신(비행/부착/자동기폭 등)
        self._update_mines()

        # 폭발 이펙트 수명 관리
        self._expire_fx()

    # 발사/오브젝트 생성
    def _fire_mine(self):
        # 총구 위치 계산(플레이어 세계좌표 + 조준 방향 오프셋)
        (ux, uy), ang = self._unit_from_mouse()
        px, py = self.get_player_world_position()
        muzzle_x = px + ux * (30 * config.PLAYER_VIEW_SCALE)
        muzzle_y = py + uy * (30 * config.PLAYER_VIEW_SCALE)

        # 최대 설치 수 초과 시: 가장 오래된 지뢰를 먼저 폭발시켜 자리 확보
        if len(self._mines) >= self.MAX_MINES:
            oldest_idx = min(range(len(self._mines)), key=lambda i: self._mines[i]["born_ms"])
            m = self._mines.pop(oldest_idx)
            self._explode_mine(m)

        # 신규 지뢰 생성(비행 상태로 시작)
        spd = self.MINE_SPEED
        now = self._now()
        mine = {
            "state": "flying",
            "x": muzzle_x, "y": muzzle_y,
            "vx": ux * spd, "vy": uy * spd,
            "dir": ang,
            "dist": 0.0,
            "born_ms": now,
            "explode_at": now + self.AUTO_FUSE_MS,
            "enemy": None,
            "rel": (0.0, 0.0),
            "spin": random.uniform(5, 9) * (1 if random.random() < 0.5 else -1),
            "rot": random.uniform(0, 360),
        }
        self._mines.append(mine)

    def _remote_detonate_all(self):
        # 모든 지뢰 즉시 폭발(목록 복사 후 순회)
        mines = list(self._mines)
        self._mines.clear()
        for m in mines:
            self._explode_mine(m)

    def _explode_mine(self, m):
        # 폭발 피해 판정
        x, y = m["x"], m["y"]
        self._apply_aoe_damage(x, y, self.EXPLOSION_RADIUS, self.EXPLOSION_DAMAGE)

        now = self._now()

        # 폭발 이펙트: 링 + 방사형 레이 + 플래시
        self._explosions.append({
            "x": x, "y": y,
            "born_ms": now,
            "until_ms": now + self.EXPLOSION_RING_MS
        })
        # 방사형 레이 생성
        for i in range(self.EXPLOSION_RAYS):
            a = (2*math.pi) * (i / self.EXPLOSION_RAYS) + random.uniform(-0.1, 0.1)
            speed = random.uniform(7.0, 12.0)
            self._explosion_rays.append({
                "x": x, "y": y,
                "vx": math.cos(a) * speed,
                "vy": math.sin(a) * speed,
                "life": 0,
                "ttl": random.randint(220, 360),
                "width": random.randint(2, 3),
            })
        # 순간 플래시
        self._explosion_flash.append({
            "x": x, "y": y,
            "until_ms": now + self.FLASH_MS
        })

        # 사운드
        self._play("explosion")

    def _apply_aoe_damage(self, x, y, radius, damage, hit_type="explosion"):
        # 단순 원거리 내 적에게 피해 적용(적 자체 반지름 포함)
        r2 = radius * radius
        for e in list(self._enemies()):
            if not getattr(e, "alive", False):
                continue
            ex = getattr(e, "world_x", getattr(e, "x", None))
            ey = getattr(e, "world_y", getattr(e, "y", None))
            if ex is None or ey is None:
                continue
            rr = self._enemy_radius(e)
            if (ex - x) * (ex - x) + (ey - y) * (ey - y) <= (r2 + rr * rr):
                self._damage_enemy(e, damage, hit_type=hit_type)

    # 지뢰 업데이트
    def _update_mines(self):
        # 비활성 시 빠른 리턴
        if not self._mines:
            return

        now = self._now()
        i = 0
        while i < len(self._mines):
            m = self._mines[i]
            state = m["state"]

            # 자동 기폭 타이밍 도래
            if now >= m["explode_at"]:
                self._mines.pop(i)
                self._explode_mine(m)
                continue

            if state == "flying":
                # CCD(작은 스텝)로 이동하여 빠른 물체의 관통 문제 완화
                moved = 0.0
                step_max = 6.0
                speed = math.hypot(m["vx"], m["vy"]) or 0.01
                while moved < speed:
                    step = min(step_max, speed - moved)
                    ux = m["vx"] / speed; uy = m["vy"] / speed
                    m["x"] += ux * step; m["y"] += uy * step
                    m["dist"] += step
                    moved += step

                    # 적에 닿으면 그 적에게 부착
                    hit_enemy = None
                    for e in self._enemies():
                        if not getattr(e, "alive", False):
                            continue
                        ex = getattr(e, "world_x", getattr(e, "x", None))
                        ey = getattr(e, "world_y", getattr(e, "y", None))
                        if ex is None or ey is None:
                            continue
                        rr = self._enemy_radius(e)
                        if (ex - m["x"])**2 + (ey - m["y"])**2 <= (rr + self.MINE_RADIUS)**2:
                            hit_enemy = e; break
                    if hit_enemy is not None:
                        ex = getattr(hit_enemy, "world_x", getattr(hit_enemy, "x", None))
                        ey = getattr(hit_enemy, "world_y", getattr(hit_enemy, "y", None))
                        # 부착시 적 중심 기준으로 살짝 안쪽으로 붙여 자연스러움 확보
                        dx = m["x"] - ex; dy = m["y"] - ey
                        d = math.hypot(dx, dy) or 1.0
                        m["x"] = ex + dx / d * (self._enemy_radius(hit_enemy) - self.MINE_STUCK_NUDGE)
                        m["y"] = ey + dy / d * (self._enemy_radius(hit_enemy) - self.MINE_STUCK_NUDGE)
                        m["state"] = "stuck_enemy"
                        m["enemy"] = hit_enemy
                        m["rel"] = (m["x"] - ex, m["y"] - ey)
                        m["vx"] = m["vy"] = 0.0
                        break  # 이 프레임의 잔여 스텝 종료

                    # 장애물/벽에 닿으면 그 자리에서 정지(부착)
                    if self._collides_obstacle_circle(m["x"], m["y"], self.MINE_RADIUS):
                        # 너무 깊게 박히지 않도록 미세하게 뒤로 당김
                        m["x"] -= ux * 0.5; m["y"] -= uy * 0.5
                        m["state"] = "stuck_static"
                        m["vx"] = m["vy"] = 0.0
                        break

                    # 3) 최대 사거리 소진 → 그 지점에서 고정
                    if m["dist"] >= self.MINE_MAX_RANGE:
                        m["state"] = "stuck_static"
                        m["vx"] = m["vy"] = 0.0
                        break

                # 비행 중에는 천천히 회전
                m["rot"] = (m["rot"] + m["spin"]) % 360

            elif state == "stuck_enemy":
                # 부착 대상이 살아있으면 상대 좌표를 유지하여 따라감
                e = m["enemy"]
                if e is None or (not getattr(e, "alive", False)):
                    # 대상 사망/소멸 시 해당 지점에 고정 상태로 전환
                    m["enemy"] = None
                    m["state"] = "stuck_static"
                else:
                    ex = getattr(e, "world_x", getattr(e, "x", None))
                    ey = getattr(e, "world_y", getattr(e, "y", None))
                    rx, ry = m["rel"]
                    m["x"] = ex + rx; m["y"] = ey + ry

            # 다음 지뢰
            i += 1

    # 폭발 FX 수명 처리
    def _expire_fx(self):
        now = self._now()
        # 폭발 링 만료
        self._explosions[:] = [e for e in self._explosions if now <= e["until_ms"]]
        # 방사형 레이 감쇠/소멸
        kept = []
        for r in self._explosion_rays:
            r["x"] += r["vx"]; r["y"] += r["vy"]
            r["vx"] *= 0.96; r["vy"] *= 0.96
            r["life"] += 16
            if r["life"] < r["ttl"]:
                kept.append(r)
        self._explosion_rays = kept
        # 플래시 만료
        self._explosion_flash[:] = [f for f in self._explosion_flash if now <= f["until_ms"]]

    # 렌더링(오버레이)
    def draw_overlay(self, screen):
        sw, sh = screen.get_size()
        now = self._now()

        # 지뢰(비행/부착) 렌더 + 플레이어↔지뢰 점선(테더) 표시
        if self._mines:
            layer = pygame.Surface((sw, sh), pygame.SRCALPHA)
            # 플레이어 화면 좌표(카메라 흔들림 포함)
            px, py = self.get_player_world_position()
            pcx, pcy = self._world_to_screen(px, py)

            for m in self._mines:
                sx, sy = self._world_to_screen(m["x"], m["y"])

                # 테더(점선) — 지뢰 위치 식별 보조
                self._draw_dashed_line(layer, (120, 240, 230, 110),
                                       (int(pcx), int(pcy)), (int(sx), int(sy)),
                                       dash_len=10, gap_len=6, width=2)

                # 지뢰 스프라이트
                if self._mine_img:
                    if m["state"] == "flying":
                        deg = int(-m["rot"]) % 360
                        img = self._rot_cache.get(deg)
                        if img is None:
                            img = pygame.transform.rotate(self._mine_img, deg)
                            self._rot_cache[deg] = img
                        layer.blit(img, img.get_rect(center=(int(sx), int(sy))))
                    else:
                        layer.blit(self._mine_img, self._mine_img.get_rect(center=(int(sx), int(sy))))
                else:
                    # 폴백: 단색 원
                    pygame.draw.circle(layer, (180, 180, 180, 230), (int(sx), int(sy)), self.MINE_RADIUS)
                    pygame.draw.circle(layer, (240, 240, 240, 200), (int(sx)+2, int(sy)-2), 2)

                # LED 점멸(남은 시간에 따라 점점 빨라짐)
                t_left = max(0, m["explode_at"] - now)
                if   t_left > 7000: period = 700
                elif t_left > 4000: period = 400
                elif t_left > 2000: period = 240
                else:               period = 120
                if ((now // period) % 2) == 0:
                    pygame.draw.circle(layer, (40, 255, 80, 240), (int(sx), int(sy)), 4)
                else:
                    pygame.draw.circle(layer, (255, 70, 50, 240), (int(sx), int(sy)), 4)

            screen.blit(layer, (0, 0))

        # 폭발 이펙트(링/레이/플래시)
        if self._explosions or self._explosion_rays or self._explosion_flash:
            fx = pygame.Surface((sw, sh), pygame.SRCALPHA)
            # 링
            for e in self._explosions:
                sx, sy = self._world_to_screen(e["x"], e["y"])
                t = 1.0 - (e["until_ms"] - now) / float(self.EXPLOSION_RING_MS)
                t = max(0.0, min(1.0, t))
                base = self.EXPLOSION_RADIUS
                rad = int(base * (0.7 + 0.45*t))
                alpha = int(220 * (1.0 - t))
                pygame.draw.circle(fx, (255, 210, 140, max(60, alpha//2)), (int(sx), int(sy)), int(rad*0.60))
                pygame.draw.circle(fx, (255, 240, 200, alpha), (int(sx), int(sy)), rad, width=3)

            # 방사형 레이
            for r in self._explosion_rays:
                sx, sy = self._world_to_screen(r["x"], r["y"])
                life_t = r["life"] / max(1, r["ttl"])
                a = max(0, 200 - int(200*life_t))
                pygame.draw.line(fx, (255, 220, 140, a),
                                 (int(sx), int(sy)),
                                 (int(sx + r["vx"]*2), int(sy + r["vy"]*2)),
                                 r["width"])

            # 플래시(짧고 강한 백색 원)
            for fl in self._explosion_flash:
                sx, sy = self._world_to_screen(fl["x"], fl["y"])
                fade = max(0, int(200 * (fl["until_ms"] - now) / float(self.FLASH_MS)))
                pygame.draw.circle(fx, (255, 255, 255, fade), (int(sx), int(sy)), int(self.EXPLOSION_RADIUS*0.7))

            screen.blit(fx, (0, 0))

    # 렌더 보조 함수
    def _draw_dashed_line(self, surf, color_rgba, start, end, dash_len=8, gap_len=6, width=2):
        # 점선 그리기(시작~끝 방향으로 dash_len만큼 선, gap_len만큼 공백을 반복)
        r, g, b, a = color_rgba
        col = pygame.Color(r, g, b, a)
        x1, y1 = start; x2, y2 = end
        dx, dy = x2 - x1, y2 - y1
        dist = math.hypot(dx, dy)
        if dist <= 1:
            return
        ux, uy = dx / dist, dy / dist
        n = int(dist // (dash_len + gap_len)) + 1
        for i in range(n):
            sx = x1 + (dash_len + gap_len) * i * ux
            sy = y1 + (dash_len + gap_len) * i * uy
            ex = sx + dash_len * ux
            ey = sy + dash_len * uy
            pygame.draw.line(surf, col, (int(sx), int(sy)), (int(ex), int(ey)), width)

class Gun37(WeaponBase):
    TIER = 4

    LEFT_AMMO_COST        = 25
    LEFT_COOLDOWN_MS      = 240
    RIGHT_COOLDOWN_MS     = 700

    FRACTURE_DISTANCE     = 300.0
    BOLT_SPEED            = 18.0
    BOLT_RADIUS           = 8
    BOLT_DAMAGE           = 35

    SHARD_COUNT           = 5
    SHARD_SPREAD_DEG      = 60.0
    SHARD_SPEED           = 22.0
    SHARD_RADIUS          = 6
    SHARD_TTL_MS          = 1800
    SHARD_DAMAGE          = 40

    POP_RING_MS           = 280
    POP_FLASH_MS          = 90
    TRAIL_MAX_POINTS      = 5
    PREVIEW_LENGTH        = 160

    @staticmethod
    def create_instance(weapon_assets, sounds, ammo_gauge, consume_ammo, get_player_world_position):
        wa = weapon_assets.get("gun37", {})
        front   = wa.get("front")
        topdown = wa.get("topdown")

        return Gun37(
            name="프랙처 볼트",
            front_image=front, topdown_image=topdown,
            uses_bullets=False, bullet_images=[],
            uses_cartridges=False, cartridge_images=[],
            can_left_click=True, can_right_click=True,
            left_click_ammo_cost=Gun37.LEFT_AMMO_COST,
            right_click_ammo_cost=0,
            tier=Gun37.TIER,
            sounds_dict={
                "leftfire":  sounds.get("gun37_leftfire"),
                "rightfire": sounds.get("gun37_rightfire"),
            },
            get_ammo_gauge_fn=ammo_gauge, reduce_ammo_fn=consume_ammo,
            bullet_has_trail=False,
            get_player_world_position_fn=get_player_world_position,
            exclusive_inputs=True
        )

    def __init__(self, name, front_image, topdown_image, **kwargs):
        super().__init__(name, front_image, topdown_image, **kwargs)
        self.distance_from_center = 50 * config.PLAYER_VIEW_SCALE
        self.recoil_strength      = 5
        self.speed_penalty        = 0.06
        self.shake_strength       = 9

        self._next_left_ms  = 0
        self._next_right_ms = 0
        self._prev_right    = False

        self._bolts      = []
        self._shards     = []
        self._pop_rings  = []
        self._pop_flash  = []

        self._last_room_pos = self._get_room_pos()

    # 유틸리티
    def _now(self):
        return pygame.time.get_ticks()

    def _get_main(self):
        # __main__ 모듈 접근(방 좌표/카메라 흔들림 오프셋 획득용)
        try:
            import __main__ as g
            return g
        except Exception:
            return None

    def _get_room_pos(self):
        # 현재 방 좌표(맵 그리드 좌표) 획득
        g = self._get_main()
        return None if g is None else getattr(g, "current_room_pos", None)

    def _get_shake_offset(self):
        # 카메라 흔들림 오프셋(렌더 시 반영)
        g = self._get_main()
        if g is None:
            return 0, 0
        return getattr(g, "shake_offset_x", 0), getattr(g, "shake_offset_y", 0)

    def _world_to_screen(self, wx, wy):
        # 플레이어 기준 월드→스크린 + 카메라 흔들림 보정
        cx, cy = config.player_rect.centerx, config.player_rect.centery
        px, py = self.get_player_world_position()
        sx = cx + (wx - px)
        sy = cy + (wy - py)
        ox, oy = self._get_shake_offset()
        return (sx + ox, sy + oy)

    def _unit_from_mouse(self):
        # 마우스 방향을 기준으로 단위 벡터와 각도(라디안)를 반환.
        mx, my = pygame.mouse.get_pos()
        dx = mx - config.player_rect.centerx
        dy = my - config.player_rect.centery
        ang = math.atan2(dy, dx)
        return (math.cos(ang), math.sin(ang)), ang

    def _enemies(self):
        # 적 목록(프로젝트 컨벤션상 all_enemies 우선)
        return getattr(config, "all_enemies", getattr(config, "enemies", []))

    def _all_obstacles(self):
        # 최신 obstacle_manager 사용
        om = getattr(config, "obstacle_manager", None)
        if not om:
            return []
        return list(getattr(om, "placed_obstacles", [])) + \
               list(getattr(om, "static_obstacles", [])) + \
               list(getattr(om, "combat_obstacles", []))

    def _collides_obstacle_circle(self, x, y, r):
        # 원형 충돌(볼트의 벽 충돌 판정에 사용, 파편은 관통이므로 사용 안 함)
        for obs in self._all_obstacles():
            for c in getattr(obs, "colliders", []):
                if getattr(c, "bullet_passable", False):
                    continue
                try:
                    if hasattr(c, "check_collision_circle"):
                        if c.check_collision_circle((x, y), r, (obs.world_x, obs.world_y)):
                            return True
                    elif hasattr(c, "compute_penetration_circle"):
                        pen = c.compute_penetration_circle((x, y), r, (obs.world_x, obs.world_y))
                        if pen:
                            return True
                except Exception:
                    return True
        return False

    def _damage_enemy(self, e, dmg, hit_type="projectile"):
        # 적에게 피해 적용(프로젝트 전역 컨벤션 우선)
        try:
            if hasattr(e, "on_hit"):
                e.on_hit(dmg, knockback=2, hit_type=hit_type)
            elif hasattr(e, "hit"):
                e.hit(dmg, None)
            else:
                e.hp = getattr(e, "hp", 0) - dmg
                if e.hp <= 0:
                    e.alive = False
        except Exception:
            pass

    def _play(self, key):
        # 사운드 안전 재생(누락/플랫폼 이슈 방지).
        s = self.sounds.get(key) if hasattr(self, "sounds") else None
        if s:
            try:
                s.play()
            except Exception:
                pass

    def _fire_kick(self):
        # 메인 루프가 last_shot_time/shake_strength를 이용해 흔들림 처리
        self.last_shot_time = self._now()

    # 입력/업데이트
    def on_update(self, left_down, right_down):
        now = self._now()

        # 방 이동 감지 시 오브젝트/이펙트 즉시 정리(잔류 방지)
        self._check_room_transition_clear()

        # 공통 필터(무기 전환 중/입력 배타 등)
        l_allow, r_allow = self._filter_inputs(left_down, right_down)

        if l_allow and now >= self._next_left_ms:
            if self.get_ammo_gauge() >= self.LEFT_AMMO_COST:
                self.reduce_ammo(self.LEFT_AMMO_COST)
                self._spawn_bolt()
                self._play("leftfire")
                self._fire_kick()
                self._next_left_ms = now + self.LEFT_COOLDOWN_MS

        right_edge_release = (not right_down) and self._prev_right

        # 미리보기는 쿨타임과 무관하게 표시(릴리즈 시점에만 쿨 검사)
        if right_edge_release and now >= self._next_right_ms:
            bolt_idx = self._latest_bolt_index()
            if bolt_idx is not None:
                # 수동 분열: 이 경로에서는 여기서 사운드/흔들림 처리
                self._fracture_bolt(bolt_idx)
                self._play("rightfire")
                self._fire_kick()
                self._next_right_ms = now + self.RIGHT_COOLDOWN_MS
            else:
                self._play("rightfire")

        self._prev_right = right_down

        self._update_bolts()
        self._update_shards()
        self._expire_fx()

    # 발사/분열 로직
    def _spawn_bolt(self):
        # 총구 위치 계산
        (ux, uy), ang = self._unit_from_mouse()
        px, py = self.get_player_world_position()
        muzzle_x = px + ux * (30 * config.PLAYER_VIEW_SCALE)
        muzzle_y = py + uy * (30 * config.PLAYER_VIEW_SCALE)

        self._bolts.append({
            "x": muzzle_x, "y": muzzle_y,
            "vx": ux * self.BOLT_SPEED, "vy": uy * self.BOLT_SPEED,
            "dir": ang,
            "dist": 0.0,
            "born_ms": self._now(),
            "trail": [(muzzle_x, muzzle_y)],
            "hit_set": set(),
        })

    def _latest_bolt_index(self):
        # 가장 최근에 쏜 살아있는 볼트의 인덱스 반환(없으면 None)
        if not self._bolts:
            return None
        latest_idx = max(range(len(self._bolts)), key=lambda i: self._bolts[i]["born_ms"])
        return latest_idx

    def _fracture_bolt(self, bolt_idx):
        # 볼트를 파편 5갈래로 즉시 분열(수동 트리거 경로)
        if bolt_idx is None or bolt_idx < 0 or bolt_idx >= len(self._bolts):
            return
        b = self._bolts.pop(bolt_idx)
        self._fracture_at_position(b["x"], b["y"], b["dir"], play_sound=False)

    def _fracture_at_position(self, x, y, dir_ang, play_sound=False):
        # dir_ang 기준 부채꼴로 파편 생성 + FX
        total = self.SHARD_SPREAD_DEG * math.pi / 180.0
        start = dir_ang - total * 0.5
        step  = (total / (self.SHARD_COUNT - 1)) if self.SHARD_COUNT > 1 else 0.0

        for i in range(self.SHARD_COUNT):
            a = start + step * i
            self._shards.append({
                "x": x, "y": y,
                "vx": math.cos(a) * self.SHARD_SPEED,
                "vy": math.sin(a) * self.SHARD_SPEED,
                "born_ms": self._now(),
                "ttl": self.SHARD_TTL_MS,
                "life": 0,
            })

        # 시각 효과(분열 링/플래시)
        now = self._now()
        self._pop_rings.append({"x": x, "y": y, "until_ms": now + self.POP_RING_MS})
        self._pop_flash.append({"x": x, "y": y, "until_ms": now + self.POP_FLASH_MS})

        # 개선점2: 자동 분열(거리/벽 충돌)에선 여기서 사운드/흔들림도 처리
        if play_sound:
            self._play("rightfire")
            self._fire_kick()

    # 오브젝트 갱신
    def _update_bolts(self):
        # 볼트는 '벽 관통 불가' 정책: 벽/장애물 충돌 또는 D 도달 시 분열.
        if not self._bolts:
            return

        i = 0
        while i < len(self._bolts):
            b = self._bolts[i]
            # 이동
            b["x"] += b["vx"]
            b["y"] += b["vy"]
            b["dist"] += math.hypot(b["vx"], b["vy"])

            # 잔상 관리
            trail = b["trail"]
            trail.append((b["x"], b["y"]))
            if len(trail) > self.TRAIL_MAX_POINTS:
                trail.pop(0)

            # 적 피해 + 개선: 적에 맞는 즉시 분열(첫 유효 히트에서 바로 분열)
            fractured_on_enemy = False
            for e in self._enemies():
                if not getattr(e, "alive", False):
                    continue
                ex = getattr(e, "world_x", getattr(e, "x", None))
                ey = getattr(e, "world_y", getattr(e, "y", None))
                if ex is None or ey is None:
                    continue
                rr = max(10, int(getattr(e, "radius", 28)))
                if (ex - b["x"])**2 + (ey - b["y"])**2 <= (rr + self.BOLT_RADIUS)**2:
                    key = id(e)
                    if key not in b["hit_set"]:
                        b["hit_set"].add(key)
                        self._damage_enemy(e, self.BOLT_DAMAGE, hit_type="bolt")
                        fractured_on_enemy = True
                        break

            if fractured_on_enemy:
                # 적 히트 판정 직후 분열(사운드/흔들림 포함)
                self._bolts.pop(i)
                self._fracture_at_position(b["x"], b["y"], b["dir"], play_sound=True)
                continue

            # ① 벽/장애물 충돌 시 즉시 분열(사운드/흔들림 포함)
            if self._collides_obstacle_circle(b["x"], b["y"], self.BOLT_RADIUS):
                self._bolts.pop(i)
                self._fracture_at_position(b["x"], b["y"], b["dir"], play_sound=True)
                continue

            # ② 자동 분열 거리 도달 시 분열(사운드/흔들림 포함)
            if b["dist"] >= self.FRACTURE_DISTANCE:
                self._bolts.pop(i)
                self._fracture_at_position(b["x"], b["y"], b["dir"], play_sound=True)
                continue

            i += 1

    def _update_shards(self):
        # 파편은 '벽 관통 가능' 정책: 장애물 충돌 판정을 건너뛰고, 적 충돌 시에만 소멸.
        if not self._shards:
            return

        i = 0
        while i < len(self._shards):
            s = self._shards[i]
            # 이동
            s["x"] += s["vx"]
            s["y"] += s["vy"]
            s["life"] += 16
            # 수명 종료
            if s["life"] >= s["ttl"]:
                self._shards.pop(i)
                continue

            # (벽 관통) 장애물 충돌 체크 제거

            # 적 충돌 시 피해 주고 소멸(1적 1회)
            hit_any = False
            for e in self._enemies():
                if not getattr(e, "alive", False):
                    continue
                ex = getattr(e, "world_x", getattr(e, "x", None))
                ey = getattr(e, "world_y", getattr(e, "y", None))
                if ex is None or ey is None:
                    continue
                rr = max(10, int(getattr(e, "radius", 28)))
                if (ex - s["x"])**2 + (ey - s["y"])**2 <= (rr + self.SHARD_RADIUS)**2:
                    self._damage_enemy(e, self.SHARD_DAMAGE, hit_type="fracture")
                    hit_any = True
                    break
            if hit_any:
                self._shards.pop(i)
                continue

            i += 1

    def _expire_fx(self):
        now = self._now()
        self._pop_rings[:] = [r for r in self._pop_rings if now <= r["until_ms"]]
        self._pop_flash[:] = [f for f in self._pop_flash if now <= f["until_ms"]]

    def _check_room_transition_clear(self):
        # 방 이동 시 남은 볼트/파편/이펙트 전부 제거(폭발 처리 없이 정리)
        cur = self._get_room_pos()
        if cur is None:
            return
        if getattr(self, "_last_room_pos", None) is None:
            self._last_room_pos = cur
            return
        if cur != self._last_room_pos:
            self._bolts.clear()
            self._shards.clear()
            self._pop_rings.clear()
            self._pop_flash.clear()
            self._last_room_pos = cur

    # 렌더링
    def draw_overlay(self, screen):
        sw, sh = screen.get_size()
        now = self._now()

        # 우클릭 홀드 미리보기(최신 볼트 기준 부채꼴, 쿨타임과 무관하게 표시)
        if pygame.mouse.get_pressed()[2]:
            idx = self._latest_bolt_index()
            if idx is not None:
                b = self._bolts[idx]
                self._draw_fan_preview(screen, b["x"], b["y"], b["dir"],
                                       self.SHARD_SPREAD_DEG, self.PREVIEW_LENGTH)

        # 볼트/잔상 렌더
        if self._bolts:
            s = pygame.Surface((sw, sh), pygame.SRCALPHA)
            for b in self._bolts:
                # 잔상(얇은 라인)
                if len(b["trail"]) >= 2:
                    pts = [self._world_to_screen(x, y) for (x, y) in b["trail"]]
                    for i in range(1, len(pts)):
                        a = int(200 * (i / len(pts)))
                        pygame.draw.line(s, (120, 220, 255, a),
                                         (int(pts[i-1][0]), int(pts[i-1][1])),
                                         (int(pts[i][0]),   int(pts[i][1])), 2)
                # 볼트 본체(작은 다이아몬드)
                sx, sy = self._world_to_screen(b["x"], b["y"])
                ux = math.cos(b["dir"]); uy = math.sin(b["dir"])
                ortx, orty = -uy, ux
                p_front = (sx + ux*10, sy + uy*10)
                p_back  = (sx - ux*8,  sy - uy*8)
                p_left  = (sx + ortx*5, sy + orty*5)
                p_right = (sx - ortx*5, sy - orty*5)
                pygame.draw.polygon(s, (90, 240, 255, 230),
                                    [(int(p_front[0]), int(p_front[1])),
                                     (int(p_left[0]),  int(p_left[1])),
                                     (int(p_back[0]),  int(p_back[1])),
                                     (int(p_right[0]), int(p_right[1]))])
            screen.blit(s, (0, 0))

        # 파편 렌더(작은 바늘형)
        if self._shards:
            s2 = pygame.Surface((sw, sh), pygame.SRCALPHA)
            for shd in self._shards:
                sx, sy = self._world_to_screen(shd["x"], shd["y"])
                ang = math.atan2(shd["vy"], shd["vx"])
                ux = math.cos(ang); uy = math.sin(ang)
                ortx, orty = -uy, ux
                tip   = (sx + ux*10, sy + uy*10)
                tail  = (sx - ux*8,  sy - uy*8)
                lpt   = (sx + ortx*3, sy + orty*3)
                rpt   = (sx - ortx*3, sy - orty*3)
                pygame.draw.polygon(s2, (255, 240, 160, 230),
                                    [(int(tip[0]), int(tip[1])),
                                     (int(lpt[0]), int(lpt[1])),
                                     (int(tail[0]),int(tail[1])),
                                     (int(rpt[0]), int(rpt[1]))])
            screen.blit(s2, (0, 0))

        # 분열 FX(링/플래시)
        if self._pop_rings or self._pop_flash:
            fx = pygame.Surface((sw, sh), pygame.SRCALPHA)
            for r in self._pop_rings:
                sx, sy = self._world_to_screen(r["x"], r["y"])
                t = 1.0 - (r["until_ms"] - now) / float(self.POP_RING_MS)
                t = max(0.0, min(1.0, t))
                rad = int(28 + 42 * t)
                alpha = int(220 * (1.0 - t))
                pygame.draw.circle(fx, (255, 230, 180, max(60, alpha//2)),
                                   (int(sx), int(sy)), int(rad*0.6))
                pygame.draw.circle(fx, (255, 250, 230, alpha),
                                   (int(sx), int(sy)), rad, width=2)
            for fl in self._pop_flash:
                sx, sy = self._world_to_screen(fl["x"], fl["y"])
                fade = max(0, int(220 * (fl["until_ms"] - now) / float(self.POP_FLASH_MS)))
                pygame.draw.circle(fx, (255, 255, 255, fade), (int(sx), int(sy)), 16)
            screen.blit(fx, (0, 0))

    # 렌더 보조
    def _draw_fan_preview(self, screen, wx, wy, dir_ang, spread_deg, length):
        # 우클릭 홀드 시 미리보기 부채꼴을 그린다(최신 볼트 기준).
        sw, sh = screen.get_size()
        surf = pygame.Surface((sw, sh), pygame.SRCALPHA)

        sx, sy = self._world_to_screen(wx, wy)
        spread = spread_deg * math.pi / 180.0
        a0 = dir_ang - spread * 0.5
        a1 = dir_ang + spread * 0.5

        # 부채꼴 폴리곤 포인트 구성(중간 샘플 몇 개)
        pts = [(sx, sy)]
        samples = 8
        for i in range(samples + 1):
            t = i / samples
            a = a0 + (a1 - a0) * t
            px = sx + math.cos(a) * length
            py = sy + math.sin(a) * length
            pts.append((px, py))

        # 내부 반투명 채우기 + 테두리 + 중앙 방향선
        pygame.draw.polygon(surf, (120, 240, 230, 60), [(int(x), int(y)) for (x, y) in pts])
        pygame.draw.arc(surf, (120, 240, 230, 160),
                        pygame.Rect(int(sx - length), int(sy - length), int(length*2), int(length*2)),
                        a0, a1, 2)
        midx = sx + math.cos(dir_ang) * length
        midy = sy + math.sin(dir_ang) * length
        pygame.draw.line(surf, (120, 240, 230, 160), (int(sx), int(sy)), (int(midx), int(midy)), 2)

        screen.blit(surf, (0, 0))

class Gun38(WeaponBase):
    TIER = 5
    NAME = "BFG6000"

    LEFT_AMMO_COST        = 50
    LEFT_COOLDOWN_MS      = 2000
    CHARGE_TIME_MS        = 800

    ORB_SPEED             = 5.0
    ORB_RADIUS            = 22
    ORB_DIRECT_DAMAGE     = 420

    SHOCKWAVE_RADIUS      = 120
    SHOCKWAVE_DAMAGE      = 150

    VINE_RANGE            = 260.0
    VINE_MAX_TARGETS      = 99
    VINE_TICK_MS          = 100
    VINE_DAMAGE_PER_TICK  = 17
    VINE_KEEP_ALIVE_MS    = 200

    FIRE_SHAKE_STRENGTH   = 18
    FIRE_SHAKE_MS         = 250
    HIT_SHAKE_STRENGTH    = 9
    HIT_SHAKE_MS          = 180
    TINT_MAX_ALPHA        = 140
    TINT_DURATION_MS      = 220

    TRAIL_MAX_POINTS      = 8
    IMPACT_RING_MS        = 320
    VINE_SEGMENTS         = 10
    SPARK_RATE_PER_ORB    = 3
    SPARK_TTL_MS          = 380
    SPARK_SPEED_MIN       = 0.5
    SPARK_SPEED_MAX       = 2.4
    MAX_SPARKS            = 160

    @staticmethod
    def create_instance(weapon_assets, sounds, ammo_gauge, consume_ammo, get_player_world_position):
        wa = weapon_assets.get("gun38", {})
        front   = wa.get("front")
        topdown = wa.get("topdown")

        return Gun38(
            name=Gun38.NAME,
            front_image=front, topdown_image=topdown,
            uses_bullets=False, bullet_images=[],
            uses_cartridges=False, cartridge_images=[],
            can_left_click=True, can_right_click=False,
            left_click_ammo_cost=Gun38.LEFT_AMMO_COST,
            right_click_ammo_cost=0,
            tier=Gun38.TIER,
            sounds_dict={
                "fire":       sounds.get("gun38_fire"),
                "explosion":  sounds.get("gun38_explosion"),
                "loop":       sounds.get("gun38_loop"),
            },
            get_ammo_gauge_fn=ammo_gauge, reduce_ammo_fn=consume_ammo,
            bullet_has_trail=False,
            get_player_world_position_fn=get_player_world_position,
            exclusive_inputs=True
        )

    def __init__(self, name, front_image, topdown_image, **kwargs):
        super().__init__(name, front_image, topdown_image, **kwargs)
        self.distance_from_center = 56 * 0.7 * config.PLAYER_VIEW_SCALE
        self.recoil_strength      = 10
        self.speed_penalty        = 0.10
        self.shake_strength       = self.FIRE_SHAKE_STRENGTH

        self._next_left_ms  = 0
        self._prev_left     = False

        self._state           = "idle"
        self._charge_start_ms = 0

        self._orbs = []

        self._impact_rings = []
        self._tint_until   = 0
        self._sparkles     = []

        self._last_vine_dot_ms = -10_000
        self._vine_loop_ch     = None
        self._rng              = random.Random()

        self._last_room_pos = self._get_room_pos()

    # 유틸리티
    def _now(self): return pygame.time.get_ticks()

    def _get_main(self):
        try:
            import __main__ as g
            return g
        except Exception:
            return None

    def _get_room_pos(self):
        g = self._get_main()
        return None if g is None else getattr(g, "current_room_pos", None)

    def _get_shake_offset(self):
        g = self._get_main()
        if g is None: return 0, 0
        return getattr(g, "shake_offset_x", 0), getattr(g, "shake_offset_y", 0)

    def _world_to_screen(self, wx, wy):
        cx, cy = config.player_rect.centerx, config.player_rect.centery
        px, py = self.get_player_world_position()
        sx = cx + (wx - px); sy = cy + (wy - py)
        ox, oy = self._get_shake_offset()
        return (sx + ox, sy + oy)

    def _unit_from_mouse(self):
        mx, my = pygame.mouse.get_pos()
        dx = mx - config.player_rect.centerx
        dy = my - config.player_rect.centery
        ang = math.atan2(dy, dx)
        return (math.cos(ang), math.sin(ang)), ang

    def _enemies(self):
        return getattr(config, "all_enemies", getattr(config, "enemies", []))

    def _all_obstacles(self):
        om = getattr(config, "obstacle_manager", None)
        if not om: return []
        return list(getattr(om, "placed_obstacles", [])) + \
               list(getattr(om, "static_obstacles", [])) + \
               list(getattr(om, "combat_obstacles", []))

    def _collides_obstacle_circle(self, x, y, r):
        # 오브는 벽/장애물에 닿으면 소멸(관통 X)
        for obs in self._all_obstacles():
            for c in getattr(obs, "colliders", []):
                if getattr(c, "bullet_passable", False):
                    continue
                try:
                    if hasattr(c, "check_collision_circle"):
                        if c.check_collision_circle((x, y), r, (obs.world_x, obs.world_y)):
                            return True
                    elif hasattr(c, "compute_penetration_circle"):
                        pen = c.compute_penetration_circle((x, y), r, (obs.world_x, obs.world_y))
                        if pen:
                            return True
                except Exception:
                    return True
        return False

    def _damage_enemy(self, e, dmg, hit_type="bfg"):
        try:
            if hasattr(e, "on_hit"):
                e.on_hit(dmg, knockback=5, hit_type=hit_type)
            elif hasattr(e, "hit"):
                e.hit(dmg, None)
            else:
                e.hp = getattr(e, "hp", 0) - dmg
                if e.hp <= 0:
                    e.alive = False
        except Exception:
            pass

    def _apply_aoe_damage(self, x, y, radius, damage, hit_type="bfg_aoe"):
        r2 = radius*radius
        for e in list(self._enemies()):
            if not getattr(e, "alive", False): continue
            ex = getattr(e, "world_x", getattr(e, "x", None))
            ey = getattr(e, "world_y", getattr(e, "y", None))
            if ex is None or ey is None: continue
            rr = max(10, int(getattr(e, "radius", 28)))
            if (ex-x)*(ex-x) + (ey-y)*(ey-y) <= (r2 + rr*rr):
                self._damage_enemy(e, damage, hit_type=hit_type)

    def _play(self, key):
        s = self.sounds.get(key) if hasattr(self, "sounds") else None
        if s:
            try: s.play()
            except Exception: pass

    def _start_loop_if_needed(self):
        # 덩굴손이 최근에 누군가를 때렸다면 루프 사운드 유지, 아니면 중지.
        loop = self.sounds.get("loop") if hasattr(self, "sounds") else None
        if not loop:
            return
        now = self._now()
        active = (now - self._last_vine_dot_ms) <= self.VINE_KEEP_ALIVE_MS
        ch = self._vine_loop_ch
        if active:
            if ch is None or (not ch.get_busy()):
                try:
                    self._vine_loop_ch = loop.play(loops=-1)
                except Exception:
                    self._vine_loop_ch = None
        else:
            if ch is not None:
                try: ch.stop()
                except Exception: pass
                self._vine_loop_ch = None

    def _big_shake(self, strength, ms):
        # 강제 카메라 흔들림(전역 설정 갱신)
        try:
            config.shake_strength = max(getattr(config, "shake_strength", 0), strength)
            config.shake_timer    = max(getattr(config, "shake_timer", 0),    ms)
        except Exception:
            pass
        self.last_shot_time = self._now()

    # 입력/업데이트
    def on_update(self, left_down, right_down):
        now = self._now()

        # 방 이동 시 잔류 오브/FX 정리
        self._check_room_transition_clear()

        # 공통 필터
        l_allow, _ = self._filter_inputs(left_down, right_down)

        # 엣지(클릭 순간) 없이도, 'idle' 상태이며 쿨타임이 지났고 탄이 있으면 차지 시작
        if l_allow and self._state == "idle" and now >= self._next_left_ms:
            if self.get_ammo_gauge() >= self.LEFT_AMMO_COST:
                self.reduce_ammo(self.LEFT_AMMO_COST)
                # 차지 시작: 사운드 즉시 재생(요구사항), 쿨타임 타이머는 시작 시점을 기준으로 설정
                self._charge_start_ms = now
                self._state = "charging"
                self._play("fire")
                self._next_left_ms = now + self.LEFT_COOLDOWN_MS

        self._prev_left = l_allow

        # 차지 중 이동속도 50% 감소
        if self._state == "charging":
            # 매 프레임 slow_until_ms 갱신하여 안정적으로 유지
            try:
                config.move_slow_factor = 0.5
                config.slow_until_ms = now + 60  # 다음 프레임 전까지 유지
            except Exception:
                pass

            if now - self._charge_start_ms >= self.CHARGE_TIME_MS:
                # 현재 마우스 방향으로 오브 생성
                (ux, uy), _ = self._unit_from_mouse()
                self._fire_orb_with_dir(ux, uy)
                self._state = "idle"
                self._big_shake(self.FIRE_SHAKE_STRENGTH, self.FIRE_SHAKE_MS)

        # 오브 갱신(비행/충돌/덩굴손) + 스파클 입자
        self._update_orbs_and_vines()

        # FX 수명 관리 & 루프음 상태 갱신
        self._expire_fx()
        self._start_loop_if_needed()

    # 발사/오브 로직
    def _muzzle_position_from_dir(self, ux, uy):
        px, py = self.get_player_world_position()
        return (px + ux * (30 * config.PLAYER_VIEW_SCALE),
                py + uy * (30 * config.PLAYER_VIEW_SCALE))

    def _fire_orb_with_dir(self, ux, uy):
        # 차지 종료 ‘현재 방향’으로 오브 발사.
        mx, my = self._muzzle_position_from_dir(ux, uy)
        self._orbs.append({
            "x": mx, "y": my,
            "vx": ux * self.ORB_SPEED, "vy": uy * self.ORB_SPEED,
            "born_ms": self._now(),
            "trail": [(mx, my)],
            "next_vine_tick": self._now(),
        })

    def _update_orbs_and_vines(self):
        if not self._orbs:
            return

        now = self._now()
        i = 0
        while i < len(self._orbs):
            o = self._orbs[i]

            # 이동
            o["x"] += o["vx"]; o["y"] += o["vy"]

            # 잔상
            tr = o["trail"]; tr.append((o["x"], o["y"]))
            if len(tr) > self.TRAIL_MAX_POINTS: tr.pop(0)

            # 스파클 입자 생성
            self._spawn_sparkles(o["x"], o["y"])

            # 적과의 충돌(직격 우선 판정)
            collided_enemy = None
            for e in self._enemies():
                if not getattr(e, "alive", False): continue
                ex = getattr(e, "world_x", getattr(e, "x", None))
                ey = getattr(e, "world_y", getattr(e, "y", None))
                if ex is None or ey is None: continue
                rr = max(10, int(getattr(e, "radius", 28)))
                if (ex - o["x"])**2 + (ey - o["y"])**2 <= (rr + self.ORB_RADIUS)**2:
                    collided_enemy = e
                    break

            if collided_enemy is not None:
                # 직격 피해 + 충격파 + 연출
                self._damage_enemy(collided_enemy, self.ORB_DIRECT_DAMAGE, hit_type="bfg_direct")
                self._apply_aoe_damage(o["x"], o["y"], self.SHOCKWAVE_RADIUS, self.SHOCKWAVE_DAMAGE, hit_type="bfg_shock")
                self._spawn_impact(o["x"], o["y"])
                self._screen_tint()
                self._play("explosion")
                self._orbs.pop(i)
                self._big_shake(self.HIT_SHAKE_STRENGTH, self.HIT_SHAKE_MS)
                continue

            # 벽/장애물 충돌 시: 오브 소멸 + 충격파
            if self._collides_obstacle_circle(o["x"], o["y"], self.ORB_RADIUS):
                self._apply_aoe_damage(o["x"], o["y"], self.SHOCKWAVE_RADIUS, self.SHOCKWAVE_DAMAGE, hit_type="bfg_shock")
                self._spawn_impact(o["x"], o["y"])
                self._screen_tint()
                self._play("explosion")
                self._orbs.pop(i)
                self._big_shake(self.HIT_SHAKE_STRENGTH, self.HIT_SHAKE_MS)
                continue

            # 덩굴손 DOT(벽 무시): 사거리 내 적들에게 주기적으로 피해
            if now >= o["next_vine_tick"]:
                o["next_vine_tick"] = now + self.VINE_TICK_MS
                candidates = []
                for e in self._enemies():
                    if not getattr(e, "alive", False): continue
                    ex = getattr(e, "world_x", getattr(e, "x", None))
                    ey = getattr(e, "world_y", getattr(e, "y", None))
                    if ex is None or ey is None: continue
                    dist2 = (ex - o["x"])**2 + (ey - o["y"])**2
                    if dist2 <= self.VINE_RANGE * self.VINE_RANGE:
                        candidates.append((dist2, e))
                candidates.sort(key=lambda t: t[0])
                hit_any = False
                for _, e in candidates[:self.VINE_MAX_TARGETS]:
                    self._damage_enemy(e, self.VINE_DAMAGE_PER_TICK, hit_type="bfg_vine")
                    hit_any = True
                if hit_any:
                    self._last_vine_dot_ms = now

            i += 1

    # FX/사운드 보조
    def _spawn_impact(self, x, y):
        self._impact_rings.append({"x": x, "y": y, "until": self._now() + self.IMPACT_RING_MS})

    def _screen_tint(self):
        self._tint_until = self._now() + self.TINT_DURATION_MS

    def _spawn_sparkles(self, x, y):
        # 오브 비행 중 스파클 입자 생성.
        rnd = self._rng
        if len(self._sparkles) > self.MAX_SPARKS:
            return
        count = min(self.SPARK_RATE_PER_ORB, self.MAX_SPARKS - len(self._sparkles))
        for _ in range(count):
            ang = rnd.random() * 2 * math.pi
            spd = rnd.uniform(self.SPARK_SPEED_MIN, self.SPARK_SPEED_MAX)
            vx = math.cos(ang) * spd
            vy = math.sin(ang) * spd
            self._sparkles.append({
                "x": x + rnd.uniform(-4, 4),
                "y": y + rnd.uniform(-4, 4),
                "vx": vx, "vy": vy,
                "born_ms": self._now(),
                "ttl": self.SPARK_TTL_MS
            })

    def _expire_fx(self):
        now = self._now()
        self._impact_rings[:] = [r for r in self._impact_rings if now <= r["until"]]
        # 스파클 소멸/이동/감쇠
        kept = []
        for p in self._sparkles:
            p["x"] += p["vx"]; p["y"] += p["vy"]
            if now - p["born_ms"] < p["ttl"]:
                kept.append(p)
        self._sparkles = kept
        # 틴트는 시간 기반 감쇠 → 메인 렌더에서만 알파 계산

    def _check_room_transition_clear(self):
        cur = self._get_room_pos()
        if cur is None: return
        if getattr(self, "_last_room_pos", None) is None:
            self._last_room_pos = cur
            return
        if cur != self._last_room_pos:
            # 오브/FX/사운드 정리
            self._orbs.clear()
            self._impact_rings.clear()
            self._tint_until = 0
            self._sparkles.clear()
            if self._vine_loop_ch is not None:
                try: self._vine_loop_ch.stop()
                except Exception: pass
                self._vine_loop_ch = None
            self._state = "idle"
            self._last_room_pos = cur

    # 렌더링
    def draw_overlay(self, screen):
        sw, sh = screen.get_size()
        now = self._now()

        # 차지 섬광(0.8초) — 총구에서 펄스
        if self._state == "charging":
            layer = pygame.Surface((sw, sh), pygame.SRCALPHA)
            (dux, duy), dang = self._unit_from_mouse()
            mx, my = self._muzzle_position_from_dir(dux, duy)
            sx, sy = self._world_to_screen(mx, my)
            t = (now - self._charge_start_ms) / float(self.CHARGE_TIME_MS)
            t = max(0.0, min(1.0, t))
            # 반경/알파가 사인파로 출렁이도록
            rad = int(24 + 18 * (1.0 + math.sin(t * math.pi * 3)) * 0.5)
            alpha_inner = 90 + int(80 * t)
            alpha_ring  = 140 + int(70 * t)
            pygame.draw.circle(layer, (140, 255, 210, alpha_inner), (int(sx), int(sy)), int(rad*0.6))
            pygame.draw.circle(layer, (120, 240, 230, alpha_ring), (int(sx), int(sy)), rad, width=3)
            # 총구 방향 라이트 콘(짧은 부채꼴)
            spread = math.radians(28)
            a0 = dang - spread*0.5; a1 = dang + spread*0.5
            length = 70
            pts = [(sx, sy)]
            for i in range(8+1):
                a = a0 + (a1-a0) * (i/8.0)
                pts.append((sx + math.cos(a)*length, sy + math.sin(a)*length))
            pygame.draw.polygon(layer, (120, 255, 230, 60), [(int(x), int(y)) for (x,y) in pts])
            screen.blit(layer, (0,0))

        # 오브/덩굴손/잔상/스파클
        if self._orbs or self._sparkles:
            s = pygame.Surface((sw, sh), pygame.SRCALPHA)

            # 오브들
            for orb in self._orbs:
                # 잔상
                if len(orb["trail"]) >= 2:
                    pts = [self._world_to_screen(x, y) for (x, y) in orb["trail"]]
                    for i in range(1, len(pts)):
                        a = int(140 * (i / len(pts)))
                        pygame.draw.line(s, (120, 240, 255, a),
                                         (int(pts[i-1][0]), int(pts[i-1][1])),
                                         (int(pts[i][0]),   int(pts[i][1])), 3)

                # 오브 본체(핵 + 링)
                sx, sy = self._world_to_screen(orb["x"], orb["y"])
                core_r = int(self.ORB_RADIUS * 0.7)
                pygame.draw.circle(s, (160, 255, 210, 240), (int(sx), int(sy)), core_r)
                pygame.draw.circle(s, (120, 240, 230, 220), (int(sx), int(sy)), self.ORB_RADIUS, width=3)

                # 덩굴손(가까운 적 최대 N) — 벽 무시, 지그재그 폴리라인
                targets = []
                for e in self._enemies():
                    if not getattr(e, "alive", False): continue
                    ex = getattr(e, "world_x", getattr(e, "x", None))
                    ey = getattr(e, "world_y", getattr(e, "y", None))
                    if ex is None or ey is None: continue
                    d2 = (ex - orb["x"])**2 + (ey - orb["y"])**2
                    if d2 <= self.VINE_RANGE * self.VINE_RANGE:
                        targets.append((d2, e, ex, ey))
                targets.sort(key=lambda t: t[0])
                for k, (_, e, ex, ey) in enumerate(targets[:self.VINE_MAX_TARGETS]):
                    self._draw_vine(s, orb["x"], orb["y"], ex, ey, seed=(k*9173 + now//33))

            # 스파클 렌더(알파 감쇠되는 작은 점)
            for p in self._sparkles:
                sx, sy = self._world_to_screen(p["x"], p["y"])
                life = now - p["born_ms"]
                t = max(0.0, min(1.0, life / float(p["ttl"])))
                alpha = int(200 * (1.0 - t))
                r = 2 if t < 0.6 else 1
                pygame.draw.circle(s, (190, 255, 220, alpha), (int(sx), int(sy)), r)

            screen.blit(s, (0,0))

        # 히트 링 FX
        if self._impact_rings:
            fx = pygame.Surface((sw, sh), pygame.SRCALPHA)
            for r in self._impact_rings:
                sx, sy = self._world_to_screen(r["x"], r["y"])
                t = 1.0 - (r["until"] - now) / float(self.IMPACT_RING_MS)
                t = max(0.0, min(1.0, t))
                rad = int(18 + 90 * t)
                alpha = int(220 * (1.0 - t))
                pygame.draw.circle(fx, (160, 255, 210, max(50, alpha//2)), (int(sx), int(sy)), int(rad*0.55))
                pygame.draw.circle(fx, (200, 255, 230, alpha), (int(sx), int(sy)), rad, width=3)
            screen.blit(fx, (0,0))

        # 화면 틴트(히트 시 잠깐 초록빛)
        if now < self._tint_until:
            left = (self._tint_until - now) / float(self.TINT_DURATION_MS)
            alpha = int(self.TINT_MAX_ALPHA * max(0.0, min(1.0, left)))
            tint = pygame.Surface((sw, sh), pygame.SRCALPHA)
            tint.fill((90, 220, 180, alpha))
            screen.blit(tint, (0,0))

    # 렌더 보조(덩굴손)
    def _draw_vine(self, surf, x0, y0, x1, y1, seed):
        # 오브 ↔ 적 사이 지그재그 전기줄(폴리라인).
        sx0, sy0 = self._world_to_screen(x0, y0)
        sx1, sy1 = self._world_to_screen(x1, y1)
        dx, dy = sx1 - sx0, sy1 - sy0
        dist = math.hypot(dx, dy)
        if dist <= 1: return
        ux, uy = dx / dist, dy / dist
        ortx, orty = -uy, ux

        rnd = self._rng
        rnd.seed(int(seed) & 0x7fffffff)

        # 세그먼트 포인트 생성(중간점에 노이즈 오프셋)
        pts = [(sx0, sy0)]
        for i in range(1, self.VINE_SEGMENTS):
            t = i / float(self.VINE_SEGMENTS)
            base_x = sx0 + dx * t
            base_y = sy0 + dy * t
            # 중심부일수록 오프셋 크게(양끝은 작게)
            mag = (0.5 - abs(t - 0.5)) * 1.6
            off = (6 + 10 * mag) * (0.6 + 0.8 * rnd.random())
            # 좌우 랜덤
            sign = -1 if rnd.random() < 0.5 else 1
            px = base_x + ortx * off * sign
            py = base_y + orty * off * sign
            pts.append((px, py))
        pts.append((sx1, sy1))

        # 외곽 글로우(굵은 라인, 낮은 알파) + 내부 라인(얇은 라인, 높은 알파)
        for w, a in ((5, 90), (3, 160), (1, 220)):
            pygame.draw.lines(surf, (120, 255, 230, a), False, [(int(x), int(y)) for (x,y) in pts], w)

        # 스파크 몇 개
        for _ in range(2):
            t = rnd.random()
            bx = sx0 + dx * t; by = sy0 + dy * t
            ox = ortx * (rnd.random()*8 - 4)
            oy = orty * (rnd.random()*8 - 4)
            pygame.draw.circle(surf, (200, 255, 230, 200), (int(bx+ox), int(by+oy)), 2)

    # 내부 처리 보조
    def _check_room_transition_clear(self):
        cur = self._get_room_pos()
        if cur is None: return
        if getattr(self, "_last_room_pos", None) is None:
            self._last_room_pos = cur
            return
        if cur != self._last_room_pos:
            # 오브/FX/사운드 정리
            self._orbs.clear()
            self._impact_rings.clear()
            self._tint_until = 0
            self._sparkles.clear()
            if self._vine_loop_ch is not None:
                try: self._vine_loop_ch.stop()
                except Exception: pass
                self._vine_loop_ch = None
            self._state = "idle"
            self._last_room_pos = cur

WEAPON_CLASSES = [Gun1, Gun2, Gun3, Gun4, Gun5, Gun6, Gun7, Gun8, Gun9, Gun10,
                  Gun11, Gun12, Gun13, Gun14, Gun15, Gun16, Gun17, Gun18, Gun19, Gun20,
                  Gun21, Gun22, Gun23, Gun24, Gun25, Gun26, Gun27, Gun28, Gun29, Gun30,
                  Gun31, Gun32, Gun33, Gun34, Gun35, Gun36, Gun37, Gun38]