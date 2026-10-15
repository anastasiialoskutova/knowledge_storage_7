
import os
from rdflib import Graph

# 1. Завантажуємо вашу онтологію
print("Завантаження онтології...")
g = Graph()
g.parse("models/onto_data.ttl", format="turtle")
print("Онтологію успішно завантажено!\n" + "=" * 50)

# 2. Шлях до папки з CQ-запитами
cq_dir = "tests/cq_sparql"

if not os.path.exists(cq_dir):
  print(f"Помилка: Папка '{cq_dir}' не знайдена.")
  exit()

cq_files = sorted([f for f in os.listdir(cq_dir) if f.endswith(".rq")])

# 3. Запускаємо кожен запит
for file_name in cq_files:
  file_path = os.path.join(cq_dir, file_name)
  print(f"\n--- ВИКОНАННЯ ЗАПИТУ: {file_name} ---")

  with open(file_path, "r", encoding="utf-8") as f:
    query_text = f.read()

  first_line = query_text.strip().split("\n")[0]
  print(f"Опис: {first_line}")

  try:
    results = g.query(query_text)
    row_count = 0
    for row in results:
      row_count += 1
      # Безпечне виведення значень (працює і для URIRef, і для Literal)
      row_str = " | ".join(
          [
              f"{var}: {val.fragment if hasattr(val, 'fragment') and val.fragment else val}"
              for var, val in row.asdict().items()
          ]
      )
      print(f"  [Рядок {row_count}] {row_str}")

    if row_count == 0:
      print("  (Запит виконано, але результатів не знайдено)")
    else:
      print(f"Успішно! Знайдено рядків: {row_count}")

  except Exception as e:
    print(f"Помилка при виконанні запиту {file_name}: {e}")

print("\n" + "=" * 50)
print("Усі CQ-тести успішно опраційовані!")