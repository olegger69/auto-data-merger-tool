"""
Расчёт корреляций между числовыми показателями
"""

import pandas as pd
import numpy as np
from typing import Optional, Tuple, List


class CorrelationAnalyzer:
    """Анализ корреляций между числовыми столбцами DataFrame"""

    # Числовые столбцы, которые нас интересуют для анализа
    TARGET_NUMERIC_COLS = ['units_sold', 'unit_price', 'revenue', 'profit', 'cost_price']

    @staticmethod
    def calculate_correlation_matrix(df: pd.DataFrame) -> Optional[pd.DataFrame]:
        """
        Расчёт матрицы корреляций Пирсона между числовыми столбцами.

        Args:
            df: DataFrame с данными

        Returns:
            DataFrame с матрицей корреляций или None
        """
        if df.empty:
            return None

        # Выбираем только нужные числовые столбцы, которые есть в данных
        available_cols = [col for col in CorrelationAnalyzer.TARGET_NUMERIC_COLS if col in df.columns]

        if len(available_cols) < 2:
            return None

        # Берём только эти столбцы
        numeric_df = df[available_cols].copy()

        # Преобразуем в числовой формат (на случай если что-то осталось строкой)
        for col in numeric_df.columns:
            numeric_df[col] = pd.to_numeric(numeric_df[col], errors='coerce')

        # Удаляем строки с NaN
        numeric_df = numeric_df.dropna()

        if len(numeric_df) < 3:
            return None

        # Считаем корреляцию
        corr_matrix = numeric_df.corr(method='pearson')

        return corr_matrix

    @staticmethod
    def get_strong_correlations(
            corr_matrix: pd.DataFrame,
            threshold: float = 0.5
    ) -> List[Tuple[str, str, float]]:
        """
        Поиск сильных корреляций (по модулю > threshold).

        Returns:
            Список кортежей (столбец1, столбец2, коэффициент)
        """
        if corr_matrix is None or corr_matrix.empty:
            return []

        strong = []
        cols = corr_matrix.columns

        for i in range(len(cols)):
            for j in range(i + 1, len(cols)):
                col1, col2 = cols[i], cols[j]
                value = corr_matrix.loc[col1, col2]

                if abs(value) >= threshold:
                    strong.append((col1, col2, value))

        # Сортируем по абсолютному значению (сильные связи сверху)
        strong.sort(key=lambda x: abs(x[2]), reverse=True)

        return strong

    @staticmethod
    def interpret_correlation(value: float) -> str:
        """Интерпретация значения корреляции"""
        abs_val = abs(value)

        if abs_val < 0.3:
            strength = "слабая"
        elif abs_val < 0.5:
            strength = "умеренная"
        elif abs_val < 0.7:
            strength = "заметная"
        elif abs_val < 0.9:
            strength = "сильная"
        else:
            strength = "очень сильная"

        direction = "положительная" if value > 0 else "отрицательная"

        return f"{strength} {direction}"

    @staticmethod
    def get_column_labels(column_names: List[str]) -> dict:
        """Получение понятных названий для столбцов"""
        labels = {
            'units_sold': 'Количество',
            'unit_price': 'Цена за ед.',
            'revenue': 'Выручка',
            'profit': 'Прибыль',
            'cost_price': 'Себестоимость'
        }
        return {col: labels.get(col, col) for col in column_names}