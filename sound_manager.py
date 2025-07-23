import pygame
import os
from config import ASSET_DIR, GUN1_VOLUME, GUN2_VOLUME, GUN3_VOLUME

def load_sounds():
    path_sound = lambda *paths: os.path.join(ASSET_DIR, *paths)

    pygame.mixer.set_num_channels(16)

    walk_sound = pygame.mixer.Sound(path_sound("Sound", "ForestWalk.mp3"))
    walk_sound.set_volume(0.3)

    enemy_die_sound = pygame.mixer.Sound(path_sound("Sound", "EnemyDie.mp3"))
    enemy_die_sound.set_volume(0.3)

    room_move_sound = pygame.mixer.Sound(path_sound("Sound", "RoomMove.mp3"))

    weapon_sounds = {
        "gun1_fire": pygame.mixer.Sound(path_sound("Sound", "Gun", "Gun1Fire.wav")),
        "gun2_fire": pygame.mixer.Sound(path_sound("Sound", "Gun", "Gun2Fire.wav")),
        "gun3_fire": pygame.mixer.Sound(path_sound("Sound", "Gun", "Gun3Fire.wav")),
        "gun4_fire": pygame.mixer.Sound(path_sound("Sound", "Gun", "Gun4Fire.mp3")),
        "gun4_explosion": pygame.mixer.Sound(path_sound("Sound", "Gun", "Gun4Explosion.mp3")),
    }

    weapon_sounds["gun1_fire"].set_volume(GUN1_VOLUME)
    weapon_sounds["gun2_fire"].set_volume(GUN2_VOLUME)
    weapon_sounds["gun3_fire"].set_volume(GUN3_VOLUME)
    weapon_sounds["gun4_fire"].set_volume(1.0)
    weapon_sounds["gun4_explosion"].set_volume(1.0)

    weapon_sounds["gun1_fire_enemy"] = pygame.mixer.Sound(path_sound("Sound", "Gun", "Gun1Fire.wav"))
    weapon_sounds["gun2_fire_enemy"] = pygame.mixer.Sound(path_sound("Sound", "Gun", "Gun2Fire.wav"))
    weapon_sounds["gun3_fire_enemy"] = pygame.mixer.Sound(path_sound("Sound", "Gun", "Gun3Fire.wav"))

    weapon_sounds["gun1_fire_enemy"].set_volume(0.25)
    weapon_sounds["gun2_fire_enemy"].set_volume(0.25)
    weapon_sounds["gun3_fire_enemy"].set_volume(0.25)

    return {
        "walk": walk_sound,
        "enemy_die": enemy_die_sound,
        "room_move": room_move_sound,
        **weapon_sounds
    }
