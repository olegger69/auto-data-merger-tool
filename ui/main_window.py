"""
Главное окно приложения
"""

import tkinter as tk
from tkinter import ttk


class MainWindow:
    """Главное окно Auto Data Merger Tool"""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Auto Data Merger Tool")
        self.root.geometry("1000x700")

        self._create_widgets()

    def _create_widgets(self):
        """Создание виджетов главного окна"""
        # Заголовок
        header = ttk.Label(
            self.root,
            text="Auto Data Merger Tool",
            font=('Arial', 18, 'bold')
        )
        header.pack(pady=30)

        # Информационное сообщение
        info = ttk.Label(
            self.root,
            text="Приложение готово к работе!\n\nЗдесь будет интерфейс для импорта файлов и дашборд.",
            font=('Arial', 12)
        )
        info.pack(pady=20)

        # Кнопка закрытия
        close_btn = ttk.Button(
            self.root,
            text="Закрыть",
            command=self.root.quit
        )
        close_btn.pack(pady=20)
