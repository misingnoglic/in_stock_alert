try:
    import secrets
except:
    raise ImportError("Need to create secrets.py file, see README")

import time

import arrow
from bs4 import BeautifulSoup
from selenium import webdriver
from twilio.rest import Client
from playsound import playsound
from selenium.webdriver.chrome.options import Options

ITEM_URL = 'https://www.costco.com/kitchenaid-professional-series-6' \
           '-quart-bowl-lift-stand-mixer-with-flex-edge.product.100485356.html'

DRIVER_PATH = r'C:\Users\misin\Downloads\chromedriver_win32\chromedriver.exe'

SECONDS_BETWEEN_REQUESTS = 60

def setup_driver():
    user_agent = "user-agent=[Mozilla/5.0 (Windows NT 10.0; Win64; x64)" \
                 " AppleWebKit/537.36 (KHTML, like Gecko) " \
                 "Chrome/83.0.4103.116 Safari/537.36]"
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument(user_agent)
    driver = webdriver.Chrome(DRIVER_PATH, chrome_options=chrome_options)
    return driver

def setup_twilio_client():
    account_sid = secrets.TWILIO_ACCOUNT_SID
    auth_token = secrets.TWILIO_AUTH_TOKEN
    return Client(account_sid, auth_token)


def check_inventory_loop():
    driver = setup_driver()
    while True:
        try:
            check_inventory(driver)
            time.sleep(SECONDS_BETWEEN_REQUESTS)
        except KeyboardInterrupt:
            driver.close()
            driver.quit()
            return


def check_inventory(driver):
    print("Attempting at {}".format(arrow.now().format('YYYY-MM-DD HH:mm:ss')))
    page_html = get_page_html(driver)
    if check_item_in_stock(page_html):
        send_notification()
    else:
        print("Out of stock still")


def get_page_html(driver):
    driver.get(ITEM_URL)
    print("page received")
    return driver.page_source

def check_item_in_stock(page_html):
    soup = BeautifulSoup(page_html, "lxml")
    out_of_stock_divs = soup.findAll("img", {"class": "oos-overlay"})
    matches = 0
    for div in out_of_stock_divs:
        if 'hide' not in div.get('class'):
            matches += 1

    return matches > 0

def send_notification():
    print("Not out of stock!")
    twilio_client = setup_twilio_client()
    for number in secrets.NUMBERS_TO_SEND_TO:
        twilio_client.messages.create(
            body="Your item is available for purchase.",
            from_=secrets.TWILIO_FROM_NUMBER,
            to=number
        )
    while True:
        playsound('alarm.mp3')

if __name__ == '__main__':
    check_inventory_loop()
