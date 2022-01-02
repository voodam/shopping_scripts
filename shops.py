import time, logging
from config import config
from urllib.parse import urlparse, quote_plus
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import choice_strategies
from helpers import parse_float, wait_until, loc

class Shop:
  def __init__(self, driver, host, search_route, cart_route="/cart",
               all_products_locator=None, wait_products_locator=None):
    self.driver = driver
    self.host = host
    self.search_url = host + search_route
    if cart_route:
      self.cart_url = host + cart_route
    self.all_products_locator = all_products_locator
    self.wait_products_locator = wait_products_locator

    self.driver.get(self.host)
    self._init_cookies()

  def _init_cookies(self):
    domain = urlparse(self.host).netloc
    cookies = config["cookies"].get(domain, [])
    for cookie in cookies:
      logging.info(f"Set cookie: {cookie}")
      self.driver.add_cookie(cookie)

  def search(self, product):
    self.driver.get(self.search_url % quote_plus(product))
    if self.wait_products_locator:
      WebDriverWait(self.driver, 10).until(
        EC.presence_of_element_located(loc(self.wait_products_locator))
      )

    for _ in range(3):
      self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    self.driver.execute_script("window.scrollTo(0, 0);")

  def go_to_cart(self):
    if self.cart_url:
      self.driver.get(self.cart_url)

  def get_all_products(self):
    elements = self.driver.find_elements(*loc(self.all_products_locator))
    products = []
    for element in elements:
      try:
        products.append(self._product_factory(element))
      except NoSuchElementException:
        logging.warning(f"Product wasn't created from element: {element.text}")
    return products

  def _product_factory(self, element):
    raise NotImplementedError()

class Product:
  def __repr__(self):
    return f"{self.get_name()}: {self.get_price()}"

  def get_name(self):
    raise NotImplementedError()

  def get_price(self):
    raise NotImplementedError()

  def add_to_cart(self):
    raise NotImplementedError()

class WaitCartStrategy:
  def element(locator):
    return lambda product: WebDriverWait(product.element, 10).until(
      EC.presence_of_element_located(loc(locator))
    )

  def text(locator, text):
    def find(product):
      return product.shop.driver.find_element(*loc(locator))

    return WaitCartStrategy._text(find, text)

  def button_text(text="В корзине"):
    return WaitCartStrategy._text(lambda product: product.cart_button_element, text)

  def _text(get_element, text):
    return lambda product: wait_until(lambda: text in product.text)

class EquippedProduct(Product):
  def __init__(self, shop, element, name_element, price_element, cart_button_element,
               wait_cart_strategy=WaitCartStrategy.button_text()):
    self.shop = shop
    self.element = element
    self.name_element = name_element
    self.price_element = price_element
    self.cart_button_element = cart_button_element
    self.wait_cart_strategy = wait_cart_strategy

  def get_name(self):
    return self.name_element.text.strip()

  def get_price(self):
    return parse_float(self.price_element.text)

  def add_to_cart(self):
    logging.info(f"Add product to cart: {self}")
    action = ActionChains(self.shop.driver)
    if self.element:
      action.move_to_element(self.element)
    action.click(self.cart_button_element)
    action.perform()
    self.wait_cart_strategy(self)

class SimpleProduct(EquippedProduct):
  def __init__(self, shop, element, name_locator, price_locator, cart_button_locator,
               wait_cart_strategy=WaitCartStrategy.button_text()):
    EquippedProduct.__init__(
      self, shop, element,
      element.find_element(*loc(name_locator)),
      element.find_element(*loc(price_locator)),
      element.find_element(*loc(cart_button_locator)),
      wait_cart_strategy
    )

class DeliveryClub(Shop):
  def __init__(self, driver, store_name):
    Shop.__init__(self, driver,
      "https://www.delivery-club.ru",
      f"/store/{store_name}?grocerySearch=%s",
      "/checkout",
      all_products_locator=".shop-product__info:not(.shop-product__info--blocked)",
      wait_products_locator=".shop-products-list__container"
    )

  def _product_factory(self, element):
    return DeliveryClubProduct(self, element)

class DeliveryClubProduct(SimpleProduct):
  def __init__(self, shop, element):
    SimpleProduct.__init__(
      self, shop, element,
      ".shop-product__title",
      ".shop-product__price",
      ".shop-product__btn",
      wait_cart_strategy=WaitCartStrategy.element(".shop-product__quantity-controls")
    )

for name, store_name in config["delivery_club_shops"].items():
  globals()[name] = type(name, (DeliveryClub,), {
    "__init__": lambda self, driver, store_name=store_name: DeliveryClub.__init__(self, driver, store_name)
  })

class MVideo(Shop):
  def __init__(self, driver):
    Shop.__init__(
      self, driver,
      "https://www.mvideo.ru",
      "/product-list-page?sort=price_asc&q=%s",
      wait_products_locator=".product-cards-layout"
    )

  def get_all_products(self):
    name_elements = self.driver.find_elements(By.CSS_SELECTOR, ".product-title__text")
    price_elements = self.driver.find_elements(By.CSS_SELECTOR, ".price__main-value")
    cart_buttons = self.driver.find_elements(By.CSS_SELECTOR, ".product-card__checkout .card-button-block button")
    assert len(name_elements) == len(price_elements) and len(name_elements) == len(cart_buttons)
    return [MVideoProduct(self, None, name, price, cart_button)
      for name, price, cart_button in zip(name_elements, price_elements, cart_buttons)]

class MVideoProduct(EquippedProduct):
  def __init__(self, shop, name_element, price_element, cart_button_element):
    EquippedProduct.__init__(self, None, name_element, price_element, cart_button_element)

class Yandex(Shop):
  def __init__(self, driver):
    Shop.__init__(
      self, driver,
      "https://market.yandex.ru",
      "/search?pricefrom=1&text=%s",
      "/my/cart",
      all_products_locator="[data-zone-name=SearchResults] article[data-zone-name=snippet-card]",
      wait_products_locator="[data-zone-name=SearchResults]"
    )

  def _product_factory(self, element):
    return YandexProduct(self, element)

class YandexProduct(SimpleProduct):
  def __init__(self, shop, element):
    SimpleProduct.__init__(
      self, shop, element,
      "[data-zone-name=title]",
      "[data-zone-name=price]",
      "[data-zone-name=cartButton] button",
      wait_cart_strategy=WaitCartStrategy.element("[data-autotest-id=decrease]")
    )

class Ozon(Shop):
  def __init__(self, driver):
    Shop.__init__(
      self, driver,
      "https://www.ozon.ru",
      "/search/?sorting=price&text=%s",
      all_products_locator=".widget-search-result-container div.bi3.bi5",
      wait_products_locator=".widget-search-result-container"
    )

  def _product_factory(self, element):
    return OzonProduct(self, element)

class OzonProduct(SimpleProduct):
  def __init__(self, shop, element):
    SimpleProduct.__init__(
      self, shop, element,
      name_locator=".a7y.a8a2.a8a6.a8b2.bj5",
      price_locator=".ui-p6 .ui-p9.ui-q1",
      cart_button_locator=".a8z2.a8z5.b0d2 button",
      wait_cart_strategy=WaitCartStrategy.element(".a8z3")
    )

class Wildberries(Shop):
  def __init__(self, driver):
    Shop.__init__(
      self, driver,
      "https://www.wildberries.ru",
      "/catalog/0/search.aspx?sort=priceup&search=%s",
      "/lk/basket",
      all_products_locator="#catalog-content .product-card__wrapper",
      wait_products_locator="#catalog-content"
    )

  def _product_factory(self, element):
    return WildberriesProduct(self, element)

class WildberriesProduct(SimpleProduct):
  def __init__(self, shop, element):
    SimpleProduct.__init__(
      self, shop, element,
      ".product-card__brand-name",
      ".lower-price",
      ".product-card__order .j-add-to-basket"
    )

class DomKnigi(Shop):
  def __init__(self, driver):
    Shop.__init__(
      self, driver,
      "https://domknigi-online.ru",
      "/search?search_type=full&search=%s",
      all_products_locator="ul li.product-layout"
    )

  def _product_factory(self, element):
    return DomKnigiProduct(self, element)

class DomKnigiProduct(SimpleProduct):
  def __init__(self, shop, element):
    SimpleProduct.__init__(
      self, shop, element,
      name_locator=".product_title",
      price_locator=".product_count.pull-left",
      cart_button_locator=".product_caption_buy.pull-rigth a.btn",
      wait_cart_strategy=WaitCartStrategy.text("#myModalLabel", "Товар добавлен в корзину")
    )

# TODO check
class ChitaiGorod(Shop):
  def __init__(self, driver):
    Shop.__init__(
      self, driver,
      "https://www.chitai-gorod.ru",
      "/search/result/?sort=sale_price&q=%s",
      "/personal/basket/",
      all_products_locator=".container_cards-product .product-card__info",
      wait_products_locator=".container_cards-product"
    )

  def _product_factory(self, element):
    return ChitaiGorodProduct(self, element)

class ChitaiGorodProduct(SimpleProduct):
  def __init__(self, shop, element):
    SimpleProduct.__init__(
      self, shop, element,
      ".product-card__link",
      ".product-card__price",
      "button.product-card__button"
    )

class Labirint(Shop):
  def __init__(self, driver):
    Shop.__init__(
      self, driver,
      "https://www.labirint.ru",
      "/search/%s/?stype=0&order=price&way=forward",
      all_products_locator=".products-row .product"
    )

  def _product_factory(self, element):
    return LabirintProduct(self, element)

class LabirintProduct(SimpleProduct):
  def __init__(self, shop, element):
    SimpleProduct.__init__(
      self, shop, element,
      ".product-title",
      ".product-pricing .price-val",
      ".product-buy.buy-avaliable a",
      wait_cart_strategy=WaitCartStrategy.button_text("ОФОРМИТЬ")
    )

#TODO
class Alib(Shop):
  def __init__(self, driver):
    Shop.__init__(
      self, driver,
      "https://www.alib.ru",
      "/find3.php4?tfind=%s",
      None
    )

class MyShop(Shop):
  def __init__(self, driver):
    Shop.__init__(
      self, driver,
      "https://my-shop.ru",
      "/shop/search/a/sort/f/page/1.html?f14_6=%s",
      "/my/cart",
      all_products_locator=".article .items .item",
      wait_products_locator=".article .items"
    )

  def _product_factory(self, element):
    return MyShopProduct(self, element)

class MyShopProduct(SimpleProduct):
  def __init__(self, shop, element):
    SimpleProduct.__init__(
      self, shop, element,
      ".item__title__container",
      ".item__price",
      ".bottom .flex-grow button",
      wait_cart_strategy=WaitCartStrategy.button_text()
    )

class Book24(Shop):
  def __init__(self, driver):
    Shop.__init__(
      self, driver,
      "https://book24.ru",
      "/search/?by=asc&sort=price_discount&q=%s",
      "/personal/cart/",
      all_products_locator=".product-list .product-card__content"
    )

  def _product_factory(self, element):
    return Book24Product(self, element)

class Book24Product(SimpleProduct):
  def __init__(self, shop, element):
    SimpleProduct.__init__(
      self, shop, element,
      ".product-card__name",
      ".product-card-price__current",
      ".product-card__add-to-cart",
      wait_cart_strategy=WaitCartStrategy.element((By.PARTIAL_LINK_TEXT, "Оформить"))
    )

#TODO not adding to cart
class Bmm(Shop):
  def __init__(self, driver):
    Shop.__init__(
      self, driver,
      "https://bmm.ru",
      "/books/?q=%s",
      "/personal/cart/",
      all_products_locator=".catalog__main_items .news-book__item"
    )
    try:
      self.driver.find_element(By.CSS_SELECTOR, "#modal-promo-popup button.close").click()
    except NoSuchElementException:
      pass

  def _product_factory(self, element):
    return BmmProduct(self, element)

class BmmProduct(SimpleProduct):
  def __init__(self, shop, element):
    SimpleProduct.__init__(
      self, shop, element,
      ".news-book__item_descr",
      ".book-sum",
      ".book-actions .btn-cart",
      wait_cart_strategy=WaitCartStrategy.text("#modal-promo-popup .modal-content", "Товар успешно добавлен в корзину")
    )
