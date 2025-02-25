import configparser
import random
import time
import datetime
import urllib.request
import Reel
import os.path
import selenium

from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FOptions
from selenium.webdriver import ActionChains, DesiredCapabilities
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


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


def auth(reel_page, wait):
    actions = ActionChains(reel_page)
    reel_page.find_element(By.NAME, "username").send_keys("moroellene")
    reel_page.find_element(By.NAME, "password").send_keys("SA0XTDAoDPKCz")
    time.sleep(0.5)
    actions.click(reel_page.find_element(By.XPATH, "//*[text()='Войти']"))
    actions.perform()
    try:
        not_now = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[text()='Не сейчас']")))
        actions.click(not_now)
    finally:
        actions.perform()


def start(url, category):
    config = configparser.ConfigParser()
    config.read("conf.ini")

    # получаем сайт
    # TODO сделать try
    options = FOptions()
    options.binary_location = r'C:\Program Files\Mozilla Firefox\firefox.exe'
    account_page = webdriver.Firefox(executable_path=r'C:\geckodriver.exe', options=options)
    account_page.get(url)
    wait = WebDriverWait(account_page, 30)

    # получаем количество подписчиков
    count_of_subs = count_to_int(
        wait.until(
            EC.presence_of_element_located((
                By.XPATH,
                config['TAGS']['xpath_to_subscribers_count']
            ))
        ).text.split(' ')[0]
    )

    # Проматываем в самый низ страницы. Будет 24 поста, если стоит 2 в настройках
    for i in range(0, int(config['SETTINGS']['count_of_pages_with_reels'])):
        account_page.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)
        time.sleep(1 + random.random() * 2)

    # Забираем все подгруженные строки с рилсами
    reels_rows = account_page.find_elements(
        By.CLASS_NAME,
        config['TAGS']['class_to_element_with_reels_rows']
    )

    # Собираем количество просмотров рилса и собираем ссылки с рилсов. i-ая ссылка соответствует i-ому счетчику
    # просмотров
    reels_link_list = []
    views_list = []
    for reels_row in reels_rows:
        for res_page in reels_row.find_elements(By.CLASS_NAME, config['TAGS']['class_to_element_with_reel_link']):
            reels_link_list.append(res_page.get_attribute('href'))
            views_list.append(count_to_int(res_page.text))

    # Ищем посты за последние сутки
    validate_reel_video_links_list = []
    validate_reels_link_list = []

    reel_page = webdriver.Firefox(executable_path=r'C:\geckodriver.exe', options=options)
    wait_reel = WebDriverWait(reel_page, 30)
    for reel in reels_link_list:
        try:
            reel_page.get(reel)
            time_ = wait_reel.until(
                EC.presence_of_element_located((
                    By.CLASS_NAME,
                    config['TAGS']['class_to_time']
                ))
            ).text
            link_to_video1 = wait_reel.until(
                EC.presence_of_element_located((
                    By.CLASS_NAME,
                    config['TAGS']['class_to_video_link']
                ))
            )
            link_to_video = link_to_video1.find_element(By.TAG_NAME, 'video').get_attribute('src')
        except:
            # если перекинуло на логин, то логинимся
            # TODO Высчитать через сколько примерно по времени банит инста
            auth(reel_page, WebDriverWait(reel_page, 30))
            time_ = wait_reel.until(
                EC.presence_of_element_located((
                    By.CLASS_NAME,
                    config['TAGS']['class_to_time']
                ))
            ).text
            link_to_video1 = wait_reel.until(
                EC.presence_of_element_located((
                    By.CLASS_NAME,
                    config['TAGS']['class_to_video_link']
                ))
            )
            link_to_video = link_to_video1.find_element(By.TAG_NAME, 'video').get_attribute('src')

        if time_.__contains__("ЧАСОВ") or \
                time_.__contains__("МИНУТ") or \
                time_.__contains__("СЕКУНД") or \
                time_.__contains__("ЧАС") or \
                time_.__contains__("МИНУТУ") or \
                time_.__contains__("СЕКУНДУ"):
            validate_reels_link_list.append(reel)
            validate_reel_video_links_list.append(link_to_video)
            reel_page.close()
        else:
            reel_page.close()
            break

    reels_object_list = []
    for i in range(0, len(validate_reel_video_links_list)):
        if views_list[i] / count_of_subs > float(config["SETTINGS"]["percent"]):
            now = datetime.datetime.now()
            destination = str(now.strftime("%d-%m-%Y_%H-%M-%S")) + '.mp4'
            urllib.request.urlretrieve(validate_reel_video_links_list[i], destination)

            reels_object_list.append(
                Reel(
                    validate_reels_link_list[i],
                    views_list[i],
                    category,
                    count_of_subs,
                    destination,
                    os.path.exists(destination),
                    now
                )
            )

    account_page.close()

    return reels_object_list


print(start("https://www.instagram.com/juliapolskayaa/reels/", "check"))
