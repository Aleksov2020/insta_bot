import configparser  # импортируем библиотеку
import random
import time
import selenium

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

chrome_options = Options()
chrome_options.add_extension("prox.zip")

config = configparser.ConfigParser()
config.read("conf.ini")


def count_to_int(count):
    if count.__contains__('M'):
        count = count.replace('M', '000000')
    if count.__contains__('K'):
        count = count.replace('K', '') + '000'
    if count.__contains__('.'):
        count = count.replace('.', '')
        return int(count) / 10
    if count.__contains__(','):
        count = count.replace(',', '')

    return int(count)


def auth(reel_page):
    actions = ActionChains(reel_page)
    reel_page.find_element(By.NAME, "username").send_keys("moroellene")
    reel_page.find_element(By.NAME, "password").send_keys("SA0XTDAoDPKCz")
    time.sleep(0.5)
    actions.click(reel_page.find_element(By.XPATH, "//*[text()='Войти']"))
    actions.perform()
    time.sleep(10 + random.random() * 2)
    actions.click(reel_page.find_element(By.XPATH, "//*[text()='Не сейчас']"))
    actions.perform()
    time.sleep(4 + random.random() * 2)


def start(url):
    # получаем сайт
    # TODO сделать try
    account_page = webdriver.Chrome('C:/chromedriver.exe', chrome_options=chrome_options)
    account_page.get(url)
    time.sleep(3 + random.random() * 2)

    # получаем количество подписчиков
    count_of_subs = count_to_int(
        account_page.find_element(
            By.XPATH,
            config["TAGS"]["xpath_to_subscribers_count"]
        ).text.split(' ')[0]
    )

    # Проматываем в самый низ страницы. Будет 24 поста, если стоит 2 в настройках
    for i in range(0, int(config["SETTINGS"]["count_of_pages_with_reels"])):
        account_page.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)
        time.sleep(2 + random.random() * 2)

    # Забираем все подгруженные строки с рилсами
    reels_rows = account_page.find_elements(
        By.CLASS_NAME,
        config["TAGS"]["class_to_element_with_reels_rows"]
    )

    # Собираем количество просмотров рилса и собираем ссылки с рилсов. i-ая ссылка соответствует i-ому счетчику просмотров
    reels_link_list = []
    views_list = []
    for reels_row in reels_rows:
        for res_page in reels_row.find_elements(By.CLASS_NAME, config["TAGS"]["class_to_element_with_reel_link"]):
            reels_link_list.append(res_page.get_attribute('href'))
            views_list.append(count_to_int(res_page.text))

    print(reels_link_list)
    print(views_list)

    # Ищем посты за последние сутки
    time_validate_reel_links = []
    reel_page = webdriver.Chrome('C:/chromedriver.exe', chrome_options=chrome_options)
    for reel in reels_link_list:
        try:
            # возможно стоит сразу логиниться, чтобы не вызывать подозрений у инсты.
            reel_page.get(reel)
            time.sleep(5 + random.random() * 2)
            time_ = reel_page.find_element(By.CLASS_NAME, '_ae5u._ae5v._ae5w').text
        except:
            # если перекинуло на логин, то логинимся
            # TODO можно будет убрать после подключения мобильного прокси.
            # TODO Высчитать через сколько примерно по времени банит инста
            auth(reel_page)
            time_ = reel_page.find_element(By.CLASS_NAME, '_ae5u._ae5v._ae5w').text

        if time_.__contains__("ЧАСОВ") or \
                time_.__contains__("МИНУТ") or \
                time_.__contains__("СЕКУНД") or \
                time_.__contains__("ЧАС") or \
                time_.__contains__("МИНУТУ") or \
                time_.__contains__("СЕКУНДУ"):
            time_validate_reel_links.append(reel)
        else:
            reel_page.close()
            break

    validate_reels = []
    for i in range(0, len(time_validate_reel_links)):
        if views_list[i] / count_of_subs > float(config["SETTINGS"]["percent"]):
            validate_reels.append(time_validate_reel_links[i])

    print(validate_reels)
    return validate_reels