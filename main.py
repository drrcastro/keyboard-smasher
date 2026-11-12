"""
Mundo Mágico do Teclado (Keyboard Smasher)
Aplicação interativa em ecrã total para todos os monitores para crianças pequenas brincarem
com o teclado e rato com segurança, animações mágicas, mudança suave de cores e sons harmoniosos.
"""

import sys
import time
import math
import random
import ctypes
from ctypes import wintypes
import pygame
from pygame._sdl2.video import Window, Renderer

from config import (
    ESCAPE_HOLD_SECONDS,
    TARGET_FPS,
    BACKGROUND_PALETTE,
    LETTER_EMOJIS,
    SPECIAL_KEY_NAMES,
    PARTICLE_COLORS
)
from sound_engine import SoundEngine
from visual_engine import MonitorScreen


# Ativação do suporte DPI Per-Monitor no Windows para coordenadas e resoluções exatas
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
except Exception:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass


class MONITORINFOEX(ctypes.Structure):
    _fields_ = [
        ('cbSize', wintypes.DWORD),
        ('rcMonitor', wintypes.RECT),
        ('rcWork', wintypes.RECT),
        ('dwFlags', wintypes.DWORD),
        ('szDevice', wintypes.WCHAR * 32)
    ]


def detect_all_monitors():
    """Enumera todos os monitores físicos conectados com suas coordenadas exatas."""
    user32 = ctypes.windll.user32
    monitors = []

    def enum_cb(hMonitor, hdcMonitor, lprcMonitor, dwData):
        mi = MONITORINFOEX()
        mi.cbSize = ctypes.sizeof(MONITORINFOEX)
        user32.GetMonitorInfoW(hMonitor, ctypes.byref(mi))
        r = mi.rcMonitor
        w = r.right - r.left
        h = r.bottom - r.top
        is_primary = bool(mi.dwFlags & 1)
        monitors.append({
            'device': mi.szDevice,
            'rect': (r.left, r.top, w, h),
            'primary': is_primary
        })
        return True

    MONITORENUMPROC = ctypes.WINFUNCTYPE(
        ctypes.c_bool,
        wintypes.HMONITOR,
        wintypes.HDC,
        ctypes.POINTER(wintypes.RECT),
        wintypes.LPARAM
    )
    user32.EnumDisplayMonitors(None, None, MONITORENUMPROC(enum_cb), 0)

    # Ordena para que o ecrã principal venha primeiro caso desejado
    if not monitors:
        # Fallback caso não seja possível enumerar via win32
        monitors = [{'device': 'Primary', 'rect': (0, 0, 1920, 1080), 'primary': True}]

    return monitors


def get_global_cursor_pos():
    """Obtém a posição global do cursor do rato em todo o desktop virtual."""
    pt = wintypes.POINT()
    ctypes.windll.user32.GetCursorPos(ctypes.byref(pt))
    return pt.x, pt.y


class KeyboardSmasherApp:
    def __init__(self):
        pygame.init()
        pygame.font.init()
        
        self.sound = SoundEngine()
        self.monitors_info = detect_all_monitors()
        print(f"[Teclado Mágico] Detectados {len(self.monitors_info)} monitores.")

        self.windows = []
        self.screens = []
        self.primary_screen = None

        # Cria uma janela em ecrã total sem margens em cada monitor
        for i, info in enumerate(self.monitors_info):
            x, y, w, h = info['rect']
            is_prim = info['primary']
            print(f"  Monitor {i}: ({w}x{h}) na posição ({x}, {y}) - Principal: {is_prim}")

            win = Window(
                f"Teclado Mágico - Ecrã {i+1}",
                size=(w, h),
                position=(x, y),
                borderless=True,
                always_on_top=True
            )
            # Aceleração de hardware por GPU via Direct3D/OpenGL
            ren = Renderer(win, vsync=False)
            
            screen_obj = MonitorScreen(i, win, ren, (x, y, w, h), is_primary=is_prim)
            self.windows.append(win)
            self.screens.append(screen_obj)
            if is_prim:
                self.primary_screen = screen_obj

        if not self.primary_screen and self.screens:
            self.primary_screen = self.screens[0]

        # Foca e bloqueia o teclado para a janela principal
        if self.windows:
            self.windows[0].focus()
            try:
                self.windows[0].grab_keyboard = True
            except Exception:
                pass

        # Estado da aplicação
        self.running = True
        self.clock = pygame.time.Clock()
        self.start_time = time.time()
        self.esc_pressed_time = None
        self.last_cursor_pos = get_global_cursor_pos()
        self.last_shake_sound_time = 0.0
        self.color_index = 0
        self.last_topmost_check = time.time()

    def get_screen_at_cursor(self, gx, gy):
        """Identifica em que monitor o cursor está e as suas coordenadas locais."""
        for s in self.screens:
            if s.x <= gx < s.x + s.w and s.y <= gy < s.y + s.h:
                return s, (gx - s.x, gy - s.y)
        return self.primary_screen, (self.primary_screen.w // 2, self.primary_screen.h // 2)

    def trigger_color_shift(self):
        """Muda suavemente as cores de fundo de todos os monitores."""
        self.color_index = (self.color_index + 1) % len(BACKGROUND_PALETTE)
        base_color = BACKGROUND_PALETTE[self.color_index]
        
        for i, s in enumerate(self.screens):
            # Pequena variação harmoniosa de tom entre cada monitor
            offset = (i * 20) % 50
            r = min(255, max(0, base_color[0] + offset))
            g = min(255, max(0, base_color[1] - offset // 2))
            b = min(255, max(0, base_color[2] + offset // 2))
            s.set_target_background((r, g, b))

    def handle_key_smash(self, event, gx, gy):
        """Processa qualquer tecla pressionada pelas crianças com animações e sons."""
        active_screen, (lx, ly) = self.get_screen_at_cursor(gx, gy)
        self.trigger_color_shift()

        # Determina o texto e o emoji a exibir
        key_name = pygame.key.name(event.key).upper()
        char = None
        emoji = None

        if event.unicode and event.unicode.isprintable() and not event.unicode.isspace():
            char = event.unicode.upper()
            emoji = LETTER_EMOJIS.get(char, '⭐')
        elif key_name in SPECIAL_KEY_NAMES:
            char = SPECIAL_KEY_NAMES[key_name]
            emoji = LETTER_EMOJIS.get(key_name, '✨')
        else:
            char = key_name[:6]
            emoji = LETTER_EMOJIS.get(key_name, '🎈')

        # Efeitos especiais para teclas importantes
        if event.key == pygame.K_SPACE:
            # Grande festival de fogos de artifício em TODOS os monitores!
            for s in self.screens:
                s.add_particle_burst(s.w // 2, s.h // 2, count=50, shapes=['star', 'sparkle', 'confetti'], speed_range=(150, 500))
            self.sound.play_firework()
        elif event.key == pygame.K_RETURN:
            # Chuva de corações e flores em todos os monitores
            for s in self.screens:
                s.add_particle_burst(s.w // 2, s.h // 2, count=45, shapes=['heart', 'flower', 'confetti'])
            self.sound.play_harp()
        elif event.key == pygame.K_BACKSPACE:
            # Chuva de bolhas
            for s in self.screens:
                s.add_particle_burst(s.w // 2, s.h // 2, count=40, shapes=['bubble', 'ring'])
            self.sound.play_pop()
        else:
            # Som musical harmonioso (escala pentatónica) ou boing divertido
            if random.random() < 0.12:
                self.sound.play_boing()
            else:
                self.sound.play_musical_note()

        # Posiciona o badge perto da posição atual ou no centro com variação divertida
        jitter_x = random.uniform(-140, 140) * active_screen.scale
        jitter_y = random.uniform(-100, 100) * active_screen.scale
        bx = min(max(int(lx + jitter_x), int(220 * active_screen.scale)), int(active_screen.w - 220 * active_screen.scale))
        by = min(max(int(ly + jitter_y), int(160 * active_screen.scale)), int(active_screen.h - 160 * active_screen.scale))

        badge_color = random.choice(PARTICLE_COLORS)
        active_screen.add_badge(char, emoji, bx, by, badge_color)
        active_screen.add_particle_burst(bx, by, count=random.randint(28, 42))

        # Dispara pequenas estrelas nos outros monitores para que todos brinquem juntos
        for other in self.screens:
            if other != active_screen:
                other.add_particle_burst(
                    random.randint(int(other.w * 0.2), int(other.w * 0.8)),
                    random.randint(int(other.h * 0.2), int(other.h * 0.8)),
                    count=16,
                    shapes=['star', 'sparkle'],
                    speed_range=(80, 250)
                )

    def run(self):
        """Ciclo principal de execução a 60 FPS."""
        print("[Teclado Mágico] Aplicação iniciada! Para sair, segure ESC durante 2 segundos.")
        
        try:
            while self.running:
                dt = self.clock.tick(TARGET_FPS) / 1000.0
                dt = min(dt, 0.05) # Limita dt para estabilidade física
                now = time.time()

                gx, gy = get_global_cursor_pos()

                # Processamento de Eventos
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False
                        break

                    elif event.type == pygame.KEYDOWN:
                        # 1. Atalhos de saída instantânea para os pais
                        mods = pygame.key.get_mods()
                        ctrl_pressed = bool(mods & pygame.KMOD_CTRL)
                        shift_pressed = bool(mods & pygame.KMOD_SHIFT)
                        alt_pressed = bool(mods & pygame.KMOD_ALT)

                        if (ctrl_pressed and shift_pressed and event.key == pygame.K_q) or \
                           (ctrl_pressed and alt_pressed and event.key == pygame.K_q) or \
                           (alt_pressed and event.key == pygame.K_F4):
                            self.running = False
                            break

                        # 2. Controlos de volume / silêncio dos pais
                        if event.key == pygame.K_F1:
                            muted = self.sound.toggle_mute()
                            print(f"[Teclado Mágico] Som {'Silenciado' if muted else 'Ativado'}")
                        elif event.key == pygame.K_F2:
                            vol = self.sound.volume_down()
                            print(f"[Teclado Mágico] Volume: {int(vol*100)}%")
                        elif event.key == pygame.K_F3:
                            vol = self.sound.volume_up()
                            print(f"[Teclado Mágico] Volume: {int(vol*100)}%")

                        # 3. Tecla ESC (segurança parental: necessita segurar 2 segundos)
                        elif event.key == pygame.K_ESCAPE:
                            if self.esc_pressed_time is None:
                                self.esc_pressed_time = now

                        # 4. Qualquer outra tecla: DIVERSÃO PARA AS CRIANÇAS!
                        else:
                            self.handle_key_smash(event, gx, gy)

                    elif event.type == pygame.KEYUP:
                        if event.key == pygame.K_ESCAPE:
                            self.esc_pressed_time = None

                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        active_screen, (lx, ly) = self.get_screen_at_cursor(gx, gy)
                        if event.button == 1: # Botão Esquerdo
                            active_screen.add_ripple(lx, ly, random.choice(PARTICLE_COLORS))
                            active_screen.add_particle_burst(lx, ly, count=26, shapes=['star', 'confetti', 'sparkle'])
                            self.sound.play_pop()
                        elif event.button == 3: # Botão Direito
                            active_screen.add_ripple(lx, ly, (255, 110, 160))
                            active_screen.add_particle_burst(lx, ly, count=28, shapes=['heart', 'flower', 'sparkle'])
                            self.sound.play_magic()
                        elif event.button in (4, 5): # Roda do rato
                            active_screen.add_particle_burst(lx, ly, count=14, shapes=['bubble', 'sparkle'])
                            self.sound.play_pop()

                # Movimento do Rato (Rastro de Pó de Fada / Estrelas)
                dx = gx - self.last_cursor_pos[0]
                dy = gy - self.last_cursor_pos[1]
                dist = math.hypot(dx, dy)
                if dist > 3.0:
                    active_screen, (lx, ly) = self.get_screen_at_cursor(gx, gy)
                    active_screen.add_fairy_dust(lx, ly)
                    
                    # Se abanarem o rato com energia, produz bolhas e som suave
                    if dist > 85.0 and (now - self.last_shake_sound_time > 0.22):
                        active_screen.add_particle_burst(lx, ly, count=10, shapes=['sparkle', 'bubble'], speed_range=(40, 180))
                        self.sound.play_pop()
                        self.last_shake_sound_time = now
                self.last_cursor_pos = (gx, gy)

                # Verificação de tecla ESC segurada continuamente
                esc_ratio = 0.0
                if self.esc_pressed_time is not None:
                    keys = pygame.key.get_pressed()
                    if keys[pygame.K_ESCAPE]:
                        held_duration = now - self.esc_pressed_time
                        esc_ratio = min(1.0, held_duration / ESCAPE_HOLD_SECONDS)
                        if held_duration >= ESCAPE_HOLD_SECONDS:
                            print("[Teclado Mágico] Saída confirmada pelo utilizador.")
                            self.running = False
                            break
                    else:
                        self.esc_pressed_time = None

                # Reafirmação periódica de topmost a cada 3 segundos
                if now - self.last_topmost_check > 3.0:
                    for win in self.windows:
                        try:
                            win.always_on_top = True
                        except Exception:
                            pass
                    self.last_topmost_check = now

                # Exibe banner de boas-vindas nos primeiros 5 segundos
                show_welcome = (now - self.start_time < 5.0)

                # Atualiza e Renderiza todos os monitores
                for screen_obj in self.screens:
                    screen_obj.update(dt)
                    screen_obj.render(esc_ratio=esc_ratio, show_welcome=show_welcome)

        finally:
            self.teardown()

    def teardown(self):
        """Limpeza limpa de recursos ao sair."""
        print("[Teclado Mágico] A encerrar janelas e a libertar recursos...")
        for win in self.windows:
            try:
                win.destroy()
            except Exception:
                pass
        pygame.quit()
        print("[Teclado Mágico] Aplicação terminada com sucesso.")


if __name__ == '__main__':
    app = KeyboardSmasherApp()
    app.run()

