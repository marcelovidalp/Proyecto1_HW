# Ejercicio 3 — Control de Reproductor de Audio vía Serial

## Arquitectura General

El sistema implementa una arquitectura **cliente-servidor** sobre un puerto serial virtual:

```
┌─────────────┐     Serial (VSPE)     ┌──────────────┐     Win32 API     ┌──────────────┐
│   CLIENTE   │ ──── COM3 → COM4 ───► │   SERVIDOR   │ ──────────────►  │ Winamp/AIMP  │
│  (envía     │                       │  (recibe cmd │                   │  (reproduce) │
│   comandos) │                       │  y presiona  │                   │              │
└─────────────┘                       │  teclas)     │                   └──────────────┘
                                      └──────────────┘
```

---

## VSPE — Virtual Serial Port Emulator

**VSPE** crea pares de puertos COM virtuales enlazados. Lo que se escribe en COM3 aparece en COM4 y viceversa, sin necesidad de hardware físico.

### Configuración típica en VSPE:
1. Abrir VSPE y crear un dispositivo tipo **"Pair"** (par).
2. Asignar los puertos: por ejemplo `COM3` ↔ `COM4`.
3. El proceso cliente abre `COM3` para escribir.
4. El proceso servidor abre `COM4` para leer.

### Parámetros de comunicación serial estándar:
```python
import serial
ser = serial.Serial(
    port='COM3',       # puerto virtual
    baudrate=9600,     # bits por segundo
    bytesize=8,        # bits de datos
    parity='N',        # sin paridad
    stopbits=1,        # 1 bit de parada
    timeout=1          # timeout de lectura (segundos)
)
```

---

## Win32 API — `keybd_event`

### ¿Qué es?

`User32.keybd_event` es una función de la API de Windows que simula la presión y liberación de teclas a nivel de sistema operativo, como si el usuario las presionara físicamente.

### Firma de la función:
```
VOID keybd_event(
    BYTE bVk,       // Virtual-Key code (código de tecla)
    BYTE bScan,     // hardware scan code (generalmente 0)
    DWORD dwFlags,  // 0 = presionar, KEYEVENTF_KEYUP(=2) = soltar
    ULONG_PTR dwExtraInfo  // información adicional (generalmente 0)
)
```

### Uso en Python con ctypes:
```python
import ctypes

user32 = ctypes.windll.user32

def presionar_tecla(vk_code):
    user32.keybd_event(vk_code, 0, 0, 0)       # KeyDown
    user32.keybd_event(vk_code, 0, 2, 0)       # KeyUp (KEYEVENTF_KEYUP = 2)
```

---

## Códigos de Teclas Virtuales (Virtual Key Codes)

### Teclas multimedia (funcionan globalmente en Windows):

| Acción | Constante | Valor Hex | Valor Dec |
|--------|-----------|-----------|-----------|
| Play/Pause | `VK_MEDIA_PLAY_PAUSE` | `0xB3` | 179 |
| Stop | `VK_MEDIA_STOP` | `0xB2` | 178 |
| Siguiente | `VK_MEDIA_NEXT_TRACK` | `0xB0` | 176 |
| Anterior | `VK_MEDIA_PREV_TRACK` | `0xB1` | 177 |
| Subir volumen | `VK_VOLUME_UP` | `0xAF` | 175 |
| Bajar volumen | `VK_VOLUME_DOWN` | `0xAE` | 174 |
| Silencio | `VK_VOLUME_MUTE` | `0xAD` | 173 |

### Teclas específicas de Winamp:

| Acción | Tecla |
|--------|-------|
| Play | `z` |
| Pause | `c` |
| Stop | `v` |
| Siguiente | `b` |
| Anterior | `x` |
| Abrir archivo | `l` |
| Aleatorio | `s` |
| Repetir | `r` |

---

## Protocolo de Comunicación

El protocolo define cómo el cliente codifica los comandos y cómo el servidor los interpreta.

### Ejemplo de protocolo simple (texto plano):

| Comando enviado | Acción en servidor |
|-----------------|-------------------|
| `"PLAY\n"` | Presiona VK_MEDIA_PLAY_PAUSE |
| `"STOP\n"` | Presiona VK_MEDIA_STOP |
| `"NEXT\n"` | Presiona VK_MEDIA_NEXT_TRACK |
| `"PREV\n"` | Presiona VK_MEDIA_PREV_TRACK |
| `"VOLU\n"` | Presiona VK_VOLUME_UP |
| `"VOLD\n"` | Presiona VK_VOLUME_DOWN |
| `"MUTE\n"` | Presiona VK_VOLUME_MUTE |
| `"PAUS\n"` | Presiona tecla `c` (Winamp) |

### Código esquemático del servidor:
```python
import serial, ctypes, time

user32 = ctypes.windll.user32
VK = {
    'PLAY': 0xB3, 'STOP': 0xB2,
    'NEXT': 0xB0, 'PREV': 0xB1,
    'VOLU': 0xAF, 'VOLD': 0xAE,
    'MUTE': 0xAD,
}

def presionar(vk):
    user32.keybd_event(vk, 0, 0, 0)
    user32.keybd_event(vk, 0, 2, 0)

ser = serial.Serial('COM4', 9600, timeout=1)
while True:
    linea = ser.readline().decode().strip()
    if linea in VK:
        presionar(VK[linea])
        print(f"Ejecutado: {linea}")
```

### Código esquemático del cliente:
```python
import serial

ser = serial.Serial('COM3', 9600, timeout=1)
while True:
    cmd = input("Comando > ").upper().strip()
    ser.write((cmd + '\n').encode())
```

---

## Flujo Completo del Ejercicio

```
1. Configurar VSPE: crear par COM3 ↔ COM4
         |
2. Lanzar servidor (COM4):
   └── Queda en bucle esperando datos del puerto serial
         |
3. Lanzar cliente (COM3):
   └── Muestra menú / interfaz de comandos al usuario
         |
4. Usuario ingresa un comando (ej: "NEXT")
         |
5. Cliente escribe "NEXT\n" en COM3
         |
6. VSPE transmite la cadena a COM4
         |
7. Servidor lee "NEXT\n" de COM4
         |
8. Servidor llama keybd_event(0xB0, 0, 0, 0) y keybd_event(0xB0, 0, 2, 0)
         |
9. Windows envía el evento de teclado a la ventana activa
         |
10. Winamp/AIMP recibe la tecla y avanza a la siguiente pista
```

---

## Consideraciones de Implementación

- **Ventana activa:** `keybd_event` envía la tecla a la ventana activa. Las teclas multimedia (`0xB0`–`0xB3`) funcionan globalmente sin importar qué ventana esté activa. Las teclas de letras (`z`, `c`, `v`, etc.) sólo funcionan si Winamp tiene el foco.
- **`FindWindow` + `PostMessage`:** alternativa más robusta que no depende del foco:
  ```python
  hwnd = user32.FindWindowW("Winamp v1.x", None)
  user32.PostMessageW(hwnd, 0x0111, 40045, 0)  # WM_COMMAND, ID=40045 (Play)
  ```
- **Baudrate:** ambos extremos del serial deben usar el mismo baudrate. 9600 es estándar y suficiente para comandos de texto.
- **Archivos MP3/MP4:** el enunciado pide al menos 10 archivos. Se deben tener cargados en la playlist de Winamp/AIMP antes de ejecutar el sistema.

---

## Preguntas de Simulación

**1. ¿Por qué se necesita VSPE si cliente y servidor están en la misma máquina?**  
Porque la comunicación serial normalmente requiere un cable físico entre dos puertos COM. VSPE emula ese cable virtualmente, creando un par de puertos donde lo escrito en uno aparece en el otro. Sin VSPE habría que usar dos computadoras o un cable USB-serial.

**2. ¿Qué diferencia hay entre `keybd_event` y `SendInput`?**  
`SendInput` es la función más moderna y recomendada (reemplaza a `keybd_event` desde Windows XP). `keybd_event` puede ser bloqueada por ciertos programas. `SendInput` es más confiable y usa una estructura `INPUT` que permite inyectar eventos de teclado, mouse y hardware en una sola llamada.

**3. ¿Qué hace exactamente el flag `KEYEVENTF_KEYUP = 2` en `keybd_event`?**  
Indica que el evento es la *liberación* de una tecla (key up). Sin este flag (valor 0), el evento es la *presión* (key down). Siempre se debe enviar el par down + up para simular una pulsación completa, de lo contrario la tecla queda "presionada" indefinidamente.

**4. ¿Por qué el segundo parámetro de `keybd_event` (bScan) suele ser 0?**  
`bScan` es el código de scan de hardware del teclado (código físico de la tecla). Al usar `keybd_event` para simulación de software, se puede pasar 0 porque Windows puede derivar el scan code del virtual key code. Sólo importa cuando se necesita precisión de hardware específico.

**5. ¿Qué protocolo de comunicación implementaste y por qué ese diseño?**  
Se implementó un protocolo de texto plano con comandos de 4 letras terminados en `\n`. La ventaja es la legibilidad y simplicidad de depuración. Una alternativa sería un protocolo binario (1 byte por comando), que sería más eficiente pero menos legible.

**6. ¿Qué pasaría si el servidor recibe un comando desconocido?**  
Depende de la implementación. Lo correcto es ignorarlo o responder con un mensaje de error por el mismo canal serial. Sin validación, podría producir comportamiento indefinido o excepciones.

**7. ¿Cómo harías para que el sistema funcione aunque Winamp no tenga el foco de la ventana?**  
Usando `FindWindow` para obtener el handle (HWND) de la ventana de Winamp, y luego `PostMessage` o `SendMessage` con los códigos de comando de Winamp (WM_COMMAND). Esto envía el mensaje directamente a la cola de mensajes del proceso de Winamp independientemente del foco.
