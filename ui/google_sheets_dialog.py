"""
Диалог импорта из Google Sheets
"""

import tkinter as tk
from tkinter import ttk, messagebox
from core.google_sheets import GoogleSheetsImporter


class GoogleSheetsDialog:
    """Диалог для импорта данных из Google Таблиц"""

    PLACEHOLDER = "https://docs.google.com/spreadsheets/d/ID_ТАБЛИЦЫ/edit"

    def __init__(self, parent):
        self.parent = parent
        self.result_df = None
        self.result_error = None

        self.dialog = tk.Toplevel(parent)
        self.dialog.title("📊 Импорт из Google Sheets")
        self.dialog.geometry("650x450")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)

        # НЕ используем grab_set() — он блокирует Ctrl+V в некоторых системах
        # self.dialog.grab_set()

        self.dialog.update_idletasks()
        x = parent.winfo_rootx() + (parent.winfo_width() // 2) - 325
        y = parent.winfo_rooty() + (parent.winfo_height() // 2) - 225
        self.dialog.geometry(f"+{max(0, x)}+{max(0, y)}")

        self._create_widgets()
        self.dialog.protocol("WM_DELETE_WINDOW", self._on_cancel)

        # Делаем окно модальным через атрибут (альтернатива grab_set)
        self.dialog.attributes('-topmost', True)

    def _create_widgets(self):
        """Создание виджетов диалога"""
        main_frame = ttk.Frame(self.dialog, padding=20)
        main_frame.pack(fill='both', expand=True)

        # Заголовок
        ttk.Label(
            main_frame,
            text="📊 Импорт данных из Google Таблиц",
            font=('Arial', 14, 'bold')
        ).pack(pady=(0, 10))

        # Инструкция
        instruction = (
            "Вставьте URL публичной Google Таблицы.\n"
            "Таблица должна быть доступна по ссылке:\n"
            "Файл → Поделиться → Доступ по ссылке → 'Все, у кого есть ссылка'"
        )
        ttk.Label(
            main_frame,
            text=instruction,
            font=('Arial', 9),
            foreground='gray',
            justify='center'
        ).pack(pady=(0, 15))

        # Поле ввода URL — используем tk.Entry вместо ttk.Entry для надёжности
        url_frame = ttk.LabelFrame(main_frame, text="URL таблицы", padding=10)
        url_frame.pack(fill='x', pady=5)

        # Контейнер для поля и кнопки вставки
        entry_container = ttk.Frame(url_frame)
        entry_container.pack(fill='x', pady=5)

        # Используем tk.Entry — он надёжнее работает с вставкой
        self.url_entry = tk.Entry(
            entry_container,
            font=('Arial', 10),
            width=55,
            fg='gray'
        )
        self.url_entry.pack(side='left', fill='x', expand=True, padx=(0, 5))
        self.url_entry.insert(0, self.PLACEHOLDER)

        # Кнопка "Вставить" — запасной вариант, если Ctrl+V не работает
        paste_btn = ttk.Button(
            entry_container,
            text="📋 Вставить",
            command=self._paste_from_clipboard,
            width=12
        )
        paste_btn.pack(side='right')

        # Привязываем события для placeholder
        self.url_entry.bind('<FocusIn>', self._on_focus_in)
        self.url_entry.bind('<FocusOut>', self._on_focus_out)

        # Явная привязка Ctrl+V
        self.url_entry.bind('<Control-v>', self._on_paste)
        self.url_entry.bind('<Control-V>', self._on_paste)

        # Кнопка проверки
        ttk.Button(
            url_frame,
            text="🔍 Проверить URL",
            command=self._validate_url
        ).pack(pady=5)

        # Статус
        self.status_label = ttk.Label(
            main_frame,
            text="",
            font=('Arial', 10)
        )
        self.status_label.pack(pady=10)

        # Кнопки
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill='x', pady=(15, 0))

        ttk.Button(btn_frame, text="❌ Отмена", command=self._on_cancel, width=15).pack(side='left')
        ttk.Button(btn_frame, text="📥 Импортировать", command=self._on_import, width=15).pack(side='right')

    def _paste_from_clipboard(self):
        """Вставка из буфера обмена через кнопку"""
        try:
            clipboard_text = self.dialog.clipboard_get()
            if clipboard_text:
                # Очищаем placeholder, если он есть
                if self.url_entry.get() == self.PLACEHOLDER:
                    self.url_entry.delete(0, 'end')
                    self.url_entry.configure(fg='black')

                # Вставляем текст
                self.url_entry.delete(0, 'end')
                self.url_entry.insert(0, clipboard_text.strip())

                self.status_label.config(text="✅ Текст вставлен из буфера", foreground='green')
        except tk.TclError:
            self.status_label.config(text="❌ Буфер обмена пуст", foreground='red')

    def _on_paste(self, event):
        """Обработка Ctrl+V"""
        # Разрешаем стандартную вставку
        return

    def _on_focus_in(self, event):
        """Обработка получения фокуса"""
        if self.url_entry.get() == self.PLACEHOLDER:
            self.url_entry.delete(0, 'end')
            self.url_entry.configure(fg='black')

    def _on_focus_out(self, event):
        """Обработка потери фокуса"""
        if not self.url_entry.get():
            self.url_entry.insert(0, self.PLACEHOLDER)
            self.url_entry.configure(fg='gray')

    def _validate_url(self):
        """Проверка URL"""
        url = self.url_entry.get().strip()

        if url == self.PLACEHOLDER or not url:
            self.status_label.config(text="❌ Введите URL таблицы", foreground='red')
            return

        is_valid, message = GoogleSheetsImporter.validate_url(url)

        if is_valid:
            self.status_label.config(text=f"✅ {message}", foreground='green')
        else:
            self.status_label.config(text=f"❌ {message}", foreground='red')

    def _on_import(self):
        """Импорт данных"""
        url = self.url_entry.get().strip()

        if url == self.PLACEHOLDER or not url:
            self.status_label.config(text="❌ Введите корректный URL Google Sheets", foreground='red')
            return

        if 'docs.google.com' not in url:
            self.status_label.config(text="❌ URL должен содержать 'docs.google.com'", foreground='red')
            return

        self.status_label.config(text="⏳ Загрузка данных...", foreground='blue')
        self.dialog.update_idletasks()

        try:
            df = GoogleSheetsImporter.import_from_url(url)

            if df.empty:
                self.status_label.config(text="⚠️ Таблица пустая", foreground='orange')
                return

            self.result_df = df
            self.status_label.config(
                text=f"✅ Загружено {len(df)} строк, {len(df.columns)} столбцов",
                foreground='green'
            )

            # Закрываем диалог через небольшую задержку
            self.dialog.after(1000, self.dialog.destroy)

        except Exception as e:
            self.status_label.config(text=f"❌ {str(e)}", foreground='red')
            self.result_error = str(e)

    def _on_cancel(self):
        """Отмена"""
        self.result_df = None
        self.dialog.destroy()

    def show(self) -> tuple:
        """
        Показать диалог

        Returns:
            (DataFrame, ошибка) — одно из значений будет None
        """
        self.parent.wait_window(self.dialog)
        return self.result_df, self.result_error