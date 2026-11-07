"""
Окно просмотра графика с возможностью масштабирования (zoom/pan)
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import matplotlib
import pandas as pd

matplotlib.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans', 'sans-serif']
matplotlib.rcParams['axes.unicode_minus'] = False


class ChartViewer:
    """
    Отдельное окно для просмотра графика с навигацией.
    Открывается по двойному клику на график в дашборде.
    """

    def __init__(self, parent, chart_data: dict):
        """
        Args:
            parent: Родительское окно
            chart_data: Словарь с данными графика:
                - title: str
                - chart_type: 'bar' | 'line'
                - df: DataFrame
                - x_col: str
                - y_col: str
                - x_label: str
                - y_label: str
                - colors: list (цвета)
                - theme_colors: dict (цвета темы)
        """
        self.parent = parent
        self.chart_data = chart_data

        self.window = tk.Toplevel(parent)
        self.window.title(chart_data.get('title', 'График'))
        self.window.geometry("900x600")
        self.window.transient(parent)

        # Центрирование
        self.window.update_idletasks()
        x = parent.winfo_rootx() + (parent.winfo_width() // 2) - 450
        y = parent.winfo_rooty() + (parent.winfo_height() // 2) - 300
        self.window.geometry(f"+{max(0, x)}+{max(0, y)}")

        self._create_widgets()

    def _create_widgets(self):
        """Создание виджетов окна просмотра"""
        # Верхняя панель с заголовком и кнопкой сохранения
        top_frame = ttk.Frame(self.window)
        top_frame.pack(fill='x', padx=10, pady=10)

        ttk.Label(
            top_frame,
            text=self.chart_data.get('title', 'График'),
            font=('Arial', 14, 'bold')
        ).pack(side='left')

        save_btn = ttk.Button(
            top_frame,
            text="💾 Сохранить как PNG",
            command=self._save_as_png
        )
        save_btn.pack(side='right')

        # Основной контейнер для графика
        main_frame = ttk.Frame(self.window)
        main_frame.pack(fill='both', expand=True, padx=10, pady=(0, 10))

        # Создаём фигуру
        self.fig = Figure(figsize=(10, 7), dpi=100)
        self.ax = self.fig.add_subplot(111)

        # Рисуем график
        self._draw_chart()

        # Canvas
        self.canvas = FigureCanvasTkAgg(self.fig, master=main_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill='both', expand=True)

        # Панель навигации (zoom, pan, home, save)
        toolbar_frame = ttk.Frame(self.window)
        toolbar_frame.pack(fill='x', padx=10, pady=(0, 10))

        self.toolbar = NavigationToolbar2Tk(self.canvas, toolbar_frame)
        self.toolbar.update()

        # Подсказка
        hint_label = ttk.Label(
            self.window,
            text="💡 Используйте кнопки выше для zoom/pan, или колёсико мыши для масштаба по Y",
            font=('Arial', 9),
            foreground='gray'
        )
        hint_label.pack(pady=(0, 5))

        # Привязка колёсика мыши для zoom по Y
        self.canvas.get_tk_widget().bind("<MouseWheel>", self._on_mousewheel)
        self.canvas.get_tk_widget().bind("<Button-4>", self._on_mousewheel_linux_up)
        self.canvas.get_tk_widget().bind("<Button-5>", self._on_mousewheel_linux_down)

    def _draw_chart(self):
        """Отрисовка графика"""
        chart_type = self.chart_data.get('chart_type', 'bar')
        df = self.chart_data.get('df', pd.DataFrame())
        x_col = self.chart_data.get('x_col', '')
        y_col = self.chart_data.get('y_col', '')
        x_label = self.chart_data.get('x_label', '')
        colors = self.chart_data.get('colors', ['#4C72B0'])
        theme_colors = self.chart_data.get('theme_colors', {})

        text_color = theme_colors.get('text_primary', 'black')
        grid_color = theme_colors.get('chart_grid', '#E0E0E0')
        bg_color = theme_colors.get('chart_bg', 'white')

        self.fig.patch.set_facecolor(bg_color)
        self.ax.set_facecolor(bg_color)

        if df.empty:
            self.ax.text(0.5, 0.5, 'Нет данных', ha='center', va='center', fontsize=14)
            return

        if chart_type == 'bar':
            # Столбчатая диаграмма
            bar_colors = [colors[i % len(colors)] for i in range(len(df))]
            bars = self.ax.bar(df[x_col].astype(str), df[y_col], color=bar_colors, edgecolor=text_color, linewidth=0.5)

            # Подписи значений над столбцами
            for bar in bars:
                yval = bar.get_height()
                self.ax.text(
                    bar.get_x() + bar.get_width() / 2,
                    yval + (yval * 0.02),
                    f'{yval:,.0f}'.replace(',', ' '),
                    ha='center', va='bottom', fontsize=9, color=text_color
                )
        elif chart_type == 'line':
            # Линейный график
            line_color = colors[0] if colors else '#C44E52'
            self.ax.plot(
                df[x_col].astype(str), df[y_col],
                marker='o', color=line_color, linewidth=2, markersize=6
            )
            self.ax.fill_between(
                df[x_col].astype(str), df[y_col],
                color=line_color, alpha=0.2
            )

        self.ax.set_title(
            self.chart_data.get('title', ''),
            fontsize=14, fontweight='bold', pad=15, color=text_color
        )
        self.ax.set_xlabel(x_label, fontsize=11, color=text_color)
        self.ax.set_ylabel(self.chart_data.get('y_label', ''), fontsize=11, color=text_color)
        self.ax.tick_params(axis='x', rotation=45, labelsize=10, colors=text_color)
        self.ax.tick_params(axis='y', labelsize=10, colors=text_color)
        self.ax.grid(True, linestyle='--', alpha=0.7, color=grid_color)

        self.fig.tight_layout()

    def _on_mousewheel(self, event):
        """Zoom по оси Y колёсиком мыши (Windows/Mac)"""
        factor = 1.1 if event.delta < 0 else 0.9
        ymin, ymax = self.ax.get_ylim()
        ycenter = (ymin + ymax) / 2
        yrange = (ymax - ymin) / 2 * factor
        self.ax.set_ylim(ycenter - yrange, ycenter + yrange)
        self.canvas.draw()

    def _on_mousewheel_linux_up(self, event):
        """Zoom in (Linux)"""
        ymin, ymax = self.ax.get_ylim()
        ycenter = (ymin + ymax) / 2
        yrange = (ymax - ymin) / 2 * 0.9
        self.ax.set_ylim(ycenter - yrange, ycenter + yrange)
        self.canvas.draw()

    def _on_mousewheel_linux_down(self, event):
        """Zoom out (Linux)"""
        ymin, ymax = self.ax.get_ylim()
        ycenter = (ymin + ymax) / 2
        yrange = (ymax - ymin) / 2 * 1.1
        self.ax.set_ylim(ycenter - yrange, ycenter + yrange)
        self.canvas.draw()

    def _save_as_png(self):
        """Сохранить график как PNG"""
        filepath = filedialog.asksaveasfilename(
            title="Сохранить график как PNG",
            defaultextension=".png",
            filetypes=[("PNG файлы", "*.png"), ("Все файлы", "*.*")],
            initialfile=f"{self.chart_data.get('title', 'chart')}.png"
        )

        if filepath:
            try:
                self.fig.savefig(filepath, dpi=150, bbox_inches='tight')
                messagebox.showinfo("Успех", f"График сохранён:\n{filepath}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось сохранить:\n{e}")