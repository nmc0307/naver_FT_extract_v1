from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

url = "https://shopping.naver.com/window/brand-fashion/search?q=DESCENTE&sort=POPULARITY"

options = Options()
options.add_argument("--headless")
driver = webdriver.Chrome(options=options)
driver.get(url)

try:
    # 최대 10초간 요소 로딩 기다리기
    element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//div[starts-with(@id, "basic_product_card_information_")]'))
    )
    print("✅ 요소 로딩 성공:", element.get_attribute("id"))
except Exception as e:
    print("❌ 요소 로딩 실패:", e)
finally:
    driver.quit()
