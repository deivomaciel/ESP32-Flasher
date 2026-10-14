import os
import sys

# Modo "esptool embutido": usado quando o programa está empacotado em .exe
if len(sys.argv) > 1 and sys.argv[1] == '--run-esptool':
    sys.argv = ['esptool'] + sys.argv[2:]
    import esptool
    esptool._main()
    sys.exit(0)

from classes.Loader import Loader
from utils.clear import clear
from utils.colors import *
from tabulate import tabulate
from utils.system_log import *
from utils.file_picker import select_firmware_file

loader = Loader()

def format_EPS_table(data):
    table = tabulate(
        data, 
        headers=["ID", "MAC", "Data/hora"], 
        tablefmt="grid"
    )
    print(table)

def menu():
    clear()
    options = ['1. Gravar firmware', '2. Visualizar ESPs gravados', '3. Gerar planilha', '4. Apagar banco de dados', '5. Selecionar firmware', '6. Adicionar novo firmware', '7. Deletar firmware', '0. Sair']

    

    while True:    
        firmwares = loader.show_saved_firmwares()
        
        if firmwares:
            loader.set_firmware(firmwares[-1])

        device = loader.list_devices()
        print(f"\n=== {GREEN}ESPFlasher {RESET}===\n")

        if not device:
            loader.set_port(None)
            print(f'{BRIGHT_RED}Nenhum dispositivo encontrado!{RESET}')

        else:
            device = device[0]
            loader.set_port(device['port'])
            print(f'Dispositivo selecionado: {BRIGHT_BLUE}{device['desc']}{RESET}')
            print(f'Porta selecionada: {BRIGHT_BLUE}{device['port']}{RESET}')

        if loader.show_current_firmware():
            print(f'Fimware: {BRIGHT_BLUE}{loader.show_current_firmware()}{RESET}\n')
        else:
            print(f'Fimware: {BRIGHT_BLUE}Nenhum firmware encontrado!{RESET}\n')
            
        for item in options:
            print(item)

        option = input("\nSelecione uma opção: ")

        if option == "1":
            if not loader.show_saved_firmwares():
                clear()
                print(f'{YELLOW}Nenhum firmware encontrado!{RESET}\n')

            else:
                clear()
                result = loader.start_load()
                if result == 'ok':
                    print(f'{BRIGHT_GREEN}Gravação realizada com sucesso!{RESET}')
                elif result == 'no_mac':
                    print(f'{BRIGHT_YELLOW}Gravada, mas o MAC não foi identificado. '
                        f'ESP NÃO registrado no banco!{RESET}')
                else:
                    print(f'\n{BRIGHT_RED}Erro ao conectar ao ESP. Tente novamente!{RESET}')
                
        
        elif option == '2':
            clear()
            try:
                EPSs = loader.view_ESPs()
                print('ESPs\n')
                format_EPS_table(EPSs)

            except Exception as e:
                print(e)
                print('Erro ao listar ESPs!')

        elif option == '3':
            clear()
            file_name = input("Informe o nome do arquivo: ")

            if file_name.strip() == "":
                warning("Operação cancelada!\n")

            else:
                output = loader.generate_sheet(file_name)
                print(f"Relatório salvo em: {BRIGHT_BLUE}{output}{RESET}")
                print('\n')

        elif option == '4':
            clear()
            print('Digite "deletar" para continuar ')
            print('Digite "cancelar" para cancelar')
            command = input('>> ')
            
            if command.lower() == 'deletar':
                loader.delete_db()
                print('\nBanco de dados deletado com sucesso!')

            elif command.lower() == 'cancelar':
                print('\nOperação cancelada!')
            
            else:
                print('\nInválido. Cancelando operação!')

        elif option == '5':
            clear()
            print('Firmwates:', end='\n\n')
            saved_firmwares = loader.show_saved_firmwares()

            if not saved_firmwares:
                clear()
                print(f'{YELLOW}Nenhum firmware encontrado!{RESET}\n')

            else: 
                for firmware_index in range(len(saved_firmwares)):
                    print(f'{firmware_index}. {BRIGHT_BLUE}{saved_firmwares[firmware_index]}{RESET}')
                
                print()
                try:
                    selected_firmware = int(input('Informe o firmware que deseja utilizar: '))
                    if selected_firmware > len(saved_firmwares) - 1 or selected_firmware < 0:
                        print('Opção inválida!\n')
                    
                    else:
                        loader.set_firmware(saved_firmwares[selected_firmware])
                        clear()
                        print(f'Firmware selecionado: {saved_firmwares[selected_firmware]}\n')

                except Exception as e:
                    print('Opção inválida!\n')

        elif option == "6":
            clear()
            print('Selecione o arquivo de firmware na janela que será aberta...\n')

            source = select_firmware_file()

            if source is None:
                print(f'{BRIGHT_YELLOW}Operação cancelada!{RESET}')
            else:
                try:
                    name = loader.add_firmware(source)
                    print(f'{BRIGHT_GREEN}Firmware "{name}" adicionado com sucesso!{RESET}')
                except FileExistsError as e:
                    print(f'{BRIGHT_YELLOW}{e}{RESET}')
                except Exception as e:
                    print(f'{BRIGHT_RED}Erro ao copiar firmware: {e}{RESET}')

        elif option == "7":
            clear()
            if not loader.show_saved_firmwares():
                clear()
                print(f'{YELLOW}Nenhum firmware encontrado!{RESET}\n')

            else:
                try:
                    print('Firmwates:', end='\n\n')
                    saved_firmwares = loader.show_saved_firmwares()

                    for firmware_index in range(len(saved_firmwares)):
                        print(f'{firmware_index}. {BRIGHT_BLUE}{saved_firmwares[firmware_index]}{RESET}')

                    print()

                    selected_firmware = int(input('Informe o firmware que deseja deletar: '))
                    if selected_firmware > len(saved_firmwares) - 1 or selected_firmware < 0:
                        print('Opção inválida!\n')
                    
                    else:
                        selected_firmware = saved_firmwares[selected_firmware]
                        delete_option = ""
                        in_loop = True
                        clear()
                        
                        while in_loop:
                            print(f'{RED}Deletar o firmware "{selected_firmware}"?{RESET}')
                            delete_option = input('[S] / [N]: ')

                            if delete_option.lower().strip() == "" or delete_option.lower() not in ['s', 'n']:
                                clear()
                                continue

                            elif delete_option.lower() == 's':
                                clear()

                                loader.delete_firmware(selected_firmware)
                                if loader.show_saved_firmwares(): loader.set_firmware(loader.show_saved_firmwares()[-1])
                                print(f'{YELLOW}"{selected_firmware}" deletado!{RESET}')
                                
                            else:
                                print(f'\n{YELLOW}Operação cancelada!{RESET}')

                            in_loop = False

                except Exception as e:
                    print(e)
                    print('Erro ao listar ESPs!')

        elif option == "0":
            print("Saindo...")
            break

        elif option.strip() == "":
            clear()
            continue

        else:
            print("\nOpção inválida! Tente novamente.")
        
        print('Pressione [ENTER] para continuar')
        input()
        clear()

if __name__ == "__main__":
    menu()
