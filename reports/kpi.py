"""
Расчёт KPI-метрик
"""

import pandas as pd
from typing import Dict, Any


class KPIReporter:
    """Генератор KPI-показателей"""

    @staticmethod
    def calculate(df: pd.DataFrame) -> Dict[str, Any]:
        """
        Расчёт основных KPI по объединённому DataFrame

        Args:
            df: Очищенный и объединённый DataFrame с данными о продажах

        Returns:
            Словарь с рассчитанными метриками
        """
        if df.empty:
            return {
                'total_rows': 0,
                'total_units_sold': 0,
                'total_revenue': 0.0,
                'date_min': None,
                'date_max': None
            }

        return {
            'total_rows': int(len(df)),
            'total_units_sold': int(df['units_sold'].sum()),
            'total_revenue': float(df['revenue'].sum()),
            'date_min': df['date'].min().strftime('%Y-%m-%d'),
            'date_max': df['date'].max().strftime('%Y-%m-%d')
        }