"""
Загрузка файлов CSV и Excel с умным автоопределением столбцов
"""

import pandas as pd
from pathlib import Path
from typing import List, Tuple, Optional, Dict
from core.smart_detector import SmartColumnDetector


class DataLoader:
    """Загрузчик файлов CSV и Excel"""

    SUPPORTED_EXTENSIONS = {'.csv', '.xlsx', '.xls'}

    # Только 5 обязательных полей (базовый набор)
    REQUIRED_ROLES = ['date', 'region', 'product', 'units_sold', 'unit_price']

    # Опциональные поля (расширенный набор)
    OPTIONAL_ROLES = ['cost_price', 'profit', 'customer', 'manager']

    # Все поля вместе
    ALL_ROLES = REQUIRED_ROLES + OPTIONAL_ROLES

    # Файлы экспорта, которые не стоит загружать как исходные данные
    EXPORT_FILE_HINTS = ['merged_output', 'summary_report']

    def __init__(self):
        self.loaded_files = []

    def load_file(self, file_path: str, sheet_name: Optional[str] = None) -> pd.DataFrame:
        """Загрузка одного файла"""
        path = Path(file_path)

        if not path.exists():
            raise ValueError(f"Файл не найден: {file_path}")

        if path.suffix.lower() not in self.SUPPORTED_EXTENSIONS:
            raise ValueError(f"Неподдерживаемый формат файла: {path.suffix}")

        if path.stem in self.EXPORT_FILE_HINTS:
            raise ValueError(
                f"Файл '{path.name}' похож на файл экспорта приложения. "
                f"Пожалуйста, выберите исходные файлы с данными о продажах."
            )

        if path.suffix.lower() == '.csv':
            df = self._load_csv(path)
        else:
            df = self._load_excel(path, sheet_name)

        self.loaded_files.append({
            'path': str(path),
            'name': path.name,
            'rows': len(df),
            'columns': list(df.columns)
        })

        return df

    def load_and_detect(self, file_path: str, sheet_name: Optional[str] = None) -> Tuple[pd.DataFrame, Dict[str, Optional[str]]]:
        """Загрузка файла с автоопределением ролей столбцов"""
        df = self.load_file(file_path, sheet_name)
        detector = SmartColumnDetector(df)
        roles = detector.detect_all()
        return df, roles

    def _load_csv(self, path: Path) -> pd.DataFrame:
        """Загрузка CSV файла"""
        encodings = ['utf-8', 'cp1251', 'latin1']
        separators = [',', ';', '\t']

        for encoding in encodings:
            for sep in separators:
                try:
                    df = pd.read_csv(path, encoding=encoding, sep=sep)
                    return df
                except (UnicodeDecodeError, ValueError):
                    continue

        raise ValueError(f"Не удалось прочитать CSV файл: {path}")

    def _load_excel(self, path: Path, sheet_name: Optional[str]) -> pd.DataFrame:
        """Загрузка Excel файла"""
        return pd.read_excel(path, sheet_name=sheet_name if sheet_name else 0)

    def get_excel_sheets(self, file_path: str) -> List[str]:
        """Получение списка листов Excel файла"""
        path = Path(file_path)
        if path.suffix.lower() not in ['.xlsx', '.xls']:
            return []

        excel_file = pd.ExcelFile(path)
        return excel_file.sheet_names

    def get_loaded_files_info(self) -> List[dict]:
        """Получение информации о загруженных файлах"""
        return self.loaded_files.copy()

    def clear(self):
        """Очистка информации о загруженных файлах"""
        self.loaded_files = []

    @staticmethod
    def apply_mapping(df: pd.DataFrame, roles: Dict[str, Optional[str]]) -> pd.DataFrame:
        """Применение маппинга: переименовывает столбцы согласно ролям"""
        df = df.copy()

        assigned_standard_cols = {role for role, col in roles.items() if col is not None}

        cols_to_drop = []
        for col in df.columns:
            if col in assigned_standard_cols:
                is_assigned = any(
                    roles.get(role) == col
                    for role in roles
                    if roles.get(role) is not None
                )
                if not is_assigned:
                    cols_to_drop.append(col)

        if cols_to_drop:
            df = df.drop(columns=cols_to_drop)

        rename_map = {}
        for role, col in roles.items():
            if col is not None and col != role:
                rename_map[col] = role

        if rename_map:
            df = df.rename(columns=rename_map)

        if df.columns.duplicated().any():
            df = df.loc[:, ~df.columns.duplicated()]

        return df

    @staticmethod
    def check_roles_complete(roles: Dict[str, Optional[str]]) -> Tuple[bool, List[str]]:
        """
        Проверка, все ли ОБЯЗАТЕЛЬНЫЕ роли определены.
        Опциональные роли не требуются.
        """
        missing = [role for role in DataLoader.REQUIRED_ROLES if roles.get(role) is None]
        return (len(missing) == 0, missing)