"""
Тест модуля прогнозирования (с актуальными датами)
"""

import pandas as pd
import numpy as np
from core.forecast import Forecaster


def test_forecast():
    print("=" * 70)
    print("Тест прогнозирования на основе линейной регрессии")
    print("=" * 70)

    # Создаём тестовые данные с трендом роста за вторую половину 2026 года
    test_data = {
        'period': ['2026-07', '2026-08', '2026-09', '2026-10', '2026-11', '2026-12'],
        'revenue': [100000, 120000, 135000, 150000, 170000, 185000]
    }

    df = pd.DataFrame(test_data)

    print("\n📊 Исторические данные (2-е полугодие 2026):")
    print(df.to_string(index=False))

    # Прогноз на 3 месяца (должен показать январь, февраль, март 2027)
    print("\n📈 Прогноз на 3 месяца вперёд (линейная регрессия):")
    forecast_df = Forecaster.linear_forecast(df, 'period', 'revenue', periods=3, degree=1)

    if forecast_df is not None:
        print(forecast_df.to_string(index=False))

        # Точность модели
        accuracy = Forecaster.calculate_accuracy(df, 'period', 'revenue', degree=1)
        if accuracy is not None:
            print(f"\n🎯 Точность модели (R²): {accuracy:.2%}")
            if accuracy > 0.8:
                print("   ✅ Отличная точность! Прогноз надёжен.")
            elif accuracy > 0.6:
                print("   ⚠️ Хорошая точность, но есть погрешность.")
            else:
                print("   ❌ Низкая точность — данные слишком хаотичны для линейного прогноза.")
    else:
        print("❌ Не удалось построить прогноз")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    test_forecast()