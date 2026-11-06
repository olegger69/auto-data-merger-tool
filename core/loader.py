"""
Загрузка файлов CSV и Excel
"""

import pandas as pd
from pathlib import Path
from typing import List, Tuple, Optional


class DataLoader:
    """Загрузчик файлов CSV и Excel"""

    SUPPORTED_EXTENSIONS = {'.csv', '.xlsx', '.xls'}

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

    def _load_csv(self, path: Path) -> pd.DataFrame:
        """Загрузка CSV файла"""
        # Пробуем разные кодировки и разделители
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
        """
        Получение списка листов Excel файла

        Args:
            file_path: Путь к Excel файлу

        Returns:
            Список имён листов
        """
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