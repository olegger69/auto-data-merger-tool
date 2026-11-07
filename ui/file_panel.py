"""
Панель импорта файлов с поддержкой маппинга, предпросмотра, Google Sheets и SQL
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import os
import pandas as pd

from core.merger import DataMerger
from core.loader import DataLoader
from core.validator import DataValidator
from reports.kpi import KPIReporter
from reports.summaries import SummaryReporter
from ui.column_mapping_dialog import ColumnMappingDialog
from ui.google_sheets_dialog import GoogleSheetsDialog
from ui.sql_dialog import SQLDialog


class FilePanel:
    """Панель для выбора и импорта данных из различных источников"""

    EXPORT_FILE_HINTS = ['merged_output', 'summary_report', 'dashboard_report']

    def __init__(self, parent, main_window):
        self.parent = parent
        self.main_window = main_window
        self.merger = DataMerger()
        self.selected_files = []  # Может содержать строки (пути) или dict (dataframe)

        self.frame = ttk.Frame(parent)
        self._create_widgets()

    def _create_widgets(self):
        """Создание виджетов панели импорта"""
        control_frame = ttk.Frame(self.frame)
        control_frame.pack(fill='x', padx=10, pady=10)

        add_btn = ttk.Button(control_frame, text="➕ Добавить файлы", command=self._add_files)
        add_btn.pack(side='left', padx=5)

        sheets_btn = ttk.Button(control_frame, text="📊 Google Sheets", command=self._import_from_google_sheets)
        sheets_btn.pack(side='left', padx=5)

        sql_btn = ttk.Button(control_frame, text="🗄️ SQL База данных", command=self._import_from_sql)
        sql_btn.pack(side='left', padx=5)

        clear_btn = ttk.Button(control_frame, text="🗑️ Очистить список", command=self._clear_files)
        clear_btn.pack(side='left', padx=5)

        merge_btn = ttk.Button(control_frame, text="🔗 Объединить данные", command=self._merge_files)
        merge_btn.pack(side='right', padx=5)

        main_container = ttk.PanedWindow(self.frame, orient='horizontal')
        main_container.pack(fill='both', expand=True, padx=10, pady=5)

        left_frame = ttk.Frame(main_container)
        main_container.add(left_frame, weight=1)

        list_frame = ttk.LabelFrame(left_frame, text="Источники данных", padding=10)
        list_frame.pack(fill='both', expand=True)

        columns = ('filename', 'rows', 'status')
        self.file_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=10)

        self.file_tree.heading('filename', text='Источник / Имя файла')
        self.file_tree.heading('rows', text='Строк')
        self.file_tree.heading('status', text='Статус')

        self.file_tree.column('filename', width=300, minwidth=200)
        self.file_tree.column('rows', width=80, minwidth=60, anchor='center')
        self.file_tree.column('status', width=120, minwidth=80)

        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.file_tree.yview)
        self.file_tree.configure(yscrollcommand=scrollbar.set)

        self.file_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        remove_btn = ttk.Button(list_frame, text="Удалить выбранный", command=self._remove_selected)
        remove_btn.pack(pady=5)

        right_frame = ttk.Frame(main_container)
        main_container.add(right_frame, weight=1)

        preview_frame = ttk.LabelFrame(right_frame, text="👁️ Предпросмотр данных", padding=10)
        preview_frame.pack(fill='both', expand=True)

        self.preview_container = ttk.Frame(preview_frame)
        self.preview_container.pack(fill='both', expand=True)

        self.preview_placeholder = ttk.Label(
            self.preview_container,
            text="Выберите источник в списке слева,\nчтобы увидеть предпросмотр данных",
            font=('Arial', 11),
            foreground='gray',
            justify='center'
        )
        self.preview_placeholder.pack(expand=True)

        self.preview_tree = None

        self.progress_var = tk.DoubleVar(value=0)
        self.progress_bar = ttk.Progressbar(self.frame, variable=self.progress_var, maximum=100, mode='indeterminate')
        self.progress_bar.pack(fill='x', padx=10, pady=5)
        self.progress_bar.pack_forget()

        self.file_tree.bind('<<TreeviewSelect>>', self._on_file_select)

    def _is_export_file(self, file_path: str) -> bool:
        filename = os.path.basename(file_path).lower()
        return any(hint in filename for hint in self.EXPORT_FILE_HINTS)

    def _on_file_select(self, event):
        selected = self.file_tree.selection()
        if not selected:
            self._clear_preview()
            return

        item = self.file_tree.item(selected[0])
        source = item['values'][0]

        self._show_loading_preview()
        thread = threading.Thread(target=self._load_preview, args=(source,), daemon=True)
        thread.start()

    def _show_loading_preview(self):
        self._clear_preview()
        ttk.Label(self.preview_container, text="Загрузка предпросмотра...", font=('Arial', 10), foreground='gray').pack(
            expand=True)

    def _load_preview(self, source):
        try:
            df = None
            for item in self.selected_files:
                if isinstance(item, dict) and item.get('name') == source:
                    df = item['data']
                    break
                elif isinstance(item, str) and os.path.basename(item) == source:
                    ext = os.path.splitext(item)[1].lower()
                    if ext == '.csv':
                        df = pd.read_csv(item, nrows=10)
                    elif ext in ['.xlsx', '.xls']:
                        df = pd.read_excel(item, nrows=10)
                    break

            if df is not None:
                self.frame.after(0, self._display_preview, df, source)
            else:
                self.frame.after(0, self._show_preview_error, "Данные не найдены")
        except Exception as e:
            self.frame.after(0, self._show_preview_error, str(e))

    def _display_preview(self, df: pd.DataFrame, source: str):
        self._clear_preview()
        if df.empty:
            ttk.Label(self.preview_container, text="Данные пустые", font=('Arial', 10), foreground='gray').pack(
                expand=True)
            return

        preview_frame = ttk.Frame(self.preview_container)
        preview_frame.pack(fill='both', expand=True)

        cols = list(df.columns)
        self.preview_tree = ttk.Treeview(preview_frame, columns=cols, show='headings', height=min(len(df), 10))

        for col in cols:
            self.preview_tree.heading(col, text=str(col))
            self.preview_tree.column(col, width=120, minwidth=80)

        for _, row in df.iterrows():
            values = [str(val) if pd.notna(val) else '' for val in row]
            self.preview_tree.insert('', 'end', values=values)

        y_scrollbar = ttk.Scrollbar(preview_frame, orient='vertical', command=self.preview_tree.yview)
        x_scrollbar = ttk.Scrollbar(preview_frame, orient='horizontal', command=self.preview_tree.xview)
        self.preview_tree.configure(yscrollcommand=y_scrollbar.set, xscrollcommand=x_scrollbar.set)

        self.preview_tree.grid(row=0, column=0, sticky='nsew')
        y_scrollbar.grid(row=0, column=1, sticky='ns')
        x_scrollbar.grid(row=1, column=0, sticky='ew')

        preview_frame.grid_rowconfigure(0, weight=1)
        preview_frame.grid_columnconfigure(0, weight=1)

        ttk.Label(self.preview_container, text=f"📄 {source} | Показано строк: {len(df)}", font=('Arial', 9),
                  foreground='gray').pack(pady=(5, 0))

    def _show_preview_error(self, error_message):
        self._clear_preview()
        ttk.Label(self.preview_container, text=f"❌ Ошибка:\n{error_message}", font=('Arial', 10), foreground='red',
                  justify='center').pack(expand=True)

    def _clear_preview(self):
        for widget in self.preview_container.winfo_children():
            widget.destroy()
        self.preview_tree = None

    def _add_files(self):
        initial_dir = self.main_window.config.get('last_import_folder', '')
        files = filedialog.askopenfilenames(
            title="Выберите файлы для импорта",
            filetypes=[("Excel файлы", "*.xlsx *.xls"), ("CSV файлы", "*.csv"), ("Все файлы", "*.*")],
            initialdir=initial_dir if initial_dir else ''
        )

        if files:
            self.main_window.config.set_last_import_folder(os.path.dirname(files[0]))
            added = 0
            for file_path in files:
                if self._is_export_file(file_path):
                    messagebox.showwarning("Внимание",
                                           f"Файл '{os.path.basename(file_path)}' похож на экспорт приложения и пропущен.")
                    continue
                if file_path not in [item for item in self.selected_files if isinstance(item, str)]:
                    self.selected_files.append(file_path)
                    self.file_tree.insert('', 'end', values=(os.path.basename(file_path), '—', 'Ожидает'))
                    added += 1
            if added > 0:
                self.main_window.set_status(f"Добавлено файлов: {added}")

    def _import_from_google_sheets(self):
        dialog = GoogleSheetsDialog(self.main_window.root)
        df, error = dialog.show()
        if df is not None and not df.empty:
            name = f"Google_Sheets_{len([i for i in self.selected_files if isinstance(i, dict)]) + 1}"
            self.selected_files.append({'type': 'dataframe', 'name': name, 'data': df})
            self.file_tree.insert('', 'end', values=(name, len(df), '✅ Готов (Sheets)'))
            self.main_window.set_status(f"✅ Импортировано из Google Sheets: {len(df)} строк")
        elif error:
            messagebox.showerror("Ошибка импорта", error)

    def _import_from_sql(self):
        dialog = SQLDialog(self.main_window.root)
        df, error = dialog.show()
        if df is not None and not df.empty:
            name = f"SQL_Query_{len([i for i in self.selected_files if isinstance(i, dict)]) + 1}"
            self.selected_files.append({'type': 'dataframe', 'name': name, 'data': df})
            self.file_tree.insert('', 'end', values=(name, len(df), '✅ Готов (SQL)'))
            self.main_window.set_status(f"✅ Импортировано из SQL: {len(df)} строк")
        elif error:
            messagebox.showerror("Ошибка импорта", error)

    def _clear_files(self):
        self.selected_files = []
        for item in self.file_tree.get_children():
            self.file_tree.delete(item)
        self._clear_preview()
        self.main_window.set_status("Список источников очищен")

    def _remove_selected(self):
        selected = self.file_tree.selection()
        if selected:
            item = self.file_tree.item(selected[0])
            source = item['values'][0]
            self.selected_files = [i for i in self.selected_files if not (
                        isinstance(i, dict) and i.get('name') == source or isinstance(i, str) and os.path.basename(
                    i) == source)]
            self.file_tree.delete(selected[0])
            self._clear_preview()
            self.main_window.set_status(f"Удалён источник: {source}")

    def _merge_files(self):
        if not self.selected_files:
            messagebox.showwarning("Внимание", "Сначала добавьте хотя бы один источник данных!")
            return

        self.main_window.set_status("Анализ и подготовка данных...")
        prepared_dfs = []
        errors = []

        for item in self.selected_files:
            try:
                if isinstance(item, dict) and item.get('type') == 'dataframe':
                    df = item['data']
                    source_name = item['name']
                    roles = {}
                else:
                    file_path = item
                    source_name = os.path.basename(file_path)
                    df, roles = self.merger.loader.load_and_detect(file_path)

                is_complete, missing = DataLoader.check_roles_complete(roles)

                if not is_complete:
                    dialog = ColumnMappingDialog(self.main_window.root, df.columns.tolist(), roles)
                    new_roles = dialog.show()
                    if new_roles is None:
                        errors.append(f"'{source_name}': обработка отменена.")
                        continue
                    is_now_complete, still_missing = DataLoader.check_roles_complete(new_roles)
                    if not is_now_complete:
                        errors.append(f"'{source_name}': не выбраны обязательные столбцы {still_missing}.")
                        continue
                    df = DataLoader.apply_mapping(df, new_roles)
                elif isinstance(item, str):
                    df = DataLoader.apply_mapping(df, roles)

                prepared_dfs.append(df)

                for tree_item in self.file_tree.get_children():
                    if self.file_tree.item(tree_item)['values'][0] == source_name:
                        self.file_tree.item(tree_item, values=(source_name, len(df), '✅ Готов'))

            except Exception as e:
                errors.append(f"'{source_name}': {str(e)}")
                for tree_item in self.file_tree.get_children():
                    if self.file_tree.item(tree_item)['values'][0] == source_name:
                        self.file_tree.item(tree_item, values=(source_name, '—', '❌ Ошибка'))

        if not prepared_dfs:
            messagebox.showerror("Ошибка", "\n".join(errors) if errors else "Не удалось подготовить данные.")
            self.main_window.set_status("❌ Объединение прервано")
            return

        if errors:
            messagebox.showwarning("Предупреждения", "Некоторые источники пропущены:\n\n" + "\n".join(errors))

        self.progress_bar.pack(fill='x', padx=10, pady=5)
        self.progress_bar.start(10)

        thread = threading.Thread(target=self._merge_worker_bg, args=(prepared_dfs,), daemon=True)
        thread.start()

    def _merge_worker_bg(self, prepared_dfs):
        try:
            self.main_window.set_status("Объединение и расчет данных...")
            merged_df = self.merger.merge_dataframes(prepared_dfs)
            clean_df = DataValidator.process(merged_df)
            summaries = SummaryReporter.generate_all(clean_df)
            kpi = KPIReporter.calculate(clean_df)
            self.frame.after(0, self._on_merge_complete, clean_df, summaries, kpi)
        except Exception as e:
            import traceback
            self.frame.after(0, self._on_merge_error, f"{str(e)}\n\n{traceback.format_exc()}")

    def _on_merge_complete(self, merged_df, summaries, kpi):
        self.progress_bar.stop()
        self.progress_bar.pack_forget()
        self.main_window.on_data_merged(merged_df, summaries, kpi)

    def _on_merge_error(self, error_message):
        self.progress_bar.stop()
        self.progress_bar.pack_forget()
        messagebox.showerror("Ошибка при обработке данных", error_message)
        self.main_window.set_status("❌ Ошибка при объединении")