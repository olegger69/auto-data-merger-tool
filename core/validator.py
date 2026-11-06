"""
Валидация и очистка данных
"""

import pandas as pd
from typing import List


class DataValidator:
    """Валидатор и очистчик данных"""

    REQUIRED_COLUMNS = ['date', 'region', 'product', 'units_sold', 'unit_price']

    @staticmethod
    def standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
        """
        Стандартизация заголовков: нижний регистр,
        замена пробелов и дефисов на подчёркивания
        """
        df = df.copy()
        df.columns = [
            str(col).strip().lower().replace(' ', '_').replace('-', '_')
            for col in df.columns
        ]
        return df

    @staticmethod
    def validate_required_columns(df: pd.DataFrame) -> None:
        """
        Проверка наличия обязательных столбцов
        Raises:
            ValueError: Если отсутствуют обязательные столбцы
        """
        missing = [col for col in DataValidator.REQUIRED_COLUMNS if col not in df.columns]
        if missing:
            raise ValueError(f"Отсутствуют обязательные столбцы: {', '.join(missing)}")

    @staticmethod
    def clean_data(df: pd.DataFrame) -> pd.DataFrame:
        """
        Очистка данных: преобразование типов и удаление некорректных строк
        """
        df = df.copy()

        # 1. Преобразование даты в datetime (некорректные станут NaT)
        df['date'] = pd.to_datetime(df['date'], errors='coerce')

        # 2. Преобразование числовых столбцов (некорректные станут NaN)
        df['units_sold'] = pd.to_numeric(df['units_sold'], errors='coerce')
        df['unit_price'] = pd.to_numeric(df['unit_price'], errors='coerce')

        # 3. Удаление полностью пустых строк
        df = df.dropna(how='all')

        # 4. Удаление строк, где отсутствуют критически важные данные для расчёта выручки
        # (Мы не можем посчитать выручку без цены или количества, а дата нужна для графиков)
        df = df.dropna(subset=['date', 'units_sold', 'unit_price'])

        # Опционально: заполнение пустых region/product строкой "Не указано"
        df['region'] = df['region'].fillna('Не указано')
        df['product'] = df['product'].fillna('Не указано')

        return df

    @staticmethod
    def calculate_revenue(df: pd.DataFrame) -> pd.DataFrame:
        """Расчёт производного поля: выручка = количество * цена"""
        df = df.copy()
        df['revenue'] = df['units_sold'] * df['unit_price']
        return df

    @classmethod
    def process(cls, df: pd.DataFrame) -> pd.DataFrame:
        """
        Полный цикл обработки одного DataFrame
        """
        df = cls.standardize_columns(df)
        cls.validate_required_columns(df)
        df = cls.clean_data(df)
        df = cls.calculate_revenue(df)
        return df