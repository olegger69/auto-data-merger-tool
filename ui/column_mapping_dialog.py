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
        'date': '📅 Дата продажи',
        'region': '🌍 Регион / Город',
        'product': '📦 Продукт / Товар',
        'units_sold': '🔢 Количество',
        'unit_price': '💰 Цена за единицу'
    }

    OPTIONAL_ROLES = {
        'cost_price': '💵 Себестоимость',
        'profit': '📈 Прибыль',
        'customer': '👤 Клиент / Покупатель',
        'manager': '👔 Менеджер / Продавец'
    }

    def __init__(self, parent, available_columns: list, current_roles: dict):
        self.parent = parent
        self.available_columns = ["— Не выбрано —"] + sorted(available_columns)
        self.current_roles = current_roles.copy()
        self.result_roles = None

        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Настройка соответствия столбцов")
        self.dialog.geometry("600x700")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()

        # Центрирование
        self.dialog.update_idletasks()
        x = parent.winfo_rootx() + (parent.winfo_width() // 2) - 300
        y = parent.winfo_rooty() + (parent.winfo_height() // 2) - 350
        self.dialog.geometry(f"+{max(0, x)}+{max(0, y)}")

        self._create_widgets()
        self.dialog.protocol("WM_DELETE_WINDOW", self._on_cancel)

    def _create_widgets(self):
        """Создание виджетов диалога"""
        # Главный контейнер
        main_frame = ttk.Frame(self.dialog)
        main_frame.pack(fill='both', expand=True, padx=15, pady=10)

        # Заголовок
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill='x', pady=(0, 10))

        ttk.Label(
            header_frame,
            text="⚠️ Не все обязательные столбцы определены",
            font=('Arial', 12, 'bold'),
            foreground='#C44E52'
        ).pack(anchor='w')

        ttk.Label(
            header_frame,
            text="Выберите соответствие для обязательных полей. Опциональные поля можно оставить пустыми.",
            font=('Arial', 9),
            wraplength=550
        ).pack(anchor='w', pady=(5, 0))

        # Разделитель
        ttk.Separator(main_frame, orient='horizontal').pack(fill='x', pady=5)

        # Прокручиваемая область для формы
        canvas_frame = ttk.Frame(main_frame)
        canvas_frame.pack(fill='both', expand=True)

        canvas = tk.Canvas(canvas_frame, highlightthickness=0, borderwidth=0)
        scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw", width=canvas.winfo_reqwidth())
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Привязка колёсика мыши
        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"))

        self.comboboxes = {}

        # Обязательные роли
        ttk.Label(
            self.scrollable_frame,
            text="ОБЯЗАТЕЛЬНЫЕ ПОЛЯ:",
            font=('Arial', 10, 'bold')
        ).pack(anchor='w', pady=(10, 5))

        for role, label_text in self.REQUIRED_ROLES.items():
            row_frame = ttk.Frame(self.scrollable_frame)
            row_frame.pack(fill='x', pady=3)

            ttk.Label(row_frame, text=label_text, width=30, font=('Arial', 10)).pack(side='left')

            cb = ttk.Combobox(
                row_frame,
                values=self.available_columns,
                state='readonly',
                width=30,
                font=('Arial', 10)
            )
            cb.pack(side='left', padx=10)

            detected_col = self.current_roles.get(role)
            if detected_col and detected_col in self.available_columns:
                cb.set(detected_col)
            else:
                cb.set("— Не выбрано —")

            self.comboboxes[role] = cb

        # Опциональные роли
        ttk.Label(
            self.scrollable_frame,
            text="ОПЦИОНАЛЬНЫЕ ПОЛЯ (можно оставить пустыми):",
            font=('Arial', 10, 'bold')
        ).pack(anchor='w', pady=(15, 5))

        for role, label_text in self.OPTIONAL_ROLES.items():
            row_frame = ttk.Frame(self.scrollable_frame)
            row_frame.pack(fill='x', pady=3)

            ttk.Label(row_frame, text=label_text, width=30, font=('Arial', 10)).pack(side='left')

            cb = ttk.Combobox(
                row_frame,
                values=self.available_columns,
                state='readonly',
                width=30,
                font=('Arial', 10)
            )
            cb.pack(side='left', padx=10)

            detected_col = self.current_roles.get(role)
            if detected_col and detected_col in self.available_columns:
                cb.set(detected_col)
            else:
                cb.set("— Не выбрано —")

            self.comboboxes[role] = cb

        # Кнопки управления (вне прокручиваемой области, всегда видны)
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill='x', pady=(15, 5))

        ttk.Button(
            btn_frame,
            text="❌ Отмена",
            command=self._on_cancel,
            width=15
        ).pack(side='left', padx=5)

        ttk.Button(
            btn_frame,
            text="✅ Применить",
            command=self._on_apply,
            width=15
        ).pack(side='right', padx=5)

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
        """Показывает диалог и возвращает обновлённый словарь ролей"""
        self.parent.wait_window(self.dialog)
        return self.result_roles