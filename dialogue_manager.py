import pygame
import ui
import config


class DialogueManager:
    def __init__(self):
        self.active = False
        self.dialogue_data = None
        self.idx = 0
        self.selected_choice = 0
        self.on_effect_callback = None
        self.close_callback = None

        self._hud_status = None

        self.dialogue_history = []
        self.history_anim_timer = 0
        self.HISTORY_ANIM_TIME = 12
        self.history_queue = []

        self.override_text = None
        self.override_speaker = None

        self._typing_target = ""
        self._typing_visible = 0
        self._typing_active = False
        self._typing_done = True
        self._typing_ms_per_char = 22
        self._typing_last_ms = 0
        self._last_display_text_cache = None

    def set_hud_status(self, hp, hp_max, ammo, ammo_max):
        # 대화 중 좌하단에 띄울 필드 상태값 전달
        self._hud_status = (hp, hp_max, ammo, ammo_max)

    def start(self, dialogue_data, on_effect_callback=None, close_callback=None):
        # 대화 시작
        self.active = True
        self.dialogue_data = dialogue_data
        self.idx = 0
        self.selected_choice = 0
        self.on_effect_callback = on_effect_callback
        self.close_callback = close_callback

        self.dialogue_history = []
        self.history_anim_timer = 0
        self.history_queue = []

        self.override_text = None
        self.override_speaker = None

        self._typing_target = ""
        self._typing_visible = 0
        self._typing_active = False
        self._typing_done = True
        self._typing_last_ms = 0
        self._last_display_text_cache = None

    def close(self):
        # 대화 강제 종료(ESC, 마지막 대사, main에서 콜백 등)
        self.active = False
        self.dialogue_data = None
        self.idx = 0
        self.selected_choice = 0
        if self.close_callback:
            try:
                self.close_callback()
            except Exception:
                pass

    def _current_node(self):
        if not self.dialogue_data:
            return {}
        try:
            return self.dialogue_data[self.idx]
        except Exception:
            return {}

    def _current_node_text(self):
        # 오버라이드 텍스트가 있으면 우선 적용
        node = self._current_node()
        if self.override_text is not None:
            return self.override_text or ""
        return node.get("text", "") or ""

    def _current_node_speaker(self):
        node = self._current_node()
        if self.override_speaker is not None:
            return self.override_speaker or ""
        return node.get("speaker", "") or ""

    def enqueue_history_line(self, speaker, text):
        # 히스토리 큐에 한 줄 추가(나중에 드레인)
        if not text:
            return
        self.history_queue.append((speaker or "", text))

    def _drain_history_queue(self):
        # 대기중인 줄을 모두 히스토리에 편입
        while self.history_queue:
            speaker, text = self.history_queue.pop(0)
            self.dialogue_history.append({
                "speaker": speaker,
                "text": text,
                "anim_y": 0,
            })
            if len(self.dialogue_history) > 3:
                self.dialogue_history.pop(0)
            self.history_anim_timer = self.HISTORY_ANIM_TIME

    def update_history_anim(self):
        # 히스토리 줄의 살짝 위로 떠오르는 애니메이션
        if self.history_anim_timer > 0:
            for entry in self.dialogue_history:
                entry["anim_y"] -= 6
            self.history_anim_timer -= 1

    def next_dialogue(self, next_idx=None):
        # 현재 노드의 본문(또는 오버라이드 텍스트)을 히스토리에 남기고 다음 인덱스로 진행.
        # 오버라이드 텍스트가 있었다면 그것부터 히스토리에 남김
        if self.override_text:
            self.enqueue_history_line(self._current_node_speaker(), self.override_text)
            self.override_text = None
            self.override_speaker = None

        # 현재 노드의 원본 텍스트도 히스토리에 남김
        node = self._current_node()
        text_to_push = node.get("text", "")
        if text_to_push:
            self.enqueue_history_line(node.get("speaker", ""), text_to_push)

        if next_idx is not None:
            self.idx = next_idx

        # 다음 노드로 넘어갔으니 타자 상태 초기화
        self._last_display_text_cache = None
        self._typing_target = ""
        self._typing_visible = 0
        self._typing_active = False
        self._typing_done = True
        self._typing_last_ms = 0

    def _refresh_typing_target_if_needed(self):
        # 노드 텍스트가 바뀌었으면 타자 상태를 리셋
        target = self._current_node_text()
        if target != self._last_display_text_cache:
            self._typing_target = target or ""
            self._typing_visible = 0
            self._typing_active = bool(self._typing_target)
            self._typing_done = not bool(self._typing_target)
            self._typing_last_ms = pygame.time.get_ticks()
            self._last_display_text_cache = target

    def _typed_text(self):
        # 현재까지 출력된 부분 문자열
        if not self._typing_target:
            return ""
        n = max(0, min(self._typing_visible, len(self._typing_target)))
        return self._typing_target[:n]

    def _advance_typing(self):
        # 시간 경과에 따라 한 번에 여러 글자까지 출력
        if not self._typing_active or self._typing_done:
            return
        now = pygame.time.get_ticks()
        delta = now - self._typing_last_ms
        if delta < 0:
            delta = 0

        step = max(1, delta // self._typing_ms_per_char)
        if step <= 0:
            return

        new_visible = min(len(self._typing_target), self._typing_visible + step)

        # 글자 출력 사운드: 공백/개행 제외
        if hasattr(config, "sounds"):
            try:
                for i in range(self._typing_visible, new_visible):
                    ch = self._typing_target[i]
                    if ch.strip():  # 공백/개행 제외
                        sfx = config.sounds.get("button_select")
                        if sfx:
                            sfx.play()
            except Exception:
                pass

        self._typing_visible = new_visible
        self._typing_last_ms = now

        if self._typing_visible >= len(self._typing_target):
            self._typing_done = True
            self._typing_active = False

    def _complete_typing(self):
        # 좌클릭으로 즉시 한 줄 완성(선택지는 즉시 노출)
        if not self._typing_done:
            self._typing_visible = len(self._typing_target)
            self._typing_done = True
            self._typing_active = False

    def _play_click(self):
        # 선택 이동/선택/진행/ESC 시 클릭음
        if hasattr(config, "sounds"):
            try:
                s = config.sounds.get("button_click")
                if s:
                    s.play()
            except Exception:
                pass

    def _apply_effect_if_any(self):
        # 노드에 effect가 있다면 외부 콜백(on_effect_callback)을 통해 적용.
        # as_text_only == True 이면, 콜백이 반환한 문자열을 이번 노드의
        # 오버라이드 텍스트로 사용(타자 효과 포함).
        node = self._current_node()
        effect = node.get("effect")
        if effect and self.on_effect_callback:
            as_text_only = not bool(node.get("text"))
            line = self.on_effect_callback(effect, node.get("effect_messages"), as_text_only)
            if as_text_only:
                self.override_text = line or ""
                self.override_speaker = node.get("speaker", "")
                # 텍스트가 바뀌었으니 타자 상태 리셋
                self._last_display_text_cache = None

    def update(self, event_list):
        # 매 프레임 호출: 입력 처리 + 타자 진행 + 히스토리 애니메이션
        # 대화 비활성 시에도 히스토리 큐만 비워 준다(잔상 자연스러운 처리)
        if not self.active:
            self._drain_history_queue()
            return

        # 현재 노드/타자 상태 갱신
        self._refresh_typing_target_if_needed()
        self._advance_typing()

        node = self._current_node()
        has_choices = bool(node.get("choices"))

        for event in event_list:
            # ESC → 대화 종료(클릭음)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self._play_click()
                self.close()
                continue

            if has_choices:
                # 출력 중: 좌클릭으로 즉시 완성(선택지 즉시 노출)
                if not self._typing_done:
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        self._complete_typing()
                    continue

                # 출력 완료 후: 선택지 이동(W/S)
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_w:
                        self.selected_choice = (self.selected_choice - 1) % len(node["choices"])
                        self._play_click()
                    elif event.key == pygame.K_s:
                        self.selected_choice = (self.selected_choice + 1) % len(node["choices"])
                        self._play_click()

                # 좌클릭으로 선택 확정
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    choice = node["choices"][self.selected_choice]
                    self._play_click()
                    if "next" in choice and choice["next"] is not None:
                        self.next_dialogue(choice["next"])
                        self.selected_choice = 0
                        self._apply_effect_if_any()
                    else:
                        self.close()
            else:
                # 선택지 없는 노드
                if not self._typing_done:
                    # 출력 중 좌클릭 → 즉시 완성
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        self._complete_typing()
                else:
                    # 출력 완료 후 좌클릭 → 다음/종료
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        self._play_click()
                        if "next" in node and node["next"] is not None:
                            self.next_dialogue(node["next"])
                            self.selected_choice = 0
                            self._apply_effect_if_any()
                        else:
                            self.close()

        # 히스토리 큐를 실제 히스토리로 편입 + 애니메이션
        self._drain_history_queue()
        self.update_history_anim()

    def draw(self, screen):
        # 현재 노드를 대화 박스로 그린다(좌하단 미니 HUD 포함).
        if not self.active:
            return

        # 현재 노드/타자 상태 갱신(드로우 직전에도 안전하게 보정)
        self._refresh_typing_target_if_needed()

        node_src = self._current_node()
        node = dict(node_src) if node_src else {}

        # 오버라이드 스피커/텍스트 적용
        if self.override_speaker is not None:
            node["speaker"] = self.override_speaker
        if self.override_text is not None:
            node["text"] = self.override_text

        # 텍스트는 '진행된 만큼만' 부분 출력
        node["text"] = self._typed_text()

        # 출력이 끝나기 전까지는 선택지를 숨긴다
        if node.get("choices") and not self._typing_done:
            node = dict(node)
            node["choices"] = []

        ui.draw_dialogue_box_with_choices(
            screen,
            node,
            self.selected_choice,
            history=self.dialogue_history,
            hud_status=self._hud_status
        )
