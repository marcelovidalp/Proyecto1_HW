# Ejercicio 4 — Generación de Archivos WAV con Python

## Conceptos Fundamentales de Audio Digital

### PCM — Pulse Code Modulation

El audio digital almacena sonido como una secuencia de **muestras numéricas**. Cada muestra es el valor instantáneo de la onda sonora en ese momento del tiempo.

```
Señal analógica continua:
  ∿∿∿∿∿∿∿∿

Muestreo (44100 veces por segundo):
  |  |  |  |  |  |  |  |  |
  ↓  ↓  ↓  ↓  ↓  ↓  ↓  ↓  ↓
 [0.7][0.9][0.5][-0.2][-0.8]...  → valores normalizados [-1, 1]
                                  → multiplicados × 32767 → enteros 16-bit
```

### Parámetros Clave de un Archivo WAV

| Parámetro | Descripción | Valores usados |
|-----------|-------------|----------------|
| **Sample rate** | Muestras por segundo (Hz) | 44100, 22050, 8000 |
| **Sample width** | Bytes por muestra | 2 (16 bits) |
| **Channels** | Mono=1, Stereo=2 | 1 o 2 |
| **Amplitude** | Valor máximo de la muestra | 32767 (máximo de int16) |

### ¿Por qué 32767 y no 32768?

El tipo `signed short` de 16 bits tiene rango `[-32768, 32767]`. Se usa 32767 (positivo máximo) para evitar overflow en el valor negativo mínimo al operar con senos que van de -1 a 1.

---

## Módulo `wave` de Python

El módulo `wave` de la biblioteca estándar permite leer y escribir archivos WAV en formato PCM sin dependencias externas.

### Escritura — métodos principales

```python
import wave

with wave.open('salida.wav', 'w') as wf:
    wf.setnchannels(1)     # 1=mono, 2=stereo
    wf.setsampwidth(2)     # 2 bytes = 16 bits por muestra
    wf.setframerate(44100) # tasa de muestreo en Hz
    wf.writeframes(data)   # bytes con las muestras empaquetadas
```

### Lectura — métodos principales

```python
with wave.open('entrada.wav', 'r') as wf:
    params   = wf.getparams()          # namedtuple con todos los parámetros
    nframes  = wf.getnframes()         # número total de frames
    nch      = wf.getnchannels()       # canales
    raw      = wf.readframes(nframes)  # bytes crudos de todas las muestras

# Para reutilizar los mismos parámetros al escribir:
with wave.open('copia.wav', 'w') as wf_out:
    wf_out.setparams(params)
    wf_out.writeframes(datos_modificados)
```

> **Frame vs Sample:** Un *frame* es un conjunto de muestras sincrónicas para todos los canales. En stereo, 1 frame = 2 samples (L + R). `getnframes()` devuelve el número de frames, no de bytes.

---

## Módulo `struct` de Python

`struct` convierte entre valores Python y representaciones binarias (bytes), esencial para empaquetar muestras de audio en el formato que espera el archivo WAV.

### `struct.pack(fmt, *values)` → `bytes`

Convierte valores Python a bytes según el formato indicado.

```python
import struct

struct.pack('<h', 16000)   # → b'\x80>' (2 bytes, little-endian, signed short)
struct.pack('<hh', 16000, -16000)   # → 4 bytes (muestra stereo: L + R)
```

### `struct.unpack(fmt, buffer)` → `tuple`

Operación inversa: convierte bytes a valores Python.

```python
raw = b'\x80>'
val = struct.unpack('<h', raw)   # → (16000,)
val[0]   # → 16000
```

### Formato de cadena para audio WAV 16-bit

| Carácter | Significado |
|----------|-------------|
| `<` | Little-endian (bytes menos significativo primero — estándar WAV) |
| `h` | `signed short` (entero con signo, 2 bytes, rango -32768..32767) |
| `<h` | Una muestra mono de 16 bits |
| `<hh` | Una muestra stereo (canal L + canal R) |
| `<Nh` | N muestras mono (N = número de samples) |

### Desempaquetar todo un archivo de una vez:

```python
n   = len(raw) // 2          # cada muestra ocupa 2 bytes
fmt = f'<{n}h'               # formato para n shorts
samples = struct.unpack(fmt, raw)   # tupla con n enteros
```

---

## Función `genNota` — Generación de Señal Sinusoidal

```python
def genNota(freq, length, rate):
    n = int(rate * length)
    return [math.sin(2 * math.pi * freq / rate * i) for i in range(n)]
```

### Análisis de la fórmula

```
math.sin(2 * π * freq / rate * i)
          └──────────────────────┘
             ángulo en radianes para la muestra i
```

- `2π` → un ciclo completo en radianes
- `freq / rate` → fracción de ciclo que avanza por muestra
- `* i` → posición en el tiempo (muestra número i)

Para `freq=440 Hz`, `rate=44100`: cada muestra avanza `440/44100 ≈ 0.00997` ciclos. En 44100 muestras se completan exactamente 440 ciclos → 440 Hz.

El resultado está normalizado en `[-1.0, 1.0]`.

---

## Items del Ejercicio

### Items 1, 2 y 3 — Escalas musicales

Las notas de la escala musical en la octava 4 (Do central):

| Nota | Frecuencia (Hz) |
|------|----------------|
| Do   | 261.63 |
| Re   | 293.66 |
| Mi   | 329.63 |
| Fa   | 349.23 |
| Sol  | 392.00 |
| La   | 440.00 |
| Si   | 493.88 |

#### Efecto de la tasa de muestreo en la calidad

| Rate | Calidad equivalente | Frecuencia máxima representable |
|------|--------------------|---------------------------------|
| 44100 Hz | CD estándar | 22050 Hz (rango audible completo) |
| 22050 Hz | Calidad FM | 11025 Hz |
| 8000 Hz | Calidad telefónica | 4000 Hz (voz humana básica) |

A 8000 Hz las notas Si (493.88 Hz) y Sol (392 Hz) siguen siendo representables, pero el timbre sufre distorsión al perder armónicos superiores.

#### Diferencia mono vs stereo en los bytes

```
Mono   (1ch): | L0 | L1 | L2 | L3 | ...  → 2 bytes por frame
Stereo (2ch): | L0 R0 | L1 R1 | L2 R2 |  → 4 bytes por frame
                └─┬─┘
              interleaved: L y R alternados
```

En `wWavStereo`, ambos canales reciben la misma señal (`int(s*width), int(s*width)`), produciendo stereo sin diferencia entre canales (igual L y R).

---

### Item 4 — Onda Compuesta

```python
y = 8000*sin(2π·500/RATE·i) + 8000*sin(2π·250/RATE·i)
```

- Amplitud: ±8000 en cada componente → suma máxima = ±16000 (dentro del rango de int16)
- La suma de dos sinusoides produce una onda que **no es sinusoidal pura**: tiene la forma de batido (beating) entre 250 Hz y 500 Hz.
- Ambos canales (L y R) reciben la misma señal.
- Duración: 10 segundos → `44100 × 10 = 441000 frames`

El clamp `max(-32767, min(32767, val))` previene overflow si la suma superara el rango.

---

### Item 5 — Reducir Volumen 75%

```python
# factor=0.25 → conserva el 25%, reduce el 75%
samples_out = [int(s * 0.25) for s in samples_in]
```

**¿Por qué multiplicar por 0.25 baja el volumen en un 75%?**  
La amplitud de una onda determina su volumen percibido. Multiplicar cada muestra por 0.25 reduce la amplitud al 25% del original. En decibelios:

```
ΔdB = 20 · log10(0.25) ≈ -12 dB
```

Una reducción de ~12 dB es perceptiblemente "mucho más silencioso" pero no inaudible.

---

### Item 6 — Limpiar Canal Izquierdo

```python
# En stereo interleaved: índice par = L, índice impar = R
for i in range(0, len(samples), 2):
    samples[i] = 0   # canal izquierdo → silencio
```

**Layout en memoria del buffer stereo:**

```
Índice: [0]  [1]  [2]  [3]  [4]  [5]  [6]  [7] ...
Canal:   L0   R0   L1   R1   L2   R2   L3   R3 ...

Después de limpiar L:
         [0]  [1]  [0]  [1]  [0]  [1]  [0]  [1] ...
          0   R0    0   R1    0   R2    0   R3 ...
```

El resultado es audio que solo se escucha por el **altavoz derecho**. En Audacity se verá el canal izquierdo como una línea plana y el derecho con la onda normal.

---

## Flujo Completo del Ejercicio 4

```
main.py
  │
  ├── Item 1: wWavMono('ej4_1...wav', [261.63, 293.66, ..., 493.88], 1, 44100)
  │     └── 7 notas × 44100 muestras × 2 bytes = 617.400 bytes
  │
  ├── Item 2: wWavStereo('ej4_2...wav', [493.88, ..., 261.63], 1, 22050)
  │     └── 7 notas × 22050 muestras × 4 bytes (stereo) = 617.400 bytes
  │
  ├── Item 3: wWavMono('ej4_3...wav', [261.63, ..., 493.88], 1, 8000)
  │     └── 7 notas × 8000 muestras × 2 bytes = 112.000 bytes
  │
  ├── Item 4: genOndaStereo('ej4_4...wav', 44100, 10)
  │     └── 441.000 frames × 4 bytes = 1.764.000 bytes (~1.7 MB)
  │
  ├── Item 5: reducirVolumen(ej4_4, 'ej4_5...wav', factor=0.25)
  │     └── Lee ej4_4, multiplica cada short × 0.25, escribe con mismos params
  │
  └── Item 6: limpiarCanalIzq(ej4_5, 'ej4_6...wav')
        └── Lee ej4_5, pone a 0 índices pares, escribe con mismos params
```

---

## Preguntas de Simulación

**1. ¿Qué significa `'<h'` en `struct.pack`?**  
`<` indica codificación little-endian (el byte menos significativo va primero, estándar en x86 y en el formato WAV). `h` es el tipo `signed short`: un entero con signo de 2 bytes con rango -32768 a 32767. `struct.pack('<h', 16000)` produce exactamente los 2 bytes que el módulo `wave` espera para una muestra PCM de 16 bits.

**2. ¿Por qué en `wWavStereo` se usa `struct.pack('<hh', val, val)` en lugar de `'<h'`?**  
Porque en un archivo stereo cada frame contiene DOS muestras: canal izquierdo (L) y canal derecho (R), intercaladas. `'<hh'` empaqueta dos `signed short` consecutivos = 4 bytes por frame. Si se usara `'<h'` el archivo resultante tendría la mitad de los frames esperados y el audio se reproduciría con artifacts.

**3. ¿Qué pasaría si se usa `setsampwidth(1)` en lugar de `setsampwidth(2)`?**  
Cambiaría a audio de 8 bits por muestra (rango 0–255, unsigned). Las muestras generadas con `struct.pack('<h', ...)` seguirían siendo de 16 bits, haciendo que el header WAV y los datos sean inconsistentes. El reproductor leería el archivo de forma incorrecta: el audio sonaría distorsionado o como ruido.

**4. ¿Cuántos bytes ocupa 1 segundo de audio en el Item 1 (44100 Hz, mono, 16-bit)?**  
`44100 muestras/s × 1 canal × 2 bytes/muestra = 88.200 bytes/segundo`. Para las 7 notas de la escala: `7 × 88.200 = 617.400 bytes`, más el header WAV de 44 bytes.

**5. ¿Por qué `genNota` retorna valores en [-1.0, 1.0] y no directamente enteros?**  
Separar la generación de la señal de su cuantización permite reutilizar `genNota` con distintos valores de `width`. Si se genera normalizada y se multiplica por `width` al escribir, se puede cambiar la amplitud sin tocar la función. También facilita operaciones como suma o mezcla de señales antes de cuantizar.

**6. En el Item 4, ¿por qué se hace `max(-32767, min(32767, val))`?**  
La onda compuesta suma dos componentes de amplitud 8000 cada una. En el peor caso (cuando ambos senos valen 1 simultáneamente) el resultado es 16000, que está dentro del rango. Sin embargo, el clamp es una salvaguarda para evitar overflow por errores de redondeo o cambios futuros en la amplitud. Sin él, un valor como 32768 haría que `struct.pack('<h', ...)` lanzara una excepción `struct.error`.

**7. ¿Qué diferencia auditiva hay entre los archivos del Item 1 (44100 Hz) y Item 3 (8000 Hz)?**  
Ambos contienen las mismas notas, pero la versión a 8000 Hz tiene menos armónicos altos porque la frecuencia máxima representable es 4000 Hz. Los armónicos de las notas por encima de 4000 Hz se pierden, haciendo el sonido más "opaco" o "telefónico". Las frecuencias fundamentales de la escala (261–493 Hz) están presentes en ambos, pero el timbre es diferente.

**8. ¿Por qué en el Item 6 se ponen a cero los índices PARES y no los impares?**  
En el formato PCM stereo interleaved, el canal izquierdo (L) siempre ocupa la primera muestra de cada frame, es decir, los índices 0, 2, 4, 6... (pares). El canal derecho (R) ocupa los índices 1, 3, 5, 7... (impares). Poner a cero los pares silencia el canal izquierdo, dejando sólo el derecho audible.

**9. ¿Qué es un frame en el contexto del módulo `wave`?**  
Un frame es la unidad mínima de tiempo en un archivo WAV: contiene una muestra de cada canal. En mono, 1 frame = 1 muestra = 2 bytes. En stereo, 1 frame = 2 muestras (L + R) = 4 bytes. `setframerate(44100)` significa 44100 frames por segundo, independientemente de si es mono o stereo.

**10. ¿Cómo verificarías en Audacity que el canal izquierdo fue correctamente silenciado?**  
Al abrir el archivo en Audacity aparecen dos pistas (L y R). La pista L debe mostrar una línea plana en amplitud 0, y la pista R debe mostrar la onda normal con amplitud reducida (del Item 5). Al reproducir, el sonido sólo sale por el altavoz derecho. También se puede usar `Analyze > Plot Spectrum` para confirmar la energía en cada canal.
