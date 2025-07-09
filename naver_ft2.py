from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

URL = "https://shopping.naver.com/window/brand-fashion/search?q=DESCENTE&sort=POPULARITY"

def init_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(options=options)
    return driver

def get_product_titles(driver):
    try:
        wait = WebDriverWait(driver, 10)
        ul_element = wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, "#content > div > div:nth-child(2) > div.fashionSearchWrapper_wrap_search_product_list__OsRij > div.fashionSearchProductListWrapper_fashion_search_product_list_wrapper__jpkpm > div > div > ul")
        ))
        li_elements = ul_element.find_elements(By.TAG_NAME, "li")

        titles = []
        for li in li_elements:
            try:
                title_elem = li.find_element(By.CSS_SELECTOR, 'strong.productName_product_name__HTpXG')
                title = title_elem.text.strip()
                titles.append(title)
            except:
                continue
        return titles
    except Exception as e:
        print("로딩 실패:", e)
        return []

def scroll_down(driver):
    driver.execute_script("window.scrollBy(0, 1000);")
    time.sleep(1.0)

def main():
    driver = init_driver()
    driver.get(URL)
    time.sleep(3)

    prev_titles = []
    unchanged_scrolls = 0

    while True:
        curr_titles = get_product_titles(driver)
        print(f"li 요소 개수: {len(curr_titles)}")  # ✅ 출력 위치

        if curr_titles == prev_titles:
            unchanged_scrolls += 1
        else:
            unchanged_scrolls = 0

        if unchanged_scrolls >= 5:
            print("스크롤 종료 감지됨.")
            break

        prev_titles = curr_titles
        scroll_down(driver)

    driver.quit()

if __name__ == "__main__":
    main()
