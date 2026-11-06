"""
Логика фильтрации данных
"""

import pandas as pd
from typing import List, Optional
from datetime import datetime


class DataFilter:
    """Фильтр для DataFrame с данными о продажах"""

    @staticmethod
    def apply(
            df: pd.DataFrame,
            regions: Optional[List[str]] = None,
            products: Optional[List[str]] = None,
            date_from: Optional[str] = None,
            date_to: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Применение фильтров к DataFrame

        Args:
            df: Исходный DataFrame
            regions: Список регионов для фильтрации (None = все)
            products: Список продуктов для фильтрации (None = все)
            date_from: Начальная дата в формате 'YYYY-MM-DD' (None = без ограничения)
            date_to: Конечная дата в формате 'YYYY-MM-DD' (None = без ограничения)

        Returns:
            Отфильтрованный DataFrame
        """
        if df.empty:
            return df

        filtered = df.copy()

        # Фильтр по регионам
        if regions and len(regions) > 0:
            filtered = filtered[filtered['region'].isin(regions)]

        # Фильтр по продуктам
        if products and len(products) > 0:
            filtered = filtered[filtered['product'].isin(products)]

        # Фильтр по датам
        if date_from:
            try:
                date_from_dt = pd.to_datetime(date_from)
                filtered = filtered[filtered['date'] >= date_from_dt]
            except ValueError:
                pass

        if date_to:
            try:
                date_to_dt = pd.to_datetime(date_to)
                # Добавляем конец дня, чтобы включить весь день
                date_to_dt = date_to_dt + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
                filtered = filtered[filtered['date'] <= date_to_dt]
            except ValueError:
                pass

        return filtered.reset_index(drop=True)

    @staticmethod
    def get_unique_values(df: pd.DataFrame, column: str) -> List[str]:
        """
        Получение уникальных значений столбца для заполнения фильтров

        Args:
            df: DataFrame
            column: Название столбца

        Returns:
            Отсортированный список уникальных значений
        """
        if column not in df.columns:
            return []
        return sorted(df[column].dropna().unique().tolist())

    @staticmethod
    def get_date_range(df: pd.DataFrame) -> tuple:
        """
        Получение минимальной и максимальной даты в данных

        Returns:
            Кортеж (min_date, max_date) в формате 'YYYY-MM-DD'
        """
        if df.empty or 'date' not in df.columns:
            return (None, None)

        min_date = df['date'].min().strftime('%Y-%m-%d')
        max_date = df['date'].max().strftime('%Y-%m-%d')
        return (min_date, max_date)