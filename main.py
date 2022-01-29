DRIVER_PATH = './chromedriver'
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait

from datetime import datetime
nw = datetime.now()
# driver = webdriver.Chrome(ChromeDriverManager().install())
driver = webdriver.Chrome()

WebDriverWait(driver, timeout=5)

driver.get("https://www.google.com")
print(driver.title) # => "Google"