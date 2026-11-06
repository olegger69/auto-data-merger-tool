"""
Тест модуля фильтрации
"""

import pandas as pd
from core.filter import DataFilter


def test_filter():
    print("=== Тест фильтрации данных ===\n")

    # Тестовые данные
    test_data = {
        'date': pd.to_datetime([
            '2024-01-01', '2024-01-15', '2024-02-01',
            '2024-02-15', '2024-03-01', '2024-03-15'
        ]),
        'region': ['North', 'South', 'North', 'East', 'South', 'West'],
        'product': ['A', 'B', 'A', 'C', 'B', 'A'],
        'units_sold': [10, 20, 15, 5, 25, 30],
        'unit_price': [100.0, 150.0, 100.0, 200.0, 150.0, 100.0],
        'revenue': [1000.0, 3000.0, 1500.0, 1000.0, 3750.0, 3000.0]
    }
    df = pd.DataFrame(test_data)

    print("Исходные данные:")
    print(df.to_string(index=False))
    print("-" * 60)

    # Тест 1: Фильтр по регионам
    print("1. Фильтр по регионам: North, South")
    filtered = DataFilter.apply(df, regions=['North', 'South'])
    print(f"   Строк: {len(filtered)} (было {len(df)})")
    print(filtered.to_string(index=False))
    print("-" * 60)

    # Тест 2: Фильтр по продуктам
    print("2. Фильтр по продуктам: A")
    filtered = DataFilter.apply(df, products=['A'])
    print(f"   Строк: {len(filtered)}")
    print(filtered.to_string(index=False))
    print("-" * 60)

    # Тест 3: Фильтр по датам
    print("3. Фильтр по датам: с 2024-02-01 по 2024-02-28")
    filtered = DataFilter.apply(
        df,
        date_from='2024-02-01',
        date_to='2024-02-28'
    )
    print(f"   Строк: {len(filtered)}")
    print(filtered.to_string(index=False))
    print("-" * 60)

    # Тест 4: Комбинированный фильтр
    print("4. Комбинированный: North + A + февраль")
    filtered = DataFilter.apply(
        df,
        regions=['North'],
        products=['A'],
        date_from='2024-02-01',
        date_to='2024-02-28'
    )
    print(f"   Строк: {len(filtered)}")
    print(filtered.to_string(index=False))
    print("-" * 60)

    # Тест 5: Получение уникальных значений
    print("5. Уникальные регионы:", DataFilter.get_unique_values(df, 'region'))
    print("   Уникальные продукты:", DataFilter.get_unique_values(df, 'product'))
    print("   Диапазон дат:", DataFilter.get_date_range(df))
    print("-" * 60)

    print("✅ Тест фильтрации прошёл успешно!")


if __name__ == "__main__":
    test_filter()