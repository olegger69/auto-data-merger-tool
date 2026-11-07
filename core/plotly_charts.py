"""
Интерактивные графики с использованием Plotly
"""

import plotly.graph_objects as go
import pandas as pd
from typing import Optional, List


class PlotlyCharts:
    """Генератор интерактивных графиков Plotly"""

    @staticmethod
    def create_bar_chart(
            df: pd.DataFrame,
            x_col: str,
            y_col: str,
            title: str,
            x_label: str,
            y_label: str,
            colors: Optional[List[str]] = None
    ) -> go.Figure:
        """Создание интерактивной столбчатой диаграммы"""
        if df.empty:
            fig = go.Figure()
            fig.update_layout(title="Нет данных")
            return fig

        if colors is None:
            colors = ['#4C72B0', '#55A868', '#C44E52', '#8172B2', '#CCB974', '#64B5CD']

        fig = go.Figure(data=[
            go.Bar(
                x=df[x_col].astype(str),
                y=df[y_col],
                marker_color=colors * (len(df) // len(colors) + 1),
                text=[f'{val:,.0f}'.replace(',', ' ') for val in df[y_col]],
                textposition='outside',
                hovertemplate=f'{x_label}: %{{x}}<br>{y_label}: %{{y:,.2f}} ₽<extra></extra>'
            )
        ])

        fig.update_layout(
            title={'text': title, 'font': {'size': 16, 'color': 'black'}, 'x': 0.5},
            xaxis_title=x_label,
            yaxis_title=y_label,
            xaxis_tickangle=-45,
            hovermode='x unified',
            template='plotly_white',
            height=500,
            margin=dict(l=60, r=30, t=60, b=60)
        )

        # Исправлено: griddash вместо gridstyle
        fig.update_yaxes(gridcolor='#E0E0E0', gridwidth=1, griddash='dash')
        return fig

    @staticmethod
    def create_line_chart(
            df: pd.DataFrame,
            x_col: str,
            y_col: str,
            title: str,
            x_label: str,
            y_label: str,
            color: str = '#C44E52'
    ) -> go.Figure:
        """Создание интерактивного линейного графика"""
        if df.empty:
            fig = go.Figure()
            fig.update_layout(title="Нет данных")
            return fig

        fig = go.Figure(data=[
            go.Scatter(
                x=df[x_col].astype(str),
                y=df[y_col],
                mode='lines+markers',
                marker=dict(size=8, color=color),
                line=dict(color=color, width=3),
                fill='tozeroy',
                hovertemplate=f'{x_label}: %{{x}}<br>{y_label}: %{{y:,.2f}} ₽<extra></extra>'
            )
        ])

        fig.update_layout(
            title={'text': title, 'font': {'size': 16, 'color': 'black'}, 'x': 0.5},
            xaxis_title=x_label,
            yaxis_title=y_label,
            xaxis_tickangle=-45,
            hovermode='x unified',
            template='plotly_white',
            height=500,
            margin=dict(l=60, r=30, t=60, b=60)
        )

        # Исправлено: griddash вместо gridstyle
        fig.update_xaxes(gridcolor='#E0E0E0', gridwidth=1, griddash='dash')
        fig.update_yaxes(gridcolor='#E0E0E0', gridwidth=1, griddash='dash')
        return fig

    @staticmethod
    def create_forecast_chart(
            historical_df: pd.DataFrame,
            forecast_df: pd.DataFrame,
            x_col: str,
            y_col: str,
            title: str,
            x_label: str,
            y_label: str
    ) -> go.Figure:
        """Создание графика с прогнозом (история + прогноз пунктиром)"""
        if historical_df.empty:
            fig = go.Figure()
            fig.update_layout(title="Нет данных")
            return fig

        fig = go.Figure()

        # Исторические данные (сплошная линия)
        fig.add_trace(go.Scatter(
            x=historical_df[x_col].astype(str),
            y=historical_df[y_col],
            mode='lines+markers',
            name='Исторические данные',
            marker=dict(size=8, color='#4C72B0'),
            line=dict(color='#4C72B0', width=3),
            hovertemplate=f'{x_label}: %{{x}}<br>{y_label}: %{{y:,.2f}} ₽<extra></extra>'
        ))

        # Прогнозные данные (пунктирная линия)
        if not forecast_df.empty:
            fig.add_trace(go.Scatter(
                x=forecast_df[x_col].astype(str),
                y=forecast_df[y_col],
                mode='lines+markers',
                name='Прогноз',
                marker=dict(size=8, color='#C44E52', symbol='diamond'),
                line=dict(color='#C44E52', width=3, dash='dash'),
                hovertemplate=f'{x_label}: %{{x}}<br>Прогноз {y_label}: %{{y:,.2f}} ₽<extra></extra>'
            ))

        fig.update_layout(
            title={'text': title, 'font': {'size': 16, 'color': 'black'}, 'x': 0.5},
            xaxis_title=x_label,
            yaxis_title=y_label,
            xaxis_tickangle=-45,
            hovermode='x unified',
            template='plotly_white',
            height=500,
            margin=dict(l=60, r=30, t=60, b=60),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )

        # Исправлено: griddash вместо gridstyle
        fig.update_xaxes(gridcolor='#E0E0E0', gridwidth=1, griddash='dash')
        fig.update_yaxes(gridcolor='#E0E0E0', gridwidth=1, griddash='dash')
        return fig

    @staticmethod
    def save_figure(fig: go.Figure, filepath: str, format: str = 'png'):
        """Сохранение графика в файл"""
        if format == 'html':
            fig.write_html(filepath)
        elif format == 'png':
            fig.write_image(filepath, scale=2)
        elif format == 'svg':
            fig.write_image(filepath, format='svg')
        else:
            raise ValueError(f"Неподдерживаемый формат: {format}")

    @staticmethod
    def show_in_browser(fig: go.Figure):
        """Открыть график в браузере"""
        fig.show()