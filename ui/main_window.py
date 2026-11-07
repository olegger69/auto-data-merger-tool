"""
Главное окно приложения с вкладками, переключением тем, палитр и корреляций
"""

import tkinter as tk
from tkinter import ttk
from core.config import ConfigManager
from core.theme import ThemeManager
from core.chart_palettes import ChartPalettes
from ui.file_panel import FilePanel
from ui.dashboard_panel import DashboardPanel
from ui.export_panel import ExportPanel
from ui.filter_panel import FilterPanel
from ui.comparison_panel import ComparisonPanel
from ui.correlation_panel import CorrelationPanel
from ui.palette_dialog import PaletteDialog


class MainWindow:
    """Главное окно Auto Data Merger Tool"""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Auto Data Merger Tool")

        self.config = ConfigManager()

        # Текущая тема и палитра
        self.current_theme = self.config.get('theme', 'light')
        self.current_palette = self.config.get('chart_palette', 'classic')
        self.theme_colors = ThemeManager.get_theme(self.current_theme)
        self.chart_palette = ChartPalettes.get_palette(self.current_palette)

        # Геометрия окна
        width = self.config.get('window_width', 1200)
        height = self.config.get('window_height', 800)
        x = self.config.get('window_x', 100)
        y = self.config.get('window_y', 100)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
        self.root.minsize(900, 600)

        # Хранилище данных
        self.merged_data = None
        self.summaries = None
        self.kpi = None

        self._setup_styles()
        self._apply_theme_colors()
        self._create_widgets()

        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)

    def _setup_styles(self):
        """Настройка стилей ttk"""
        style = ttk.Style()
        style.theme_use('clam')

        style.configure('Header.TLabel', font=('Arial', 14, 'bold'))
        style.configure('Title.TLabel', font=('Arial', 18, 'bold'))
        style.configure('TButton', font=('Arial', 10), padding=5)
        style.configure('Accent.TButton', font=('Arial', 10, 'bold'))
        style.configure('TLabelframe', borderwidth=2)
        style.configure('TLabelframe.Label', font=('Arial', 10, 'bold'))

    def _apply_theme_colors(self):
        """Применение цветов текущей темы"""
        colors = self.theme_colors

        self.root.configure(bg=colors['bg_primary'])

        style = ttk.Style()
        style.configure('TFrame', background=colors['bg_primary'])
        style.configure('TLabelframe', background=colors['bg_secondary'])
        style.configure('TLabelframe.Label', background=colors['bg_secondary'],
                        foreground=colors['text_primary'])
        style.configure('TLabel', background=colors['bg_primary'],
                        foreground=colors['text_primary'])
        style.configure('TButton', background=colors['bg_tertiary'],
                        foreground=colors['text_primary'])
        style.configure('Treeview', background=colors['bg_secondary'],
                        foreground=colors['text_primary'],
                        fieldbackground=colors['bg_secondary'])
        style.configure('Treeview.Heading', background=colors['bg_tertiary'],
                        foreground=colors['text_primary'])
        style.map('Treeview', background=[('selected', colors['accent'])])
        style.map('TButton', background=[('active', colors['accent_hover'])])

        import matplotlib
        matplotlib.rcParams['axes.facecolor'] = colors['chart_bg']
        matplotlib.rcParams['axes.edgecolor'] = colors['text_secondary']
        matplotlib.rcParams['axes.labelcolor'] = colors['text_primary']
        matplotlib.rcParams['text.color'] = colors['text_primary']
        matplotlib.rcParams['xtick.color'] = colors['text_secondary']
        matplotlib.rcParams['ytick.color'] = colors['text_secondary']
        matplotlib.rcParams['grid.color'] = colors['chart_grid']

    def _create_widgets(self):
        """Создание виджетов главного окна"""
        # Верхняя панель
        header_frame = ttk.Frame(self.root)
        header_frame.pack(fill='x', padx=10, pady=10)

        title = ttk.Label(header_frame, text="Auto Data Merger Tool", style='Title.TLabel')
        title.pack(side='left')

        # Правая часть: настройки
        settings_frame = ttk.Frame(header_frame)
        settings_frame.pack(side='right')

        # Переключатель темы
        theme_frame = ttk.Frame(settings_frame)
        theme_frame.pack(side='left', padx=(0, 10))

        ttk.Label(theme_frame, text="🎨 Тема:", font=('Arial', 10)).pack(side='left', padx=(0, 5))

        self.theme_var = tk.StringVar(value=self.current_theme)
        theme_combo = ttk.Combobox(
            theme_frame,
            textvariable=self.theme_var,
            values=['light', 'dark'],
            state='readonly',
            width=10
        )
        theme_combo.pack(side='left')
        theme_combo.bind('<<ComboboxSelected>>', self._on_theme_change)

        # Кнопка выбора палитры
        palette_btn = ttk.Button(
            settings_frame,
            text="🎨 Палитра",
            command=self._on_palette_change
        )
        palette_btn.pack(side='left')

        # Статусная строка
        self.status_var = tk.StringVar(value="Готов к работе")
        status_bar = ttk.Label(
            self.root,
            textvariable=self.status_var,
            relief='sunken',
            anchor='w'
        )
        status_bar.pack(side='bottom', fill='x')

        # Вкладки
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=5)

        self.file_panel = FilePanel(self.notebook, self)
        self.notebook.add(self.file_panel.frame, text="📁 Импорт файлов")

        dashboard_container = ttk.Frame(self.notebook)
        self.notebook.add(dashboard_container, text="📊 Дашборд")

        self.filter_panel = FilterPanel(dashboard_container, self)
        self.filter_panel.frame.pack(fill='x')

        self.dashboard_panel = DashboardPanel(dashboard_container, self)
        self.dashboard_panel.frame.pack(fill='both', expand=True)

        self.comparison_panel = ComparisonPanel(self.notebook, self)
        self.notebook.add(self.comparison_panel.frame, text="📈 Сравнение")

        # НОВАЯ ВКЛАДКА: Корреляции
        self.correlation_panel = CorrelationPanel(self.notebook, self)
        self.notebook.add(self.correlation_panel.frame, text="🔗 Корреляции")

        self.export_panel = ExportPanel(self.notebook, self)
        self.notebook.add(self.export_panel.frame, text="💾 Экспорт")

    def _on_theme_change(self, event):
        """Обработка смены темы"""
        new_theme = self.theme_var.get()
        if new_theme != self.current_theme:
            self.current_theme = new_theme
            self.theme_colors = ThemeManager.get_theme(new_theme)
            self.config.set('theme', new_theme)

            self._setup_styles()
            self._apply_theme_colors()

            self.dashboard_panel.update_theme(new_theme)
            self.correlation_panel.update_theme(new_theme)
            self.root.update_idletasks()

            if self.merged_data is not None:
                self.dashboard_panel.update_dashboard(
                    self.merged_data, self.summaries, self.kpi
                )

            self.set_status(f"🎨 Тема изменена на: {'тёмная' if new_theme == 'dark' else 'светлая'}")

    def _on_palette_change(self):
        """Обработка смены палитры"""
        dialog = PaletteDialog(self.root, self.current_palette)
        new_palette = dialog.show()

        if new_palette and new_palette != self.current_palette:
            self.current_palette = new_palette
            self.chart_palette = ChartPalettes.get_palette(new_palette)
            self.config.set('chart_palette', new_palette)

            if self.merged_data is not None:
                self.dashboard_panel.update_palette(self.chart_palette)
                self.dashboard_panel.update_dashboard(
                    self.merged_data, self.summaries, self.kpi
                )

            palette_name = ChartPalettes.PALETTES[new_palette]['name']
            self.set_status(f"🎨 Палитра изменена на: {palette_name}")

    def set_status(self, message: str):
        """Обновление статусной строки"""
        self.status_var.set(message)
        self.root.update_idletasks()

    def _on_closing(self):
        """Обработчик закрытия окна"""
        try:
            self.root.update_idletasks()
            width = self.root.winfo_width()
            height = self.root.winfo_height()
            x = self.root.winfo_x()
            y = self.root.winfo_y()

            self.config.update_window_geometry(width, height, x, y)
        except Exception as e:
            print(f"⚠️ Не удалось сохранить геометрию окна: {e}")

        self.root.destroy()

    def on_data_merged(self, merged_df, summaries, kpi):
        """Callback после успешного объединения данных."""
        self.merged_data = merged_df
        self.summaries = summaries
        self.kpi = kpi

        self.set_status(f"✅ Данные объединены: {len(merged_df)} строк")

        self.filter_panel.update_options(merged_df)
        self.dashboard_panel.update_theme(self.current_theme)
        self.dashboard_panel.update_palette(self.chart_palette)
        self.dashboard_panel.update_dashboard(merged_df, summaries, kpi)

        # Обновляем панель корреляций
        self.correlation_panel.update_theme(self.current_theme)
        self.correlation_panel.update_data(merged_df)

        self.notebook.select(1)