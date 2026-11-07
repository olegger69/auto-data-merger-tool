"""
Генерация сводных таблиц (адаптивный набор полей)
"""

import pandas as pd
from typing import Dict


class SummaryReporter:
    """Генератор сводных отчётов"""

    @staticmethod
    def generate_all(df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
        """
        Генерация всех сводных таблиц.
        Адаптируется к наличию опциональных полей.
        """
        if df.empty:
            return {
                'by_product': pd.DataFrame(),
                'by_region': pd.DataFrame(),
                'by_manager': pd.DataFrame(),
                'by_customer': pd.DataFrame(),
                'by_month': pd.DataFrame()
            }

        # Определяем, какие опциональные поля есть в данных
        has_profit = 'profit' in df.columns
        has_customer = 'customer' in df.columns
        has_manager = 'manager' in df.columns

        # Вспомогательная функция для группировки
        def group_by(col: str) -> pd.DataFrame:
            if col not in df.columns:
                return pd.DataFrame()

            agg_dict = {'revenue': 'sum'}
            if has_profit:
                agg_dict['profit'] = 'sum'

            res = df.groupby(col).agg(agg_dict).reset_index()
            res = res.sort_values('revenue', ascending=False).round(2)
            return res

        # 1. Выручка и прибыль по продуктам
        by_product = group_by('product')

        # 2. Выручка и прибыль по регионам
        by_region = group_by('region')

        # 3. Выручка и прибыль по менеджерам (только если есть менеджер)
        by_manager = group_by('manager') if has_manager else pd.DataFrame()

        # 4. Выручка и прибыль по клиентам (только если есть клиент)
        by_customer = group_by('customer') if has_customer else pd.DataFrame()

        # 5. Динамика по месяцам
        df_with_month = df.copy()
        df_with_month['period'] = df_with_month['date'].dt.to_period('M').astype(str)

        agg_dict_month = {'revenue': 'sum'}
        if has_profit:
            agg_dict_month['profit'] = 'sum'

        by_month = df_with_month.groupby('period').agg(agg_dict_month).reset_index()
        by_month = by_month.sort_values('period').round(2)

        return {
            'by_product': by_product,
            'by_region': by_region,
            'by_manager': by_manager,
            'by_customer': by_customer,
            'by_month': by_month
        }