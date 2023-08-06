# 从关键字文件导入基类
from yhproject_pkg.framework.key_word.keyword_web import WebKeys


class TmglPage(WebKeys):
    def input_search(self, key_words):
        self.locator("xpath", "//*[@id='app']/section/div/div/div/div/div/div[1]/div[1]/div/input").send_keys(key_words)
        self.wait(2)
        self.locator("xpath", "//*[@id='app']/section/div/div/div/div/div/div[1]/div[1]/button[1]").click()
        self.wait(2)

    def button_reset(self):
        self.locator("xpath", "//*[@id='app']/section/div/div/div/div/div/div[1]/div[1]/button[2]").click()
        self.wait(2)

    def button_manage(self):
        self.locator("xpath", "//*[@id='app']/section/div/div/div/div/div/div[1]/div[2]/button").click()
        self.wait(2)

    def core_switch(self):
        self.locator("xpath", "//*[@id='app']/section/div/div/div/div/div/div[2]/div[3]/table/tbody/tr/td[9]/div/div/span[2]").click()
        self.wait(1)

    def button_remove(self):
        self.locator("xpath", "//*[@id='app']/section/div/div/div/div/div/div[2]/div[5]/div[2]/table/tbody/tr/td[10]/div/div/button").click()
        self.wait(2)
        self.enter_keys()
        self.wait(2)


