"""
Экспорт дашборда в PDF-отчёт
"""

import os
import io
from datetime import datetime
from fpdf import FPDF
import matplotlib

matplotlib.use('Agg')  # Неинтерактивный бэкенд для matplotlib
import matplotlib.pyplot as plt
import pandas as pd


class DashboardPDF(FPDF):
    """PDF-документ дашборда с поддержкой кириллицы"""

    def __init__(self):
        super().__init__()
        self._setup_fonts()

    def _setup_fonts(self):
        """Настройка шрифтов с поддержкой кириллицы"""
        # Ищем системный шрифт Arial (Windows) или DejaVuSans (Linux/Mac)
        font_paths = [
            r'C:\Windows\Fonts\arial.ttf',
            r'C:\Windows\Fonts\arialbd.ttf',
            '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
            '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
            '/System/Library/Fonts/Helvetica.ttc',
        ]

        # Используем встроенный шрифт DejaVu из matplotlib как fallback
        mpl_font_path = None
        try:
            from matplotlib.font_manager import findfont, FontProperties
            mpl_font_path = findfont(FontProperties(family='DejaVu Sans'))
        except:
            pass

        if mpl_font_path and os.path.exists(mpl_font_path):
            self.add_font('DejaVu', '', mpl_font_path, uni=True)
            # Для жирного попробуем найти
            bold_path = mpl_font_path.replace('DejaVuSans.ttf', 'DejaVuSans-Bold.ttf')
            if os.path.exists(bold_path):
                self.add_font('DejaVu', 'B', bold_path, uni=True)
            else:
                self.add_font('DejaVu', 'B', mpl_font_path, uni=True)
            self.font_family = 'DejaVu'
        else:
            # Пробуем Arial
            arial_found = False
            for path in font_paths:
                if os.path.exists(path):
                    if 'arialbd' in path.lower():
                        self.add_font('Arial', 'B', path, uni=True)
                    else:
                        self.add_font('Arial', '', path, uni=True)
                        arial_found = True

            if not arial_found:
                # Fallback: используем встроенный шрифт (кириллица может не работать)
                self.font_family = 'Helvetica'
            else:
                self.font_family = 'Arial'

    def header(self):
        """Колонтитул сверху на каждой странице"""
        self.set_font(self.font_family, 'B', 10)
        self.set_text_color(100, 100, 100)
        self.cell(0, 10, 'Auto Data Merger Tool - Отчёт по продажам', align='L')
        self.cell(0, 10, f'Сформирован: {datetime.now().strftime("%d.%m.%Y %H:%M")}', align='R', new_x="LMARGIN",
                  new_y="NEXT")
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(5)

    def footer(self):
        """Колонтитул снизу"""
        self.set_y(-15)
        self.set_font(self.font_family, '', 8)  # Изменили 'I' на '' (обычный стиль)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'Страница {self.page_no()}/{{nb}}', align='C')


class PDFExporter:
    """Экспорт дашборда в PDF"""

    @staticmethod
    def export_dashboard(
            summaries: dict,
            kpi: dict,
            output_path: str,
            title: str = 'Отчёт по продажам'
    ):
        """
        Создание PDF-отчёта с дашбордом

        Args:
            summaries: Словарь сводных таблиц
            kpi: Словарь KPI-метрик
            output_path: Путь для сохранения PDF
            title: Заголовок отчёта
        """
        pdf = DashboardPDF()
        pdf.alias_nb_pages()
        pdf.set_auto_page_break(auto=True, margin=20)

        # === СТРАНИЦА 1: Титульная + KPI ===
        pdf.add_page()

        # Заголовок
        pdf.set_font(pdf.font_family, 'B', 22)
        pdf.set_text_color(30, 30, 30)
        pdf.cell(0, 20, title, align='C', new_x="LMARGIN", new_y="NEXT")
        pdf.ln(5)

        # Подзаголовок с периодом
        if kpi.get('date_min') and kpi.get('date_max'):
            pdf.set_font(pdf.font_family, '', 12)
            pdf.set_text_color(80, 80, 80)
            period_text = f"Период: {kpi['date_min']} — {kpi['date_max']}"
            pdf.cell(0, 10, period_text, align='C', new_x="LMARGIN", new_y="NEXT")
            pdf.ln(10)

        # Разделитель
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(10)

        # KPI секция
        pdf.set_font(pdf.font_family, 'B', 16)
        pdf.set_text_color(30, 30, 30)
        pdf.cell(0, 12, 'Ключевые показатели (KPI)', new_x="LMARGIN", new_y="NEXT")
        pdf.ln(5)

        # KPI карточки (2 в ряд)
        kpi_items = [
            ('Всего строк', str(kpi.get('total_rows', 0))),
            ('Продано единиц', f"{kpi.get('total_units_sold', 0):,}".replace(',', ' ')),
            ('Общая выручка', f"{kpi.get('total_revenue', 0):,.2f} ₽".replace(',', ' ')),
            ('Общая прибыль', f"{kpi.get('total_profit', 0):,.2f} ₽".replace(',', ' ')),
            ('Средний чек', f"{kpi.get('avg_check', 0):,.2f} ₽".replace(',', ' ')),
        ]

        for i in range(0, len(kpi_items), 2):
            pdf.set_font(pdf.font_family, '', 10)

            # Первая карточка
            label1, value1 = kpi_items[i]
            pdf.set_fill_color(240, 245, 255)
            pdf.cell(95, 8, f"  {label1}:", fill=True)
            pdf.cell(95, 8, f"  {value1}", fill=True, new_x="LMARGIN", new_y="NEXT")

            # Вторая карточка (если есть)
            if i + 1 < len(kpi_items):
                label2, value2 = kpi_items[i + 1]
                pdf.cell(95, 8, f"  {label2}:", fill=True)
                pdf.cell(95, 8, f"  {value2}", fill=True, new_x="LMARGIN", new_y="NEXT")
            else:
                pdf.cell(95, 8, '', fill=True)
                pdf.cell(95, 8, '', fill=True, new_x="LMARGIN", new_y="NEXT")

        pdf.ln(10)

        # === СТРАНИЦЫ С ГРАФИКАМИ ===
        pdf.set_font(pdf.font_family, 'B', 16)
        pdf.set_text_color(30, 30, 30)
        pdf.cell(0, 12, 'Графики', new_x="LMARGIN", new_y="NEXT")
        pdf.ln(5)

        # График 1: По продуктам
        if not summaries.get('by_product', pd.DataFrame()).empty:
            pdf.add_page()
            img_bytes = PDFExporter._create_bar_chart_png(
                summaries['by_product'],
                'Выручка по продуктам',
                'product', 'revenue', 'Продукт'
            )
            pdf.image(img_bytes, x=15, w=180)

        # График 2: По регионам
        if not summaries.get('by_region', pd.DataFrame()).empty:
            pdf.add_page()
            img_bytes = PDFExporter._create_bar_chart_png(
                summaries['by_region'],
                'Выручка по регионам',
                'region', 'revenue', 'Регион'
            )
            pdf.image(img_bytes, x=15, w=180)

        # График 3: По месяцам
        if not summaries.get('by_month', pd.DataFrame()).empty:
            pdf.add_page()
            img_bytes = PDFExporter._create_line_chart_png(
                summaries['by_month'],
                'Динамика выручки по месяцам',
                'period', 'revenue', 'Период'
            )
            pdf.image(img_bytes, x=15, w=180)

        # === СТРАНИЦЫ С ТАБЛИЦАМИ ===
        tables_config = [
            ('by_product', 'Сводная таблица: По продуктам', 'product', 'revenue', 'profit'),
            ('by_region', 'Сводная таблица: По регионам', 'region', 'revenue', 'profit'),
            ('by_manager', 'Сводная таблица: По менеджерам', 'manager', 'revenue', 'profit'),
            ('by_customer', 'Сводная таблица: По клиентам', 'customer', 'revenue', 'profit'),
            ('by_month', 'Сводная таблица: По месяцам', 'period', 'revenue', 'profit'),
        ]

        for key, title, col1, col2, col3 in tables_config:
            df = summaries.get(key, pd.DataFrame())
            if df.empty:
                continue

            pdf.add_page()
            pdf.set_font(pdf.font_family, 'B', 14)
            pdf.set_text_color(30, 30, 30)
            pdf.cell(0, 12, title, new_x="LMARGIN", new_y="NEXT")
            pdf.ln(5)

            # Заголовки таблицы
            pdf.set_font(pdf.font_family, 'B', 10)
            pdf.set_fill_color(70, 130, 180)
            pdf.set_text_color(255, 255, 255)

            has_profit = col3 in df.columns
            col_widths = [70, 60, 60] if has_profit else [95, 95]
            headers = [col1.capitalize(), 'Выручка (₽)']
            if has_profit:
                headers.append('Прибыль (₽)')

            for j, header in enumerate(headers):
                pdf.cell(col_widths[j], 8, f" {header}", border=1, fill=True)
            pdf.ln()

            # Данные таблицы
            pdf.set_font(pdf.font_family, '', 9)
            pdf.set_text_color(0, 0, 0)
            fill = False

            for _, row in df.iterrows():
                if pdf.get_y() > 270:  # Проверка конца страницы
                    pdf.add_page()
                    # Повторяем заголовки
                    pdf.set_font(pdf.font_family, 'B', 10)
                    pdf.set_fill_color(70, 130, 180)
                    pdf.set_text_color(255, 255, 255)
                    for j, header in enumerate(headers):
                        pdf.cell(col_widths[j], 8, f" {header}", border=1, fill=True)
                    pdf.ln()
                    pdf.set_font(pdf.font_family, '', 9)
                    pdf.set_text_color(0, 0, 0)
                    fill = False

                pdf.set_fill_color(245, 245, 245) if fill else pdf.set_fill_color(255, 255, 255)

                val1 = str(row[col1])
                val2 = f"{row[col2]:,.2f} ₽".replace(',', ' ')

                if has_profit:
                    val3 = f"{row[col3]:,.2f} ₽".replace(',', ' ')
                    pdf.cell(col_widths[0], 7, f" {val1}", border=1, fill=fill)
                    pdf.cell(col_widths[1], 7, f" {val2}", border=1, fill=fill)
                    pdf.cell(col_widths[2], 7, f" {val3}", border=1, fill=fill, new_x="LMARGIN", new_y="NEXT")
                else:
                    pdf.cell(col_widths[0], 7, f" {val1}", border=1, fill=fill)
                    pdf.cell(col_widths[1], 7, f" {val2}", border=1, fill=fill, new_x="LMARGIN", new_y="NEXT")

                fill = not fill

        # Сохранение PDF
        pdf.output(output_path)
        return output_path

    @staticmethod
    def _create_bar_chart_png(df: pd.DataFrame, title: str, x_col: str, y_col: str, x_label: str) -> io.BytesIO:
        """Создание столбчатой диаграммы в памяти"""
        matplotlib.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial']
        matplotlib.rcParams['axes.unicode_minus'] = False

        fig, ax = plt.subplots(figsize=(10, 6))

        bars = ax.bar(df[x_col].astype(str), df[y_col], color='#4C72B0', edgecolor='black', linewidth=0.5)

        for bar in bars:
            yval = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2, yval,
                    f'{yval:,.0f}'.replace(',', ' '), ha='center', va='bottom', fontsize=9)

        ax.set_title(title, fontsize=14, fontweight='bold', pad=15)
        ax.set_xlabel(x_label, fontsize=11)
        ax.set_ylabel('Выручка (₽)', fontsize=11)
        ax.tick_params(axis='x', rotation=45)
        ax.grid(axis='y', linestyle='--', alpha=0.7)

        fig.tight_layout()

        buf = io.BytesIO()
        fig.savefig(buf, format='png', dpi=150, bbox_inches='tight')
        plt.close(fig)
        buf.seek(0)
        return buf

    @staticmethod
    def _create_line_chart_png(df: pd.DataFrame, title: str, x_col: str, y_col: str, x_label: str) -> io.BytesIO:
        """Создание линейного графика в памяти"""
        matplotlib.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial']
        matplotlib.rcParams['axes.unicode_minus'] = False

        fig, ax = plt.subplots(figsize=(10, 6))

        ax.plot(df[x_col].astype(str), df[y_col], marker='o', color='#C44E52', linewidth=2, markersize=8)
        ax.fill_between(df[x_col].astype(str), df[y_col], color='#C44E52', alpha=0.2)

        ax.set_title(title, fontsize=14, fontweight='bold', pad=15)
        ax.set_xlabel(x_label, fontsize=11)
        ax.set_ylabel('Выручка (₽)', fontsize=11)
        ax.tick_params(axis='x', rotation=45)
        ax.grid(True, linestyle='--', alpha=0.7)

        fig.tight_layout()

        buf = io.BytesIO()
        fig.savefig(buf, format='png', dpi=150, bbox_inches='tight')
        plt.close(fig)
        buf.seek(0)
        return buf