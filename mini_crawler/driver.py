from selenium import webdriver
from selenium.webdriver.chrome.options import Options


class HeadlessChromeDriver(object):
    def __init__(self, chrome_driver='/usr/local/bin/chromedriver'):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--window-size=1920x1080")
        chrome_options.add_experimental_option('prefs', {'intl.accept_languages': 'zh-CN,zh'})

        self.driver = webdriver.Chrome(chrome_options=chrome_options, executable_path=chrome_driver)

    def get(self, url):
        self.driver.get(url=url)
        return self.driver.page_source

    def quit(self):
        self.driver.quit()
