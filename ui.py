import pygame
import config
import os
import re
import os
import pygame
from config import ASSET_DIR
from text_data import weapon_stats
from text_data import (
    STATUS_EVAL_TEMPLATES, HP_BUCKET_LABELS, AMMO_BUCKET_LABELS, STAGE_ORDER,
    HP_BUCKET_SENTENCES, AMMO_BUCKET_SENTENCES, STAGE_DESCRIPTIONS,
    WEAPON_COUNT_SENTENCES,
    KILL_THRESHOLDS, KILL_SENTENCES,
    ESSENCE_THRESHOLDS, ESSENCE_SENTENCES,
    HP_MAX_THRESHOLDS, HP_MAX_SENTENCES,
    AMMO_MAX_THRESHOLDS, AMMO_MAX_SENTENCES
)

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
KOREAN_FONT_BOLD_22 = pygame.font.Font(BOLD_FONT_PATH, 22)

TAB_NAMES = ["내 상태", "무기1", "무기2", "무기3", "무기4"]
TAB_SIZE = (140, 140)
TAB_SPACING = -15
NUM_TABS = len(TAB_NAMES)

_story_img_cache = {}
_story_img_scaled_cache = {}

gun_ids = ["gun1", "gun2", "gun3", "gun4"]

DIALOGUE_TEXT_Y_RATIO = 0.28
STORY_IMG_MAX_W_RATIO = 0.90
STORY_IMG_MAX_H_RATIO = 0.28
STORY_IMG_CENTER_Y_RATIO = 5/6

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

def draw_dialogue_box_with_choices(screen, node, selected_choice_idx, history=None, hud_status=None):
    # 대화창 띄우기
    screen_w, screen_h = screen.get_size()

    box_w = int(screen_w * 0.7)
    box_h = int(screen_h * 0.22)
    box_x = (screen_w - box_w) // 2 - 60
    base_y = screen_h - box_h - 140

    if history:
        hist = history[-3:]
        overlap = 50
        for i, entry in enumerate(hist):
            idx_from_bottom = len(hist) - i
            h_y = base_y - idx_from_bottom * (box_h - overlap) + entry.get("anim_y", 0)
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
        screen.blit(hint_surf, (screen_w - hint_surf.get_width() - 20, screen_h - 30))
    else:
        hint_font = pygame.font.Font(FONT_PATH, 18)
        hint_surf = hint_font.render("좌클릭: 다음/종료  ESC: 대화 종료", True, (200, 200, 255, 180))
        screen.blit(hint_surf, (screen_w - hint_surf.get_width() - 20, screen_h - 30))

    if hud_status is not None:
        try:
            hp, hp_max, ammo, ammo_max = hud_status
            draw_field_status_mini(screen, hp, hp_max, ammo, ammo_max)
        except Exception:
            # 잘못된 인자여도 대화 진행엔 영향 없게 무시
            pass

    return

STORY_SEARCH_PATHS = [
    os.path.join(ASSET_DIR, "Image", "Story"),
    os.path.join(ASSET_DIR, "image", "story"),
    os.path.join("Asset", "Image", "Story"),
    os.path.join("Asset", "image", "story"),
    "",
]

def _get_story_image(filename):
    if not filename:
        return None
    if filename in _story_img_cache:
        return _story_img_cache[filename]
    raw = None
    for base in STORY_SEARCH_PATHS:
        path = os.path.join(base, filename) if base else filename
        if os.path.exists(path):
            try:
                raw = pygame.image.load(path).convert_alpha()
                break
            except Exception:
                pass
    _story_img_cache[filename] = raw
    return raw

def _get_story_image_scaled(filename, max_w, max_h, upscale=False):
    # 중앙정렬·페이드용으로 draw_cinematic_dialogue에서 사용
    if not filename:
        return None
    orig = _get_story_image(filename)
    if orig is None:
        return None
    iw, ih = orig.get_size()
    # 업스케일 금지면, 이미 작으면 그대로 사용
    if not upscale and iw <= max_w and ih <= max_h:
        return orig
    # 축소 비율(가로/세로 한계 내)
    scale = min(max_w / max(iw, 1), max_h / max(ih, 1))
    # 업스케일 금지 조건이면 원본 반환
    if not upscale and scale >= 1.0:
        return orig
    key = (filename, int(max_w), int(max_h), int(bool(upscale)))
    cached = _story_img_scaled_cache.get(key)
    if cached:
        return cached
    import pygame
    new_w = max(1, int(iw * scale))
    new_h = max(1, int(ih * scale))
    scaled = pygame.transform.smoothscale(orig, (new_w, new_h))
    _story_img_scaled_cache[key] = scaled
    return scaled

def draw_cinematic_dialogue(screen, node):
    # 완전 검은 배경 + 단일 대사(히스토리 미표시)
    screen_w, screen_h = screen.get_size()
    screen.fill((0, 0, 0))

    speaker = node.get("speaker", "") or ""
    text = node.get("text", "") or ""
    image_file = node.get("image")
    image_prev = node.get("image_prev")
    image_fade = node.get("image_fade", 1.0)
    
    # 텍스트
    text_max_w = int(screen_w * 0.82)
    lines = wrap_text(text, KOREAN_FONT_28, text_max_w)
    speaker_h = 54 if speaker else 0
    body_h = 36 * len(lines)
    block_h = speaker_h + body_h
    # 텍스트 블록: 상단 1/3 근방(조금 더 위)에서 시작
    text_center_y = int(screen_h * DIALOGUE_TEXT_Y_RATIO)
    y = max(10, text_center_y - (block_h // 2))

    # 스피커
    if speaker:
        name_surf = KOREAN_FONT_BOLD_28.render(f"[{speaker}]", True, (200, 200, 200))
        screen.blit(name_surf, ((screen_w - name_surf.get_width()) // 2, y))
        y += 54

    # 본문
    for line in lines:
        surf = KOREAN_FONT_28.render(line, True, (255, 255, 255))
        screen.blit(surf, ((screen_w - surf.get_width()) // 2, y))
        y += 36

    # 이미지
    # 같은 파일이면 이전 이미지는 사용하지 않음(유지)
    if image_prev and image_file and image_prev == image_file:
        image_prev = None
        image_fade = 1.0
    max_w = int(screen_w * 1.0)
    max_h = int(screen_h * 0.5)
    cur = _get_story_image_scaled(image_file, max_w, max_h, upscale=False) if image_file else None
    prv = _get_story_image_scaled(image_prev, max_w, max_h, upscale=False) if image_prev else None
    img_center_y = (screen_h * 2) // 3

    def _blit_center(img, alpha):
        if not img:
            return
        if 0 <= alpha < 255:
            surf = img.copy()
            surf.set_alpha(alpha)
        else:
            surf = img
        ix = (screen_w - img.get_width()) // 2
        iy = img_center_y - (img.get_height() // 2)
        screen.blit(surf, (ix, iy))

    # 크로스페이드: 이전(prv)은 서서히 사라지고, 현재(cur)는 동시에 나타남
    a = max(0.0, min(1.0, float(image_fade)))
    s = (a * a * (3 - 2 * a))
    if prv:
        _blit_center(prv, int(255 * (1.0 - s)))
    if cur:
        _blit_center(cur, int(255 * s))

    # 힌트
    hint_font = pygame.font.Font(FONT_PATH, 18)
    hint_surf = hint_font.render("좌클릭: 다음/종료  ESC: 건너뛰기", True, (140, 140, 140))
    screen.blit(hint_surf, (screen_w - hint_surf.get_width() - 20, screen_h - 28))

def draw_field_status_mini(screen, player_hp, player_hp_max, ammo_gauge, ammo_gauge_max, x=18, y=None):
    # 대화 중 좌하단에 간이 체력/탄약/악의 정수 표시
    sw, sh = screen.get_size()
    panel_w, panel_h = 300, 120
    if y is None:
        y = sh - panel_h - 8

    panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
    pygame.draw.rect(panel, (20, 20, 28, 210), panel.get_rect(), border_radius=14)
    pygame.draw.rect(panel, (90, 90, 120), panel.get_rect(), width=2, border_radius=14)
    screen.blit(panel, (x, y))

    pad = 18
    bar_w = panel_w - pad * 2
    bar_h = 18

    hp = max(0, int(player_hp))
    hp_max = max(1, int(player_hp_max or 1))
    hp_ratio = max(0.0, min(1.0, hp / hp_max))
    hp_bg = pygame.Rect(x + pad, y + pad, bar_w, bar_h)
    pygame.draw.rect(screen, (30, 50, 30), hp_bg, border_radius=9)
    pygame.draw.rect(screen, (120, 255, 120), (hp_bg.x, hp_bg.y, int(bar_w * hp_ratio), bar_h), border_radius=9)
    hp_text = KOREAN_FONT_18.render(f"{hp}/{hp_max}", True, (120, 255, 120))
    screen.blit(hp_text, (hp_bg.x + 6, hp_bg.y - 20))

    ammo = max(0, int(ammo_gauge))
    ammo_max = max(1, int(ammo_gauge_max or 1))
    ammo_ratio = max(0.0, min(1.0, ammo / ammo_max))
    ammo_y = hp_bg.y + bar_h + 16
    ammo_bg = pygame.Rect(x + pad, ammo_y, bar_w, bar_h)
    pygame.draw.rect(screen, (30, 50, 30), ammo_bg, border_radius=9)
    pygame.draw.rect(screen, (255, 200, 80), (ammo_bg.x, ammo_bg.y, int(bar_w * ammo_ratio), bar_h), border_radius=9)
    ammo_text = KOREAN_FONT_18.render(f"{ammo}/{ammo_max}", True, (255, 200, 80))
    screen.blit(ammo_text, (ammo_bg.x + 6, ammo_bg.y - 20))

    evil_val = getattr(config, "player_score", 0)
    evil_surf = KOREAN_FONT_18.render(f"악의 정수: {evil_val}", True, (200, 100, 255))
    screen.blit(evil_surf, (x + pad, ammo_bg.bottom + 10))

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
    cls_name = weapon.__class__.__name__.lower()
    if cls_name in weapon_stats:
        weapon_id = cls_name
    else:
        m = re.match(r'gun\d+$', cls_name) or re.search(r'gun(\d+)', cls_name)
        weapon_id = (m.group(0) if m and m.re == re.match(r'gun\d+$', cls_name).re else
                     (f"gun{m.group(1)}" if m else None))
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

def draw_status_tab(screen, player_hp, player_hp_max, ammo_gauge, ammo_gauge_max, selected_tab, sounds, kill_count, weapon_count):
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

    max_hp_text = KOREAN_FONT_BOLD_22.render(f"현재 최대 체력: {int(player_hp_max)}", True, (120,255,120))
    max_ammo_text = KOREAN_FONT_BOLD_22.render(f"현재 최대 탄약 게이지: {int(ammo_gauge_max)}", True, (120,255,120))
    screen.blit(max_hp_text, (info_x + 24, info_y + 72))
    screen.blit(max_ammo_text, (info_x + 24, info_y + 72 + 30))

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

    stage_text = KOREAN_FONT_BOLD_22.render(f"현재 스테이지: {config.CURRENT_STAGE}", True, (120,255,120))
    kills_text = KOREAN_FONT_BOLD_22.render(f"잡은 적: {kill_count}", True, (120,255,120))
    stage_y = hp_bar_y - 110
    kills_y = stage_y + 32
    screen.blit(stage_text, (info_x + 24, stage_y))
    screen.blit(kills_text, (info_x + 24, kills_y))

    evil_font = KOREAN_FONT_BOLD_28
    evil_text = evil_font.render(f"악의 정수: {config.player_score}", True, (200, 100, 255))
    evil_y = info_y + info_height - 40 - evil_text.get_height()//2
    screen.blit(evil_text, (info_x + 24, evil_y))

    panel_width = (screen_width // 2) - margin_x * 2
    panel_height = screen_height - margin_y * 2
    panel_x = screen_width - panel_width - margin_x
    panel_y = margin_y

    draw_glow_box(screen, panel_x, panel_y, panel_width, panel_height)

    title_surface = KOREAN_FONT_BOLD_28.render("슈트 평가 항목:", True, (120, 255, 120))
    screen.blit(title_surface, (panel_x + 18, panel_y + 20))
    pygame.draw.line(screen, (100, 255, 100), (panel_x + 16, panel_y + 58), (panel_x + panel_width - 16, panel_y + 58), 2)

    hp_ratio = max(0.0, min(1.0, player_hp / max(player_hp_max,1)))
    ammo_ratio = max(0.0, min(1.0, ammo_gauge / max(ammo_gauge_max,1)))
    hp_bucket_idx = min(3, int(hp_ratio * 4))
    ammo_bucket_idx = min(3, int(ammo_ratio * 4))
    hp_bucket = HP_BUCKET_LABELS[hp_bucket_idx]
    ammo_bucket = AMMO_BUCKET_LABELS[ammo_bucket_idx]
    hp_sentence = HP_BUCKET_SENTENCES[hp_bucket_idx]
    ammo_sentence = AMMO_BUCKET_SENTENCES[ammo_bucket_idx]

    stage_desc = STAGE_DESCRIPTIONS.get(getattr(config, "CURRENT_STAGE", "1-1"), "현재 구역.")
    templates = STATUS_EVAL_TEMPLATES or {
        "hp_state": "{hp_sentence} ({hp_bucket})",
        "ammo_state": "{ammo_sentence} ({ammo_bucket})",
        "weapon_state": "{weapon_sentence} ({weapon_count}/4)",
        "stage_progress": "스테이지 안내: {stage_desc}",
        "kills_state": "{kill_sentence} (처치: {kills})",
        "essence_state": "{essence_sentence} (악의 정수: {essence})",
        "hp_max_state": "{hpmax_sentence} (최대 체력: {hp_max})",
        "ammo_max_state": "{ammomax_sentence} (최대 탄약: {ammo_max})",
    }

    def pick_by_threshold(value, thresholds, sentences):
        idx = 0
        for i, t in enumerate(thresholds):
            if value >= t:
                idx = i
        idx = min(idx, len(sentences)-1)
        return sentences[idx]

    weapon_sentence = WEAPON_COUNT_SENTENCES[min(max(0, weapon_count), 4)]
    kill_sentence   = pick_by_threshold(kill_count, KILL_THRESHOLDS, KILL_SENTENCES)
    essence_val     = getattr(config, "player_score", 0)
    essence_sentence= pick_by_threshold(essence_val, ESSENCE_THRESHOLDS, ESSENCE_SENTENCES)
    hpmax_sentence  = pick_by_threshold(int(player_hp_max), HP_MAX_THRESHOLDS, HP_MAX_SENTENCES)
    ammomax_sentence= pick_by_threshold(int(ammo_gauge_max), AMMO_MAX_THRESHOLDS, AMMO_MAX_SENTENCES)

    lines = [
        templates["hp_state"].format(
            hp_sentence=hp_sentence, hp_bucket=hp_bucket),
        templates["ammo_state"].format(
            ammo_sentence=ammo_sentence, ammo_bucket=ammo_bucket),
        templates["weapon_state"].format(
            weapon_sentence=weapon_sentence, weapon_count=weapon_count),
        templates["stage_progress"].format(stage_desc=stage_desc),
        templates["kills_state"].format(
            kill_sentence=kill_sentence, kills=kill_count),
        templates["essence_state"].format(
            essence_sentence=essence_sentence, essence=essence_val),
        templates["hp_max_state"].format(
            hpmax_sentence=hpmax_sentence, hp_max=int(player_hp_max)),
        templates["ammo_max_state"].format(
            ammomax_sentence=ammomax_sentence, ammo_max=int(ammo_gauge_max)),
    ]

    y = panel_y + 80
    max_w = panel_width - 48
    lh = 32
    for line in lines:
        for wrapped in wrap_text(line, KOREAN_FONT_BOLD_22, max_w):
            surf = KOREAN_FONT_BOLD_22.render(wrapped, True, (120, 255, 120))
            screen.blit(surf, (panel_x + 24, y))
            y += lh

    return tab_rects

def handle_tab_click(pos, tab_rects, sounds):
    # 탭 클릭 시 사운드 재생 및 선택 반환
    for i, rect in enumerate(tab_rects):
        if rect.collidepoint(pos):
            sounds["button_click"].play()
            return i
    return None

def draw_combat_banner(screen, text, theme, progress):
    # 상단 배너
    if progress < 0: progress = 0.0
    if progress > 1: progress = 1.0
    sw, sh = screen.get_size()
    banner_w = min(int(sw * 0.8), 560)
    banner_h = 64
    x = (sw - banner_w) // 2

    if progress < 0.2:
        t = progress / 0.2
        y = int(-banner_h + (60 + banner_h) * t)
    elif progress > 0.8:
        t = (progress - 0.8) / 0.2
        y = int(60 + (-banner_h - 60) * t)
    else:
        y = 60

    if theme == "start":
        bg = (200, 40, 40, 220)
        border = (255, 120, 120)
        fg = (255, 255, 255)
    else:
        bg = (40, 150, 60, 220)
        border = (150, 255, 170)
        fg = (255, 255, 255)
    panel = pygame.Surface((banner_w, banner_h), pygame.SRCALPHA)
    pygame.draw.rect(panel, bg, panel.get_rect(), border_radius=14)
    pygame.draw.rect(panel, border, panel.get_rect(), width=2, border_radius=14)
    screen.blit(panel, (x, y))

    try:
        font = KOREAN_FONT_BOLD_28
    except Exception:
        font = pygame.font.Font(None, 32)
    surf = font.render(text, True, fg)
    screen.blit(surf, (x + (banner_w - surf.get_width()) // 2,
                       y + (banner_h - surf.get_height()) // 2))

def draw_enemy_counter(screen, remaining, slide_progress=1.0, alpha=255, anchor_rect=None, margin_y=8, align_right=True):
    # 우상단 '남은 적: N' 라벨.
    if remaining is None:
        return
    sw, sh = screen.get_size()
    try:
        font = KOREAN_FONT_BOLD_22
    except Exception:
        font = pygame.font.Font(None, 28)
    text = f"남은 적: {remaining}"
    text_surf = font.render(text, True, (255, 255, 255))
    text_surf.set_alpha(alpha)

    pad_x, pad_y = 10, 6
    panel_w = text_surf.get_width() + pad_x * 2
    panel_h = text_surf.get_height() + pad_y * 2
    
    if anchor_rect is not None:
        y = anchor_rect.bottom + margin_y
        if align_right:
            final_x = anchor_rect.right - panel_w
        else:
            final_x = anchor_rect.left
        final_x = max(10, min(final_x, sw - panel_w - 10))
        y = max(10, min(y, sh - panel_h - 10))
    else:
        final_x = sw - panel_w - 20
        y = 20

    slide_progress = max(0.0, min(1.0, slide_progress))
    x = int(final_x + (panel_w + 24) * (1.0 - slide_progress))

    panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
    pygame.draw.rect(panel, (20, 20, 28, 210), panel.get_rect(), border_radius=10)
    pygame.draw.rect(panel, (120, 255, 120), panel.get_rect(), width=2, border_radius=12)
    panel.set_alpha(alpha)
    screen.blit(panel, (x, y))
    screen.blit(text_surf, (x + pad_x, y + pad_y))

def draw_shock_overlay(screen, intensity: float):
    # 감전 상태 전용 파란 비네트 오버레이.
    if intensity <= 0:
        return
    w, h = screen.get_size()
    surf = pygame.Surface((w, h), pygame.SRCALPHA)

    base_alpha = int(140 * max(0.0, min(1.0, intensity)))
    color = (60, 160, 255, base_alpha)

    surf.fill(color)
    ell_w, ell_h = int(w * 0.85), int(h * 0.75)
    hole = pygame.Surface((ell_w, ell_h), pygame.SRCALPHA)
    pygame.draw.ellipse(hole, (0, 0, 0, 0), hole.get_rect())
    surf.blit(hole, ((w - ell_w)//2, (h - ell_h)//2), special_flags=pygame.BLEND_RGBA_SUB)

    screen.blit(surf, (0, 0))