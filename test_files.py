"""
Тест файлов из папки курса Excel
"""

from diagnose_file import diagnose_file

folder = r"C:\Users\Oleg\Documents\Data_Analyst\Файлы по блоку курса Excel"

# Файл 1: EC03
print("=" * 70)
print("ФАЙЛ 1: EC03")
print("=" * 70)
diagnose_file(f"{folder}\\EC03. Продвинутое управление данными в Excel.xlsx")

# Файл 2: List of Orders (возможно, идеальный для нашего приложения)
print("\n\n")
print("=" * 70)
print("ФАЙЛ 2: List of Orders")
print("=" * 70)
diagnose_file(f"{folder}\\List of Orders.xlsx")