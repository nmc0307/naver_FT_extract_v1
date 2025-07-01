from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
import csv
import time
import traceback

# Chrome 옵션 설정 (헤드리스 모드)
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(options=chrome_options)

def extract_article_number(title):
    """상품명에서 아티클 번호 추출 (디버깅 출력 추가)"""
    try:
        pattern = r'\b[A-Z]{2,}\d{3,6}[_-]\d{2,3}\b'
        match = re.search(pattern, title)
        result = match.group(0) if match else "NOT_FOUND"
        print(f"[아티클 추출] 입력: '{title}' → 결과: '{result}'")
        return result
    except Exception as e:
        print(f"[아티클 추출 에러] {str(e)}")
        return "EXTRACTION_ERROR"

try:
    # 타겟 URL 로드 (시간 측정)
    start_time = time.time()
    url = "https://www.lotteon.com/csearch/search/search?render=search&platform=pc&q=%EB%82%98%EC%9D%B4%ED%82%A4&mallId=1"
    print(f"[진행] URL 로드 시작: {url}")
    driver.get(url)
    
    # 페이지 로딩 대기 (상세한 상태 출력)
    print("[진행] 상품 목록 로딩 대기 중...")
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "li.s-goods-grid-item"))
    )
    load_time = time.time() - start_time
    print(f"[성공] 페이지 로드 완료 ({load_time:.2f}초 소요)")
    
    # 상품 개수 확인
    products = driver.find_elements(By.CSS_SELECTOR, "li.s-goods-grid-item")
    print(f"[정보] 발견된 상품 수: {len(products)}개")
    
    # 결과 저장 리스트
    product_data = []
    
    # 상품 순회 처리
    for i in range(1, min(61, len(products)+1)):
        try:
            print(f"\n[진행] {i}번 상품 처리 시작 ------------------")
            
            # 상품 컨테이너 선택자
            item_selector = f"li.s-goods-grid-item:nth-child({i})"
            print(f"[선택자] 아이템: {item_selector}")
            
            # 요소 존재 확인
            item = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, item_selector))
            )
            
            # 제목 추출 (디버깅 출력)
            title_elem = item.find_element(By.CSS_SELECTOR, "div.s-goods-title")
            title = title_elem.text.strip()
            print(f"[제목] {title}")
            
            # 아티클 번호 추출
            article = extract_article_number(title)
            
            # 가격 추출 (오류 처리 강화)
            try:
                price_elem = item.find_element(By.CSS_SELECTOR, "span.s-goods-price__number")
                price_text = price_elem.text.strip()
                price_num = re.sub(r"[^\d]", "", price_text)
                print(f"[가격] 원본: '{price_text}' → 변환: '{price_num}'")
            except Exception as e:
                print(f"[가격 추출 에러] {str(e)}")
                price_num = "PRICE_ERROR"
            
            # 링크 추출 (상세한 오류 메시지)
            try:
                link_elem = item.find_element(By.CSS_SELECTOR, "a.s-goods-link")
                product_link = link_elem.get_attribute("href")
                print(f"[링크] {product_link}")
            except Exception as e:
                print(f"[링크 추출 에러] {str(e)}")
                product_link = "LINK_ERROR"
            
            # 결과 조합
            result_line = f"{article},{price_num},{product_link}"
            product_data.append(result_line)
            print(f"[결과] {result_line}")
            
        except Exception as e:
            error_msg = f"[{i}번 상품 처리 실패] {str(e)}"
            print(error_msg)
            print(traceback.format_exc())  # 스택 트레이스 출력
            continue
    
    # 파일 저장
    with open('output.txt', 'w', encoding='utf-8') as f:
        f.write("article,price,link\n")
        for line in product_data:
            f.write(f"{line}\n")
    
    print(f"\n[최종] 총 {len(product_data)}개 상품 저장 완료")

except Exception as e:
    print(f"\n[치명적 오류] 메인 실행 에러: {str(e)}")
    print(traceback.format_exc())  # 전체 오류 스택 출력
    
    # 현재 페이지 상태 저장 (디버깅용)
    with open('page_source.html', 'w', encoding='utf-8') as f:
        f.write(driver.page_source)
    print("[디버깅] 페이지 소스 저장: page_source.html")

finally:
    driver.quit()
    print("[종료] 드라이버 세션 종료")
