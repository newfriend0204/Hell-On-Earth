import pygame
import os
from config import ASSET_DIR, GUN1_VOLUME, GUN2_VOLUME, GUN3_VOLUME

def load_sounds():
    # 게임에서 사용할 모든 사운드 로드 및 볼륨 설정
    path_sound = lambda *paths: os.path.join(ASSET_DIR, *paths)

    # 믹서 채널 수 설정
    pygame.mixer.set_num_channels(16)
    
    walk_sound = pygame.mixer.Sound(path_sound("Sound", "ForestWalk.mp3"))
    walk_sound.set_volume(0.3)

    enemy_die_sound = pygame.mixer.Sound(path_sound("Sound", "EnemyDie.mp3"))
    enemy_die_sound.set_volume(0.3)

    room_move_sound = pygame.mixer.Sound(path_sound("Sound", "RoomMove.mp3"))

    swap_gun_sound = pygame.mixer.Sound(path_sound("Sound", "SwapGun.mp3"))
    swap_gun_sound.set_volume(0.8)

    button_click = pygame.mixer.Sound(path_sound("Sound", "UI", "ButtonClick.wav"))
    button_click.set_volume(0.8)
    button_select = pygame.mixer.Sound(path_sound("Sound", "UI", "ButtonSelect.mp3"))
    button_select.set_volume(0.6)

    weapon_sounds = {
        "boss1_gun1_fire": pygame.mixer.Sound(path_sound("Sound", "Gun", "Boss1Gun1Fire.mp3")),
        "boss1_gun2_fire": pygame.mixer.Sound(path_sound("Sound", "Gun", "Boss1Gun2Fire.mp3")),
        "gun1_fire": pygame.mixer.Sound(path_sound("Sound", "Gun", "Gun1Fire.wav")),
        "gun2_fire": pygame.mixer.Sound(path_sound("Sound", "Gun", "Gun2Fire.wav")),
        "gun3_fire": pygame.mixer.Sound(path_sound("Sound", "Gun", "Gun3Fire.wav")),
        "gun4_fire": pygame.mixer.Sound(path_sound("Sound", "Gun", "Gun4Fire.mp3")),
        "gun5_fire": pygame.mixer.Sound(path_sound("Sound", "Gun", "Gun5Fire.mp3")),
        "gun5_preheat": pygame.mixer.Sound(path_sound("Sound", "Gun", "Gun5Preheat.mp3")),
        "gun5_overheat": pygame.mixer.Sound(path_sound("Sound", "Gun", "Gun5Overheat.mp3")),
        "gun4_explosion": pygame.mixer.Sound(path_sound("Sound", "Gun", "Gun4Explosion.mp3")),
        "gun6_leftfire": pygame.mixer.Sound(path_sound("Sound", "Gun", "Gun6LeftFire.wav")),
        "gun6_rightfire": pygame.mixer.Sound(path_sound("Sound", "Gun", "Gun6RightFire.mp3")),
        "gun6_explosion": pygame.mixer.Sound(path_sound("Sound", "Gun", "Gun6Explosion.mp3")),
        "gun7_leftfire": pygame.mixer.Sound(path_sound("Sound", "Gun", "Gun7LeftFire.mp3")),
        "gun7_rightfire": pygame.mixer.Sound(path_sound("Sound", "Gun", "Gun7RightFire.mp3")),
        "gun8_fire": pygame.mixer.Sound(path_sound("Sound", "Gun", "Gun8Fire.mp3")),
        "gun8_explosion": pygame.mixer.Sound(path_sound("Sound", "Gun", "Gun8Explosion.mp3")),
        "gun9_leftfire": pygame.mixer.Sound(path_sound("Sound", "Gun", "Gun9LeftFire.mp3")),
        "gun9_rightfire": pygame.mixer.Sound(path_sound("Sound", "Gun", "Gun9RightFire.mp3")),
        "gun9_explosion": pygame.mixer.Sound(path_sound("Sound", "Gun", "Gun9Explosion.mp3")),
    }

    weapon_sounds["gun1_fire"].set_volume(GUN1_VOLUME)
    weapon_sounds["gun2_fire"].set_volume(GUN2_VOLUME)
    weapon_sounds["gun3_fire"].set_volume(GUN3_VOLUME)
    weapon_sounds["gun4_fire"].set_volume(1.0)
    weapon_sounds["gun4_explosion"].set_volume(1.0)
    weapon_sounds["gun5_preheat"].set_volume(1.0)
    weapon_sounds["gun5_fire"].set_volume(1.0)
    weapon_sounds["gun5_overheat"].set_volume(0.5)
    weapon_sounds["gun6_leftfire"].set_volume(0.85)
    weapon_sounds["gun6_rightfire"].set_volume(1.0)
    weapon_sounds["gun6_explosion"].set_volume(1.0)
    weapon_sounds["gun9_leftfire"].set_volume(1.0)
    weapon_sounds["gun9_rightfire"].set_volume(1.0)
    weapon_sounds["gun9_explosion"].set_volume(1.0)

    weapon_sounds["gun1_fire_enemy"] = pygame.mixer.Sound(path_sound("Sound", "Gun", "Gun1Fire.wav"))
    weapon_sounds["gun2_fire_enemy"] = pygame.mixer.Sound(path_sound("Sound", "Gun", "Gun2Fire.wav"))
    weapon_sounds["gun3_fire_enemy"] = pygame.mixer.Sound(path_sound("Sound", "Gun", "Gun3Fire.wav"))
    weapon_sounds["enemy4_fire"] = weapon_sounds["gun5_fire"]
    weapon_sounds["enemy4_preheat"] = weapon_sounds["gun5_preheat"]
    weapon_sounds["enemy4_shield_break"] = pygame.mixer.Sound(path_sound("Sound", "ShieldBreak.mp3"))
    weapon_sounds["enemy4_shield_chared"] = pygame.mixer.Sound(path_sound("Sound", "ShieldCharged.mp3"))
    weapon_sounds["enemy5_fire"] = weapon_sounds["gun3_fire"]

    weapon_sounds["gun1_fire_enemy"].set_volume(0.25)
    weapon_sounds["gun2_fire_enemy"].set_volume(0.25)
    weapon_sounds["gun3_fire_enemy"].set_volume(0.25)
    weapon_sounds["enemy4_fire"].set_volume(0.2)
    weapon_sounds["enemy4_preheat"].set_volume(0.25)
    weapon_sounds["enemy4_shield_break"].set_volume(0.25)
    weapon_sounds["enemy4_shield_chared"].set_volume(0.1)
    weapon_sounds["enemy5_fire"].set_volume(0.25)
    weapon_sounds["boss1_gun1_fire"].set_volume(0.5)
    weapon_sounds["boss1_gun2_fire"].set_volume(0.5)

    return {
        # 모든 사운드 딕셔너리 반환
        "walk": walk_sound,
        "enemy_die": enemy_die_sound,
        "room_move": room_move_sound,
        "swap_gun": swap_gun_sound,
        "button_click": button_click,
        "button_select": button_select,
        **weapon_sounds
    }
