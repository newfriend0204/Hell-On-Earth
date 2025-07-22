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
        play_sound_fn,
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
        self.play_sound = play_sound_fn
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

    def on_update(self, mouse_down):
        if mouse_down and pygame.time.get_ticks() - self.last_shot_time >= self.fire_delay:
            self.on_left_click()
            self.last_shot_time = pygame.time.get_ticks()


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
            play_sound_fn=lambda name: sounds[name].play(),
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
        self.play_sound("gun1_fire")

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
        print(f"[DEBUG] Bullet added to config.bullets at ({bullet_x:.1f}, {bullet_y:.1f})")

class Gun2(WeaponBase):
    AMMO_COST = 7
    DAMAGE = 20
    SPREAD = 10
    FIRE_DELAY = 200

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
            play_sound_fn=lambda name: sounds[name].play(),
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
        self.play_sound("gun2_fire")

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
            play_sound_fn=lambda name: sounds[name].play(),
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
        self.play_sound("gun3_fire")

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


WEAPON_CLASSES = [Gun1, Gun2, Gun3]