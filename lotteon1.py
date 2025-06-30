from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import re

# Chrome 옵션 설정 (헤드리스 모드)
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(options=chrome_options)

def extract_article_number(title):
    """타이틀에서 아티클 넘버 추출"""
    # 정규식 패턴: 대문자/숫자 + 하이픈 + 숫자
    # pattern = r'[A-Z0-9]+-\d+'
    # 수정된 정규식 (더 포괄적인 패턴)
    pattern = r'[A-Z0-9]+[-_][A-Z0-9]+'
    match = re.search(pattern, title)
    return match.group(0) if match else "NOT_FOUND"


try:
    url = "https://www.lotteon.com/csearch/search/search?render=search&platform=pc&q=%EB%82%98%EC%9D%B4%ED%82%A4&mallId=1"
    driver.get(url)

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 
        "#content > div > section > div.srchResultArea > section.srchResultContentArea > div > div.s-goods-layout.s-goods-layout__grid > div.s-goods-grid.s-goods-grid--col-4 > ul"))
    )

    article_numbers = []

    for i in range(1, 61):
        info_selector = f"#content > div > section > div.srchResultArea > section.srchResultContentArea > div > div.s-goods-layout.s-goods-layout__grid > div.s-goods-grid.s-goods-grid--col-4 > ul > li:nth-child({i}) > div > div.s-goods__info"
        try:
            info_div = driver.find_element(By.CSS_SELECTOR, info_selector)
            title_elem = info_div.find_element(By.CSS_SELECTOR, "div.s-goods-title")
            title = title_elem.text.strip()
            
            if title:
                article = extract_article_number(title)
                article_numbers.append(article)
                print(f"추출된 아티클: {article}")  # 콘솔 출력
                
        except Exception as e:
            continue

    # 파일 저장
    with open('output.txt', 'w', encoding='utf-8') as f:
        for article in article_numbers:
            f.write(article + '\n')

    print("아티클 번호 추출 완료! output.txt 파일 저장됨")

finally:
    driver.quit()


