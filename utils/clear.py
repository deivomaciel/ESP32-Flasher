import os
import platform

def clear():
    sistema = platform.system()
    if sistema == "Windows":
        os.system('cls')  # Comando para Windows
    else:
        os.system('clear')  # Comando para Linux/Mac