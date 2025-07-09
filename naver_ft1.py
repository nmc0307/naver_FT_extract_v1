from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

url = "https://shopping.naver.com/window/brand-fashion/search?q=DESCENTE&sort=POPULARITY"

# 셀레니움 드라이버 세팅
options = Options()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
driver = webdriver.Chrome(options=options)
driver.get(url)

# 페이지 로딩 후 스크롤 반복
for i in range(2):  # 총 10번 스크롤
    driver.execute_script("window.scrollBy(0, 1500);")
    time.sleep(1.5)

# 상품 정보 로딩 기다리기
try:
    element = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, '//div[starts-with(@id, "basic_product_card_information_")]'))
    )
    print("✅ 로딩된 상품 ID:", element.get_attribute("id"))
except Exception as e:
    print("❌ 여전히 요소 없음:", str(e))
finally:
    driver.quit()
