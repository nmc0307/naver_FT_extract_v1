from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os

# Chrome 옵션 설정 (헤드리스 모드)
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(options=chrome_options)

try:
    url = "https://www.lotteon.com/csearch/search/search?render=search&platform=pc&q=%EB%82%98%EC%9D%B4%ED%82%A4&mallId=1"
    driver.get(url)
    time.sleep(3)

    # 수정된 selector 적용
    title_elements = driver.find_elements(
        By.CSS_SELECTOR, 'div.s-goods__info div[id^="product-head-"] > div.s-goods-title'
    )

    product_titles = [elem.text for elem in title_elements]
    for title in product_titles:
        print(title)

finally:
    driver.quit()
