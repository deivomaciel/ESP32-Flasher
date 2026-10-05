import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

# Garante que o Python carregue o esptool que está dentro do BOOT
sys.path.insert(0, str(BASE_DIR))

import esptool

if __name__ == "__main__":
    esptool._main()
