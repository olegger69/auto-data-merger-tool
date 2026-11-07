"""
Диалог импорта данных из SQL баз данных
"""

import tkinter as tk
from tkinter import ttk, messagebox
from core.sql_importer import SQLImporter


class SQLDialog:
    """Диалог для подключения к SQL и импорта данных"""

    def __init__(self, parent):
        self.parent = parent
        self.result_df = None
        self.result_error = None

        self.dialog = tk.Toplevel(parent)
        self.dialog.title("🗄️ Импорт из SQL")
        self.dialog.geometry("550x500")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()

        self.dialog.update_idletasks()
        x = parent.winfo_rootx() + (parent.winfo_width() // 2) - 275
        y = parent.winfo_rooty() + (parent.winfo_height() // 2) - 250
        self.dialog.geometry(f"+{max(0, x)}+{max(0, y)}")

        self._create_widgets()
        self.dialog.protocol("WM_DELETE_WINDOW", self._on_cancel)

    def _create_widgets(self):
        """Создание виджетов диалога"""
        main_frame = ttk.Frame(self.dialog, padding=20)
        main_frame.pack(fill='both', expand=True)

        ttk.Label(main_frame, text="🗄️ Подключение к базе данных", font=('Arial', 14, 'bold')).pack(pady=(0, 10))

        # Тип базы данных
        db_frame = ttk.LabelFrame(main_frame, text="Тип базы данных", padding=10)
        db_frame.pack(fill='x', pady=5)

        self.dialect_var = tk.StringVar(value="sqlite")
        ttk.Radiobutton(db_frame, text="SQLite (файл)", variable=self.dialect_var, value="sqlite",
                        command=self._toggle_fields).pack(side='left', padx=10)
        ttk.Radiobutton(db_frame, text="PostgreSQL", variable=self.dialect_var, value="postgresql",
                        command=self._toggle_fields).pack(side='left', padx=10)
        ttk.Radiobutton(db_frame, text="MySQL", variable=self.dialect_var, value="mysql",
                        command=self._toggle_fields).pack(side='left', padx=10)

        # Поля подключения
        self.conn_frame = ttk.LabelFrame(main_frame, text="Параметры подключения", padding=10)
        self.conn_frame.pack(fill='x', pady=5)

        # SQLite: только путь к файлу
        self.sqlite_path_var = tk.StringVar()
        self.sqlite_entry = ttk.Entry(self.conn_frame, textvariable=self.sqlite_path_var, width=50)
        self.sqlite_entry.pack(fill='x', pady=5)
        ttk.Button(self.conn_frame, text="📂 Выбрать файл", command=self._browse_sqlite).pack(pady=5)

        # PostgreSQL / MySQL: Host, Port, User, Password, DB
        self.advanced_frame = ttk.Frame(self.conn_frame)

        row1 = ttk.Frame(self.advanced_frame)
        row1.pack(fill='x', pady=2)
        ttk.Label(row1, text="Host:", width=10).pack(side='left')
        self.host_var = tk.StringVar(value="localhost")
        ttk.Entry(row1, textvariable=self.host_var, width=20).pack(side='left', padx=5)

        ttk.Label(row1, text="Port:", width=5).pack(side='left')
        self.port_var = tk.StringVar(value="5432")
        ttk.Entry(row1, textvariable=self.port_var, width=10).pack(side='left', padx=5)

        row2 = ttk.Frame(self.advanced_frame)
        row2.pack(fill='x', pady=2)
        ttk.Label(row2, text="User:", width=10).pack(side='left')
        self.user_var = tk.StringVar()
        ttk.Entry(row2, textvariable=self.user_var, width=20).pack(side='left', padx=5)

        ttk.Label(row2, text="Password:", width=8).pack(side='left')
        self.pass_var = tk.StringVar()
        ttk.Entry(row2, textvariable=self.pass_var, width=18, show="*").pack(side='left', padx=5)

        row3 = ttk.Frame(self.advanced_frame)
        row3.pack(fill='x', pady=2)
        ttk.Label(row3, text="Database:", width=10).pack(side='left')
        self.db_var = tk.StringVar()
        ttk.Entry(row3, textvariable=self.db_var, width=40).pack(side='left', padx=5)

        self.advanced_frame.pack(fill='x', pady=5)

        # SQL запрос
        query_frame = ttk.LabelFrame(main_frame, text="SQL запрос", padding=10)
        query_frame.pack(fill='both', expand=True, pady=5)

        self.query_text = tk.Text(query_frame, height=6, font=('Consolas', 10))
        self.query_text.pack(fill='both', expand=True)
        self.query_text.insert('1.0', "SELECT * FROM sales")

        # Кнопки
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill='x', pady=(10, 0))

        ttk.Button(btn_frame, text="❌ Отмена", command=self._on_cancel, width=15).pack(side='left')
        ttk.Button(btn_frame, text="📥 Импортировать", command=self._on_import, width=15).pack(side='right')

        self._toggle_fields()

    def _toggle_fields(self):
        """Переключение видимости полей в зависимости от типа БД"""
        dialect = self.dialect_var.get()
        if dialect == 'sqlite':
            self.sqlite_entry.pack(fill='x', pady=5)
            self.advanced_frame.pack_forget()
            self.port_var.set("")
        else:
            self.sqlite_entry.pack_forget()
            self.advanced_frame.pack(fill='x', pady=5)
            if dialect == 'postgresql':
                self.port_var.set("5432")
            elif dialect == 'mysql':
                self.port_var.set("3306")

    def _browse_sqlite(self):
        """Выбор файла SQLite"""
        from tkinter import filedialog
        filepath = filedialog.askopenfilename(
            title="Выберите файл базы данных SQLite",
            filetypes=[("SQLite файлы", "*.db *.sqlite *.sqlite3"), ("Все файлы", "*.*")]
        )
        if filepath:
            self.sqlite_path_var.set(filepath)

    def _on_import(self):
        """Выполнение импорта"""
        dialect = self.dialect_var.get()

        try:
            if dialect == 'sqlite':
                db_path = self.sqlite_path_var.get().strip()
                if not db_path:
                    messagebox.showwarning("Внимание", "Укажите путь к файлу SQLite")
                    return
                conn_str = SQLImporter.build_connection_string(dialect, "", "", "", "", db_path)
            else:
                host = self.host_var.get().strip()
                port = self.port_var.get().strip()
                user = self.user_var.get().strip()
                password = self.pass_var.get()
                database = self.db_var.get().strip()

                if not all([host, port, user, database]):
                    messagebox.showwarning("Внимание", "Заполните все обязательные поля подключения")
                    return

                conn_str = SQLImporter.build_connection_string(dialect, user, password, host, port, database)

            query = self.query_text.get('1.0', 'end').strip()
            if not query:
                messagebox.showwarning("Внимание", "Введите SQL запрос")
                return

            self.dialog.update_idletasks()
            df = SQLImporter.import_from_query(conn_str, query)

            if df.empty:
                messagebox.showinfo("Информация", "Запрос выполнен, но данных не найдено.")
                self.result_df = None
            else:
                self.result_df = df
                self.dialog.destroy()

        except Exception as e:
            messagebox.showerror("Ошибка подключения или запроса", str(e))
            self.result_error = str(e)

    def _on_cancel(self):
        """Отмена"""
        self.result_df = None
        self.dialog.destroy()

    def show(self) -> tuple:
        """Показать диалог"""
        self.parent.wait_window(self.dialog)
        return self.result_df, self.result_error