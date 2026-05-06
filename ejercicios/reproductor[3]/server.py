'''User32.Keybd_event(.) para
simular la presión y liberación de las teclas
'''

import ctypes as ct, serial as ser, time

VK_CODES = {
    "PLAY":     0xB3,
    "STOP":     0xB2,
    "NEXT":     0xB0,
    "PREV":     0xB1,
    "VOL+":     0xAF,
    "VOL-":     0xAE,
    "MUTE":     0xAD,
    "PAUSE":    0xB3,  
}

KEYEVENTF_KEYUP = 0x0002
def press_key(vk_code):
    ct.windll.user32.keybd_event(vk_code, 0, 0, 0)  # key down
    time.sleep(0.05)
    ct.windll.user32.keybd_event(vk_code, 0, KEYEVENTF_KEYUP, 0)  # key up

def main():
    port = 'COM4' 
    baud = 9600

    print(f"[SERVER] Escuchando en {port}...")
    with ser.Serial(port,baud,timeout=1) as ser_port:
        while True:
            if ser_port.in_waiting > 0:
                line = ser_port.readline().decode('utf-8').strip().upper()
                print(f"[SERVER] Recibido: {line}")
                if line in VK_CODES:
                    press_key(VK_CODES[line])
                    print(f"[SERVER] Presionada tecla: {line}")
                elif line == "EXIT":
                    print("SERVER TERMINADO DESDE CLIENTE")
                    break
                else:
                    print(f"[SERVER] Comando desconocido: {line}")

if __name__ == "__main__":
    main()