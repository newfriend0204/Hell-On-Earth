import pygame
import os

pygame.init()

# 📁 경로 상수
BASE_DIR = os.path.dirname(__file__)
ASSET_DIR = os.path.join(BASE_DIR, "Asset")
ASSET_UI_DIR = os.path.join(ASSET_DIR, "Image", "UI")
FONT_PATH = os.path.join(ASSET_DIR, "Font", "SUIT-Regular.ttf")

# 💬 폰트
KOREAN_FONT_18 = pygame.font.Font(FONT_PATH, 18)
KOREAN_FONT_28 = pygame.font.Font(FONT_PATH, 28)
KOREAN_FONT_36 = pygame.font.Font(FONT_PATH, 36)

# 무기 정보
gun_ids = ["gun3", "gun6", "gun1", "gun2"]
weapon_stats = {
    "gun1": {"name": "M1911", "power": 30, "spread": 10, "cost": 10, "rank": "1",
              "desc": "기본 권총. 탄환 소모량이 적고 반동이 적다.", "usage": "좌클릭: 단발 사격. 우클릭 없음."},
    "gun2": {"name": "AK47", "power": 20, "spread": 15, "cost": 7, "rank": "1",
              "desc": "자동 소총. 연사력이 뛰어나며 반동이 다소 있다.", "usage": "좌클릭: 자동 연사. 우클릭 없음."},
    "gun3": {"name": "Remington 870", "power": 10, "spread": 35, "cost": 15, "rank": "2",
              "desc": "산탄총. 근거리에서 강력한 데미지를 준다.\n14\134\n14\n1\n1\n1\n1\n1\n1", "usage": "좌클릭: 산탄 발사. 우클릭 없음."},
    "gun6": {"name": "개조된 기관단총", "power": 20, "spread": 8, "cost": 10, "rank": "3",
              "desc": "양손 사용 가능한 개조 SMG. 폭발탄 발사 가능.\nasdf\nasdf\nasdfasdf\nsdfasd\nasdfas", "usage": "좌클릭: 자동 사격 / 우클릭: 유탄 발사"},
}

# 이미지 로딩 함수
def load_ui_image(filename):
    return pygame.image.load(os.path.join(ASSET_UI_DIR, filename))

# 아이콘 및 배경 이미지 로딩
power_icon = pygame.transform.smoothscale(load_ui_image("Power.png"), (32, 32))
spread_icon = pygame.transform.smoothscale(load_ui_image("Spread.png"), (32, 32))
cost_icon = pygame.transform.smoothscale(load_ui_image("Cost.png"), (32, 32))
rank_icon = pygame.transform.smoothscale(load_ui_image("Rank.png"), (32, 32))
background_img = pygame.image.load(os.path.join(ASSET_UI_DIR, "Background.png"))

# 탭 UI
TAB_NAMES = ["내 상태", "무기1", "무기2", "무기3", "무기4"]
NUM_TABS = len(TAB_NAMES)
TAB_SIZE = (140, 140)
TAB_SPACING = -15

tab_images = {}
for i, name in enumerate(TAB_NAMES):
    key = "Status" if i == 0 else f"Weapon{i}"
    on_img = load_ui_image(f"{key}On.png")
    off_img = load_ui_image(f"{key}Off.png")
    tab_images[f"{key}On"] = pygame.transform.smoothscale(on_img, TAB_SIZE)
    tab_images[f"{key}Off"] = pygame.transform.smoothscale(off_img, TAB_SIZE)

def draw_tabs(screen, selected_tab):
    screen_width = screen.get_width()
    button_width, button_height = TAB_SIZE
    base_x = (screen_width - (button_width * NUM_TABS + TAB_SPACING * (NUM_TABS - 1))) // 2
    tab_rects = []
    mouse_pos = pygame.mouse.get_pos()

    for i in range(NUM_TABS):
        key = "Status" if i == 0 else f"Weapon{i}"
        is_hover = pygame.Rect(base_x + i * (button_width + TAB_SPACING), -40, button_width, button_height).collidepoint(mouse_pos)
        show_on = (i == selected_tab or is_hover)
        image = tab_images[f"{key}On"] if show_on else tab_images[f"{key}Off"]
        x = base_x + i * (button_width + TAB_SPACING)
        screen.blit(image, (x, -40))
        tab_rects.append(pygame.Rect(x, -40, button_width, button_height))

    return tab_rects

def draw_text_box(screen, x, y, w, h, text, font=KOREAN_FONT_18):
    box = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(box, (255, 255, 255, 200), box.get_rect(), border_radius=12)
    screen.blit(box, (x, y))
    for i, line in enumerate(text.split("\n")):
        surf = font.render(line, True, (0, 0, 0))
        screen.blit(surf, (x + 16, y + 16 + i * 28))

def draw_weapon_detail_ui(screen, selected_tab, weapons):
    screen.blit(pygame.transform.smoothscale(background_img, screen.get_size()), (0, 0))
    tab_rects = draw_tabs(screen, selected_tab)
    if selected_tab == 0:
        return tab_rects

    weapon_index = selected_tab - 1
    if weapon_index >= len(weapons):
        return tab_rects

    weapon = weapons[weapon_index]
    weapon_id = gun_ids[weapon_index]
    stat = weapon_stats[weapon_id]

    # 무기 이미지
    img = weapon.front_image
    max_w, max_h = 460, 230
    iw, ih = img.get_size()
    scale = min(max_w / iw, max_h / ih, 2.0)
    img = pygame.transform.smoothscale(img, (int(iw * scale), int(ih * scale)))
    screen.blit(img, (80, 140))

    # 무기 이름 + 스탯 박스
    box_w, box_h = 300, 200
    box_x, box_y = 80, 160 + img.get_height()
    draw_text_box(screen, box_x, box_y, box_w, box_h, "")
    name_surf = KOREAN_FONT_28.render(stat["name"], True, (0, 0, 0))
    screen.blit(name_surf, (box_x + 10, box_y + 10))
    icon_texts = [
        (power_icon, f"공격력: {stat['power']}"),
        (spread_icon, f"탄퍼짐: {stat['spread']}"),
        (cost_icon, f"소모량: {stat['cost']}"),
        (rank_icon, f"등급: {stat['rank']}"),
    ]
    y = box_y + 50
    for icon, text in icon_texts:
        screen.blit(icon, (box_x + 10, y))
        txt = KOREAN_FONT_28.render(text, True, (0, 0, 0))
        screen.blit(txt, (box_x + 50, y + 3))
        y += 40

    # 무기 설명 (상단)
    draw_text_box(screen, 520, 130, 380, 100, f"무기 설명\n{stat['desc']}")
    draw_text_box(screen, 520, 260, 380, 100, f"무기 사용법\n{stat['usage']}")

    return tab_rects

def handle_tab_click(pos, tab_rects):
    for i, rect in enumerate(tab_rects):
        if rect.collidepoint(pos):
            return i
    return None
