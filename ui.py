import pygame
import config
import os
import textwrap

pygame.init()

BASE_DIR = os.path.dirname(__file__)
ASSET_DIR = os.path.join(BASE_DIR, "Asset")
ASSET_UI_DIR = os.path.join(ASSET_DIR, "Image", "UI")
FONT_PATH = os.path.join(ASSET_DIR, "Font", "SUIT-Regular.ttf")
BOLD_FONT_PATH = os.path.join(ASSET_DIR, "Font", "SUIT-Bold.ttf")

KOREAN_FONT_18 = pygame.font.Font(FONT_PATH, 18)
KOREAN_FONT_28 = pygame.font.Font(FONT_PATH, 28)
KOREAN_FONT_25 = pygame.font.Font(FONT_PATH, 25)
KOREAN_FONT_BOLD_28 = pygame.font.Font(BOLD_FONT_PATH, 28)

TAB_NAMES = ["내 상태", "무기1", "무기2", "무기3", "무기4"]
TAB_SIZE = (140, 140)
TAB_SPACING = -15
NUM_TABS = len(TAB_NAMES)

gun_ids = ["gun1", "gun2", "gun3", "gun4"]
weapon_stats = {
    # 무기별 스탯 및 설명, 사용법
    "gun1": {
        "name": "M1911",
        "power": 28,
        "spread": 8,
        "cost": 5,
        "rank": "1",
        "desc": "NF 코퍼레이션이 지급하는 기본 권총입니다. 모든 경비들이 차고다닙니다.",
        "usage": "좌클릭\n단발사격."
    },
    "gun2": {
        "name": "AK47",
        "power": 18,
        "spread": 9,
        "cost": 3,
        "rank": "1",
        "desc": "NF 코퍼레이션이 군인들에게 지급하는 기본 소총입니다.",
        "usage": "좌클릭\n연사"
    },
    "gun3": {
        "name": "Remington 870",
        "power": "8 x 15발",
        "spread": 30,
        "cost": 8,
        "rank": "2",
        "desc": "사거리가 다른 샷건들보단 짧지만, 근거리에서는 강력한 위력을 자랑합니다.",
        "usage": "좌클릭\n15발 산탄 발사"
    },
    "gun4": {
        "name": "유탄 발사기",
        "power": "최대 80 / 최소 15",
        "spread": 0,
        "cost": 15,
        "rank": "3",
        "desc": "광역 피해를 주는 폭발 무기입니다. 중심에 가까울수록 피해가 큽니다.",
        "usage": "좌클릭\n사거리가 적당한 유탄 발사"
    },
    "gun5": {
        "name": "미니건",
        "power": 14,
        "spread": 5,
        "cost": 6,
        "rank": "2",
        "desc": "강력한 연사력의 기관총입니다. 발사 전 약간의 예열 시간이 필요합니다.",
        "usage": "좌클릭\n0.8간의 예열 시간 후 강력한 연사력으로 발사\n마우스를 놓으면 1.0간의 과열 시간이 존재하며, 시간이 지날때까지 다시 예열 불가능"
    },
    "gun6": {
        "name": "개조된 기관단총",
        "power": "좌: 20 / 우: 최대 80, 최소 30",
        "spread": "좌: 8 / 우: 0",
        "cost": "좌: 7 / 우: 15",
        "rank": "3",
        "desc": "빠루를 든 사내가 애용하는 기관단총입니다. 우클릭 시 유탄을 발사할 수 있습니다.",
        "usage": "좌클릭\n연사\n\n우클릭\n사거리가 짧은 유탄 발사"
    },
    "gun7": {
        "name": "C8-SFW",
        "power": "좌: 25 / 우: 17 x 5발",
        "spread": "좌: 6 / 우: 15",
        "cost": "좌: 4 / 우: 10",
        "rank": "2",
        "desc": "BUCK이라고 불리는 대원이 애용하는 돌격소총입니다. 우클릭으로 산탄을 발사할 수 있습니다.",
        "usage": "좌클릭\n연사\n\n우클릭\n산탄 발사"
    },
    "gun8": {
        "name": "RPG",
        "power": "최대 120 / 최소 40",
        "spread": 0,
        "cost": 29,
        "rank": "3",
        "desc": "강력한 폭발 범위를 가진 로켓 발사기입니다.",
        "usage": "좌클릭\n로켓 발사"
    },
    "gun9": {
        "name": "ARX200",
        "power": "좌: 25 / 우: 10 + 넉백",
        "spread": "좌: 6 / 우: 0",
        "cost": "좌: 8 / 우: 18",
        "rank": "4",
        "desc": "NOMAD라고 불리는 대원이 애용하는 돌격소총입니다. 우클릭으로 적을 밀치는 기압탄을 발사합니다.",
        "usage": "좌클릭\n연사\n\n우클릭\n기압탄 발사"
    },
    "gun10": {
        "name": "Mx4 Storm",
        "power": "좌: 16 / 우: 20",
        "spread": "좌: 12 / 우: 8",
        "cost": "좌: 5 / 우: 6",
        "rank": "2",
        "desc": "가벼운 무게와 빠른 연사력을 가진 기관단총입니다. 우클릭 시 정밀 사격(ADS) 모드로 전환되어 탄퍼짐과 반동이 줄어듭니다.",
        "usage": "좌클릭\n기본 연사 사격\n\n우클릭\n정밀 사격(ADS) 모드 전환"
    },
    "gun11": {
        "name": "SPAS-15",
        "power": "8 x 6발",
        "spread": 60,
        "cost": 10,
        "rank": "3",
        "desc": "반자동으로 빠르게 쏠 수 있는 산탄총입니다. 근거리에서 여러 적에게 강한 위력을 발휘합니다.",
        "usage": "좌클릭\n6발의 산탄을 한 번에 발사"
    },
    "gun12": {
        "name": "DP-27",
        "power": 80,
        "spread": 6,
        "cost": 8,
        "rank": "3",
        "desc": "구 소련의 경기관총을 개조한 중화기입니다. 한 발 한 발 강력한 위력을 자랑합니다.",
        "usage": "좌클릭\n단발 사격\n(한 번에 강한 데미지)"
    },
    "gun13": {
        "name": "MPX",
        "power": "좌: 18 / 우: 22",
        "spread": "좌: 10 / 우: 8",
        "cost": "좌: 4 / 우: 5",
        "rank": "1",
        "desc": "경량 SMG로, 연사력과 휴대성이 뛰어납니다. 우클릭 시 정밀 사격(ADS) 모드로 더욱 정확하게 공격할 수 있습니다.",
        "usage": "좌클릭\n연사\n\n우클릭\n정밀 사격(ADS) 모드"
    },
    "gun14": {
        "name": "MP5",
        "power": "좌: 20 / 우: 24",
        "spread": "좌: 9 / 우: 8",
        "cost": "좌: 4 / 우: 5",
        "rank": "2",
        "desc": "전통적인 NF 코퍼레이션의 기관단총입니다. ADS 모드에서는 반동이 줄고 명중률이 올라갑니다.",
        "usage": "좌클릭\n연사\n\n우클릭\n정밀 사격(ADS) 모드"
    },
    "gun15": {
        "name": "플라즈마 라이플",
        "power": "좌: 24 / 우: 최대 150",
        "spread": 10,
        "cost": 10,
        "rank": "5",
        "desc": "UAC의 군사 기술 부서에서 설계한 첨단 무기이며, 악마를 찣고 죽이는 남자가 애용합니다. 차지(충전) 후 우클릭 시 광역 플라즈마 공격을 펼칠 수 있습니다.",
        "usage": "좌클릭\n플라즈마 에너지 발사(차지 증가, 최대 50차지)\n\n우클릭\n차지된 에너지를 광역 공격으로 방출"
    },
    "gun16": {
        "name": "P90",
        "power": "좌: 12 / 우: 14",
        "spread": "좌: 15 / 우: 9",
        "cost": "좌: 3 / 우: 4",
        "rank": "1",
        "desc": "50발 대용량 탄창의 소형 PDW. 우클릭 시 조준 사격(ADS) 모드로 명중률이 향상됩니다.",
        "usage": "좌클릭\n연사\n\n우클릭\n조준 사격(ADS) 모드"
    },
    "gun17": {
        "name": "FAMAS",
        "power": "3점사: 30",
        "spread": 0,
        "cost": 5,
        "rank": "3",
        "desc": "프랑스산 돌격소총. 트리거 한 번에 3발의 점사로 공격합니다.",
        "usage": "좌클릭\n3점사 사격(짧은 시간에 3발 발사)"
    },
    "gun18": {
        "name": "SMG-11",
        "power": 13,
        "spread": 30,
        "cost": 7,
        "rank": "1",
        "desc": "초소형 기관단총으로, 매우 빠른 연사력과 넓은 탄퍼짐을 지녔습니다.",
        "usage": "좌클릭\n고속 연사 사격"
    },
    "gun19": {
        "name": "방패",
        "power": "-",
        "spread": "-",
        "cost": "-",
        "rank": "4",
        "desc": "강력한 내구성의 방패로, 전방에서 오는 공격을 막아냅니다. 방어 시 탄약 게이지가 감소합니다. 다만, 폭팔 혹은 장판은 막지 못합니다.",
        "usage": "좌클릭\n방패 전개 및 방어 상태 유지(계속 누르기)"
    },
    "gun20": {
        "name": "수류탄",
        "power": "최대 80 / 최소 30",
        "spread": 0,
        "cost": 35,
        "rank": "4",
        "desc": "일정 시간 후 폭발하며 넓은 범위에 피해를 입히는 투척 무기입니다. 3발이 동시에 부채꼴로 발사됩니다.",
        "usage": "좌클릭\n핀 뽑은 후 잠시 뒤 3발 부채꼴 투척\n0.8초 후 폭발"
    }
}

def wrap_text(text, font, max_width):
    # 자동 줄바꿈
    words = text.split(' ')
    lines = []
    current_line = ''
    for word in words:
        test_line = current_line + (' ' if current_line else '') + word
        if font.size(test_line)[0] <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)
    return lines

def draw_dialogue_box_with_choices(screen, node, selected_choice_idx, history=None):
    # 대화창 띄우기
    screen_w, screen_h = screen.get_size()

    overlay = pygame.Surface((screen_w, screen_h), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 215))
    screen.blit(overlay, (0, 0))

    box_w = int(screen_w * 0.7)
    box_h = int(screen_h * 0.18)
    box_x = (screen_w - box_w) // 2 - 60
    base_y = screen_h - box_h - 140

    if history:
        for i, entry in enumerate(history):
            h_y = base_y - (len(history) - i) * (box_h - 50) + entry.get("anim_y", 0)
            h_surface = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
            pygame.draw.rect(h_surface, (60, 60, 70, 175), (0, 0, box_w, box_h), border_radius=18)
            pygame.draw.rect(h_surface, (150, 150, 180, 70), (0, 0, box_w, box_h), width=2, border_radius=18)

            name = entry.get("speaker", "")
            if name:
                name_surf = KOREAN_FONT_BOLD_28.render(f"[{name}]", True, (140, 140, 180))
                h_surface.blit(name_surf, (24, 14))

            text = entry.get("text", "")
            lines = wrap_text(text, KOREAN_FONT_18, box_w - 48)
            for j, line in enumerate(lines):
                line_surf = KOREAN_FONT_18.render(line, True, (200, 200, 200))
                h_surface.blit(line_surf, (24, 56 + j * 24))

            screen.blit(h_surface, (box_x, h_y))

    box_surface = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
    pygame.draw.rect(box_surface, (34, 34, 34, 245), (0, 0, box_w, box_h), border_radius=22)
    pygame.draw.rect(box_surface, (120, 255, 120, 110), (0, 0, box_w, box_h), width=4, border_radius=22)

    name = node.get("speaker", "")
    if name:
        name_surf = KOREAN_FONT_BOLD_28.render(f"[{name}]", True, (180, 120, 255))
        box_surface.blit(name_surf, (24, 18))

    text = node.get("text", "")
    lines = wrap_text(text, KOREAN_FONT_18, box_w - 48)
    for j, line in enumerate(lines):
        line_surf = KOREAN_FONT_18.render(line, True, (255, 255, 255))
        box_surface.blit(line_surf, (24, 60 + j * 24))

    screen.blit(box_surface, (box_x, base_y))

    choices = node.get("choices")
    if choices:
        slot_w = 300
        slot_h = 54
        slot_gap = 14
        base_x = screen_w - slot_w - 20
        choice_base_y = screen_h - (slot_h + slot_gap) * len(choices) - 30

        for i, choice in enumerate(choices):
            slot_rect = pygame.Rect(base_x, choice_base_y + i * (slot_h + slot_gap), slot_w, slot_h)
            color_bg = (42, 42, 48, 210) if i != selected_choice_idx else (130, 70, 210, 225)
            color_border = (120, 255, 120) if i == selected_choice_idx else (120, 120, 120)
            pygame.draw.rect(screen, color_bg, slot_rect, border_radius=13)
            pygame.draw.rect(screen, color_border, slot_rect, width=3, border_radius=13)
            text_surf = KOREAN_FONT_28.render(choice["text"], True, (255, 255, 255) if i != selected_choice_idx else (255, 255, 140))
            screen.blit(text_surf, (slot_rect.x + 22, slot_rect.y + 8))

        hint_font = pygame.font.Font(FONT_PATH, 18)
        hint_surf = hint_font.render("W/S: 선택  좌클릭: 결정  ESC: 나가기", True, (200, 200, 255, 180))
        screen.blit(hint_surf, (20, screen_h - 30))
    else:
        hint_font = pygame.font.Font(FONT_PATH, 18)
        hint_surf = hint_font.render("좌클릭: 다음/종료  ESC: 대화 종료", True, (200, 200, 255, 180))
        screen.blit(hint_surf, (20, screen_h - 30))

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
    weapon_id = None
    for wid, _ in weapon_stats.items():
        if wid.lower() in weapon.__class__.__name__.lower():
            weapon_id = wid
            break
    stat = weapon_stats.get(weapon_id, {})

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
        txt = KOREAN_FONT_25.render(text, True, (120, 255, 120))
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

def draw_status_tab(screen, player_hp, player_hp_max, ammo_gauge, ammo_gauge_max, selected_tab, sounds):
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
    ammo_num = KOREAN_FONT_BOLD_28.render(f"{int(ammo_gauge)}/{ammo_gauge_max}", True, (255,200,80))
    ammo_label_y = ammo_bar_y - label_bar_gap - ammo_label.get_height()
    ammo_num_y = ammo_label_y
    screen.blit(ammo_label, (info_x + bar_margin, ammo_label_y))
    screen.blit(ammo_num, (info_x + bar_margin + bar_w - ammo_num.get_width(), ammo_num_y))
    ammo_bg_rect = pygame.Rect(info_x + bar_margin, ammo_bar_y, bar_w, bar_h)
    pygame.draw.rect(screen, (30, 50, 30), ammo_bg_rect.inflate(8,8), border_radius=10)
    pygame.draw.rect(screen, (255,200,80), (ammo_bg_rect.x, ammo_bg_rect.y, int(bar_w * ammo_gauge / ammo_gauge_max), bar_h), border_radius=10)

    evil_font = KOREAN_FONT_BOLD_28
    evil_text = evil_font.render(f"악의 정수: {config.player_score}", True, (200, 100, 255))
    screen.blit(evil_text, (info_x + 24, ammo_bar_y + 80))

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