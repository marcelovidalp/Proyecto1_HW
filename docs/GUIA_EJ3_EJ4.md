# Guía Ejercicios 3 y 4 — Proyecto #1 INFO1157

**Entrega:** Jueves 30 de Abril, 14:00–18:00 en oficina del profesor.

---

## Ejercicio 3 — Control de Reproductor de Audio por Puerto Serie

### Objetivo

Crear **dos programas Python** (cliente y servidor) que se comuniquen por puerto serie virtual.  
El cliente envía comandos en texto, el servidor los recibe y simula teclas del sistema con `Win32Api` para controlar WINAMP o AIMP.

---

### Arquitectura

```
[cliente.py]  --COM3-->  [VSPE]  --COM4-->  [servidor.py]
  Envía "PLAY\n"                             Recibe "PLAY"
                                             Llama keybd_event(VK_MEDIA_PLAY_PAUSE)
                                             AIMP/Winamp reacciona
```

---

### Paso 1 — Instalar dependencias

```bash
pip install pyserial pywin32
```

También necesitas instalar **VSPE** (Virtual Serial Port Emulator):
- Descarga desde el sitio oficial de Eterlogic
- Crea un par de puertos virtuales: por ejemplo `COM3` ↔ `COM4`
  - En VSPE: **New Device → Pair** → COM3 y COM4

---

### Paso 2 — Virtual Key Codes necesarios

| Acción       | VK Code  | Hex  |
|--------------|----------|------|
| Play/Pause   | `VK_MEDIA_PLAY_PAUSE` | `0xB3` |
| Stop         | `VK_MEDIA_STOP`       | `0xB2` |
| Next Track   | `VK_MEDIA_NEXT_TRACK` | `0xB0` |
| Prev Track   | `VK_MEDIA_PREV_TRACK` | `0xB1` |
| Volume +     | `VK_VOLUME_UP`        | `0xAF` |
| Volume -     | `VK_VOLUME_DOWN`      | `0xAE` |
| Mute         | `VK_VOLUME_MUTE`      | `0xAD` |

> AIMP y Winamp responden a estas media keys globales sin necesitar foco de ventana.

---

### Paso 3 — Código base del servidor (`servidor.py`)

```python
import ctypes
import serial
import time

# Virtual Key Codes
VK_CODES = {
    "PLAY":     0xB3,
    "STOP":     0xB2,
    "NEXT":     0xB0,
    "PREV":     0xB1,
    "VOL+":     0xAF,
    "VOL-":     0xAE,
    "MUTE":     0xAD,
    "PAUSE":    0xB3,  # mismo que PLAY (toggle en media players)
}

KEYEVENTF_KEYUP = 0x0002

def press_key(vk_code):
    """Simula presión y liberación de una tecla virtual."""
    ctypes.windll.user32.keybd_event(vk_code, 0, 0, 0)          # Press
    time.sleep(0.05)
    ctypes.windll.user32.keybd_event(vk_code, 0, KEYEVENTF_KEYUP, 0)  # Release

def main():
    port = "COM4"  # El extremo del servidor en el par VSPE
    baud = 9600

    print(f"[SERVIDOR] Escuchando en {port}...")

    with serial.Serial(port, baud, timeout=1) as ser:
        while True:
            line = ser.readline().decode("utf-8").strip().upper()
            if not line:
                continue

            print(f"[SERVIDOR] Comando recibido: {line}")

            if line in VK_CODES:
                press_key(VK_CODES[line])
                ser.write(f"OK:{line}\n".encode("utf-8"))
            elif line == "EXIT":
                ser.write(b"BYE\n")
                break
            else:
                ser.write(f"ERR:UNKNOWN:{line}\n".encode("utf-8"))

if __name__ == "__main__":
    main()
```

---

### Paso 4 — Código base del cliente (`cliente.py`)

```python
import serial
import time

COMANDOS_VALIDOS = ["PLAY", "STOP", "PAUSE", "NEXT", "PREV", "VOL+", "VOL-", "MUTE", "EXIT"]

def menu():
    print("\n=== CONTROL REPRODUCTOR ===")
    for i, cmd in enumerate(COMANDOS_VALIDOS, 1):
        print(f"  {i}. {cmd}")
    print("===========================")

def main():
    port = "COM3"  # El extremo del cliente en el par VSPE
    baud = 9600

    print(f"[CLIENTE] Conectando a {port}...")

    with serial.Serial(port, baud, timeout=2) as ser:
        time.sleep(1)  # Esperar que el puerto esté listo
        while True:
            menu()
            try:
                opcion = int(input("Selecciona opción: ")) - 1
                if 0 <= opcion < len(COMANDOS_VALIDOS):
                    cmd = COMANDOS_VALIDOS[opcion]
                    ser.write(f"{cmd}\n".encode("utf-8"))
                    respuesta = ser.readline().decode("utf-8").strip()
                    print(f"[RESPUESTA] {respuesta}")
                    if cmd == "EXIT":
                        break
                else:
                    print("Opción inválida.")
            except ValueError:
                print("Ingresa un número.")

if __name__ == "__main__":
    main()
```

---

### Paso 5 — Cómo ejecutar

1. Abre VSPE y activa el par COM3 ↔ COM4
2. Abre AIMP o Winamp con al menos **10 archivos mp3/mp4** en la playlist
3. En una terminal: `python servidor.py`
4. En otra terminal: `python cliente.py`
5. Selecciona comandos desde el cliente y verifica que el reproductor responde

---

### Checklist Ejercicio 3

- [ ] VSPE instalado y par de puertos creado
- [ ] `servidor.py` operativo en COM4
- [ ] `cliente.py` operativo en COM3
- [ ] Todos los comandos funcionan: PLAY, STOP, PAUSE, NEXT, PREV, VOL+, VOL-, MUTE
- [ ] Playlist con ≥ 10 archivos mp3/mp4
- [ ] Protocolo tiene respuesta del servidor (`OK:CMD` / `ERR:...`)

---

---

## Ejercicio 4 — Generación de Audio con el módulo `wave` y `struct`

### Objetivo

Generar archivos `.WAV` desde cero en Python usando `wave` + `struct`, sin librerías de audio externas.  
Cada nota dura **1 segundo** exacto.

---

### Frecuencias de notas (escala Do mayor, octava 4)

| Nota | Frecuencia (Hz) |
|------|-----------------|
| Do   | 261.63          |
| Re   | 293.66          |
| Mi   | 329.63          |
| Fa   | 349.23          |
| Sol  | 392.00          |
| La   | 440.00          |
| Si   | 493.88          |

---

### Concepto clave: cómo funciona `wave` + `struct`

```
Para cada muestra i (i = 0, 1, ..., RATE-1):
    valor_flotante = amplitud * sin(2 * pi * frecuencia / RATE * i)
    valor_entero   = int(valor_flotante)          # convertir a entero 16-bit
    bytes_muestra  = struct.pack('<h', valor_entero)  # '<h' = little-endian signed short (2 bytes)
    escribir bytes_muestra al archivo WAV
```

- `'<h'` → little-endian, entero con signo de 16 bits (rango: -32768 a 32767)
- Amplitud máxima para 16 bits: `32767`
- Para **stereo**, cada frame tiene DOS muestras: `struct.pack('<hh', muestra_izq, muestra_der)`

---

### Función base reutilizable

```python
import wave
import struct
import math

def generar_nota(frecuencia, duracion, rate):
    """Devuelve lista de samples (floats) para una nota sinusoidal."""
    n_samples = int(rate * duracion)
    return [math.sin(2 * math.pi * frecuencia / rate * i) for i in range(n_samples)]

def escribir_wav_mono(nombre, notas_freqs, duracion, rate, amplitud=32767):
    with wave.open(nombre, 'w') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)       # 2 bytes = 16 bits
        wf.setframerate(rate)
        for freq in notas_freqs:
            samples = generar_nota(freq, duracion, rate)
            data = b''.join(struct.pack('<h', int(s * amplitud)) for s in samples)
            wf.writeframes(data)
    print(f"Generado: {nombre}")

def escribir_wav_stereo(nombre, notas_freqs, duracion, rate, amplitud=32767):
    with wave.open(nombre, 'w') as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(rate)
        for freq in notas_freqs:
            samples = generar_nota(freq, duracion, rate)
            # Canal izquierdo y derecho idénticos
            data = b''.join(struct.pack('<hh', int(s * amplitud), int(s * amplitud)) for s in samples)
            wf.writeframes(data)
    print(f"Generado: {nombre}")
```

---

### Sub-tarea 1 — Escala Do→Si, 44100 Hz, Mono

```python
NOTAS_ASC = [261.63, 293.66, 329.63, 349.23, 392.00, 440.00, 493.88]  # Do Re Mi Fa Sol La Si

escribir_wav_mono("escala_44100_mono.wav", NOTAS_ASC, duracion=1, rate=44100)
```

---

### Sub-tarea 2 — Escala Si→Do, 22050 Hz, Stereo

```python
NOTAS_DESC = [493.88, 440.00, 392.00, 349.23, 329.63, 293.66, 261.63]  # Si La Sol Fa Mi Re Do

escribir_wav_stereo("escala_22050_stereo.wav", NOTAS_DESC, duracion=1, rate=22050)
```

---

### Sub-tarea 3 — Escala Do→Si, 8000 Hz, Mono

```python
escribir_wav_mono("escala_8000_mono.wav", NOTAS_ASC, duracion=1, rate=8000)
```

> Nota: a 8000 Hz se pierde calidad en notas altas (La=440, Si=493) porque la tasa de muestreo apenas supera el doble de la frecuencia (teorema de Nyquist).

---

### Sub-tarea 4 — Onda compuesta en Stereo, 44100 Hz, 10 segundos

```
y = 8000*sin(2*pi*500/RATE*i) + 8000*sin(2*pi*250/RATE*i)
```

```python
RATE = 44100
DURACION = 10  # segundos
N = RATE * DURACION

with wave.open("onda_compuesta.wav", 'w') as wf:
    wf.setnchannels(2)
    wf.setsampwidth(2)
    wf.setframerate(RATE)
    for i in range(N):
        muestra = int(
            8000 * math.sin(2 * math.pi * 500.0 / RATE * i) +
            8000 * math.sin(2 * math.pi * 250.0 / RATE * i)
        )
        # Mismo valor en canal L y R
        wf.writeframes(struct.pack('<hh', muestra, muestra))

print("Generado: onda_compuesta.wav")
```

> Abrir en **Audacity**: deberías ver dos picos en el espectro de frecuencias (250 Hz y 500 Hz).

---

### Sub-tarea 5 — Bajar volumen 75%

Reducir la amplitud al **25%** de su valor original (= bajar 75%):

```python
def bajar_volumen(archivo_entrada, archivo_salida, factor=0.25):
    with wave.open(archivo_entrada, 'r') as wf_in:
        params = wf_in.getparams()
        n_frames = wf_in.getnframes()
        n_channels = wf_in.getnchannels()
        raw = wf_in.readframes(n_frames)

    # Unpack todos los samples
    n_samples = n_frames * n_channels
    samples = struct.unpack('<' + 'h' * n_samples, raw)

    # Aplicar factor de volumen
    samples_mod = [int(s * factor) for s in samples]

    # Repack
    raw_mod = struct.pack('<' + 'h' * n_samples, *samples_mod)

    with wave.open(archivo_salida, 'w') as wf_out:
        wf_out.setparams(params)
        wf_out.writeframes(raw_mod)

    print(f"Volumen reducido al {int(factor*100)}%: {archivo_salida}")

bajar_volumen("onda_compuesta.wav", "onda_volumen25.wav", factor=0.25)
```

---

### Sub-tarea 6 — Limpiar canal izquierdo

El canal izquierdo se pone en **cero** (silencio) manteniendo el derecho intacto:

```python
def limpiar_canal_izquierdo(archivo_entrada, archivo_salida):
    with wave.open(archivo_entrada, 'r') as wf_in:
        params = wf_in.getparams()
        n_frames = wf_in.getnframes()
        raw = wf_in.readframes(n_frames)

    # Stereo: samples intercalados [L, R, L, R, ...]
    n_samples = n_frames * 2
    samples = list(struct.unpack('<' + 'h' * n_samples, raw))

    # Poner en 0 todos los samples pares (canal izquierdo, índice 0, 2, 4, ...)
    for i in range(0, len(samples), 2):
        samples[i] = 0

    raw_mod = struct.pack('<' + 'h' * n_samples, *samples)

    with wave.open(archivo_salida, 'w') as wf_out:
        wf_out.setparams(params)
        wf_out.writeframes(raw_mod)

    print(f"Canal izquierdo limpiado: {archivo_salida}")

limpiar_canal_izquierdo("onda_volumen25.wav", "onda_canal_derecho.wav")
```

> En Audacity: el canal izquierdo aparecerá como línea plana; el derecho conserva la señal.

---

### Sub-tarea 7 — Verificación con Audacity

Para cada archivo generado:
1. `File → Import → Audio` → selecciona el `.wav`
2. Para ver el espectro: `Analyze → Plot Spectrum`
3. Para ver la forma de onda directamente en la pista
4. Para reproducir: barra de espaciado

**Qué deberías observar:**
- Sub-tarea 1/2/3: 7 segmentos de 1s cada uno, frecuencia creciente o decreciente visible
- Sub-tarea 4: onda compuesta con variación periódica (batimiento entre 250 y 500 Hz)
- Sub-tarea 5: misma forma de onda, amplitud visualmente más pequeña
- Sub-tarea 6: canal L plano, canal R con señal

---

### Checklist Ejercicio 4

- [ ] `escala_44100_mono.wav` — Do→Si, 44100, Mono, 7 seg total
- [ ] `escala_22050_stereo.wav` — Si→Do, 22050, Stereo, 7 seg total
- [ ] `escala_8000_mono.wav` — Do→Si, 8000, Mono, 7 seg total
- [ ] `onda_compuesta.wav` — 250+500 Hz, Stereo, 44100, 10 seg
- [ ] `onda_volumen25.wav` — volumen al 25%
- [ ] `onda_canal_derecho.wav` — canal izquierdo en cero
- [ ] Capturas de pantalla de Audacity para cada archivo

---

## Resumen de archivos a entregar

| Archivo              | Descripción                              |
|----------------------|------------------------------------------|
| `servidor.py`        | Servidor serial + control de teclas      |
| `cliente.py`         | Cliente serial con menú de comandos      |
| `ejercicio4.py`      | Generación de todos los archivos WAV     |
| `*.wav` (6 archivos) | Archivos de audio generados              |
| Capturas Audacity    | Evidencia visual de cada señal           |

---

## Dependencias del proyecto

```
numpy
matplotlib
pyserial
pywin32
```

Instalar todo: `pip install numpy matplotlib pyserial pywin32`
