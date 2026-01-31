import os
import sys
import subprocess

def install_requirements():
    print("Instalando dependencias desde requirements.txt...")

    req_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "requirements.txt")

    if not os.path.exists(req_path):
        print("❌ No se encontró requirements.txt")
        return

    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", req_path])
        print("✔ Dependencias instaladas correctamente.\n")
    except subprocess.CalledProcessError as e:
        print("❌ Error instalando dependencias:", e)

def run_server():
    manage_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "manage.py")

    command = [sys.executable, manage_path, "runserver", "0.0.0.0:8000"]

    print("Iniciando servidor Django en http://127.0.0.1:8000 ...\n")

    try:
        subprocess.run(command)
    except Exception as e:
        print("❌ Error ejecutando runserver:", e)

def main():
    install_requirements()
    run_server()

if __name__ == "__main__":
    main()
