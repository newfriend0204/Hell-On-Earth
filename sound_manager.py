import pygame
import os
from config import ASSET_DIR

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

    knife_use = pygame.mixer.Sound(path_sound("Sound", "KnifeUse.mp3"))
    knife_kill = pygame.mixer.Sound(path_sound("Sound", "KnifeKill.mp3"))
    knife_use.set_volume(0.6)
    knife_kill.set_volume(0.7)

    weapon_sounds = {
        "boss1_gun1_fire": pygame.mixer.Sound(path_sound("Sound", "Gun", "Boss1Gun1Fire.mp3")),
        "boss1_gun2_fire": pygame.mixer.Sound(path_sound("Sound", "Gun", "Boss1Gun2Fire.mp3")),
        "boss2_gun1_fire": pygame.mixer.Sound(path_sound("Sound", "Gun", "Boss2Gun1Fire.mp3")),
        "boss2_gun1_explosion": pygame.mixer.Sound(path_sound("Sound", "Gun", "Boss2Gun1Explosion.mp3")),
        "boss2_gun2_fire": pygame.mixer.Sound(path_sound("Sound", "Gun", "Boss2Gun2Fire.wav")),
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
        "gun10_fire": pygame.mixer.Sound(path_sound("Sound", "Gun", "Gun10Fire.mp3")),
        "gun11_fire": pygame.mixer.Sound(path_sound("Sound", "Gun", "Gun11Fire.mp3")),
        "gun12_fire": pygame.mixer.Sound(path_sound("Sound", "Gun", "Gun12Fire.mp3")),
        "gun13_fire": pygame.mixer.Sound(path_sound("Sound", "Gun", "Gun13Fire.mp3")),
        "gun14_fire": pygame.mixer.Sound(path_sound("Sound", "Gun", "Gun14Fire.mp3")),
        "gun15_leftfire": pygame.mixer.Sound(path_sound("Sound", "Gun", "Gun15LeftFire.mp3")),
        "gun15_rightfire": pygame.mixer.Sound(path_sound("Sound", "Gun", "Gun15RightFire.mp3")),
        "gun16_fire": pygame.mixer.Sound(path_sound("Sound", "Gun", "Gun16Fire.mp3")),
        "gun17_fire": pygame.mixer.Sound(path_sound("Sound", "Gun", "Gun17Fire.mp3")),
        "gun18_fire": pygame.mixer.Sound(path_sound("Sound", "Gun", "Gun18Fire.mp3")),
        "gun19_defend": pygame.mixer.Sound(path_sound("Sound", "Gun", "Gun19Defend.mp3")),
        "gun20_fire": pygame.mixer.Sound(path_sound("Sound", "Gun", "Gun20Fire.mp3")),
        "gun20_explosion": pygame.mixer.Sound(path_sound("Sound", "Gun", "Gun20Explosion.mp3")),
    }

    entity_sounds = {
        "drone_spawn": pygame.mixer.Sound(path_sound("Sound", "Entity", "DroneSpawn.mp3")),
        "drone_warning": pygame.mixer.Sound(path_sound("Sound", "Entity", "DroneWarning.mp3")),
        "drone_explosion": pygame.mixer.Sound(path_sound("Sound", "Entity", "DroneExplosion.mp3")),
        "fireball": pygame.mixer.Sound(path_sound("Sound", "Entity", "Fireball.mp3")),
        "flame_pillar": pygame.mixer.Sound(path_sound("Sound", "Entity", "FlamePillar.mp3")),
        "acid": pygame.mixer.Sound(path_sound("Sound", "Entity", "Acid.mp3")),
    }

    weapon_sounds["gun5_overheat"].set_volume(0.5)
    weapon_sounds["gun6_leftfire"].set_volume(0.85)
    weapon_sounds["gun15_leftfire"].set_volume(0.3)
    weapon_sounds["gun15_rightfire"].set_volume(0.4)


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
    weapon_sounds["boss2_gun1_fire"].set_volume(0.5)
    weapon_sounds["boss2_gun1_explosion"].set_volume(0.5)
    weapon_sounds["boss2_gun2_fire"].set_volume(0.5)

    entity_sounds["drone_spawn"].set_volume(0.5)
    entity_sounds["drone_warning"].set_volume(1)
    entity_sounds["drone_explosion"].set_volume(0.5)
    entity_sounds["fireball"].set_volume(0.5)
    entity_sounds["flame_pillar"].set_volume(0.5)
    entity_sounds["acid"].set_volume(0.2)

    return {
        # 모든 사운드 딕셔너리 반환
        "walk": walk_sound,
        "enemy_die": enemy_die_sound,
        "room_move": room_move_sound,
        "swap_gun": swap_gun_sound,
        "button_click": button_click,
        "button_select": button_select,
        "knife_use": knife_use,
        "knife_kill": knife_kill,
        **weapon_sounds,
        **entity_sounds
    }
