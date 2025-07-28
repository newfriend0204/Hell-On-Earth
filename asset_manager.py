import pygame
import os
from config import *

def load_images():
    path_image = lambda *paths: os.path.join(ASSET_DIR, *paths)

    player_img = pygame.image.load(path_image("image", "character", "MainCharacter.png")).convert_alpha()
    player_img = pygame.transform.smoothscale(player_img, (90, 90))

    gun1_img = pygame.image.load(path_image("image", "Gun", "Gun1Player.png")).convert_alpha()
    gun1_img = pygame.transform.smoothscale(gun1_img, (30, int(gun1_img.get_height() * (30 / gun1_img.get_width()))))

    gun2_img = pygame.image.load(path_image("image", "Gun", "Gun2Player.png")).convert_alpha()
    gun2_img = pygame.transform.smoothscale(gun2_img, (60, int(gun2_img.get_height() * (60 / gun2_img.get_width()))))

    gun3_img = pygame.image.load(path_image("image", "Gun", "Gun3Player.png")).convert_alpha()
    gun3_img = pygame.transform.smoothscale(gun3_img, (70, int(gun3_img.get_height() * (70 / gun3_img.get_width()))))

    gun4_img = pygame.image.load(path_image("image", "Gun", "Gun4Player.png")).convert_alpha()
    gun4_img = pygame.transform.smoothscale(gun4_img, (60, int(gun4_img.get_height() * (60 / gun4_img.get_width()))))

    gun5_img = pygame.image.load(path_image("image", "Gun", "Gun5Player.png")).convert_alpha()
    gun5_img = pygame.transform.smoothscale(gun5_img, (65, int(gun5_img.get_height() * (65 / gun5_img.get_width()))))

    gun6_img = pygame.image.load(path_image("image", "Gun", "Gun6Player.png")).convert_alpha()
    gun6_img = pygame.transform.smoothscale(gun6_img, (55, int(gun6_img.get_height() * (55 / gun6_img.get_width()))))

    gun7_img = pygame.image.load(path_image("image", "Gun", "Gun7Player.png")).convert_alpha()
    gun7_img = pygame.transform.smoothscale(gun7_img, (80, int(gun7_img.get_height() * (80 / gun7_img.get_width()))))

    gun8_img = pygame.image.load(path_image("image", "Gun", "Gun8Player.png")).convert_alpha()
    gun8_img = pygame.transform.smoothscale(gun8_img, (50, int(gun8_img.get_height() * (50 / gun8_img.get_width()))))

    warhead_img = pygame.image.load(path_image("image", "Gun", "Warhead1.png")).convert_alpha()
    warhead_img = pygame.transform.smoothscale(warhead_img, (40, 40))

    grenade_img = pygame.image.load(path_image("image", "Gun", "LauncherGrenade1.png")).convert_alpha()
    grenade_img = pygame.transform.smoothscale(grenade_img, (30, 30))

    explosion_img = pygame.image.load(path_image("image", "Gun", "LauncherGrenade1Explosion.png")).convert_alpha()
    explosion_img = pygame.transform.smoothscale(explosion_img, (200, 200))

    bullet1_img = pygame.image.load(path_image("image", "Gun", "Bullet1.png")).convert_alpha()
    desired_width = 60
    scale_factor = desired_width / bullet1_img.get_width()
    bullet1_img = pygame.transform.smoothscale(
        bullet1_img,
        (
            int(bullet1_img.get_width() * scale_factor),
            int(bullet1_img.get_height() * scale_factor)
        )
    )

    enemy_bullet_img = bullet1_img.copy()
    enemy_bullet_img.fill((255, 0, 0, 255), special_flags=pygame.BLEND_RGBA_MULT)

    cartridge_case_img = pygame.image.load(path_image("image", "Gun", "CartridgeCase1.png")).convert_alpha()
    cartridge_case_img = pygame.transform.smoothscale(
        cartridge_case_img,
        (5, int(cartridge_case_img.get_height() * 5 / cartridge_case_img.get_width()))
    )

    cursor_img = pygame.image.load(path_image("image", "MouseCursor.png")).convert_alpha()
    cursor_img = pygame.transform.smoothscale(cursor_img, (32, 32))

    bg_img = pygame.image.load(path_image("Image", "Map1.png")).convert()
    bg_img = pygame.transform.smoothscale(bg_img, (BG_WIDTH, BG_HEIGHT))

    wall_barrier_img = pygame.image.load(path_image("Image", "Map1Wall.png")).convert_alpha()
    scale_factor = 0.275 * PLAYER_VIEW_SCALE
    wall_barrier_img = pygame.transform.smoothscale(wall_barrier_img, (
        int(wall_barrier_img.get_width() * scale_factor),
        int(wall_barrier_img.get_height() * scale_factor)
    ))
    wall_barrier_img_rotated = pygame.transform.rotate(wall_barrier_img, 90)

    obstacle_sizes = {
        "Pond1.png": (1536, 1024),
        "Pond2.png": (1536, 1024),
        "Rock1.png": (1536, 1024),
        "Rock2.png": (1024, 1024),
        "Rock3.png": (1536, 1024),
        "Tree1.png": (1024, 1024),
        "Tree2.png": (1024, 1024),
        "FallenLog1.png": (1024, 1536),
        "FallenLog2.png": (1536, 1024),
        "TreeStump.png": (1024, 1024),
    }

    obstacle_dir = path_image("Image", "Obstacle")
    obstacle_images = {}
    obstacle_masks = {}

    if os.path.exists(obstacle_dir):
        for filename in os.listdir(obstacle_dir):
            if filename in obstacle_sizes:
                img_path = os.path.join(obstacle_dir, filename)
                image = pygame.image.load(img_path).convert_alpha()
                image = pygame.transform.smoothscale(image, obstacle_sizes[filename])
                obstacle_images[filename] = image
                obstacle_masks[filename] = pygame.mask.from_surface(image)

    enemy1_img = pygame.image.load(path_image("image", "character", "Enemy1.png")).convert_alpha()
    enemy1_img = pygame.transform.smoothscale(enemy1_img, (90, 90))

    enemy2_img = pygame.image.load(path_image("image", "character", "Enemy2.png")).convert_alpha()
    enemy2_img = pygame.transform.smoothscale(enemy2_img, (90, 90))

    ammo_gauge_up_img = pygame.image.load(path_image("Image", "AmmoGaugeUp.png")).convert_alpha()
    ammo_gauge_up_img = pygame.transform.smoothscale(ammo_gauge_up_img, (16, 16))
    health_up_img = pygame.image.load(path_image("Image", "HealthUp.png")).convert_alpha()
    health_up_img = pygame.transform.smoothscale(health_up_img, (16, 16))

    return {
        "player": player_img,
        "gun1": gun1_img,
        "gun2": gun2_img,
        "gun3": gun3_img,
        "gun4": gun4_img,
        "gun5": gun5_img,
        "gun6": gun6_img,
        "gun7": gun7_img,
        "gun8": gun8_img,
        "bullet1": bullet1_img,
        "grenade1": grenade_img,
        "warhead1": warhead_img,
        "explosion1": explosion_img,
        "cartridge_case1": cartridge_case_img,
        "enemy_bullet": enemy_bullet_img,
        "enemy1": enemy1_img,
        "enemy2": enemy2_img,
        "ammo_gauge_up": ammo_gauge_up_img,
        "health_up": health_up_img,
        "cursor": cursor_img,
        "background": bg_img,
        "obstacles": obstacle_images,
        "obstacle_masks": obstacle_masks,
        "wall_barrier": wall_barrier_img,
        "wall_barrier_rotated": wall_barrier_img_rotated,
    }

def load_weapon_assets(images):
    weapons = {
        "gun1": {
            "front": pygame.image.load(os.path.join(ASSET_DIR, "image", "Gun", "Gun1.png")).convert_alpha(),
            "topdown": images["gun1"],
            "bullets": [images["bullet1"]],
            "cartridges": [images["cartridge_case1"]],
        },
        "gun2": {
            "front": pygame.image.load(os.path.join(ASSET_DIR, "image", "Gun", "Gun2.png")).convert_alpha(),
            "topdown": images["gun2"],
            "bullets": [images["bullet1"]],
            "cartridges": [images["cartridge_case1"]],
        },
        "gun3": {
            "front": pygame.image.load(os.path.join(ASSET_DIR, "image", "Gun", "Gun3.png")).convert_alpha(),
            "topdown": images["gun3"],
            "bullets": [images["bullet1"]],
            "cartridges": [images["cartridge_case1"]],
        },
        "gun4": {
            "front": pygame.image.load(os.path.join(ASSET_DIR, "image", "Gun", "Gun4.png")).convert_alpha(),
            "topdown": images["gun4"],
            "bullets": [images["grenade1"]],
            "cartridges": [],
            "grenade": images["grenade1"],
            "explosion": images["explosion1"],
        },
        "gun5": {
            "front": pygame.image.load(os.path.join(ASSET_DIR, "image", "Gun", "Gun5.png")).convert_alpha(),
            "topdown": images["gun5"],
            "bullets": [pygame.transform.smoothscale(
                images["bullet1"],
                (images["bullet1"].get_width() // 2, images["bullet1"].get_height() // 2)
            )],
            "cartridges": [images["cartridge_case1"]],
        },
        "gun6": {
            "front": pygame.image.load(os.path.join(ASSET_DIR, "image", "Gun", "Gun6.png")).convert_alpha(),
            "topdown": images["gun6"],
            "bullets": [images["bullet1"]],
            "cartridges": [images["cartridge_case1"]],
            "grenade": images["grenade1"],
            "explosion": images["explosion1"],
        },
        "gun7": {
            "front": pygame.image.load(os.path.join(ASSET_DIR, "image", "Gun", "Gun7.png")).convert_alpha(),
            "topdown": images["gun7"],
            "bullets": [images["bullet1"]],
            "cartridges": [images["cartridge_case1"]],
        },
        "gun8": {
            "front": pygame.image.load(os.path.join(ASSET_DIR, "image", "Gun", "Gun8.png")).convert_alpha(),
            "topdown": images["gun8"],
            "bullets": [images["warhead1"]],
            "cartridges": [],
            "grenade": images["warhead1"],
            "explosion": images["explosion1"],
        },
    }
    return weapons