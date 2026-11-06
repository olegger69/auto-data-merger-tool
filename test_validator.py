"""
Тест валидатора данных
"""

import pandas as pd
from core.validator import DataValidator


def test_validator():
    print("=== Тест валидатора данных ===\n")

    # Создаём "грязные" тестовые данные
    dirty_data = {
        'Date ': ['2024-01-01', 'invalid_date', '2024-01-03', None],  # Пробел, невалидная дата, пустота
        'Region': ['North', 'South', None, 'East'],
        'Product': ['A', 'B', 'C', 'D'],
        'Units Sold': [10, 'twenty', 15, 5],  # Текст вместо числа
        'Unit-Price': [100.0, 150.0, 'free', 200.0]  # Дефис, текст вместо числа
    }

    df = pd.DataFrame(dirty_data)
    print("1. Исходные 'грязные' данные:")
    print(df)
    print("-" * 50)

    try:
        # Обрабатываем данные
        clean_df = DataValidator.process(df)

        print("2. Очищенные и обработанные данные:")
        print(clean_df)
        print("-" * 50)

        print("3. Информация о типах данных:")
        print(clean_df.dtypes)
        print("-" * 50)

        print("✅ Валидация прошла успешно!")

    except ValueError as e:
        print(f"❌ Ошибка валидации: {e}")


if __name__ == "__main__":
    test_validator()