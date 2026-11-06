"""
Тест умного автоопределения столбцов
"""

import pandas as pd
from core.smart_detector import SmartColumnDetector


def test_detector():
    print("=" * 70)
    print("ТЕСТ 1: Файл с синонимами (order_date, product_name, qty, price)")
    print("=" * 70)
    df1 = pd.DataFrame({
        'order_date': ['2024-01-01', '2024-01-02', '2024-01-03'],
        'manager': ['Иванов', 'Петров', 'Сидоров'],
        'product_name': ['Ноутбук', 'Телефон', 'Планшет'],
        'qty': [10, 20, 15],
        'price': [1000.0, 500.0, 800.0]
    })
    detector1 = SmartColumnDetector(df1)
    detector1.detect_all()  # <-- ВОТ ЭТОГО НЕ ХВАТАЛО!
    print(detector1.get_report())
    print()

    print("=" * 70)
    print("ТЕСТ 2: Файл с кириллицей и длинными названиями")
    print("=" * 70)
    df2 = pd.DataFrame({
        'Дата продажи': ['2024-01-01', '2024-01-02', '2024-01-03'],
        'Город': ['Москва', 'Питер', 'Казань'],
        'Наименование товара': ['A', 'B', 'C'],
        'Кол-во': [5, 10, 8],
        'Цена за единицу': [100.0, 200.0, 150.0]
    })
    detector2 = SmartColumnDetector(df2)
    detector2.detect_all()  # <-- И ЭТОГО
    print(detector2.get_report())
    print()

    print("=" * 70)
    print("ТЕСТ 3: Твои учебные файлы (EC01/EC03 структура)")
    print("=" * 70)
    df4 = pd.DataFrame({
        'ID': ['B-25601', 'B-25602', 'B-25603'],
        'Объем продаж': [1275, 66, 8],
        'Выручка': [-1148, -12, -2],
        'Колличество': [7, 5, 3],
        'Категория': ['Furniture', 'Clothing', 'Clothing'],
        'Подкатегория': ['Bookcases', 'Stole', 'Hankerchief'],
        'Цена за штуку': [182.14, 13.2, 2.67]
    })
    detector4 = SmartColumnDetector(df4)
    detector4.detect_all()  # <-- И ЭТОГО
    print(detector4.get_report())
    print()

    print("=" * 70)
    print("✅ Все тесты завершены!")
    print("=" * 70)


if __name__ == "__main__":
    test_detector()