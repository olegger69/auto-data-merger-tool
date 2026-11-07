"""
Управление цветовыми палитрами для графиков
"""

from typing import Dict, List


class ChartPalettes:
    """Менеджер цветовых палитр для графиков"""

    # Предустановленные палитры
    PALETTES = {
        'classic': {
            'name': '🎨 Классическая',
            'description': 'Синий, зелёный, красный — стандартная аналитика',
            'bar_colors': ['#4C72B0', '#55A868', '#C44E52', '#8172B2', '#CCB974', '#64B5CD'],
            'line_colors': ['#C44E52', '#4C72B0', '#55A868', '#8172B2', '#CCB974'],
            'pie_colors': ['#4C72B0', '#55A868', '#C44E52', '#8172B2', '#CCB974', '#64B5CD', '#DD8452', '#937860'],
            'positive': '#55A868',
            'negative': '#C44E52'
        },
        'pastel': {
            'name': '🌸 Пастельная',
            'description': 'Мягкие, спокойные тона',
            'bar_colors': ['#AEC6CF', '#B2D8B2', '#FFB7B2', '#C3B1E1', '#FDFD96', '#B5EAD7'],
            'line_colors': ['#FFB7B2', '#AEC6CF', '#B2D8B2', '#C3B1E1', '#FDFD96'],
            'pie_colors': ['#AEC6CF', '#B2D8B2', '#FFB7B2', '#C3B1E1', '#FDFD96', '#B5EAD7', '#FFDAC1', '#E2B0FF'],
            'positive': '#B2D8B2',
            'negative': '#FFB7B2'
        },
        'vibrant': {
            'name': '⚡ Яркая',
            'description': 'Насыщенные, контрастные цвета',
            'bar_colors': ['#FF6B6B', '#4ECDC4', '#FFE66D', '#95E1D3', '#F38181', '#AA96DA'],
            'line_colors': ['#FF6B6B', '#4ECDC4', '#FFE66D', '#95E1D3', '#F38181'],
            'pie_colors': ['#FF6B6B', '#4ECDC4', '#FFE66D', '#95E1D3', '#F38181', '#AA96DA', '#FCBAD3', '#A8D8EA'],
            'positive': '#4ECDC4',
            'negative': '#FF6B6B'
        },
        'monochrome': {
            'name': '⚫ Монохромная',
            'description': 'Оттенки серого — минимализм',
            'bar_colors': ['#2C2C2C', '#4A4A4A', '#6B6B6B', '#8C8C8C', '#ADADAD', '#CECECE'],
            'line_colors': ['#2C2C2C', '#4A4A4A', '#6B6B6B', '#8C8C8C', '#ADADAD'],
            'pie_colors': ['#2C2C2C', '#4A4A4A', '#6B6B6B', '#8C8C8C', '#ADADAD', '#CECECE', '#EFEFEF', '#1A1A1A'],
            'positive': '#4A4A4A',
            'negative': '#8C8C8C'
        },
        'corporate': {
            'name': '💼 Корпоративная',
            'description': 'Профессиональные деловые тона',
            'bar_colors': ['#1F4E79', '#2E75B6', '#5B9BD5', '#9DC3E6', '#D9E2F3', '#7F7F7F'],
            'line_colors': ['#C00000', '#1F4E79', '#2E75B6', '#5B9BD5', '#7F7F7F'],
            'pie_colors': ['#1F4E79', '#2E75B6', '#5B9BD5', '#9DC3E6', '#D9E2F3', '#7F7F7F', '#C00000', '#ED7D31'],
            'positive': '#2E75B6',
            'negative': '#C00000'
        }
    }

    @staticmethod
    def get_palette(palette_name: str) -> Dict:
        """Получение палитры по имени"""
        if palette_name in ChartPalettes.PALETTES:
            return ChartPalettes.PALETTES[palette_name].copy()
        return ChartPalettes.PALETTES['classic'].copy()

    @staticmethod
    def get_available_palettes() -> List[str]:
        """Список доступных палитр"""
        return list(ChartPalettes.PALETTES.keys())

    @staticmethod
    def get_palette_names() -> Dict[str, str]:
        """Словарь {имя: полное_название}"""
        return {key: val['name'] for key, val in ChartPalettes.PALETTES.items()}