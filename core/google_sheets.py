"""
Импорт данных из Google Sheets
Поддерживает публичные таблицы (без авторизации) через CSV-экспорт
"""

import pandas as pd
import re
from typing import Optional
from io import StringIO
import urllib.request
import urllib.error


class GoogleSheetsImporter:
    """Импорт данных из Google Таблиц"""

    # Регулярное выражение для извлечения ID таблицы из URL
    SHEET_ID_PATTERN = re.compile(r'/spreadsheets/d/([a-zA-Z0-9-_]+)')

    @staticmethod
    def extract_sheet_id(url: str) -> Optional[str]:
        """
        Извлечение ID таблицы из URL Google Sheets

        Args:
            url: URL таблицы (например, https://docs.google.com/spreadsheets/d/1ABC.../edit)

        Returns:
            ID таблицы или None
        """
        match = GoogleSheetsImporter.SHEET_ID_PATTERN.search(url)
        if match:
            return match.group(1)
        return None

    @staticmethod
    def extract_gid(url: str) -> str:
        """
        Извлечение GID (ID листа) из URL

        Args:
            url: URL таблицы

        Returns:
            GID листа (по умолчанию '0' — первый лист)
        """
        match = re.search(r'[?&]gid=(\d+)', url)
        return match.group(1) if match else '0'

    @staticmethod
    def build_csv_url(sheet_id: str, gid: str = '0') -> str:
        """
        Построение URL для CSV-экспорта

        Args:
            sheet_id: ID таблицы
            gid: ID листа

        Returns:
            URL для скачивания CSV
        """
        return f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"

    @staticmethod
    def import_from_url(url: str) -> pd.DataFrame:
        """
        Импорт данных из публичной Google Таблицы по URL

        Args:
            url: URL таблицы (должна быть опубликована для чтения)

        Returns:
            DataFrame с данными

        Raises:
            ValueError: Если URL некорректный
            ConnectionError: Если не удалось подключиться
        """
        sheet_id = GoogleSheetsImporter.extract_sheet_id(url)
        if not sheet_id:
            raise ValueError(
                "Неверный URL Google Sheets. "
                "Ожидаемый формат: https://docs.google.com/spreadsheets/d/ID_ТАБЛИЦЫ/edit"
            )

        gid = GoogleSheetsImporter.extract_gid(url)
        csv_url = GoogleSheetsImporter.build_csv_url(sheet_id, gid)

        try:
            # Скачиваем CSV
            with urllib.request.urlopen(csv_url, timeout=30) as response:
                csv_data = response.read().decode('utf-8')

            # Парсим CSV
            df = pd.read_csv(StringIO(csv_data))

            return df

        except urllib.error.HTTPError as e:
            if e.code == 404:
                raise ConnectionError(
                    "Таблица не найдена. Убедитесь, что:\n"
                    "1. URL корректный\n"
                    "2. Таблица опубликована для чтения (Файл → Поделиться → Доступ по ссылке → 'Все, у кого есть ссылка')"
                )
            raise ConnectionError(f"Ошибка HTTP {e.code}: {e.reason}")
        except urllib.error.URLError as e:
            raise ConnectionError(f"Не удалось подключиться к Google Sheets: {e.reason}")
        except Exception as e:
            raise ConnectionError(f"Ошибка импорта: {e}")

    @staticmethod
    def validate_url(url: str) -> tuple[bool, str]:
        """
        Проверка корректности URL

        Returns:
            (валиден, сообщение)
        """
        if not url or not url.strip():
            return False, "URL не может быть пустым"

        if 'docs.google.com/spreadsheets' not in url:
            return False, "URL должен содержать 'docs.google.com/spreadsheets'"

        sheet_id = GoogleSheetsImporter.extract_sheet_id(url)
        if not sheet_id:
            return False, "Не удалось извлечь ID таблицы из URL"

        return True, "URL корректный"