"""
Тест загрузчика файлов
"""

from core.loader import DataLoader
import pandas as pd


def test_loader():
    """Тестирование DataLoader"""
    loader = DataLoader()

    # Создадим тестовый CSV файл
    test_data = {
        'date': ['2024-01-01', '2024-01-02', '2024-01-03'],
        'region': ['North', 'South', 'East'],
        'product': ['A', 'B', 'C'],
        'units_sold': [10, 20, 15],
        'unit_price': [100.0, 150.0, 200.0]
    }

    df = pd.DataFrame(test_data)
    df.to_csv('test_data/sample.csv', index=False)
    print("✓ Тестовый файл создан: test_data/sample.csv")

    # Загрузим файл
    try:
        loaded_df = loader.load_file('test_data/sample.csv')
        print(f"✓ Файл загружен успешно")
        print(f"  Строк: {len(loaded_df)}")
        print(f"  Столбцы: {list(loaded_df.columns)}")
        print(f"\nДанные:\n{loaded_df}")
    except Exception as e:
        print(f" Ошибка загрузки: {e}")

    # Информация о файле
    info = loader.get_loaded_files_info()
    print(f"\nИнформация о загруженных файлах: {info}")


if __name__ == "__main__":
    test_loader()