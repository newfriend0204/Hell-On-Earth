import pygame
import os
from config import *

def load_images():
    # 게임에서 사용하는 모든 이미지 로드 및 크기 조정
    path_image = lambda *paths: os.path.join(ASSET_DIR, *paths)

    # 플레이어 이미지 로드 및 크기 조정
    player_img = pygame.image.load(path_image("image", "character", "MainCharacter.png")).convert_alpha()
    player_img = pygame.transform.smoothscale(player_img, (90, 90))

    # 무기별 상단(Top-down) 이미지 로드 및 스케일
    gun1_img = pygame.image.load(path_image("image", "Gun", "Gun1Player.png")).convert_alpha()
    gun1_img = pygame.transform.smoothscale(gun1_img, (30, int(gun1_img.get_height() * (30 / gun1_img.get_width()))))

    gun2_img = pygame.image.load(path_image("image", "Gun", "Gun2Player.png")).convert_alpha()
    gun2_img = pygame.transform.smoothscale(gun2_img, (60, int(gun2_img.get_height() * (60 / gun2_img.get_width()))))

    gun3_img = pygame.image.load(path_image("image", "Gun", "Gun3Player.png")).convert_alpha()
    gun3_img = pygame.transform.smoothscale(gun3_img, (70, int(gun3_img.get_height() * (70 / gun3_img.get_width()))))

    gun4_img = pygame.image.load(path_image("image", "Gun", "Gun4Player.png")).convert_alpha()
    gun4_img = pygame.transform.smoothscale(gun4_img, (60, int(gun4_img.get_height() * (60 / gun4_img.get_width()))))

    gun5_img = pygame.image.load(path_image("image", "Gun", "Gun5Player.png")).convert_alpha()
    gun5_img = pygame.transform.smoothscale(gun5_img, (65, int(gun5_img.get_height() * (65 / gun5_img.get_width()))))

    gun6_img = pygame.image.load(path_image("image", "Gun", "Gun6Player.png")).convert_alpha()
    gun6_img = pygame.transform.smoothscale(gun6_img, (55, int(gun6_img.get_height() * (55 / gun6_img.get_width()))))

    gun7_img = pygame.image.load(path_image("image", "Gun", "Gun7Player.png")).convert_alpha()
    gun7_img = pygame.transform.smoothscale(gun7_img, (80, int(gun7_img.get_height() * (80 / gun7_img.get_width()))))

    gun8_img = pygame.image.load(path_image("image", "Gun", "Gun8Player.png")).convert_alpha()
    gun8_img = pygame.transform.smoothscale(gun8_img, (50, int(gun8_img.get_height() * (50 / gun8_img.get_width()))))

    gun9_img = pygame.image.load(path_image("image", "Gun", "Gun9Player.png")).convert_alpha()
    gun9_img = pygame.transform.smoothscale(gun9_img, (50, int(gun9_img.get_height() * (50 / gun9_img.get_width()))))

    gun10_img = pygame.image.load(path_image("image", "Gun", "Gun10Player.png")).convert_alpha()
    gun10_img = pygame.transform.smoothscale(gun10_img, (50, int(gun10_img.get_height() * (50 / gun10_img.get_width()))))

    gun11_img = pygame.image.load(path_image("image", "Gun", "Gun10Player.png")).convert_alpha()
    gun11_img = pygame.transform.smoothscale(gun11_img, (50, int(gun11_img.get_height() * (50 / gun11_img.get_width()))))

    gun12_img = pygame.image.load(path_image("image", "Gun", "Gun12Player.png")).convert_alpha()
    gun12_img = pygame.transform.smoothscale(gun12_img, (55, int(gun12_img.get_height() * (55 / gun12_img.get_width()))))

    gun13_img = pygame.image.load(path_image("image", "Gun", "Gun13Player.png")).convert_alpha()
    gun13_img = pygame.transform.smoothscale(gun13_img, (55, int(gun13_img.get_height() * (55 / gun13_img.get_width()))))

    gun14_img = pygame.image.load(path_image("image", "Gun", "Gun14Player.png")).convert_alpha()
    gun14_img = pygame.transform.smoothscale(gun14_img, (55, int(gun14_img.get_height() * (55 / gun14_img.get_width()))))

    gun15_img = pygame.image.load(path_image("image", "Gun", "Gun15Player.png")).convert_alpha()
    gun15_img = pygame.transform.smoothscale(gun15_img, (55, int(gun15_img.get_height() * (55 / gun15_img.get_width()))))

    gun16_img = pygame.image.load(path_image("image", "Gun", "Gun16Player.png")).convert_alpha()
    gun16_img = pygame.transform.smoothscale(gun16_img, (55, int(gun16_img.get_height() * (55 / gun16_img.get_width()))))

    gun17_img = pygame.image.load(path_image("image", "Gun", "Gun17Player.png")).convert_alpha()
    gun17_img = pygame.transform.smoothscale(gun17_img, (55, int(gun17_img.get_height() * (55 / gun17_img.get_width()))))

    gun18_img = pygame.image.load(path_image("image", "Gun", "Gun18Player.png")).convert_alpha()
    gun18_img = pygame.transform.smoothscale(gun18_img, (50, int(gun18_img.get_height() * (50 / gun18_img.get_width()))))

    gun19_img = pygame.image.load(path_image("image", "Gun", "Gun19Player.png")).convert_alpha()
    gun19_img = pygame.transform.smoothscale(gun19_img, (100, int(gun19_img.get_height() * (100 / gun19_img.get_width()))))

    gun20_img = pygame.image.load(path_image("image", "Gun", "Gun20Player.png")).convert_alpha()
    gun20_img = pygame.transform.smoothscale(gun20_img, (30, int(gun20_img.get_height() * (30 / gun20_img.get_width()))))

    boss1gun1_img = pygame.image.load(path_image("image", "Gun", "Boss1Gun1.png")).convert_alpha()
    boss1gun1_img = pygame.transform.smoothscale(boss1gun1_img, (50, int(boss1gun1_img.get_height() * (50 / boss1gun1_img.get_width()))))

    boss1gun2_img = pygame.image.load(path_image("image", "Gun", "Boss1Gun2.png")).convert_alpha()
    boss1gun2_img = pygame.transform.smoothscale(boss1gun2_img, (50, int(boss1gun2_img.get_height() * (50 / boss1gun2_img.get_width()))))

    warhead_img = pygame.image.load(path_image("image", "Gun", "Warhead1.png")).convert_alpha()
    warhead_img = pygame.transform.smoothscale(warhead_img, (40, 40))

    grenade_img = pygame.image.load(path_image("image", "Gun", "LauncherGrenade1.png")).convert_alpha()
    grenade_img = pygame.transform.smoothscale(grenade_img, (30, 30))

    hand_grenade_img = pygame.image.load(path_image("image", "Gun", "Gun20.png")).convert_alpha()
    hand_grenade_img = pygame.transform.smoothscale(hand_grenade_img, (30, 30))

    explosion_img = pygame.image.load(path_image("image", "Gun", "Explosion.png")).convert_alpha()
    explosion_img = pygame.transform.smoothscale(explosion_img, (200, 200))

    # 탄환 이미지 크기 조정
    bullet1_img = pygame.image.load(path_image("image", "Gun", "Bullet1.png")).convert_alpha()
    scale_factor = 60 / bullet1_img.get_width()
    bullet1_img = pygame.transform.smoothscale(
        bullet1_img,
        (
            int(bullet1_img.get_width() * scale_factor),
            int(bullet1_img.get_height() * scale_factor)
        )
    )
    bullet2_img = pygame.image.load(path_image("image", "Gun", "Bullet2.png")).convert_alpha()
    scale_factor = 40 / bullet2_img.get_width()
    bullet2_img = pygame.transform.smoothscale(
        bullet2_img,
        (
            int(bullet2_img.get_width() * scale_factor),
            int(bullet2_img.get_height() * scale_factor)
        )
    )
    bullet3_img = pygame.image.load(path_image("image", "Gun", "Bullet3.png")).convert_alpha()
    scale_factor = 50 / bullet3_img.get_width()
    bullet3_img = pygame.transform.smoothscale(
        bullet3_img,
        (
            int(bullet3_img.get_width() * scale_factor),
            int(bullet3_img.get_height() * scale_factor)
        )
    )

    # 적 탄환 색상 변경(빨간색)
    enemy_bullet_img = bullet1_img.copy()
    enemy_bullet_img.fill((255, 0, 0, 255), special_flags=pygame.BLEND_RGBA_MULT)

    cartridge_case_img1 = pygame.image.load(path_image("image", "Gun", "CartridgeCase1.png")).convert_alpha()
    cartridge_case_img1 = pygame.transform.smoothscale(
        cartridge_case_img1,
        (2, int(cartridge_case_img1.get_height() * 4 / cartridge_case_img1.get_width()))
    )
    cartridge_case_img2 = pygame.image.load(path_image("image", "Gun", "CartridgeCase2.png")).convert_alpha()
    cartridge_case_img2 = pygame.transform.smoothscale(
        cartridge_case_img2,
        (20, int(cartridge_case_img2.get_height() * 20 / cartridge_case_img2.get_width()))
    )

    cursor_img = pygame.image.load(path_image("image", "MouseCursor.png")).convert_alpha()
    cursor_img = pygame.transform.smoothscale(cursor_img, (32, 32))

    bg_img = pygame.image.load(path_image("Image", "Map1.png")).convert()
    bg_img = pygame.transform.smoothscale(bg_img, (BG_WIDTH, BG_HEIGHT))

    wall_barrier_img = pygame.image.load(path_image("Image", "Map1Wall.png")).convert_alpha()
    scale_factor = 0.275 * PLAYER_VIEW_SCALE
    wall_barrier_img = pygame.transform.smoothscale(wall_barrier_img, (
        int(wall_barrier_img.get_width() * scale_factor),
        int(wall_barrier_img.get_height() * scale_factor)
    ))
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
        "TreeStump.png": (1024, 1024),
    }

    # 장애물 이미지 및 마스크 로드
    obstacle_dir = path_image("Image", "Obstacle")
    obstacle_images = {}
    obstacle_masks = {}

    if os.path.exists(obstacle_dir):
        for filename in os.listdir(obstacle_dir):
            if filename in obstacle_sizes:
                img_path = os.path.join(obstacle_dir, filename)
                image = pygame.image.load(img_path).convert_alpha()
                image = pygame.transform.smoothscale(image, obstacle_sizes[filename])
                obstacle_images[filename] = image
                obstacle_masks[filename] = pygame.mask.from_surface(image)

    # 캐릭터 이미지 로드
    merchant1_img = pygame.image.load(path_image("image", "character", "Merchant1.png")).convert_alpha()
    merchant1_img = pygame.transform.smoothscale(merchant1_img, (90, 90))

    doctorNF_img = pygame.image.load(path_image("image", "character", "DoctorNF.png")).convert_alpha()
    doctorNF_img = pygame.transform.smoothscale(doctorNF_img, (90, 90))

    enemy1_img = pygame.image.load(path_image("image", "character", "Enemy1.png")).convert_alpha()
    enemy1_img = pygame.transform.smoothscale(enemy1_img, (90, 90))

    enemy2_img = pygame.image.load(path_image("image", "character", "Enemy2.png")).convert_alpha()
    enemy2_img = pygame.transform.smoothscale(enemy2_img, (90, 90))

    enemy3_img = pygame.image.load(path_image("image", "character", "Enemy3.png")).convert_alpha()
    enemy3_img = pygame.transform.smoothscale(enemy3_img, (117, 117))

    enemy4_img = pygame.image.load(path_image("image", "character", "Enemy4.png")).convert_alpha()
    enemy4_img = pygame.transform.smoothscale(enemy4_img, (108, 108))

    enemy5_img = pygame.image.load(path_image("image", "character", "Enemy5.png")).convert_alpha()
    enemy5_img = pygame.transform.smoothscale(enemy5_img, (90, 90))

    enemy6_img = pygame.image.load(path_image("image", "character", "Enemy6.png")).convert_alpha()
    enemy6_img = pygame.transform.smoothscale(enemy6_img, (150, 150))

    enemy7_img = pygame.image.load(path_image("image", "character", "Enemy7.png")).convert_alpha()
    enemy7_img = pygame.transform.smoothscale(enemy7_img, (120, 120))

    enemy8_img = pygame.image.load(path_image("image", "character", "Enemy8.png")).convert_alpha()
    enemy8_img = pygame.transform.smoothscale(enemy8_img, (90, 90))

    enemy9_img = pygame.image.load(path_image("image", "character", "Enemy9.png")).convert_alpha()
    enemy9_img = pygame.transform.smoothscale(enemy9_img, (90, 90))

    boss1_img = pygame.image.load(path_image("image", "character", "Boss1.png")).convert_alpha()
    boss1_img = pygame.transform.smoothscale(boss1_img, (120, 120))

    boss2_img = pygame.image.load(path_image("image", "character", "Boss2.png")).convert_alpha()
    boss2_img = pygame.transform.smoothscale(boss2_img, (120, 120))

    drone_img = pygame.image.load(path_image("image", "entity", "Drone.png")).convert_alpha()
    drone_img = pygame.transform.smoothscale(drone_img, (60, 60))

    fireball_img = pygame.image.load(path_image("image", "entity", "Fireball.png")).convert_alpha()
    fireball_img = pygame.transform.smoothscale(fireball_img, (100, 50))

    flame_pillar_img = pygame.image.load(path_image("image", "entity", "FirePillar.png")).convert_alpha()
    flame_pillar_img = pygame.transform.smoothscale(flame_pillar_img, (300, 300))

    acid_projectile_img = fireball_img.copy()
    acid_projectile_img.fill((0, 100, 0, 255), special_flags=pygame.BLEND_RGBA_MULT)

    acid_pool_img = flame_pillar_img.copy()
    acid_pool_img.fill((0, 100, 0, 255), special_flags=pygame.BLEND_RGBA_MULT)

    ammo_gauge_up_img = pygame.image.load(path_image("Image", "AmmoGaugeUp.png")).convert_alpha()
    ammo_gauge_up_img = pygame.transform.smoothscale(ammo_gauge_up_img, (16, 16))
    health_up_img = pygame.image.load(path_image("Image", "HealthUp.png")).convert_alpha()
    health_up_img = pygame.transform.smoothscale(health_up_img, (16, 16))

    return {
        # 로드된 모든 이미지를 딕셔너리로 반환
        "player": player_img,
        "gun1": gun1_img,
        "gun2": gun2_img,
        "gun3": gun3_img,
        "gun4": gun4_img,
        "gun5": gun5_img,
        "gun6": gun6_img,
        "gun7": gun7_img,
        "gun8": gun8_img,
        "gun9": gun9_img,
        "gun10": gun10_img,
        "gun11": gun11_img,
        "gun12": gun12_img,
        "gun13": gun13_img,
        "gun14": gun14_img,
        "gun15": gun15_img,
        "gun16": gun16_img,
        "gun17": gun17_img,
        "gun18": gun18_img,
        "gun19": gun19_img,
        "gun20": gun20_img,
        "boss1gun1": boss1gun1_img,
        "boss1gun2": boss1gun2_img,
        "bullet1": bullet1_img,
        "bullet2": bullet2_img,
        "bullet3": bullet3_img,
        "grenade1": grenade_img,
        "hand_grenade": hand_grenade_img,
        "warhead1": warhead_img,
        "explosion1": explosion_img,
        "cartridge_case1": cartridge_case_img1,
        "cartridge_case2": cartridge_case_img2,
        "enemy_bullet": enemy_bullet_img,
        "merchant1": merchant1_img,
        "doctorNF": doctorNF_img,
        "enemy1": enemy1_img,
        "enemy2": enemy2_img,
        "enemy3": enemy3_img,
        "enemy4": enemy4_img,
        "enemy5": enemy5_img,
        "enemy6": enemy6_img,
        "enemy7": enemy7_img,
        "enemy8": enemy8_img,
        "enemy9": enemy9_img,
        "boss1": boss1_img,
        "boss2": boss2_img,
        "drone": drone_img,
        "fireball": fireball_img,
        "flame_pillar": flame_pillar_img,
        "acid_projectile": acid_projectile_img,
        "acid_pool": acid_pool_img,
        "ammo_gauge_up": ammo_gauge_up_img,
        "health_up": health_up_img,
        "cursor": cursor_img,
        "background": bg_img,
        "obstacles": obstacle_images,
        "obstacle_masks": obstacle_masks,
        "wall_barrier": wall_barrier_img,
        "wall_barrier_rotated": wall_barrier_img_rotated,
    }

def load_weapon_assets(images):
    # 무기별 전방(Front) 이미지, 상단(Top-down) 이미지, 탄환, 탄피, 폭발 이미지 설정
    weapons = {
        "gun1": {
            "front": pygame.image.load(os.path.join(ASSET_DIR, "image", "Gun", "Gun1.png")).convert_alpha(),
            "topdown": images["gun1"],
            "bullets": [images["bullet1"]],
            "cartridges": [images["cartridge_case1"]],
        },
        "gun2": {
            "front": pygame.image.load(os.path.join(ASSET_DIR, "image", "Gun", "Gun2.png")).convert_alpha(),
            "topdown": images["gun2"],
            "bullets": [images["bullet1"]],
            "cartridges": [images["cartridge_case1"]],
        },
        "gun3": {
            "front": pygame.image.load(os.path.join(ASSET_DIR, "image", "Gun", "Gun3.png")).convert_alpha(),
            "topdown": images["gun3"],
            "bullets": [images["bullet1"]],
            "cartridges": [images["cartridge_case2"]],
        },
        "gun4": {
            "front": pygame.image.load(os.path.join(ASSET_DIR, "image", "Gun", "Gun4.png")).convert_alpha(),
            "topdown": images["gun4"],
            "bullets": [images["grenade1"]],
            "cartridges": [],
            "grenade": images["grenade1"],
            "explosion": images["explosion1"],
        },
        "gun5": {
            "front": pygame.image.load(os.path.join(ASSET_DIR, "image", "Gun", "Gun5.png")).convert_alpha(),
            "topdown": images["gun5"],
            "bullets": [pygame.transform.smoothscale(
                images["bullet1"],
                (images["bullet1"].get_width() // 2, images["bullet1"].get_height() // 2)
            )],
            "cartridges": [images["cartridge_case1"]],
        },
        "gun6": {
            "front": pygame.image.load(os.path.join(ASSET_DIR, "image", "Gun", "Gun6.png")).convert_alpha(),
            "topdown": images["gun6"],
            "bullets": [images["bullet1"]],
            "cartridges": [images["cartridge_case1"]],
            "grenade": images["grenade1"],
            "explosion": images["explosion1"],
        },
        "gun7": {
            "front": pygame.image.load(os.path.join(ASSET_DIR, "image", "Gun", "Gun7.png")).convert_alpha(),
            "topdown": images["gun7"],
            "bullets": [images["bullet1"]],
            "cartridges": [images["cartridge_case1"], images["cartridge_case2"]],
        },
        "gun8": {
            "front": pygame.image.load(os.path.join(ASSET_DIR, "image", "Gun", "Gun8.png")).convert_alpha(),
            "topdown": images["gun8"],
            "bullets": [images["warhead1"]],
            "cartridges": [],
            "grenade": images["warhead1"],
            "explosion": images["explosion1"],
        },
        "gun9": {
            "front": pygame.image.load(os.path.join(ASSET_DIR, "image", "Gun", "Gun9.png")).convert_alpha(),
            "topdown": images["gun9"],
            "bullets": [
                [images["bullet1"]],
                [images["bullet2"]]
            ],
            "cartridges": [images["cartridge_case1"]],
        },
        "gun10": {
            "front": pygame.image.load(os.path.join(ASSET_DIR, "image", "Gun", "Gun10.png")).convert_alpha(),
            "topdown": images["gun10"],
            "bullets": [images["bullet1"]],
            "cartridges": [images["cartridge_case1"]],
        },
        "gun11": {
            "front": pygame.image.load(os.path.join(ASSET_DIR, "image", "Gun", "Gun11.png")).convert_alpha(),
            "topdown": images["gun11"],
            "bullets": [images["bullet1"]],
            "cartridges": [images["cartridge_case2"]],
        },
        "gun12": {
            "front": pygame.image.load(os.path.join(ASSET_DIR, "image", "Gun", "Gun12.png")).convert_alpha(),
            "topdown": images["gun12"],
            "bullets": [images["bullet1"]],
            "cartridges": [],
        },
        "gun13": {
            "front": pygame.image.load(os.path.join(ASSET_DIR, "image", "Gun", "Gun13.png")).convert_alpha(),
            "topdown": images["gun13"],
            "bullets": [images["bullet1"]],
            "cartridges": [images["cartridge_case1"]],
        },
        "gun14": {
            "front": pygame.image.load(os.path.join(ASSET_DIR, "image", "Gun", "Gun14.png")).convert_alpha(),
            "topdown": images["gun14"],
            "bullets": [images["bullet1"]],
            "cartridges": [images["cartridge_case1"]],
        },
        "gun15": {
            "front": pygame.image.load(os.path.join(ASSET_DIR, "image", "Gun", "Gun15.png")).convert_alpha(),
            "topdown": images["gun15"],
            "bullets": [images["bullet3"]],
            "cartridges": [],
        },
        "gun16": {
            "front": pygame.image.load(os.path.join(ASSET_DIR, "image", "Gun", "Gun16.png")).convert_alpha(),
            "topdown": images["gun16"],
            "bullets": [images["bullet1"]],
            "cartridges": [images["cartridge_case1"]],
        },
        "gun17": {
            "front": pygame.image.load(os.path.join(ASSET_DIR, "image", "Gun", "Gun17.png")).convert_alpha(),
            "topdown": images["gun17"],
            "bullets": [images["bullet1"]],
            "cartridges": [images["cartridge_case1"]],
        },
        "gun18": {
            "front": pygame.image.load(os.path.join(ASSET_DIR, "image", "Gun", "Gun18.png")).convert_alpha(),
            "topdown": images["gun18"],
            "bullets": [images["bullet1"]],
            "cartridges": [images["cartridge_case1"]],
        },
        "gun19": {
            "front": pygame.image.load(os.path.join(ASSET_DIR, "image", "Gun", "Gun19.png")).convert_alpha(),
            "topdown": images["gun19"],
            "bullets": [],
            "cartridges": [],
        },
        "gun20": {
            "front": pygame.image.load(os.path.join(ASSET_DIR, "image", "Gun", "Gun20.png")).convert_alpha(),
            "topdown": images["gun20"],
            "bullets": [images["hand_grenade"]],
            "cartridges": [],
            "explosion": images["explosion1"]
        },
    }
    return weapons