import pygame
import os
from config import ASSET_DIR, WALK_VOLUME, GUN1_VOLUME

def load_sounds():
    path_sound = lambda *paths: os.path.join(ASSET_DIR, *paths)

    gun1_fire = pygame.mixer.Sound(path_sound("Sound", "Gun1Fire.wav"))
    gun1_fire.set_volume(GUN1_VOLUME)

    walk_sound = pygame.mixer.Sound(path_sound("Sound", "ForestWalk.mp3"))
    walk_sound.set_volume(WALK_VOLUME)

    return {
        "gun1_fire": gun1_fire,
        "walk": walk_sound
    }
