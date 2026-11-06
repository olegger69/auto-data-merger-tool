"""
Диагностика файла: показывает структуру и возможные проблемы
"""

import pandas as pd
import sys


def diagnose_file(file_path):
    """Диагностика файла"""
    print(f"=== Диагностика файла: {file_path} ===\n")

    try:
        # Попытка загрузить файл
        print("1. Попытка загрузки...")
        df = pd.read_excel(file_path)
        print(f"   ✅ Файл загружен успешно")
        print(f"   Строк: {len(df)}")
        print(f"   Столбцов: {len(df.columns)}")
        print(f"   Названия столбцов: {list(df.columns)}")
        print()

        # Показать первые 10 строк
        print("2. Первые 10 строк:")
        print(df.head(10).to_string())
        print()

        # Проверка на пустые строки в начале
        print("3. Проверка первых строк на пустоту:")
        for i in range(min(5, len(df))):
            row = df.iloc[i]
            is_empty = row.isna().all()
            print(f"   Строка {i}: {'ПУСТАЯ' if is_empty else 'Заполненная'}")
        print()

        # Проверка типов данных
        print("4. Типы данных столбцов:")
        print(df.dtypes)
        print()

        # Проверка на объединённые ячейки (NaN в заголовках)
        print("5. Проверка заголовков на NaN:")
        nan_headers = [col for col in df.columns if pd.isna(col)]
        if nan_headers:
            print(f"   ⚠️ Найдено столбцов с NaN в заголовке: {len(nan_headers)}")
            print(f"   Это может быть из-за объединённых ячеек в Excel")
        else:
            print(f"   ✅ Все заголовки заполнены")
        print()

        # Рекомендации
        print("6. Рекомендации:")
        if len(df) == 0:
            print("   - Файл пустой или данные начинаются не с первой строки")
            print("   - Попробуйте открыть файл в Excel и проверить структуру")

        if any(pd.isna(col) for col in df.columns):
            print("   - В файле есть объединённые ячейки в заголовке")
            print("   - Откройте файл в Excel, уберите объединение ячеек, сохраните")

        print("\n" + "=" * 60)
        print("✅ Диагностика завершена")

    except Exception as e:
        print(f"   ❌ Ошибка загрузки: {type(e).__name__}")
        print(f"   Сообщение: {e}")
        print()
        print("Возможные причины:")
        print("  - Файл повреждён")
        print("  - Файл открыт в другой программе (Excel)")
        print("  - Нестандартный формат файла")
        print("  - Путь к файлу содержит спецсимволы")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        file_path = input("Введите путь к файлу: ").strip()

    diagnose_file(file_path)