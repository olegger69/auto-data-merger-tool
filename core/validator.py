"""
Валидация и очистка данных
"""

import pandas as pd
from typing import List, Optional


class DataValidator:
    """Валидатор и очистчик данных"""

    REQUIRED_COLUMNS = ['date', 'region', 'product', 'units_sold', 'unit_price']

    # Словарь синонимов для столбца с датой
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
    def detect_date_column(df: pd.DataFrame) -> Optional[str]:
        """
        Автоопределение столбца с датой.

        Алгоритм:
        1. Сначала ищем точное совпадение 'date'
        2. Затем ищем по словарю синонимов
        3. Если не нашли — анализируем содержимое столбцов

        Returns:
            Название столбца с датой или None, если не удалось определить
        """
        # Уровень 1: Точное совпадение
        if 'date' in df.columns:
            return 'date'

        # Уровень 2: Поиск по синонимам
        for synonym in DataValidator.DATE_SYNONYMS:
            standardized = synonym.lower().replace(' ', '_').replace('-', '_')
            if standardized in df.columns:
                return standardized

        # Уровень 3: Эвристика по содержимому
        # Перебираем все столбцы и пытаемся преобразовать в datetime
        best_column = None
        best_score = 0

        for col in df.columns:
            # Пропускаем столбцы, которые уже являются datetime
            if pd.api.types.is_datetime64_any_dtype(df[col]):
                return col

            # Пропускаем столбцы, которые явно числовые (кроме случаев, когда это timestamp)
            if pd.api.types.is_numeric_dtype(df[col]):
                # Проверяем, не является ли это Unix timestamp
                sample = df[col].dropna().head(10)
                if len(sample) > 0:
                    # Если значения в диапазоне типичных Unix timestamp (1970-2030)
                    if sample.min() > 946684800 and sample.max() < 1893456000:
                        return col
                continue

            # Пытаемся преобразовать в datetime
            try:
                converted = pd.to_datetime(df[col], errors='coerce')
                # Считаем процент успешных преобразований
                success_rate = converted.notna().sum() / len(df) if len(df) > 0 else 0

                # Если больше 50% значений успешно преобразовались — это кандидат
                if success_rate > 0.5 and success_rate > best_score:
                    best_score = success_rate
                    best_column = col
            except (ValueError, TypeError):
                continue

        # Если нашли хороший кандидат — возвращаем его
        if best_column and best_score > 0.5:
            return best_column

        return None

    @staticmethod
    def rename_date_column(df: pd.DataFrame, date_column: str) -> pd.DataFrame:
        """
        Переименование столбца с датой в 'date'
        """
        df = df.copy()
        if date_column != 'date' and date_column in df.columns:
            df = df.rename(columns={date_column: 'date'})
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

        # Автоопределение и переименование столбца с датой
        date_column = cls.detect_date_column(df)
        if date_column is None:
            raise ValueError(
                "Не удалось определить столбец с датой. "
                "Убедитесь, что в файле есть столбец с датами (например, 'date', 'дата', 'order_date')."
            )
        if date_column != 'date':
            df = cls.rename_date_column(df, date_column)

        cls.validate_required_columns(df)
        df = cls.clean_data(df)
        df = cls.calculate_revenue(df)
        return df