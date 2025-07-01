from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import re

# Chrome 옵션 설정 (헤드리스 모드)
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(options=chrome_options)

def extract_article_number(title):
    pattern = r'\b[A-Z]{2,}\d{3,6}[_-]\d{2,3}\b'
    match = re.search(pattern, title)
    return match.group(0) if match else "NOT_FOUND"

try:
    url = "https://www.lotteon.com/csearch/search/search?render=search&platform=pc&q=%EB%82%98%EC%9D%B4%ED%82%A4&mallId=1"
    driver.get(url)
    print("페이지 로드 완료")

    # 더 안정적인 대기 조건 (상품 목록 표시 확인)
    WebDriverWait(driver, 15).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "div.s-goods-title"))
    )
    print("상품 목록 로드 완료")

    product_data = []

    for i in range(1, 61):
        try:
            # 상품 정보 컨테이너 선택자
            item_selector = f"li.s-goods-grid-item:nth-child({i})"
            item = driver.find_element(By.CSS_SELECTOR, item_selector)
            
            # 타이틀 추출
            title_elem = item.find_element(By.CSS_SELECTOR, "div.s-goods-title")
            title = title_elem.text.strip()
            print(f"[제목] {title}")  # 제목 출력
            
            # 가격 추출 (단순화된 선택자)
            price_elem = item.find_element(
                By.CSS_SELECTOR, 
                "span.s-goods-price__number"
            )
            price = price_elem.text.strip()
            print(f"[가격] {price}")  # 가격 출력
            
            if title:
                article = extract_article_number(title)
                product_data.append((article, price))
                print(f"추출된 아티클: {article} | 가격: {price}")
                
        except Exception as e:
            print(f"[에러] li {i} 처리 실패: {str(e)}")
            continue

    # 파일 저장
    with open('output.txt', 'w', encoding='utf-8') as f:
        for article, price in product_data:
            f.write(f"{article} {price}\n")

    print(f"총 {len(product_data)}개 항목 저장 완료")

finally:
    driver.quit()
    print("드라이버 종료")
