# Ejercicio 2 — Filtro Complementario

## Concepto Central: ¿Qué es el Filtro Complementario?

El **Filtro Complementario** es un filtro digital de primer orden de tipo **IIR (Infinite Impulse Response)**. Actúa como un **filtro pasa-bajo**: atenúa las frecuencias altas (ruido rápido) y deja pasar las frecuencias bajas (tendencia o componente lenta).

Su ecuación de recurrencia es:

```
aF[0] = aV[0]
aF[i] = nA * aV[i] + (1.0 - nA) * aF[i-1]
```

Donde:
- `aV[i]` → muestra actual de la señal de entrada (cruda)
- `aF[i]` → muestra actual de la señal filtrada (salida)
- `aF[i-1]` → muestra anterior de la salida (memoria del filtro)
- `nA` (alpha, α) → parámetro de suavizado: valor entre 0 y 1

---

## El Parámetro Alpha (nA)

| Valor de nA | Comportamiento |
|-------------|---------------|
| nA → 1.0 | El filtro casi no suaviza: `aF[i] ≈ aV[i]` (sigue a la señal cruda) |
| nA → 0.0 | Suavizado máximo: la salida cambia muy lentamente (alta inercia) |
| nA = 0.5 | Balance entre señal actual e historial |

**Analogía física:** Es como el comportamiento de un termómetro. Con alpha bajo, reacciona lento a cambios de temperatura (suaviza mucho). Con alpha alto, reacciona casi instantáneamente.

La relación con la frecuencia de corte es:
```
f_corte ≈ nA * S_RATE / (2π)
```

---

## Variables y Señales del Script

### Ondas base (`aW`)

```python
FREQ_0 = 9000  # Hz
FREQ_1 = 5000  # Hz
FREQ_2 = 100   # Hz
SAMPLE = 20000
S_RATE = 20000.0

aW = [
    [2*sin(2π·9000·i/20000)  para i en 0..19999],   # aW[0]: amplitud 2, alta freq
    [3*sin(2π·5000·i/20000)  para i en 0..19999],   # aW[1]: amplitud 3, media freq
    [9*sin(2π·100·i/20000)   para i en 0..19999],   # aW[2]: amplitud 9, baja freq
]
```

### Señales compuestas (`aS`)

```python
aS[0] = np.array(aW[0]) + np.array(aW[1])   # suma: 9000Hz + 5000Hz
aS[1] = np.array(aW[0]) + np.array(aW[2])   # suma: 9000Hz + 100Hz
aS[2] = np.array(aW[1]) * np.array(aW[2])   # producto: 5000Hz × 100Hz
```

> **Nota sobre aS[2]:** La multiplicación de dos sinusoides produce una señal **modulada en amplitud (AM)**. Matemáticamente:  
> `sin(A) · sin(B) = 0.5·[cos(A−B) − cos(A+B)]`  
> Esto genera componentes en `5000−100=4900 Hz` y `5000+100=5100 Hz`.

---

## La Función `Filter_Comp`

```python
def Filter_Comp(aV, nA):
    aF[0] = aV[0]                              # condición inicial
    for i in range(1, nMAX):
        aF[i] = nA * aV[i] + (1.0 - nA) * aF[i-1]
    return aF
```

### ¿Por qué es IIR?

Porque la salida `aF[i]` depende de salidas **anteriores** (`aF[i-1]`), creando una "respuesta infinita" al impulso teóricamente. En la práctica la respuesta decae exponencialmente.

### ¿Por qué se llama "Complementario"?

Los pesos `nA` y `(1-nA)` siempre suman 1 (son complementarios). Esto garantiza que el filtro no amplifica la señal: si la entrada es constante, la salida converge al mismo valor.

---

## Flujo Completo del Ejercicio

```
1. Definir constantes: FREQ_0=9000, FREQ_1=5000, FREQ_2=100, SAMPLE=nMAX=20000
         |
2. Generar 3 ondas base (aW[0], aW[1], aW[2]) con distintas amplitudes y frecuencias
         |
3. Crear 3 señales compuestas (aS):
   ├── aS[0] = aW[0] + aW[1]   (suma de alta y media frecuencia)
   ├── aS[1] = aW[0] + aW[2]   (suma de alta y baja frecuencia)
   └── aS[2] = aW[1] * aW[2]   (modulación AM)
         |
4. Aplicar Filter_Comp a cada aS con un valor de nA
         |
5. Graficar en matplotlib:
   ├── Signal 1: aS[0] (azul) + filtrada (rojo)  → se ven 200 muestras
   ├── Signal 2: aS[1] (azul) + filtrada (rojo)
   └── Signal 3: aS[2] (azul) + filtrada (rojo)
```

---

## Interpretación de las Gráficas

| Señal | Composición | Efecto del filtro |
|-------|------------|-------------------|
| Signal 1 | 9000 Hz + 5000 Hz (ambas altas) | El filtro atenúa ambas → señal filtrada muy plana, cerca de 0 |
| Signal 2 | 9000 Hz + 100 Hz | El filtro elimina 9000 Hz y deja la envolvente de 100 Hz |
| Signal 3 | AM de 5000×100 Hz | El filtro suaviza la modulación, mostrando la envolvente lenta |

- **Curva azul:** señal cruda (aS) — variaciones rápidas visibles
- **Curva roja:** señal filtrada (Filter_Comp) — más suave, sigue la tendencia lenta

---

## Diferencia entre Filtro Pasa-Bajo y Pasa-Alto

| Filtro | Deja pasar | Atenúa |
|--------|-----------|--------|
| Pasa-bajo (este filtro) | Frecuencias bajas (variación lenta) | Frecuencias altas (ruido) |
| Pasa-alto | Frecuencias altas | Frecuencias bajas (DC, tendencias) |
| Pasa-banda | Rango específico | Fuera del rango |

---

## Preguntas de Simulación

**1. ¿Por qué el Filtro Complementario es considerado un filtro IIR?**  
Porque la salida actual depende de salidas anteriores (retroalimentación). La ecuación `aF[i] = nA·aV[i] + (1-nA)·aF[i-1]` tiene un polo en z=(1-nA), lo que significa que la respuesta al impulso es teóricamente infinita (decae exponencialmente).

**2. ¿Qué pasaría si nA = 0?**  
La salida sería `aF[i] = aF[i-1]` para todo i, es decir, el filtro "congela" su primer valor y nunca cambia. La señal filtrada sería una constante igual a `aV[0]`.

**3. ¿Qué pasaría si nA = 1?**  
`aF[i] = 1·aV[i] + 0·aF[i-1] = aV[i]`. El filtro no hace nada: la salida es idéntica a la entrada. No hay suavizado.

**4. ¿Por qué la Signal 1 (9000 Hz + 5000 Hz) aparece tan plana después del filtro?**  
Porque ambas componentes son de alta frecuencia relativa a nMAX. El filtro complementario con un alpha bajo atenúa fuertemente ambas, haciendo que la señal filtrada converja a un valor casi nulo.

**5. ¿Qué efecto matemático tiene multiplicar dos sinusoides como en aS[2]?**  
Por identidad trigonométrica: `sin(A)·sin(B) = ½[cos(A-B) - cos(A+B)]`. La multiplicación de aW[1] (5000 Hz) × aW[2] (100 Hz) genera dos nuevas frecuencias: 4900 Hz y 5100 Hz. Es modulación AM (Amplitud Modulada).

**6. ¿Cuál es la condición inicial del filtro y por qué importa?**  
`aF[0] = aV[0]`. Es importante porque si se inicializara en 0, habría un transitorio inicial donde el filtro "arranca" desde 0 hacia la señal real. Inicializar con el primer valor real evita ese artefacto.

**7. ¿Dónde se aplica el Filtro Complementario en sistemas reales de hardware?**  
Se usa ampliamente en sensores inerciales (IMU): combina datos de acelerómetro (confiable a largo plazo pero ruidoso) con giroscopio (preciso a corto plazo pero que deriva). El filtro fusiona ambas fuentes atenuando sus respectivos defectos.
