"""
Тест модулей отчётности (KPI и сводные таблицы)
"""

import pandas as pd
from reports.kpi import KPIReporter
from reports.summaries import SummaryReporter


def test_reports():
    print("=== Тест отчётности ===\n")

    # Создаём тестовые данные (имитация результата работы DataMerger)
    test_data = {
        'date': pd.to_datetime(['2024-01-01', '2024-01-02', '2024-01-15', '2024-02-10']),
        'region': ['North', 'South', 'North', 'East'],
        'product': ['A', 'B', 'A', 'C'],
        'units_sold': [10, 20, 15, 5],
        'unit_price': [100.0, 150.0, 100.0, 200.0],
        'revenue': [1000.0, 3000.0, 1500.0, 1000.0]
    }
    df = pd.DataFrame(test_data)

    print("1. Исходные данные:")
    print(df.to_string(index=False))
    print("-" * 50)

    # Тест KPI
    kpi = KPIReporter.calculate(df)
    print("2. KPI-метрики:")
    for key, value in kpi.items():
        print(f"  - {key}: {value}")
    print("-" * 50)

    # Тест сводных таблиц
    summaries = SummaryReporter.generate_all(df)

    print("3. Сводная таблица: Выручка по продуктам")
    print(summaries['by_product'].to_string(index=False))
    print("-" * 50)

    print("4. Сводная таблица: Выручка по регионам")
    print(summaries['by_region'].to_string(index=False))
    print("-" * 50)

    print("5. Сводная таблица: Динамика выручки по месяцам")
    print(summaries['by_month'].to_string(index=False))
    print("-" * 50)

    print("✅ Тест отчётности прошёл успешно!")


if __name__ == "__main__":
    test_reports()