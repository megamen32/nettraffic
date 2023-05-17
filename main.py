import datetime
import itertools
import os
import random
import re
import subprocess
import threading
import time
import traceback

from cachetools import cached, TTLCache

import requests as requests
from selenium.webdriver.support.wait import WebDriverWait
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import threading
import time
SERVER_URL='http://bezrabotnyi.com:8888'
from requests.auth import HTTPBasicAuth
AUTH = HTTPBasicAuth(username='rasta', password='6516599')
ip_cache = TTLCache(maxsize=1, ttl=datetime.timedelta(minutes=10).total_seconds())
proxies_cashe = TTLCache(maxsize=2, ttl=datetime.timedelta(minutes=10).total_seconds())
@cached(ip_cache)
def get_public_ip():
    try:
        response = requests.get('https://checkip.amazonaws.com')
        response.raise_for_status()
        return response.text.strip()
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None
@cached(proxies_cashe)
def get_proxies(ip=None):
    if not ip:
        ip=get_public_ip()
    proxies = requests.get(f'{SERVER_URL}/proxy/', auth=AUTH, params={'ip': ip,'count':300}).json()
    return proxies
from my_fake_useragent import UserAgent
from user_agent import generate_user_agent
def random_useragent():
    agent_1 = generate_user_agent(device_type='smartphone')
    agents_2 = [UserAgent(os_family='ios').random(), UserAgent(os_family='android').random(),
                UserAgent(phone=True).random()]
    agent_2 = random.choice(agents_2)
    agents = [agent_1, agent_2]
    agent = random.choice(agents)
    return agent
def get_random_proxy():
    while True:
        proxies = get_proxies()
        proxy_random = random.choice(proxies)
        proxy = proxy_random['proxy']
        auth_required = re.search(':.*[@:].*:', proxy)
        if auth_required:
            proxys = proxy.replace('@', ':')
            proxys = proxys.split(':')
            PROXY_HOST = proxys[2]
            PROXY_PORT = proxys[-1]
            PROXY_USER = proxys[0]
            PROXY_PASS = proxys[1]
            prx = {
                'http': f'http://{PROXY_USER}:{PROXY_PASS}@{PROXY_HOST}:{PROXY_PORT}',
                'https': f'http://{PROXY_USER}:{PROXY_PASS}@{PROXY_HOST}:{PROXY_PORT}',
            }
        else:
            prx = {
                'http': f'http://{proxy}',
                'https': f'http://{proxy}',
            }
        try:
            print(proxy)
            useragent = random_useragent()
            requests.get('https://t.me/bezrabotnyi', headers={'user-agent': useragent}, proxies=prx, timeout=2)
            requests.get('https://bit.ly/3nYYtiZ', headers={'user-agent': useragent}, proxies=prx, timeout=2)
            return prx['http']
        except:
            continue


from playwright.async_api import async_playwright
import asyncio

from playwright.async_api import async_playwright
import asyncio
from get_driver import get_driver

def do_traffic(url, goto_url):
    try:

        proxy = get_random_proxy()
        driver = get_driver(proxy)  # Сюда добавьте параметр proxy, если это необходимо

        driver.get(url)

        # Ищем на странице goto_url и кликаем
        link = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, f"//a[contains(@href, '{goto_url}')]"))
        )
        link.click()

        # Переключаемся на новую вкладку
        driver.switch_to.window(driver.window_handles[-1])
        time.sleep(random.randint(5, 10))

        # Ищем кнопку и кликаем
        btn = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, "//a[contains(@class, 'btn_new')]"))
        )
        btn.click()

        driver.switch_to.window(driver.window_handles[-1])
        print(driver.current_url)


    except:
        traceback.print_exc()
    finally:
        driver.quit()
def parse_proxy(proxy):
    if proxy is None: return None
    proxy_url = proxy["proxy"] if 'proxy' in proxy else proxy

    if "@" in proxy_url:
        credentials, host_and_port = proxy_url.split("@")
        username, password = credentials.split(":")
        proxy_url = f"http://{host_and_port}"
    else:
        username = ""
        password = ""

    return {
        "server": proxy_url,
        "username": username,
        "password": password,
    }

from concurrent.futures import ThreadPoolExecutor

from concurrent.futures import ThreadPoolExecutor
import time

# Функция для чтения количества открытых ссылок из файла
def read_count():
    try:
        with open('count.txt', 'r') as file:
            return int(file.read())
    except FileNotFoundError:
        return 0

# Функция для записи количества открытых ссылок в файл
def write_count(count):
    with open('count.txt', 'w') as file:
        file.write(str(count))

def run():
    max_tasks = 10
    total_tasks = 550
    url = "https://t.me/podslushhhno/5?embed=1"
    goto_url = "https://bit.ly/3nYYtiY"

    # Читаем количество уже открытых ссылок
    opened_links = read_count()

    if opened_links >= total_tasks:
        print(f'All {total_tasks} links have been opened')
        return

    times = []

    with ThreadPoolExecutor(max_workers=max_tasks) as executor:
        for _ in range(total_tasks - opened_links):
            start = time.time()
            executor.submit(do_traffic, url, goto_url)
            end = time.time()
            times.append(end - start)

            # Увеличиваем счетчик открытых ссылок и записываем его в файл
            opened_links += 1
            write_count(opened_links)

    avg_time = sum(times) / len(times)
    print(f'Average time per task: {avg_time} seconds')

    total_hours = 5
    total_seconds = total_hours * 60 * 60

    # Расчет времени задержки между задачами, чтобы распределить их равномерно на 5 часов
    delay = total_seconds / total_tasks - avg_time

    if delay < 0:
        print('Warning: tasks cannot be evenly distributed within 5 hours with the current average time.')
    else:
        print(f'Suggested delay between tasks: {delay} seconds')


if __name__=='__main__':
# Запускаем асинхронную функцию run
    run()


