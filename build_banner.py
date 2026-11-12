"""
Script para compor a imagem de demonstração do README.
Utiliza capturas REAIS do jogo e combina-as num mockup de secretária com 2 monitores,
teclado, rato e a silhueta da criança a brincar.
"""

import math
import pygame
from PIL import Image, ImageDraw, ImageFilter
from visual_engine import MonitorScreen
from config import BACKGROUND_PALETTE, PARTICLE_COLORS


def capture_real_game_screens():
    """Gera e captura frames reais com o motor visual nativo do jogo."""
    pygame.init()
    pygame.font.init()
    from pygame._sdl2.video import Window, Renderer

    w, h = 1280, 720
    win1 = Window('Cap1', size=(w, h))
    ren1 = Renderer(win1)
    win2 = Window('Cap2', size=(w, h))
    ren2 = Renderer(win2)

    s1 = MonitorScreen(0, win1, ren1, (0, 0, w, h), is_primary=True)
    s2 = MonitorScreen(1, win2, ren2, (w, 0, w, h), is_primary=False)

    # Monitor 1 (Esquerdo): Tecla 'A' 🚀 com explosão real de estrelas e brilhos
    s1.bg_color = [35, 65, 100]
    s1.target_bg_color = [35, 65, 100]
    s1.add_badge('A', '🚀', w // 2 - 30, h // 2 + 10, (255, 220, 50))
    s1.add_particle_burst(w // 2 - 30, h // 2 + 10, count=45, speed_range=(100, 360))
    s1.add_ripple(w // 2 - 30, h // 2 + 10, (255, 120, 160))
    for i in range(18):
        s1.add_fairy_dust(260 + i * 26, 200 + i * 14)

    # Monitor 2 (Direito): Tecla 'B' 🎈 e '7' 🌈 com corações, bolhas e confetes reais
    s2.bg_color = [85, 45, 95]
    s2.target_bg_color = [85, 45, 95]
    s2.add_badge('B', '🎈', w // 2 - 140, h // 2, (255, 110, 220))
    s2.add_badge('7', '🌈', w // 2 + 150, h // 2 + 30, (80, 230, 255))
    s2.add_particle_burst(w // 2 - 140, h // 2, count=35, shapes=['star', 'confetti', 'heart', 'sparkle'])
    s2.add_particle_burst(w // 2 + 150, h // 2 + 30, count=30, shapes=['star', 'bubble', 'flower'])
    s2.add_ripple(w // 2 - 140, h // 2, (100, 220, 255))
    for i in range(18):
        s2.add_fairy_dust(960 - i * 25, 230 + i * 12)

    # Atualiza a física do jogo por 10 frames
    for _ in range(10):
        s1.update(1/60.0)
        s2.update(1/60.0)

    cap1 = s1.render(capture=True)
    cap2 = s2.render(capture=True)

    pygame.image.save(cap1, 'temp_s1.png')
    pygame.image.save(cap2, 'temp_s2.png')

    win1.destroy()
    win2.destroy()
    pygame.quit()


def create_mockup_banner(output_path='preview.png'):
    capture_real_game_screens()

    # Dimensões da imagem final (16:9 widescreen)
    canvas_w, canvas_h = 1920, 1080
    banner = Image.new('RGBA', (canvas_w, canvas_h), (14, 17, 25, 255))
    draw = ImageDraw.Draw(banner)

    # 1. Fundo Gradiente e Iluminação Ambiente da Sala
    for y in range(canvas_h):
        ratio = y / canvas_h
        r = int(14 + (24 - 14) * (1.0 - ratio))
        g = int(17 + (28 - 17) * (1.0 - ratio))
        b = int(25 + (38 - 25) * (1.0 - ratio))
        draw.line([(0, y), (canvas_w, y)], fill=(r, g, b, 255))

    # Glow atrás dos monitores na parede
    glow_layer = Image.new('RGBA', (canvas_w, canvas_h), (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow_layer)
    # Glow ciano sob monitor esquerdo
    glow_draw.ellipse([80, 80, 950, 620], fill=(40, 110, 180, 80))
    # Glow roxo sob monitor direito
    glow_draw.ellipse([970, 80, 1840, 620], fill=(140, 50, 150, 75))
    glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(80))
    banner.alpha_composite(glow_layer)

    # 2. Desenho da Secretária de Madeira Moderna
    desk_top_y = 610
    for y in range(desk_top_y, canvas_h):
        dy = (y - desk_top_y) / (canvas_h - desk_top_y)
        # Tom de madeira nogueira escura
        r = int(28 + 12 * (1.0 - dy))
        g = int(24 + 10 * (1.0 - dy))
        b = int(22 + 8 * (1.0 - dy))
        draw.line([(0, y), (canvas_w, y)], fill=(r, g, b, 255))

    # Borda superior e reflexo da secretária
    draw.line([(0, desk_top_y), (canvas_w, desk_top_y)], fill=(75, 70, 65, 255), width=2)
    draw.line([(0, desk_top_y + 1), (canvas_w, desk_top_y + 1)], fill=(45, 42, 40, 255), width=1)

    # Reflexos suaves coloridos das telas na madeira
    desk_reflect = Image.new('RGBA', (canvas_w, canvas_h), (0, 0, 0, 0))
    d_ref_draw = ImageDraw.Draw(desk_reflect)
    d_ref_draw.ellipse([140, desk_top_y - 20, 920, desk_top_y + 220], fill=(45, 100, 160, 45))
    d_ref_draw.ellipse([1000, desk_top_y - 20, 1780, desk_top_y + 220], fill=(130, 50, 130, 40))
    desk_reflect = desk_reflect.filter(ImageFilter.GaussianBlur(40))
    banner.alpha_composite(desk_reflect)

    # Tapete de Secretária (Desk Mat)
    mat_x1, mat_y1 = 520, 635
    mat_x2, mat_y2 = 1400, 980
    draw.rounded_rectangle([mat_x1, mat_y1, mat_x2, mat_y2], radius=16, fill=(18, 20, 26, 240), outline=(40, 44, 56, 255), width=2)

    # 3. Suporte dos Monitores
    # Base e braço central
    draw.rounded_rectangle([920, 570, 1000, 630], radius=6, fill=(25, 27, 34, 255), outline=(50, 55, 68, 255), width=2)
    draw.rectangle([945, 320, 975, 580], fill=(22, 24, 30, 255))
    draw.line([(944, 320), (944, 580)], fill=(45, 50, 62, 255), width=2)

    # 4. Monitores e Conteúdo Real do Jogo
    mon_w, mon_h = 790, 450
    bezel = 8
    mon1_x, mon1_y = 135, 145
    mon2_x, mon2_y = 995, 145

    # Carrega as capturas reais
    s1_img = Image.open('temp_s1.png').convert('RGBA')
    s2_img = Image.open('temp_s2.png').convert('RGBA')

    screen_w = mon_w - bezel * 2
    screen_h = mon_h - bezel * 2
    s1_resized = s1_img.resize((screen_w, screen_h), Image.Resampling.LANCZOS)
    s2_resized = s2_img.resize((screen_w, screen_h), Image.Resampling.LANCZOS)

    # Monitor 1 (Moldura + Ecrã Real)
    draw.rounded_rectangle([mon1_x, mon1_y, mon1_x + mon_w, mon1_y + mon_h], radius=10, fill=(20, 22, 28, 255), outline=(65, 72, 88, 255), width=2)
    banner.paste(s1_resized, (mon1_x + bezel, mon1_y + bezel), s1_resized)
    # Bevel interior do ecrã
    draw.rectangle([mon1_x + bezel, mon1_y + bezel, mon1_x + mon_w - bezel, mon1_y + mon_h - bezel], outline=(0, 0, 0, 160), width=1)
    # Luz piloto discreta
    draw.ellipse([mon1_x + mon_w // 2 - 2, mon1_y + mon_h - 6, mon1_x + mon_w // 2 + 2, mon1_y + mon_h - 2], fill=(100, 220, 255, 200))

    # Monitor 2 (Moldura + Ecrã Real)
    draw.rounded_rectangle([mon2_x, mon2_y, mon2_x + mon_w, mon2_y + mon_h], radius=10, fill=(20, 22, 28, 255), outline=(65, 72, 88, 255), width=2)
    banner.paste(s2_resized, (mon2_x + bezel, mon2_y + bezel), s2_resized)
    draw.rectangle([mon2_x + bezel, mon2_y + bezel, mon2_x + mon_w - bezel, mon2_y + mon_h - bezel], outline=(0, 0, 0, 160), width=1)
    draw.ellipse([mon2_x + mon_w // 2 - 2, mon2_y + mon_h - 6, mon2_x + mon_w // 2 + 2, mon2_y + mon_h - 2], fill=(100, 220, 255, 200))

    # 5. Teclado Retroiluminado
    kb_x, kb_y = 660, 670
    kb_w, kb_h = 560, 180
    # Corpo do teclado
    draw.rounded_rectangle([kb_x, kb_y, kb_x + kb_w, kb_y + kb_h], radius=12, fill=(22, 24, 30, 255), outline=(55, 60, 75, 255), width=2)
    # Brilho sob as teclas (RGB suave combinando com os monitores)
    kb_glow = Image.new('RGBA', (canvas_w, canvas_h), (0, 0, 0, 0))
    kb_g_draw = ImageDraw.Draw(kb_glow)
    kb_g_draw.rounded_rectangle([kb_x + 10, kb_y + 10, kb_x + kb_w - 10, kb_y + kb_h - 10], radius=8, fill=(80, 140, 220, 80))
    kb_glow = kb_glow.filter(ImageFilter.GaussianBlur(12))
    banner.alpha_composite(kb_glow)

    # Desenho das teclas individuais organizadas
    rows = 5
    cols = 15
    key_margin_x = 18
    key_margin_y = 16
    avail_w = kb_w - key_margin_x * 2
    avail_h = kb_h - key_margin_y * 2
    kw = avail_w // cols
    kh = avail_h // rows

    for r_idx in range(rows):
        for c_idx in range(cols):
            kx = kb_x + key_margin_x + c_idx * kw + 2
            ky = kb_y + key_margin_y + r_idx * kh + 2
            # Espaço na última linha
            if r_idx == 4 and 4 <= c_idx <= 10:
                if c_idx == 4:
                    draw.rounded_rectangle([kx, ky, kx + kw * 7 - 4, ky + kh - 4], radius=3, fill=(35, 38, 48, 255), outline=(70, 75, 95, 200))
                continue
            draw.rounded_rectangle([kx, ky, kx + kw - 4, ky + kh - 4], radius=3, fill=(32, 35, 44, 255), outline=(65, 70, 88, 180))

    # 6. Rato de Computador Ergonómico
    m_x, m_y = 1270, 715
    m_w, m_h = 76, 124
    draw.rounded_rectangle([m_x, m_y, m_x + m_w, m_y + m_h], radius=28, fill=(24, 26, 32, 255), outline=(55, 60, 75, 255), width=2)
    # Scroll wheel iluminado
    draw.rounded_rectangle([m_x + m_w//2 - 4, m_y + 20, m_x + m_w//2 + 4, m_y + 44], radius=3, fill=(80, 200, 255, 240))
    # Divisão dos botões
    draw.line([(m_x + m_w//2, m_y + 8), (m_x + m_w//2, m_y + 52)], fill=(40, 44, 55, 255), width=1)

    # 7. Silhueta Adorável da Criança no Primeiro Plano
    # Desenhada com curvas elegantes e iluminação de contorno (rim light)
    child_layer = Image.new('RGBA', (canvas_w, canvas_h), (0, 0, 0, 0))
    ch_draw = ImageDraw.Draw(child_layer)

    # Centro da criança
    cx = 940
    # Cabeça e cabelo (maria-chiquinhas fofas de criança pequena)
    head_y = 800
    head_r = 75

    # Tronco / Costas da criança
    body_pts = [
        (cx - 130, canvas_h),
        (cx - 100, head_y + 90),
        (cx - 70, head_y + 50),
        (cx + 70, head_y + 50),
        (cx + 100, head_y + 90),
        (cx + 130, canvas_h),
    ]
    ch_draw.polygon(body_pts, fill=(10, 11, 16, 255))

    # Cabeça
    ch_draw.ellipse([cx - head_r, head_y - head_r, cx + head_r, head_y + head_r], fill=(10, 11, 16, 255))

    # Cabelo / Penteado infantil com totós / maria-chiquinhas
    ch_draw.ellipse([cx - head_r - 28, head_y - 55, cx - head_r + 15, head_y - 10], fill=(10, 11, 16, 255))
    ch_draw.ellipse([cx + head_r - 15, head_y - 55, cx + head_r + 28, head_y - 10], fill=(10, 11, 16, 255))
    ch_draw.ellipse([cx - 40, head_y - head_r - 18, cx + 40, head_y - head_r + 30], fill=(10, 11, 16, 255))

    # Braços estendidos em direção ao teclado com energia
    # Braço esquerdo
    arm_l_pts = [
        (cx - 85, head_y + 70),
        (cx - 135, head_y + 10),
        (cx - 105, head_y - 25),
        (cx - 70, head_y - 30), # Mão esquerda sobre o teclado
        (cx - 50, head_y + 15),
        (cx - 60, head_y + 70),
    ]
    ch_draw.polygon(arm_l_pts, fill=(10, 11, 16, 255))
    # Mãozinha esquerda com dedinhos a carregar
    ch_draw.ellipse([cx - 110, head_y - 45, cx - 60, head_y - 10], fill=(10, 11, 16, 255))

    # Braço direito
    arm_r_pts = [
        (cx + 85, head_y + 70),
        (cx + 135, head_y + 10),
        (cx + 105, head_y - 25),
        (cx + 70, head_y - 30), # Mão direita sobre o teclado
        (cx + 50, head_y + 15),
        (cx + 60, head_y + 70),
    ]
    ch_draw.polygon(arm_r_pts, fill=(10, 11, 16, 255))
    # Mãozinha direita
    ch_draw.ellipse([cx + 60, head_y - 45, cx + 110, head_y - 10], fill=(10, 11, 16, 255))

    # 8. Efeito de Luz de Contorno (Rim Light) na Silhueta
    # Produz o brilho mágico dos ecrãs a iluminar o contorno da criança
    rim_layer = Image.new('RGBA', (canvas_w, canvas_h), (0, 0, 0, 0))
    rim_draw = ImageDraw.Draw(rim_layer)
    # Lado esquerdo recebe luz ciano/azul do monitor 1
    rim_draw.ellipse([cx - head_r - 2, head_y - head_r - 2, cx - head_r + 30, head_y + head_r + 2], fill=(80, 200, 255, 140))
    rim_draw.ellipse([cx - 115, head_y - 50, cx - 80, head_y - 10], fill=(100, 220, 255, 180))
    # Lado direito recebe luz rosa/magenta do monitor 2
    rim_draw.ellipse([cx + head_r - 30, head_y - head_r - 2, cx + head_r + 2, head_y + head_r + 2], fill=(240, 100, 200, 140))
    rim_draw.ellipse([cx + 80, head_y - 50, cx + 115, head_y - 10], fill=(240, 110, 210, 180))

    rim_layer = rim_layer.filter(ImageFilter.GaussianBlur(6))

    # Junta as camadas da criança
    banner.alpha_composite(child_layer)
    # Aplica o brilho de contorno apenas nas bordas
    banner.alpha_composite(rim_layer)

    # 9. Converte para RGB e guarda a imagem final
    final_banner = banner.convert('RGB')
    final_banner.save(output_path, 'PNG', quality=95)
    print(f"[Mockup] Imagem final gerada com sucesso em: {output_path}")


if __name__ == '__main__':
    create_mockup_banner('preview.png')
