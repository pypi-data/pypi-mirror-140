# 从关键字文件导入基类
from yhproject_pkg.framework.key_word.keyword_web import WebKeys


class JkcxPage(WebKeys):
    def input_search(self, search_key):
        self.locator("xpath", "//*[@id='app']/section/div/div[1]/div/form/div[1]/div/div/input").send_keys(search_key)
        self.wait(2)
        self.locator("xpath", "//*[@id='app']/section/div/div[1]/div/form/button[1]").click()
        self.wait(2)

    def button_reset(self):
        self.locator("xpath", "//*[@id='app']/section/div/div[1]/div/form/button[2]").click()
        self.wait(2)

    def button_apply(self):
        self.locator("xpath", "//*[@id='app']/section/div/div[2]/div/div[2]/div[4]/div[2]/table/tbody/tr[1]/td[8]/div/button").click()
        self.wait(2)

    def button_appkey(self):
        self.locator("xpath", "//*[@id='app']/section/div/div[2]/div/div[1]/button").click()
        self.wait(2)

    def button_close(self):
        self.locator("xpath", "//*[@id='app']/section/div/div[2]/div/div[4]/div/div/div[1]/button").click()

    def button_apitest(self):
        self.locator("xpath", "//*[@id='app']/section/div/div[2]/div/div[4]/div/div[2]/div/div/div/form/div/div[2]/div/div[9]/div/span[2]/button").click()

    def button_reback(self):
        self.locator("xpath", "//*[@id='app']/section/div/div[2]/div/div[4]/div/div[2]/div/div/div/form/div/div[2]/div/div[11]/button").click()
