"""
Генератор тестовых данных для Auto Data Merger Tool
"""

import pandas as pd
import os
import random
from datetime import datetime, timedelta


def generate_sample_data():
    """Генерация тестовых файлов для проверки приложения"""

    # Создаём папку test_data
    os.makedirs('test_data', exist_ok=True)

    print("=== Генерация тестовых данных ===\n")

    # 1. Корректный CSV файл
    print("1. Создание test_data/sales_2024_q1.csv (корректный CSV)...")
    data1 = {
        'date': pd.date_range('2024-01-01', periods=30, freq='D').strftime('%Y-%m-%d'),
        'region': [random.choice(['North', 'South', 'East', 'West']) for _ in range(30)],
        'product': [random.choice(['Laptop', 'Phone', 'Tablet', 'Monitor']) for _ in range(30)],
        'units_sold': [random.randint(5, 50) for _ in range(30)],
        'unit_price': [random.uniform(100, 1000) for _ in range(30)]
    }
    df1 = pd.DataFrame(data1)
    df1.to_csv('test_data/sales_2024_q1.csv', index=False)
    print(f"   ✓ Создан: 30 строк\n")

    # 2. Корректный Excel файл
    print("2. Создание test_data/sales_2024_q2.xlsx (корректный Excel)...")
    data2 = {
        'date': pd.date_range('2024-04-01', periods=30, freq='D').strftime('%Y-%m-%d'),
        'region': [random.choice(['North', 'South', 'East', 'West']) for _ in range(30)],
        'product': [random.choice(['Laptop', 'Phone', 'Tablet', 'Monitor']) for _ in range(30)],
        'units_sold': [random.randint(5, 50) for _ in range(30)],
        'unit_price': [random.uniform(100, 1000) for _ in range(30)]
    }
    df2 = pd.DataFrame(data2)
    df2.to_excel('test_data/sales_2024_q2.xlsx', index=False)
    print(f"   ✓ Создан: 30 строк\n")

    # 3. Файл с "грязными" данными (для проверки валидации)
    print("3. Создание test_data/dirty_data.csv (с ошибками)...")
    dirty_data = {
        'Date ': ['2024-01-01', 'invalid', '2024-01-03', None, '2024-01-05'],
        'Region': ['North', 'South', None, 'East', 'West'],
        'Product': ['A', 'B', 'C', 'D', 'E'],
        'Units Sold': [10, 'twenty', 15, 5, 20],
        'Unit-Price': [100.0, 150.0, 'free', 200.0, 250.0]
    }
    df3 = pd.DataFrame(dirty_data)
    df3.to_csv('test_data/dirty_data.csv', index=False)
    print(f"   ✓ Создан: 5 строк (с ошибками для тестирования)\n")

    # 4. Файл с дубликатами
    print("4. Создание test_data/duplicates.csv (с дубликатами)...")
    dup_data = {
        'date': ['2024-01-01', '2024-01-01', '2024-01-02', '2024-01-02', '2024-01-03'],
        'region': ['North', 'North', 'South', 'South', 'East'],
        'product': ['A', 'A', 'B', 'B', 'C'],
        'units_sold': [10, 10, 20, 20, 15],
        'unit_price': [100.0, 100.0, 150.0, 150.0, 200.0]
    }
    df4 = pd.DataFrame(dup_data)
    df4.to_csv('test_data/duplicates.csv', index=False)
    print(f"   ✓ Создан: 5 строк (2 дубликата)\n")

    print("✅ Все тестовые файлы созданы в папке test_data/")
    print("\nТеперь вы можете:")
    print("  1. Запустить python main.py")
    print("  2. На вкладке 'Импорт файлов' добавить sales_2024_q1.csv и sales_2024_q2.xlsx")
    print("  3. Нажать 'Объединить файлы'")
    print("  4. Проверить дашборд и экспорт")


if __name__ == "__main__":
    generate_sample_data()