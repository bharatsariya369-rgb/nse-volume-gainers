from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

options = Options()
options.add_argument("--start-maximized")

driver = webdriver.Chrome(options=options)

driver.get("https://www.nseindia.com/market-data/volume-gainers-spurts")

time.sleep(10)

print(driver.page_source[:1000])

driver.quit()
