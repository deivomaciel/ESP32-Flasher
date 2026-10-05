import sys
import os

def path_resolver(dir_name: str) -> str:
    if getattr(sys, 'frozen', False): # Verifica exe
        base_path = sys._MEIPASS
        boot_path = os.path.join(base_path, dir_name)

    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
        boot_path = os.path.join(base_path, '..', dir_name)
    
    boot_path = os.path.abspath(boot_path).replace('\\', '/')
    return boot_path

def data_path(dir_name: str) -> str:
    """Pasta gravável e persistente (ao lado do .exe ou na raiz do projeto)."""
    if getattr(sys, 'frozen', False):
        base = os.path.dirname(sys.executable)
    else:
        base = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
    path = os.path.join(base, dir_name)
    os.makedirs(path, exist_ok=True)
    return path.replace('\\', '/')