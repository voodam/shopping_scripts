#ukazka.ru
class Partsdirect(Shop):
  def __init__(self, driver):
    Shop.__init__(
      self, driver,
      "https://ekb.partsdirect.ru",
      "/search_results?sort=inexpensive&q=%s",
      "/basket"
    )

class Intelekt(Shop):
  def __init__(self, driver):
    Shop.__init__(
      self, driver,
      "https://www.intel-ekt.ru/",
      "catalog/search/?keyword=%s",
      "/order/"
    )

class Nix(Shop):
  def __init__(self, driver):
    Shop.__init__(
      self, driver,
      "https://e-burg.nix.ru",
      "/price/search_panel_ajax.html#t:goods;k:%s",
      "/scripts/order_cb.html"
    )

class Dns(Shop):
  def __init__(self, driver):
    Shop.__init__(
      self, driver,
      "https://www.dns-shop.ru",
      "/search/?q=%s",
      "/order/begin/"
    )

class Eldorado(Shop):
  def __init__(self, driver):
    Shop.__init__(
      self, driver,
      "https://www.eldorado.ru",
      "/search/catalog.php?sort=price&type=ASC&q=%s",
      "#listing-container > ul",
      "/personal/basket.php"
    )

  def _get_all_product_elements(self):
    return self.driver.find_elements(By.CSS_SELECTOR, "#listing-container > ul > li")

  def _product_factory(self, element):
    return EldoradoProduct(element)

class EldoradoProduct(SimpleProduct):
  def __init__(self, element):
    SimpleProduct.__init__(
      self, element,
      "[data-dy='title']",
      "[data-pc='offer_price']",
      "button[data-dy='button']"
    )


      WebDriverWait(element, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, name_selector)))
      WebDriverWait(element, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, price_selector))),
      WebDriverWait(element, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, cart_button_selector)))
