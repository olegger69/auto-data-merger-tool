"""
Умное автоопределение ролей столбцов по содержимому и названиям
"""

import pandas as pd
import numpy as np
import warnings
from typing import Dict, List, Optional


class SmartColumnDetector:
    """
    Анализирует содержимое DataFrame и определяет роли столбцов:
    date, region, product, units_sold, unit_price
    """

    # Синонимы названий столбцов (теперь работает поиск по подстроке!)
    NAME_SYNONYMS = {
        'date': [
            'date', 'дата', 'даты', 'order_date', 'orderdate', 'order date',
            'sale_date', 'saledate', 'sale date', 'transaction_date', 'purchase_date',
            'invoice_date', 'created_at', 'updated_at', 'report_date',
            'datetime', 'date_time', 'period', 'период', 'day', 'день', 'время'
        ],
        'region': [
            'region', 'регион', 'регионы', 'city', 'город', 'country',
            'страна', 'state', 'штат', 'location', 'местоположение',
            'branch', 'филиал', 'office', 'офис', 'store', 'магазин',
            'territory', 'территория', 'area', 'зона', 'округ'
        ],
        'product': [
            'product', 'продукт', 'продукция', 'товар', 'item', 'наименование',
            'name', 'название', 'sku', 'article', 'артикул', 'category',
            'категория', 'subcategory', 'подкатегория', 'brand', 'бренд',
            'model', 'модель', 'goods', 'услуга', 'service', 'номенклатура'
        ],
        'units_sold': [
            'units_sold', 'units', 'количество', 'кол-во', 'коллич', 'qty', 'quantity',
            'count', 'число', 'volume', 'объем', 'объём', 'amount',
            'pieces', 'штук', 'шт', 'number', 'численность', 'sales_qty', 'qty_sold'
        ],
        'unit_price': [
            'unit_price', 'price', 'цена', 'стоимость', 'cost', 'cost_price',
            'себестоимость', 'retail_price', 'розничная', 'wholesale_price',
            'оптовая', 'rate', 'ставка', 'tariff', 'тариф', 'fee', 'сбор', 'прайс'
        ]
    }

    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.columns = list(df.columns)
        self.assignments: Dict[str, Optional[str]] = {
            'date': None,
            'region': None,
            'product': None,
            'units_sold': None,
            'unit_price': None
        }
        self.confidence: Dict[str, float] = {
            'date': 0.0,
            'region': 0.0,
            'product': 0.0,
            'units_sold': 0.0,
            'unit_price': 0.0
        }

    def detect_all(self) -> Dict[str, Optional[str]]:
        """Полный цикл определения ролей столбцов."""
        # Шаг 1: Поиск по подстрокам в названиях (высокая уверенность)
        self._detect_by_name()

        # Шаг 2: Анализ содержимого для неопределённых ролей
        self._detect_by_content()

        # Шаг 3: Разрешение конфликтов
        self._resolve_conflicts()

        return self.assignments.copy()

    def _matches_synonym(self, col_name: str, synonyms: list) -> bool:
        """Проверка, содержит ли имя столбца синоним или наоборот"""
        col_lower = str(col_name).strip().lower().replace(' ', '_').replace('-', '_')
        for syn in synonyms:
            syn_clean = syn.replace(' ', '_').replace('-', '_')
            # Проверяем и "syn в col", и "col в syn"
            if syn_clean in col_lower or col_lower in syn_clean:
                return True
        return False

    def _detect_by_name(self):
        """Поиск столбцов по синонимам названий (с поиском по подстроке)"""
        for role, synonyms in self.NAME_SYNONYMS.items():
            if self.assignments[role] is not None:
                continue

            for col in self.columns:
                if self._matches_synonym(col, synonyms):
                    self.assignments[role] = col
                    self.confidence[role] = 0.95
                    break

    def _detect_by_content(self):
        """Анализ содержимого столбцов для неопределённых ролей"""
        candidates = {
            'date': [],
            'region': [],
            'product': [],
            'units_sold': [],
            'unit_price': []
        }

        for col in self.columns:
            if col in self.assignments.values():
                continue

            col_data = self.df[col].dropna()
            if len(col_data) == 0:
                continue

            date_score = self._score_as_date(col_data)
            int_score = self._score_as_integer(col_data)
            float_score = self._score_as_float(col_data)
            text_score = self._score_as_text(col_data)

            if date_score > 0.8:  # Повышенный порог для даты, чтобы избежать ложных срабатываний
                candidates['date'].append((col, date_score))

            if int_score > 0.8 and self._looks_like_quantity(col_data):
                candidates['units_sold'].append((col, int_score))

            if float_score > 0.8 and self._looks_like_price(col_data):
                candidates['unit_price'].append((col, float_score))

            if text_score > 0.8:
                unique_count = col_data.nunique()
                avg_length = col_data.astype(str).str.len().mean()

                # Мало уникальных значений + короткие строки → region
                if unique_count < 50 and avg_length < 30:
                    candidates['region'].append((col, text_score * 0.8))

                # Много уникальных значений → product
                if unique_count > 5 or avg_length > 3:
                    candidates['product'].append((col, text_score * 0.7))

        # Назначаем лучшие кандидаты
        for role, cands in candidates.items():
            if self.assignments[role] is None and cands:
                cands.sort(key=lambda x: x[1], reverse=True)
                best_col, best_score = cands[0]

                if best_col not in self.assignments.values():
                    self.assignments[role] = best_col
                    self.confidence[role] = best_score

    def _score_as_date(self, series: pd.Series) -> float:
        """Оценка, насколько столбец похож на дату (игнорируем чисто числовые столбцы)"""
        if pd.api.types.is_numeric_dtype(series):
            return 0.0  # Числа (цены, количества) не должны становиться датами

        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                # format='mixed' предотвращает предупреждения в новых pandas
                converted = pd.to_datetime(series, errors='coerce', format='mixed')
            success_rate = converted.notna().sum() / len(series)
            return success_rate if success_rate > 0.8 else 0.0
        except:
            return 0.0

    def _score_as_integer(self, series: pd.Series) -> float:
        """Оценка, насколько столбец похож на целые числа"""
        try:
            numeric = pd.to_numeric(series, errors='coerce')
            valid = numeric.dropna()
            if len(valid) == 0:
                return 0.0
            is_integer = (valid == valid.astype(int)).all()
            if not is_integer:
                return 0.0
            return len(valid) / len(series)
        except:
            return 0.0

    def _score_as_float(self, series: pd.Series) -> float:
        """Оценка, насколько столбец похож на числа (целые или дробные)"""
        try:
            numeric = pd.to_numeric(series, errors='coerce')
            valid = numeric.dropna()
            if len(valid) == 0:
                return 0.0
            return len(valid) / len(series)
        except:
            return 0.0

    def _score_as_text(self, series: pd.Series) -> float:
        """Оценка, насколько столбец похож на текст"""
        try:
            numeric = pd.to_numeric(series, errors='coerce')
            non_numeric_rate = numeric.isna().sum() / len(series)
            return non_numeric_rate
        except:
            return 0.0

    def _looks_like_quantity(self, series: pd.Series) -> bool:
        """Проверка, похожи ли числа на количество"""
        try:
            numeric = pd.to_numeric(series, errors='coerce').dropna()
            if len(numeric) == 0:
                return False
            if not (numeric == numeric.astype(int)).all():
                return False
            if (numeric < 0).any():
                return False
            if numeric.max() > 100000:
                return False
            return True
        except:
            return False

    def _looks_like_price(self, series: pd.Series) -> bool:
        """Проверка, похожи ли числа на цену"""
        try:
            numeric = pd.to_numeric(series, errors='coerce').dropna()
            if len(numeric) == 0:
                return False
            if (numeric < 0).any():
                return False
            if numeric.max() > 1000000:
                return False
            return True
        except:
            return False

    def _resolve_conflicts(self):
        """Разрешение конфликтов, если один столбец назначен нескольким ролям"""
        used_columns = {}
        for role, col in self.assignments.items():
            if col is not None:
                if col in used_columns:
                    existing_role = used_columns[col]
                    if self.confidence[role] > self.confidence[existing_role]:
                        self.assignments[existing_role] = None
                        self.confidence[existing_role] = 0.0
                        used_columns[col] = role
                else:
                    used_columns[col] = role

    def get_report(self) -> str:
        """Формирование отчёта о найденных столбцах"""
        lines = ["=== Отчёт автоопределения столбцов ===\n"]
        for role, col in self.assignments.items():
            conf = self.confidence[role]
            if col is not None:
                conf_str = f"{conf:.0%}"
                lines.append(f"  ✅ {role:12} → '{col}' (уверенность: {conf_str})")
            else:
                lines.append(f"  ❌ {role:12} → не определён")

        lines.append(f"\n  Всего столбцов в файле: {len(self.columns)}")
        lines.append(f"  Назначено ролей: {sum(1 for v in self.assignments.values() if v is not None)}/5")
        return "\n".join(lines)