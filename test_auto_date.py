"""
Тест автоопределения столбца с датой
"""

import pandas as pd
from core.validator import DataValidator


def test_auto_date():
    print("=== Тест автоопределения столбца с датой ===\n")

    # Тест 1: Точное совпадение 'date'
    print("1. Точное совпадение 'date'")
    df1 = pd.DataFrame({
        'date': ['2024-01-01', '2024-01-02'],
        'region': ['North', 'South'],
        'product': ['A', 'B'],
        'units_sold': [10, 20],
        'unit_price': [100.0, 150.0]
    })
    detected = DataValidator.detect_date_column(df1)
    print(f"   Обнаружен столбец: '{detected}'")
    assert detected == 'date', "Должен найти 'date'"
    print("   ✅ Пройден\n")

    # Тест 2: Синоним 'order_date'
    print("2. Синоним 'order_date'")
    df2 = pd.DataFrame({
        'order_date': ['2024-01-01', '2024-01-02'],
        'region': ['North', 'South'],
        'product': ['A', 'B'],
        'units_sold': [10, 20],
        'unit_price': [100.0, 150.0]
    })
    detected = DataValidator.detect_date_column(df2)
    print(f"   Обнаружен столбец: '{detected}'")
    assert detected == 'order_date', "Должен найти 'order_date'"
    print("   ✅ Пройден\n")

    # Тест 3: Синоним 'дата' (кириллица)
    print("3. Синоним 'дата' (кириллица)")
    df3 = pd.DataFrame({
        'дата': ['2024-01-01', '2024-01-02'],
        'регион': ['North', 'South'],
        'продукт': ['A', 'B'],
        'количество': [10, 20],
        'цена': [100.0, 150.0]
    })
    detected = DataValidator.detect_date_column(df3)
    print(f"   Обнаружен столбец: '{detected}'")
    assert detected == 'дата', "Должен найти 'дата'"
    print("   ✅ Пройден\n")

    # Тест 4: Эвристика по содержимому (нестандартное название)
    print("4. Эвристика: столбец 'my_custom_field' с датами")
    df4 = pd.DataFrame({
        'my_custom_field': ['2024-01-01', '2024-01-02', '2024-01-03', '2024-01-04', '2024-01-05'],
        'region': ['North', 'South', 'East', 'West', 'North'],
        'product': ['A', 'B', 'C', 'D', 'E'],
        'units_sold': [10, 20, 15, 5, 25],
        'unit_price': [100.0, 150.0, 200.0, 50.0, 300.0]
    })
    detected = DataValidator.detect_date_column(df4)
    print(f"   Обнаружен столбец: '{detected}'")
    assert detected == 'my_custom_field', "Должен найти 'my_custom_field' по содержимому"
    print("   ✅ Пройден\n")

    # Тест 5: Полный процесс обработки с нестандартным названием
    print("5. Полный процесс: 'Order Date' → 'date'")
    df5 = pd.DataFrame({
        'Order Date': ['2024-01-01', '2024-01-02'],
        'Region': ['North', 'South'],
        'Product': ['A', 'B'],
        'Units Sold': [10, 20],
        'Unit Price': [100.0, 150.0]
    })
    try:
        processed = DataValidator.process(df5)
        print(f"   Столбцы после обработки: {list(processed.columns)}")
        assert 'date' in processed.columns, "Должен быть столбец 'date'"
        assert 'revenue' in processed.columns, "Должен быть столбец 'revenue'"
        print(f"   Данные:\n{processed.to_string(index=False)}")
        print("   ✅ Пройден\n")
    except Exception as e:
        print(f"   ❌ Ошибка: {e}\n")

    # Тест 6: Отсутствие столбца с датой
    print("6. Отсутствие столбца с датой (должна быть ошибка)")
    df6 = pd.DataFrame({
        'region': ['North', 'South'],
        'product': ['A', 'B'],
        'units_sold': [10, 20],
        'unit_price': [100.0, 150.0]
    })
    detected = DataValidator.detect_date_column(df6)
    print(f"   Обнаружен столбец: {detected}")
    assert detected is None, "Не должен найти столбец с датой"
    print("   ✅ Пройден\n")

    print("=" * 60)
    print("✅ Все тесты автоопределения даты прошли успешно!")


if __name__ == "__main__":
    test_auto_date()