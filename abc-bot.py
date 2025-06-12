"""
1. Python 3.12.8 프로그램을 작성한다.
2. selenium 4.27.1와 webdriver-manager 4.0.2이 설치되어있어. 
3. "https://abcmart.a-rt.com/product/new?prdtNo=1010109424&page=1" url을 오픈한다.
4. chrome DevTools Protocol을 사용해서 네트워크 로그를 캡쳐한다.
5. 여러개의 XHR 타입의 네트워크 로그들이 캡쳐될 것인데
5.1. 그중에서 XHR 타입이고 request url이 "abcmart.a-rt.com/product/info?prdtNo" 문구를 포함하는 네트워크 로그를 찾고
5.2. 그중에서 아래 6번을 찾으면 prdtNo, optnName, orderDailydlvyPsbltQty를 print한다.
6. "productOption": [
        {
            "pageNum": 1,
            "rowsPerPage": 10,
            "prdtNo": "1010109424",
            "prdtOptnNo": "250",
            "optnName": "250",
            "orderDailydlvyPsbltQty": 243,
            "totalOrderQty": 0,
            "orderPsbltQty": 243,
            "vndrPrdtNoText": "0109424001250",
            "sellStatCode": "10001",
            "sortSeq": 1,
            "useYn": "Y",
            "optionPrice": {
                "pageNum": 1,
                "rowsPerPage": 10,
                "prdtNo": "1010109424",
                "prdtOptnNo": "250",
                "sellPriceHistSeq": 1,
                "optnAddAmt": 0
            },
            "orderDailydlvyPsbltQty": 2
        },
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import json
import random
import time
import os
import datetime

from telegram import Bot
import asyncio

from random_user_agent.params import SoftwareName, HardwareType, OperatingSystem
from random_user_agent.user_agent import UserAgent

TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

# Define bot
bot = Bot(token=TELEGRAM_BOT_TOKEN)

async def send_message(text, chat_id):
    async with bot:
        await bot.send_message(text=text, chat_id=chat_id)

async def run_bot(botmsg, chat_id):
    text = ''.join(botmsg)
    await send_message(text, chat_id)

def random_delay(min_seconds=5, max_seconds=10):
    delay = random.uniform(min_seconds, max_seconds)
    time.sleep(delay)
    return delay

# Chrome DevTools Protocol을 사용해 네트워크 로그 캡처 및 분석
def capture_and_analyze_network_logs(analyze_func):
    # ChromeOptions 설정
    options = Options()
    options.add_argument("--headless=new")
    options.set_capability("goog:loggingPrefs", {"performance": "ALL"})

    software_names = [SoftwareName.CHROME.value]
    operating_systems = [OperatingSystem.WINDOWS.value]
    user_agent_rotator = UserAgent(software_names=software_names, operating_systems=operating_systems, limit=100)
    user_agent = user_agent_rotator.get_random_user_agent()    

    # 랜덤 User-Agent 추가
    options.add_argument(f"user-agent={user_agent}")

    # WebDriver 설정 및 실행
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()), options=options
    )

    try:
        # URL 열기
        driver.get(prod_url)

        # 네트워크 로그 캡처
        logs = driver.get_log("performance")

        # 네트워크 로그 분석
        for log_entry in logs:
            message = json.loads(log_entry["message"])  # 로그 메시지를 JSON으로 파싱
            message_data = message.get("message", {})
            if message_data.get("method") == "Network.responseReceived":
                request_url = message_data.get("params", {}).get("response", {}).get("url", "")
                #if "abcmart.a-rt.com/product/info?prdtNo" in request_url:
                if "/product/info?prdtNo" in request_url:    
                    analyze_func(driver, message_data)
    finally:
        # WebDriver 종료
        driver.quit()

# 예시 분석 함수 1
def analyze_request_data1(driver, message_data):
    try:
        # 요청의 JSON 응답을 가져옴
        response_body = driver.execute_cdp_cmd("Network.getResponseBody", {
            "requestId": message_data["params"]["requestId"]
        })
        response_data = json.loads(response_body["body"])
            
        # 맨 위에 출력할 항목들
        engPrdtName = response_data.get("engPrdtName", "N/A")
        styleInfo = response_data.get("styleInfo", "N/A")
        prdtColorInfo = response_data.get("prdtColorInfo", "N/A")
        displayProductPrice = response_data.get("displayProductPrice", "N/A")
        displayDiscountRate = response_data.get("displayDiscountRate", "N/A")

        # 맨 윗줄에 출력
        botmsg1 = "103000 by ??/?? [스탁엑스1]\n" ### 🟥 [2]
        botmsg2 = f"{displayProductPrice},{displayDiscountRate}%,{styleInfo}-{prdtColorInfo}\n{engPrdtName}\n"  ###################

        # productOption 필드에서 원하는 데이터 필터링
        product_options = response_data.get("productOption", [])
        for option in product_options:
            prdtNo = option.get("prdtNo")
            optnName = option.get("optnName")
            orderDailydlvyPsbltQty = option.get("orderDailydlvyPsbltQty")
            if prdtNo and optnName:
                if optnName in ["230"]:    ### 🟥 [3.1]
                    botmsg3 = (f"{prdtNo},{optnName}: {orderDailydlvyPsbltQty}\n")
                elif optnName in ["240"]:  ### 🟥
                    botmsg4 = (f"{prdtNo},{optnName}: {orderDailydlvyPsbltQty}\n")
                else:
                    print(f"prdtNo: {prdtNo}, optnName: {optnName}, orderDailydlvyPsbltQty: {orderDailydlvyPsbltQty}")
        botmsg = ''.join([botmsg1,botmsg2,botmsg3,botmsg4]) ### 🟥 [3.2]
        asyncio.run(run_bot(botmsg, CHAT_ID))
    except Exception as e:
        print(f"Error analyzing request: {e}")

# 예시 분석 함수 2
def analyze_request_data2(driver, message_data):
    try:
        # 요청의 JSON 응답을 가져옴
        response_body = driver.execute_cdp_cmd("Network.getResponseBody", {
            "requestId": message_data["params"]["requestId"]
        })
        response_data = json.loads(response_body["body"])
            
        # 맨 위에 출력할 항목들
        engPrdtName = response_data.get("engPrdtName", "N/A")
        styleInfo = response_data.get("styleInfo", "N/A")
        prdtColorInfo = response_data.get("prdtColorInfo", "N/A")
        displayProductPrice = response_data.get("displayProductPrice", "N/A")
        displayDiscountRate = response_data.get("displayDiscountRate", "N/A")

        # 맨 윗줄에 출력
        botmsg1 = "88000 by ??/?? [스탁엑스2]\n" ### 🟥 [2]
        botmsg2 = f"{displayProductPrice},{displayDiscountRate}%,{styleInfo}-{prdtColorInfo}\n{engPrdtName}\n"  ###################

        # productOption 필드에서 원하는 데이터 필터링
        product_options = response_data.get("productOption", [])
        for option in product_options:
            prdtNo = option.get("prdtNo")
            optnName = option.get("optnName")
            orderDailydlvyPsbltQty = option.get("orderDailydlvyPsbltQty")
            if prdtNo and optnName:
                if optnName in ["280"]:    ### 🟥 [3.1]
                    botmsg3 = (f"{prdtNo},{optnName}: {orderDailydlvyPsbltQty}\n")
                else:
                    print(f"prdtNo: {prdtNo}, optnName: {optnName}, orderDailydlvyPsbltQty: {orderDailydlvyPsbltQty}")
        botmsg = ''.join([botmsg1,botmsg2,botmsg3]) ### 🟥 [3.2]
        asyncio.run(run_bot(botmsg, CHAT_ID))
    except Exception as e:
        print(f"Error analyzing request: {e}")

# 예시 분석 함수 3
def analyze_request_data3(driver, message_data):
    try:
        # 요청의 JSON 응답을 가져옴
        response_body = driver.execute_cdp_cmd("Network.getResponseBody", {
            "requestId": message_data["params"]["requestId"]
        })
        response_data = json.loads(response_body["body"])
            
        # 맨 위에 출력할 항목들
        engPrdtName = response_data.get("engPrdtName", "N/A")
        styleInfo = response_data.get("styleInfo", "N/A")
        prdtColorInfo = response_data.get("prdtColorInfo", "N/A")
        displayProductPrice = response_data.get("displayProductPrice", "N/A")
        displayDiscountRate = response_data.get("displayDiscountRate", "N/A")

        # 맨 윗줄에 출력
        botmsg1 = "88000 by ??/?? [스탁엑스3]\n" ### 🟥 [2]
        botmsg2 = f"{displayProductPrice},{displayDiscountRate}%,{styleInfo}-{prdtColorInfo}\n{engPrdtName}\n"  ### 🟥

        # productOption 필드에서 원하는 데이터 필터링
        product_options = response_data.get("productOption", [])
        for option in product_options:
            prdtNo = option.get("prdtNo")
            optnName = option.get("optnName")
            orderDailydlvyPsbltQty = option.get("orderDailydlvyPsbltQty")
            if prdtNo and optnName:
                if optnName in ["220"]:    ### 🟥 [3.1]
                    botmsg3 = (f"{prdtNo},{optnName}: {orderDailydlvyPsbltQty}\n")
                if optnName in ["225"]:    ### 🟥 [3.1]
                    botmsg4 = (f"{prdtNo},{optnName}: {orderDailydlvyPsbltQty}\n")
                if optnName in ["230"]:    ### 🟥 [3.1]
                    botmsg5 = (f"{prdtNo},{optnName}: {orderDailydlvyPsbltQty}\n")
                if optnName in ["235"]:    ### 🟥 [3.1]
                    botmsg6 = (f"{prdtNo},{optnName}: {orderDailydlvyPsbltQty}\n")
                if optnName in ["240"]:    ### 🟥 [3.1]
                    botmsg7 = (f"{prdtNo},{optnName}: {orderDailydlvyPsbltQty}\n")
                if optnName in ["245"]:    ### 🟥 [3.1]
                    botmsg8 = (f"{prdtNo},{optnName}: {orderDailydlvyPsbltQty}\n")
                if optnName in ["250"]:    ### 🟥 [3.1]
                    botmsg9 = (f"{prdtNo},{optnName}: {orderDailydlvyPsbltQty}\n")
                if optnName in ["255"]:    ### 🟥 [3.1]
                    botmsg10 = (f"{prdtNo},{optnName}: {orderDailydlvyPsbltQty}\n")
                else:
                    print(f"prdtNo: {prdtNo}, optnName: {optnName}, orderDailydlvyPsbltQty: {orderDailydlvyPsbltQty}")
        botmsg = ''.join([botmsg1,botmsg2,botmsg3,botmsg4,botmsg5,botmsg6,botmsg7,botmsg8,botmsg9,botmsg10]) ### 🟥 [3.2]
        asyncio.run(run_bot(botmsg, CHAT_ID))
    except Exception as e:
        print(f"Error analyzing request: {e}")

# 예시 분석 함수 4
def analyze_request_data4(driver, message_data):
    try:
        # 요청의 JSON 응답을 가져옴
        response_body = driver.execute_cdp_cmd("Network.getResponseBody", {
            "requestId": message_data["params"]["requestId"]
        })
        response_data = json.loads(response_body["body"])
            
        # 맨 위에 출력할 항목들
        engPrdtName = response_data.get("engPrdtName", "N/A")
        styleInfo = response_data.get("styleInfo", "N/A")
        prdtColorInfo = response_data.get("prdtColorInfo", "N/A")
        displayProductPrice = response_data.get("displayProductPrice", "N/A")
        displayDiscountRate = response_data.get("displayDiscountRate", "N/A")

        # 맨 윗줄에 출력
        botmsg1 = "215000 by ??/?? [스탁엑스4]\n" ### 🟥 [2]
        botmsg2 = f"{displayProductPrice},{displayDiscountRate}%,{styleInfo}-{prdtColorInfo}\n{engPrdtName}\n"  ### 🟥

        # productOption 필드에서 원하는 데이터 필터링
        product_options = response_data.get("productOption", [])
        for option in product_options:
            prdtNo = option.get("prdtNo")
            optnName = option.get("optnName")
            orderDailydlvyPsbltQty = option.get("orderDailydlvyPsbltQty")
            if prdtNo and optnName:
                if optnName in ["250"]:    ### 🟥 [3.1]
                    botmsg3 = (f"{prdtNo},{optnName}: {orderDailydlvyPsbltQty}\n")
                else:
                    print(f"prdtNo: {prdtNo}, optnName: {optnName}, orderDailydlvyPsbltQty: {orderDailydlvyPsbltQty}")
        botmsg = ''.join([botmsg1,botmsg2,botmsg3]) ### 🟥 [3.2]
        asyncio.run(run_bot(botmsg, CHAT_ID))
    except Exception as e:
        print(f"Error analyzing request: {e}")





if __name__ == "__main__":
    prod_url = "https://grandstage.a-rt.com/product/new?prdtNo=1020105566&page=1" ### 🟥
    capture_and_analyze_network_logs(analyze_request_data1) ### 🟥
    random_delay()

    prod_url = "https://grandstage.a-rt.com/product/new?prdtNo=1020112354&page=1" ### 🟥
    capture_and_analyze_network_logs(analyze_request_data2) ### 🟥
    random_delay()

    prod_url = "https://grandstage.a-rt.com/product/new?prdtNo=1020112191&page=1" ### 🟥
    capture_and_analyze_network_logs(analyze_request_data3) ### 🟥
    random_delay()

    prod_url = "https://grandstage.a-rt.com/product/new?prdtNo=1020111590&page=1" ### 🟥
    capture_and_analyze_network_logs(analyze_request_data4) ### 🟥
    random_delay()

















