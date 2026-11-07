"""
Тест сравнения периодов
"""

import pandas as pd
from reports.period_comparison import PeriodComparator


def test_comparison():
    print("=== Тест сравнения периодов ===\n")

    # Создаём тестовые данные за 2 месяца
    test_data = {
        'date': pd.to_datetime([
            '2024-01-05', '2024-01-10', '2024-01-15', '2024-01-20', '2024-01-25',
            '2024-02-03', '2024-02-08', '2024-02-12', '2024-02-18', '2024-02-25'
        ]),
        'region': ['North', 'South', 'East', 'West', 'North', 'South', 'East', 'West', 'North', 'South'],
        'product': ['A', 'B', 'C', 'A', 'B', 'C', 'A', 'B', 'C', 'A'],
        'units_sold': [10, 15, 20, 12, 18, 25, 30, 22, 28, 35],
        'unit_price': [100, 150, 200, 100, 150, 200, 100, 150, 200, 100],
        'cost_price': [70, 100, 150, 70, 100, 150, 70, 100, 150, 70],
        'profit': [300, 750, 1000, 360, 900, 1250, 900, 1100, 1400, 1050],
        'customer': ['C1', 'C2', 'C3', 'C1', 'C2', 'C3', 'C1', 'C2', 'C3', 'C1'],
        'manager': ['M1', 'M2', 'M3', 'M1', 'M2', 'M3', 'M1', 'M2', 'M3', 'M1']
    }

    df = pd.DataFrame(test_data)
    df['revenue'] = df['units_sold'] * df['unit_price']

    print("Тестовые данные:")
    print(f"  Январь: 5 транзакций")
    print(f"  Февраль: 5 транзакций")
    print()

    # Сравнение января и февраля
    comparison = PeriodComparator.compare_periods(
        df,
        '2024-01-01', '2024-01-31',
        '2024-02-01', '2024-02-29'
    )

    if comparison:
        print("📊 Результаты сравнения:")
        print()

        # Период 1
        p1 = comparison['period1']
        print(f"📅 {p1['period_name']} (Январь):")
        print(f"   Выручка: {p1['revenue']:,.0f} ₽")
        print(f"   Прибыль: {p1['profit']:,.0f} ₽")
        print(f"   Единиц продано: {p1['units_sold']}")
        print(f"   Транзакций: {p1['transactions']}")
        print(f"   Средний чек: {p1['avg_check']:,.2f} ₽")
        print()

        # Период 2
        p2 = comparison['period2']
        print(f"📅 {p2['period_name']} (Февраль):")
        print(f"   Выручка: {p2['revenue']:,.0f} ₽")
        print(f"   Прибыль: {p2['profit']:,.0f} ₽")
        print(f"   Единиц продано: {p2['units_sold']}")
        print(f"   Транзакций: {p2['transactions']}")
        print(f"   Средний чек: {p2['avg_check']:,.2f} ₽")
        print()

        # Изменения
        print("📈 Изменения (Февраль vs Январь):")
        for metric, change in comparison['changes'].items():
            direction = "⬆️" if change['direction'] == 'up' else ("⬇️" if change['direction'] == 'down' else "➡️")
            print(f"   {direction} {metric}: {change['absolute']:+,.0f} ({change['percent']:+.1f}%)")

        print()
        print("=" * 70)
        print("✅ Тест сравнения периодов прошёл успешно!")
    else:
        print("❌ Ошибка: не удалось сравнить периоды")


if __name__ == "__main__":
    test_comparison()