from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

url = "https://shopping.naver.com/window/brand-fashion/search?q=DESCENTE&sort=POPULARITY"

# Chrome headless 모드로 설정
options = Options()
options.add_argument("--headless")
options.add_argument("--disable-gpu")

driver = webdriver.Chrome(options=options)
driver.get(url)

try:
    # CSS Selector 방식 사용
    element = driver.find_element(By.CSS_SELECTOR, "#__next > div")
    print("✅ 추출 성공! 태그명:", element.tag_name)
except Exception as e:
    print("❌ 추출 실패:", str(e))
finally:
    driver.quit()
