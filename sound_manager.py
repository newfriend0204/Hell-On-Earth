import pygame
import os
from config import ASSET_DIR

def load_sounds():
    # 게임에서 사용할 모든 사운드 로드 및 볼륨 설정
    path_sound = lambda *paths: os.path.join(ASSET_DIR, *paths)

    # 믹서 채널 수 설정
    pygame.mixer.set_num_channels(32)
    
    walk_sound = pygame.mixer.Sound(path_sound("Sound", "ForestWalk.mp3"))
    walk_sound.set_volume(0.3)

    enemy_die_sound = pygame.mixer.Sound(path_sound("Sound", "EnemyDie.mp3"))
    enemy_die_sound.set_volume(0.5)

    room_move_sound = pygame.mixer.Sound(path_sound("Sound", "RoomMove.mp3"))

    swap_gun_sound = pygame.mixer.Sound(path_sound("Sound", "SwapGun.mp3"))
    swap_gun_sound.set_volume(1)

    button_click = pygame.mixer.Sound(path_sound("Sound", "UI", "ButtonClick.wav"))
    button_click.set_volume(0.8)
    button_select = pygame.mixer.Sound(path_sound("Sound", "UI", "ButtonSelect.wav"))
    button_select.set_volume(0.6)

    knife_use = pygame.mixer.Sound(path_sound("Sound", "Gun", "KnifeUse.mp3"))
    knife_kill = pygame.mixer.Sound(path_sound("Sound", "Gun", "KnifeKill.mp3"))
    knife_use.set_volume(0.6)
    knife_kill.set_volume(1)

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
        "gun21_fire": pygame.mixer.Sound(path_sound("Sound", "Gun", "Gun21Fire.mp3")),
        "gun22_fire": pygame.mixer.Sound(path_sound("Sound", "Gun", "Gun22Fire.mp3")),
        "gun23_fire": pygame.mixer.Sound(path_sound("Sound", "Gun", "Gun23Fire.mp3")),
        "gun24_fire": pygame.mixer.Sound(path_sound("Sound", "Gun", "Gun24Fire.mp3")),
        "gun25_fire": pygame.mixer.Sound(path_sound("Sound", "Gun", "Gun25Fire.mp3")),
        "gun26_fire": pygame.mixer.Sound(path_sound("Sound", "Gun", "Gun26Fire.mp3")),
        "gun27_leftfire": pygame.mixer.Sound(path_sound("Sound", "Gun", "Gun27LeftFire.mp3")),
        "gun27_rightfire": pygame.mixer.Sound(path_sound("Sound", "Gun", "Gun27RightFire.mp3")),
        "gun27_charge_loop": pygame.mixer.Sound(path_sound("Sound", "Gun", "Gun27ChargeLoop.mp3")),
        "gun28_leftfire": pygame.mixer.Sound(path_sound("Sound", "Gun", "Gun28LeftFire.mp3")),
        "gun28_singularity_loop": pygame.mixer.Sound(path_sound("Sound", "Gun", "Gun28SingularityLoop.mp3")),
        "gun28_rightfire": pygame.mixer.Sound(path_sound("Sound", "Gun", "Gun28RightFire.mp3")),
        "gun28_pop": pygame.mixer.Sound(path_sound("Sound", "Gun", "Gun28Pop.mp3")),
        "gun29_fire": pygame.mixer.Sound(path_sound("Sound", "Gun", "Gun29Fire.mp3")),
        "gun30_fire": pygame.mixer.Sound(path_sound("Sound", "Gun", "Gun30Fire.mp3")),
        "gun31_fire": pygame.mixer.Sound(path_sound("Sound", "Gun", "Gun31Fire.mp3")),
        "gun31_explosion": pygame.mixer.Sound(path_sound("Sound", "Gun", "Gun31Explosion.mp3")),
        "gun32_fire": pygame.mixer.Sound(path_sound("Sound", "Gun", "Gun32Fire.mp3")),
        "gun33_fire": pygame.mixer.Sound(path_sound("Sound", "Gun", "Gun33Fire.wav")),
        "gun34_leftfire": pygame.mixer.Sound(path_sound("Sound", "Gun", "Gun34LeftFire.wav")),
        "gun34_rightfire": pygame.mixer.Sound(path_sound("Sound", "Gun", "Gun34RightFire.wav")),
        "gun35_explosion": pygame.mixer.Sound(path_sound("Sound", "Gun", "Gun35Explosion.mp3")),
        "gun35_fire": pygame.mixer.Sound(path_sound("Sound", "Gun", "Gun35Fire.mp3")),
        "gun36_leftfire": pygame.mixer.Sound(path_sound("Sound", "Gun", "Gun36LeftFire.mp3")),
        "gun36_rightfire": pygame.mixer.Sound(path_sound("Sound", "Gun", "Gun36RightFire.mp3")),
        "gun37_leftfire": pygame.mixer.Sound(path_sound("Sound", "Gun", "Gun37LeftFire.mp3")),
        "gun37_rightfire": pygame.mixer.Sound(path_sound("Sound", "Gun", "Gun37RightFire.mp3")),
        "gun38_fire": pygame.mixer.Sound(path_sound("Sound", "Gun", "Gun38Fire.mp3")),
        "gun38_explosion": pygame.mixer.Sound(path_sound("Sound", "Gun", "Gun38Explosion.mp3")),
        "gun38_loop": pygame.mixer.Sound(path_sound("Sound", "Gun", "Gun38Loop.mp3")),
    }

    entity_sounds = {
        "drone_spawn": pygame.mixer.Sound(path_sound("Sound", "Entity", "DroneSpawn.mp3")),
        "drone_warning": pygame.mixer.Sound(path_sound("Sound", "Entity", "DroneWarning.mp3")),
        "drone_explosion": pygame.mixer.Sound(path_sound("Sound", "Entity", "DroneExplosion.mp3")),
        "fireball": pygame.mixer.Sound(path_sound("Sound", "Entity", "Fireball.mp3")),
        "flame_pillar": pygame.mixer.Sound(path_sound("Sound", "Entity", "FlamePillar.mp3")),
        "acid": pygame.mixer.Sound(path_sound("Sound", "Entity", "Acid.mp3")),
        "portal_enter": pygame.mixer.Sound(path_sound("Sound", "Entity", "PortalEnter.mp3")),
        "mine_plant": pygame.mixer.Sound(path_sound("Sound", "Entity", "MinePlant.mp3")),
        "mine_activate": pygame.mixer.Sound(path_sound("Sound", "Entity", "MineActivate.mp3")),
        "mine_explosion": pygame.mixer.Sound(path_sound("Sound", "Entity", "MineExplosion.mp3")),
        "spawn_enemy": pygame.mixer.Sound(path_sound("Sound", "Entity", "SpawnEnemy.mp3")),
        "flame_start": pygame.mixer.Sound(path_sound("Sound", "Entity", "FlameStart.mp3")),
        "flame_loop": pygame.mixer.Sound(path_sound("Sound", "Entity", "FlameLoop.mp3")),
        "reaver_slam": pygame.mixer.Sound(path_sound("Sound", "Entity", "ReaverSlam.mp3")),
        "shock_charge": pygame.mixer.Sound(path_sound("Sound", "Entity", "ShockCharge.mp3")),
        "shock_burst":  pygame.mixer.Sound(path_sound("Sound", "Entity", "ShockBurst.mp3")),
        "stab_hit":  pygame.mixer.Sound(path_sound("Sound", "Entity", "StabHit.mp3")),
        "pulse_tick":  pygame.mixer.Sound(path_sound("Sound", "Entity", "PulseTick.mp3")),
        "cocoon_shatter":  pygame.mixer.Sound(path_sound("Sound", "Entity", "CocoonShatter.mp3")),
        "burster_explode":  pygame.mixer.Sound(path_sound("Sound", "Entity", "BursterExplode.mp3")),
        "anvil_spawn":  pygame.mixer.Sound(path_sound("Sound", "Entity", "AnvilSpawn.mp3")),
        "anvil_break":  pygame.mixer.Sound(path_sound("Sound", "Entity", "AnvilBreak.mp3")),
        "chain_hit":  pygame.mixer.Sound(path_sound("Sound", "Entity", "ChainHit.mp3")),
        "chain_drag":  pygame.mixer.Sound(path_sound("Sound", "Entity", "ChainDrag.mp3")),
        "chain_throw":  pygame.mixer.Sound(path_sound("Sound", "Entity", "ChainThrow.mp3")),
        "whirl":  pygame.mixer.Sound(path_sound("Sound", "Entity", "Whirl.mp3")),
    }

    weapon_sounds["gun5_overheat"].set_volume(0.5)
    weapon_sounds["gun6_leftfire"].set_volume(0.85)
    weapon_sounds["gun15_leftfire"].set_volume(0.3)
    weapon_sounds["gun15_rightfire"].set_volume(0.4)
    weapon_sounds["gun29_fire"].set_volume(0.7)


    weapon_sounds["gun1_fire_enemy"] = pygame.mixer.Sound(path_sound("Sound", "Gun", "Gun1Fire.wav"))
    weapon_sounds["gun2_fire_enemy"] = pygame.mixer.Sound(path_sound("Sound", "Gun", "Gun2Fire.wav"))
    weapon_sounds["gun3_fire_enemy"] = pygame.mixer.Sound(path_sound("Sound", "Gun", "Gun3Fire.wav"))
    weapon_sounds["enemy4_fire"] = weapon_sounds["gun5_fire"]
    weapon_sounds["enemy4_preheat"] = weapon_sounds["gun5_preheat"]
    weapon_sounds["enemy4_shield_break"] = pygame.mixer.Sound(path_sound("Sound", "Entity", "ShieldBreak.mp3"))
    weapon_sounds["enemy4_shield_charged"] = pygame.mixer.Sound(path_sound("Sound", "Entity", "ShieldCharged.mp3"))
    weapon_sounds["enemy5_fire"] = weapon_sounds["gun3_fire"]

    weapon_sounds["gun1_fire_enemy"].set_volume(0.25)
    weapon_sounds["gun2_fire_enemy"].set_volume(0.25)
    weapon_sounds["gun3_fire_enemy"].set_volume(0.25)
    weapon_sounds["enemy4_fire"].set_volume(0.2)
    weapon_sounds["enemy4_preheat"].set_volume(0.25)
    weapon_sounds["enemy4_shield_break"].set_volume(0.25)
    weapon_sounds["enemy4_shield_charged"].set_volume(0.1)
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

_BGM_FILES = None
_bgm_current_key = None

def _ensure_bgm_files():
    global _BGM_FILES
    if _BGM_FILES is None:
        path = lambda *p: os.path.join(ASSET_DIR, *p)
        _BGM_FILES = {
            1: path("Sound", "Background", "Map1.mp3"),
            2: path("Sound", "Background", "Map2.mp3"),
            3: path("Sound", "Background", "Map3.mp3"),
            "main": path("Sound", "Background", "Main.mp3"),
        }

def _stage_to_key(stage_like):
    # "1-1" → 1, 2 → 2 등 유연 파싱
    try:
        if isinstance(stage_like, str):
            return int(stage_like.split("-")[0])
        return int(stage_like)
    except Exception:
        return 1

def set_bgm_volume(vol: float):
    pygame.mixer.music.set_volume(max(0.0, min(1.0, float(vol))))

def stop_bgm(fade_ms: int = 400):
    try:
        pygame.mixer.music.fadeout(max(0, int(fade_ms)))
    except Exception:
        pass

def cut_bgm():
    # 즉시(하드) 정지 — 사망 연출 등에 사용
    try:
        pygame.mixer.music.stop()
        global _bgm_current_key
        _bgm_current_key = None
    except Exception:
        pass

def play_bgm_for_stage(stage_like, fade_ms: int = 600):
    # 스테이지(1/2/3 또는 '1-1' 등)를 받아 해당 BGM을 무한 반복 재생
    global _bgm_current_key
    _ensure_bgm_files()
    key = _stage_to_key(stage_like)
    if key == _bgm_current_key:
        # 이미 같은 곡이 플레이 중이면 무시
        return
    try:
        # 부드럽게 교체
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.fadeout(250)
        pygame.mixer.music.load(_BGM_FILES.get(key, _BGM_FILES[1]))
        set_bgm_volume(0.3)
        pygame.mixer.music.play(-1, fade_ms=max(0, int(fade_ms)))  # 무한 반복
        _bgm_current_key = key
    except Exception:
        _bgm_current_key = None

def play_bgm_main(fade_ms: int = 600, restart: bool = False):
    # 메인 메뉴 BGM을 무한 반복 재생. 이미 재생 중이면 기본적으로 그대로 둠.
    global _bgm_current_key
    _ensure_bgm_files()
    if _bgm_current_key == "main" and not restart:
        return
    try:
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.fadeout(250)
        pygame.mixer.music.load(_BGM_FILES["main"])
        set_bgm_volume(0.3)
        pygame.mixer.music.play(-1, fade_ms=max(0, int(fade_ms)))
        _bgm_current_key = "main"
    except Exception:
        _bgm_current_key = None