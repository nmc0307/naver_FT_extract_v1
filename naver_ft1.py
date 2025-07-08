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



# 아티클 넘버 추출 함수
def extract_article_number(title):
    patterns = [
        r'\b([A-Z]{2,}\d{3,6})[ _\-]?(\d{2,4})\b',
        r'\b([A-Z]{2,}\d{4,})\b',
    ]
    for pattern in patterns:
        match = re.search(pattern, title)
        if match:
            if len(match.groups()) == 2:
                return f"{match.group(1)}-{match.group(2)}"
            return match.group(1)
    return ""

# 가격 정수 변환
def clean_price(price_str):
    digits = re.sub(r"[^\d]", "", price_str)
    return int(digits) if digits else 0

# 대상 URL
url = "https://shopping.naver.com/window/brand-fashion/search?q=DESCENTE&sort=POPULARITY"  #🟥
driver.get(url)
time.sleep(2)

# 중복 체크용 ID
seen_ids = set()
results = []

# 스크롤 반복 및 데이터 수집
while True:
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)

    items = driver.find_elements(By.CSS_SELECTOR, "ul > li[id^='basic_product_card_information_']")    

    new_count = 0
    for item in items:
        print(item) #########################################🟥
        item_id = item.get_attribute("id")
        if not item_id or item_id in seen_ids:
            continue
        seen_ids.add(item_id)

        try:
            name = item.find_element(By.CSS_SELECTOR, "strong[class*='productName_product_name__']").text.strip()
            price_str = item.find_element(By.CSS_SELECTOR, "span[class*='productPrice_price__']").text.strip()
            price = clean_price(price_str)
            link = item.find_element(By.TAG_NAME, "a").get_attribute("href")
            article = extract_article_number(name)
            results.append([item_id, name, price, article, link])
            new_count += 1
        except Exception as e:
            continue

    print(f"🟢 새로 수집한 상품 수: {new_count}")

    if new_count == 0:
        print("✅ 더 이상 새로운 항목이 없습니다. 종료합니다.")
        break

driver.quit()

# CSV 저장
with open("output.csv", "w", newline="", encoding="utf-8-sig") as f:
    writer = csv.writer(f)
    writer.writerow(["상품 ID", "상품명", "가격(숫자)", "아티클 넘버", "링크"])
    writer.writerows(results)

print(f"📦 총 {len(results)}개의 상품이 저장되었습니다.")
