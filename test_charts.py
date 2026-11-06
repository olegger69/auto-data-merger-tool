"""
Тест построения графиков
"""

import pandas as pd
import os
from charts.plots import ChartBuilder


def test_charts():
    print("=== Тест построения графиков ===\n")

    os.makedirs('test_data', exist_ok=True)

    # 1. Тестовые данные для столбчатой диаграммы (по продуктам)
    df_product = pd.DataFrame({
        'product': ['Ноутбук', 'Смартфон', 'Планшет'],
        'revenue': [150000.0, 85000.0, 42000.0]
    })

    # 2. Тестовые данные для линейного графика (по месяцам)
    df_month = pd.DataFrame({
        'period': ['2024-01', '2024-02', '2024-03', '2024-04'],
        'revenue': [120000.0, 135000.0, 110000.0, 160000.0]
    })

    print("Генерация графиков...")

    # Создаём графики
    fig_product = ChartBuilder.create_bar_chart(
        df=df_product,
        x_col='product',
        y_col='revenue',
        title='Выручка по продуктам',
        x_label='Продукт',
        y_label='Выручка (руб.)'
    )

    fig_month = ChartBuilder.create_line_chart(
        df=df_month,
        x_col='period',
        y_col='revenue',
        title='Динамика выручки по месяцам',
        x_label='Месяц',
        y_label='Выручка (руб.)'
    )

    # Сохраняем в файлы для проверки
    ChartBuilder.save_figure(fig_product, 'test_data/chart_products.png')
    ChartBuilder.save_figure(fig_month, 'test_data/chart_month.png')

    print("✅ Графики успешно созданы и сохранены:")
    print("  - test_data/chart_products.png")
    print("  - test_data/chart_month.png")
    print("\nОткройте эти файлы, чтобы проверить отображение кириллицы и значений.")


if __name__ == "__main__":
    test_charts()