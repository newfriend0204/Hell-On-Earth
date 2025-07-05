import pygame
import os
from config import ASSET_DIR, BG_WIDTH, BG_HEIGHT

def load_images():
    path_image = lambda *paths: os.path.join(ASSET_DIR, *paths)

    player_img = pygame.image.load(path_image("image", "MainCharacter.png")).convert_alpha()
    player_img = pygame.transform.scale(player_img, (90, 90))

    gun1_img = pygame.image.load(path_image("image", "Gun1.png")).convert_alpha()
    gun1_img = pygame.transform.rotate(gun1_img, 180)
    desired_gun_width = 30
    scale_factor = desired_gun_width / gun1_img.get_width()
    new_gun_size = (int(gun1_img.get_width() * scale_factor), int(gun1_img.get_height() * scale_factor))
    gun1_img = pygame.transform.smoothscale(gun1_img, new_gun_size)

    gun2_img = pygame.image.load(path_image("image", "Testgun2.png")).convert_alpha()

    bullet_img = pygame.image.load(path_image("image", "Bullet.png")).convert_alpha()
    cursor_img = pygame.image.load(path_image("image", "MouseCursor.png")).convert_alpha()
    bg_img = pygame.image.load(path_image("image", "TestField.png")).convert()

    bg_img = pygame.transform.scale(bg_img, (BG_WIDTH, BG_HEIGHT))
    cursor_img = pygame.transform.scale(cursor_img, (32, 32))

    return {
        "player": player_img,
        "gun1": gun1_img,
        "gun2": gun2_img,
        "bullet": bullet_img,
        "cursor": cursor_img,
        "background": bg_img
    }
