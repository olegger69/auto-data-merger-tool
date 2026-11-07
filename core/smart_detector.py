"""
Умное автоопределение ролей столбцов по содержимому и названиям
"""

import pandas as pd
import numpy as np
import warnings
from typing import Dict, List, Optional


class SmartColumnDetector:
    """
    Анализирует содержимое DataFrame и определяет роли столбцов.
    Приоритет: обязательные поля > опциональные поля.
    """

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
            'unit_price', 'price', 'цена', 'стоимость', 'retail_price', 'розничная',
            'wholesale_price', 'оптовая', 'rate', 'ставка', 'tariff', 'тариф',
            'fee', 'сбор', 'прайс'
        ],
        'cost_price': [
            'cost_price', 'себестоимость', 'costprice', 'закупочная',
            'purchase_price', 'закупка', 'себест', 'себестоим'
        ],
        'profit': [
            'profit', 'прибыль', 'доход', 'income', 'earnings', 'выгода',
            'маржа', 'margin', 'чистая_прибыль', 'net_profit'
        ],
        'customer': [
            'customer', 'клиент', 'покупатель', 'buyer', 'client', 'заказчик',
            'customer_name', 'имя_клиента', 'name_customer'
        ],
        'manager': [
            'manager', 'менеджер', 'продавец', 'salesman', 'seller', 'employee',
            'сотрудник', 'manager_name', 'имя_менеджера', 'sales_rep', 'торговый_представитель'
        ]
    }

    # Обязательные роли (обрабатываются в первую очередь)
    REQUIRED_ROLES = ['date', 'region', 'product', 'units_sold', 'unit_price']

    # Опциональные роли (обрабатываются после обязательных)
    OPTIONAL_ROLES = ['cost_price', 'profit', 'customer', 'manager']

    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.columns = list(df.columns)
        self.assignments: Dict[str, Optional[str]] = {
            'date': None, 'region': None, 'product': None,
            'units_sold': None, 'unit_price': None,
            'cost_price': None, 'profit': None,
            'customer': None, 'manager': None
        }
        self.confidence: Dict[str, float] = {
            'date': 0.0, 'region': 0.0, 'product': 0.0,
            'units_sold': 0.0, 'unit_price': 0.0,
            'cost_price': 0.0, 'profit': 0.0,
            'customer': 0.0, 'manager': 0.0
        }

    def detect_all(self) -> Dict[str, Optional[str]]:
        """Полный цикл определения ролей столбцов"""
        # Сначала определяем обязательные роли
        for role in self.REQUIRED_ROLES:
            self._detect_role_by_name(role)

        for role in self.REQUIRED_ROLES:
            if self.assignments[role] is None:
                self._detect_role_by_content(role)

        # Потом опциональные (не трогая уже назначенные столбцы)
        for role in self.OPTIONAL_ROLES:
            self._detect_role_by_name(role)

        for role in self.OPTIONAL_ROLES:
            if self.assignments[role] is None:
                self._detect_role_by_content(role)

        return self.assignments.copy()

    def _matches_synonym(self, col_name: str, synonyms: list) -> bool:
        """Проверка, содержит ли имя столбца синоним"""
        col_lower = str(col_name).strip().lower().replace(' ', '_').replace('-', '_')
        for syn in synonyms:
            syn_clean = syn.replace(' ', '_').replace('-', '_')
            if syn_clean in col_lower or col_lower in syn_clean:
                return True
        return False

    def _get_used_columns(self) -> set:
        """Получить множество уже назначенных столбцов"""
        return {col for col in self.assignments.values() if col is not None}

    def _detect_role_by_name(self, role: str):
        """Поиск столбца по синонимам названия"""
        if self.assignments[role] is not None:
            return

        synonyms = self.NAME_SYNONYMS.get(role, [])
        for col in self.columns:
            if self._matches_synonym(col, synonyms):
                self.assignments[role] = col
                self.confidence[role] = 0.95
                break

    def _detect_role_by_content(self, role: str):
        """Анализ содержимого для определения роли"""
        if self.assignments[role] is not None:
            return

        used = self._get_used_columns()
        candidates = []

        for col in self.columns:
            if col in used:
                continue

            col_data = self.df[col].dropna()
            if len(col_data) == 0:
                continue

            if role == 'date':
                score = self._score_as_date(col_data)
                if score > 0.8:
                    candidates.append((col, score))

            elif role in ['units_sold']:
                int_score = self._score_as_integer(col_data)
                if int_score > 0.8 and self._looks_like_quantity(col_data):
                    candidates.append((col, int_score))

            elif role in ['unit_price', 'cost_price']:
                float_score = self._score_as_float(col_data)
                if float_score > 0.8 and self._looks_like_price(col_data):
                    candidates.append((col, float_score))

            elif role in ['region', 'product', 'customer', 'manager']:
                text_score = self._score_as_text(col_data)
                if text_score > 0.8:
                    unique_count = col_data.nunique()
                    avg_length = col_data.astype(str).str.len().mean()

                    if role == 'region' and unique_count < 50 and avg_length < 30:
                        candidates.append((col, text_score * 0.8))
                    elif role == 'product' and (unique_count > 5 or avg_length > 3):
                        candidates.append((col, text_score * 0.7))
                    elif role == 'customer' and unique_count > 10:
                        candidates.append((col, text_score * 0.6))
                    elif role == 'manager' and unique_count > 5:
                        candidates.append((col, text_score * 0.5))

        if candidates:
            candidates.sort(key=lambda x: x[1], reverse=True)
            best_col, best_score = candidates[0]
            if best_col not in self._get_used_columns():
                self.assignments[role] = best_col
                self.confidence[role] = best_score

    def _score_as_date(self, series: pd.Series) -> float:
        if pd.api.types.is_numeric_dtype(series):
            return 0.0
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                converted = pd.to_datetime(series, errors='coerce', format='mixed')
            success_rate = converted.notna().sum() / len(series)
            return success_rate if success_rate > 0.8 else 0.0
        except:
            return 0.0

    def _score_as_integer(self, series: pd.Series) -> float:
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
        try:
            numeric = pd.to_numeric(series, errors='coerce')
            valid = numeric.dropna()
            if len(valid) == 0:
                return 0.0
            return len(valid) / len(series)
        except:
            return 0.0

    def _score_as_text(self, series: pd.Series) -> float:
        try:
            numeric = pd.to_numeric(series, errors='coerce')
            non_numeric_rate = numeric.isna().sum() / len(series)
            return non_numeric_rate
        except:
            return 0.0

    def _looks_like_quantity(self, series: pd.Series) -> bool:
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
        assigned_count = sum(1 for v in self.assignments.values() if v is not None)
        lines.append(f"  Назначено ролей: {assigned_count}/9")
        return "\n".join(lines)