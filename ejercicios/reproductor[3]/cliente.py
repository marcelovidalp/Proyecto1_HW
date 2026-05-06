import serial as ser, time

COMANDOS = ["PLAY", "STOP", "NEXT", "PREV", "VOL+", "VOL-", "MUTE", "PAUSE", "EXIT"]

def menu():
    print("\n==== REPRODUCTOR ====")
    for i, cmd in enumerate(COMANDOS):
        print(f"   {i}. {cmd}")
    print(10*"=")

def main():
    port = 'COM3' 
    baud = 9600

    print(f"[CLIENTE] Conectando a {port}")
    with ser.Serial(port, baud, timeout=2) as ser_client:
        time.sleep(1)
        while True:
            menu()

            try:
                opcion = int(input(f"SELECCIONA: "))
                if 0 <= opcion < len(COMANDOS):
                    cmd = COMANDOS[opcion]
                    ser_client.write(f"{cmd}\n".encode("utf-8"))
                    response = ser_client.readline().decode("utf-8").strip()
                    print(f"[RESPUESTA]{cmd}")
                    if cmd == "EXIT":
                        break
                else:
                    print("[ERROR] Opcion Invalida")
            except ValueError:
                print("Igresa un numero.")

if __name__ == "__main__":
    main()