from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import re
import os
import random

# 무작위 User-Agent 목록
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.1 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
]

# Chrome 옵션 설정
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument(f"user-agent={random.choice(USER_AGENTS)}")

driver = webdriver.Chrome(options=chrome_options)

def extract_article_number(title):
    """타이틀에서 아티클 넘버 추출"""    
    pattern = r'\b[A-Z]{2,}\d{3,6}[_\-\s]\d{2,3}\b'
    match = re.search(pattern, title)
    return match.group(0) if match else "NOT_FOUND"

try:
    url = "https://www.lotteon.com/csearch/search/search?render=search&platform=pc&q=%EB%82%98%EC%9D%B4%ED%82%A4&mallId=1"
    driver.get(url)

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 
        "#content > div > section > div.srchResultArea > section.srchResultContentArea > div > div.s-goods-layout.s-goods-layout__grid > div.s-goods-grid.s-goods-grid--col-4 > ul"))
    )

    output_lines = []

    while True:
        print("현재 페이지에서 데이터 수집 중...")

        for i in range(1, 61):
            li_selector = f"#content > div > section > div.srchResultArea > section.srchResultContentArea > div > div.s-goods-layout.s-goods-layout__grid > div.s-goods-grid.s-goods-grid--col-4 > ul > li:nth-child({i})"
            try:
                li_element = driver.find_element(By.CSS_SELECTOR, li_selector)
                product_id = li_element.get_attribute("id").replace("product-head-", "")
                
                # 링크 추출
                try:
                    anchor = li_element.find_element(By.CSS_SELECTOR, "div.s-goods__info > a.s-goods__anchor")
                    href = anchor.get_attribute("href")
                except Exception as e:
                    print(f"링크 추출 실패: {str(e)}")
                    href = "LINK_NOT_FOUND"

                # 제목에서 아티클 추출
                try:
                    title_elem = li_element.find_element(By.CSS_SELECTOR, "div.s-goods__info div.s-goods-title")
                    title = title_elem.text.strip()
                    article = extract_article_number(title) if title else "NOT_FOUND"
                except Exception as e:
                    print(f"타이틀 추출 실패: {str(e)}")
                    article = "NOT_FOUND"
                
                # 가격 추출
                try:
                    price_elem = li_element.find_element(By.CSS_SELECTOR, "div.s-goods__column strong span.s-goods-price__number")
                    price = price_elem.text.strip()
                except Exception as e:
                    print(f"가격 추출 실패: {str(e)}")
                    price = "PRICE_NOT_FOUND"
                
                # 결과 저장
                output_line = f"{article} {price} {href}"
                output_lines.append(output_line)
                print(f"추출 완료: {output_line}")
                
            except (NoSuchElementException, TimeoutException):
                continue

        # 다음 페이지 버튼이 존재하는지 확인
        try:
            next_button = driver.find_element(By.CSS_SELECTOR, "a.srchPaginationNext")
            driver.execute_script("arguments[0].click();", next_button)
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 
                "#content > div > section > div.srchResultArea > section.srchResultContentArea > div > div.s-goods-layout.s-goods-layout__grid > div.s-goods-grid.s-goods-grid--col-4 > ul"))
            )
        except NoSuchElementException:
            print("마지막 페이지 도달.")
            break
        except Exception as e:
            print(f"페이지 이동 실패: {str(e)}")
            break

    # 파일 저장
    with open('output.txt', 'w', encoding='utf-8') as f:
        for line in output_lines:
            f.write(line + '\n')

    print("모든 페이지 수집 완료! output.txt에 저장됨.")

finally:
    driver.quit()
