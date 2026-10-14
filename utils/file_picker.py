import tkinter as tk
from tkinter import filedialog


def select_firmware_file():
    root = tk.Tk()
    root.withdraw()                      # esconde a janela principal vazia
    root.attributes('-topmost', True)    # garante que o diálogo apareça na frente do terminal

    path = filedialog.askopenfilename(
        title="Selecione o firmware",
        filetypes=[
            (".bin", "*.bin"),
            (".hex", "*.hex"),
            ("Todos os arquivos", "*.*"),
        ],
    )

    root.destroy()
    return path or None                  # string vazia (cancelou) vira None
