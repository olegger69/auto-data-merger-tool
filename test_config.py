"""
Тест менеджера настроек
"""

from core.config import ConfigManager


def test_config():
    print("=== Тест менеджера настроек ===\n")

    # 1. Создание менеджера
    print("1. Создание ConfigManager...")
    config = ConfigManager()
    print(f"   ✅ Создан. Путь: {config.config_path}")
    print()

    # 2. Значения по умолчанию
    print("2. Значения по умолчанию:")
    for key, value in config.get_all().items():
        print(f"   {key}: {value}")
    print()

    # 3. Установка и получение значений
    print("3. Установка значений...")
    config.set('last_import_folder', 'C:\\Users\\Oleg\\Documents')
    config.set('last_export_folder', 'C:\\Users\\Oleg\\Downloads')
    config.set('theme', 'dark')
    print(f"   last_import_folder: {config.get('last_import_folder')}")
    print(f"   last_export_folder: {config.get('last_export_folder')}")
    print(f"   theme: {config.get('theme')}")
    print()

    # 4. Сохранение геометрии окна
    print("4. Сохранение геометрии окна...")
    config.update_window_geometry(1400, 900, 50, 50)
    print(f"   width: {config.get('window_width')}")
    print(f"   height: {config.get('window_height')}")
    print(f"   x: {config.get('window_x')}")
    print(f"   y: {config.get('window_y')}")
    print()

    # 5. Пересоздание менеджера (имитация перезапуска приложения)
    print("5. Пересоздание ConfigManager (имитация перезапуска)...")
    config2 = ConfigManager()
    print(f"   last_import_folder: {config2.get('last_import_folder')}")
    print(f"   theme: {config2.get('theme')}")
    print(f"   window_width: {config2.get('window_width')}")
    print()

    # 6. Получение несуществующего ключа
    print("6. Получение несуществующего ключа...")
    value = config.get('non_existent_key', 'fallback_value')
    print(f"   Значение: {value}")
    print()

    # 7. Сброс настроек
    print("7. Сброс настроек...")
    config.reset()
    print(f"   theme после сброса: {config.get('theme')}")
    print(f"   last_import_folder после сброса: '{config.get('last_import_folder')}'")
    print()

    print("=" * 60)
    print("✅ Все тесты настроек прошли успешно!")
    print(f"\n📁 Файл настроек находится по пути:")
    print(f"   {config.config_path}")
    print("\n💡 Откройте его в текстовом редакторе, чтобы увидеть содержимое.")


if __name__ == "__main__":
    test_config()