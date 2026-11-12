"""
Motor de Som Procedural (SoundEngine)
Gera sons harmoniosos e agradáveis diretamente em memória sem necessidade de ficheiros de áudio externos.
Utiliza escalas pentatónicas para que qualquer tecla premida soe sempre como uma melodia mágica!
"""

import math
import struct
import io
import wave
import random
import pygame


class SoundEngine:
    def __init__(self, sample_rate=44100):
        self.sample_rate = sample_rate
        self.muted = False
        self.volume = 0.8
        self.ready = False
        self.sounds = {}
        self.note_index = 0
        
        # Inicializa mixer do pygame
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=sample_rate, size=-16, channels=2, buffer=512)
            pygame.mixer.set_num_channels(20)
            self._generate_all_sounds()
            self.set_volume(self.volume)
            self.ready = True
        except Exception as e:
            print(f"[SoundEngine] Aviso: Não foi possível inicializar áudio ({e}). O programa funcionará em modo silencioso.")

    def _create_wav_sound(self, gen_fn, duration=0.4):
        """Sintetiza uma função matemática de áudio para pygame.mixer.Sound"""
        n_samples = int(self.sample_rate * duration)
        frames = bytearray()
        
        for i in range(n_samples):
            t = i / self.sample_rate
            vl, vr = gen_fn(t, duration)
            # Clip de 16-bit
            sl = max(-32767, min(32767, int(vl * 26000)))
            sr = max(-32767, min(32767, int(vr * 26000)))
            frames.extend(struct.pack('<hh', sl, sr))
        
        buf = io.BytesIO()
        with wave.open(buf, 'wb') as w:
            w.setnchannels(2)
            w.setsampwidth(2)
            w.setframerate(self.sample_rate)
            w.writeframes(frames)
        buf.seek(0)
        return pygame.mixer.Sound(buf)

    def _generate_all_sounds(self):
        """Gera a biblioteca de efeitos sonoros em memória."""
        # 1. Escala Pentatónica (Marimba / Glockenspiel / Toy Piano)
        # Notas: C4, D4, E4, G4, A4, C5, D5, E5, G5, A5, C6, D6, E6, G6, A6, C7
        pentatonic_freqs = [
            261.63, 293.66, 329.63, 392.00, 440.00,
            523.25, 587.33, 659.25, 783.99, 880.00,
            1046.50, 1174.66, 1318.51, 1567.98, 1760.00, 2093.00
        ]
        
        for idx, freq in enumerate(pentatonic_freqs):
            def make_marimba(f):
                def gen(t, dur):
                    env = math.exp(-5.0 * t / dur)
                    # Tom puro com segundo e terceiro harmónicos suaves (timbre de xilofone/marimba)
                    s = (math.sin(2 * math.pi * f * t) * 0.7 +
                         math.sin(4 * math.pi * f * t) * 0.22 +
                         math.sin(6 * math.pi * f * t) * 0.08) * env
                    return s, s
                return gen
            self.sounds[f'note_{idx}'] = self._create_wav_sound(make_marimba(freq), duration=0.45)
        
        self.num_notes = len(pentatonic_freqs)

        # 2. Pops de Bolha (4 tons diferentes)
        for p_idx, base_f in enumerate([950, 800, 650, 500]):
            def make_pop(bf):
                def gen(t, dur):
                    # Frequência desce muito rápido produzindo o som clássico "plop"
                    cur_f = bf * math.exp(-22 * t)
                    phase = 2 * math.pi * cur_f * t
                    env = math.exp(-28 * t)
                    s = math.sin(phase) * env
                    return s, s
                return gen
            self.sounds[f'pop_{p_idx}'] = self._create_wav_sound(make_pop(base_f), duration=0.12)

        # 3. Mola / Cartoon Boing
        def gen_boing(t, dur):
            # Frequência sobe com modulação de vibrato divertida
            f = 220 + 120 * (t / dur) + 40 * math.sin(2 * math.pi * 20 * t)
            env = math.exp(-3.5 * t / dur)
            s = math.sin(2 * math.pi * f * t) * env
            return s, s
        self.sounds['boing'] = self._create_wav_sound(gen_boing, duration=0.45)

        # 4. Brilho Mágico de Varinha / Fada (Arpeggio rápido de notas cintilantes)
        def gen_magic(t, dur):
            s = 0.0
            sparkle_notes = [(0.00, 1046.5), (0.04, 1318.5), (0.08, 1567.9), (0.12, 2093.0)]
            for offset, freq in sparkle_notes:
                if t >= offset:
                    st = t - offset
                    env = math.exp(-6.5 * st / (dur - offset))
                    s += 0.25 * math.sin(2 * math.pi * freq * st) * env
            return s, s
        self.sounds['magic'] = self._create_wav_sound(gen_magic, duration=0.5)

        # 5. Fogos de Artifício (Assobio ascendente e explosão de estrelas)
        def gen_firework(t, dur):
            if t < 0.18:
                f = 350 + 1500 * (t / 0.18) ** 2
                env = (t / 0.18) * 0.4
                s = math.sin(2 * math.pi * f * t) * env
                return s, s
            else:
                tb = t - 0.18
                env = math.exp(-5.5 * tb / 0.42)
                f = 600 * math.exp(-6.0 * tb)
                sparkle = math.sin(2 * math.pi * f * tb) * 0.4 + 0.25 * math.sin(2 * math.pi * 1800 * tb)
                s = sparkle * env
                return s, s
        self.sounds['firework'] = self._create_wav_sound(gen_firework, duration=0.6)

        # 6. Harpa Celeste (Sweep descendente para o Enter/Corações)
        def gen_harp(t, dur):
            s = 0.0
            notes = [(0.00, 1760.0), (0.03, 1318.5), (0.06, 1046.5), (0.09, 880.0), (0.12, 659.2)]
            for offset, freq in notes:
                if t >= offset:
                    st = t - offset
                    env = math.exp(-4.5 * st / (dur - offset))
                    s += 0.2 * math.sin(2 * math.pi * freq * st) * env
            return s, s
        self.sounds['harp'] = self._create_wav_sound(gen_harp, duration=0.55)

    def play(self, sound_name):
        """Reproduz um som pelo nome se o áudio estiver disponível e não silenciado."""
        if not self.ready or self.muted:
            return
        snd = self.sounds.get(sound_name)
        if snd:
            # Encontra um canal livre para sobreposição perfeita (polifonia)
            chan = pygame.mixer.find_channel(True)
            if chan:
                chan.play(snd)

    def play_musical_note(self, note_idx=None):
        """Reproduz uma nota musical harmoniosa. Se note_idx for None, progride ciclicamente."""
        if not self.ready or self.muted:
            return
        if note_idx is None:
            # Caminhada musical aleatória mas suave
            step = random.choice([-2, -1, 1, 2, 3])
            self.note_index = (self.note_index + step) % self.num_notes
            note_idx = self.note_index
        else:
            note_idx = note_idx % self.num_notes
            
        self.play(f'note_{note_idx}')

    def play_pop(self):
        """Reproduz som de bolha a rebentar."""
        pop_name = f'pop_{random.randint(0, 3)}'
        self.play(pop_name)

    def play_boing(self):
        """Reproduz som divertido de desenho animado (boing)."""
        self.play('boing')

    def play_magic(self):
        """Reproduz som brilhante de fada/magia."""
        self.play('magic')

    def play_firework(self):
        """Reproduz som de fogos de artifício."""
        self.play('firework')

    def play_harp(self):
        """Reproduz som suave de harpa."""
        self.play('harp')

    def toggle_mute(self):
        """Alterna entre silenciado e com som."""
        self.muted = not self.muted
        return self.muted

    def set_volume(self, vol):
        """Ajusta o volume geral (0.0 a 1.0)."""
        self.volume = max(0.0, min(1.0, vol))
        for snd in self.sounds.values():
            snd.set_volume(self.volume)

    def volume_up(self):
        self.set_volume(self.volume + 0.1)
        return self.volume

    def volume_down(self):
        self.set_volume(self.volume - 0.1)
        return self.volume

