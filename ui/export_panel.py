"""
Панель экспорта данных (Excel, PDF, PNG)
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import os
from reports.pdf_exporter import PDFExporter


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
            text="📑 Сводный отчёт (Excel)",
            padding=15
        )
        export_report_frame.pack(fill='x', pady=10)

        ttk.Label(
            export_report_frame,
            text="Сохранить сводные таблицы в Excel с несколькими листами",
            font=('Arial', 10),
            wraplength=500
        ).pack(anchor='w', pady=(0, 10))

        export_report_btn = ttk.Button(
            export_report_frame,
            text="📑 Экспортировать summary_report.xlsx",
            command=self._export_summary_report
        )
        export_report_btn.pack(anchor='w')

        # Кнопка 3: Экспорт в PDF (НОВОЕ)
        export_pdf_frame = ttk.LabelFrame(
            buttons_frame,
            text="📄 PDF-отчёт для руководства",
            padding=15
        )
        export_pdf_frame.pack(fill='x', pady=10)

        ttk.Label(
            export_pdf_frame,
            text="Создать красивый PDF-файл с KPI, графиками и сводными таблицами",
            font=('Arial', 10),
            wraplength=500
        ).pack(anchor='w', pady=(0, 10))

        export_pdf_btn = ttk.Button(
            export_pdf_frame,
            text="📄 Экспортировать dashboard_report.pdf",
            command=self._export_pdf
        )
        export_pdf_btn.pack(anchor='w')

        # Кнопка 4: Экспорт графиков
        export_charts_frame = ttk.LabelFrame(
            buttons_frame,
            text="🖼️ Графики (PNG)",
            padding=15
        )
        export_charts_frame.pack(fill='x', pady=10)

        ttk.Label(
            export_charts_frame,
            text="Сохранить все три графика в отдельные PNG-файлы",
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

        initial_dir = self.main_window.config.get('last_export_folder', '')

        filepath = filedialog.asksaveasfilename(
            title="Сохранить объединённые данные",
            defaultextension=".xlsx",
            filetypes=[("Excel файлы", "*.xlsx")],
            initialfile="merged_output.xlsx",
            initialdir=initial_dir if initial_dir else ''
        )

        if filepath:
            try:
                self.main_window.merged_data.to_excel(
                    filepath,
                    index=False,
                    engine='openpyxl'
                )

                last_folder = os.path.dirname(filepath)
                self.main_window.config.set_last_export_folder(last_folder)

                messagebox.showinfo("Успех", f"Данные сохранены:\n{filepath}")
                self.main_window.set_status(f"✅ Экспортировано: {filepath}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось сохранить файл:\n{e}")

    def _export_summary_report(self):
        """Экспорт сводного отчёта в Excel с несколькими листами"""
        if not self._check_data_available():
            return

        initial_dir = self.main_window.config.get('last_export_folder', '')

        filepath = filedialog.asksaveasfilename(
            title="Сохранить сводный отчёт",
            defaultextension=".xlsx",
            filetypes=[("Excel файлы", "*.xlsx")],
            initialfile="summary_report.xlsx",
            initialdir=initial_dir if initial_dir else ''
        )

        if filepath:
            try:
                with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                    summaries = self.main_window.summaries

                    summaries['by_product'].to_excel(writer, sheet_name='По продуктам', index=False)
                    summaries['by_region'].to_excel(writer, sheet_name='По регионам', index=False)
                    summaries['by_manager'].to_excel(writer, sheet_name='По менеджерам', index=False)
                    summaries['by_customer'].to_excel(writer, sheet_name='По клиентам', index=False)
                    summaries['by_month'].to_excel(writer, sheet_name='По месяцам', index=False)

                    kpi_df = pd.DataFrame([self.main_window.kpi])
                    kpi_df.to_excel(writer, sheet_name='KPI', index=False)

                last_folder = os.path.dirname(filepath)
                self.main_window.config.set_last_export_folder(last_folder)

                messagebox.showinfo(
                    "Успех",
                    f"Сводный отчёт сохранён:\n{filepath}\n\nЛисты: Продукты, Регионы, Менеджеры, Клиенты, Месяцы, KPI"
                )
                self.main_window.set_status(f"✅ Экспортировано: {filepath}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось сохранить файл:\n{e}")

    def _export_pdf(self):
        """Экспорт дашборда в PDF"""
        if not self._check_data_available():
            return

        initial_dir = self.main_window.config.get('last_export_folder', '')

        filepath = filedialog.asksaveasfilename(
            title="Сохранить PDF-отчёт",
            defaultextension=".pdf",
            filetypes=[("PDF файлы", "*.pdf")],
            initialfile="dashboard_report.pdf",
            initialdir=initial_dir if initial_dir else ''
        )

        if filepath:
            try:
                self.main_window.set_status("⏳ Генерация PDF-отчёта (это может занять пару секунд)...")
                self.parent.update()  # Обновляем интерфейс, чтобы показать статус

                PDFExporter.export_dashboard(
                    summaries=self.main_window.summaries,
                    kpi=self.main_window.kpi,
                    output_path=filepath,
                    title='Отчёт по продажам'
                )

                last_folder = os.path.dirname(filepath)
                self.main_window.config.set_last_export_folder(last_folder)

                messagebox.showinfo(
                    "Успех",
                    f"PDF-отчёт успешно создан и сохранён:\n{filepath}"
                )
                self.main_window.set_status(f"✅ PDF экспортирован: {filepath}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось создать PDF:\n{e}")
                self.main_window.set_status("❌ Ошибка экспорта PDF")

    def _export_charts(self):
        """Экспорт графиков в PNG"""
        if not self._check_data_available():
            return

        folder = filedialog.askdirectory(
            title="Выберите папку для сохранения графиков",
            initialdir=self.main_window.config.get('last_export_folder', '')
        )

        if folder:
            try:
                from charts.plots import ChartBuilder

                summaries = self.main_window.summaries

                fig1 = ChartBuilder.create_bar_chart(
                    summaries['by_product'], 'product', 'revenue',
                    'Выручка по продуктам', 'Продукт', 'Выручка (₽)'
                )
                ChartBuilder.save_figure(fig1, os.path.join(folder, 'chart_products.png'))

                fig2 = ChartBuilder.create_bar_chart(
                    summaries['by_region'], 'region', 'revenue',
                    'Выручка по регионам', 'Регион', 'Выручка (₽)'
                )
                ChartBuilder.save_figure(fig2, os.path.join(folder, 'chart_regions.png'))

                fig3 = ChartBuilder.create_line_chart(
                    summaries['by_month'], 'period', 'revenue',
                    'Динамика выручки по месяцам', 'Период', 'Выручка (₽)'
                )
                ChartBuilder.save_figure(fig3, os.path.join(folder, 'chart_months.png'))

                self.main_window.config.set_last_export_folder(folder)

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