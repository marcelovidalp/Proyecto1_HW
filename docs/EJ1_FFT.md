# Ejercicio 1 — Transformada Rápida de Fourier (FFT)

## Concepto Central: ¿Qué es la FFT?

La **Transformada de Fourier** convierte una señal del **dominio del tiempo** al **dominio de la frecuencia**. En otras palabras, toma una señal compleja (mezcla de ondas) y determina *qué frecuencias* la componen y con qué amplitud aparece cada una.

La **FFT (Fast Fourier Transform)** es un algoritmo eficiente para calcular la DFT (Transformada Discreta de Fourier). Su complejidad es **O(n log n)** en lugar de O(n²), lo que la hace práctica para señales de audio.

---

## Teorema de Nyquist-Shannon

> Para reconstruir una señal sin pérdida de información, la **tasa de muestreo debe ser al menos el doble de la frecuencia máxima** presente en la señal.

```
f_muestreo >= 2 * f_max
```

En el ejercicio: `S_RATE = 44100` Hz puede representar frecuencias de hasta **22050 Hz**, que cubre todo el rango audible humano (20 Hz – 20 000 Hz).

---

## Variables del Script

| Variable | Valor | Significado |
|----------|-------|-------------|
| `FREQ_0` | 1000 | Frecuencia principal (Hz) |
| `FREQ_1` | 50   | Frecuencia de ruido (Hz) |
| `SAMPLE` | 44100 | Número de muestras generadas |
| `S_RATE` | 44100.0 | Tasa de muestreo (muestras/segundo) |

---

## Funciones de NumPy Utilizadas

### `numpy.sin(x)`
Calcula el seno de cada elemento. En el script se usa dentro de una list comprehension:
```python
s_1 = [np.sin(2*np.pi * FREQ_0 * i/S_RATE) for i in range(SAMPLE)]
```
Esto genera **SAMPLE** muestras de una onda sinusoidal de 1000 Hz discretizada a 44100 muestras/segundo.

### `numpy.array(lista)`
Convierte una lista Python en un array NumPy, habilitando operaciones vectorizadas:
```python
w_1 = np.array(s_1)
w_2 = np.array(s_2)
w12 = w_1 + w_2   # suma elemento a elemento (no concatena)
```

### `numpy.fft.fft(señal)`
Calcula la FFT. Devuelve un array de **números complejos** donde:
- El **módulo** de cada número es la amplitud de esa frecuencia.
- El **ángulo** (fase) indica el desfase de esa componente.

```python
fft_result = np.fft.fft(w12)
magnitudes  = np.abs(fft_result)   # amplitudes reales
```

El resultado tiene `N` elementos, pero sólo los primeros `N/2` son útiles (la segunda mitad es el espejo conjugado, por ser la señal real).

### `numpy.fft.fftfreq(n, d)`
Genera el eje de frecuencias correspondiente a la FFT:
```python
freqs = np.fft.fftfreq(SAMPLE, d=1/S_RATE)
# d = 1/S_RATE = período entre muestras (segundos)
```
Devuelve frecuencias en Hz asociadas a cada bin de la FFT.

---

## Flujo Completo del Ejercicio

```
1. Definir constantes (FREQ_0=1000, FREQ_1=50, SAMPLE=44100, S_RATE=44100)
         |
2. Generar señal principal s_1 → 44100 muestras de sin(2π·1000·i/44100)
         |
3. Generar señal de ruido s_2  → 44100 muestras de sin(2π·50·i/44100)
         |
4. Convertir ambas a arrays NumPy (w_1, w_2)
         |
5. Sumar: w12 = w_1 + w_2  → señal compuesta (mezcla de ambas frecuencias)
         |
6. Graficar con matplotlib:
   ├── Gráfica 1: Onda Original      (primeras ~500 muestras de w_1)
   ├── Gráfica 2: Onda Ruido         (w_2 completa)
   ├── Gráfica 3: Onda Original+Ruido (w12 completa)
   └── Gráfica 4: FFT de w12         (magnitudes vs frecuencia)
```

---

## Interpretación de las Gráficas

| Gráfica | Lo que se ve | Por qué |
|---------|-------------|---------|
| Onda Original | Ciclos rápidos (1000 Hz) | Alta frecuencia → ciclos cortos |
| Onda Ruido | Ciclos lentos (50 Hz) | Baja frecuencia → ciclos largos |
| Onda Compuesta | Ondulación rápida dentro de una envolvente lenta | Superposición de ambas |
| FFT | Dos picos verticales, uno en ~50 Hz y otro en ~1000 Hz | La FFT "separa" las componentes frecuenciales |

Los **picos en la FFT** corresponden exactamente a FREQ_0 y FREQ_1. Si no hubiera ruido, sólo existiría un pico.

---

## Propiedades Importantes de la FFT

- **Linealidad:** FFT(a·x + b·y) = a·FFT(x) + b·FFT(y)  
- **Simetría:** para señales reales, la segunda mitad del espectro es espejo de la primera.  
- **Resolución frecuencial:** Δf = S_RATE / SAMPLE = 44100/44100 = **1 Hz por bin**.

---

## Preguntas de Simulación

**1. ¿Qué diferencia hay entre la DFT y la FFT?**  
La DFT calcula la transformada discreta de Fourier de forma directa con complejidad O(n²). La FFT es un algoritmo que calcula exactamente el mismo resultado pero en O(n log n) aprovechando la simetría de las raíces de la unidad. Para n=44100, la diferencia en operaciones es enorme.

**2. ¿Por qué se usa `np.abs()` sobre el resultado de `np.fft.fft()`?**  
Porque `fft()` devuelve números complejos (parte real + imaginaria). El módulo `abs()` calcula la magnitud √(real² + imag²), que representa la amplitud de cada frecuencia. Sin eso, no se puede graficar directamente.

**3. ¿Qué ocurre si la frecuencia de una señal supera la mitad de la tasa de muestreo?**  
Se produce **aliasing**: la frecuencia aparece reflejada como una frecuencia más baja en el espectro. Por ejemplo, con S_RATE=44100, una señal de 23000 Hz aparecería como 44100-23000 = 21100 Hz.

**4. ¿Por qué el eje X de la FFT llega sólo hasta S_RATE/2 = 22050 Hz y no hasta 44100?**  
Por el teorema de Nyquist. La segunda mitad del espectro (de N/2 a N) es el conjugado simétrico de la primera y no aporta información nueva para señales reales.

**5. ¿Qué representa la amplitud de un pico en el espectro FFT?**  
Representa la "energía" o "peso" de esa frecuencia dentro de la señal. Un pico alto significa que esa frecuencia contribuye significativamente a la forma de onda resultante.

**6. ¿Cómo se interpretaría una FFT con muchos picos distribuidos a lo largo del espectro?**  
Indicaría una señal con muchas componentes frecuenciales, como ruido blanco. Una señal sinusoidal pura produce exactamente un pico (y su simétrico).

**7. Si duplicas SAMPLE pero mantienes S_RATE, ¿qué cambia en la FFT?**  
Mejora la resolución frecuencial (Δf = S_RATE/SAMPLE se reduce), por lo que los picos en el espectro son más estrechos y precisos. No cambia el rango de frecuencias representable.
