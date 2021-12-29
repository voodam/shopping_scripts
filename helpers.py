from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from contextlib import contextmanager
import os, fileinput, time, re

@contextmanager
def selenium_driver(driver_path):
  try:
    service = Service(driver_path)
    service.start()
    driver = webdriver.Remote(service.service_url)
    yield driver
  finally:
    driver.quit()

def file_to_list(file_path):
  with open(file_path, "r") as file:
    lines = [line.rstrip() for line in file]
  return lines

def parse_float(string):
  return float(re.search("[\d\s]+([.,]\d+)*", string).group(0) \
                 .replace(" ", "") \
                 .replace(",", "."))

def flatmap(func, *iterable):
  return itertools.chain.from_iterable(map(func, *iterable))

def throw(error):
  raise error
