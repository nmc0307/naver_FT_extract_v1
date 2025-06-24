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

def process_product(driver, product_code):
    """개별 품번 처리 함수"""
    url = f"https://www.lotteon.com/csearch/search/search?render=search&platform=pc&q={product_code}&mallId=1"
    print(f"[INFO] 요청 URL: {url}")
    driver.get(url)
    
    # 페이지 로딩 대기 (상품 리스트 로딩 확인)
    print(f"[INFO] 상품 리스트 로딩 대기 중...")
    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".s-goods"))
    )
    time.sleep(2)  # 추가 로딩 시간 확보
    
    products = driver.find_elements(By.CSS_SELECTOR, ".s-goods")
    print(f"[INFO] 상품 개수: {len(products)}")
    min_price = float('inf')
    min_link = ""
    
    for idx, product in enumerate(products):
        try:
            # 가격 추출
            price_element = product.find_element(
                By.CSS_SELECTOR, ".s-goods-price__final .s-goods-price__number"
            )
            price_text = price_element.text.replace(",", "").replace("원", "")
            price = int(price_text)
            
            # 링크 추출
            link_element = product.find_element(
                By.CSS_SELECTOR, ".s-goods__anchor"
            )
            link = link_element.get_attribute("href")
            
            print(f"[DEBUG] 상품 {idx+1}: 가격={price}, 링크={link}")
            
            # 최저가 갱신
            if price < min_price:
                min_price = price
                min_link = link
                print(f"[INFO] 최저가 갱신: {min_price}원, 링크: {min_link}")
                
        except Exception as e:
            print(f"[WARN] 상품 {idx+1} 처리 중 오류 발생: {e}")
            continue
    
    print(f"[RESULT] 품번: {product_code}, 최저가: {min_price}, 링크: {min_link}")
    return [product_code, min_price, min_link]

def main():
    print("[START] Selenium 크롤러 시작")
    # 드라이버 초기화
    driver = webdriver.Chrome(options=chrome_options)
    
    # 입출력 파일 경로
    input_file = "inputList.txt"
    output_file = "output.txt"
    
    # 출력 파일 초기화
    open(output_file, "w").close()
    print(f"[INFO] 결과 파일 초기화: {output_file}")
    
    # 품번 처리
    with open(input_file, "r") as f_in, open(output_file, "a") as f_out:
        for line_num, line in enumerate(f_in, 1):
            product_code = line.strip()
            if not product_code:
                print(f"[INFO] {line_num}번째 줄이 비어있어 건너뜀")
                continue
            
            print(f"[PROCESS] {line_num}번째 품번 처리: {product_code}")
            result = process_product(driver, product_code)
            f_out.write(f"{result[0]},{result[1]},{result[2]}\n")
            f_out.flush()  # 즉시 저장 보장
            print(f"[INFO] 결과 저장 완료: {result}")
    
    driver.quit()
    print("[END] Selenium 크롤러 종료")

if __name__ == "__main__":
    main()
