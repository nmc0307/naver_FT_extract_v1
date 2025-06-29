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

driver = webdriver.Chrome(options=chrome_options)

try:
    url = "https://www.lotteon.com/csearch/search/search?render=search&platform=pc&q=%EB%82%98%EC%9D%B4%ED%82%A4&mallId=1"
    driver.get(url)

    # ul 요소가 로딩될 때까지 대기
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 
        "#content > div > section > div.srchResultArea > section.srchResultContentArea > div > div.s-goods-layout.s-goods-layout__grid > div.s-goods-grid.s-goods-grid--col-4 > ul"))
    )

    product_titles = []

    # li:nth-child(1) ~ li:nth-child(60) 반복
    for i in range(1, 61):
        info_selector = f"#content > div > section > div.srchResultArea > section.srchResultContentArea > div > div.s-goods-layout.s-goods-layout__grid > div.s-goods-grid.s-goods-grid--col-4 > ul > li:nth-child({i}) > div > div.s-goods__info"
        try:
            info_div = driver.find_element(By.CSS_SELECTOR, info_selector)
            # 해당 info_div 내부의 s-goods-title 추출
            title_elem = info_div.find_element(By.CSS_SELECTOR, "div.s-goods-title")
            title = title_elem.text.strip()
            if title:
                product_titles.append(title)
        except Exception as e:
            # 해당 li가 없거나 title이 없는 경우 무시
            continue

    # 결과 출력 및 파일 저장
    for title in product_titles:
        print(title)

    with open('output.txt', 'w', encoding='utf-8') as f:
        for title in product_titles:
            f.write(title + '\n')

finally:
    driver.quit()
