import pygame
import os
from config import ASSET_DIR, GUN1_VOLUME, GUN2_VOLUME, WALK_VOLUME

def load_sounds():
    path_sound = lambda *paths: os.path.join(ASSET_DIR, *paths)

    pygame.mixer.set_num_channels(16)  # 채널 충분히 확보

    walk_sound = pygame.mixer.Sound(path_sound("Sound", "ForestWalk.mp3"))
    walk_sound.set_volume(WALK_VOLUME)

    gun1_fire = pygame.mixer.Sound(path_sound("Sound", "Gun1Fire.wav"))
    gun1_fire.set_volume(GUN1_VOLUME)

    gun1_fire_enemy = pygame.mixer.Sound(path_sound("Sound", "Gun1Fire.wav"))
    gun1_fire_enemy.set_volume(0.25)

    gun2_fire = pygame.mixer.Sound(path_sound("Sound", "Gun2Fire.wav"))
    gun2_fire.set_volume(GUN2_VOLUME)

    return {
        "walk": walk_sound,
        "gun1_fire": gun1_fire,
        "gun1_fire_enemy": gun1_fire_enemy,
        "gun2_fire": gun2_fire
    }
