from rdflib import Graph

# Створюємо граф та завантажуємо ваш єдиний файл з онтологією та індивідами
# (замініть 'ontology.ttl' на реальну назву вашого файлу, наприклад 'data.ttl')
g = Graph()
g.parse("models/onto_data.ttl", format="turtle")

print("--- РЕЗУЛЬТАТ ЗАПИТУ 1: Рекомендації з високим балом ---")
query1 = """
PREFIX : <http://example.org/ecommerce-recommendations#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

SELECT ?customerId ?productName ?score ?modelId WHERE {
    ?rec a :Recommendation ;
         :generatedFor ?customer ;
         :recommendsProduct ?product ;
         :producedByModel ?model ;
         :recommendationScore ?score .
         
    ?customer :customerId ?customerId .
    ?product :productName ?productName .
    ?model :modelVersion ?modelId .
    
    FILTER(?score > 0.90)
}
"""
for row in g.query(query1):
  print(
      f"Клієнт: {row.customerId} | Товар: {row.productName} | Бал:"
      f" {row.score} | Модель: {row.modelId}"
  )

print("\n--- РЕЗУЛЬТАТ ЗАПИТУ 2: Товари, ціни та наявність ---")
query2 = """
PREFIX : <http://example.org/ecommerce-recommendations#>

SELECT ?productId ?productName ?priceAmount ?currency ?stockQuantity WHERE {
    ?product a :Product ;
             :productId ?productId ;
             :productName ?productName ;
             :hasOffer ?offer ;
             :hasInventory ?inventory .
             
    ?offer :hasPrice ?price .
    ?price :priceAmount ?priceAmount ;
           :currency ?currency .
           
    ?inventory :stockQuantity ?stockQuantity .
}
"""
for row in g.query(query2):
  print(
      f"ID: {row.productId} | Назва: {row.productName} | Ціна:"
      f" {row.priceAmount} {row.currency} | На складі: {row.stockQuantity}"
  )