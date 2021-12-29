from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from contextlib import contextmanager
import os, fileinput, time

@contextmanager
def selenium_driver(driver_path, wait_quit=0):
  try:
    service = Service(driver_path)
    service.start()
    driver = webdriver.Remote(service.service_url)
    yield driver
  finally:
    time.sleep(wait_quit)
    driver.quit()

def read_stdin():
  return map(lambda line: line.rstrip(), fileinput.input(files=["-"]))

