import pygame
import os
from config import ASSET_DIR, GUN1_VOLUME, GUN2_VOLUME, GUN3_FIRE_DELAY

def load_sounds():
    path_sound = lambda *paths: os.path.join(ASSET_DIR, *paths)

    pygame.mixer.set_num_channels(16)

    walk_sound = pygame.mixer.Sound(path_sound("Sound", "ForestWalk.mp3"))
    walk_sound.set_volume(0.3)

    gun1_fire = pygame.mixer.Sound(path_sound("Sound", "Gun1Fire.wav"))
    gun1_fire.set_volume(GUN1_VOLUME)

    gun1_fire_enemy = pygame.mixer.Sound(path_sound("Sound", "Gun1Fire.wav"))
    gun1_fire_enemy.set_volume(0.25)

    gun2_fire = pygame.mixer.Sound(path_sound("Sound", "Gun2Fire.wav"))
    gun2_fire.set_volume(GUN2_VOLUME)

    gun2_fire_enemy = pygame.mixer.Sound(path_sound("Sound", "Gun2Fire.wav"))
    gun2_fire_enemy.set_volume(0.25)

    # ✅ gun3 추가
    gun3_fire = pygame.mixer.Sound(path_sound("Sound", "Gun3Fire.wav"))
    gun3_fire.set_volume(1.0)

    gun3_fire_enemy = pygame.mixer.Sound(path_sound("Sound", "Gun3Fire.wav"))
    gun3_fire_enemy.set_volume(0.25)

    return {
        "walk": walk_sound,
        "gun1_fire": gun1_fire,
        "gun1_fire_enemy": gun1_fire_enemy,
        "gun2_fire": gun2_fire,
        "gun2_fire_enemy": gun2_fire_enemy,
        "gun3_fire": gun3_fire,
        "gun3_fire_enemy": gun3_fire_enemy,
    }
