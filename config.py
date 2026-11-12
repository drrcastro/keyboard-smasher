"""
Configurações e dados para o Teclado Mágico (Keyboard Smasher).
"""

# Tempo necessário segurando ESC para sair (segurança para crianças não saírem sem querer)
ESCAPE_HOLD_SECONDS = 2.0

# Taxa de quadros alvo
TARGET_FPS = 60

# Volume inicial padrão (0.0 a 1.0)
DEFAULT_VOLUME = 0.8

# Cores suaves e vibrantes para o fundo (interpolação suave)
BACKGROUND_PALETTE = [
    (38, 50, 72),     # Azul meia-noite suave
    (42, 82, 115),    # Azul oceano
    (35, 110, 105),   # Verde esmeralda pastel
    (92, 55, 110),    # Roxo mágico
    (130, 50, 85),    # Magenta profundo
    (115, 65, 45),    # Coral acolhedor
    (45, 95, 75),     # Menta profundo
    (55, 60, 115),    # Índigo estrelado
    (120, 70, 120),   # Lilás vibrante
    (30, 80, 95),     # Turquesa
]

# Mapeamento de letras para emojis fofos e educativos
LETTER_EMOJIS = {
    'A': '🚀', 'B': '🎈', 'C': '🐱', 'D': '🐬', 'E': '⭐',
    'F': '🌸', 'G': '🦒', 'H': '🚁', 'I': '🍦', 'J': '🌈',
    'K': '🥝', 'L': '🦁', 'M': '🐵', 'N': '☁️', 'O': '🐑',
    'P': '🐼', 'Q': '🧀', 'R': '🤖', 'S': '☀️', 'T': '🐯',
    'U': '🦄', 'V': '🐮', 'W': '🧇', 'X': '👑', 'Y': '🪀',
    'Z': '🦓',
    # Números
    '0': '🍩', '1': '🥇', '2': '✌️', '3': '🎂', '4': '🍀',
    '5': '⭐', '6': '🎲', '7': '🌈', '8': '🐙', '9': '🎈',
    # Teclas especiais
    'SPACE': '🎆', 'RETURN': '💖', 'BACKSPACE': '🫧',
    'TAB': '✨', 'UP': '🚀', 'DOWN': '⚓', 'LEFT': '⬅️', 'RIGHT': '➡️'
}

# Nomes bonitos para teclas especiais
SPECIAL_KEY_NAMES = {
    'SPACE': 'ESPAÇO',
    'RETURN': 'ENTER',
    'BACKSPACE': 'APAGAR',
    'TAB': 'TAB',
    'UP': 'CIMA',
    'DOWN': 'BAIXO',
    'LEFT': 'ESQUERDA',
    'RIGHT': 'DIREITA'
}

# Cores vivas para partículas e confetis (RGB)
PARTICLE_COLORS = [
    (255, 95, 140),   # Rosa choque
    (255, 160, 50),   # Laranja sol
    (255, 230, 60),   # Amarelo ouro
    (80, 225, 140),   # Verde lima
    (50, 210, 255),   # Ciano elétrico
    (160, 110, 255),  # Roxo neon
    (255, 110, 220),  # Magenta
    (255, 255, 255),  # Branco brilhante
    (255, 215, 0),    # Dourado
    (100, 255, 218),  # Turquesa claro
]
