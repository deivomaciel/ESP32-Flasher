import serial.tools.list_ports as port_list
import subprocess
import re
import os
import sys
from os import listdir
from openpyxl import Workbook
from .Database import Database
from utils.path_resolver import path_resolver
from utils.clear import clear
from utils.colors import BRIGHT_GREEN, BRIGHT_BLUE, RESET

boot_path = path_resolver('BOOT')
firmware_path = path_resolver('firmwares')
database = Database('System')
database.create_tables()

MAC_RE = re.compile(r'^([0-9A-F]{2}:){5}[0-9A-F]{2}$')

class Loader:
    def __init__(self):
        self.__port = None
        self.__current_firmware = None
        firmwares = self.show_saved_firmwares()
        if not firmwares:
            raise FileNotFoundError(f'Nenhum firmware .bin encontrado em {firmware_path}')
        self.set_firmware(firmwares[-1])  # o mais recente

    def list_devices(self) -> list:
        ports = port_list.comports()
        if not ports:
            return False
        else:
            total_ports = [ { 'port': port.device, 'desc': port.description } for port in ports ]
            return total_ports

    def get_mac(self, line_output: str):
        if line_output.startswith('MAC:'):
            mac = line_output.split('MAC:', 1)[1].strip().upper()
            return mac if MAC_RE.match(mac) else None
        return None
            
    def show_saved_firmwares(self):
        files = [f for f in listdir(firmware_path) if f.lower().endswith('.bin')]
        return sorted(files, key=lambda f: [int(x) if x.isdigit() else x for x in re.split(r'(\d+)', f)])

    def set_firmware(self, firm):
        self.__current_firmware = firm

    def show_current_firmware(self):
        return self.__current_firmware

    def save_mac(self, mac: str) -> None:    
        # Criear nova thread para guardar mac no banco
        database.save_ctd(mac)

    def set_port(self, port: str):
        self.__port = port

    def list_ports():
        ports = port_list.comports()
        print(ports)

    def view_remotes(self):
        return database.get_all_remotes()

    def delete_db(self):
        database.drop_database()
    

    def _esptool_cmd(self) -> list:
        if getattr(sys, 'frozen', False):
            # No .exe, sys.executable é o próprio programa; ele se reinvoca com a flag
            return [sys.executable, '--run-esptool']
        return [sys.executable, f'{boot_path}/tool-esptoolpy/run_esptool.py']

    def start_load(self) -> str:
        mac = None

        if not self.__port:
            return 'error'

        try:
            command = self._esptool_cmd() + [
                "--chip", "esp32c3",
                "--port", self.__port,
                "--baud", "460800",
                "--before", "default_reset",
                "--after", "hard-reset",
                "write-flash", "-z",
                "--flash-mode", "dio",
                "--flash-freq", "80m",
                "--flash-size", "4MB",
                "0x0000", f"{boot_path}/bootloader.bin",
                "0x8000", f"{boot_path}/partitions.bin",
                "0xe000", f"{boot_path}/boot_app0.bin",
                "0x10000", f"{firmware_path}/{self.__current_firmware}"
            ]

            print("Executando:")

            processo = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )

            for line in processo.stdout:
                if mac is None:
                    mac = self.get_mac(line)

                if line.startswith("Writing at"):
                    clear()
                    print(f"MAC do ESP: {BRIGHT_BLUE}{mac}{RESET}")
                    print(line)

                elif "A fatal error occurred" in line:
                    processo.wait()
                    return 'error'

            codigo = processo.wait()

            if codigo != 0:
                print(f"\nProcesso finalizado com código: {codigo}")
                return 'error'

            if mac is None:
                return 'no_mac'

            if not database.find_remote_by_mac(mac):
                self.save_mac(mac)

            return 'ok'

        except Exception as e:
            print(f"Erro ao executar esptool: {e}")
            return 'error'
    
    
    def generate_sheet(self, file_name):
        user_dir = os.path.expanduser("~")
        output_path = os.path.join(user_dir, f"{file_name}.xlsx")

        wb = Workbook()
        ws = wb.active
        ws.title = 'ESPs'
        ws.append(['ID', 'MAC', 'Data e Hora'])
        for row in self.view_remotes():
            ws.append(list(row))
        wb.save(output_path)
        return output_path



