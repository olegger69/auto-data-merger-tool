"""
Построение графиков с помощью Matplotlib
"""

import matplotlib.pyplot as plt
import matplotlib
from matplotlib.figure import Figure
import pandas as pd

# Настройка шрифтов для корректного отображения кириллицы
matplotlib.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans', 'sans-serif']
matplotlib.rcParams['axes.unicode_minus'] = False  # Для корректного отображения минуса


class ChartBuilder:
    """Генератор графиков для дашборда"""

    @staticmethod
    def create_bar_chart(df: pd.DataFrame, x_col: str, y_col: str, title: str, x_label: str, y_label: str) -> Figure:
        """
        Создание столбчатой диаграммы

        Returns:
            Объект matplotlib.figure.Figure для встраивания в Tkinter
        """
        fig = Figure(figsize=(6, 4), dpi=100)
        ax = fig.add_subplot(111)

        # Построение столбчатой диаграммы
        bars = ax.bar(df[x_col].astype(str), df[y_col], color='#4C72B0', edgecolor='black', linewidth=0.5)

        # Добавление значений на столбцы
        for bar in bars:
            yval = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width()/2,
                yval + (yval * 0.02),
                f'{yval:,.0f}',
                ha='center',
                va='bottom',
                fontsize=9
            )

        ax.set_title(title, fontsize=12, fontweight='bold', pad=10)
        ax.set_xlabel(x_label, fontsize=10)
        ax.set_ylabel(y_label, fontsize=10)
        ax.tick_params(axis='x', rotation=45)
        ax.grid(axis='y', linestyle='--', alpha=0.7)

        fig.tight_layout()
        return fig

    @staticmethod
    def create_line_chart(df: pd.DataFrame, x_col: str, y_col: str, title: str, x_label: str, y_label: str) -> Figure:
        """
        Создание линейного графика динамики

        Returns:
            Объект matplotlib.figure.Figure для встраивания в Tkinter
        """
        fig = Figure(figsize=(6, 4), dpi=100)
        ax = fig.add_subplot(111)

        # Построение линейного графика с маркерами
        ax.plot(
            df[x_col].astype(str),
            df[y_col],
            marker='o',
            color='#C44E52',
            linewidth=2,
            markersize=6
        )

        # Заполнение области под графиком для наглядности
        ax.fill_between(df[x_col].astype(str), df[y_col], color='#C44E52', alpha=0.2)

        ax.set_title(title, fontsize=12, fontweight='bold', pad=10)
        ax.set_xlabel(x_label, fontsize=10)
        ax.set_ylabel(y_label, fontsize=10)
        ax.tick_params(axis='x', rotation=45)
        ax.grid(True, linestyle='--', alpha=0.7)

        fig.tight_layout()
        return fig

    @staticmethod
    def save_figure(fig: Figure, filepath: str):
        """
        Сохранение графика в файл (опционально, для экспорта в PNG)
        """
        fig.savefig(filepath, dpi=150, bbox_inches='tight')
