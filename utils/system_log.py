from .colors import *

def info(message: str) -> None:
    print(f'{BRIGHT_BLUE}{message}{RESET}')

def error(message: str) -> None:
    print(f'{BRIGHT_RED}{message}{RESET}')

def warning(message: str) -> None:
    print(f'{YELLOW}{message}{RESET}')

def success(message: str) -> None:
    print(f'{GREEN}{message}{RESET}')