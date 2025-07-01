from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import re
import os

# Chrome 옵션 설정 (헤드리스 모드)
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(options=chrome_options)

def extract_article_number(title):
    """타이틀에서 아티클 넘버 추출"""
    pattern = r'\b[A-Z]{2,}\d{3,6}[_-]\d{2,3}\b'
    match = re.search(pattern, title)
    return match.group(0) if match else "NOT_FOUND"

try:
    url = "https://www.lotteon.com/csearch/search/search?render=search&platform=pc&q=%EB%82%98%EC%9D%B4%ED%82%A4&mallId=1"
    driver.get(url)

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 
        "#content > div > section > div.srchResultArea > section.srchResultContentArea > div > div.s-goods-layout.s-goods-layout__grid > div.s-goods-grid.s-goods-grid--col-4 > ul"))
    )

    output_lines = []  # 아티클과 가격을 함께 저장할 리스트

    for i in range(1, 61):
        li_selector = f"#content > div > section > div.srchResultArea > section.srchResultContentArea > div > div.s-goods-layout.s-goods-layout__grid > div.s-goods-grid.s-goods-grid--col-4 > ul > li:nth-child({i})"
        try:
            li_element = driver.find_element(By.CSS_SELECTOR, li_selector)
            product_id = li_element.get_attribute("id").replace("product-head-", "")
            
            # 제목에서 아티클 추출
            title_elem = li_element.find_element(By.CSS_SELECTOR, "div.s-goods__info div.s-goods-title")
            title = title_elem.text.strip()
            article = extract_article_number(title) if title else "NOT_FOUND"
            
            # 가격 추출
            try:
                price_selector = f"#{li_element.get_attribute('id')} > div > div.s-goods__column > div > strong > span.s-goods-price__number"
                price_elem = li_element.find_element(By.CSS_SELECTOR, price_selector)
                price = price_elem.text.strip()
            except Exception as e:
                print(f"가격 추출 실패: {str(e)}")
                price = "PRICE_NOT_FOUND"
            
            # 아티클과 가격을 함께 저장
            output_line = f"{article} {price}"
            output_lines.append(output_line)
            print(f"추출 완료: {output_line}")  # 콘솔 출력
            
        except (NoSuchElementException, TimeoutException) as e:
            print(f"제품 {i}에서 오류 발생: {str(e)}")
            continue

    # 파일 저장
    with open('output.txt', 'w', encoding='utf-8') as f:
        for line in output_lines:
            f.write(line + '\n')

    print("아티클 번호와 가격 추출 완료! output.txt 파일 저장됨")

finally:
    driver.quit()
