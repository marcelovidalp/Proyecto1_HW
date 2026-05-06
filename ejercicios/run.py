import os, sys, subprocess

BASE         = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE)

EJERCICIOS = [
    {
        "num":    1,
        "titulo": "FFT de señales",
        "desc":   "Genera dos ondas sinusoidales, las suma y muestra su espectro de frecuencias con FFT.",
        "cmd":    [sys.executable, os.path.join(BASE, "freqFFT.py")],
        "aviso":  None,
    },
    {
        "num":    2,
        "titulo": "Filtro Complementario",
        "desc":   "Aplica un filtro paso-bajo a señales compuestas y grafica la señal original vs filtrada.",
        "cmd":    [sys.executable, os.path.join(BASE, "filtroComplementario.py")],
        "aviso":  None,
    },
    {
        "num":    3,
        "titulo": "Control Reproductor (Serial)",
        "desc":   "Envía comandos (PLAY, STOP, NEXT…) a un servidor vía puerto serial COM3.",
        "cmd":    [sys.executable, os.path.join(BASE, "reproductor[3]", "cliente.py")],
        "aviso":  None,
    },
    {
        "num":    4,
        "titulo": "Generación de archivos WAV",
        "desc":   "Genera 6 archivos .wav: escalas Do-Si con distintas tasas, onda compuesta, volumen reducido y canal limpio.",
        "cmd":    [sys.executable, os.path.join(BASE, "ej4", "main.py")],
        "aviso":  None,
    },
]

SEP   = "─" * 48
BOLD  = "\033[1m"
CYAN  = "\033[96m"
GREEN = "\033[92m"
YELL  = "\033[93m"
RED   = "\033[91m"
RST   = "\033[0m"


def header():
    print(f"\n{BOLD}{CYAN}{'═'*48}")
    print(f"   PROYECTO 1 — INFO1157")
    print(f"{'═'*48}{RST}")


def mostrar_menu():
    header()
    for ej in EJERCICIOS:
        aviso = f"  {YELL}[!] {ej['aviso']}{RST}" if ej["aviso"] else ""
        print(f"  {BOLD}[{ej['num']}]{RST} EJ{ej['num']} — {ej['titulo']}{aviso}")
    print(f"  {BOLD}[a]{RST} Ejecutar todos en orden")
    print(f"  {BOLD}[q]{RST} Salir")
    print(SEP)


def ejecutar(ej):
    print(f"\n{GREEN}{SEP}")
    print(f"  EJ{ej['num']} — {ej['titulo']}")
    print(f"  {ej['desc']}")
    if ej["aviso"]:
        print(f"  {YELL}[!] {ej['aviso']}{RST}{GREEN}")
    print(f"{SEP}{RST}")

    env = os.environ.copy()
    env["PYTHONPATH"] = PROJECT_ROOT + os.pathsep + env.get("PYTHONPATH", "")

    try:
        subprocess.run(ej["cmd"], cwd=PROJECT_ROOT, env=env, check=True)
        print(f"{GREEN}  [OK] EJ{ej['num']} finalizado.{RST}")
    except subprocess.CalledProcessError as e:
        print(f"{RED}  [ERROR] EJ{ej['num']} terminó con código {e.returncode}.{RST}")
    except FileNotFoundError:
        print(f"{RED}  [ERROR] Script no encontrado: {ej['cmd']}{RST}")
    except KeyboardInterrupt:
        print(f"\n{YELL}  [!] EJ{ej['num']} interrumpido por el usuario.{RST}")


def main():
    while True:
        mostrar_menu()
        opcion = input("  Selecciona: ").strip().lower()

        if opcion == "q":
            print("Saliendo.\n")
            break
        elif opcion == "a":
            for ej in EJERCICIOS:
                ejecutar(ej)
                if ej != EJERCICIOS[-1]:
                    cont = input("\n  Continuar con el siguiente? [Enter / q]: ").strip().lower()
                    if cont == "q":
                        break
        elif opcion.isdigit() and 1 <= int(opcion) <= len(EJERCICIOS):
            ejecutar(EJERCICIOS[int(opcion) - 1])
        else:
            print(f"{RED}  Opción inválida.{RST}")


if __name__ == "__main__":
    main()
