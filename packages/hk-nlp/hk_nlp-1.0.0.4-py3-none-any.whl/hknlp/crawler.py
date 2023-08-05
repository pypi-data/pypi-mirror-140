import random as rd
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys


def set_options(headless=True):
    window_sizes = [(1280, 1024), (1600, 1200), (1920, 1440), (1920, 1080), (2560, 1600), (3840, 2400)]
    options = webdriver.ChromeOptions()
    if headless:
        options.add_argument('headless')  # 웹을 보이지 않게 실행(headless)
    options.add_argument('window-size={}x{}'.format(*window_sizes[rd.randint(0, len(window_sizes) - 1)]))  # 창 크기 설정
    options.add_argument("disable-gpu")  # gpu설정
    options.add_argument("lang=ko_KR")  # 언어 설정
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    return options


class BasicCrawler(object):
    def __init__(self, engine='chromedriver', headless=True):
        self.driver = webdriver.Chrome(engine, options=set_options(headless=headless))

    def get_page(self, url):
        self.driver.get(url)
        self.driver.implicitly_wait(10)

    def page_down(self):
        ActionChains(self.driver).send_keys(Keys.END).perform()
        self.driver.implicitly_wait(10)

    def press_enter(self):
        ActionChains(self.driver).send_keys(Keys.ENTER).perform()
        self.driver.implicitly_wait(10)

    def close(self):
        self.driver.close()

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()