"""
Окно для отображения интерактивных Plotly графиков через pywebview
"""

import webview
import plotly.graph_objects as go
from typing import Optional


class PlotlyViewer:
    """
    Отдельное окно с интерактивным Plotly графиком.
    Использует pywebview для отображения HTML с графиком.
    """

    @staticmethod
    def show_chart(fig: go.Figure, title: str = "Интерактивный график"):
        """
        Показать Plotly график в отдельном окне

        Args:
            fig: Plotly Figure объект
            title: Заголовок окна
        """
        # Генерируем HTML с графиком
        html_content = fig.to_html(
            include_plotlyjs=True,
            full_html=True,
            config={
                'displayModeBar': True,
                'modeBarButtonsToRemove': ['lasso2d', 'select2d'],
                'toImageButtonOptions': {
                    'format': 'png',
                    'filename': title,
                    'height': 800,
                    'width': 1200,
                    'scale': 2
                }
            }
        )

        # Создаём окно pywebview
        window = webview.create_window(
            title=title,
            html=html_content,
            width=1000,
            height=700,
            resizable=True,
            min_size=(600, 400)
        )

        # Запускаем окно (блокирует выполнение до закрытия)
        webview.start(debug=False)

    @staticmethod
    def show_chart_async(fig: go.Figure, title: str = "Интерактивный график"):
        """
        Показать Plotly график в отдельном окне (неблокирующий вызов)

        Args:
            fig: Plotly Figure объект
            title: Заголовок окна
        """
        html_content = fig.to_html(
            include_plotlyjs=True,
            full_html=True,
            config={
                'displayModeBar': True,
                'modeBarButtonsToRemove': ['lasso2d', 'select2d'],
                'toImageButtonOptions': {
                    'format': 'png',
                    'filename': title,
                    'height': 800,
                    'width': 1200,
                    'scale': 2
                }
            }
        )

        # Сохраняем HTML во временный файл
        import tempfile
        import os

        temp_file = os.path.join(tempfile.gettempdir(), f"plotly_{title.replace(' ', '_')}.html")
        with open(temp_file, 'w', encoding='utf-8') as f:
            f.write(html_content)

        # Открываем в браузере по умолчанию
        import webbrowser
        webbrowser.open(f'file://{temp_file}')