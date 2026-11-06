"""
Главное окно приложения с вкладками
"""

import tkinter as tk
from tkinter import ttk
from core.config import ConfigManager
from ui.file_panel import FilePanel
from ui.dashboard_panel import DashboardPanel
from ui.export_panel import ExportPanel
from ui.filter_panel import FilterPanel


class MainWindow:
    """Главное окно Auto Data Merger Tool"""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Auto Data Merger Tool")

        # Менеджер настроек
        self.config = ConfigManager()

        # Применение сохранённой геометрии окна
        width = self.config.get('window_width', 1200)
        height = self.config.get('window_height', 800)
        x = self.config.get('window_x', 100)
        y = self.config.get('window_y', 100)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
        self.root.minsize(900, 600)

        # Хранилище данных приложения
        self.merged_data = None
        self.summaries = None
        self.kpi = None

        # Настройка стилей
        self._setup_styles()

        # Создание интерфейса
        self._create_widgets()

        # Сохранение настроек при закрытии
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)

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

        # Вкладка 2: Дашборд (с фильтрами)
        dashboard_container = ttk.Frame(self.notebook)
        self.notebook.add(dashboard_container, text="📊 Дашборд")

        # Панель фильтров (внутри вкладки дашборда)
        self.filter_panel = FilterPanel(dashboard_container, self)
        self.filter_panel.frame.pack(fill='x')

        # Дашборд (под фильтрами)
        self.dashboard_panel = DashboardPanel(dashboard_container, self)
        self.dashboard_panel.frame.pack(fill='both', expand=True)

        # Вкладка 3: Экспорт
        self.export_panel = ExportPanel(self.notebook, self)
        self.notebook.add(self.export_panel.frame, text="💾 Экспорт")

    def set_status(self, message: str):
        """Обновление статусной строки"""
        self.status_var.set(message)
        self.root.update_idletasks()

    def _on_closing(self):
        """Обработчик закрытия окна — сохраняет геометрию"""
        try:
            # Получаем текущие размеры и позицию
            self.root.update_idletasks()
            width = self.root.winfo_width()
            height = self.root.winfo_height()
            x = self.root.winfo_x()
            y = self.root.winfo_y()

            # Сохраняем в конфиг
            self.config.update_window_geometry(width, height, x, y)
        except Exception as e:
            print(f"⚠️ Не удалось сохранить геометрию окна: {e}")

        # Закрываем приложение
        self.root.destroy()

    def on_data_merged(self, merged_df, summaries, kpi):
        """
        Callback после успешного объединения данных.
        Вызывается из FilePanel.
        """
        self.merged_data = merged_df
        self.summaries = summaries
        self.kpi = kpi

        self.set_status(f"✅ Данные объединены: {len(merged_df)} строк")

        # Обновляем опции фильтров
        self.filter_panel.update_options(merged_df)

        # Обновляем дашборд
        self.dashboard_panel.update_dashboard(merged_df, summaries, kpi)

        # Переключаемся на вкладку дашборда
        self.notebook.select(1)