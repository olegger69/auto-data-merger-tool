"""
Валидация и очистка данных (5 обязательных + 4 опциональных поля)
"""

import pandas as pd
from typing import List, Optional


class DataValidator:
    """Валидатор и очистчик данных"""

    # Только 5 обязательных полей
    REQUIRED_COLUMNS = ['date', 'region', 'product', 'units_sold', 'unit_price']

    # Опциональные поля
    OPTIONAL_COLUMNS = ['cost_price', 'profit', 'customer', 'manager']

    DATE_SYNONYMS = [
        'date', 'дата', 'даты',
        'order_date', 'order date', 'orderdate',
        'sale_date', 'sale date', 'saledate',
        'transaction_date', 'transaction date',
        'purchase_date', 'purchase date',
        'invoice_date', 'invoice date',
        'created_at', 'created at', 'createdat',
        'updated_at', 'updated at',
        'report_date', 'report date',
        'period', 'период',
        'datetime', 'date_time', 'date time'
    ]

    @staticmethod
    def standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
        """Стандартизация заголовков"""
        df = df.copy()
        df.columns = [
            str(col).strip().lower().replace(' ', '_').replace('-', '_')
            for col in df.columns
        ]
        return df

    @staticmethod
    def detect_date_column(df: pd.DataFrame) -> Optional[str]:
        """Автоопределение столбца с датой"""
        if 'date' in df.columns:
            return 'date'

        for synonym in DataValidator.DATE_SYNONYMS:
            standardized = synonym.lower().replace(' ', '_').replace('-', '_')
            if standardized in df.columns:
                return standardized

        best_column = None
        best_score = 0

        for col in df.columns:
            if pd.api.types.is_datetime64_any_dtype(df[col]):
                return col

            if pd.api.types.is_numeric_dtype(df[col]):
                sample = df[col].dropna().head(10)
                if len(sample) > 0:
                    if sample.min() > 946684800 and sample.max() < 1893456000:
                        return col
                continue

            try:
                converted = pd.to_datetime(df[col], errors='coerce')
                success_rate = converted.notna().sum() / len(df) if len(df) > 0 else 0

                if success_rate > 0.5 and success_rate > best_score:
                    best_score = success_rate
                    best_column = col
            except (ValueError, TypeError):
                continue

        if best_column and best_score > 0.5:
            return best_column

        return None

    @staticmethod
    def rename_date_column(df: pd.DataFrame, date_column: str) -> pd.DataFrame:
        """Переименование столбца с датой в 'date'"""
        df = df.copy()
        if date_column != 'date' and date_column in df.columns:
            df = df.rename(columns={date_column: 'date'})
        return df

    @staticmethod
    def validate_required_columns(df: pd.DataFrame) -> None:
        """Проверка наличия только ОБЯЗАТЕЛЬНЫХ столбцов"""
        missing = [col for col in DataValidator.REQUIRED_COLUMNS if col not in df.columns]
        if missing:
            raise ValueError(f"Отсутствуют обязательные столбцы: {', '.join(missing)}")

    @staticmethod
    def clean_data(df: pd.DataFrame) -> pd.DataFrame:
        """Очистка данных"""
        df = df.copy()

        df['date'] = pd.to_datetime(df['date'], errors='coerce')

        numeric_cols = ['units_sold', 'unit_price']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

        # Опциональные числовые поля
        optional_numeric = ['cost_price', 'profit']
        for col in optional_numeric:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

        df = df.dropna(how='all')
        df = df.dropna(subset=['date', 'units_sold', 'unit_price'])

        text_cols = ['region', 'product']
        for col in text_cols:
            if col in df.columns:
                df[col] = df[col].fillna('Не указано')

        optional_text = ['customer', 'manager']
        for col in optional_text:
            if col in df.columns:
                df[col] = df[col].fillna('Не указано')

        return df

    @staticmethod
    def calculate_derived_fields(df: pd.DataFrame) -> pd.DataFrame:
        """Расчёт производных полей"""
        df = df.copy()

        df['revenue'] = df['units_sold'] * df['unit_price']

        # Если есть cost_price, но нет profit - рассчитаем
        if 'cost_price' in df.columns and 'profit' not in df.columns:
            df['profit'] = df['revenue'] - (df['units_sold'] * df['cost_price'])
        elif 'cost_price' in df.columns and 'profit' in df.columns:
            df['profit'] = df['revenue'] - (df['units_sold'] * df['cost_price'])

        return df

    @classmethod
    def process(cls, df: pd.DataFrame) -> pd.DataFrame:
        """Полный цикл обработки"""
        df = cls.standardize_columns(df)

        date_column = cls.detect_date_column(df)
        if date_column is None:
            raise ValueError(
                "Не удалось определить столбец с датой. "
                "Убедитесь, что в файле есть столбец с датами."
            )
        if date_column != 'date':
            df = cls.rename_date_column(df, date_column)

        cls.validate_required_columns(df)
        df = cls.clean_data(df)
        df = cls.calculate_derived_fields(df)
        return df