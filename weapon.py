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
    TIER = 3
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
    TIER = 3
    AMMO_COST = 8
    DAMAGE = 80
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
            get_player_world_position_fn=get_player_world_position
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
        now = pygame.time.get_ticks()

        if self.can_left_click and mouse_left_down and now - self.last_shot_time >= self.fire_delay:
            if self.get_ammo_gauge() >= self.left_click_ammo_cost:
                self.on_left_click()
                self.last_shot_time = now

        if self.can_right_click and mouse_right_down and now - self.last_right_click_time >= self.RIGHT_FIRE_DELAY:
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
    TIER = 3
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

WEAPON_CLASSES = [Gun1, Gun2, Gun3, Gun4, Gun5, Gun6, Gun7, Gun8, Gun9, Gun10,
                  Gun11, Gun12, Gun13, Gun14, Gun15, Gun16, Gun17, Gun18, Gun19, Gun20]