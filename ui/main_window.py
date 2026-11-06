"""
Главное окно приложения с вкладками
"""

import tkinter as tk
from tkinter import ttk
from ui.file_panel import FilePanel
from ui.dashboard_panel import DashboardPanel
from ui.export_panel import ExportPanel


class MainWindow:
    """Главное окно Auto Data Merger Tool"""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Auto Data Merger Tool")
        self.root.geometry("1200x800")
        self.root.minsize(900, 600)

        # Хранилище данных приложения
        self.merged_data = None
        self.summaries = None
        self.kpi = None

        # Настройка стилей
        self._setup_styles()

        # Создание интерфейса
        self._create_widgets()

    def _setup_styles(self):
        """Настройка стилей ttk"""
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Header.TLabel', font=('Arial', 14, 'bold'))
        style.configure('Title.TLabel', font=('Arial', 18, 'bold'))

    def _create_widgets(self):
        """Создание виджетов главного окна"""
        # Заголовок приложения
        header_frame = ttk.Frame(self.root)
        header_frame.pack(fill='x', padx=10, pady=10)

        title = ttk.Label(
            header_frame,
            text="Auto Data Merger Tool",
            style='Title.TLabel'
        )
        title.pack(side='left')

        # Статусная строка
        self.status_var = tk.StringVar(value="Готов к работе")
        status_bar = ttk.Label(
            self.root,
            textvariable=self.status_var,
            relief='sunken',
            anchor='w'
        )
        status_bar.pack(side='bottom', fill='x')

        # Notebook (вкладки)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=5)

        # Вкладка 1: Импорт файлов
        self.file_panel = FilePanel(self.notebook, self)
        self.notebook.add(self.file_panel.frame, text="📁 Импорт файлов")

        # Вкладка 2: Дашборд
        self.dashboard_panel = DashboardPanel(self.notebook, self)
        self.notebook.add(self.dashboard_panel.frame, text="📊 Дашборд")

        # Вкладка 3: Экспорт
        self.export_panel = ExportPanel(self.notebook, self)
        self.notebook.add(self.export_panel.frame, text="💾 Экспорт")

    def set_status(self, message: str):
        """Обновление статусной строки"""
        self.status_var.set(message)
        self.root.update_idletasks()

    def on_data_merged(self, merged_df, summaries, kpi):
        """
        Callback после успешного объединения данных.
        Вызывается из FilePanel.
        """
        self.merged_data = merged_df
        self.summaries = summaries
        self.kpi = kpi

        self.set_status(f"✅ Данные объединены: {len(merged_df)} строк")

        # Обновляем дашборд
        self.dashboard_panel.update_dashboard(merged_df, summaries, kpi)

        # Переключаемся на вкладку дашборда
        self.notebook.select(1)