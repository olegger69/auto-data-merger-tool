"""
Панель визуализации корреляций (Heatmap)
"""

import tkinter as tk
from tkinter import ttk, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib
import pandas as pd
import numpy as np
from core.correlation import CorrelationAnalyzer
from core.theme import ThemeManager

matplotlib.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans', 'sans-serif']
matplotlib.rcParams['axes.unicode_minus'] = False


class CorrelationPanel:
    """Панель для отображения heatmap корреляций"""

    def __init__(self, parent, main_window):
        self.parent = parent
        self.main_window = main_window
        self.frame = ttk.Frame(parent)
        self.theme_colors = ThemeManager.get_theme('light')

        self._create_widgets()

    def _create_widgets(self):
        """Создание виджетов панели"""
        # Заголовок
        header = ttk.Label(
            self.frame,
            text="🔗 Анализ корреляций показателей",
            font=('Arial', 16, 'bold')
        )
        header.pack(pady=15)

        # Описание
        desc = ttk.Label(
            self.frame,
            text="Тепловая карта показывает силу линейной связи между числовыми показателями.\n"
                 "Значения от -1 (полная отрицательная связь) до +1 (полная положительная связь).",
            font=('Arial', 10),
            justify='center',
            foreground=self.theme_colors.get('text_secondary', 'gray')
        )
        desc.pack(pady=(0, 15))

        # Контейнер для графика
        self.chart_container = ttk.Frame(self.frame)
        self.chart_container.pack(fill='both', expand=True, padx=20, pady=10)

        # Заглушка
        self.placeholder = ttk.Label(
            self.chart_container,
            text="Загрузите и объедините данные на вкладке «Импорт файлов»,\nчтобы увидеть анализ корреляций.",
            font=('Arial', 12),
            foreground='gray',
            justify='center'
        )
        self.placeholder.pack(expand=True)

        # Секция текстовой интерпретации
        self.interpretation_frame = ttk.LabelFrame(
            self.frame,
            text="💡 Ключевые взаимосвязи",
            padding=15
        )
        self.interpretation_frame.pack(fill='x', padx=20, pady=10)

        self.interpretation_text = tk.Text(
            self.interpretation_frame,
            height=6,
            font=('Arial', 10),
            wrap='word',
            bg=self.theme_colors.get('bg_secondary', 'white'),
            fg=self.theme_colors.get('text_primary', 'black')
        )
        self.interpretation_text.pack(fill='both', expand=True)
        self.interpretation_text.insert('1.0', "Данные не загружены.")
        self.interpretation_text.config(state='disabled')

    def update_theme(self, theme_name: str):
        """Обновление темы"""
        self.theme_colors = ThemeManager.get_theme(theme_name)
        self.interpretation_text.config(
            bg=self.theme_colors.get('bg_secondary', 'white'),
            fg=self.theme_colors.get('text_primary', 'black')
        )

    def update_data(self, df: pd.DataFrame):
        """Обновление данных и перерисовка heatmap"""
        if df is None or df.empty:
            self._show_placeholder()
            return

        # Считаем матрицу корреляций
        corr_matrix = CorrelationAnalyzer.calculate_correlation_matrix(df)

        if corr_matrix is None or corr_matrix.empty:
            self._show_placeholder(
                "Недостаточно числовых данных для анализа корреляций.\nУбедитесь, что в данных есть столбцы: количество, цена, выручка, прибыль.")
            return

        # Очищаем контейнер
        for widget in self.chart_container.winfo_children():
            widget.destroy()

        # Рисуем heatmap
        self._draw_heatmap(corr_matrix)

        # Обновляем текстовую интерпретацию
        self._update_interpretation(corr_matrix)

    def _show_placeholder(self, message: str = None):
        """Показать заглушку"""
        for widget in self.chart_container.winfo_children():
            widget.destroy()

        text = message or "Загрузите и объедините данные на вкладке «Импорт файлов»,\nчтобы увидеть анализ корреляций."
        ttk.Label(
            self.chart_container,
            text=text,
            font=('Arial', 12),
            foreground='gray',
            justify='center'
        ).pack(expand=True)

        self.interpretation_text.config(state='normal')
        self.interpretation_text.delete('1.0', 'end')
        self.interpretation_text.insert('1.0', "Данные не загружены или недостаточно числовых показателей.")
        self.interpretation_text.config(state='disabled')

    def _draw_heatmap(self, corr_matrix: pd.DataFrame):
        """Отрисовка тепловой карты"""
        fig = Figure(figsize=(8, 6), dpi=100)
        ax = fig.add_subplot(111)

        # Получаем понятные названия
        labels = CorrelationAnalyzer.get_column_labels(list(corr_matrix.columns))
        display_labels = [labels[col] for col in corr_matrix.columns]

        # Рисуем heatmap
        cax = ax.imshow(corr_matrix, cmap='coolwarm', vmin=-1, vmax=1)

        # Добавляем цветовую шкалу
        cbar = fig.colorbar(cax, ax=ax)
        cbar.set_label('Коэффициент корреляции Пирсона', fontsize=10)

        # Настраиваем оси
        ax.set_xticks(np.arange(len(display_labels)))
        ax.set_yticks(np.arange(len(display_labels)))
        ax.set_xticklabels(display_labels, rotation=45, ha='right', fontsize=10)
        ax.set_yticklabels(display_labels, fontsize=10)

        # Добавляем числовые значения в ячейки
        for i in range(len(corr_matrix.columns)):
            for j in range(len(corr_matrix.columns)):
                val = corr_matrix.iloc[i, j]
                # Белый текст на тёмном фоне, чёрный на светлом
                text_color = "white" if abs(val) > 0.5 else "black"
                ax.text(j, i, f"{val:.2f}", ha="center", va="center", color=text_color, fontsize=10, fontweight='bold')

        ax.set_title("Матрица корреляций показателей", fontsize=12, fontweight='bold', pad=15)

        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=self.chart_container)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)

    def _update_interpretation(self, corr_matrix: pd.DataFrame):
        """Обновление текстовой интерпретации сильных связей"""
        strong = CorrelationAnalyzer.get_strong_correlations(corr_matrix, threshold=0.5)
        labels = CorrelationAnalyzer.get_column_labels(list(corr_matrix.columns))

        self.interpretation_text.config(state='normal')
        self.interpretation_text.delete('1.0', 'end')

        if not strong:
            self.interpretation_text.insert('1.0',
                                            "Сильных линейных взаимосвязей (|r| > 0.5) между показателями не обнаружено.")
        else:
            lines = ["Обнаружены следующие заметные и сильные взаимосвязи:\n"]
            for col1, col2, value in strong[:5]:  # Показываем топ-5
                name1 = labels[col1]
                name2 = labels[col2]
                interp = CorrelationAnalyzer.interpret_correlation(value)
                lines.append(f"  • {name1} и {name2}: {value:+.2f} ({interp})")

            lines.append(
                "\n💡 Вывод: Положительная связь означает, что рост одного показателя сопровождается ростом другого.")

            self.interpretation_text.insert('1.0', "\n".join(lines))

        self.interpretation_text.config(state='disabled')