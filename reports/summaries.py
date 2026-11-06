"""
Генерация сводных таблиц
"""

import pandas as pd
from typing import Dict


class SummaryReporter:
    """Генератор сводных отчётов"""

    @staticmethod
    def generate_all(df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
        """
        Генерация всех сводных таблиц

        Args:
            df: Очищенный и объединённый DataFrame

        Returns:
            Словарь с названиями отчётов в качестве ключей и DataFrame в качестве значений
        """
        if df.empty:
            return {
                'by_product': pd.DataFrame(columns=['product', 'revenue']),
                'by_region': pd.DataFrame(columns=['region', 'revenue']),
                'by_month': pd.DataFrame(columns=['month', 'revenue'])
            }

        # 1. Выручка по продуктам
        by_product = (
            df.groupby('product')['revenue']
            .sum()
            .reset_index()
            .sort_values('revenue', ascending=False)
            .round(2)
        )

        # 2. Выручка по регионам
        by_region = (
            df.groupby('region')['revenue']
            .sum()
            .reset_index()
            .sort_values('revenue', ascending=False)
            .round(2)
        )

        # 3. Динамика выручки по месяцам
        # Создаём колонку с годом и месяцем для группировки
        df_with_month = df.copy()
        df_with_month['month'] = df_with_month['date'].dt.to_period('M').astype(str)

        by_month = (
            df_with_month.groupby('month')['revenue']
            .sum()
            .reset_index()
            .sort_values('month')
            .round(2)
        )
        # Переименуем колонку для удобства отображения
        by_month = by_month.rename(columns={'month': 'period'})

        return {
            'by_product': by_product,
            'by_region': by_region,
            'by_month': by_month
        }
