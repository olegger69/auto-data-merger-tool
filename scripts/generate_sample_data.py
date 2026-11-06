"""Генерация тестовых данных в test_data/."""
import random
from datetime import date, timedelta
from pathlib import Path

import pandas as pd

OUT = Path(__file__).resolve().parent.parent / "test_data"
REGIONS = ["North", "South", "East", "West"]
PRODUCTS = ["Laptop", "Phone", "Tablet", "Monitor"]


def make_rows(n: int, start: date) -> pd.DataFrame:
    rows = []
    for i in range(n):
        rows.append({
            "date": (start + timedelta(days=random.randint(0, 90))).isoformat(),
            "region": random.choice(REGIONS),
            "product": random.choice(PRODUCTS),
            "units_sold": random.randint(1, 50),
            "unit_price": round(random.uniform(50, 1500), 2),
        })
    return pd.DataFrame(rows)


def main() -> None:
    random.seed(42)
    OUT.mkdir(exist_ok=True)
    make_rows(60, date(2025, 1, 1)).to_csv(OUT / "sample_sales_1.csv", index=False)
    make_rows(60, date(2025, 3, 1)).to_excel(OUT / "sample_sales_2.xlsx", index=False)
    # Некорректный файл: нет unit_price, плохая дата
    bad = make_rows(5, date(2025, 1, 1)).drop(columns=["unit_price"])
    bad.loc[0, "date"] = "not-a-date"
    bad.to_csv(OUT / "invalid_data.csv", index=False)
    print(f"Файлы созданы в {OUT}")


if __name__ == "__main__":
    main()
