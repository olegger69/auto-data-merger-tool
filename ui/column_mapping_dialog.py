"""
Диалоговое окно для ручного сопоставления столбцов
"""

import tkinter as tk
from tkinter import ttk


class ColumnMappingDialog:
    """
    Модальное окно для выбора соответствия столбцов файла ролям приложения.
    """

    REQUIRED_ROLES = {
        'date': '📅 Дата продажи (date)',
        'region': '🌍 Регион / Город (region)',
        'product': '📦 Продукт / Товар (product)',
        'units_sold': '🔢 Количество (units_sold)',
        'unit_price': '💰 Цена за единицу (unit_price)'
    }

    def __init__(self, parent, available_columns: list, current_roles: dict):
        """
        Args:
            parent: Родительское окно (MainWindow)
            available_columns: Список реальных названий столбцов из файла
            current_roles: Словарь {роль: название_столбца}, который предложил детектор
        """
        self.parent = parent
        self.available_columns = ["— Не выбрано —"] + sorted(available_columns)
        self.current_roles = current_roles.copy()
        self.result_roles = None

        # Создаём диалоговое окно (Toplevel)
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Настройка соответствия столбцов")
        self.dialog.geometry("500x450")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)  # Привязка к родителю
        self.dialog.grab_set()  # Делаем окно модальным (блокирует основное)

        # Центрирование окна
        self.dialog.update_idletasks()
        x = parent.winfo_rootx() + (parent.winfo_width() // 2) - 250
        y = parent.winfo_rooty() + (parent.winfo_height() // 2) - 225
        self.dialog.geometry(f"+{x}+{y}")

        self._create_widgets()

        # Обработка закрытия окна через крестик
        self.dialog.protocol("WM_DELETE_WINDOW", self._on_cancel)

    def _create_widgets(self):
        """Создание виджетов диалога"""
        # Заголовок и инструкция
        header_frame = ttk.Frame(self.dialog)
        header_frame.pack(fill='x', padx=20, pady=15)

        ttk.Label(
            header_frame,
            text="Не все столбцы определены автоматически",
            font=('Arial', 12, 'bold'),
            foreground='#C44E52'
        ).pack(anchor='w')

        ttk.Label(
            header_frame,
            text="Пожалуйста, укажите, какой столбец из вашего файла соответствует каждому параметру:",
            font=('Arial', 10),
            wraplength=450
        ).pack(anchor='w', pady=(5, 0))

        # Форма с выпадающими списками
        form_frame = ttk.Frame(self.dialog)
        form_frame.pack(fill='both', expand=True, padx=20, pady=10)

        self.comboboxes = {}

        for i, (role, label_text) in enumerate(self.REQUIRED_ROLES.items()):
            row_frame = ttk.Frame(form_frame)
            row_frame.pack(fill='x', pady=5)

            # Метка роли
            ttk.Label(
                row_frame,
                text=label_text,
                width=30,
                font=('Arial', 10)
            ).pack(side='left')

            # Выпадающий список
            cb = ttk.Combobox(
                row_frame,
                values=self.available_columns,
                state='readonly',
                width=35,
                font=('Arial', 10)
            )
            cb.pack(side='left', padx=10)

            # Предвыбор значения, которое предложил детектор
            detected_col = self.current_roles.get(role)
            if detected_col and detected_col in self.available_columns:
                cb.set(detected_col)
            else:
                cb.set("— Не выбрано —")

            self.comboboxes[role] = cb

        # Кнопки управления
        btn_frame = ttk.Frame(self.dialog)
        btn_frame.pack(fill='x', padx=20, pady=15)

        ttk.Button(
            btn_frame,
            text="❌ Отмена",
            command=self._on_cancel,
            width=15
        ).pack(side='left')

        ttk.Button(
            btn_frame,
            text="✅ Применить",
            command=self._on_apply,
            width=15
        ).pack(side='right')

        # Фокус на первую кнопку
        btn_frame.focus_set()

    def _on_apply(self):
        """Сбор данных при нажатии 'Применить'"""
        new_roles = {}
        for role, cb in self.comboboxes.items():
            val = cb.get()
            new_roles[role] = val if val != "— Не выбрано —" else None

        self.result_roles = new_roles
        self.dialog.destroy()

    def _on_cancel(self):
        """Обработка отмены"""
        self.result_roles = None
        self.dialog.destroy()

    def show(self) -> dict:
        """
        Показывает диалог и возвращает обновлённый словарь ролей.
        Возвращает None, если пользователь нажал 'Отмена'.
        """
        self.parent.wait_window(self.dialog)
        return self.result_roles