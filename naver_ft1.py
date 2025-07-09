from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

url = "https://shopping.naver.com/window/brand-fashion/search?q=DESCENTE&sort=POPULARITY"

options = Options()
options.add_argument("--headless")  # 테스트 시 주석 처리해도 좋음
options.add_argument("--disable-gpu")

driver = webdriver.Chrome(options=options)
driver.get(url)

try:
    # __next가 로딩될 때까지 기다림 (최대 10초)
    element = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "#__next > div"))
    )
    print("✅ 추출 성공! 태그명:", element.tag_name)
except Exception as e:
    print("❌ 추출 실패:", str(e))
finally:
    driver.quit()
