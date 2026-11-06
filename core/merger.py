"""
Объединение и дедупликация данных
"""

import pandas as pd
from typing import List
from core.loader import DataLoader
from core.validator import DataValidator


class DataMerger:
    """Менеджер объединения данных"""

    def __init__(self):
        self.loader = DataLoader()
        self.errors = []
        self.stats = {
            'files_processed': 0,
            'total_rows_before_dedup': 0,
            'total_rows_after_dedup': 0,
            'duplicates_removed': 0
        }

    def merge_dataframes(self, dataframes: List[pd.DataFrame]) -> pd.DataFrame:
        """
        Объединение уже подготовленных и замапленных DataFrame.
        """
        if not dataframes:
            raise ValueError("Нет данных для объединения")

        self.stats = {
            'files_processed': len(dataframes),
            'total_rows_before_dedup': 0,
            'total_rows_after_dedup': 0,
            'duplicates_removed': 0
        }

        # 1. Объединение всех DataFrame
        merged_df = pd.concat(dataframes, ignore_index=True)
        self.stats['total_rows_before_dedup'] = len(merged_df)

        # 2. Удаление дубликатов
        initial_len = len(merged_df)
        merged_df = merged_df.drop_duplicates()
        final_len = len(merged_df)

        self.stats['total_rows_after_dedup'] = final_len
        self.stats['duplicates_removed'] = initial_len - final_len

        # 3. Сортировка по дате для удобства
        if 'date' in merged_df.columns:
            merged_df = merged_df.sort_values('date').reset_index(drop=True)

        return merged_df

    def get_errors(self) -> List[str]:
        """Получение списка ошибок при обработке"""
        return self.errors.copy()

    def get_stats(self) -> dict:
        """Получение статистики объединения"""
        return self.stats.copy()