import pygame
import os
from config import ASSET_DIR, BG_WIDTH, BG_HEIGHT

def load_images():
    path_image = lambda *paths: os.path.join(ASSET_DIR, *paths)

    # Player
    player_img = pygame.image.load(path_image("image", "MainCharacter.png")).convert_alpha()
    player_img = pygame.transform.scale(player_img, (90, 90))

    # Guns
    gun1_img = pygame.image.load(path_image("image", "Gun1.png")).convert_alpha()
    gun1_img = pygame.transform.rotate(gun1_img, 180)
    desired_gun_width = 30
    scale_factor = desired_gun_width / gun1_img.get_width()
    new_size = (int(gun1_img.get_width() * scale_factor), int(gun1_img.get_height() * scale_factor))
    gun1_img = pygame.transform.smoothscale(gun1_img, new_size)

    gun2_img = pygame.image.load(path_image("image", "Gun2.png")).convert_alpha()
    gun2_img = pygame.transform.rotate(gun2_img, 180)
    gun2_img = pygame.transform.smoothscale(gun2_img, new_size)

    bullet_img = pygame.image.load(path_image("image", "Bullet.png")).convert_alpha()

    # ✅ Enemy bullet - load and colorize red
    enemy_bullet_img = pygame.image.load(path_image("image", "Bullet.png")).convert_alpha()
    enemy_bullet_img = enemy_bullet_img.copy()
    enemy_bullet_img.fill((255, 0, 0, 255), special_flags=pygame.BLEND_RGBA_MULT)

    cursor_img = pygame.image.load(path_image("image", "MouseCursor.png")).convert_alpha()
    bg_img = pygame.image.load(path_image("Image", "Map1.png")).convert()
    bg_img = pygame.transform.scale(bg_img, (BG_WIDTH, BG_HEIGHT))
    cursor_img = pygame.transform.scale(cursor_img, (32, 32))

    obstacle_sizes = {
        "Pond1.png": (1536, 1024),
        "Pond2.png": (70, 50),
        "Rock1.png": (95, 75),
        "Rock2.png": (70, 50),
        "Rock3.png": (70, 50)
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
                image = pygame.transform.scale(image, new_size)
                mask = pygame.mask.from_surface(image)
                obstacle_images[filename] = image
                obstacle_masks[filename] = mask

    # ✅ Enemy character
    enemy_img = pygame.image.load(path_image("image", "EnemyCharacter.png")).convert_alpha()
    enemy_img = pygame.transform.scale(enemy_img, (90, 90))

    return {
        "player": player_img,
        "gun1": gun1_img,
        "gun2": gun2_img,
        "bullet": bullet_img,
        "enemy_bullet": enemy_bullet_img,
        "enemy": enemy_img,
        "cursor": cursor_img,
        "background": bg_img,
        "obstacles": obstacle_images,
        "obstacle_masks": obstacle_masks,
    }
