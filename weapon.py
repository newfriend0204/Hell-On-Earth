import pygame
import random
import math
from entities import Bullet, ScatteredBullet
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
            name="gun1",
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
            name="gun2",
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
            name="gun3",
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
            name="gun4",
            front_image=weapon_assets["gun4"]["front"],
            topdown_image=weapon_assets["gun4"]["topdown"],
            uses_bullets=True,
            bullet_images=weapon_assets["gun4"]["bullets"],
            explosion_image=weapon_assets["explosion1"],
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
            name="gun5",
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
            name="gun6",
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

WEAPON_CLASSES = [Gun3, Gun6, Gun1, Gun2]