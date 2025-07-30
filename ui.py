import pygame
import os

pygame.init()

BASE_DIR = os.path.dirname(__file__)
ASSET_DIR = os.path.join(BASE_DIR, "Asset")
ASSET_UI_DIR = os.path.join(ASSET_DIR, "Image", "UI")
FONT_PATH = os.path.join(ASSET_DIR, "Font", "SUIT-Regular.ttf")
BOLD_FONT_PATH = os.path.join(ASSET_DIR, "Font", "SUIT-Bold.ttf")

KOREAN_FONT_18 = pygame.font.Font(FONT_PATH, 18)
KOREAN_FONT_28 = pygame.font.Font(FONT_PATH, 28)
KOREAN_FONT_BOLD_28 = pygame.font.Font(BOLD_FONT_PATH, 28)

TAB_NAMES = ["내 상태", "무기1", "무기2", "무기3", "무기4"]
TAB_SIZE = (140, 140)
TAB_SPACING = -15
NUM_TABS = len(TAB_NAMES)

gun_ids = ["gun3", "gun6", "gun1", "gun2"]
weapon_stats = {
    # 무기별 스탯 및 설명, 사용법
    "gun1": {"name": "M1911", "power": 30, "spread": 10, "cost": 10, "rank": "1", "desc": "NF 코퍼레이션이 지급하는 기본 권총입니다. 모든 경비들이 차고다닙니다.", "usage": "좌클릭\n단발사격\n\n우클릭\n없음."},
    "gun2": {"name": "AK47", "power": 20, "spread": 15, "cost": 7, "rank": "1", "desc": "NF 코퍼레이션이 군인들에게 지급하는 기본 소총입니다.", "usage": "좌클릭\n연사\n\n우클릭\n없음."},
    "gun3": {"name": "Remington 870", "power": 10, "spread": 35, "cost": 15, "rank": "2", "desc": "사거리가 다른 샷건들보단 짧지만, 강력한 위력을 자랑합니다.", "usage": "좌클릭\n15발 동시 사격\n\n우클릭\n없음."},
    "gun6": {"name": "개조된 기관단총", "power": 20, "spread": "좌클릭:8 우클릭:0", "cost": 10, "rank": "3", "desc": "빠루를 든 사내가 애용하는 기관단총입니다. 우클릭 시 유탄을 발사해 큰 피해를 입힐 수 있습니다.", "usage": "좌클릭\n연사\n\n우클릭\n사거리가 짧은 유탄을 발사합니다."},
}

def load_ui_image(filename):
    return pygame.image.load(os.path.join(ASSET_UI_DIR, filename))

power_icon = pygame.transform.smoothscale(load_ui_image("Power.png"), (32, 32))
spread_icon = pygame.transform.smoothscale(load_ui_image("Spread.png"), (32, 32))
cost_icon = pygame.transform.smoothscale(load_ui_image("Cost.png"), (32, 32))
rank_icon = pygame.transform.smoothscale(load_ui_image("Rank.png"), (32, 32))
background_img = pygame.image.load(os.path.join(ASSET_UI_DIR, "Background.png"))

tab_images = {}
for i, name in enumerate(TAB_NAMES):
    key = "Status" if i == 0 else f"Weapon{i}"
    tab_images[f"{key}On"] = pygame.transform.smoothscale(load_ui_image(f"{key}On.png"), TAB_SIZE)
    tab_images[f"{key}Off"] = pygame.transform.smoothscale(load_ui_image(f"{key}Off.png"), TAB_SIZE)

hovered_states = [False] * NUM_TABS

def draw_tabs(screen, selected_tab, sounds):
    # 상단 탭 UI 그리기
    screen_width = screen.get_width()
    base_x = (screen_width - (TAB_SIZE[0] * NUM_TABS + TAB_SPACING * (NUM_TABS - 1))) // 2
    tab_rects = []
    mouse_pos = pygame.mouse.get_pos()

    for i in range(NUM_TABS):
        key = "Status" if i == 0 else f"Weapon{i}"
        rect = pygame.Rect(base_x + i * (TAB_SIZE[0] + TAB_SPACING), -40, *TAB_SIZE)
        is_hover = rect.collidepoint(mouse_pos)
        show_on = (i == selected_tab or is_hover)
        image = tab_images[f"{key}On"] if show_on else tab_images[f"{key}Off"]
        screen.blit(image, (rect.x, rect.y))
        tab_rects.append(rect)

        global hovered_states
        if is_hover:
            if not hovered_states[i]:
                sounds["button_select"].play()
                hovered_states[i] = True
        else:
            hovered_states[i] = False

    return tab_rects

def draw_glow_box(screen, x, y, w, h):
    # 빛나는 박스(테두리) 그리기
    s = pygame.Surface((w, h), pygame.SRCALPHA)
    s.fill((0, 0, 0, 150))
    pygame.draw.rect(s, (0, 255, 0), s.get_rect(), width=1, border_radius=14)
    screen.blit(s, (x, y))

def draw_text_box(screen, x, y, w, h, title, body, title_font, body_font):
    # 제목과 본문이 있는 텍스트 박스 그리기
    draw_glow_box(screen, x, y, w, h)
    title_surf = title_font.render(title, True, (120, 255, 120))
    screen.blit(title_surf, (x + 18, y + 20))
    pygame.draw.line(screen, (100, 255, 100), (x + 16, y + 58), (x + w - 16, y + 58), 2)

    body_lines = []
    for paragraph in body.split("\n"):
        if paragraph == "":
            body_lines.append("")
        else:
            while paragraph:
                for i in range(len(paragraph), 0, -1):
                    if body_font.size(paragraph[:i])[0] <= w - 36:
                        body_lines.append(paragraph[:i])
                        paragraph = paragraph[i:]
                        break

    for i, line in enumerate(body_lines):
        surf = body_font.render(line, True, (120, 255, 120))
        screen.blit(surf, (x + 18, y + 70 + i * 28))

def draw_weapon_detail_ui(screen, selected_tab, weapons, sounds):
    # 무기 상세 정보 UI 그리기
    screen.blit(pygame.transform.smoothscale(background_img, screen.get_size()), (0, 0))
    tab_rects = draw_tabs(screen, selected_tab, sounds)
    if selected_tab == 0:
        return tab_rects

    idx = selected_tab - 1
    if idx >= len(weapons):
        return tab_rects

    weapon = weapons[idx]
    weapon_id = gun_ids[idx]
    stat = weapon_stats[weapon_id]

    screen_width, screen_height = screen.get_size()
    margin_x = 30
    margin_y = 70
    quad_width = (screen_width - margin_x * 3) // 2
    quad_height = (screen_height - margin_y * 3) // 2

    # 무기 전방 이미지 스케일 조정
    img = weapon.front_image
    iw, ih = img.get_size()
    scale = min(quad_width / iw, quad_height / ih, 2.0)
    img = pygame.transform.smoothscale(img, (int(iw * scale), int(ih * scale)))
    img_x = margin_x
    img_y = margin_y
    draw_glow_box(screen, img_x, img_y, quad_width, quad_height)
    screen.blit(img, (img_x + (quad_width - img.get_width()) // 2, img_y + (quad_height - img.get_height()) // 2))

    stat_x = margin_x
    stat_y = margin_y * 2 + quad_height
    draw_glow_box(screen, stat_x, stat_y, quad_width, quad_height)
    name_surf = KOREAN_FONT_BOLD_28.render(stat["name"], True, (120, 255, 120))
    screen.blit(name_surf, (stat_x + 10, stat_y + 10))
    pygame.draw.line(screen, (100, 255, 100), (stat_x + 8, stat_y + 46), (stat_x + quad_width - 8, stat_y + 46), 2)

    icon_texts = [
        # 아이콘과 스탯 텍스트 목록
        (power_icon, f"공격력: {stat['power']}"),
        (spread_icon, f"탄퍼짐: {stat['spread']}"),
        (cost_icon, f"소모량: {stat['cost']}"),
        (rank_icon, f"등급: {stat['rank']}")
    ]
    y = stat_y + 50
    for icon, text in icon_texts:
        screen.blit(icon, (stat_x + 10, y))
        txt = KOREAN_FONT_BOLD_28.render(text, True, (120, 255, 120))
        screen.blit(txt, (stat_x + 50, y + 3))
        y += 40

    # 무기 설명 박스
    desc_x = margin_x * 2 + quad_width
    desc_y = margin_y
    draw_text_box(screen, desc_x, desc_y, quad_width, quad_height,
                  "무기 설명", stat["desc"],
                  title_font=KOREAN_FONT_BOLD_28, body_font=KOREAN_FONT_18)

    # 무기 사용법 박스
    usage_x = margin_x * 2 + quad_width
    usage_y = margin_y * 2 + quad_height
    draw_text_box(screen, usage_x, usage_y, quad_width, quad_height,
                  "무기 사용법", stat["usage"],
                  title_font=KOREAN_FONT_BOLD_28, body_font=KOREAN_FONT_18)

    return tab_rects

def draw_status_tab(screen, player_hp, player_hp_max, ammo_gauge, max_ammo, selected_tab, sounds):
    # '내 상태' 탭 UI 그리기
    screen_width, screen_height = screen.get_size()

    screen.blit(pygame.transform.smoothscale(background_img, screen.get_size()), (0, 0))
    tab_rects = draw_tabs(screen, selected_tab, sounds)

    margin_x = 48
    margin_y = 70
    info_width = (screen_width // 2) - margin_x * 2
    info_height = 520
    info_x = margin_x
    info_y = margin_y + 60

    draw_glow_box(screen, info_x, info_y, info_width, info_height)

    info_title = KOREAN_FONT_BOLD_28.render("내 슈트 정보", True, (120, 255, 120))
    screen.blit(info_title, (info_x + 24, info_y + 18))
    pygame.draw.line(screen, (100, 255, 100), (info_x + 18, info_y + 60), (info_x + info_width - 18, info_y + 60), 2)

    info_desc = "자신의 슈트 상태와 능력치를 확인할 수 있습니다.\n\n체력과 탄약 게이지를 확인하고, 무기 평가 항목을 볼 수 있습니다.\n\n이곳은 자동 줄바꿈이 적용됩니다."
    def draw_multiline(surface, text, font, color, pos, max_width, line_height):
        # 문자열을 자동 줄바꿈하여 여러 줄로 그리기
        x, y = pos
        lines = []
        for paragraph in text.split("\n"):
            while paragraph:
                for i in range(len(paragraph), 0, -1):
                    if font.size(paragraph[:i])[0] <= max_width:
                        lines.append(paragraph[:i])
                        paragraph = paragraph[i:]
                        break
                else:
                    lines.append(paragraph[0])
                    paragraph = paragraph[1:]
            if paragraph == "":
                lines.append("")
        for idx, line in enumerate(lines):
            surf = font.render(line, True, color)
            surface.blit(surf, (x, y + idx * line_height))

    draw_multiline(
        screen,
        info_desc,
        KOREAN_FONT_18,
        (120, 255, 120),
        (info_x + 24, info_y + 75),
        info_width - 48,
        28
    )

    bar_margin = 42
    bar_w = info_width - bar_margin * 2
    bar_h = 24
    bar_gap = 52
    label_bar_gap = 8

    hp_bar_y = info_y + info_height - 160
    ammo_bar_y = hp_bar_y + bar_h + bar_gap

    hp_label = KOREAN_FONT_BOLD_28.render("체력", True, (120,255,120))
    hp_num = KOREAN_FONT_BOLD_28.render(f"{int(player_hp)}/{player_hp_max}", True, (120,255,120))
    hp_label_y = hp_bar_y - label_bar_gap - hp_label.get_height()
    hp_num_y = hp_label_y
    screen.blit(hp_label, (info_x + bar_margin, hp_label_y))
    screen.blit(hp_num, (info_x + bar_margin + bar_w - hp_num.get_width(), hp_num_y))
    hp_bg_rect = pygame.Rect(info_x + bar_margin, hp_bar_y, bar_w, bar_h)
    pygame.draw.rect(screen, (30, 50, 30), hp_bg_rect.inflate(8,8), border_radius=10)
    pygame.draw.rect(screen, (120,255,120), (hp_bg_rect.x, hp_bg_rect.y, int(bar_w * player_hp / player_hp_max), bar_h), border_radius=10)

    ammo_label = KOREAN_FONT_BOLD_28.render("탄약", True, (120,255,120))
    ammo_num = KOREAN_FONT_BOLD_28.render(f"{int(ammo_gauge)}/{max_ammo}", True, (255,200,80))
    ammo_label_y = ammo_bar_y - label_bar_gap - ammo_label.get_height()
    ammo_num_y = ammo_label_y
    screen.blit(ammo_label, (info_x + bar_margin, ammo_label_y))
    screen.blit(ammo_num, (info_x + bar_margin + bar_w - ammo_num.get_width(), ammo_num_y))
    ammo_bg_rect = pygame.Rect(info_x + bar_margin, ammo_bar_y, bar_w, bar_h)
    pygame.draw.rect(screen, (30, 50, 30), ammo_bg_rect.inflate(8,8), border_radius=10)
    pygame.draw.rect(screen, (255,200,80), (ammo_bg_rect.x, ammo_bg_rect.y, int(bar_w * ammo_gauge / max_ammo), bar_h), border_radius=10)

    panel_width = (screen_width // 2) - margin_x * 2
    panel_height = screen_height - margin_y * 2
    panel_x = screen_width - panel_width - margin_x
    panel_y = margin_y

    draw_glow_box(screen, panel_x, panel_y, panel_width, panel_height)

    title_surface = KOREAN_FONT_BOLD_28.render("슈트 평가 항목:", True, (120, 255, 120))
    screen.blit(title_surface, (panel_x + 18, panel_y + 20))
    pygame.draw.line(screen, (100, 255, 100), (panel_x + 16, panel_y + 58), (panel_x + panel_width - 16, panel_y + 58), 2)

    inner_x = panel_x + 18
    inner_y = panel_y + 80
    inner_w = panel_width - 36
    inner_h = panel_height - 120
    draw_glow_box(screen, inner_x, inner_y, inner_w, inner_h)
    eval_text = "자신의 슈트는 다음과 같은 항목으로 평가됩니다:\n\n- 체력: 슈트의 내구성\n- 탄약: 무기 사용 가능 횟수\n- 공격력: 적에게 입히는 피해량\n- 탄퍼짐: 총기의 정확도\n\n이곳은 자동 줄바꿈이 적용됩니다."
    draw_multiline(
        screen,
        eval_text,
        KOREAN_FONT_18,
        (120, 255, 120),
        (inner_x + 12, inner_y + 28),
        inner_w - 24,
        28
    )

    return tab_rects

def handle_tab_click(pos, tab_rects, sounds):
    # 탭 클릭 시 사운드 재생 및 선택 반환
    for i, rect in enumerate(tab_rects):
        if rect.collidepoint(pos):
            sounds["button_click"].play()
            return i
    return None