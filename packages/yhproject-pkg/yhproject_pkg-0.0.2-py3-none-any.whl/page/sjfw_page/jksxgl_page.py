# 从关键字文件导入基类
from yhproject_pkg.framework.key_word.keyword_web import WebKeys


class JksxglPage(WebKeys):
    def input_search(self, search_key):
        self.locator("xpath", "//*[@id='app']/section/div/div[1]/div/form/div[1]/div/div/input").send_keys(search_key)

    def button_search(self):
        self.locator("xpath", "//*[@id='app']/section/div/div[1]/div/form/button[1]").click()
        self.wait(3)

    def button_reset(self):
        self.locator("xpath", "//*[@id='app']/section/div/div[1]/div/form/button[2]").click()
        self.wait(1)

    def button_select(self):
        self.locator("xpath", "//*[@id='app']/section/div/div[2]/div/div[1]/div[4]/div[2]/table/tbody/tr/td[8]/div/button[2]").click()
        self.wait(2)

    def button_apitest(self):
        self.locator("xpath", "//*[@id='app']/section/div/div[2]/div/div[3]/div/div[2]/div/div/div/form/div/div[2]/div/div[9]/div/span[2]/button").click()
        self.wait(2)

    def button_back(self):
        self.locator("xpath", "//*[@id='app']/section/div/div[2]/div/div[3]/div/div[2]/div/div/div/form/div/div[2]/div/div[11]/button").click()

    def button_line(self):
        self.locator("xpath", "//*[@id='app']/section/div/div[2]/div/div[1]/div[4]/div[2]/table/tbody/tr/td[8]/div/button[1]").click()

