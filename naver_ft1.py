from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

url = "https://shopping.naver.com/window/brand-fashion/search?q=DESCENTE&sort=POPULARITY"

options = Options()
options.add_argument("--headless")
driver = webdriver.Chrome(options=options)
driver.get(url)
time.sleep(3)  # 페이지 로딩 대기

# 첫 번째 상품 정보 추출 시도
try:
    first_item = driver.find_element(By.XPATH, '//div[starts-with(@id, "basic_product_card_information_")]')
    print("✅ 추출 성공:", first_item.get_attribute("id"))
except Exception as e:
    print("❌ 추출 실패:", e)

driver.quit()
