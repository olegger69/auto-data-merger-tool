"""
Менеджер настроек приложения
Сохраняет и загружает пользовательские настройки в config.json
"""

import json
import os
from pathlib import Path
from typing import Any, Dict


class ConfigManager:
    """Менеджер настроек приложения"""

    # Имя папки для хранения настроек
    APP_FOLDER = '.auto_data_merger'
    CONFIG_FILENAME = 'config.json'

    # Значения по умолчанию
    DEFAULTS = {
        'version': '1.0',
        'last_import_folder': '',
        'last_export_folder': '',
        'window_width': 1200,
        'window_height': 800,
        'window_x': 100,
        'window_y': 100,
        'theme': 'light',
        'chart_color_scheme': 'default'
    }

    def __init__(self):
        self.config_path = self._get_config_path()
        self.config = self._load()

    def _get_config_path(self) -> Path:
        """Получение пути к файлу конфигурации"""
        config_dir = Path.home() / self.APP_FOLDER
        config_dir.mkdir(exist_ok=True)
        return config_dir / self.CONFIG_FILENAME

    def _load(self) -> Dict[str, Any]:
        """Загрузка настроек из файла"""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    saved_config = json.load(f)
                # Объединяем с defaults (чтобы новые поля появлялись автоматически)
                config = self.DEFAULTS.copy()
                config.update(saved_config)
                return config
            except (json.JSONDecodeError, IOError) as e:
                print(f"⚠️ Ошибка чтения config.json: {e}. Используются значения по умолчанию.")
                return self.DEFAULTS.copy()
        else:
            return self.DEFAULTS.copy()

    def _save(self):
        """Сохранение настроек в файл"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"⚠️ Ошибка сохранения config.json: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        """Получение значения настройки"""
        return self.config.get(key, default if default is not None else self.DEFAULTS.get(key))

    def set(self, key: str, value: Any):
        """Установка значения настройки и сохранение"""
        self.config[key] = value
        self._save()

    def get_all(self) -> Dict[str, Any]:
        """Получение всех настроек"""
        return self.config.copy()

    def reset(self):
        """Сброс настроек к значениям по умолчанию"""
        self.config = self.DEFAULTS.copy()
        self._save()

    def update_window_geometry(self, width: int, height: int, x: int, y: int):
        """Сохранение геометрии окна"""
        self.set('window_width', width)
        self.set('window_height', height)
        self.set('window_x', x)
        self.set('window_y', y)

    def set_last_import_folder(self, folder: str):
        """Сохранение последней папки импорта"""
        if folder and os.path.isdir(folder):
            self.set('last_import_folder', folder)

    def set_last_export_folder(self, folder: str):
        """Сохранение последней папки экспорта"""
        if folder and os.path.isdir(folder):
            self.set('last_export_folder', folder)