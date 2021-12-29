from time import sleep
from config import config
from urllib.parse import urlparse

class Shop:
	def __init__(self, driver, host, search_route, cart_route="/cart",
							 loading_time=0):
		self.driver = driver
		self.host = host
		self.search_url = host + search_route
		if cart_route:
			self.cart_url = host + cart_route
		self.loading_time = loading_time
		self._init_cookies()

	def _init_cookies(self):
		domain = urlparse(self.host).netloc
		cookies = config["cookies"].get(domain)
		if not cookies:
			return

		self.driver.get(self.host)
		for cookie in cookies:
			self.driver.add_cookie(cookie)

	def search(self, good):
		self.driver.get(self.search_url % good);
		sleep(self.loading_time)

	def go_to_cart(self):
		self.driver.get(self.cart_url)

	def count_goods(self):
		raise NotImplementedError()

	def add_first_good(self):
		raise NotImplementedError()

	def _count_goods(self, selector):
		elements = self.driver.find_elements_by_css_selector(selector)
		return len(elements)

	def _add_first_good(self, selector):
		button = self.driver.find_element_by_css_selector(selector)
		button.click()


class DeliveryClub(Shop):
	def __init__(self, driver, store_name):
		Shop.__init__(
			self, driver,
			"https://www.delivery-club.ru",
			f"/store/{store_name}?grocerySearch=%s",
			"/checkout",
			loading_time=2
		)

	def count_goods(self):
		selector = ".shop-product__info:not(.shop-product__info--blocked)"
		return self._count_goods(selector)

	def add_first_good(self):
		selector = ".shop-product__info:not(.shop-product__info--blocked) button"
		self._add_first_good(selector)

for name, store_name in config["delivery_club_shops"].items():
	globals()[name] = type(name, (DeliveryClub,), {
		"__init__": lambda self, driver, store_name=store_name: DeliveryClub.__init__(self, driver, store_name)
	})

class MVideo(Shop):
	def __init__(self, driver, store_name):
		Shop.__init__(
			self, driver,
			"https://www.mvideo.ru",
			"/product-list-page?q=%s"
		)

class Eldorado(Shop):
	def __init__(self, driver, store_name):
		Shop.__init__(
			self, driver,
			"https://www.eldorado.ru/",
			"/search/catalog.php?q=%s",
			"/personal/cart.php"
		)

class YandexMarket(Shop):
	def __init__(self, driver, store_name):
		Shop.__init__(
			self, driver,
			"https://market.yandex.ru",
			"/search?text=%s",
			"/my/cart"
		)

class Ozon(Shop):
	def __init__(self, driver, store_name):
		Shop.__init__(
			self, driver,
			"https://www.ozon.ru",
			"/search/?text=%s"
		)

class Wildberries(Shop):
	def __init__(self, driver, store_name):
		Shop.__init__(
			self, driver,
			"https://www.wildberries.ru",
			"/catalog/0/search.aspx?search=%s",
			"/lk/basket"
		)

class Partsdirect(Shop):
	def __init__(self, driver, store_name):
		Shop.__init__(
			self, driver,
			"https://ekb.partsdirect.ru",
			"/search_results?q=%s",
			"/basket"
		)

class Intelekt(Shop):
	def __init__(self, driver, store_name):
		Shop.__init__(
			self, driver,
			"https://www.intel-ekt.ru/",
			"catalog/search/?keyword=%s",
			"/order/"
		)

class Nix(Shop):
	def __init__(self, driver, store_name):
		Shop.__init__(
			self, driver,
			"https://e-burg.nix.ru",
			"/price/search_panel_ajax.html#t:goods;k:%s",
			"/scripts/order_cb.html"
		)

class Dns(Shop):
	def __init__(self, driver, store_name):
		Shop.__init__(
			self, driver,
			"https://www.dns-shop.ru",
			"/search/?q=%s",
			"/order/begin/"
		)

class DomKnigi(Shop):
	def __init__(self, driver, store_name):
		Shop.__init__(
			self, driver,
			"https://domknigi-online.ru",
			"/search?search_type=full&search=%s"
		)

class ChitaiGorod(Shop):
	def __init__(self, driver, store_name):
		Shop.__init__(
			self, driver,
			"https://www.chitai-gorod.ru",
			"/search/result/?q=%s",
			"/personal/basket/"
		)

class Labirint(Shop):
	def __init__(self, driver, store_name):
		Shop.__init__(
			self, driver,
			"https://www.labirint.ru",
			"/search/%s",
		)

class Alib(Shop):
	def __init__(self, driver, store_name):
		Shop.__init__(
			self, driver,
			"https://www.alib.ru",
			"/find3.php4?tfind=%s",
			None
		)

class MyShop(Shop):
	def __init__(self, driver, store_name):
		Shop.__init__(
			self, driver,
			"https://my-shop.ru",
			"/shop/search/a/sort/z/page/1.html?f14_6=%s",
			"/my/cart"
		)

class Book24(Shop):
	def __init__(self, driver, store_name):
		Shop.__init__(
			self, driver,
			"https://book24.ru",
			"/search/?q=%s",
			"/personal/cart/"
		)

class Bmm(Shop):
	def __init__(self, driver, store_name):
		Shop.__init__(
			self, driver,
			"https://bmm.ru",
			"/books/?q=%s",
			"/personal/cart/"
		)
