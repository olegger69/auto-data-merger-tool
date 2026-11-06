"""
Панель импорта файлов
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinter import simpledialog
import threading
from core.merger import DataMerger
from reports.kpi import KPIReporter
from reports.summaries import SummaryReporter


class FilePanel:
    """Панель для выбора и импорта файлов"""

    def __init__(self, parent, main_window):
        self.parent = parent
        self.main_window = main_window
        self.merger = DataMerger()
        self.selected_files = []  # Список выбранных файлов

        self.frame = ttk.Frame(parent)
        self._create_widgets()

    def _create_widgets(self):
        """Создание виджетов панели импорта"""
        # Верхняя часть: кнопки управления
        control_frame = ttk.Frame(self.frame)
        control_frame.pack(fill='x', padx=10, pady=10)

        add_btn = ttk.Button(
            control_frame,
            text="➕ Добавить файлы",
            command=self._add_files
        )
        add_btn.pack(side='left', padx=5)

        clear_btn = ttk.Button(
            control_frame,
            text="🗑️ Очистить список",
            command=self._clear_files
        )
        clear_btn.pack(side='left', padx=5)

        merge_btn = ttk.Button(
            control_frame,
            text="🔗 Объединить файлы",
            command=self._merge_files
        )
        merge_btn.pack(side='right', padx=5)

        # Средняя часть: список файлов
        list_frame = ttk.LabelFrame(self.frame, text="Выбранные файлы", padding=10)
        list_frame.pack(fill='both', expand=True, padx=10, pady=5)

        # Treeview для списка файлов
        columns = ('filename', 'rows', 'status')
        self.file_tree = ttk.Treeview(
            list_frame,
            columns=columns,
            show='headings',
            height=10
        )

        self.file_tree.heading('filename', text='Имя файла')
        self.file_tree.heading('rows', text='Строк')
        self.file_tree.heading('status', text='Статус')

        self.file_tree.column('filename', width=400, minwidth=200)
        self.file_tree.column('rows', width=100, minwidth=80, anchor='center')
        self.file_tree.column('status', width=150, minwidth=100)

        # Скроллбар
        scrollbar = ttk.Scrollbar(
            list_frame,
            orient='vertical',
            command=self.file_tree.yview
        )
        self.file_tree.configure(yscrollcommand=scrollbar.set)

        self.file_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        # Кнопка удаления выбранного файла
        remove_btn = ttk.Button(
            list_frame,
            text="Удалить выбранный",
            command=self._remove_selected
        )
        remove_btn.pack(pady=5)

        # Нижняя часть: прогресс-бар
        self.progress_var = tk.DoubleVar(value=0)
        self.progress_bar = ttk.Progressbar(
            self.frame,
            variable=self.progress_var,
            maximum=100,
            mode='indeterminate'
        )
        self.progress_bar.pack(fill='x', padx=10, pady=5)
        self.progress_bar.pack_forget()  # Скрыт по умолчанию

    def _add_files(self):
        """Открытие диалога выбора файлов"""
        files = filedialog.askopenfilenames(
            title="Выберите файлы для импорта",
            filetypes=[
                ("Excel файлы", "*.xlsx *.xls"),
                ("CSV файлы", "*.csv"),
                ("Все поддерживаемые", "*.xlsx *.xls *.csv"),
                ("Все файлы", "*.*")
            ]
        )

        if files:
            for file_path in files:
                if file_path not in self.selected_files:
                    self.selected_files.append(file_path)
                    self.file_tree.insert('', 'end', values=(file_path, '—', 'Ожидает'))

            self.main_window.set_status(f"Добавлено файлов: {len(self.selected_files)}")

    def _clear_files(self):
        """Очистка списка файлов"""
        self.selected_files = []
        for item in self.file_tree.get_children():
            self.file_tree.delete(item)
        self.main_window.set_status("Список файлов очищен")

    def _remove_selected(self):
        """Удаление выбранного файла из списка"""
        selected = self.file_tree.selection()
        if selected:
            item = self.file_tree.item(selected[0])
            file_path = item['values'][0]
            self.selected_files.remove(file_path)
            self.file_tree.delete(selected[0])
            self.main_window.set_status(f"Удалён файл: {file_path}")

    def _merge_files(self):
        """Запуск объединения файлов в фоновом потоке"""
        if not self.selected_files:
            messagebox.showwarning("Внимание", "Сначала добавьте хотя бы один файл!")
            return

        # Показываем прогресс-бар
        self.progress_bar.pack(fill='x', padx=10, pady=5)
        self.progress_bar.start(10)

        # Запускаем обработку в отдельном потоке
        thread = threading.Thread(target=self._merge_worker, daemon=True)
        thread.start()

    def _merge_worker(self):
        """Фоновая задача объединения файлов"""
        try:
            self.main_window.set_status("Обработка файлов...")

            # Объединение данных
            merged_df = self.merger.merge_files(self.selected_files)

            # Расчёт сводок и KPI
            summaries = SummaryReporter.generate_all(merged_df)
            kpi = KPIReporter.calculate(merged_df)

            # Проверка ошибок
            errors = self.merger.get_errors()

            # Возвращаемся в главный поток для обновления UI
            self.frame.after(0, self._on_merge_complete, merged_df, summaries, kpi, errors)

        except Exception as e:
            self.frame.after(0, self._on_merge_error, str(e))

    def _on_merge_complete(self, merged_df, summaries, kpi, errors):
        """Обработка успешного завершения объединения"""
        self.progress_bar.stop()
        self.progress_bar.pack_forget()

        # Показываем предупреждения, если есть
        if errors:
            error_text = "\n".join(errors)
            messagebox.showwarning(
                "Предупреждения при обработке",
                f"Следующие файлы не удалось обработать:\n\n{error_text}"
            )

        # Обновляем статус в списке файлов
        for item in self.file_tree.get_children():
            self.file_tree.item(item, values=(
                self.file_tree.item(item)['values'][0],
                self.file_tree.item(item)['values'][1],
                '✅ Обработан'
            ))

        # Передаём данные в главное окно
        self.main_window.on_data_merged(merged_df, summaries, kpi)

    def _on_merge_error(self, error_message):
        """Обработка ошибки при объединении"""
        self.progress_bar.stop()
        self.progress_bar.pack_forget()
        messagebox.showerror("Ошибка", f"Не удалось объединить файлы:\n\n{error_message}")
        self.main_window.set_status("❌ Ошибка при объединении")
