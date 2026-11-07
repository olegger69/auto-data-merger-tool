"""
Тест экспорта в PDF
"""

import pandas as pd
from reports.pdf_exporter import PDFExporter
from reports.kpi import KPIReporter
from reports.summaries import SummaryReporter


def test_pdf():
    print("=== Тест экспорта в PDF ===\n")

    # Создаём тестовые данные
    test_data = {
        'date': pd.to_datetime(['2024-01-01', '2024-01-02', '2024-01-03', '2024-02-01', '2024-02-02']),
        'region': ['North', 'South', 'East', 'North', 'West'],
        'product': ['Laptop', 'Phone', 'Tablet', 'Laptop', 'Monitor'],
        'units_sold': [10, 20, 15, 8, 12],
        'unit_price': [1000.0, 500.0, 800.0, 1000.0, 400.0],
        'cost_price': [700.0, 350.0, 600.0, 700.0, 300.0],
        'profit': [3000.0, 3000.0, 3000.0, 2400.0, 1200.0],
        'customer': ['Company A', 'Company B', 'Company C', 'Company A', 'Company D'],
        'manager': ['Иванов', 'Петров', 'Сидоров', 'Иванов', 'Кузнецов']
    }

    df = pd.DataFrame(test_data)
    df['revenue'] = df['units_sold'] * df['unit_price']

    # Расчёт KPI и сводок
    kpi = KPIReporter.calculate(df)
    summaries = SummaryReporter.generate_all(df)

    # Экспорт в PDF
    output_path = 'test_data/test_report.pdf'
    try:
        PDFExporter.export_dashboard(summaries, kpi, output_path, title='Тестовый отчёт по продажам')
        print(f"✅ PDF успешно создан: {output_path}")
        print(f"   Размер файла: {__import__('os').path.getsize(output_path):,} байт")
    except Exception as e:
        print(f"❌ Ошибка создания PDF: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_pdf()