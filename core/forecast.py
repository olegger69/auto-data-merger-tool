"""
Прогнозирование на основе линейной регрессии
"""

import numpy as np
import pandas as pd
from typing import Optional, Tuple


class Forecaster:
    """Простой прогноз на основе линейной регрессии"""

    @staticmethod
    def linear_forecast(
            df: pd.DataFrame,
            x_col: str,
            y_col: str,
            periods: int = 3,
            degree: int = 1
    ) -> Optional[pd.DataFrame]:
        """
        Прогноз будущих значений на основе исторических данных.

        Args:
            df: DataFrame с историческими данными
            x_col: Столбец с периодами (строки типа '2024-01')
            y_col: Столбец со значениями (выручка, прибыль и т.д.)
            periods: Количество периодов для прогноза
            degree: Степень полинома (1 = линейная, 2 = квадратичная)

        Returns:
            DataFrame с прогнозными значениями или None
        """
        if df.empty or len(df) < 2:
            return None

        try:
            # Преобразуем периоды в числовой формат (порядковый номер)
            x_values = np.arange(len(df))
            y_values = df[y_col].values.astype(float)

            # Удаляем NaN
            valid_mask = ~np.isnan(y_values)
            if valid_mask.sum() < 2:
                return None

            x_valid = x_values[valid_mask]
            y_valid = y_values[valid_mask]

            # Фитим полином
            coefficients = np.polyfit(x_valid, y_valid, degree)
            poly = np.poly1d(coefficients)

            # Генерируем прогнозные периоды
            last_period = df[x_col].iloc[-1]
            future_periods = Forecaster._generate_future_periods(last_period, periods)

            # Рассчитываем прогнозные значения
            future_x = np.arange(len(df), len(df) + periods)
            future_y = poly(future_x)

            # Создаём DataFrame с прогнозом
            forecast_df = pd.DataFrame({
                x_col: future_periods,
                f'{y_col}_forecast': future_y,
                'type': ['forecast'] * periods
            })

            # Добавляем исторические данные для отображения на графике
            historical_df = df[[x_col, y_col]].copy()
            historical_df = historical_df.rename(columns={y_col: f'{y_col}_forecast'})
            historical_df['type'] = 'historical'

            result = pd.concat([historical_df, forecast_df], ignore_index=True)
            return result

        except Exception as e:
            print(f"⚠️ Ошибка прогнозирования: {e}")
            return None

    @staticmethod
    def _generate_future_periods(last_period: str, periods: int) -> list:
        """
        Генерация будущих периодов на основе последнего периода.

        Args:
            last_period: Последний период в формате 'YYYY-MM' или 'YYYY'
            periods: Количество периодов

        Returns:
            Список строк с будущими периодами
        """
        try:
            # Пробуем формат YYYY-MM
            if '-' in last_period:
                year, month = map(int, last_period.split('-'))
                future = []
                for i in range(1, periods + 1):
                    month += 1
                    if month > 12:
                        month = 1
                        year += 1
                    future.append(f"{year}-{month:02d}")
                return future
            else:
                # Формат YYYY
                year = int(last_period)
                return [str(year + i) for i in range(1, periods + 1)]
        except:
            # Fallback: просто нумеруем
            return [f"Period {i}" for i in range(1, periods + 1)]

    @staticmethod
    def calculate_accuracy(
            df: pd.DataFrame,
            x_col: str,
            y_col: str,
            degree: int = 1
    ) -> Optional[float]:
        """
        Расчёт точности модели (R²) на исторических данных.

        Returns:
            R² score (0-1) или None
        """
        if df.empty or len(df) < 2:
            return None

        try:
            x_values = np.arange(len(df))
            y_values = df[y_col].values.astype(float)

            valid_mask = ~np.isnan(y_values)
            if valid_mask.sum() < 2:
                return None

            x_valid = x_values[valid_mask]
            y_valid = y_values[valid_mask]

            coefficients = np.polyfit(x_valid, y_valid, degree)
            poly = np.poly1d(coefficients)

            y_pred = poly(x_valid)

            ss_res = np.sum((y_valid - y_pred) ** 2)
            ss_tot = np.sum((y_valid - np.mean(y_valid)) ** 2)

            if ss_tot == 0:
                return 1.0

            r_squared = 1 - (ss_res / ss_tot)
            return max(0, min(1, r_squared))

        except:
            return None