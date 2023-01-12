import logging, re
from helpers import flatmap, throw

def includes_words(target, query):
  query_words = set(query.lower().split())
  target_words = re.split("\.* ", target.lower().replace(",", "."))
  return query_words.issubset(target_words)

def constructor(choose_many):
  def strategy(shop, query):
    shop.search(query)
    all_products = shop.get_all_products()
    products = [product for product in all_products
      if includes_words(product.get_name(), query)]
    count = len(products)
    logging.info(f"Filtered products: {count}")
    logging.info(f"Full list: {len(all_products)}, {all_products}")

    if count == 0:
      return []
    elif count == 1:
      return [products[0]]
    else:
      return choose_many(products)
  return strategy

def first_from_many(products):
  assert len(products) > 0
  return [products[0]]

def all_from_many(products):
  return products

def reduce_price(products, reduce):
  if not products:
    return []
  product = reduce(products, key=lambda product: product.get_price())
  return [product]

def min_price_from_many(products):
  return reduce_price(products, min)

def max_price_from_many(products):
  return reduce_price(products, max)

first = constructor(first_from_many)
all = constructor(all_from_many)
min_price = constructor(min_price_from_many)
max_price = constructor(max_price_from_many)

def ask(shop, query):
  shop.search(query)
  print(f"Please choose the product you want in the browser," +
        " and then press Enter in the command line")
  input()
  return []

def smart(shop, query_line):
  query_list, *flags = query_line.split("|")
  queries = query_list.split(",")

  flags = flags[0] if flags else "ask"
  main_flag, *list_flag = flags.split(",")
  list_flag = list_flag[0] if list_flag else "ask"

  if main_flag == "fbc":
    for query in queries:
      products = smart(shop, f"{query}|{list_flag}")
      if products:
        return products
    return []
  elif main_flag == "mlt":
    products = flatmap(lambda: smart(shop, f"{query}|{list_flag}"), products)
    return min_price_from_many(products)
  else:
    strategies = {
      "fst": first,
      "all": all,
      "ask": ask,
      "min": min_price,
      "max": max_price
    }
    strategy = strategies.get(main_flag) \
      or throw(ValueError(f"No strategy with name {main_flag}"))
    return strategy(shop, queries[0])
