import pygame
import os
from config import *

def load_images():
    # 게임에서 사용하는 모든 이미지 로드 및 크기 조정
    path_image = lambda *paths: os.path.join(ASSET_DIR, *paths)

    # 플레이어 이미지 로드 및 크기 조정
    player_img = pygame.image.load(path_image("Image", "character", "MainCharacter.png")).convert_alpha()
    player_img = pygame.transform.smoothscale(player_img, (90, 90))

    # 무기별 상단(Top-down) 이미지 로드 및 스케일
    knife_img = pygame.image.load(path_image("Image", "Gun", "Knife.png")).convert_alpha()
    knife_img = pygame.transform.smoothscale(knife_img, (25, int(knife_img.get_height() * (25 / knife_img.get_width()))))

    gun1_img = pygame.image.load(path_image("Image", "Gun", "Gun1Player.png")).convert_alpha()
    gun1_img = pygame.transform.smoothscale(gun1_img, (30, int(gun1_img.get_height() * (30 / gun1_img.get_width()))))

    gun2_img = pygame.image.load(path_image("Image", "Gun", "Gun2Player.png")).convert_alpha()
    gun2_img = pygame.transform.smoothscale(gun2_img, (60, int(gun2_img.get_height() * (60 / gun2_img.get_width()))))

    gun3_img = pygame.image.load(path_image("Image", "Gun", "Gun3Player.png")).convert_alpha()
    gun3_img = pygame.transform.smoothscale(gun3_img, (70, int(gun3_img.get_height() * (70 / gun3_img.get_width()))))

    gun4_img = pygame.image.load(path_image("Image", "Gun", "Gun4Player.png")).convert_alpha()
    gun4_img = pygame.transform.smoothscale(gun4_img, (60, int(gun4_img.get_height() * (60 / gun4_img.get_width()))))

    gun5_img = pygame.image.load(path_image("Image", "Gun", "Gun5Player.png")).convert_alpha()
    gun5_img = pygame.transform.smoothscale(gun5_img, (65, int(gun5_img.get_height() * (65 / gun5_img.get_width()))))

    gun6_img = pygame.image.load(path_image("Image", "Gun", "Gun6Player.png")).convert_alpha()
    gun6_img = pygame.transform.smoothscale(gun6_img, (55, int(gun6_img.get_height() * (55 / gun6_img.get_width()))))

    gun7_img = pygame.image.load(path_image("Image", "Gun", "Gun7Player.png")).convert_alpha()
    gun7_img = pygame.transform.smoothscale(gun7_img, (80, int(gun7_img.get_height() * (80 / gun7_img.get_width()))))

    gun8_img = pygame.image.load(path_image("Image", "Gun", "Gun8Player.png")).convert_alpha()
    gun8_img = pygame.transform.smoothscale(gun8_img, (50, int(gun8_img.get_height() * (50 / gun8_img.get_width()))))

    gun9_img = pygame.image.load(path_image("Image", "Gun", "Gun9Player.png")).convert_alpha()
    gun9_img = pygame.transform.smoothscale(gun9_img, (50, int(gun9_img.get_height() * (50 / gun9_img.get_width()))))

    gun10_img = pygame.image.load(path_image("Image", "Gun", "Gun10Player.png")).convert_alpha()
    gun10_img = pygame.transform.smoothscale(gun10_img, (50, int(gun10_img.get_height() * (50 / gun10_img.get_width()))))

    gun11_img = pygame.image.load(path_image("Image", "Gun", "Gun10Player.png")).convert_alpha()
    gun11_img = pygame.transform.smoothscale(gun11_img, (50, int(gun11_img.get_height() * (50 / gun11_img.get_width()))))

    gun12_img = pygame.image.load(path_image("Image", "Gun", "Gun12Player.png")).convert_alpha()
    gun12_img = pygame.transform.smoothscale(gun12_img, (55, int(gun12_img.get_height() * (55 / gun12_img.get_width()))))

    gun13_img = pygame.image.load(path_image("Image", "Gun", "Gun13Player.png")).convert_alpha()
    gun13_img = pygame.transform.smoothscale(gun13_img, (55, int(gun13_img.get_height() * (55 / gun13_img.get_width()))))

    gun14_img = pygame.image.load(path_image("Image", "Gun", "Gun14Player.png")).convert_alpha()
    gun14_img = pygame.transform.smoothscale(gun14_img, (55, int(gun14_img.get_height() * (55 / gun14_img.get_width()))))

    gun15_img = pygame.image.load(path_image("Image", "Gun", "Gun15Player.png")).convert_alpha()
    gun15_img = pygame.transform.smoothscale(gun15_img, (55, int(gun15_img.get_height() * (55 / gun15_img.get_width()))))

    gun16_img = pygame.image.load(path_image("Image", "Gun", "Gun16Player.png")).convert_alpha()
    gun16_img = pygame.transform.smoothscale(gun16_img, (55, int(gun16_img.get_height() * (55 / gun16_img.get_width()))))

    gun17_img = pygame.image.load(path_image("Image", "Gun", "Gun17Player.png")).convert_alpha()
    gun17_img = pygame.transform.smoothscale(gun17_img, (55, int(gun17_img.get_height() * (55 / gun17_img.get_width()))))

    gun18_img = pygame.image.load(path_image("Image", "Gun", "Gun18Player.png")).convert_alpha()
    gun18_img = pygame.transform.smoothscale(gun18_img, (50, int(gun18_img.get_height() * (50 / gun18_img.get_width()))))

    gun19_img = pygame.image.load(path_image("Image", "Gun", "Gun19Player.png")).convert_alpha()
    gun19_img = pygame.transform.smoothscale(gun19_img, (100, int(gun19_img.get_height() * (100 / gun19_img.get_width()))))

    gun20_img = pygame.image.load(path_image("Image", "Gun", "Gun20Player.png")).convert_alpha()
    gun20_img = pygame.transform.smoothscale(gun20_img, (30, int(gun20_img.get_height() * (30 / gun20_img.get_width()))))

    gun21_img = pygame.image.load(path_image("Image", "Gun", "Gun21Player.png")).convert_alpha()
    gun21_img = pygame.transform.smoothscale(gun21_img, (55, int(gun21_img.get_height() * (55 / gun21_img.get_width()))))

    gun22_img = pygame.image.load(path_image("Image", "Gun", "Gun22Player.png")).convert_alpha()
    gun22_img = pygame.transform.smoothscale(gun22_img, (55, int(gun22_img.get_height() * (55 / gun22_img.get_width()))))

    gun23_img = pygame.image.load(path_image("Image", "Gun", "Gun23Player.png")).convert_alpha()
    gun23_img = pygame.transform.smoothscale(gun23_img, (55, int(gun23_img.get_height() * (55 / gun23_img.get_width()))))

    gun24_img = pygame.image.load(path_image("Image", "Gun", "Gun24Player.png")).convert_alpha()
    gun24_img = pygame.transform.smoothscale(gun24_img, (55, int(gun24_img.get_height() * (55 / gun24_img.get_width()))))

    gun25_img = pygame.image.load(path_image("Image", "Gun", "Gun25Player.png")).convert_alpha()
    gun25_img = pygame.transform.smoothscale(gun25_img, (55, int(gun25_img.get_height() * (55 / gun25_img.get_width()))))

    gun26_img = pygame.image.load(path_image("Image", "Gun", "Gun26Player.png")).convert_alpha()
    gun26_img = pygame.transform.smoothscale(gun26_img, (55, int(gun26_img.get_height() * (55 / gun26_img.get_width()))))

    gun27_img = pygame.image.load(path_image("Image", "Gun", "Gun27Player.png")).convert_alpha()
    gun27_img = pygame.transform.smoothscale(gun27_img, (55, int(gun27_img.get_height() * (55 / gun27_img.get_width()))))

    gun28_img = pygame.image.load(path_image("Image", "Gun", "Gun28Player.png")).convert_alpha()
    gun28_img = pygame.transform.smoothscale(gun28_img, (55, int(gun28_img.get_height() * (55 / gun28_img.get_width()))))

    gun29_img = pygame.image.load(path_image("Image", "Gun", "Gun29Player.png")).convert_alpha()
    gun29_img = pygame.transform.smoothscale(gun29_img, (55, int(gun29_img.get_height() * (55 / gun29_img.get_width()))))

    gun30_img = pygame.image.load(path_image("Image", "Gun", "Gun30Player.png")).convert_alpha()
    gun30_img = pygame.transform.smoothscale(gun30_img, (55, int(gun30_img.get_height() * (55 / gun30_img.get_width()))))

    gun31_img = pygame.image.load(path_image("Image", "Gun", "Gun31Player.png")).convert_alpha()
    gun31_img = pygame.transform.smoothscale(gun31_img, (55, int(gun31_img.get_height() * (55 / gun31_img.get_width()))))

    gun32_img = pygame.image.load(path_image("Image", "Gun", "Gun32Player.png")).convert_alpha()
    gun32_img = pygame.transform.smoothscale(gun32_img, (55, int(gun32_img.get_height() * (55 / gun32_img.get_width()))))

    gun33_img = pygame.image.load(path_image("Image", "Gun", "Gun33Player.png")).convert_alpha()
    gun33_img = pygame.transform.smoothscale(gun33_img, (55, int(gun33_img.get_height() * (55 / gun33_img.get_width()))))

    gun34_img = pygame.image.load(path_image("Image", "Gun", "Gun34Player.png")).convert_alpha()
    gun34_img = pygame.transform.smoothscale(gun34_img, (55, int(gun34_img.get_height() * (55 / gun34_img.get_width()))))

    gun35_img = pygame.image.load(path_image("Image", "Gun", "Gun35Player.png")).convert_alpha()
    gun35_img = pygame.transform.smoothscale(gun35_img, (55, int(gun35_img.get_height() * (55 / gun35_img.get_width()))))

    gun36_img = pygame.image.load(path_image("Image", "Gun", "Gun36Player.png")).convert_alpha()
    gun36_img = pygame.transform.smoothscale(gun36_img, (55, int(gun36_img.get_height() * (55 / gun36_img.get_width()))))

    gun37_img = pygame.image.load(path_image("Image", "Gun", "Gun37Player.png")).convert_alpha()
    gun37_img = pygame.transform.smoothscale(gun37_img, (55, int(gun37_img.get_height() * (55 / gun37_img.get_width()))))


    boss1gun1_img = pygame.image.load(path_image("Image", "Gun", "Boss1Gun1.png")).convert_alpha()
    boss1gun1_img = pygame.transform.smoothscale(boss1gun1_img, (50, int(boss1gun1_img.get_height() * (50 / boss1gun1_img.get_width()))))

    boss1gun2_img = pygame.image.load(path_image("Image", "Gun", "Boss1Gun2.png")).convert_alpha()
    boss1gun2_img = pygame.transform.smoothscale(boss1gun2_img, (50, int(boss1gun2_img.get_height() * (50 / boss1gun2_img.get_width()))))

    warhead_img = pygame.image.load(path_image("Image", "Gun", "Warhead1.png")).convert_alpha()
    warhead_img = pygame.transform.smoothscale(warhead_img, (40, 40))

    grenade_img = pygame.image.load(path_image("Image", "Gun", "LauncherGrenade1.png")).convert_alpha()
    grenade_img = pygame.transform.smoothscale(grenade_img, (30, 30))

    hand_grenade_img = pygame.image.load(path_image("Image", "Gun", "Gun20.png")).convert_alpha()
    hand_grenade_img = pygame.transform.smoothscale(hand_grenade_img, (30, 30))

    explosion_img = pygame.image.load(path_image("Image", "Gun", "Explosion.png")).convert_alpha()
    explosion_img = pygame.transform.smoothscale(explosion_img, (200, 200))

    mine_img = pygame.image.load(path_image("Image", "entity", "Mine.png")).convert_alpha()
    mine_img = pygame.transform.smoothscale(mine_img, (36, 36))

    # 탄환 이미지 크기 조정
    bullet1_img = pygame.image.load(path_image("Image", "Gun", "Bullet1.png")).convert_alpha()
    scale_factor = 60 / bullet1_img.get_width()
    bullet1_img = pygame.transform.smoothscale(
        bullet1_img,
        (
            int(bullet1_img.get_width() * scale_factor),
            int(bullet1_img.get_height() * scale_factor)
        )
    )
    bullet2_img = pygame.image.load(path_image("Image", "Gun", "Bullet2.png")).convert_alpha()
    scale_factor = 40 / bullet2_img.get_width()
    bullet2_img = pygame.transform.smoothscale(
        bullet2_img,
        (
            int(bullet2_img.get_width() * scale_factor),
            int(bullet2_img.get_height() * scale_factor)
        )
    )
    bullet3_img = pygame.image.load(path_image("Image", "Gun", "Bullet3.png")).convert_alpha()
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

    cartridge_case_img1 = pygame.image.load(path_image("Image", "Gun", "CartridgeCase1.png")).convert_alpha()
    cartridge_case_img1 = pygame.transform.smoothscale(
        cartridge_case_img1,
        (2, int(cartridge_case_img1.get_height() * 4 / cartridge_case_img1.get_width()))
    )
    cartridge_case_img2 = pygame.image.load(path_image("Image", "Gun", "CartridgeCase2.png")).convert_alpha()
    cartridge_case_img2 = pygame.transform.smoothscale(
        cartridge_case_img2,
        (20, int(cartridge_case_img2.get_height() * 20 / cartridge_case_img2.get_width()))
    )

    cursor_img = pygame.image.load(path_image("Image", "MouseCursor.png")).convert_alpha()
    cursor_img = pygame.transform.smoothscale(cursor_img, (32, 32))

    portal_img = pygame.image.load(path_image("Image", "Entity", "Portal.png")).convert_alpha()
    portal_img = pygame.transform.smoothscale(portal_img, (64, 64))

    bg_img = pygame.image.load(path_image("Image", "Map1.png")).convert()
    bg_img = pygame.transform.smoothscale(bg_img, (BG_WIDTH, BG_HEIGHT))
    bg_img2 = pygame.image.load(path_image("Image", "Map2.png")).convert()
    bg_img2 = pygame.transform.smoothscale(bg_img2, (BG_WIDTH, BG_HEIGHT))
    bg_img3 = pygame.image.load(path_image("Image", "Map3.png")).convert()
    bg_img3 = pygame.transform.smoothscale(bg_img3, (BG_WIDTH, BG_HEIGHT))

    wall_barrier_img = pygame.image.load(path_image("Image", "Map1Wall.png")).convert_alpha()
    scale_factor = 0.275 * PLAYER_VIEW_SCALE
    wall_barrier_img = pygame.transform.smoothscale(wall_barrier_img, (
        int(wall_barrier_img.get_width() * scale_factor),
        int(wall_barrier_img.get_height() * scale_factor)
    ))
    wall_barrier_img_rotated = pygame.transform.rotate(wall_barrier_img, 90)
    wall_barrier_img2 = pygame.image.load(path_image("Image", "Map2Wall.png")).convert_alpha()
    wall_barrier_img2 = pygame.transform.smoothscale(wall_barrier_img2, (
        int(wall_barrier_img2.get_width() * scale_factor),
        int(wall_barrier_img2.get_height() * scale_factor)
    ))
    wall_barrier_img2_rotated = pygame.transform.rotate(wall_barrier_img2, 90)

    wall_barrier_img_rotated = pygame.transform.rotate(wall_barrier_img, 90)
    wall_barrier_img3 = pygame.image.load(path_image("Image", "Map3Wall.png")).convert_alpha()
    wall_barrier_img3 = pygame.transform.smoothscale(wall_barrier_img3, (
        int(wall_barrier_img3.get_width() * scale_factor),
        int(wall_barrier_img3.get_height() * scale_factor)
    ))
    wall_barrier_img3_rotated = pygame.transform.rotate(wall_barrier_img3, 90)

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
        "Vehicle1.png": (1536, 768),
        "Vehicle2.png": (1536, 768),
        "Vehicle3.png": (1536, 768),
        "Vehicle4.png": (1536, 768),
        "Barricade1.png": (1536, 384),
        "Dump1.png": (1024, 1024),
        "Dump2.png": (1024, 1024),
        "ElectricBox1.png": (768, 768),
        "FirePlug1.png": (384, 384),
        "Hole1.png": (1024, 1024),
        "TrashCan1.png": (768, 768),
        "Altar1.png": (1024, 1024),
        "Altar2.png": (1024, 1024),
        "BrokenStoneStatue1.png": (1024, 1280),
        "Coffin1.png": (1536, 768),
        "Coffin2.png": (1536, 768),
        "LavaPond1.png": (1536, 1024),
        "LavaStone1.png": (1024, 1024),
        "LavaStone2.png": (1024, 1024),
        "Skull1.png": (1024, 1024),
        "Skull2.png": (1024, 1024),
        "Skull3.png": (1024, 1024),
    }

    # 장애물 이미지 및 마스크 로드
    obstacle_dir = path_image("Image", "Obstacle")
    obstacle_images = {}
    obstacle_masks = {}

    if os.path.exists(obstacle_dir):
        for filename in os.listdir(obstacle_dir):
            if filename in obstacle_sizes:
                img_path = os.path.join(obstacle_dir, filename)
                orig = pygame.image.load(img_path).convert_alpha()

                box_w, box_h = obstacle_sizes[filename]
                sx = box_w / orig.get_width()
                sy = box_h / orig.get_height()
                s = min(1.0, sx, sy)

                new_size = (int(orig.get_width() * s), int(orig.get_height() * s))
                image = pygame.transform.smoothscale(orig, new_size)

                obstacle_images[filename] = image
                obstacle_masks[filename] = pygame.mask.from_surface(image)

    # 캐릭터 이미지 로드
    merchant1_img = pygame.image.load(path_image("Image", "character", "Merchant1.png")).convert_alpha()
    merchant1_img = pygame.transform.smoothscale(merchant1_img, (90, 90))

    doctorNF_img = pygame.image.load(path_image("Image", "character", "DoctorNF.png")).convert_alpha()
    doctorNF_img = pygame.transform.smoothscale(doctorNF_img, (90, 90))

    soldier1_img = pygame.image.load(path_image("Image", "character", "Soilder1.png")).convert_alpha()
    soldier1_img = pygame.transform.smoothscale(soldier1_img, (90, 90))

    soldier2_img = pygame.image.load(path_image("Image", "character", "Soilder2.png")).convert_alpha()
    soldier2_img = pygame.transform.smoothscale(soldier2_img, (90, 90))

    soldier3_img = pygame.image.load(path_image("Image", "character", "Soilder3.png")).convert_alpha()
    soldier3_img = pygame.transform.smoothscale(soldier3_img, (90, 90))

    scientist1_img = pygame.image.load(path_image("Image", "character", "Scientist1.png")).convert_alpha()
    scientist1_img = pygame.transform.smoothscale(scientist1_img, (90, 90))

    scientist2_img = pygame.image.load(path_image("Image", "character", "Scientist2.png")).convert_alpha()
    scientist2_img = pygame.transform.smoothscale(scientist2_img, (90, 90))

    scientist3_img = pygame.image.load(path_image("Image", "character", "Scientist3.png")).convert_alpha()
    scientist3_img = pygame.transform.smoothscale(scientist3_img, (90, 90))

    enemy1_img = pygame.image.load(path_image("Image", "character", "Enemy1.png")).convert_alpha()
    enemy1_img = pygame.transform.smoothscale(enemy1_img, (90, 90))

    enemy2_img = pygame.image.load(path_image("Image", "character", "Enemy2.png")).convert_alpha()
    enemy2_img = pygame.transform.smoothscale(enemy2_img, (90, 90))

    enemy3_img = pygame.image.load(path_image("Image", "character", "Enemy3.png")).convert_alpha()
    enemy3_img = pygame.transform.smoothscale(enemy3_img, (117, 117))

    enemy4_img = pygame.image.load(path_image("Image", "character", "Enemy4.png")).convert_alpha()
    enemy4_img = pygame.transform.smoothscale(enemy4_img, (108, 108))

    enemy5_img = pygame.image.load(path_image("Image", "character", "Enemy5.png")).convert_alpha()
    enemy5_img = pygame.transform.smoothscale(enemy5_img, (90, 90))

    enemy6_img = pygame.image.load(path_image("Image", "character", "Enemy6.png")).convert_alpha()
    enemy6_img = pygame.transform.smoothscale(enemy6_img, (150, 150))

    enemy7_img = pygame.image.load(path_image("Image", "character", "Enemy7.png")).convert_alpha()
    enemy7_img = pygame.transform.smoothscale(enemy7_img, (120, 120))

    enemy8_img = pygame.image.load(path_image("Image", "character", "Enemy8.png")).convert_alpha()
    enemy8_img = pygame.transform.smoothscale(enemy8_img, (90, 90))

    enemy9_img = pygame.image.load(path_image("Image", "character", "Enemy9.png")).convert_alpha()
    enemy9_img = pygame.transform.smoothscale(enemy9_img, (90, 90))

    enemy10_img = pygame.image.load(path_image("Image", "character", "Enemy10.png")).convert_alpha()
    enemy10_img = pygame.transform.smoothscale(enemy10_img, (90, 90))

    enemy11_img = pygame.image.load(path_image("Image", "character", "Enemy11.png")).convert_alpha()
    enemy11_img = pygame.transform.smoothscale(enemy11_img, (110, 110))

    enemy12_img = pygame.image.load(path_image("Image", "character", "Enemy12.png")).convert_alpha()
    enemy12_img = pygame.transform.smoothscale(enemy12_img, (90, 90))

    enemy13_img = pygame.image.load(path_image("Image", "character", "Enemy13.png")).convert_alpha()
    enemy13_img = pygame.transform.smoothscale(enemy13_img, (100, 100))

    enemy14_img = pygame.image.load(path_image("Image", "character", "Enemy14.png")).convert_alpha()
    enemy14_img = pygame.transform.smoothscale(enemy14_img, (90, 90))

    enemy15_img = pygame.image.load(path_image("Image", "character", "Enemy15.png")).convert_alpha()
    enemy15_img = pygame.transform.smoothscale(enemy15_img, (90, 90))

    enemy16_img = pygame.image.load(path_image("Image", "character", "Enemy16.png")).convert_alpha()
    enemy16_img = pygame.transform.smoothscale(enemy16_img, (90, 90))

    enemy17_img = pygame.image.load(path_image("Image", "character", "Enemy17.png")).convert_alpha()
    enemy17_img = pygame.transform.smoothscale(enemy17_img, (90, 90))

    enemy18_img = pygame.image.load(path_image("Image", "character", "Enemy18.png")).convert_alpha()
    enemy18_img = pygame.transform.smoothscale(enemy18_img, (90, 90))

    enemy19_img = pygame.image.load(path_image("Image", "character", "Enemy19.png")).convert_alpha()
    enemy19_img = pygame.transform.smoothscale(enemy19_img, (110, 110))

    enemy20_img = pygame.image.load(path_image("Image", "character", "Enemy20.png")).convert_alpha()
    enemy20_img = pygame.transform.smoothscale(enemy20_img, (110, 110))

    enemy21_img = pygame.image.load(path_image("Image", "character", "Enemy21.png")).convert_alpha()
    enemy21_img = pygame.transform.smoothscale(enemy21_img, (90, 90))

    enemy22_img = pygame.image.load(path_image("Image", "character", "Enemy22.png")).convert_alpha()
    enemy22_img = pygame.transform.smoothscale(enemy22_img, (90, 90))

    enemy23_img = pygame.image.load(path_image("Image", "character", "Enemy23.png")).convert_alpha()
    enemy23_img = pygame.transform.smoothscale(enemy23_img, (90, 90))

    enemy24_img = pygame.image.load(path_image("Image", "character", "Enemy24.png")).convert_alpha()
    enemy24_img = pygame.transform.smoothscale(enemy24_img, (90, 90))

    enemy24_cocoon_img = pygame.image.load(path_image("Image", "character", "Enemy24Cocoon.png")).convert_alpha()
    enemy24_cocoon_img = pygame.transform.smoothscale(enemy24_cocoon_img, (90, 90))

    enemy25_img = pygame.image.load(path_image("Image", "character", "Enemy25.png")).convert_alpha()
    enemy25_img = pygame.transform.smoothscale(enemy25_img, (120, 120))

    enemy26_img = pygame.image.load(path_image("Image", "character", "Enemy26.png")).convert_alpha()
    enemy26_img = pygame.transform.smoothscale(enemy26_img, (90, 90))

    enemy27_img = pygame.image.load(path_image("Image", "character", "Enemy27.png")).convert_alpha()
    enemy27_img = pygame.transform.smoothscale(enemy27_img, (90, 90))

    boss1_img = pygame.image.load(path_image("Image", "character", "Boss1.png")).convert_alpha()
    boss1_img = pygame.transform.smoothscale(boss1_img, (120, 120))

    boss2_img = pygame.image.load(path_image("Image", "character", "Boss2.png")).convert_alpha()
    boss2_img = pygame.transform.smoothscale(boss2_img, (120, 120))

    boss3_img = pygame.image.load(path_image("Image", "character", "Boss3.png")).convert_alpha()
    boss3_img = pygame.transform.smoothscale(boss3_img, (120, 120))

    boss4_img = pygame.image.load(path_image("Image", "character", "Boss4.png")).convert_alpha()
    boss4_img = pygame.transform.smoothscale(boss4_img, (120, 120))

    drone_img = pygame.image.load(path_image("Image", "entity", "Drone.png")).convert_alpha()
    drone_img = pygame.transform.smoothscale(drone_img, (60, 60))

    fireball_img = pygame.image.load(path_image("Image", "entity", "Fireball.png")).convert_alpha()
    fireball_img = pygame.transform.smoothscale(fireball_img, (100, 50))

    flame_pillar_img = pygame.image.load(path_image("Image", "entity", "FirePillar.png")).convert_alpha()
    flame_pillar_img = pygame.transform.smoothscale(flame_pillar_img, (300, 300))

    hammer_img = pygame.image.load(path_image("Image", "entity", "Hammer.png")).convert_alpha()
    hammer_img = pygame.transform.smoothscale(hammer_img, (50, 100))

    anvil_img = pygame.image.load(path_image("Image", "entity", "Anvil.png")).convert_alpha()
    anvil_img = pygame.transform.smoothscale(anvil_img, (60, 60))

    electric_grenade_img = pygame.image.load(path_image("Image", "entity", "ElectricGrenade.png")).convert_alpha()
    electric_grenade_img = pygame.transform.smoothscale(electric_grenade_img, (60, 60))

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
        "knife": knife_img,
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
        "gun21": gun21_img,
        "gun22": gun22_img,
        "gun23": gun23_img,
        "gun24": gun24_img,
        "gun25": gun25_img,
        "gun26": gun26_img,
        "gun27": gun27_img,
        "gun28": gun28_img,
        "gun29": gun29_img,
        "gun30": gun30_img,
        "gun31": gun31_img,
        "gun32": gun32_img,
        "gun33": gun33_img,
        "gun34": gun34_img,
        "gun35": gun35_img,
        "gun36": gun36_img,
        "gun37": gun37_img,
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
        "soldier1": soldier1_img,
        "soldier2": soldier2_img,
        "soldier3": soldier3_img,
        "scientist1": scientist1_img,
        "scientist2": scientist2_img,
        "scientist3": scientist3_img,
        "enemy1": enemy1_img,
        "enemy2": enemy2_img,
        "enemy3": enemy3_img,
        "enemy4": enemy4_img,
        "enemy5": enemy5_img,
        "enemy6": enemy6_img,
        "enemy7": enemy7_img,
        "enemy8": enemy8_img,
        "enemy9": enemy9_img,
        "enemy10": enemy10_img,
        "enemy11": enemy11_img,
        "enemy12": enemy12_img,
        "enemy13": enemy13_img,
        "enemy14": enemy14_img,
        "enemy15": enemy15_img,
        "enemy16": enemy16_img,
        "enemy17": enemy17_img,
        "enemy18": enemy18_img,
        "enemy19": enemy19_img,
        "enemy20": enemy20_img,
        "enemy21": enemy21_img,
        "enemy22": enemy22_img,
        "enemy23": enemy23_img,
        "enemy24": enemy24_img,
        "enemy24_cocoon": enemy24_cocoon_img,
        "enemy25": enemy25_img,
        "enemy26": enemy26_img,
        "enemy27": enemy27_img,
        "boss1": boss1_img,
        "boss2": boss2_img,
        "boss3": boss3_img,
        "boss4": boss4_img,
        "drone": drone_img,
        "fireball": fireball_img,
        "flame_pillar": flame_pillar_img,
        "hammer": hammer_img,
        "anvil": anvil_img,
        "electric_grenade": electric_grenade_img,
        "acid_projectile": acid_projectile_img,
        "acid_pool": acid_pool_img,
        "mine": mine_img,
        "ammo_gauge_up": ammo_gauge_up_img,
        "health_up": health_up_img,
        "cursor": cursor_img,
        "background": bg_img,
        "wall_barrier": wall_barrier_img,
        "wall_barrier_rotated": wall_barrier_img_rotated,
        "background_map1": bg_img,
        "background_map2": bg_img2,
        "background_map3": bg_img3,
        "wall_barrier_map1": wall_barrier_img,
        "wall_barrier_map1_rotated": wall_barrier_img_rotated,
        "wall_barrier_map2": wall_barrier_img2,
        "wall_barrier_map2_rotated": wall_barrier_img2_rotated,
        "wall_barrier_map3": wall_barrier_img3,
        "wall_barrier_map3_rotated": wall_barrier_img3_rotated,
        "portal": portal_img,
        "background": bg_img,
        "obstacles": obstacle_images,
        "obstacle_masks": obstacle_masks,
    }

def load_weapon_assets(images):
    # 무기별 전방(Front) 이미지, 상단(Top-down) 이미지, 탄환, 탄피, 폭발 이미지 설정
    weapons = {
        "knife": {
            "front": images["knife"],
            "topdown": images["knife"],
            "bullets": [],
            "cartridges": [],
        },
        "gun1": {
            "front": pygame.image.load(os.path.join(ASSET_DIR, "Image", "Gun", "Gun1.png")).convert_alpha(),
            "topdown": images["gun1"],
            "bullets": [images["bullet1"]],
            "cartridges": [images["cartridge_case1"]],
        },
        "gun2": {
            "front": pygame.image.load(os.path.join(ASSET_DIR, "Image", "Gun", "Gun2.png")).convert_alpha(),
            "topdown": images["gun2"],
            "bullets": [images["bullet1"]],
            "cartridges": [images["cartridge_case1"]],
        },
        "gun3": {
            "front": pygame.image.load(os.path.join(ASSET_DIR, "Image", "Gun", "Gun3.png")).convert_alpha(),
            "topdown": images["gun3"],
            "bullets": [images["bullet1"]],
            "cartridges": [images["cartridge_case2"]],
        },
        "gun4": {
            "front": pygame.image.load(os.path.join(ASSET_DIR, "Image", "Gun", "Gun4.png")).convert_alpha(),
            "topdown": images["gun4"],
            "bullets": [images["grenade1"]],
            "cartridges": [],
            "grenade": images["grenade1"],
            "explosion": images["explosion1"],
        },
        "gun5": {
            "front": pygame.image.load(os.path.join(ASSET_DIR, "Image", "Gun", "Gun5.png")).convert_alpha(),
            "topdown": images["gun5"],
            "bullets": [pygame.transform.smoothscale(
                images["bullet1"],
                (images["bullet1"].get_width() // 2, images["bullet1"].get_height() // 2)
            )],
            "cartridges": [images["cartridge_case1"]],
        },
        "gun6": {
            "front": pygame.image.load(os.path.join(ASSET_DIR, "Image", "Gun", "Gun6.png")).convert_alpha(),
            "topdown": images["gun6"],
            "bullets": [images["bullet1"]],
            "cartridges": [images["cartridge_case1"]],
            "grenade": images["grenade1"],
            "explosion": images["explosion1"],
        },
        "gun7": {
            "front": pygame.image.load(os.path.join(ASSET_DIR, "Image", "Gun", "Gun7.png")).convert_alpha(),
            "topdown": images["gun7"],
            "bullets": [images["bullet1"]],
            "cartridges": [images["cartridge_case1"], images["cartridge_case2"]],
        },
        "gun8": {
            "front": pygame.image.load(os.path.join(ASSET_DIR, "Image", "Gun", "Gun8.png")).convert_alpha(),
            "topdown": images["gun8"],
            "bullets": [images["warhead1"]],
            "cartridges": [],
            "grenade": images["warhead1"],
            "explosion": images["explosion1"],
        },
        "gun9": {
            "front": pygame.image.load(os.path.join(ASSET_DIR, "Image", "Gun", "Gun9.png")).convert_alpha(),
            "topdown": images["gun9"],
            "bullets": [
                [images["bullet1"]],
                [images["bullet2"]]
            ],
            "cartridges": [images["cartridge_case1"]],
        },
        "gun10": {
            "front": pygame.image.load(os.path.join(ASSET_DIR, "Image", "Gun", "Gun10.png")).convert_alpha(),
            "topdown": images["gun10"],
            "bullets": [images["bullet1"]],
            "cartridges": [images["cartridge_case1"]],
        },
        "gun11": {
            "front": pygame.image.load(os.path.join(ASSET_DIR, "Image", "Gun", "Gun11.png")).convert_alpha(),
            "topdown": images["gun11"],
            "bullets": [images["bullet1"]],
            "cartridges": [images["cartridge_case2"]],
        },
        "gun12": {
            "front": pygame.image.load(os.path.join(ASSET_DIR, "Image", "Gun", "Gun12.png")).convert_alpha(),
            "topdown": images["gun12"],
            "bullets": [images["bullet1"]],
            "cartridges": [],
        },
        "gun13": {
            "front": pygame.image.load(os.path.join(ASSET_DIR, "Image", "Gun", "Gun13.png")).convert_alpha(),
            "topdown": images["gun13"],
            "bullets": [images["bullet1"]],
            "cartridges": [images["cartridge_case1"]],
        },
        "gun14": {
            "front": pygame.image.load(os.path.join(ASSET_DIR, "Image", "Gun", "Gun14.png")).convert_alpha(),
            "topdown": images["gun14"],
            "bullets": [images["bullet1"]],
            "cartridges": [images["cartridge_case1"]],
        },
        "gun15": {
            "front": pygame.image.load(os.path.join(ASSET_DIR, "Image", "Gun", "Gun15.png")).convert_alpha(),
            "topdown": images["gun15"],
            "bullets": [images["bullet3"]],
            "cartridges": [],
        },
        "gun16": {
            "front": pygame.image.load(os.path.join(ASSET_DIR, "Image", "Gun", "Gun16.png")).convert_alpha(),
            "topdown": images["gun16"],
            "bullets": [images["bullet1"]],
            "cartridges": [images["cartridge_case1"]],
        },
        "gun17": {
            "front": pygame.image.load(os.path.join(ASSET_DIR, "Image", "Gun", "Gun17.png")).convert_alpha(),
            "topdown": images["gun17"],
            "bullets": [images["bullet1"]],
            "cartridges": [images["cartridge_case1"]],
        },
        "gun18": {
            "front": pygame.image.load(os.path.join(ASSET_DIR, "Image", "Gun", "Gun18.png")).convert_alpha(),
            "topdown": images["gun18"],
            "bullets": [images["bullet1"]],
            "cartridges": [images["cartridge_case1"]],
        },
        "gun19": {
            "front": pygame.image.load(os.path.join(ASSET_DIR, "Image", "Gun", "Gun19.png")).convert_alpha(),
            "topdown": images["gun19"],
            "bullets": [],
            "cartridges": [],
        },
        "gun20": {
            "front": pygame.image.load(os.path.join(ASSET_DIR, "Image", "Gun", "Gun20.png")).convert_alpha(),
            "topdown": images["gun20"],
            "bullets": [images["hand_grenade"]],
            "cartridges": [],
            "explosion": images["explosion1"]
        },
        "gun21": {
            "front": pygame.image.load(os.path.join(ASSET_DIR, "Image", "Gun", "Gun21.png")).convert_alpha(),
            "topdown": images["gun21"],
            "bullets": [images["bullet1"]],
            "cartridges": [images["cartridge_case1"]],
        },
        "gun22": {
            "front": pygame.image.load(os.path.join(ASSET_DIR, "Image", "Gun", "Gun22.png")).convert_alpha(),
            "topdown": images["gun22"],
            "bullets": [images["bullet1"]],
            "cartridges": [images["cartridge_case1"]],
        },
        "gun23": {
            "front": pygame.image.load(os.path.join(ASSET_DIR, "Image", "Gun", "Gun23.png")).convert_alpha(),
            "topdown": images["gun23"],
            "bullets": [images["bullet1"]],
            "cartridges": [images["cartridge_case1"]],
        },
        "gun24": {
            "front": pygame.image.load(os.path.join(ASSET_DIR, "Image", "Gun", "Gun24.png")).convert_alpha(),
            "topdown": images["gun24"],
            "bullets": [images["bullet1"]],
            "cartridges": [images["cartridge_case1"]],
        },
        "gun25": {
            "front": pygame.image.load(os.path.join(ASSET_DIR, "Image", "Gun", "Gun25.png")).convert_alpha(),
            "topdown": images["gun25"],
            "bullets": [images["bullet1"]],
            "cartridges": [images["cartridge_case1"]],
        },
        "gun26": {
            "front": pygame.image.load(os.path.join(ASSET_DIR, "Image", "Gun", "Gun26.png")).convert_alpha(),
            "topdown": images["gun26"],
            "bullets": [images["bullet1"]],
            "cartridges": [images["cartridge_case1"]],
        },
        "gun27": {
            "front": pygame.image.load(os.path.join(ASSET_DIR, "Image", "Gun", "Gun27.png")).convert_alpha(),
            "topdown": images["gun27"],
            "bullets": [],
            "cartridges": [],
        },
        "gun28": {
            "front": pygame.image.load(os.path.join(ASSET_DIR, "Image", "Gun", "Gun28.png")).convert_alpha(),
            "topdown": images["gun28"],
            "bullets": [],
            "cartridges": [],
        },
        "gun29": {
            "front": pygame.image.load(os.path.join(ASSET_DIR, "Image", "Gun", "Gun29.png")).convert_alpha(),
            "topdown": images["gun29"],
            "bullets": [],
            "cartridges": [],
        },
        "gun30": {
            "front": pygame.image.load(os.path.join(ASSET_DIR, "Image", "Gun", "Gun30.png")).convert_alpha(),
            "topdown": images["gun30"],
            "bullets": [],
            "cartridges": [],
        },
        "gun31": {
            "front": pygame.image.load(os.path.join(ASSET_DIR, "Image", "Gun", "Gun31.png")).convert_alpha(),
            "topdown": images["gun31"],
            "bullets": [images["grenade1"]],
            "cartridges": [],
        },
        "gun32": {
            "front": pygame.image.load(os.path.join(ASSET_DIR, "Image", "Gun", "Gun32.png")).convert_alpha(),
            "topdown": images["gun32"],
            "bullets": [images["bullet1"]],
            "cartridges": [],
        },
    }
    return weapons