"""
Панель дашборда: KPI, сводные таблицы, графики (matplotlib), кнопки Plotly и прогнозирование
"""

import tkinter as tk
from tkinter import ttk, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib
import pandas as pd
import numpy as np
from core.theme import ThemeManager
from core.chart_palettes import ChartPalettes
from core.forecast import Forecaster
from core.plotly_charts import PlotlyCharts
from ui.chart_viewer import ChartViewer
from ui.plotly_viewer import PlotlyViewer

matplotlib.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans', 'sans-serif']
matplotlib.rcParams['axes.unicode_minus'] = False


class DashboardPanel:
    """Панель дашборда с KPI, таблицами, графиками и прогнозом"""

    def __init__(self, parent, main_window):
        self.parent = parent
        self.main_window = main_window
        self.frame = ttk.Frame(parent)
        self.theme_colors = ThemeManager.get_theme('light')
        self.chart_palette = ChartPalettes.get_palette('classic')

        self.monthly_df = None

        self._create_scrollable_area()

    def _create_scrollable_area(self):
        """Создание прокручиваемой области"""
        self.canvas = tk.Canvas(self.frame, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Привязываем прокрутку ко всем виджетам
        self._bind_mousewheel_to_all(self.scrollable_frame)

    def _bind_mousewheel_to_all(self, widget):
        """Рекурсивная привязка прокрутки ко всем виджетам"""
        widget.bind("<MouseWheel>", self._on_mousewheel, add="+")
        widget.bind("<Button-4>", self._on_mousewheel_linux_up, add="+")
        widget.bind("<Button-5>", self._on_mousewheel_linux_down, add="+")

        for child in widget.winfo_children():
            self._bind_mousewheel_to_all(child)

    def _on_mousewheel(self, event):
        """Прокрутка колёсиком мыши (Windows/Mac)"""
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _on_mousewheel_linux_up(self, event):
        """Прокрутка вверх (Linux)"""
        self.canvas.yview_scroll(-1, "units")

    def _on_mousewheel_linux_down(self, event):
        """Прокрутка вниз (Linux)"""
        self.canvas.yview_scroll(1, "units")

    def update_theme(self, theme_name: str):
        """Обновление темы"""
        self.theme_colors = ThemeManager.get_theme(theme_name)

    def update_palette(self, palette: dict):
        """Обновление палитры"""
        self.chart_palette = palette

    def update_dashboard(self, merged_df: pd.DataFrame, summaries: dict, kpi: dict):
        """Обновление дашборда"""
        self.theme_colors = self.main_window.theme_colors
        self.chart_palette = self.main_window.chart_palette
        self.monthly_df = summaries.get('by_month', pd.DataFrame())

        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        self._create_kpi_section(kpi)
        self._create_charts_section(summaries)
        self._create_summaries_section(summaries)

        # Перепривязываем прокрутку ко всем новым виджетам
        self._bind_mousewheel_to_all(self.scrollable_frame)

    def _create_kpi_section(self, kpi: dict):
        """Создание секции KPI-карточек"""
        kpi_frame = ttk.LabelFrame(self.scrollable_frame, text="📊 Ключевые показатели (KPI)", padding=15)
        kpi_frame.pack(fill='x', padx=10, pady=10)

        cards_frame = ttk.Frame(kpi_frame)
        cards_frame.pack(fill='x')

        cards_config = [
            {'title': 'Всего строк', 'value': str(kpi.get('total_rows', 0)), 'icon': '📋'},
            {'title': 'Продано единиц', 'value': f"{kpi.get('total_units_sold', 0):,}".replace(',', ' '), 'icon': '📦'},
            {'title': 'Общая выручка', 'value': f"{kpi.get('total_revenue', 0):,.2f} ₽".replace(',', ' '), 'icon': '💰'},
        ]

        if kpi.get('total_profit', 0) != 0:
            cards_config.append(
                {'title': 'Общая прибыль', 'value': f"{kpi.get('total_profit', 0):,.2f} ₽".replace(',', ' '),
                 'icon': '📈'})

        if kpi.get('avg_check', 0) != 0:
            cards_config.append(
                {'title': 'Средний чек', 'value': f"{kpi.get('avg_check', 0):,.2f} ₽".replace(',', ' '), 'icon': '🧾'})

        cards_config.append(
            {'title': 'Период', 'value': f"{kpi.get('date_min', '—')} — {kpi.get('date_max', '—')}", 'icon': '📅'})

        for card in cards_config:
            card_frame = ttk.Frame(cards_frame, relief='ridge', borderwidth=2)
            card_frame.pack(side='left', expand=True, fill='both', padx=5, pady=5)

            ttk.Label(card_frame, text=f"{card['icon']} {card['title']}", font=('Arial', 10, 'bold')).pack(pady=(10, 5))
            ttk.Label(card_frame, text=card['value'], font=('Arial', 14, 'bold'), wraplength=150,
                      justify='center').pack(pady=(0, 10))

    def _create_charts_section(self, summaries: dict):
        """Создание секции графиков"""
        charts_container = ttk.LabelFrame(self.scrollable_frame, text="📈 Графики (двойной клик — увеличить)",
                                          padding=15)
        charts_container.pack(fill='both', expand=True, padx=10, pady=10)

        has_product = not summaries.get('by_product', pd.DataFrame()).empty
        has_region = not summaries.get('by_region', pd.DataFrame()).empty
        has_month = not summaries.get('by_month', pd.DataFrame()).empty

        if not (has_product or has_region or has_month):
            ttk.Label(charts_container, text="Нет данных для графиков", font=('Arial', 12)).pack(expand=True)
            return

        if has_product and has_region:
            top_row = ttk.Frame(charts_container)
            top_row.pack(fill='both', expand=True, pady=(0, 10))

            left_frame = ttk.Frame(top_row)
            left_frame.pack(side='left', expand=True, fill='both', padx=(0, 5))
            self._create_bar_chart_inline(
                left_frame, summaries['by_product'],
                'Выручка по продуктам', 'product', 'revenue', 'Продукт'
            )

            right_frame = ttk.Frame(top_row)
            right_frame.pack(side='right', expand=True, fill='both', padx=(5, 0))
            self._create_bar_chart_inline(
                right_frame, summaries['by_region'],
                'Выручка по регионам', 'region', 'revenue', 'Регион'
            )
        elif has_product:
            self._create_bar_chart_inline(
                charts_container, summaries['by_product'],
                'Выручка по продуктам', 'product', 'revenue', 'Продукт'
            )
        elif has_region:
            self._create_bar_chart_inline(
                charts_container, summaries['by_region'],
                'Выручка по регионам', 'region', 'revenue', 'Регион'
            )

        if has_month:
            bottom_frame = ttk.Frame(charts_container)
            bottom_frame.pack(fill='both', expand=True)
            self._create_line_chart_inline(
                bottom_frame, summaries['by_month'],
                'Динамика выручки по месяцам', 'period', 'revenue', 'Период'
            )

            # Секция прогнозирования под графиком по месяцам
            self._create_forecast_section(bottom_frame, summaries['by_month'])

    def _create_forecast_section(self, parent, df_monthly: pd.DataFrame):
        """Создание секции прогнозирования"""
        self.forecast_frame = ttk.LabelFrame(parent, text="🔮 Прогнозирование (линейная регрессия)", padding=10)
        self.forecast_frame.pack(fill='x', pady=(15, 0))

        ctrl_frame = ttk.Frame(self.forecast_frame)
        ctrl_frame.pack(fill='x')

        ttk.Label(ctrl_frame, text="Горизонт прогноза:", font=('Arial', 10)).pack(side='left', padx=5)

        self.forecast_periods_var = tk.StringVar(value="3")
        periods_combo = ttk.Combobox(
            ctrl_frame,
            textvariable=self.forecast_periods_var,
            values=["1", "3", "6", "12"],
            state="readonly",
            width=5
        )
        periods_combo.pack(side='left', padx=5)
        ttk.Label(ctrl_frame, text="мес.", font=('Arial', 10)).pack(side='left')

        build_btn = ttk.Button(
            ctrl_frame,
            text="📈 Построить прогноз",
            command=lambda: self._build_forecast(df_monthly)
        )
        build_btn.pack(side='left', padx=20)

        self.forecast_results_frame = ttk.Frame(self.forecast_frame)
        self.forecast_results_frame.pack(fill='both', expand=True, pady=(10, 0))

        ttk.Label(
            self.forecast_results_frame,
            text="Нажмите 'Построить прогноз', чтобы увидеть будущие значения",
            font=('Arial', 10),
            foreground='gray'
        ).pack(expand=True)

    def _build_forecast(self, df_monthly: pd.DataFrame):
        """Построение и отображение прогноза"""
        if df_monthly.empty or len(df_monthly) < 2:
            messagebox.showwarning("Внимание", "Недостаточно данных для построения прогноза (нужно минимум 2 периода).")
            return

        periods = int(self.forecast_periods_var.get())

        forecast_df = Forecaster.linear_forecast(df_monthly, 'period', 'revenue', periods=periods, degree=1)
        accuracy = Forecaster.calculate_accuracy(df_monthly, 'period', 'revenue', degree=1)

        if forecast_df is None:
            messagebox.showerror("Ошибка", "Не удалось построить прогноз. Проверьте данные.")
            return

        for widget in self.forecast_results_frame.winfo_children():
            widget.destroy()

        acc_text = f"🎯 Точность модели (R²): {accuracy:.1%}"
        acc_color = "green" if accuracy > 0.8 else ("orange" if accuracy > 0.6 else "red")
        acc_label = ttk.Label(
            self.forecast_results_frame,
            text=acc_text,
            font=('Arial', 11, 'bold'),
            foreground=acc_color
        )
        acc_label.pack(anchor='w', pady=(0, 10))

        table_frame = ttk.LabelFrame(self.forecast_results_frame, text="Прогнозные значения", padding=10)
        table_frame.pack(fill='both', expand=True)

        forecast_only = forecast_df[forecast_df['type'] == 'forecast']

        tree = ttk.Treeview(table_frame, columns=('period', 'revenue'), show='headings',
                            height=min(len(forecast_only), 6))
        tree.heading('period', text='Период')
        tree.heading('revenue', text='Прогноз выручки (₽)')
        tree.column('period', width=150, anchor='center')
        tree.column('revenue', width=200, anchor='e')

        for _, row in forecast_only.iterrows():
            tree.insert('', 'end', values=(
                row['period'],
                f"{row['revenue_forecast']:,.2f} ₽".replace(',', ' ')
            ))

        tree.pack(fill='both', expand=True)

        self.main_window.set_status(f"✅ Прогноз на {periods} мес. построен. Точность: {accuracy:.1%}")

    def _create_bar_chart_inline(self, parent, df: pd.DataFrame, title: str, x_col: str, y_col: str, x_label: str):
        """Создание столбчатой диаграммы с кнопкой Plotly"""
        chart_frame = ttk.LabelFrame(parent, text=title, padding=5)
        chart_frame.pack(fill='both', expand=True)

        if df.empty:
            ttk.Label(chart_frame, text="Нет данных").pack(expand=True)
            return

        fig = Figure(figsize=(5, 3.5), dpi=100)
        ax = fig.add_subplot(111)

        bar_colors = self.chart_palette.get('bar_colors', ['#4C72B0'])
        text_color = self.theme_colors.get('text_primary', 'black')
        grid_color = self.theme_colors.get('chart_grid', '#E0E0E0')

        colors = [bar_colors[i % len(bar_colors)] for i in range(len(df))]

        bars = ax.bar(df[x_col].astype(str), df[y_col], color=colors, edgecolor=text_color, linewidth=0.5)

        for bar in bars:
            yval = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2, yval + (yval * 0.02),
                    f'{yval:,.0f}'.replace(',', ' '), ha='center', va='bottom', fontsize=8, color=text_color)

        ax.set_title(title, fontsize=11, fontweight='bold', pad=8, color=text_color)
        ax.set_xlabel(x_label, fontsize=9, color=text_color)
        ax.set_ylabel('Выручка (₽)', fontsize=9, color=text_color)
        ax.tick_params(axis='x', rotation=45, labelsize=8, colors=text_color)
        ax.tick_params(axis='y', colors=text_color)
        ax.grid(axis='y', linestyle='--', alpha=0.7, color=grid_color)
        ax.set_facecolor(self.theme_colors.get('chart_bg', 'white'))
        fig.patch.set_facecolor(self.theme_colors.get('chart_bg', 'white'))

        fig.tight_layout()

        canvas_widget = FigureCanvasTkAgg(fig, master=chart_frame)
        canvas_widget.draw()
        canvas_widget.get_tk_widget().pack(fill='both', expand=True)

        # Кнопка для открытия интерактивной версии
        btn_frame = ttk.Frame(chart_frame)
        btn_frame.pack(fill='x', pady=5)

        ttk.Button(
            btn_frame,
            text="📊 Открыть интерактивную версию",
            command=lambda: self._open_plotly_bar(df, x_col, y_col, title, x_label, 'Выручка (₽)', colors)
        ).pack(side='right')

        canvas_widget.get_tk_widget().bind(
            "<Double-Button-1>",
            lambda e: self._open_chart_viewer(
                chart_type='bar', df=df, x_col=x_col, y_col=y_col,
                x_label=x_label, y_label='Выручка (₽)', title=title, colors=colors
            )
        )

        canvas_widget.get_tk_widget().bind(
            "<Enter>",
            lambda e: self.main_window.set_status(f"🔍 Двойной клик для увеличения графика: {title}")
        )

    def _create_line_chart_inline(self, parent, df: pd.DataFrame, title: str, x_col: str, y_col: str, x_label: str):
        """Создание линейного графика с кнопкой Plotly"""
        chart_frame = ttk.LabelFrame(parent, text=title, padding=5)
        chart_frame.pack(fill='both', expand=True)

        if df.empty:
            ttk.Label(chart_frame, text="Нет данных").pack(expand=True)
            return

        fig = Figure(figsize=(10, 4), dpi=100)
        ax = fig.add_subplot(111)

        line_colors = self.chart_palette.get('line_colors', ['#C44E52'])
        line_color = line_colors[0]
        text_color = self.theme_colors.get('text_primary', 'black')
        grid_color = self.theme_colors.get('chart_grid', '#E0E0E0')

        ax.plot(df[x_col].astype(str), df[y_col], marker='o', color=line_color, linewidth=2, markersize=6)
        ax.fill_between(df[x_col].astype(str), df[y_col], color=line_color, alpha=0.2)

        ax.set_title(title, fontsize=11, fontweight='bold', pad=8, color=text_color)
        ax.set_xlabel(x_label, fontsize=9, color=text_color)
        ax.set_ylabel('Выручка (₽)', fontsize=9, color=text_color)
        ax.tick_params(axis='x', rotation=45, labelsize=8, colors=text_color)
        ax.tick_params(axis='y', colors=text_color)
        ax.grid(True, linestyle='--', alpha=0.7, color=grid_color)
        ax.set_facecolor(self.theme_colors.get('chart_bg', 'white'))
        fig.patch.set_facecolor(self.theme_colors.get('chart_bg', 'white'))

        fig.tight_layout()

        canvas_widget = FigureCanvasTkAgg(fig, master=chart_frame)
        canvas_widget.draw()
        canvas_widget.get_tk_widget().pack(fill='both', expand=True)

        # Кнопка для открытия интерактивной версии
        btn_frame = ttk.Frame(chart_frame)
        btn_frame.pack(fill='x', pady=5)

        ttk.Button(
            btn_frame,
            text="📊 Открыть интерактивную версию",
            command=lambda: self._open_plotly_line(df, x_col, y_col, title, x_label, 'Выручка (₽)', line_color)
        ).pack(side='right')

        canvas_widget.get_tk_widget().bind(
            "<Double-Button-1>",
            lambda e: self._open_chart_viewer(
                chart_type='line', df=df, x_col=x_col, y_col=y_col,
                x_label=x_label, y_label='Выручка (₽)', title=title, colors=[line_color]
            )
        )

        canvas_widget.get_tk_widget().bind(
            "<Enter>",
            lambda e: self.main_window.set_status(f"🔍 Двойной клик для увеличения графика: {title}")
        )

    def _open_plotly_bar(self, df, x_col, y_col, title, x_label, y_label, colors):
        """Открыть интерактивную столбчатую диаграмму"""
        try:
            fig = PlotlyCharts.create_bar_chart(df, x_col, y_col, title, x_label, y_label, colors)
            PlotlyViewer.show_chart_async(fig, title)
            self.main_window.set_status(f"📊 Интерактивный график открыт: {title}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось открыть интерактивный график:\n{e}")

    def _open_plotly_line(self, df, x_col, y_col, title, x_label, y_label, color):
        """Открыть интерактивный линейный график"""
        try:
            fig = PlotlyCharts.create_line_chart(df, x_col, y_col, title, x_label, y_label, color)
            PlotlyViewer.show_chart_async(fig, title)
            self.main_window.set_status(f"📊 Интерактивный график открыт: {title}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось открыть интерактивный график:\n{e}")

    def _open_chart_viewer(self, chart_type: str, df: pd.DataFrame,
                           x_col: str, y_col: str, x_label: str, y_label: str,
                           title: str, colors: list):
        """Открыть график в отдельном окне с навигацией"""
        chart_data = {
            'chart_type': chart_type,
            'df': df,
            'x_col': x_col,
            'y_col': y_col,
            'x_label': x_label,
            'y_label': y_label,
            'title': title,
            'colors': colors,
            'theme_colors': self.theme_colors
        }
        ChartViewer(self.main_window.root, chart_data)

    def _create_summaries_section(self, summaries: dict):
        """Создание секции сводных таблиц"""
        summaries_frame = ttk.LabelFrame(self.scrollable_frame, text="📑 Сводные таблицы", padding=15)
        summaries_frame.pack(fill='both', expand=True, padx=10, pady=10)

        tables_notebook = ttk.Notebook(summaries_frame)
        tables_notebook.pack(fill='both', expand=True)

        has_profit = 'profit' in summaries.get('by_product', pd.DataFrame()).columns
        has_manager = not summaries.get('by_manager', pd.DataFrame()).empty
        has_customer = not summaries.get('by_customer', pd.DataFrame()).empty

        if not summaries.get('by_product', pd.DataFrame()).empty:
            cols = ['product', 'revenue']
            headers = ['Продукт', 'Выручка (₽)']
            if has_profit:
                cols.append('profit')
                headers.append('Прибыль (₽)')
            self._create_table_tab(tables_notebook, 'По продуктам', summaries['by_product'], columns=cols,
                                   headers=headers)

        if not summaries.get('by_region', pd.DataFrame()).empty:
            cols = ['region', 'revenue']
            headers = ['Регион', 'Выручка (₽)']
            if has_profit:
                cols.append('profit')
                headers.append('Прибыль (₽)')
            self._create_table_tab(tables_notebook, 'По регионам', summaries['by_region'], columns=cols,
                                   headers=headers)

        if has_manager:
            cols = ['manager', 'revenue']
            headers = ['Менеджер', 'Выручка (₽)']
            if has_profit:
                cols.append('profit')
                headers.append('Прибыль (₽)')
            self._create_table_tab(tables_notebook, 'По менеджерам', summaries['by_manager'], columns=cols,
                                   headers=headers)

        if has_customer:
            cols = ['customer', 'revenue']
            headers = ['Клиент', 'Выручка (₽)']
            if has_profit:
                cols.append('profit')
                headers.append('Прибыль (₽)')
            self._create_table_tab(tables_notebook, 'По клиентам', summaries['by_customer'], columns=cols,
                                   headers=headers)

        if not summaries.get('by_month', pd.DataFrame()).empty:
            cols = ['period', 'revenue']
            headers = ['Период', 'Выручка (₽)']
            if has_profit:
                cols.append('profit')
                headers.append('Прибыль (₽)')
            self._create_table_tab(tables_notebook, 'По месяцам', summaries['by_month'], columns=cols, headers=headers)

        if not tables_notebook.tabs():
            ttk.Label(tables_notebook, text="Нет данных для отображения", font=('Arial', 12)).pack(expand=True)

    def _create_table_tab(self, parent, title: str, df: pd.DataFrame, columns: list, headers: list):
        """Создание вкладки с таблицей"""
        tab_frame = ttk.Frame(parent)
        parent.add(tab_frame, text=title)

        if df.empty:
            ttk.Label(tab_frame, text="Нет данных для отображения", font=('Arial', 12)).pack(expand=True)
            return

        tree = ttk.Treeview(tab_frame, columns=columns, show='headings', height=min(len(df), 15))

        for col, header in zip(columns, headers):
            tree.heading(col, text=header)
            tree.column(col, width=150, anchor='center' if col != columns[0] else 'w')

        for _, row in df.iterrows():
            values = []
            for col in columns:
                val = row[col]
                if col in ['revenue', 'profit']:
                    values.append(f"{val:,.2f} ₽".replace(',', ' '))
                else:
                    values.append(str(val))
            tree.insert('', 'end', values=values)

        scrollbar = ttk.Scrollbar(tab_frame, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)

        tree.pack(side='left', fill='both', expand=True, padx=5, pady=5)
        scrollbar.pack(side='right', fill='y', pady=5)