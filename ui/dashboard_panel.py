"""
Панель дашборда: KPI, сводные таблицы и графики
"""

import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib
import pandas as pd

# Настройка шрифтов для кириллицы
matplotlib.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans', 'sans-serif']
matplotlib.rcParams['axes.unicode_minus'] = False


class DashboardPanel:
    """Панель дашборда с KPI, таблицами и графиками"""

    def __init__(self, parent, main_window):
        self.parent = parent
        self.main_window = main_window
        self.frame = ttk.Frame(parent)

        # Создаём прокручиваемую область
        self._create_scrollable_area()

    def _create_scrollable_area(self):
        """Создание прокручиваемой области для дашборда"""
        # Canvas для прокрутки
        self.canvas = tk.Canvas(self.frame, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)

        # Привязка колёсика мыши
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def _on_mousewheel(self, event):
        """Прокрутка колёсиком мыши"""
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def update_dashboard(self, merged_df: pd.DataFrame, summaries: dict, kpi: dict):
        """
        Обновление дашборда новыми данными

        Args:
            merged_df: Объединённый DataFrame
            summaries: Словарь со сводными таблицами
            kpi: Словарь с KPI-метриками
        """
        # Очищаем предыдущее содержимое
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        # 1. Секция KPI
        self._create_kpi_section(kpi)

        # 2. Секция сводных таблиц
        self._create_summaries_section(summaries)

        # 3. Секция графиков
        self._create_charts_section(summaries)

    def _create_kpi_section(self, kpi: dict):
        """Создание секции KPI-карточек"""
        kpi_frame = ttk.LabelFrame(self.scrollable_frame, text="📊 Ключевые показатели (KPI)", padding=15)
        kpi_frame.pack(fill='x', padx=10, pady=10)

        # Создаём 4 карточки в ряд
        cards_frame = ttk.Frame(kpi_frame)
        cards_frame.pack(fill='x')

        # Конфигурация карточек
        cards_config = [
            {
                'title': 'Всего строк',
                'value': str(kpi.get('total_rows', 0)),
                'icon': '📋'
            },
            {
                'title': 'Продано единиц',
                'value': f"{kpi.get('total_units_sold', 0):,}".replace(',', ' '),
                'icon': '📦'
            },
            {
                'title': 'Общая выручка',
                'value': f"{kpi.get('total_revenue', 0):,.2f} ₽".replace(',', ' '),
                'icon': '💰'
            },
            {
                'title': 'Период',
                'value': f"{kpi.get('date_min', '—')} — {kpi.get('date_max', '—')}",
                'icon': '📅'
            }
        ]

        for i, card in enumerate(cards_config):
            card_frame = ttk.Frame(cards_frame, relief='ridge', borderwidth=2)
            card_frame.pack(side='left', expand=True, fill='both', padx=5, pady=5)

            ttk.Label(
                card_frame,
                text=f"{card['icon']} {card['title']}",
                font=('Arial', 10, 'bold')
            ).pack(pady=(10, 5))

            ttk.Label(
                card_frame,
                text=card['value'],
                font=('Arial', 14, 'bold'),
                wraplength=150,
                justify='center'
            ).pack(pady=(0, 10))

    def _create_summaries_section(self, summaries: dict):
        """Создание секции сводных таблиц"""
        summaries_frame = ttk.LabelFrame(self.scrollable_frame, text="📑 Сводные таблицы", padding=15)
        summaries_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Создаём Notebook для таблиц
        tables_notebook = ttk.Notebook(summaries_frame)
        tables_notebook.pack(fill='both', expand=True)

        # Таблица 1: По продуктам
        self._create_table_tab(
            tables_notebook,
            'По продуктам',
            summaries.get('by_product', pd.DataFrame()),
            columns=['product', 'revenue'],
            headers=['Продукт', 'Выручка (₽)']
        )

        # Таблица 2: По регионам
        self._create_table_tab(
            tables_notebook,
            'По регионам',
            summaries.get('by_region', pd.DataFrame()),
            columns=['region', 'revenue'],
            headers=['Регион', 'Выручка (₽)']
        )

        # Таблица 3: По месяцам
        self._create_table_tab(
            tables_notebook,
            'По месяцам',
            summaries.get('by_month', pd.DataFrame()),
            columns=['period', 'revenue'],
            headers=['Период', 'Выручка (₽)']
        )

    def _create_table_tab(self, parent, title: str, df: pd.DataFrame, columns: list, headers: list):
        """Создание вкладки с таблицей"""
        tab_frame = ttk.Frame(parent)
        parent.add(tab_frame, text=title)

        if df.empty:
            ttk.Label(
                tab_frame,
                text="Нет данных для отображения",
                font=('Arial', 12)
            ).pack(expand=True)
            return

        # Treeview для таблицы
        tree = ttk.Treeview(
            tab_frame,
            columns=columns,
            show='headings',
            height=min(len(df), 15)
        )

        for col, header in zip(columns, headers):
            tree.heading(col, text=header)
            tree.column(col, width=150, anchor='center' if col != columns[0] else 'w')

        # Заполнение данными
        for _, row in df.iterrows():
            values = []
            for col in columns:
                val = row[col]
                if col == 'revenue':
                    values.append(f"{val:,.2f} ₽".replace(',', ' '))
                else:
                    values.append(str(val))
            tree.insert('', 'end', values=values)

        # Скроллбар
        scrollbar = ttk.Scrollbar(tab_frame, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)

        tree.pack(side='left', fill='both', expand=True, padx=5, pady=5)
        scrollbar.pack(side='right', fill='y', pady=5)

    def _create_charts_section(self, summaries: dict):
        """Создание секции графиков"""
        charts_frame = ttk.LabelFrame(self.scrollable_frame, text="📈 Графики", padding=15)
        charts_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # График 1: По продуктам (столбчатая)
        self._create_bar_chart(
            charts_frame,
            summaries.get('by_product', pd.DataFrame()),
            'Выручка по продуктам',
            'product',
            'revenue',
            'Продукт'
        )

        # График 2: По регионам (столбчатая)
        self._create_bar_chart(
            charts_frame,
            summaries.get('by_region', pd.DataFrame()),
            'Выручка по регионам',
            'region',
            'revenue',
            'Регион'
        )

        # График 3: По месяцам (линейный)
        self._create_line_chart(
            charts_frame,
            summaries.get('by_month', pd.DataFrame()),
            'Динамика выручки по месяцам',
            'period',
            'revenue',
            'Период'
        )

    def _create_bar_chart(self, parent, df: pd.DataFrame, title: str, x_col: str, y_col: str, x_label: str):
        """Создание столбчатой диаграммы"""
        chart_frame = ttk.LabelFrame(parent, text=title, padding=10)
        chart_frame.pack(fill='both', expand=True, padx=5, pady=10)

        if df.empty:
            ttk.Label(chart_frame, text="Нет данных").pack(expand=True)
            return

        fig = Figure(figsize=(8, 4), dpi=100)
        ax = fig.add_subplot(111)

        bars = ax.bar(df[x_col].astype(str), df[y_col], color='#4C72B0', edgecolor='black', linewidth=0.5)

        for bar in bars:
            yval = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width()/2,
                yval + (yval * 0.02),
                f'{yval:,.0f}'.replace(',', ' '),
                ha='center',
                va='bottom',
                fontsize=9
            )

        ax.set_title(title, fontsize=12, fontweight='bold', pad=10)
        ax.set_xlabel(x_label, fontsize=10)
        ax.set_ylabel('Выручка (₽)', fontsize=10)
        ax.tick_params(axis='x', rotation=45)
        ax.grid(axis='y', linestyle='--', alpha=0.7)

        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)

    def _create_line_chart(self, parent, df: pd.DataFrame, title: str, x_col: str, y_col: str, x_label: str):
        """Создание линейного графика"""
        chart_frame = ttk.LabelFrame(parent, text=title, padding=10)
        chart_frame.pack(fill='both', expand=True, padx=5, pady=10)

        if df.empty:
            ttk.Label(chart_frame, text="Нет данных").pack(expand=True)
            return

        fig = Figure(figsize=(8, 4), dpi=100)
        ax = fig.add_subplot(111)

        ax.plot(
            df[x_col].astype(str),
            df[y_col],
            marker='o',
            color='#C44E52',
            linewidth=2,
            markersize=6
        )
        ax.fill_between(df[x_col].astype(str), df[y_col], color='#C44E52', alpha=0.2)

        ax.set_title(title, fontsize=12, fontweight='bold', pad=10)
        ax.set_xlabel(x_label, fontsize=10)
        ax.set_ylabel('Выручка (₽)', fontsize=10)
        ax.tick_params(axis='x', rotation=45)
        ax.grid(True, linestyle='--', alpha=0.7)

        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)