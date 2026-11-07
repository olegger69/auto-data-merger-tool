"""
Тест импорта из Google Sheets
Используем публичную тестовую таблицу
"""

from core.google_sheets import GoogleSheetsImporter


def test_google_sheets():
    print("=" * 70)
    print("Тест импорта из Google Sheets")
    print("=" * 70)

    # Публичная тестовая таблица (пример)
    # Замени на свой URL публичной таблицы для реального теста
    test_url = "https://docs.google.com/spreadsheets/d/163gmy56BTRaQqldnmid03MjpR71_GhTF7gfaGFayIvc/edit?usp=sharing"

    print(f"\n🔗 Тестовый URL: {test_url}")

    # Проверка URL
    is_valid, message = GoogleSheetsImporter.validate_url(test_url)
    print(f"\n✅ Проверка URL: {message}")

    # Извлечение ID
    sheet_id = GoogleSheetsImporter.extract_sheet_id(test_url)
    print(f"📋 ID таблицы: {sheet_id}")

    # Построение CSV URL
    csv_url = GoogleSheetsImporter.build_csv_url(sheet_id)
    print(f"📥 CSV URL: {csv_url}")

    # Попытка импорта
    print("\n📥 Попытка импорта данных...")
    try:
        df = GoogleSheetsImporter.import_from_url(test_url)
        print(f"\n✅ Успешно импортировано!")
        print(f"   Строк: {len(df)}")
        print(f"   Столбцов: {len(df.columns)}")
        print(f"\n📊 Первые 5 строк:")
        print(df.head().to_string())
    except Exception as e:
        print(f"\n⚠️ Не удалось импортировать (возможно, таблица недоступна):")
        print(f"   {e}")
        print("\n💡 Для реального теста создай публичную таблицу:")
        print("   1. Открой Google Sheets")
        print("   2. Создай таблицу с данными")
        print("   3. Файл → Поделиться → Доступ по ссылке → 'Все, у кого есть ссылка'")
        print("   4. Скопируй URL и вставь в этот тест")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    test_google_sheets()