from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

# 프록시 정보
PROXY = "115.144.113.130:16315"

# Chrome 옵션 설정
options = Options()
options.add_argument(f'--proxy-server=http://{PROXY}')
options.add_argument('--headless')  # 시각 디버깅 시에는 이 줄을 주석 처리
options.add_argument('--disable-gpu')
options.add_argument('--no-sandbox')

# Chrome WebDriver 실행
driver = webdriver.Chrome(options=options)

# 테스트할 URL (네이버 쇼핑)
url = "https://shopping.naver.com/window/brand-fashion/search?q=DESCENTE&sort=POPULARITY"
driver.get(url)

# 충분히 로딩 대기
time.sleep(3)

# 결과 출력
print("✅ 접근 완료. 페이지 타이틀:", driver.title)

driver.quit()
