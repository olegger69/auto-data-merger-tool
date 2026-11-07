"""
Создание тестовой SQLite базы данных
"""

import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import random


def create_test_database():
    # Создаём подключение к SQLite
    conn = sqlite3.connect('test_data/test_sales.db')
    cursor = conn.cursor()

    # Создаём таблицу sales
    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS sales
                   (
                       id
                       INTEGER
                       PRIMARY
                       KEY
                       AUTOINCREMENT,
                       date
                       TEXT
                       NOT
                       NULL,
                       region
                       TEXT
                       NOT
                       NULL,
                       product
                       TEXT
                       NOT
                       NULL,
                       units_sold
                       INTEGER
                       NOT
                       NULL,
                       unit_price
                       REAL
                       NOT
                       NULL
                   )
                   ''')

    # Генерируем тестовые данные
    regions = ['North', 'South', 'East', 'West']
    products = ['Laptop', 'Monitor', 'Phone', 'Tablet']

    base_date = datetime(2026, 7, 1)
    data = []

    for i in range(50):
        date = (base_date + timedelta(days=i)).strftime('%Y-%m-%d')
        region = random.choice(regions)
        product = random.choice(products)
        units = random.randint(5, 50)
        price = round(random.uniform(200, 1000), 2)
        data.append((date, region, product, units, price))

    # Вставляем данные
    cursor.executemany(
        'INSERT INTO sales (date, region, product, units_sold, unit_price) VALUES (?, ?, ?, ?, ?)',
        data
    )

    conn.commit()
    conn.close()

    print("✅ Тестовая база данных создана: test_data/test_sales.db")
    print(f"   Таблица: sales")
    print(f"   Строк: {len(data)}")


if __name__ == "__main__":
    create_test_database()