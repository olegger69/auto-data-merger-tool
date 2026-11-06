"""
Тест диалога маппинга столбцов
"""

import tkinter as tk
from ui.column_mapping_dialog import ColumnMappingDialog
from core.loader import DataLoader


def test_dialog():
    # Создаём главное окно (фон)
    root = tk.Tk()
    root.title("Главное окно (фон)")
    root.geometry("600x400")

    ttk_label = tk.Label(
        root,
        text="Это главное окно.\nСейчас откроется диалог маппинга.",
        font=('Arial', 14)
    )
    ttk_label.pack(expand=True)

    # Имитируем данные из файла
    available_columns = ['ID', 'Дата заказа', 'Менеджер', 'Кол-во штук', 'Цена', 'Скидка']

    # Имитируем то, что нашёл детектор (например, он не нашёл product и region)
    detected_roles = {
        'date': 'Дата заказа',
        'region': None,  # Не нашёл
        'product': None,  # Не нашёл
        'units_sold': 'Кол-во штук',
        'unit_price': 'Цена'
    }

    # Показываем диалог
    print("Открытие диалога маппинга...")
    dialog = ColumnMappingDialog(root, available_columns, detected_roles)
    result = dialog.show()

    # Вывод результата в консоль
    if result is not None:
        print("\n✅ Пользователь выбрал:")
        for role, col in result.items():
            print(f"   {role:12} → {col}")

        # Проверяем полноту
        is_complete, missing = DataLoader.check_roles_complete(result)
        if is_complete:
            print("\n🎉 Отлично! Все обязательные столбцы выбраны.")
        else:
            print(f"\n⚠️ Внимание! Не выбраны: {missing}")
    else:
        print("\n❌ Пользователь нажал 'Отмена' или закрыл окно.")

    # Закрываем главное окно после диалога
    root.destroy()


if __name__ == "__main__":
    test_dialog()