"""
Панель сравнения периодов
"""

import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
from reports.period_comparison import PeriodComparator


class ComparisonPanel:
    """Панель для сравнения метрик между двумя периодами"""

    def __init__(self, parent, main_window):
        self.parent = parent
        self.main_window = main_window
        self.frame = ttk.Frame(parent)
        self._create_widgets()

    def _create_widgets(self):
        """Создание виджетов панели сравнения"""
        # Заголовок
        header = ttk.Label(
            self.frame,
            text="📈 Сравнение периодов",
            font=('Arial', 16, 'bold')
        )
        header.pack(pady=15)

        # Рамка для ввода дат
        dates_frame = ttk.LabelFrame(self.frame, text="Выберите периоды для сравнения", padding=15)
        dates_frame.pack(fill='x', padx=20, pady=10)

        # Период 1
        p1_frame = ttk.Frame(dates_frame)
        p1_frame.pack(fill='x', pady=5)
        ttk.Label(p1_frame, text="Период 1 (Базовый):", font=('Arial', 10, 'bold'), width=20).pack(side='left')

        self.p1_start = ttk.Entry(p1_frame, width=12)
        self.p1_start.pack(side='left', padx=5)
        self.p1_start.insert(0, 'YYYY-MM-DD')
        self.p1_start.bind('<FocusIn>', self._clear_placeholder)

        ttk.Label(p1_frame, text="по", font=('Arial', 10)).pack(side='left', padx=5)

        self.p1_end = ttk.Entry(p1_frame, width=12)
        self.p1_end.pack(side='left', padx=5)
        self.p1_end.insert(0, 'YYYY-MM-DD')
        self.p1_end.bind('<FocusIn>', self._clear_placeholder)

        # Период 2
        p2_frame = ttk.Frame(dates_frame)
        p2_frame.pack(fill='x', pady=5)
        ttk.Label(p2_frame, text="Период 2 (Сравниваемый):", font=('Arial', 10, 'bold'), width=20).pack(side='left')

        self.p2_start = ttk.Entry(p2_frame, width=12)
        self.p2_start.pack(side='left', padx=5)
        self.p2_start.insert(0, 'YYYY-MM-DD')
        self.p2_start.bind('<FocusIn>', self._clear_placeholder)

        ttk.Label(p2_frame, text="по", font=('Arial', 10)).pack(side='left', padx=5)

        self.p2_end = ttk.Entry(p2_frame, width=12)
        self.p2_end.pack(side='left', padx=5)
        self.p2_end.insert(0, 'YYYY-MM-DD')
        self.p2_end.bind('<FocusIn>', self._clear_placeholder)

        # Кнопки быстрого выбора
        quick_btn_frame = ttk.Frame(dates_frame)
        quick_btn_frame.pack(fill='x', pady=10)

        ttk.Button(
            quick_btn_frame,
            text="📅 Прошлый месяц vs Текущий",
            command=self._set_last_months
        ).pack(side='left', padx=5)

        ttk.Button(
            quick_btn_frame,
            text="📅 Прошлый год vs Текущий год",
            command=self._set_last_years
        ).pack(side='left', padx=5)

        # Кнопка сравнения
        cmp_btn = ttk.Button(
            self.frame,
            text="📊 Сравнить периоды",
            command=self._compare
        )
        cmp_btn.pack(pady=10)

        # Рамка для результатов
        self.results_frame = ttk.Frame(self.frame)
        self.results_frame.pack(fill='both', expand=True, padx=20, pady=10)

        self._show_placeholder()

    def _clear_placeholder(self, event):
        """Очистка placeholder при фокусе"""
        if event.widget.get() == 'YYYY-MM-DD':
            event.widget.delete(0, 'end')

    def _set_last_months(self):
        """Автоматическая установка прошлого и текущего месяца"""
        if self.main_window.merged_data is None or self.main_window.merged_data.empty:
            messagebox.showwarning("Внимание", "Сначала загрузите данные")
            return

        max_date = self.main_window.merged_data['date'].max()
        last_month_start = max_date.replace(day=1)

        if last_month_start.month == 1:
            prev_month_start = last_month_start.replace(year=last_month_start.year - 1, month=12)
        else:
            prev_month_start = last_month_start.replace(month=last_month_start.month - 1)

        prev_month_end = last_month_start - pd.Timedelta(days=1)

        self.p1_start.delete(0, 'end')
        self.p1_start.insert(0, prev_month_start.strftime('%Y-%m-%d'))
        self.p1_end.delete(0, 'end')
        self.p1_end.insert(0, prev_month_end.strftime('%Y-%m-%d'))

        self.p2_start.delete(0, 'end')
        self.p2_start.insert(0, last_month_start.strftime('%Y-%m-%d'))
        self.p2_end.delete(0, 'end')
        self.p2_end.insert(0, max_date.strftime('%Y-%m-%d'))

    def _set_last_years(self):
        """Автоматическая установка прошлого и текущего года"""
        if self.main_window.merged_data is None or self.main_window.merged_data.empty:
            messagebox.showwarning("Внимание", "Сначала загрузите данные")
            return

        max_date = self.main_window.merged_data['date'].max()
        curr_year_start = max_date.replace(month=1, day=1)
        prev_year_start = curr_year_start.replace(year=curr_year_start.year - 1)
        prev_year_end = curr_year_start - pd.Timedelta(days=1)

        self.p1_start.delete(0, 'end')
        self.p1_start.insert(0, prev_year_start.strftime('%Y-%m-%d'))
        self.p1_end.delete(0, 'end')
        self.p1_end.insert(0, prev_year_end.strftime('%Y-%m-%d'))

        self.p2_start.delete(0, 'end')
        self.p2_start.insert(0, curr_year_start.strftime('%Y-%m-%d'))
        self.p2_end.delete(0, 'end')
        self.p2_end.insert(0, max_date.strftime('%Y-%m-%d'))

    def _show_placeholder(self):
        """Показать заглушку, пока нет результатов"""
        for widget in self.results_frame.winfo_children():
            widget.destroy()
        ttk.Label(
            self.results_frame,
            text="Выберите периоды и нажмите 'Сравнить'",
            font=('Arial', 12),
            foreground='gray'
        ).pack(expand=True)

    def _compare(self):
        """Запуск сравнения"""
        if self.main_window.merged_data is None:
            messagebox.showwarning("Внимание", "Сначала загрузите и объедините данные")
            return

        p1_start = self.p1_start.get().strip()
        p1_end = self.p1_end.get().strip()
        p2_start = self.p2_start.get().strip()
        p2_end = self.p2_end.get().strip()

        if 'YYYY' in p1_start or 'YYYY' in p1_end or 'YYYY' in p2_start or 'YYYY' in p2_end:
            messagebox.showwarning("Внимание", "Пожалуйста, введите корректные даты в формате YYYY-MM-DD")
            return

        try:
            comparison = PeriodComparator.compare_periods(
                self.main_window.merged_data,
                p1_start, p1_end,
                p2_start, p2_end
            )

            if not comparison:
                messagebox.showwarning("Внимание", "Нет данных для выбранных периодов")
                return

            self._display_results(comparison)

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка сравнения: {e}")

    def _display_results(self, comparison):
        """Отображение результатов сравнения в таблице"""
        for widget in self.results_frame.winfo_children():
            widget.destroy()

        columns = ('metric', 'p1', 'p2', 'abs_change', 'pct_change')
        tree = ttk.Treeview(self.results_frame, columns=columns, show='headings', height=8)

        tree.heading('metric', text='Показатель')
        tree.heading('p1', text='Период 1')
        tree.heading('p2', text='Период 2')
        tree.heading('abs_change', text='Абс. изменение')
        tree.heading('pct_change', text='Изменение %')

        tree.column('metric', width=180, anchor='w')
        tree.column('p1', width=120, anchor='e')
        tree.column('p2', width=120, anchor='e')
        tree.column('abs_change', width=130, anchor='e')
        tree.column('pct_change', width=120, anchor='e')

        metrics_map = {
            'revenue': '💰 Выручка',
            'profit': '📈 Прибыль',
            'units_sold': '📦 Продано единиц',
            'transactions': '📋 Транзакций',
            'avg_check': '🧾 Средний чек'
        }

        for key, label in metrics_map.items():
            val1 = comparison['period1'].get(key, 0)
            val2 = comparison['period2'].get(key, 0)
            change = comparison['changes'].get(key, {})

            abs_val = change.get('absolute', 0)
            pct_val = change.get('percent', 0)
            direction = change.get('direction', 'same')

            # Форматирование чисел
            if key in ['revenue', 'profit', 'avg_check']:
                v1_str = f"{val1:,.0f} ₽".replace(',', ' ')
                v2_str = f"{val2:,.0f} ₽".replace(',', ' ')
                abs_str = f"{abs_val:+,.0f} ₽".replace(',', ' ')
            else:
                v1_str = f"{val1:,}".replace(',', ' ')
                v2_str = f"{val2:,}".replace(',', ' ')
                abs_str = f"{abs_val:+,}".replace(',', ' ')

            pct_str = f"{pct_val:+.1f}%"

            tree.insert('', 'end', values=(label, v1_str, v2_str, abs_str, pct_str), tags=(direction,))

        # Настройка цветов для тегов
        tree.tag_configure('up', foreground='green')
        tree.tag_configure('down', foreground='red')
        tree.tag_configure('same', foreground='gray')

        tree.pack(fill='both', expand=True, pady=10)