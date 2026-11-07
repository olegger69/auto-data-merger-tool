"""
Сравнение двух периодов с расчётом изменений
"""

import pandas as pd
from typing import Dict, Any, Optional


class PeriodComparator:
    """Сравнение метрик между двумя периодами"""

    @staticmethod
    def compare_periods(
            df: pd.DataFrame,
            period1_start: str,
            period1_end: str,
            period2_start: str,
            period2_end: str
    ) -> Dict[str, Any]:
        """
        Сравнение двух периодов

        Args:
            df: DataFrame с данными о продажах
            period1_start: Начало первого периода (YYYY-MM-DD)
            period1_end: Конец первого периода (YYYY-MM-DD)
            period2_start: Начало второго периода (YYYY-MM-DD)
            period2_end: Конец второго периода (YYYY-MM-DD)

        Returns:
            Словарь с метриками и изменениями
        """
        if df.empty or 'date' not in df.columns:
            return None

        # Фильтрация данных по периодам
        period1_mask = (df['date'] >= period1_start) & (df['date'] <= period1_end)
        period2_mask = (df['date'] >= period2_start) & (df['date'] <= period2_end)

        df_period1 = df[period1_mask]
        df_period2 = df[period2_mask]

        # Расчёт метрик для каждого периода
        metrics1 = PeriodComparator._calculate_metrics(df_period1, "Период 1")
        metrics2 = PeriodComparator._calculate_metrics(df_period2, "Период 2")

        # Расчёт изменений
        comparison = {
            'period1': metrics1,
            'period2': metrics2,
            'changes': {}
        }

        # Вычисляем изменения для каждой метрики
        for key in ['revenue', 'profit', 'units_sold', 'transactions', 'avg_check']:
            val1 = metrics1.get(key, 0)
            val2 = metrics2.get(key, 0)

            change_abs = val2 - val1
            change_pct = ((val2 - val1) / val1 * 100) if val1 != 0 else 0

            comparison['changes'][key] = {
                'absolute': change_abs,
                'percent': change_pct,
                'direction': 'up' if change_abs > 0 else ('down' if change_abs < 0 else 'same')
            }

        return comparison

    @staticmethod
    def _calculate_metrics(df: pd.DataFrame, period_name: str) -> Dict[str, float]:
        """Расчёт метрик для одного периода"""
        if df.empty:
            return {
                'revenue': 0,
                'profit': 0,
                'units_sold': 0,
                'transactions': 0,
                'avg_check': 0,
                'period_name': period_name
            }

        revenue = float(df['revenue'].sum()) if 'revenue' in df.columns else 0
        profit = float(df['profit'].sum()) if 'profit' in df.columns else 0
        units_sold = int(df['units_sold'].sum()) if 'units_sold' in df.columns else 0
        transactions = len(df)
        avg_check = revenue / transactions if transactions > 0 else 0

        return {
            'revenue': revenue,
            'profit': profit,
            'units_sold': units_sold,
            'transactions': transactions,
            'avg_check': avg_check,
            'period_name': period_name
        }

    @staticmethod
    def get_quick_comparison(df: pd.DataFrame) -> Optional[Dict[str, Any]]:
        """
        Быстрое сравнение: последний месяц vs предыдущий месяц

        Args:
            df: DataFrame с данными

        Returns:
            Словарь сравнения или None
        """
        if df.empty or 'date' not in df.columns:
            return None

        # Находим последний месяц в данных
        max_date = df['date'].max()
        last_month_start = max_date.replace(day=1)

        # Предыдущий месяц
        if last_month_start.month == 1:
            prev_month_start = last_month_start.replace(year=last_month_start.year - 1, month=12)
        else:
            prev_month_start = last_month_start.replace(month=last_month_start.month - 1)

        # Конец предыдущего месяца = начало последнего месяца - 1 день
        prev_month_end = last_month_start - pd.Timedelta(days=1)
        last_month_end = max_date

        return PeriodComparator.compare_periods(
            df,
            prev_month_start.strftime('%Y-%m-%d'),
            prev_month_end.strftime('%Y-%m-%d'),
            last_month_start.strftime('%Y-%m-%d'),
            last_month_end.strftime('%Y-%m-%d')
        )