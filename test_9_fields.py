"""
Тест данных с 9 полями
"""

import pandas as pd
import os
from core.validator import DataValidator


def test_9_fields():
    print("=== Тест 9 обязательных полей ===\n")

    os.makedirs('test_data', exist_ok=True)

    # Создаём тестовый файл с 9 полями
    test_data = {
        'Date': ['2024-01-01', '2024-01-02', '2024-01-03'],
        'Region': ['North', 'South', 'East'],
        'Product': ['Laptop', 'Phone', 'Tablet'],
        'Units Sold': [10, 20, 15],
        'Unit Price': [1000.0, 500.0, 800.0],
        'Cost Price': [700.0, 350.0, 600.0],
        'Profit': [3000.0, 3000.0, 3000.0],
        'Customer': ['Company A', 'Company B', 'Company C'],
        'Manager': ['Иванов', 'Петров', 'Сидоров']
    }

    df = pd.DataFrame(test_data)
    test_path = 'test_data/test_9_fields.xlsx'
    df.to_excel(test_path, index=False)
    print(f"✅ Создан тестовый файл: {test_path}\n")

    # Проверяем валидацию
    print("Проверка валидации...")
    try:
        clean_df = DataValidator.process(df)
        print(f"✅ Валидация прошла успешно!")
        print(f"\nСтолбцы после обработки: {list(clean_df.columns)}")
        print(f"\nПервые строки:")
        print(clean_df.to_string(index=False))
    except Exception as e:
        print(f"❌ Ошибка валидации: {e}")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    test_9_fields()