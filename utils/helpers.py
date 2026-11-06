"""
Вспомогательные функции для работы с путями
"""

import sys
import os


def get_base_path():
    """
    Получение базового пути приложения.
    Работает корректно как при запуске из исходников, так и из .exe
    """
    if getattr(sys, 'frozen', False):
        # Приложение запущено из .exe
        return os.path.dirname(sys.executable)
    else:
        # Приложение запущено из исходников
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_resource_path(relative_path):
    """
    Получение полного пути к ресурсу (файлу)
    """
    base_path = get_base_path()
    return os.path.join(base_path, relative_path)