"""
Тест интерактивных графиков Plotly
"""

import pandas as pd
from core.plotly_charts import PlotlyCharts


def test_plotly():
    print("=" * 70)
    print("Тест интерактивных графиков Plotly")
    print("=" * 70)

    # Создаём тестовые данные
    test_data = {
        'period': ['2026-07', '2026-08', '2026-09', '2026-10', '2026-11', '2026-12'],
        'revenue': [100000, 120000, 135000, 150000, 170000, 185000]
    }

    df = pd.DataFrame(test_data)

    print("\n📊 Тестовые данные:")
    print(df.to_string(index=False))

    # Создаём линейный график
    print("\n📈 Создание интерактивного линейного графика...")
    fig = PlotlyCharts.create_line_chart(
        df, 'period', 'revenue',
        'Динамика выручки по месяцам',
        'Период', 'Выручка (₽)'
    )

    # Сохраняем в HTML
    html_path = 'test_data/test_plotly_chart.html'
    PlotlyCharts.save_figure(fig, html_path, format='html')
    print(f"✅ График сохранён: {html_path}")
    print(f"   Открой файл в браузере, чтобы увидеть интерактивный график!")

    # Сохраняем в PNG
    png_path = 'test_data/test_plotly_chart.png'
    try:
        PlotlyCharts.save_figure(fig, png_path, format='png')
        print(f"✅ График сохранён: {png_path}")
    except Exception as e:
        print(f"⚠️ Не удалось сохранить PNG (возможно, kaleido не установлен): {e}")

    print("\n" + "=" * 70)
    print("💡 В браузере ты сможешь:")
    print("   • Наводить мышь на точки для просмотра значений")
    print("   • Зумить колёсиком мыши")
    print("   • Перемещать график")
    print("   • Выделять области")
    print("   • Сохранять в PNG через панель инструментов")
    print("=" * 70)


if __name__ == "__main__":
    test_plotly()