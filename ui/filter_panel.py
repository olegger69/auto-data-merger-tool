"""
Панель фильтров для дашборда
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from core.filter import DataFilter


class FilterPanel:
    """Панель фильтров: регион, продукт, даты"""

    def __init__(self, parent, main_window):
        self.parent = parent
        self.main_window = main_window
        self.frame = ttk.Frame(parent)

        # Хранение выбранных значений
        self.selected_regions = []
        self.selected_products = []

        self._create_widgets()

    def _create_widgets(self):
        """Создание виджетов панели фильтров"""
        # Заголовок
        header = ttk.Label(
            self.frame,
            text="🔍 Фильтры",
            font=('Arial', 12, 'bold')
        )
        header.pack(anchor='w', padx=10, pady=(10, 5))

        # Основной контейнер для фильтров
        filters_frame = ttk.Frame(self.frame)
        filters_frame.pack(fill='x', padx=10, pady=5)

        # 1. Фильтр по регионам
        region_frame = ttk.LabelFrame(filters_frame, text="Регион", padding=5)
        region_frame.pack(side='left', expand=True, fill='both', padx=5)

        self.region_listbox = tk.Listbox(
            region_frame,
            selectmode='multiple',
            height=4,
            font=('Arial', 9),
            exportselection=0  # Сохраняет выделение при переходе к другому виджету
        )
        region_scrollbar = ttk.Scrollbar(
            region_frame,
            orient='vertical',
            command=self.region_listbox.yview
        )
        self.region_listbox.configure(yscrollcommand=region_scrollbar.set)

        self.region_listbox.pack(side='left', fill='both', expand=True)
        region_scrollbar.pack(side='right', fill='y')

        # 2. Фильтр по продуктам
        product_frame = ttk.LabelFrame(filters_frame, text="Продукт", padding=5)
        product_frame.pack(side='left', expand=True, fill='both', padx=5)

        self.product_listbox = tk.Listbox(
            product_frame,
            selectmode='multiple',
            height=4,
            font=('Arial', 9),
            exportselection=0  # Сохраняет выделение при переходе к другому виджету
        )
        product_scrollbar = ttk.Scrollbar(
            product_frame,
            orient='vertical',
            command=self.product_listbox.yview
        )
        self.product_listbox.configure(yscrollcommand=product_scrollbar.set)

        self.product_listbox.pack(side='left', fill='both', expand=True)
        product_scrollbar.pack(side='right', fill='y')

        # 3. Фильтр по датам
        date_frame = ttk.LabelFrame(filters_frame, text="Период", padding=5)
        date_frame.pack(side='left', expand=True, fill='both', padx=5)

        date_inner = ttk.Frame(date_frame)
        date_inner.pack(fill='x')

        ttk.Label(date_inner, text="С:", font=('Arial', 9)).pack(side='left', padx=(0, 5))
        self.date_from_entry = ttk.Entry(date_inner, width=12)
        self.date_from_entry.pack(side='left', padx=(0, 10))
        self.date_from_entry.insert(0, 'YYYY-MM-DD')
        self.date_from_entry.bind('<FocusIn>', self._clear_placeholder_from)

        ttk.Label(date_inner, text="По:", font=('Arial', 9)).pack(side='left', padx=(0, 5))
        self.date_to_entry = ttk.Entry(date_inner, width=12)
        self.date_to_entry.pack(side='left')
        self.date_to_entry.insert(0, 'YYYY-MM-DD')
        self.date_to_entry.bind('<FocusIn>', self._clear_placeholder_to)

        # Кнопки управления
        buttons_frame = ttk.Frame(self.frame)
        buttons_frame.pack(fill='x', padx=10, pady=5)

        apply_btn = ttk.Button(
            buttons_frame,
            text="✅ Применить фильтры",
            command=self._apply_filters
        )
        apply_btn.pack(side='left', padx=5)

        reset_btn = ttk.Button(
            buttons_frame,
            text="🔄 Сбросить",
            command=self._reset_filters
        )
        reset_btn.pack(side='left', padx=5)

        # Разделитель
        ttk.Separator(self.frame, orient='horizontal').pack(fill='x', pady=5)

    def _clear_placeholder_from(self, event):
        """Очистка placeholder при фокусе"""
        if self.date_from_entry.get() == 'YYYY-MM-DD':
            self.date_from_entry.delete(0, 'end')

    def _clear_placeholder_to(self, event):
        """Очистка placeholder при фокусе"""
        if self.date_to_entry.get() == 'YYYY-MM-DD':
            self.date_to_entry.delete(0, 'end')

    def update_options(self, df):
        """
        Обновление списков регионов и продуктов при загрузке новых данных

        Args:
            df: DataFrame с данными
        """
        # Очистка текущих списков
        self.region_listbox.delete(0, 'end')
        self.product_listbox.delete(0, 'end')

        # Заполнение регионов
        regions = DataFilter.get_unique_values(df, 'region')
        for region in regions:
            self.region_listbox.insert('end', region)

        # Заполнение продуктов
        products = DataFilter.get_unique_values(df, 'product')
        for product in products:
            self.product_listbox.insert('end', product)

        # Установка диапазона дат
        min_date, max_date = DataFilter.get_date_range(df)
        if min_date and max_date:
            self.date_from_entry.delete(0, 'end')
            self.date_from_entry.insert(0, min_date)
            self.date_to_entry.delete(0, 'end')
            self.date_to_entry.insert(0, max_date)

        # Сброс выбранных значений
        self.selected_regions = []
        self.selected_products = []

        self.main_window.set_status("Фильтры обновлены")

    def _apply_filters(self):
        """Применение фильтров"""
        # Получение выбранных регионов
        selected_region_indices = self.region_listbox.curselection()
        self.selected_regions = [
            self.region_listbox.get(i) for i in selected_region_indices
        ]

        # Получение выбранных продуктов
        selected_product_indices = self.product_listbox.curselection()
        self.selected_products = [
            self.product_listbox.get(i) for i in selected_product_indices
        ]

        # Получение дат
        date_from = self.date_from_entry.get().strip()
        date_to = self.date_to_entry.get().strip()

        # Валидация дат
        if date_from and date_from != 'YYYY-MM-DD':
            try:
                datetime.strptime(date_from, '%Y-%m-%d')
            except ValueError:
                messagebox.showerror(
                    "Ошибка",
                    "Неверный формат даты 'С'. Используйте формат YYYY-MM-DD"
                )
                return

        if date_to and date_to != 'YYYY-MM-DD':
            try:
                datetime.strptime(date_to, '%Y-%m-%d')
            except ValueError:
                messagebox.showerror(
                    "Ошибка",
                    "Неверный формат даты 'По'. Используйте формат YYYY-MM-DD"
                )
                return

        # Если даты не заполнены, не применяем фильтр по ним
        if date_from == 'YYYY-MM-DD':
            date_from = None
        if date_to == 'YYYY-MM-DD':
            date_to = None

        # Применение фильтра
        if self.main_window.merged_data is not None:
            filtered_df = DataFilter.apply(
                self.main_window.merged_data,
                regions=self.selected_regions if self.selected_regions else None,
                products=self.selected_products if self.selected_products else None,
                date_from=date_from,
                date_to=date_to
            )

            # Пересчёт сводок и KPI для отфильтрованных данных
            from reports.kpi import KPIReporter
            from reports.summaries import SummaryReporter

            summaries = SummaryReporter.generate_all(filtered_df)
            kpi = KPIReporter.calculate(filtered_df)

            # Обновление дашборда
            self.main_window.dashboard_panel.update_dashboard(
                filtered_df, summaries, kpi
            )

            # Обновление статусной строки
            filter_desc = []
            if self.selected_regions:
                filter_desc.append(f"регионы: {', '.join(self.selected_regions)}")
            if self.selected_products:
                filter_desc.append(f"продукты: {', '.join(self.selected_products)}")
            if date_from or date_to:
                filter_desc.append(f"период: {date_from or '...'} — {date_to or '...'}")

            if filter_desc:
                status = f"Фильтр применён: {'; '.join(filter_desc)}"
            else:
                status = "Показаны все данные"

            self.main_window.set_status(status)
        else:
            messagebox.showwarning("Внимание", "Сначала загрузите и объедините файлы")

    def _reset_filters(self):
        """Сброс всех фильтров"""
        # Сброс выделения в списках
        self.region_listbox.selection_clear(0, 'end')
        self.product_listbox.selection_clear(0, 'end')

        # Сброс дат
        self.date_from_entry.delete(0, 'end')
        self.date_from_entry.insert(0, 'YYYY-MM-DD')
        self.date_to_entry.delete(0, 'end')
        self.date_to_entry.insert(0, 'YYYY-MM-DD')

        # Сброс выбранных значений
        self.selected_regions = []
        self.selected_products = []

        # Если есть данные, показать все
        if self.main_window.merged_data is not None:
            from reports.kpi import KPIReporter
            from reports.summaries import SummaryReporter

            summaries = SummaryReporter.generate_all(self.main_window.merged_data)
            kpi = KPIReporter.calculate(self.main_window.merged_data)

            self.main_window.dashboard_panel.update_dashboard(
                self.main_window.merged_data, summaries, kpi
            )

        self.main_window.set_status("Фильтры сброшены")