"""
Тест объединения данных
"""

import pandas as pd
import os
from core.merger import DataMerger


def test_merger():
    print("=== Тест объединения данных ===\n")

    # Создаём папку test_data, если её нет
    os.makedirs('test_data', exist_ok=True)

    # 1. Создаём первый файл (CSV) с чистыми данными
    data1 = {
        'date': ['2024-01-01', '2024-01-02'],
        'region': ['North', 'South'],
        'product': ['A', 'B'],
        'units_sold': [10, 20],
        'unit_price': [100.0, 150.0]
    }
    pd.DataFrame(data1).to_csv('test_data/file1.csv', index=False)
    print("✓ Создан test_data/file1.csv")

    # 2. Создаём второй файл (Excel) с дубликатом первой строки и одной "грязной" строкой
    data2 = {
        'Date': ['2024-01-01', '2024-01-03', 'bad_date'],  # Первая строка - дубликат, третья - ошибка
        'Region': ['North', 'East', 'West'],
        'Product': ['A', 'C', 'D'],
        'Units Sold': [10, 15, 5],
        'Unit Price': [100.0, 200.0, 50.0]
    }
    pd.DataFrame(data2).to_excel('test_data/file2.xlsx', index=False)
    print("✓ Создан test_data/file2.xlsx")

    # 3. Запускаем объединение
    merger = DataMerger()
    files_to_merge = ['test_data/file1.csv', 'test_data/file2.xlsx', 'test_data/nonexistent.csv']

    print("\nЗапуск объединения...")
    try:
        merged_df = merger.merge_files(files_to_merge)

        print("\n✅ Объединение завершено!")
        print(f"Статистика: {merger.get_stats()}")

        errors = merger.get_errors()
        if errors:
            print("\n⚠️ Ошибки при обработке (это нормально для тестов):")
            for err in errors:
                print(f"  - {err}")

        print("\nИтоговые объединённые данные:")
        print(merged_df.to_string(index=False))

    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")


if __name__ == "__main__":
    test_merger()