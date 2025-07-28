import pygame
import random
import math
from entities import Bullet, ScatteredBullet, ExplosionEffectPersistent
import config

class WeaponBase:
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
        pass

    def on_right_click(self):
        pass

    def on_update(self, mouse_left_down, mouse_right_down):
        if self.can_left_click and mouse_left_down and pygame.time.get_ticks() - self.last_shot_time >= self.fire_delay:
            self.on_left_click()
            self.last_shot_time = pygame.time.get_ticks()
        if self.can_right_click and mouse_right_down:
            self.on_right_click()


class Gun1(WeaponBase):
    AMMO_COST = 10
    DAMAGE = 30
    SPREAD = 10
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
            get_ammo_gauge_fn=lambda: ammo_gauge,
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
    AMMO_COST = 7
    DAMAGE = 20
    SPREAD = 10
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
            get_ammo_gauge_fn=lambda: ammo_gauge,
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
    AMMO_COST = 15
    DAMAGE = 10
    FIRE_DELAY = 750
    NUM_BULLETS = 15
    SPREAD_DEGREES = 35

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
            get_ammo_gauge_fn=lambda: ammo_gauge,
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
        self.reduce_ammo(self.left_click_ammo_cost)
        self.sounds["fire"].play()

        mouse_x, mouse_y = pygame.mouse.get_pos()
        player_center_x, player_center_y = self.get_player_world_position()
        angle = math.atan2(mouse_y - config.player_rect.centery, mouse_x - config.player_rect.centerx)

        for _ in range(self.NUM_BULLETS):
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
    AMMO_COST = 30
    DAMAGE_MAX = 80
    DAMAGE_MIN = 10
    SPREAD = 0
    FIRE_DELAY = 1000
    EXPLOSION_RADIUS = 200

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
            get_ammo_gauge_fn=lambda: ammo_gauge,
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
    AMMO_COST = 10
    DAMAGE = 15
    FIRE_INTERVAL = 80
    PREHEAT_DURATION = 1000
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
            get_ammo_gauge_fn=lambda: ammo_gauge,
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
        if self.state == "preheat":
            self.sounds["preheat"].stop()
        elif self.state == "firing":
            self.sounds["fire"].stop()
        elif self.state == "cooldown":
            self.sounds["overheat"].stop()
        self.state = "idle"
        self.speed_penalty = self.base_speed_penalty

class Gun6(WeaponBase):
    LEFT_AMMO_COST = 10
    RIGHT_AMMO_COST = 20
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
            get_ammo_gauge_fn=lambda: ammo_gauge,
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
        now = pygame.time.get_ticks()

        if self.can_left_click and mouse_left_down and now - self.last_shot_time >= self.fire_delay:
            self.on_left_click()
            self.last_shot_time = now

        if self.can_right_click and mouse_right_down and now - self.last_right_click_time >= self.right_fire_delay:
            self.on_right_click()
            self.last_right_click_time = now

    def on_left_click(self):
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
    LEFT_FIRE_DELAY = 110  # 돌격소총: 빠른 연사
    RIGHT_FIRE_DELAY = 700  # 샷건: 느린 발사

    LEFT_AMMO_COST = 5
    RIGHT_AMMO_COST = 15

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
            get_ammo_gauge_fn=lambda: ammo_gauge,
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
        now = pygame.time.get_ticks()

        if self.can_left_click and mouse_left_down and now - self.last_shot_time >= self.fire_delay:
            self.on_left_click()
            self.last_shot_time = now

        if self.can_right_click and mouse_right_down and now - self.last_right_click_time >= self.right_fire_delay:
            self.on_right_click()
            self.last_right_click_time = now

    def on_left_click(self):
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
    NAME = "RPG"
    LEFT_FIRE_DELAY = 1000
    TIER = 3

    @staticmethod
    def create_instance(weapon_assets, sounds, ammo_gauge, consume_ammo, get_player_world_position):
        return Gun8(
            name=Gun8.NAME,
            front_image=weapon_assets["gun8"]["front"],
            topdown_image=weapon_assets["gun8"]["topdown"],
            bullet_image=weapon_assets["gun8"]["bullets"][0],
            explosion_image=weapon_assets["gun8"]["explosion"],
            fire_sound=sounds["gun8_fire"],
            explosion_sound=sounds["gun8_explosion"],
            get_ammo_gauge_fn=ammo_gauge,
            consume_ammo=consume_ammo,
            get_player_world_position=get_player_world_position
        )

    def __init__(self, name, front_image, topdown_image, bullet_image, explosion_image, fire_sound, explosion_sound, get_ammo_gauge_fn, consume_ammo, get_player_world_position):
        self.bullet_image = bullet_image
        self.explosion_image = explosion_image
        self.fire_sound = fire_sound
        self.explosion_sound = explosion_sound
        self.get_ammo_gauge = get_ammo_gauge_fn
        self.consume_ammo = consume_ammo
        self.get_player_world_position = get_player_world_position

        self.left_click_ammo_cost = 40
        self.fire_delay = Gun8.LEFT_FIRE_DELAY
        self.last_shot_time = 0
        self.projectile = None
        self.pending_ready = False
        self.pending_ready_time = 0
        self.ready_to_fire = True

        self.explosion_radius = 300 * config.PLAYER_VIEW_SCALE
        self.damage_center = 120
        self.damage_edge = 50

        self.recoil_strength = 12
        self.speed_penalty = 0.20
        self.distance_from_center = config.PLAYER_VIEW_SCALE * 65
        self.shake_strength = 18

        super().__init__(
            name=name,
            front_image=front_image,
            topdown_image=topdown_image,
            uses_bullets=True,
            bullet_images=[bullet_image],
            uses_cartridges=False,
            cartridge_images=[],
            can_left_click=True,
            can_right_click=False,
            left_click_ammo_cost=self.left_click_ammo_cost,
            right_click_ammo_cost=0,
            tier=Gun8.TIER,
            sounds_dict={"fire": fire_sound},
            get_ammo_gauge_fn=self.get_ammo_gauge,
            reduce_ammo_fn=consume_ammo,
            bullet_has_trail=False,
            get_player_world_position_fn=get_player_world_position
        )

    def on_update(self, mouse_left_down, mouse_right_down):
        now = pygame.time.get_ticks()
        if self.projectile and mouse_left_down:
            self.projectile.follow_mouse = True
        elif self.projectile:
            self.projectile.follow_mouse = False

        if self.projectile is None:
            if self.pending_ready and now >= self.pending_ready_time:
                self.ready_to_fire = True
                self.pending_ready = False

            if self.ready_to_fire and mouse_left_down and now - self.last_shot_time >= self.fire_delay:
                self.on_left_click()
                self.last_shot_time = now
                self.ready_to_fire = False

    def on_left_click(self):
        if self.get_ammo_gauge() < self.left_click_ammo_cost:
            return

        self.consume_ammo(self.left_click_ammo_cost)
        self.fire_sound.play()

        px, py = self.get_player_world_position()
        mx, my = pygame.mouse.get_pos()
        dx = mx - config.SCREEN_WIDTH // 2
        dy = my - config.SCREEN_HEIGHT // 2
        angle = math.atan2(dy, dx)

        speed = 4 * config.PLAYER_VIEW_SCALE
        vx = math.cos(angle) * speed
        vy = math.sin(angle) * speed

        self.projectile = self.GuidedMissile(px, py, vx, vy, angle, self)
        config.global_bullets.append(self.projectile)

    def get_active_projectiles(self):
        return [self.projectile] if self.projectile else []

    class GuidedMissile:
        def __init__(self, x, y, vx, vy, angle, gun):
            self.x = x
            self.y = y
            self.vx = vx
            self.vy = vy
            self.angle = angle
            self.speed = math.hypot(vx, vy)
            self.image = gun.bullet_image
            self.explosion_image = gun.explosion_image
            self.gun = gun
            self.follow_mouse = True
            self.spawn_time = pygame.time.get_ticks()
            self.max_distance = 9999 * config.PLAYER_VIEW_SCALE
            self.travelled = 0
            self.hit = False

        def update(self):
            if self.follow_mouse:
                mx, my = pygame.mouse.get_pos()
                px, py = self.gun.get_player_world_position()
                target_x = px + (mx - config.SCREEN_WIDTH // 2)
                target_y = py + (my - config.SCREEN_HEIGHT // 2)
                dx = target_x - self.x
                dy = target_y - self.y
                angle_to_mouse = math.atan2(dy, dx)
                turn_rate = 0.05
                self.angle += (angle_to_mouse - self.angle) * turn_rate
                self.vx = math.cos(self.angle) * self.speed
                self.vy = math.sin(self.angle) * self.speed

            self.x += self.vx
            self.y += self.vy
            self.travelled += self.speed

            for obs in config.obstacle_manager.static_obstacles + config.obstacle_manager.combat_obstacles:
                for c in obs.colliders:
                    if c.check_collision_circle((self.x, self.y), 15 * config.PLAYER_VIEW_SCALE, (obs.world_x, obs.world_y)):
                        self.explode()
                        return

            for enemy in config.enemies:
                if enemy.alive:
                    dist = math.hypot(enemy.world_x - self.x, enemy.world_y - self.y)
                    if dist <= 15 * config.PLAYER_VIEW_SCALE:
                        self.explode()
                        return

            if self.travelled >= self.max_distance:
                self.explode()

        def explode(self):
            if self.hit:
                return
            self.hit = True
            ex = ExplosionEffectPersistent(self.x, self.y, self.explosion_image, 0.2)
            config.explosions.append(ex)
            self.gun.explosion_sound.play()

            for enemy in config.enemies:
                if enemy.alive:
                    dist = math.hypot(enemy.world_x - self.x, enemy.world_y - self.y)
                    if dist <= self.gun.explosion_radius:
                        damage = self.gun.damage_center if dist < self.gun.explosion_radius * 0.4 else self.gun.damage_edge
                        enemy.hit(damage, config.blood_effects)

            config.global_bullets.remove(self)
            self.gun.projectile = None
            self.gun.pending_ready = True
            self.gun.pending_ready_time = pygame.time.get_ticks() + self.gun.fire_delay

        def draw(self, screen, world_x, world_y):
            screen_x = self.x - world_x
            screen_y = self.y - world_y
            rotated = pygame.transform.rotate(self.image, -math.degrees(self.angle))
            rect = rotated.get_rect(center=(screen_x, screen_y))
            screen.blit(rotated, rect)

WEAPON_CLASSES = [Gun3, Gun2, Gun8, Gun7]