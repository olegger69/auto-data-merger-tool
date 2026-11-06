"""
Панель импорта файлов с поддержкой маппинга столбцов
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import os
from core.merger import DataMerger
from core.loader import DataLoader
from core.validator import DataValidator
from reports.kpi import KPIReporter
from reports.summaries import SummaryReporter
from ui.column_mapping_dialog import ColumnMappingDialog


class FilePanel:
    """Панель для выбора и импорта файлов"""

    def __init__(self, parent, main_window):
        self.parent = parent
        self.main_window = main_window
        self.merger = DataMerger()
        self.selected_files = []

        self.frame = ttk.Frame(parent)
        self._create_widgets()

    def _create_widgets(self):
        """Создание виджетов панели импорта"""
        control_frame = ttk.Frame(self.frame)
        control_frame.pack(fill='x', padx=10, pady=10)

        add_btn = ttk.Button(control_frame, text="➕ Добавить файлы", command=self._add_files)
        add_btn.pack(side='left', padx=5)

        clear_btn = ttk.Button(control_frame, text="🗑️ Очистить список", command=self._clear_files)
        clear_btn.pack(side='left', padx=5)

        merge_btn = ttk.Button(control_frame, text="🔗 Объединить файлы", command=self._merge_files)
        merge_btn.pack(side='right', padx=5)

        list_frame = ttk.LabelFrame(self.frame, text="Выбранные файлы", padding=10)
        list_frame.pack(fill='both', expand=True, padx=10, pady=5)

        columns = ('filename', 'rows', 'status')
        self.file_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=10)

        self.file_tree.heading('filename', text='Имя файла')
        self.file_tree.heading('rows', text='Строк')
        self.file_tree.heading('status', text='Статус')

        self.file_tree.column('filename', width=400, minwidth=200)
        self.file_tree.column('rows', width=100, minwidth=80, anchor='center')
        self.file_tree.column('status', width=150, minwidth=100)

        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.file_tree.yview)
        self.file_tree.configure(yscrollcommand=scrollbar.set)

        self.file_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        remove_btn = ttk.Button(list_frame, text="Удалить выбранный", command=self._remove_selected)
        remove_btn.pack(pady=5)

        self.progress_var = tk.DoubleVar(value=0)
        self.progress_bar = ttk.Progressbar(self.frame, variable=self.progress_var, maximum=100, mode='indeterminate')
        self.progress_bar.pack(fill='x', padx=10, pady=5)
        self.progress_bar.pack_forget()

    def _add_files(self):
        """Открытие диалога выбора файлов"""
        initial_dir = self.main_window.config.get('last_import_folder', '')

        files = filedialog.askopenfilenames(
            title="Выберите файлы для импорта",
            filetypes=[
                ("Excel файлы", "*.xlsx *.xls"),
                ("CSV файлы", "*.csv"),
                ("Все поддерживаемые", "*.xlsx *.xls *.csv"),
                ("Все файлы", "*.*")
            ],
            initialdir=initial_dir if initial_dir else ''
        )

        if files:
            last_folder = os.path.dirname(files[0])
            self.main_window.config.set_last_import_folder(last_folder)

            for file_path in files:
                if file_path not in self.selected_files:
                    self.selected_files.append(file_path)
                    self.file_tree.insert('', 'end', values=(file_path, '—', 'Ожидает'))

            self.main_window.set_status(f"Добавлено файлов: {len(self.selected_files)}")

    def _clear_files(self):
        self.selected_files = []
        for item in self.file_tree.get_children():
            self.file_tree.delete(item)
        self.main_window.set_status("Список файлов очищен")

    def _remove_selected(self):
        selected = self.file_tree.selection()
        if selected:
            item = self.file_tree.item(selected[0])
            file_path = item['values'][0]
            self.selected_files.remove(file_path)
            self.file_tree.delete(selected[0])
            self.main_window.set_status(f"Удалён файл: {file_path}")

    def _merge_files(self):
        """Проверка файлов, маппинг и запуск объединения"""
        if not self.selected_files:
            messagebox.showwarning("Внимание", "Сначала добавьте хотя бы один файл!")
            return

        self.main_window.set_status("Анализ структуры файлов...")
        prepared_dfs = []
        errors = []

        # Этап 1: Проверка и маппинг (в главном потоке, это быстро)
        for file_path in self.selected_files:
            try:
                # Загружаем и определяем роли
                df, roles = self.merger.loader.load_and_detect(file_path)
                is_complete, missing = DataLoader.check_roles_complete(roles)

                if not is_complete:
                    # Открываем диалог маппинга
                    dialog = ColumnMappingDialog(
                        self.main_window.root,
                        df.columns.tolist(),
                        roles
                    )
                    new_roles = dialog.show()

                    if new_roles is None:
                        errors.append(f"Файл '{os.path.basename(file_path)}': обработка отменена.")
                        continue

                    # Проверяем, выбрал ли пользователь все обязательные поля
                    is_now_complete, still_missing = DataLoader.check_roles_complete(new_roles)
                    if not is_now_complete:
                        errors.append(f"Файл '{os.path.basename(file_path)}': не выбраны столбцы {still_missing}.")
                        continue

                    # Применяем маппинг с выбранными ролями
                    df = DataLoader.apply_mapping(df, new_roles)
                else:
                    # Все роли определены автоматически — всё равно применяем маппинг
                    # для стандартизации имён столбцов
                    df = DataLoader.apply_mapping(df, roles)

                prepared_dfs.append(df)

                # Обновляем статус в дереве
                for item in self.file_tree.get_children():
                    if self.file_tree.item(item)['values'][0] == file_path:
                        self.file_tree.item(item, values=(file_path, len(df), '✅ Готов'))

            except Exception as e:
                errors.append(f"Файл '{os.path.basename(file_path)}': {str(e)}")
                for item in self.file_tree.get_children():
                    if self.file_tree.item(item)['values'][0] == file_path:
                        self.file_tree.item(item, values=(file_path, '—', '❌ Ошибка'))

        if not prepared_dfs:
            error_text = "\n".join(errors) if errors else "Не удалось подготовить ни один файл."
            messagebox.showerror("Ошибка", error_text)
            self.main_window.set_status("❌ Объединение прервано")
            return

        if errors:
            error_text = "\n".join(errors)
            messagebox.showwarning("Предупреждения", f"Некоторые файлы были пропущены:\n\n{error_text}")

        # Этап 2: Фоновая обработка (объединение и расчеты)
        self.progress_bar.pack(fill='x', padx=10, pady=5)
        self.progress_bar.start(10)

        thread = threading.Thread(target=self._merge_worker_bg, args=(prepared_dfs,), daemon=True)
        thread.start()

    def _merge_worker_bg(self, prepared_dfs):
        """Фоновая задача объединения и расчетов"""
        try:
            self.main_window.set_status("Объединение и расчет данных...")

            # 1. Объединение
            merged_df = self.merger.merge_dataframes(prepared_dfs)

            # 2. Валидация и очистка (приведение типов, расчет revenue)
            clean_df = DataValidator.process(merged_df)

            # 3. Расчет сводок и KPI
            summaries = SummaryReporter.generate_all(clean_df)
            kpi = KPIReporter.calculate(clean_df)

            # Возвращаемся в главный поток
            self.frame.after(0, self._on_merge_complete, clean_df, summaries, kpi)

        except Exception as e:
            self.frame.after(0, self._on_merge_error, str(e))

    def _on_merge_complete(self, merged_df, summaries, kpi):
        """Обработка успешного завершения"""
        self.progress_bar.stop()
        self.progress_bar.pack_forget()

        self.main_window.on_data_merged(merged_df, summaries, kpi)

    def _on_merge_error(self, error_message):
        """Обработка ошибки"""
        self.progress_bar.stop()
        self.progress_bar.pack_forget()
        messagebox.showerror("Ошибка", f"Не удалось объединить файлы:\n\n{error_message}")
        self.main_window.set_status("❌ Ошибка при объединении")