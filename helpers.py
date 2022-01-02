from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from contextlib import contextmanager
import os, fileinput, time, re, signal, traceback

@contextmanager
def selenium_driver(driver_path, debug=True):
  try:
    service = Service(driver_path)
    service.start()
    driver = webdriver.Remote(service.service_url)
    yield driver
  except Exception as ex:
    if debug:
      print(traceback.format_exc())
      input()
    else:
      raise ex
  finally:
    driver.quit()

def loc(locator):
  if isinstance(locator, str):
    locator = (By.CSS_SELECTOR, locator)

  assert isinstance(locator, tuple)
  return locator

def wait_until(condition, timeout=10, poll_frequency=0.5):
  signal.signal(signal.SIGALRM, lambda _, __: throw(TimeoutException("Wait timeout exceed")))
  signal.alarm(timeout)

  while not condition():
    time.sleep(poll_frequency)

  signal.alarm(0)

def file_to_list(file_path):
  with open(file_path, "r") as file:
    lines = [line.rstrip() for line in file]
  return lines

def read_ignore_comments(file_path):
  lines = file_to_list(file_path)
  return [line for line in lines if line and not line.startswith("#")]

def parse_float(string):
  string = string.replace(u"\u2009", " ") \
                 .replace(" ", "") \
                 .replace(",", ".")
  return float(re.search("[\d]+(.\d+)*", string).group(0))

def flatmap(func, *iterable):
  return itertools.chain.from_iterable(map(func, *iterable))

def throw(error):
  raise error
