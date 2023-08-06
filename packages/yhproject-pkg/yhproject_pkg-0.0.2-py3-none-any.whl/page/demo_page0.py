# 从关键字文件导入基类
from yhproject_pkg.framework.key_word.keyword_web import WebKeys
import time


class BaiduPage(WebKeys):
    url = "http://www.baidu.com"

    def search_input(self, search_key):
        self.locator("id", "kw").send_keys(search_key)

    def search_button(self):
        self.locator("id", "su").click()

    def button_ssgs(self):
        self.locator("xpath", "/html/body/div[2]/ul/li[3]/a").click()

    def get_screen(self):
        now_time = time.strftime('%Y_%m_%d_%H_%M_%S')
        self.driver.get_screenshot_as_file(f'{now_time}.jpg')

