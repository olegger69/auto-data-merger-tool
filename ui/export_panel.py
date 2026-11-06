"""
Панель экспорта данных
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import os


class ExportPanel:
    """Панель экспорта объединённых данных и отчётов"""

    def __init__(self, parent, main_window):
        self.parent = parent
        self.main_window = main_window
        self.frame = ttk.Frame(parent)
        self._create_widgets()

    def _create_widgets(self):
        """Создание виджетов панели экспорта"""
        # Заголовок
        header = ttk.Label(
            self.frame,
            text="Экспорт результатов",
            font=('Arial', 16, 'bold')
        )
        header.pack(pady=20)

        # Контейнер для кнопок экспорта
        buttons_frame = ttk.Frame(self.frame)
        buttons_frame.pack(fill='x', padx=40, pady=20)

        # Кнопка 1: Экспорт объединённых данных
        export_data_frame = ttk.LabelFrame(
            buttons_frame,
            text="📊 Объединённые данные",
            padding=15
        )
        export_data_frame.pack(fill='x', pady=10)

        ttk.Label(
            export_data_frame,
            text="Сохранить все объединённые строки в Excel-файл",
            font=('Arial', 10)
        ).pack(anchor='w', pady=(0, 10))

        export_data_btn = ttk.Button(
            export_data_frame,
            text="💾 Экспортировать merged_output.xlsx",
            command=self._export_merged_data
        )
        export_data_btn.pack(anchor='w')

        # Кнопка 2: Экспорт сводного отчёта
        export_report_frame = ttk.LabelFrame(
            buttons_frame,
            text="📑 Сводный отчёт",
            padding=15
        )
        export_report_frame.pack(fill='x', pady=10)

        ttk.Label(
            export_report_frame,
            text="Сохранить сводные таблицы (по продуктам, регионам, месяцам) в Excel с несколькими листами",
            font=('Arial', 10),
            wraplength=500
        ).pack(anchor='w', pady=(0, 10))

        export_report_btn = ttk.Button(
            export_report_frame,
            text="📑 Экспортировать summary_report.xlsx",
            command=self._export_summary_report
        )
        export_report_btn.pack(anchor='w')

        # Кнопка 3: Экспорт графиков
        export_charts_frame = ttk.LabelFrame(
            buttons_frame,
            text="🖼️ Графики",
            padding=15
        )
        export_charts_frame.pack(fill='x', pady=10)

        ttk.Label(
            export_charts_frame,
            text="Сохранить все три графика в PNG-файлы",
            font=('Arial', 10)
        ).pack(anchor='w', pady=(0, 10))

        export_charts_btn = ttk.Button(
            export_charts_frame,
            text="🖼️ Экспортировать графики в PNG",
            command=self._export_charts
        )
        export_charts_btn.pack(anchor='w')

        # Информационное сообщение
        info_label = ttk.Label(
            self.frame,
            text="⚠️ Для экспорта сначала объедините файлы на вкладке «Импорт файлов»",
            font=('Arial', 10),
            foreground='gray'
        )
        info_label.pack(pady=20)

    def _check_data_available(self) -> bool:
        """Проверка наличия данных для экспорта"""
        if self.main_window.merged_data is None:
            messagebox.showwarning(
                "Нет данных",
                "Сначала загрузите и объедините файлы на вкладке «Импорт файлов»."
            )
            return False
        return True

    def _export_merged_data(self):
        """Экспорт объединённых данных в Excel"""
        if not self._check_data_available():
            return

        filepath = filedialog.asksaveasfilename(
            title="Сохранить объединённые данные",
            defaultextension=".xlsx",
            filetypes=[("Excel файлы", "*.xlsx")],
            initialfile="merged_output.xlsx"
        )

        if filepath:
            try:
                self.main_window.merged_data.to_excel(
                    filepath,
                    index=False,
                    engine='openpyxl'
                )
                messagebox.showinfo(
                    "Успех",
                    f"Объединённые данные сохранены:\n{filepath}"
                )
                self.main_window.set_status(f"✅ Экспортировано: {filepath}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось сохранить файл:\n{e}")

    def _export_summary_report(self):
        """Экспорт сводного отчёта в Excel с несколькими листами"""
        if not self._check_data_available():
            return

        filepath = filedialog.asksaveasfilename(
            title="Сохранить сводный отчёт",
            defaultextension=".xlsx",
            filetypes=[("Excel файлы", "*.xlsx")],
            initialfile="summary_report.xlsx"
        )

        if filepath:
            try:
                with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                    summaries = self.main_window.summaries

                    # Лист 1: По продуктам
                    summaries['by_product'].to_excel(
                        writer,
                        sheet_name='По продуктам',
                        index=False
                    )

                    # Лист 2: По регионам
                    summaries['by_region'].to_excel(
                        writer,
                        sheet_name='По регионам',
                        index=False
                    )

                    # Лист 3: По месяцам
                    summaries['by_month'].to_excel(
                        writer,
                        sheet_name='По месяцам',
                        index=False
                    )

                    # Лист 4: KPI
                    kpi_df = pd.DataFrame([self.main_window.kpi])
                    kpi_df.to_excel(
                        writer,
                        sheet_name='KPI',
                        index=False
                    )

                messagebox.showinfo(
                    "Успех",
                    f"Сводный отчёт сохранён:\n{filepath}\n\nЛисты: По продуктам, По регионам, По месяцам, KPI"
                )
                self.main_window.set_status(f"✅ Экспортировано: {filepath}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось сохранить файл:\n{e}")

    def _export_charts(self):
        """Экспорт графиков в PNG"""
        if not self._check_data_available():
            return

        folder = filedialog.askdirectory(
            title="Выберите папку для сохранения графиков"
        )

        if folder:
            try:
                from charts.plots import ChartBuilder

                summaries = self.main_window.summaries

                # График 1: По продуктам
                fig1 = ChartBuilder.create_bar_chart(
                    summaries['by_product'],
                    'product', 'revenue',
                    'Выручка по продуктам', 'Продукт', 'Выручка (₽)'
                )
                path1 = os.path.join(folder, 'chart_products.png')
                ChartBuilder.save_figure(fig1, path1)

                # График 2: По регионам
                fig2 = ChartBuilder.create_bar_chart(
                    summaries['by_region'],
                    'region', 'revenue',
                    'Выручка по регионам', 'Регион', 'Выручка (₽)'
                )
                path2 = os.path.join(folder, 'chart_regions.png')
                ChartBuilder.save_figure(fig2, path2)

                # График 3: По месяцам
                fig3 = ChartBuilder.create_line_chart(
                    summaries['by_month'],
                    'period', 'revenue',
                    'Динамика выручки по месяцам', 'Период', 'Выручка (₽)'
                )
                path3 = os.path.join(folder, 'chart_months.png')
                ChartBuilder.save_figure(fig3, path3)

                messagebox.showinfo(
                    "Успех",
                    f"Графики сохранены в папку:\n{folder}\n\n"
                    f"- chart_products.png\n"
                    f"- chart_regions.png\n"
                    f"- chart_months.png"
                )
                self.main_window.set_status(f"✅ Графики экспортированы в {folder}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось сохранить графики:\n{e}")

    def enable(self):
        """Активация панели (когда данные загружены)"""
        pass  # Кнопки всегда активны, проверка внутри методов

    def disable(self):
        """Деактивация панели"""
        pass
