import pygame
import os
from config import *

def load_images():
    path_image = lambda *paths: os.path.join(ASSET_DIR, *paths)

    player_img = pygame.image.load(path_image("image", "character", "MainCharacter.png")).convert_alpha()
    player_img = pygame.transform.smoothscale(player_img, (90, 90))

    gun1_img = pygame.image.load(path_image("image", "Gun", "Gun1Player.png")).convert_alpha()
    gun1_img = pygame.transform.rotate(gun1_img, 180)
    desired_gun1_width = 30
    scale_factor1 = desired_gun1_width / gun1_img.get_width()
    gun1_img = pygame.transform.smoothscale(gun1_img, (int(gun1_img.get_width() * scale_factor1), int(gun1_img.get_height() * scale_factor1)))

    gun2_img = pygame.image.load(path_image("image", "Gun", "Gun2Player.png")).convert_alpha()
    gun2_img = pygame.transform.rotate(gun2_img, 180)
    desired_gun2_width = 50
    scale_factor2 = desired_gun2_width / gun2_img.get_width()
    gun2_img = pygame.transform.smoothscale(gun2_img, (int(gun2_img.get_width() * scale_factor2), int(gun2_img.get_height() * scale_factor2)))

    gun3_img = pygame.image.load(path_image("image", "Gun", "Gun3Player.png")).convert_alpha()
    gun3_img = pygame.transform.rotate(gun3_img, 180)
    desired_gun3_width = 60
    scale_factor3 = desired_gun3_width / gun3_img.get_width()
    gun3_img = pygame.transform.smoothscale(gun3_img, (int(gun3_img.get_width() * scale_factor3), int(gun3_img.get_height() * scale_factor3)))

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

    cartridge_case_img = pygame.image.load(path_image("image", "Gun", "CartridgeCase1.png")).convert_alpha()
    desired_width = 5
    scale_factor = desired_width / cartridge_case_img.get_width()
    cartridge_case_img = pygame.transform.smoothscale(
        cartridge_case_img,
        (
            int(cartridge_case_img.get_width() * scale_factor),
            int(cartridge_case_img.get_height() * scale_factor)
        )
    )

    enemy_bullet_img = bullet1_img.copy()
    enemy_bullet_img.fill((255, 0, 0, 255), special_flags=pygame.BLEND_RGBA_MULT)

    cursor_img = pygame.image.load(path_image("image", "MouseCursor.png")).convert_alpha()
    bg_img = pygame.image.load(path_image("Image", "Map1.png")).convert()
    bg_img = pygame.transform.smoothscale(bg_img, (BG_WIDTH, BG_HEIGHT))
    cursor_img = pygame.transform.smoothscale(cursor_img, (32, 32))

    wall_barrier_img = pygame.image.load(path_image("Image", "Map1Wall.png")).convert_alpha()
    scale_factor = 0.275 * PLAYER_VIEW_SCALE
    scaled_width = int(wall_barrier_img.get_width() * scale_factor)
    scaled_height = int(wall_barrier_img.get_height() * scale_factor)

    wall_barrier_img = pygame.transform.smoothscale(
        wall_barrier_img,
        (scaled_width, scaled_height)
    )

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
        "TreeStump.png" : (1024, 1024),
    }

    obstacle_dir = path_image("Image", "Obstacle")
    obstacle_images = {}
    obstacle_masks = {}

    if os.path.exists(obstacle_dir):
        for filename in os.listdir(obstacle_dir):
            if filename in obstacle_sizes:
                img_path = os.path.join(obstacle_dir, filename)
                image = pygame.image.load(img_path).convert_alpha()
                new_size = obstacle_sizes[filename]
                image = pygame.transform.smoothscale(image, new_size)
                mask = pygame.mask.from_surface(image)
                obstacle_images[filename] = image
                obstacle_masks[filename] = mask

    enemy1_img = pygame.image.load(path_image("image", "character", "Enemy1.png")).convert_alpha()
    enemy1_img = pygame.transform.smoothscale(enemy1_img, (90, 90))

    enemy2_img = pygame.image.load(path_image("image", "character", "Enemy2.png")).convert_alpha()
    enemy2_img = pygame.transform.smoothscale(enemy2_img, (90, 90))

    return {
        "player": player_img,
        "gun1": gun1_img,
        "gun2": gun2_img,
        "gun3": gun3_img,
        "bullet1": bullet1_img,
        "cartridge_case1": cartridge_case_img,
        "enemy_bullet": enemy_bullet_img,
        "enemy1": enemy1_img,
        "enemy2": enemy2_img,
        "cursor": cursor_img,
        "background": bg_img,
        "obstacles": obstacle_images,
        "obstacle_masks": obstacle_masks,
        "wall_barrier": wall_barrier_img,
        "wall_barrier_rotated": wall_barrier_img_rotated,
    }
