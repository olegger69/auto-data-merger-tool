"""
Управление темами приложения (светлая и тёмная)
"""

from typing import Dict


class ThemeManager:
    """Менеджер тем оформления"""

    # Светлая тема (по умолчанию)
    LIGHT_THEME = {
        'bg_primary': '#F0F0F0',
        'bg_secondary': '#FFFFFF',
        'bg_tertiary': '#E8E8E8',
        'text_primary': '#000000',
        'text_secondary': '#555555',
        'text_muted': '#888888',
        'accent': '#2196F3',
        'accent_hover': '#1976D2',
        'border': '#CCCCCC',
        'success': '#4CAF50',
        'warning': '#FF9800',
        'error': '#F44336',
        'chart_colors': ['#4C72B0', '#55A868', '#C44E52', '#8172B2', '#CCB974', '#64B5CD'],
        'chart_bg': '#FFFFFF',
        'chart_grid': '#E0E0E0'
    }

    # Тёмная тема
    DARK_THEME = {
        'bg_primary': '#1E1E1E',
        'bg_secondary': '#2D2D2D',
        'bg_tertiary': '#3D3D3D',
        'text_primary': '#FFFFFF',
        'text_secondary': '#B0B0B0',
        'text_muted': '#808080',
        'accent': '#64B5F6',
        'accent_hover': '#42A5F5',
        'border': '#555555',
        'success': '#81C784',
        'warning': '#FFB74D',
        'error': '#E57373',
        'chart_colors': ['#64B5F6', '#81C784', '#E57373', '#9575CD', '#FFD54F', '#4DD0E1'],
        'chart_bg': '#2D2D2D',
        'chart_grid': '#404040'
    }

    @staticmethod
    def get_theme(theme_name: str) -> Dict:
        """Получение настроек темы по имени"""
        if theme_name == 'dark':
            return ThemeManager.DARK_THEME.copy()
        return ThemeManager.LIGHT_THEME.copy()

    @staticmethod
    def get_available_themes():
        """Список доступных тем"""
        return ['light', 'dark']