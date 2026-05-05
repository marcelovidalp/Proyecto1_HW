import wave, struct, math

NOTAS = {
    'Do': 261.63, 'Re': 293.66, 'Mi': 329.63,
    'Fa': 349.23, 'Sol': 392.00, 'La': 440.00, 'Si': 493.88,
}
ESCALA_ASC  = ['Do', 'Re', 'Mi', 'Fa', 'Sol', 'La', 'Si']
ESCALA_DESC = ['Si', 'La', 'Sol', 'Fa', 'Mi', 'Re', 'Do']


def genNota(freq, length, rate):
    n = int(rate * length)
    return [math.sin(2 * math.pi * freq / rate * i) for i in range(n)]


def wWavMono(name, freqs, length, rate, width=32767):
    with wave.open(name, 'w') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(rate)
        for f in freqs:
            data = b''.join(struct.pack('<h', int(s * width)) for s in genNota(f, length, rate))
            wf.writeframes(data)
    print(f"GENERADO: {name}")


def wWavStereo(name, freqs, length, rate, width=32767):
    with wave.open(name, 'w') as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(rate)
        for f in freqs:
            data = b''.join(struct.pack('<hh', int(s * width), int(s * width)) for s in genNota(f, length, rate))
            wf.writeframes(data)
    print(f"GENERADO: {name}")


def genOndaStereo(name, rate, duration):
    """Item 4: y = 8000*sin(2*pi*500/RATE*i) + 8000*sin(2*pi*250/RATE*i), ambos canales."""
    n = int(rate * duration)
    frames = []
    for i in range(n):
        val = int(8000 * math.sin(2 * math.pi * 500.0 / rate * i) +
                  8000 * math.sin(2 * math.pi * 250.0 / rate * i))
        val = max(-32767, min(32767, val))
        frames.append(struct.pack('<hh', val, val))
    with wave.open(name, 'w') as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(rate)
        wf.writeframes(b''.join(frames))
    print(f"GENERADO: {name}")


def reducirVolumen(src, dst, factor=0.25):
    """Item 5: reduce el volumen en (1-factor)*100%. factor=0.25 => baja 75%."""
    with wave.open(src, 'r') as wf:
        params = wf.getparams()
        raw = wf.readframes(wf.getnframes())
    n = len(raw) // 2
    fmt = f'<{n}h'
    samples = struct.unpack(fmt, raw)
    with wave.open(dst, 'w') as wf:
        wf.setparams(params)
        wf.writeframes(struct.pack(fmt, *(int(s * factor) for s in samples)))
    print(f"GENERADO: {dst}")


def limpiarCanalIzq(src, dst):
    """Item 6: pone a 0 el canal izquierdo (indices pares en stereo interleaved)."""
    with wave.open(src, 'r') as wf:
        params = wf.getparams()
        raw = wf.readframes(wf.getnframes())
    n = len(raw) // 2
    fmt = f'<{n}h'
    samples = list(struct.unpack(fmt, raw))
    for i in range(0, len(samples), 2):   # L=par, R=impar
        samples[i] = 0
    with wave.open(dst, 'w') as wf:
        wf.setparams(params)
        wf.writeframes(struct.pack(fmt, *samples))
    print(f"GENERADO: {dst}")
