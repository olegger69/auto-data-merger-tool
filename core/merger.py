"""
Объединение и дедупликация данных из нескольких файлов
"""

import pandas as pd
from typing import List, Tuple
from core.loader import DataLoader
from core.validator import DataValidator


class DataMerger:
    """Менеджер объединения данных"""

    def __init__(self):
        self.loader = DataLoader()
        self.errors = []  # Список ошибок при обработке файлов
        self.stats = {
            'files_processed': 0,
            'total_rows_before_dedup': 0,
            'total_rows_after_dedup': 0
        }

    def merge_files(self, file_paths: List[str], subset: List[str] = None) -> pd.DataFrame:
        """
        Объединение нескольких файлов в один DataFrame

        Args:
            file_paths: Список путей к файлам
            subset: Список столбцов для поиска дубликатов (None = все столбцы)

        Returns:
            Объединённый и очищенный DataFrame
        """
        dataframes = []
        self.errors = []
        self.stats = {'files_processed': 0, 'total_rows_before_dedup': 0, 'total_rows_after_dedup': 0}
        self.loader.clear()

        for file_path in file_paths:
            try:
                # 1. Загрузка
                df = self.loader.load_file(file_path)

                # 2. Валидация и очистка (включая расчёт revenue)
                clean_df = DataValidator.process(df)

                dataframes.append(clean_df)
                self.stats['files_processed'] += 1
                self.stats['total_rows_before_dedup'] += len(clean_df)

            except Exception as e:
                self.errors.append(f"Ошибка в файле '{file_path}': {str(e)}")

        if not dataframes:
            raise ValueError("Не удалось загрузить ни один файл. Проверьте логи ошибок.")

        # 3. Объединение всех DataFrame
        merged_df = pd.concat(dataframes, ignore_index=True)

        # 4. Удаление дубликатов
        initial_len = len(merged_df)
        merged_df = merged_df.drop_duplicates(subset=subset)
        final_len = len(merged_df)

        self.stats['total_rows_after_dedup'] = final_len
        self.stats['duplicates_removed'] = initial_len - final_len

        # 5. Сортировка по дате для удобства
        if 'date' in merged_df.columns:
            merged_df = merged_df.sort_values('date').reset_index(drop=True)

        return merged_df

    def get_errors(self) -> List[str]:
        """Получение списка ошибок при обработке"""
        return self.errors.copy()

    def get_stats(self) -> dict:
        """Получение статистики объединения"""
        return self.stats.copy()

    def get_loaded_files_info(self) -> List[dict]:
        """Получение информации о успешно загруженных файлах"""
        return self.loader.get_loaded_files_info()
