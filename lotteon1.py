from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
import csv

# Chrome 옵션 설정 (헤드리스 모드)
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(options=chrome_options)

def extract_article_number(title):
    """상품명에서 아티클 번호 추출"""
    pattern = r'\b[A-Z]{2,}\d{3,6}[_-]\d{2,3}\b'
    match = re.search(pattern, title)
    return match.group(0) if match else "NOT_FOUND"

try:
    # [##1] 타겟 URL 로드
    url = "https://www.lotteon.com/csearch/search/search?render=search&platform=pc&q=%EB%82%98%EC%9D%B4%ED%82%A4&mallId=1"
    driver.get(url)
    
    # 상품 목록 로딩 대기
    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "li.s-goods-grid-item"))
    )
    
    # 결과 저장 리스트
    product_data = []
    
    # [##3]~[##4] 1~60번 상품 순회
    for i in range(1, 61):
        try:
            # [##3] 상품 컨테이너 선택자
            item_selector = f"li.s-goods-grid-item:nth-child({i})"
            item = driver.find_element(By.CSS_SELECTOR, item_selector)
            
            # [##5] 아티클 번호 추출
            title_elem = item.find_element(By.CSS_SELECTOR, "div.s-goods-title")
            title = title_elem.text.strip()
            article = extract_article_number(title)
            
            # [##6] 가격 추출 및 숫자 변환
            price_elem = item.find_element(By.CSS_SELECTOR, "span.s-goods-price__number")
            price_text = price_elem.text.strip()
            price_num = re.sub(r"[^\d]", "", price_text)  # 숫자만 추출
            
            # [##7] 상품 링크 추출
            link_elem = item.find_element(By.CSS_SELECTOR, "a.s-goods-link")
            product_link = link_elem.get_attribute("href")
            
            # 결과 조합
            result_line = f"{article},{price_num},{product_link}"
            product_data.append(result_line)
            print(result_line)  # 콘솔 출력
            
        except Exception as e:
            print(f"[에러] 상품 {i}번 처리 실패: {str(e)}")
    
    # 파일 저장 (CSV 형식)
    with open('output.txt', 'w', encoding='utf-8') as f:
        f.write("article,price,link\n")  # 헤더 추가
        for line in product_data:
            f.write(f"{line}\n")
    
    print(f"총 {len(product_data)}개 상품 저장 완료")

except Exception as e:
    print(f"메인 실행 에러: {str(e)}")

finally:
    driver.quit()
