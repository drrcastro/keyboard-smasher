"""
Motor Visual e de Partículas para o Teclado Mágico.
Desenha formas vetoriais, estrelas, confetes, bolhas, corações e badges animados
usando aceleração por GPU (SDL2 Renderer) para atingir 60+ FPS em múltiplos monitores.
"""

import math
import random
import pygame
from pygame._sdl2.video import Texture

from config import (
    BACKGROUND_PALETTE,
    LETTER_EMOJIS,
    SPECIAL_KEY_NAMES,
    PARTICLE_COLORS,
    ESCAPE_HOLD_SECONDS
)


def create_master_shapes(renderer, size=128):
    """Gera texturas mestras em branco com canal alfa para cada forma vetorial."""
    shapes = {}
    cx, cy = size / 2.0, size / 2.0

    # 1. Estrela (5 pontas)
    s_star = pygame.Surface((size, size), pygame.SRCALPHA)
    r_out, r_in = size * 0.46, size * 0.20
    pts_star = []
    for i in range(10):
        r = r_out if i % 2 == 0 else r_in
        a = -math.pi / 2 + i * (math.pi / 5)
        pts_star.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    pygame.draw.polygon(s_star, (255, 255, 255, 255), pts_star)
    shapes['star'] = Texture.from_surface(renderer, s_star)

    # 2. Brilho Diamante / Centelha (Astroid)
    s_sparkle = pygame.Surface((size, size), pygame.SRCALPHA)
    pts_sp = []
    for i in range(32):
        t = i * (2 * math.pi / 32)
        x = cx + (size * 0.44) * (math.cos(t) ** 3)
        y = cy + (size * 0.44) * (math.sin(t) ** 3)
        pts_sp.append((x, y))
    pygame.draw.polygon(s_sparkle, (255, 255, 255, 255), pts_sp)
    shapes['sparkle'] = Texture.from_surface(renderer, s_sparkle)

    # 3. Coração Suave
    s_heart = pygame.Surface((size, size), pygame.SRCALPHA)
    pts_h = []
    sc = size / 36.0
    for i in range(60):
        t = i * (2 * math.pi / 60)
        x = 16 * (math.sin(t) ** 3)
        y = -(13 * math.cos(t) - 5 * math.cos(2*t) - 2 * math.cos(3*t) - math.cos(4*t))
        pts_h.append((cx + x * sc, cy - 3 + y * sc))
    pygame.draw.polygon(s_heart, (255, 255, 255, 255), pts_h)
    shapes['heart'] = Texture.from_surface(renderer, s_heart)

    # 4. Bolha de Sabão com Brilho 3D
    s_bubble = pygame.Surface((size, size), pygame.SRCALPHA)
    r_bub = int(size * 0.44)
    pygame.draw.circle(s_bubble, (255, 255, 255, 210), (int(cx), int(cy)), r_bub, width=5)
    pygame.draw.circle(s_bubble, (255, 255, 255, 35), (int(cx), int(cy)), r_bub - 5)
    hx, hy = int(cx - r_bub * 0.35), int(cy - r_bub * 0.35)
    pygame.draw.circle(s_bubble, (255, 255, 255, 250), (hx, hy), int(r_bub * 0.22))
    pygame.draw.circle(s_bubble, (255, 255, 255, 170), (int(cx + r_bub * 0.3), int(cy + r_bub * 0.3)), int(r_bub * 0.1))
    shapes['bubble'] = Texture.from_surface(renderer, s_bubble)

    # 5. Anel / Shockwave Ripple
    s_ring = pygame.Surface((size, size), pygame.SRCALPHA)
    pygame.draw.circle(s_ring, (255, 255, 255, 255), (int(cx), int(cy)), int(size * 0.44), width=6)
    shapes['ring'] = Texture.from_surface(renderer, s_ring)

    # 6. Confete Retangular
    s_conf = pygame.Surface((size, size), pygame.SRCALPHA)
    cw, ch = int(size * 0.65), int(size * 0.35)
    pygame.draw.rect(s_conf, (255, 255, 255, 255), ((size - cw)//2, (size - ch)//2, cw, ch), border_radius=6)
    shapes['confetti'] = Texture.from_surface(renderer, s_conf)

    # 7. Flor com 5 Pétalas
    s_flower = pygame.Surface((size, size), pygame.SRCALPHA)
    petals = 5
    pr = size * 0.22
    for p in range(petals):
        pa = p * (2 * math.pi / petals)
        px = cx + pr * 1.1 * math.cos(pa)
        py = cy + pr * 1.1 * math.sin(pa)
        pygame.draw.circle(s_flower, (255, 255, 255, 230), (int(px), int(py)), int(pr))
    pygame.draw.circle(s_flower, (255, 255, 255, 255), (int(cx), int(cy)), int(pr * 0.95))
    shapes['flower'] = Texture.from_surface(renderer, s_flower)

    # 8. Círculo / Ponto de Brilho
    s_circle = pygame.Surface((size, size), pygame.SRCALPHA)
    pygame.draw.circle(s_circle, (255, 255, 255, 255), (int(cx), int(cy)), int(size * 0.44))
    shapes['circle'] = Texture.from_surface(renderer, s_circle)

    return shapes


class Particle:
    """Uma partícula animada (estrela, confete, coração, bolha, brilho)."""
    def __init__(self, shape, x, y, vx, vy, color, size=40, max_life=1.5, gravity=180.0, drag=0.98, spin=0.0):
        self.shape = shape
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.base_size = size
        self.size = size
        self.max_life = max_life
        self.life = max_life
        self.gravity = gravity
        self.drag = drag
        self.angle = random.uniform(0, 360)
        self.spin = spin
        self.alive = True

    def update(self, dt):
        self.life -= dt
        if self.life <= 0:
            self.alive = False
            return

        # Movimento com atrito e gravidade suave
        self.vx *= (self.drag ** (dt * 60))
        self.vy *= (self.drag ** (dt * 60))
        self.vy += self.gravity * dt
        
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.angle += self.spin * dt

        # Alpha proporcional ao tempo de vida restante
        self.alpha = int(255 * (self.life / self.max_life))


class RippleShockwave:
    """Onda de choque circular expansiva quando o utilizador clica."""
    def __init__(self, x, y, color, max_radius=220, duration=0.6):
        self.x = x
        self.y = y
        self.color = color
        self.max_radius = max_radius
        self.radius = 10.0
        self.duration = duration
        self.life = duration
        self.alive = True

    def update(self, dt):
        self.life -= dt
        if self.life <= 0:
            self.alive = False
            return
        progress = 1.0 - (self.life / self.duration)
        # Expansão rápida no início, desacelera no fim
        ease = 1.0 - (1.0 - progress) ** 3
        self.radius = 10.0 + (self.max_radius - 10.0) * ease
        self.alpha = int(255 * (1.0 - progress))


class KeyBadge:
    """Letra / Número / Símbolo gigante que salta e flutua no ecrã."""
    def __init__(self, text, emoji, x, y, color, scale_factor=1.0, duration=2.4):
        self.text = text
        self.emoji = emoji
        self.x = x
        self.y = y
        self.color = color
        self.scale_factor = scale_factor
        self.duration = duration
        self.life = duration
        self.vx = random.uniform(-15, 15)
        self.vy = random.uniform(-40, -15) # Flutua suavemente para cima
        self.angle = random.uniform(-6, 6)
        self.spin = random.uniform(-2, 2)
        self.alive = True
        self.current_scale = 0.2

    def update(self, dt):
        self.life -= dt
        if self.life <= 0:
            self.alive = False
            return

        self.x += self.vx * dt
        self.y += self.vy * dt
        self.angle += self.spin * dt

        # Animação de pop-in (elastic bounce)
        elapsed = self.duration - self.life
        if elapsed < 0.25:
            # Salto inicial com overshoot
            t = elapsed / 0.25
            self.current_scale = self.scale_factor * (1.0 + 0.3 * math.sin(t * math.pi))
        else:
            self.current_scale = self.scale_factor

        # Desvanecimento suave nos últimos 0.8 segundos
        if self.life < 0.8:
            self.alpha = int(255 * (self.life / 0.8))
        else:
            self.alpha = 255


class AmbientElement:
    """Estrelas e bolhas suaves de fundo para os monitores nunca ficarem estáticos."""
    def __init__(self, w, h):
        self.w = w
        self.h = h
        self.reset(random_start=True)

    def reset(self, random_start=False):
        self.shape = random.choice(['star', 'bubble', 'sparkle'])
        self.x = random.uniform(0, self.w)
        self.y = random.uniform(0, self.h) if random_start else self.h + 50
        self.size = random.uniform(18, 48)
        self.vx = random.uniform(-10, 10)
        self.vy = random.uniform(-35, -15) # Flutua para cima
        self.color = random.choice(PARTICLE_COLORS)
        self.alpha = random.randint(50, 140)
        self.angle = random.uniform(0, 360)
        self.spin = random.uniform(-20, 20)

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.angle += self.spin * dt
        if self.y < -60 or self.x < -60 or self.x > self.w + 60:
            self.reset(random_start=False)


class MonitorScreen:
    """Gere o renderizador, janela, texturas e objetos visuais de um monitor específico."""
    def __init__(self, index, window, renderer, rect, is_primary=False):
        self.index = index
        self.window = window
        self.renderer = renderer
        self.rect = rect # (x, y, w, h)
        self.x, self.y, self.w, self.h = rect
        self.is_primary = is_primary

        # Fator de escala baseado na resolução (referência: 1080p = 1.0, 4K = 2.0)
        self.scale = max(0.8, min(self.w / 1920.0, self.h / 1080.0))

        # Texturas mestras
        self.master_shapes = create_master_shapes(renderer, size=128)
        self.badge_cache = {}
        self.ui_text_cache = {}

        # Listas de entidades visuais ativas
        self.particles = []
        self.ripples = []
        self.badges = []
        
        # Elementos de fundo ambiente (15 por ecrã)
        self.ambient = [AmbientElement(self.w, self.h) for _ in range(16)]

        # Cores de fundo (interpolação suave)
        self.bg_color = list(random.choice(BACKGROUND_PALETTE))
        self.target_bg_color = list(self.bg_color)

    def set_target_background(self, color):
        self.target_bg_color = list(color)

    def add_badge(self, text, emoji, x, y, color):
        badge = KeyBadge(text, emoji, x, y, color, scale_factor=self.scale)
        self.badges.append(badge)
        # Limita badges simultâneos para manter o ecrã limpo
        if len(self.badges) > 8:
            self.badges.pop(0)

    def add_particle_burst(self, x, y, count=30, shapes=None, colors=None, speed_range=(100, 450)):
        if shapes is None:
            shapes = ['star', 'sparkle', 'confetti', 'heart', 'flower', 'bubble']
        if colors is None:
            colors = PARTICLE_COLORS

        for _ in range(count):
            shp = random.choice(shapes)
            clr = random.choice(colors)
            angle = random.uniform(0, 2 * math.pi)
            spd = random.uniform(speed_range[0], speed_range[1]) * self.scale
            vx = math.cos(angle) * spd
            vy = math.sin(angle) * spd
            size = random.uniform(22, 50) * self.scale
            life = random.uniform(1.0, 2.2)
            grav = random.uniform(120, 260) * self.scale
            spin = random.uniform(-180, 180)
            p = Particle(shp, x, y, vx, vy, clr, size=size, max_life=life, gravity=grav, spin=spin)
            self.particles.append(p)

    def add_ripple(self, x, y, color):
        r = RippleShockwave(x, y, color, max_radius=int(260 * self.scale))
        self.ripples.append(r)

    def add_fairy_dust(self, x, y, color=None):
        """Partículas cintilantes que seguem o movimento do rato."""
        if color is None:
            color = random.choice(PARTICLE_COLORS)
        shp = random.choice(['sparkle', 'star', 'bubble', 'circle'])
        vx = random.uniform(-25, 25) * self.scale
        vy = random.uniform(-45, -15) * self.scale
        size = random.uniform(14, 28) * self.scale
        life = random.uniform(0.4, 0.8)
        p = Particle(shp, x, y, vx, vy, color, size=size, max_life=life, gravity=-20, drag=0.95, spin=random.uniform(-90, 90))
        self.particles.append(p)

    def _get_badge_texture(self, text, emoji, color):
        """Cria e guarda em cache a textura de um badge de letra/emoji para este renderizador."""
        key = (text, emoji, color)
        if key in self.badge_cache:
            return self.badge_cache[key]

        font_size = int(115 * self.scale) if len(text) <= 2 else int(65 * self.scale)
        emoji_size = int(90 * self.scale)
        font_letter = pygame.font.SysFont('Arial', font_size, bold=True)
        font_emoji = pygame.font.SysFont('segoeuiemoji', emoji_size)

        s_text = font_letter.render(text, True, color)
        s_emoji = font_emoji.render(emoji, True, (255, 255, 255))

        pad_x = int(32 * self.scale)
        pad_y = int(20 * self.scale)
        gap = int(22 * self.scale)
        w = s_text.get_width() + s_emoji.get_width() + pad_x * 2 + gap
        h = max(s_text.get_height(), s_emoji.get_height()) + pad_y * 2

        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        radius = int(h * 0.35)
        # Fundo translúcido elegante e rebordo colorido
        pygame.draw.rect(surf, (15, 20, 35, 205), (0, 0, w, h), border_radius=radius)
        pygame.draw.rect(surf, (*color, 240), (0, 0, w, h), width=max(3, int(4 * self.scale)), border_radius=radius)

        ty = (h - s_text.get_height()) // 2
        ey = (h - s_emoji.get_height()) // 2
        surf.blit(s_text, (pad_x, ty))
        surf.blit(s_emoji, (pad_x + s_text.get_width() + gap, ey))

        tex = Texture.from_surface(self.renderer, surf)
        self.badge_cache[key] = (tex, w, h)
        return self.badge_cache[key]

    def update(self, dt):
        """Atualiza física e interpolação de cores."""
        # Interpolação suave do fundo (lerp)
        for i in range(3):
            self.bg_color[i] += (self.target_bg_color[i] - self.bg_color[i]) * min(1.0, dt * 3.5)

        # Atualiza ambiente
        for amb in self.ambient:
            amb.update(dt)

        # Atualiza ripples
        for rip in self.ripples:
            rip.update(dt)
        self.ripples = [r for r in self.ripples if r.alive]

        # Atualiza partículas
        for p in self.particles:
            p.update(dt)
        self.particles = [p for p in self.particles if p.alive]

        # Limite máximo de partículas por segurança de desempenho
        if len(self.particles) > 300:
            self.particles = self.particles[-300:]

        # Atualiza badges
        for b in self.badges:
            b.update(dt)
        self.badges = [b for b in self.badges if b.alive]

    def render(self, esc_ratio=0.0, show_welcome=False):
        """Desenha todos os elementos com aceleração GPU."""
        ren = self.renderer
        # 1. Limpa fundo com cor interpolada
        ren.draw_color = (int(self.bg_color[0]), int(self.bg_color[1]), int(self.bg_color[2]), 255)
        ren.clear()

        # 2. Desenha elementos ambiente suaves
        for amb in self.ambient:
            tex = self.master_shapes.get(amb.shape)
            if tex:
                tex.color = amb.color
                tex.alpha = amb.alpha
                sz = int(amb.size * self.scale)
                dst = pygame.Rect(int(amb.x - sz/2), int(amb.y - sz/2), sz, sz)
                tex.draw(dstrect=dst, angle=amb.angle)

        # 3. Desenha Ripples
        ring_tex = self.master_shapes.get('ring')
        if ring_tex:
            for rip in self.ripples:
                ring_tex.color = rip.color
                ring_tex.alpha = rip.alpha
                sz = int(rip.radius * 2)
                dst = pygame.Rect(int(rip.x - rip.radius), int(rip.y - rip.radius), sz, sz)
                ring_tex.draw(dstrect=dst)

        # 4. Desenha Partículas
        for p in self.particles:
            tex = self.master_shapes.get(p.shape, self.master_shapes.get('star'))
            if tex:
                tex.color = p.color
                tex.alpha = p.alpha
                sz = int(p.size)
                dst = pygame.Rect(int(p.x - sz/2), int(p.y - sz/2), sz, sz)
                tex.draw(dstrect=dst, angle=p.angle)

        # 5. Desenha Badges de Letras/Números
        for b in self.badges:
            tex, bw, bh = self._get_badge_texture(b.text, b.emoji, b.color)
            tex.alpha = b.alpha
            scaled_w = int(bw * b.current_scale)
            scaled_h = int(bh * b.current_scale)
            dst = pygame.Rect(int(b.x - scaled_w/2), int(b.y - scaled_h/2), scaled_w, scaled_h)
            tex.draw(dstrect=dst, angle=b.angle)

        # 6. Indicador de Saída com ESC (Proteção Parental)
        if esc_ratio > 0.05 and self.is_primary:
            self._render_exit_prompt(esc_ratio)

        # 7. Atalho permanente no canto para desbloquear a aplicação
        self._render_unlock_hint()

        # 8. Mensagem inicial de boas-vindas
        if show_welcome and self.is_primary:
            self._render_welcome_banner()

        # Apresenta frame na janela
        ren.present()

    def _get_ui_text(self, text, font_size, color=(255, 255, 255)):
        """Cache para textos de interface."""
        key = (text, font_size, color)
        if key in self.ui_text_cache:
            return self.ui_text_cache[key]
        font = pygame.font.SysFont('Arial', font_size, bold=True)
        s = font.render(text, True, color)
        tex = Texture.from_surface(self.renderer, s)
        self.ui_text_cache[key] = (tex, s.get_width(), s.get_height())
        return self.ui_text_cache[key]

    def _render_unlock_hint(self):
        """Exibe num canto o atalho para desbloquear a aplicação."""
        if not hasattr(self, '_unlock_badge_tex') or self._unlock_badge_tex is None:
            font_size = int(16 * self.scale)
            font = pygame.font.SysFont('Arial', font_size, bold=True)
            font_emoji = pygame.font.SysFont('segoeuiemoji', font_size)

            txt1 = font_emoji.render('🔒', True, (255, 255, 255))
            txt2 = font.render(' Desbloquear: Segurar ESC (2s) | Ctrl+Shift+Q', True, (235, 245, 255))

            pad_x = int(14 * self.scale)
            pad_y = int(8 * self.scale)
            w = txt1.get_width() + txt2.get_width() + pad_x * 2
            h = max(txt1.get_height(), txt2.get_height()) + pad_y * 2

            surf = pygame.Surface((w, h), pygame.SRCALPHA)
            radius = int(h * 0.35)
            # Fundo suave translúcido para não distrair as crianças mas legível para os pais
            pygame.draw.rect(surf, (15, 20, 35, 185), (0, 0, w, h), border_radius=radius)
            pygame.draw.rect(surf, (110, 180, 255, 190), (0, 0, w, h), width=max(2, int(2 * self.scale)), border_radius=radius)

            surf.blit(txt1, (pad_x, (h - txt1.get_height()) // 2))
            surf.blit(txt2, (pad_x + txt1.get_width(), (h - txt2.get_height()) // 2))

            self._unlock_badge_tex = Texture.from_surface(self.renderer, surf)
            self._unlock_badge_w = w
            self._unlock_badge_h = h

        # Posiciona no canto superior direito
        bx = self.w - self._unlock_badge_w - int(20 * self.scale)
        by = int(16 * self.scale)
        dst = pygame.Rect(bx, by, self._unlock_badge_w, self._unlock_badge_h)
        self._unlock_badge_tex.draw(dstrect=dst)

    def _render_exit_prompt(self, ratio):
        """Desenha barra de progresso elegante quando o pai/mãe segura ESC."""
        pw = int(480 * self.scale)
        ph = int(105 * self.scale)
        px = (self.w - pw) // 2
        py = int(60 * self.scale)

        # Caixa de fundo translúcida
        self.renderer.draw_color = (15, 20, 35, 240)
        self.renderer.fill_rect(pygame.Rect(px, py, pw, ph))
        self.renderer.draw_color = (255, 120, 120, 255)
        self.renderer.draw_rect(pygame.Rect(px, py, pw, ph))

        # Texto do aviso
        tex_txt, tw, th = self._get_ui_text("A SAIR... Mantenha ESC premido (2s)", int(22 * self.scale), (255, 230, 230))
        tx = px + (pw - tw) // 2
        ty = py + int(14 * self.scale)
        tex_txt.draw(dstrect=pygame.Rect(tx, ty, tw, th))

        # Barra de progresso interior
        bar_margin = int(20 * self.scale)
        bar_w = pw - (bar_margin * 2)
        bar_h = int(22 * self.scale)
        bar_x = px + bar_margin
        bar_y = py + ph - bar_h - int(16 * self.scale)

        # Fundo da barra
        self.renderer.draw_color = (45, 50, 70, 255)
        self.renderer.fill_rect(pygame.Rect(bar_x, bar_y, bar_w, bar_h))

        # Progresso ativo preenchido (verde brilhante)
        fill_w = int(bar_w * min(1.0, ratio))
        self.renderer.draw_color = (80, 245, 140, 255)
        self.renderer.fill_rect(pygame.Rect(bar_x, bar_y, fill_w, bar_h))

    def _render_welcome_banner(self):
        """Banner suave de ajuda rápida no fundo do ecrã principal."""
        msg = "✨ Mundo Mágico do Teclado | Pais: Segurem ESC durante 2s para sair | F1 Silenciar ✨"
        tex, tw, th = self._get_ui_text(msg, int(18 * self.scale), (255, 255, 255))
        bw = tw + int(36 * self.scale)
        bh = th + int(16 * self.scale)
        bx = (self.w - bw) // 2
        by = self.h - bh - int(25 * self.scale)

        self.renderer.draw_color = (15, 20, 30, 180)
        self.renderer.fill_rect(pygame.Rect(bx, by, bw, bh))
        self.renderer.draw_color = (100, 200, 255, 200)
        self.renderer.draw_rect(pygame.Rect(bx, by, bw, bh))

        tex.draw(dstrect=pygame.Rect(bx + int(18 * self.scale), by + int(8 * self.scale), tw, th))
