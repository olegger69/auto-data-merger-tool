"""
Тест модуля корреляций
"""

import pandas as pd
import numpy as np
from core.correlation import CorrelationAnalyzer


def test_correlation():
    print("=" * 70)
    print("Тест анализа корреляций")
    print("=" * 70)

    # Создаём тестовые данные с явными зависимостями
    np.random.seed(42)
    n = 50

    units = np.random.randint(5, 50, n)
    price = np.random.uniform(100, 500, n)
    revenue = units * price + np.random.normal(0, 1000, n)  # revenue ~ units * price
    cost = price * 0.7 + np.random.normal(0, 10, n)
    profit = revenue - units * cost

    df = pd.DataFrame({
        'units_sold': units,
        'unit_price': price,
        'revenue': revenue,
        'cost_price': cost,
        'profit': profit
    })

    print("\n📊 Тестовые данные (первые 5 строк):")
    print(df.head().to_string(index=False))

    # Считаем корреляции
    corr_matrix = CorrelationAnalyzer.calculate_correlation_matrix(df)

    if corr_matrix is not None:
        print("\n🔗 Матрица корреляций:")
        print(corr_matrix.round(3).to_string())

        # Сильные связи
        strong = CorrelationAnalyzer.get_strong_correlations(corr_matrix, threshold=0.5)

        print(f"\n💡 Сильные корреляции (|r| > 0.5):")
        labels = CorrelationAnalyzer.get_column_labels(list(corr_matrix.columns))

        for col1, col2, value in strong:
            interpretation = CorrelationAnalyzer.interpret_correlation(value)
            print(f"   • {labels[col1]} ↔ {labels[col2]}: {value:+.3f} ({interpretation})")

        if not strong:
            print("   (сильных связей не обнаружено)")
    else:
        print("❌ Не удалось построить матрицу корреляций")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    test_correlation()