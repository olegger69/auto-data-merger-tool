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

    # Роли, которые должны быть определены для полноценной работы
    REQUIRED_ROLES = ['date', 'region', 'product', 'units_sold', 'unit_price']

    # Файлы экспорта, которые не стоит загружать как исходные данные
    EXPORT_FILE_HINTS = ['merged_output', 'summary_report']

    def __init__(self):
        self.loaded_files = []

    def load_file(self, file_path: str, sheet_name: Optional[str] = None) -> pd.DataFrame:
        """
        Загрузка одного файла

        Args:
            file_path: Путь к файлу
            sheet_name: Имя листа для Excel (по умолчанию первый лист)

        Returns:
            DataFrame с данными

        Raises:
            ValueError: Если файл не поддерживается или не найден
        """
        path = Path(file_path)

        # Проверка существования файла
        if not path.exists():
            raise ValueError(f"Файл не найден: {file_path}")

        # Проверка расширения
        if path.suffix.lower() not in self.SUPPORTED_EXTENSIONS:
            raise ValueError(f"Неподдерживаемый формат файла: {path.suffix}")

        # Предупреждение о файлах экспорта
        if path.stem in self.EXPORT_FILE_HINTS:
            raise ValueError(
                f"Файл '{path.name}' похож на файл экспорта приложения. "
                f"Пожалуйста, выберите исходные файлы с данными о продажах."
            )

        # Загрузка в зависимости от типа файла
        if path.suffix.lower() == '.csv':
            df = self._load_csv(path)
        else:
            df = self._load_excel(path, sheet_name)

        # Сохранение информации о файле
        self.loaded_files.append({
            'path': str(path),
            'name': path.name,
            'rows': len(df),
            'columns': list(df.columns)
        })

        return df

    def load_and_detect(self, file_path: str, sheet_name: Optional[str] = None) -> Tuple[
        pd.DataFrame, Dict[str, Optional[str]]]:
        """
        Загрузка файла с автоопределением ролей столбцов.

        Returns:
            Кортеж (DataFrame, словарь ролей)
        """
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
        """
        Применение маппинга: переименовывает столбцы согласно ролям.
        Удаляет дубликаты и лишние столбцы.

        Args:
            df: Исходный DataFrame
            roles: Словарь ролей от SmartColumnDetector

        Returns:
            DataFrame со стандартными именами столбцов
        """
        df = df.copy()

        # Шаг 1: Собираем все стандартные имена ролей, которые назначены
        assigned_standard_cols = {role for role, col in roles.items() if col is not None}

        # Шаг 2: Удаляем столбцы, которые уже имеют стандартные имена,
        # но не назначены никакой роли (чтобы избежать дубликатов после переименования)
        cols_to_drop = []
        for col in df.columns:
            if col in assigned_standard_cols:
                # Проверяем, назначен ли этот столбец какой-либо роли
                is_assigned = any(
                    roles.get(role) == col
                    for role in roles
                    if roles.get(role) is not None
                )
                if not is_assigned:
                    cols_to_drop.append(col)

        if cols_to_drop:
            df = df.drop(columns=cols_to_drop)

        # Шаг 3: Переименовываем назначенные столбцы в стандартные имена
        rename_map = {}
        for role, col in roles.items():
            if col is not None and col != role:
                rename_map[col] = role

        if rename_map:
            df = df.rename(columns=rename_map)

        # Шаг 4: Финальная проверка на дубликаты столбцов
        if df.columns.duplicated().any():
            # Оставляем только первое вхождение каждого столбца
            df = df.loc[:, ~df.columns.duplicated()]

        return df

    @staticmethod
    def check_roles_complete(roles: Dict[str, Optional[str]]) -> Tuple[bool, List[str]]:
        """
        Проверка, все ли обязательные роли определены.

        Returns:
            Кортеж (полнота, список недостающих ролей)
        """
        missing = [role for role in DataLoader.REQUIRED_ROLES if roles.get(role) is None]
        return (len(missing) == 0, missing)