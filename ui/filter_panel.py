"""
Панель фильтрации данных на дашборде
"""

import tkinter as tk
from tkinter import ttk
import pandas as pd


class FilterPanel:
    """Панель для фильтрации данных по дате, региону и продукту"""

    def __init__(self, parent, main_window):
        self.parent = parent
        self.main_window = main_window
        self.frame = ttk.Frame(parent)

        self.region_var = tk.StringVar(value="Все")
        self.product_var = tk.StringVar(value="Все")

        self._create_widgets()

    def _create_widgets(self):
        """Создание виджетов панели фильтров"""
        filter_frame = ttk.LabelFrame(self.frame, text="🔍 Фильтры", padding=10)
        filter_frame.pack(fill='x', padx=10, pady=5)

        # Фильтр по региону
        ttk.Label(filter_frame, text="Регион:", font=('Arial', 10)).pack(side='left', padx=(0, 5))
        self.region_combo = ttk.Combobox(
            filter_frame,
            textvariable=self.region_var,
            state='readonly',
            width=20
        )
        self.region_combo.pack(side='left', padx=(0, 15))
        self.region_combo.bind('<<ComboboxSelected>>', self._apply_filters)

        # Фильтр по продукту
        ttk.Label(filter_frame, text="Продукт:", font=('Arial', 10)).pack(side='left', padx=(0, 5))
        self.product_combo = ttk.Combobox(
            filter_frame,
            textvariable=self.product_var,
            state='readonly',
            width=20
        )
        self.product_combo.pack(side='left', padx=(0, 15))
        self.product_combo.bind('<<ComboboxSelected>>', self._apply_filters)

        # Кнопка сброса
        reset_btn = ttk.Button(
            filter_frame,
            text="🔄 Сбросить",
            command=self._reset_filters
        )
        reset_btn.pack(side='right')

    def update_options(self, df: pd.DataFrame):
        """Обновление списков фильтров на основе данных"""
        if df is None or df.empty:
            return

        # Уникальные регионы
        regions = ["Все"] + sorted(df['region'].dropna().unique().tolist())
        self.region_combo['values'] = regions
        self.region_var.set("Все")

        # Уникальные продукты
        products = ["Все"] + sorted(df['product'].dropna().unique().tolist())
        self.product_combo['values'] = products
        self.product_var.set("Все")

    def _apply_filters(self, event=None):
        """Применение фильтров и обновление дашборда"""
        if self.main_window.merged_data is None:
            return

        df = self.main_window.merged_data.copy()

        # Фильтр по региону
        if self.region_var.get() != "Все":
            df = df[df['region'] == self.region_var.get()]

        # Фильтр по продукту
        if self.product_var.get() != "Все":
            df = df[df['product'] == self.product_var.get()]

        # Пересчет KPI и сводок для отфильтрованных данных
        from reports.kpi import KPIReporter
        from reports.summaries import SummaryReporter

        kpi = KPIReporter.calculate(df)
        summaries = SummaryReporter.generate_all(df)

        # Обновление дашборда
        self.main_window.dashboard_panel.update_dashboard(df, summaries, kpi)

        self.main_window.set_status(
            f"🔍 Применены фильтры: Регион={self.region_var.get()}, Продукт={self.product_var.get()}")

    def _reset_filters(self):
        """Сброс фильтров к значениям по умолчанию"""
        self.region_var.set("Все")
        self.product_var.set("Все")

        if self.main_window.merged_data is not None:
            kpi = self.main_window.kpi
            summaries = self.main_window.summaries
            self.main_window.dashboard_panel.update_dashboard(self.main_window.merged_data, summaries, kpi)
            self.main_window.set_status("🔄 Фильтры сброшены")