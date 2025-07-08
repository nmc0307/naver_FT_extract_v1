from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import re
import os
import random
import csv
import time

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


URL = "https://shopping.naver.com/window/brand-fashion/search?q=DESCENTE&sort=POPULARITY"

# 스크롤 다운
def scroll_down(driver):
    driver.execute_script("window.scrollBy(0, 1000);")
    time.sleep(1.5)

# 상품 아이디 추출
def extract_products(driver, seen_ids):
    products = []
    product_elements = driver.find_elements(By.XPATH, '//*[@id="content"]/div/div[2]/div[3]/div[2]/div/div/ul/li')

    for li in product_elements:
        try:
            info_div = li.find_element(By.XPATH, './/div[starts-with(@id, "basic_product_card_information_")]')
            prod_id = info_div.get_attribute("id").replace("basic_product_card_information_", "")

            if prod_id not in seen_ids:
                seen_ids.add(prod_id)
                products.append(prod_id)
        except Exception:
            continue

    return products

# 결과 저장
def save_to_file(prod_array, filename="output.txt"):
    with open(filename, "w", encoding="utf-8") as f:
        for pid in prod_array:
            f.write(f"{pid}\n")

# 메인 실행
def main():
    driver = init_driver()
    driver.get(URL)
    time.sleep(3)

    prod_array = []
    seen_ids = set()
    prev_height = driver.execute_script("return document.body.scrollHeight")
    unchanged_scroll_count = 0

    while True:
        new_products = extract_products(driver, seen_ids)
        if new_products:
            prod_array.extend(new_products)
            save_to_file(prod_array)  # 중간 저장

        scroll_down(driver)
        curr_height = driver.execute_script("return document.body.scrollHeight")

        if curr_height == prev_height:
            unchanged_scroll_count += 1
        else:
            unchanged_scroll_count = 0

        if unchanged_scroll_count >= 5:
            print("스크롤 종료 감지됨.")
            break

        prev_height = curr_height

    save_to_file(prod_array)
    driver.quit()
    print(f"총 {len(prod_array)}개 상품 저장 완료.")

if __name__ == "__main__":
    main()
