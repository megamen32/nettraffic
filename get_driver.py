import json
import logging
import os
import pickle
import platform
import random
import re
import time
import traceback
import zipfile

import chromedriver_binary
import requests
from fake_useragent import UserAgent
from selenium.webdriver import DesiredCapabilities, Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver import ActionChains
from selenium.webdriver import Chrome
from undetected_chromedriver import ChromeOptions


from glob import glob

SELENIUMWIRE = False
if SELENIUMWIRE:
    pass
else:
    from selenium.webdriver import ActionChains
driver_list = []
WEBRTC = os.path.join('extension', 'webrtc_control.zip')
ACTIVE = os.path.join('extension', 'always_active.zip')
FINGERPRINT = os.path.join('extension', 'fingerprint_defender.zip')
TIMEZONE = os.path.join('extension', 'spoof_timezone.zip')
CUSTOM_EXTENSIONS = glob(os.path.join('extension', 'custom_extension', '*.zip')) + glob(
    os.path.join('extension', 'custom_extension', '*.crx'))
WIDTH = 0

VIEWPORT = ['1920,1080']
WATCH_IN_BACKROUND = True
REFERERS = ['https://search.yahoo.com/', 'https://duckduckgo.com/', 'https://www.google.com/', 'https://www.bing.com/',
            'https://t.co/', '']


def quit_driver(driver):
    try:
        driver.quit()
        if driver in driver_list:
            driver_list.remove(driver)
    except:
        traceback.print_exc()

    status = 400
    return status


def check_current_ip(driver, new_window=False):
    if new_window:
        driver.execute_script('''window.open("","_blank");''')
        driver.switch_to.window(driver.window_handles[1])

    driver.get('http://httpbin.org/ip')
    answer = driver.find_element(By.XPATH, '/html/body').text
    try:
        js_answer = json.loads(answer)
        ip = js_answer['origin']
        if new_window:
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
        return ip
    except:
        return '0.0.0.0'

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
def get_driver(proxy=None, mobile_simulation=False):
    background = True

    OSNAME = platform.system()
    exe_names = {'Linux': "./chromedriver", "Darwin": "./chromedriver", 'Windows': 'chromedriver.exe'}
    fname = exe_names['Linux']
    fname=chromedriver_binary.chromedriver_filename

    agent =  random_useragent()

    options = ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument("disable-popup-blocking")
    options.add_argument("disable-notifications")
    options.add_argument("disable-gpu")
    options.headless = background

    options.add_argument(f"--window-size={random.choice(VIEWPORT)}")
    options.add_argument("--log-level=3")
    options.add_experimental_option(
        "excludeSwitches", ["enable-automation", "enable-logging"]
    )
    options.add_experimental_option('useAutomationExtension', False)
    options.add_experimental_option(
        'prefs', {'intl.accept_languages': 'ru_RU,ru'}
    )
    options.add_argument(f"user-agent={agent}")
    options.add_argument("--mute-audio")

    options.add_argument('--disable-features=UserAgentClientHint')
    # options.AddArgument("--window-position=-32000,-32000");
    caps = DesiredCapabilities.CHROME['loggingPrefs'] = {'driver': 'OFF', 'server': 'OFF', 'browser': 'OFF'}
    # caps['pageLoadStrategy'] = 'eager'

    referer = False
    if referer: pass
    # options.add_argument("--Referer=https://away.vk.com")

    if mobile_simulation:
        devices = ['Nexus 5', 'iPhone X', 'Nexus 4', 'Galaxy S5', 'iPad', 'iPad Pro', 'Pixel 2']
        mobile_emulation = {"deviceName": random.choice(devices)}
        options.add_experimental_option("mobileEmulation", mobile_emulation)
    if not background:
        options.add_extension(WEBRTC)
        options.add_extension(FINGERPRINT)
        options.add_extension(TIMEZONE)
        if WATCH_IN_BACKROUND:
            options.add_extension(ACTIVE)

        if CUSTOM_EXTENSIONS:
            for extension in CUSTOM_EXTENSIONS:
                options.add_extension(extension)
    sel_options = {}
    if proxy is not None:
        auth_required = re.search(':.*[@:].*:', proxy)
        if auth_required:
            proxys = proxy.replace('@', ':')
            proxys = proxys.split(':')
            PROXY_HOST = proxys[2]
            PROXY_PORT = proxys[-1]
            PROXY_USER = proxys[0]
            PROXY_PASS = proxys[1]
            manifest_json = """
            {
                "version": "1.0.0",
                "manifest_version": 2,
                "name": "Chrome Proxy",
                "permissions": [
                    "proxy",
                    "tabs",
                    "unlimitedStorage",
                    "storage",
                    "<all_urls>",
                    "webRequest",
                    "webRequestBlocking"
                ],
                "background": {
                    "scripts": ["background.js"]
                },
                "minimum_chrome_version":"22.0.0"
            }
            """

            background_js = """
            var config = {
                    mode: "fixed_servers",
                    rules: {
                    singleProxy: {
                        scheme: "http",
                        host: "%s",
                        port: parseInt(%s)
                    },
                    bypassList: ["localhost"]
                    }
                };

            chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});

            function callbackFn(details) {
                return {
                    authCredentials: {
                        username: "%s",
                        password: "%s"
                    }
                };
            }

            chrome.webRequest.onAuthRequired.addListener(
                        callbackFn,
                        {urls: ["<all_urls>"]},
                        ['blocking']
            );
            """ % (PROXY_HOST, PROXY_PORT, PROXY_USER, PROXY_PASS)
            pluginfile = f'extension/proxy/proxy_auth_plugin{PROXY_HOST}.zip'
            os.makedirs('extension/proxy/', exist_ok=True)
            with zipfile.ZipFile(pluginfile, 'w') as zp:
                zp.writestr("manifest.json", manifest_json)
                zp.writestr("background.js", background_js)
            options.add_extension(pluginfile)

        else:
            if 'dummy' not in proxy:
                options.add_argument(f'--proxy-server={proxy}')
    if SELENIUMWIRE:
        driver = Chrome(executable_path=fname, options=options, desired_capabilities=caps,
                        seleniumwire_options=sel_options)
    else:
        driver = Chrome(executable_path=fname, options=options,
                        desired_capabilities=caps)  # ,seleniumwire_options=sel_options)
    driver_list.append(driver)
    if referer:
        REFERALS = ['https://away.vk.com/', 'https://www.google.com/', 'https://yandex.ru/']
        refere = random.choice(REFERALS)
        if SELENIUMWIRE:
            # Create a request interceptor
            def interceptor(request):
                del request.headers['Referer']  # Delete the header first
                request.headers['Referer'] = refere

            # Set the interceptor on the driver
            driver.request_interceptor = interceptor
        else:
            if False:
                driver.get("chrome-extension://fpfmkkljdiofokoikgglafnfmmffmmhc/html/options.html")
                driver.find_element_by_xpath('//*[@id="addall"]').click()
                # driver.find_element_by_xpath('//*[@id="jsBlock"]').click()
                time.sleep(1)
                driver.find_element_by_xpath('//*[@id="tableForm"]/div[6]/div[2]/label[3]').click()
                time.sleep(1)

                driver.find_element_by_xpath('//*[@id="inputDomain"]').send_keys(refere)
                time.sleep(1)
                driver.find_element_by_xpath('//*[@id="save"]').click()

    if proxy:
        if SELENIUMWIRE:
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
                    'https': f'https://{PROXY_USER}:{PROXY_PASS}@{PROXY_HOST}:{PROXY_PORT}',
                    "no_proxy": "localhost,127.0.0.1",
                }
                driver.proxy = prx
        if False:
            ip = check_current_ip(driver, False)
            print(f"IP is {ip} | good? {ip in proxy})")
            if ip not in proxy:
                quit_driver(driver)
                driver = None

    return driver
