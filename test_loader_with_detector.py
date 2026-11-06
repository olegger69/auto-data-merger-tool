"""
Тест загрузчика с автоопределением столбцов
"""

import pandas as pd
import os
from core.loader import DataLoader


def test_loader_with_detector():
    print("=" * 70)
    print("Тест загрузчика с умным автоопределением")
    print("=" * 70)

    os.makedirs('test_data', exist_ok=True)

    # Создаём тестовый файл с нестандартными названиями
    test_df = pd.DataFrame({
        'Дата продажи': ['2024-01-01', '2024-01-02', '2024-01-03'],
        'Город': ['Москва', 'Питер', 'Казань'],
        'Наименование товара': ['Ноутбук', 'Телефон', 'Планшет'],
        'Кол-во': [10, 20, 15],
        'Цена за единицу': [1000.0, 500.0, 800.0],
        'Менеджер': ['Иванов', 'Петров', 'Сидоров']  # Лишний столбец
    })

    test_path = 'test_data/test_smart_load.xlsx'
    test_df.to_excel(test_path, index=False)
    print(f"\n✅ Создан тестовый файл: {test_path}\n")

    # Загружаем файл с детектором
    loader = DataLoader()
    df, roles = loader.load_and_detect(test_path)

    print("📊 Результат автоопределения:")
    for role, col in roles.items():
        status = f"→ '{col}'" if col else "→ не определено"
        print(f"   {role:12} {status}")

    # Проверяем полноту
    is_complete, missing = DataLoader.check_roles_complete(roles)
    print(f"\n{'✅ Все роли определены' if is_complete else f'⚠️ Не хватает: {missing}'}")

    # Применяем маппинг
    mapped_df = DataLoader.apply_mapping(df, roles)
    print(f"\n📋 Столбцы после маппинга: {list(mapped_df.columns)}")
    print(f"\nПервые строки после маппинга:")
    print(mapped_df.head())

    print("\n" + "=" * 70)
    print("✅ Тест завершён!")


if __name__ == "__main__":
    test_loader_with_detector()