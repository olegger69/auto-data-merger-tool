"""
Показать все файлы в папке
"""

import os

folder = r"C:\Users\Oleg\Documents\Data_Analyst\Файлы по блоку курса Excel"

print(f"=== Файлы в папке: {folder} ===\n")

if not os.path.exists(folder):
    print(f"❌ Папка не существует: {folder}")
else:
    files = os.listdir(folder)
    for i, f in enumerate(files, 1):
        full_path = os.path.join(folder, f)
        size = os.path.getsize(full_path) if os.path.isfile(full_path) else 0
        print(f"{i}. {f}  ({size:,} байт)")

    print(f"\nВсего файлов: {len(files)}")