import pygame
import random
import math
from entities import Bullet, ScatteredBullet, ExplosionEffectPersistent
import config

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

    def on_left_click(self):
        # 좌클릭 발사 동작 (하위 클래스에서 구현)
        pass

    def on_right_click(self):
        # 우클릭 발사 동작 (하위 클래스에서 구현)
        pass
    
    def on_update(self, mouse_left_down, mouse_right_down):
        # 매 프레임마다 발사 입력을 처리하는 메서드
        # 발사 지연 시간(fire_delay)을 확인한 뒤 발사 동작 실행
        if self.can_left_click and mouse_left_down and pygame.time.get_ticks() - self.last_shot_time >= self.fire_delay:
            # 탄약이 충분할 때만 발사 및 반동 처리
            if self.get_ammo_gauge() >= self.left_click_ammo_cost:
                self.on_left_click()
                self.last_shot_time = pygame.time.get_ticks()


class Gun1(WeaponBase):
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
            tier=1,
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
            tier=1,
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
    AMMO_COST = 8
    DAMAGE = 8
    FIRE_DELAY = 750
    NUM_BULLETS = 15
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
            tier=2,
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
                scale=1.5
            )
            config.scattered_bullets.append(scatter)

class Gun4(WeaponBase):
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
            tier=3,
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
            tier=2,
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
            tier=3,
            sounds_dict={
                "left_fire": sounds["gun6_leftfire"],
                "right_fire": sounds["gun6_rightfire"],
                "explosion": sounds["gun6_explosion"]
            },
            get_ammo_gauge_fn=ammo_gauge,
            reduce_ammo_fn=consume_ammo,
            bullet_has_trail=False,
            get_player_world_position_fn=get_player_world_position,
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
        # 좌클릭과 우클릭 각각의 쿨타임 관리
        now = pygame.time.get_ticks()

        if self.can_left_click and mouse_left_down and now - self.last_shot_time >= self.fire_delay:
            if self.get_ammo_gauge() >= self.left_click_ammo_cost:
                self.on_left_click()
                self.last_shot_time = now

        if self.can_right_click and mouse_right_down and now - self.last_right_click_time >= self.right_fire_delay:
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
            tier=2,
            sounds_dict={
                "left_fire": sounds["gun7_leftfire"],
                "right_fire": sounds["gun7_rightfire"]
            },
            get_ammo_gauge_fn=ammo_gauge,
            reduce_ammo_fn=consume_ammo,
            bullet_has_trail=True,
            get_player_world_position_fn=get_player_world_position
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
        # 좌/우클릭 각각 쿨타임 체크 후 발사 처리
        now = pygame.time.get_ticks()

        if self.can_left_click and mouse_left_down and now - self.last_shot_time >= self.fire_delay:
            if self.get_ammo_gauge() >= self.left_click_ammo_cost:
                self.on_left_click()
                self.last_shot_time = now

        if self.can_right_click and mouse_right_down and now - self.last_right_click_time >= self.right_fire_delay:
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
                self.cartridge_images[0],
                scale=1.5
            )
            config.scattered_bullets.append(scatter)

class Gun8(WeaponBase):
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
            tier=3,
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
            tier=4,
            sounds_dict={
                "left_fire": sounds["gun9_leftfire"],
                "right_fire": sounds["gun9_rightfire"],
                "explosion": sounds["gun9_explosion"],
            },
            get_ammo_gauge_fn=ammo_gauge,
            reduce_ammo_fn=consume_ammo,
            bullet_has_trail=False,
            get_player_world_position_fn=get_player_world_position
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
        # 좌/우클릭 각각 쿨타임 체크 후 발사 처리
        now = pygame.time.get_ticks()

        if self.can_left_click and mouse_left_down and now - self.last_shot_time >= self.fire_delay:
            if self.get_ammo_gauge() >= self.left_click_ammo_cost:
                self.on_left_click()
                self.last_shot_time = now

        if self.can_right_click and mouse_right_down and now - self.last_right_click_time >= self.right_fire_delay:
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

WEAPON_CLASSES = [Gun1, Gun2, Gun3, Gun4, Gun5, Gun6, Gun7, Gun8, Gun9]