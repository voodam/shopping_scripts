from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from contextlib import contextmanager
import os, fileinput, time

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
    lines = list(map(lambda line: line.rstrip(), file))
  return lines
