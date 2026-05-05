import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ejercicios.ej4.wav_gen import (
    NOTAS, ESCALA_ASC, ESCALA_DESC,
    wWavMono, wWavStereo, genOndaStereo,
    reducirVolumen, limpiarCanalIzq,
)

WAV_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'wavs')
os.makedirs(WAV_DIR, exist_ok=True)

def p(name):
    return os.path.join(WAV_DIR, name)

freqs_asc  = [NOTAS[n] for n in ESCALA_ASC]   # Do Re Mi Fa Sol La Si
freqs_desc = [NOTAS[n] for n in ESCALA_DESC]  # Si La Sol Fa Mi Re Do

# 1. Escala Do->Si | 44100 Hz | Mono
wWavMono(p('ej4_1_escala_44100_mono.wav'), freqs_asc, 1, 44100)

# 2. Escala Si->Do | 22050 Hz | Stereo
wWavStereo(p('ej4_2_escala_22050_stereo.wav'), freqs_desc, 1, 22050)

# 3. Escala Do->Si | 8000 Hz  | Mono
wWavMono(p('ej4_3_escala_8000_mono.wav'), freqs_asc, 1, 8000)

# 4. y = 8000*sin(2pi*500/RATE*i) + 8000*sin(2pi*250/RATE*i) | Stereo | 44100 | 10s
onda = p('ej4_4_onda_compuesta.wav')
genOndaStereo(onda, 44100, 10)

# 5. Bajar volumen 75% (conservar 25%)
vol = p('ej4_5_volumen_reducido.wav')
reducirVolumen(onda, vol, factor=0.25)

# 6. Limpiar canal izquierdo de la señal del item 5
limpiarCanalIzq(vol, p('ej4_6_canal_izq_limpio.wav'))
