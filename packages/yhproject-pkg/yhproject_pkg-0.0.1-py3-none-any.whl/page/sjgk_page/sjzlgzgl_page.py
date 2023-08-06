# 从关键字文件导入基类
from yhproject_pkg.framework.key_word.keyword_web import WebKeys


class SjzlgzglPage(WebKeys):
    def button_add(self):
        self.locator("xpath", "//*[@id='app']/section/div/div/div/div[1]/div[1]/button[1]").click()
        self.wait(2)

    def input_rwmc(self, word_keys):
        self.locator("xpath", "//*[@id='app']/section/div/div/div/div[4]/div/div/div[2]/form/div[1]/div/div/input").send_keys(word_keys)
        self.wait(2)

    def input_rulecode(self, word_keys):
        self.locator("xpath", "//*[@id='app']/section/div/div/div/div[4]/div/div/div[2]/form/div[2]/div/div/div/input").send_keys(word_keys)
        self.wait(2)
        self.down_keys()
        self.wait(2)
        self.enter_keys()
        self.wait(2)

    def button_qr(self):
        self.locator("xpath", "//*[@id='app']/section/div/div/div/div[4]/div/div/div[3]/span/button[2]").click()
        self.wait(1)

    def input_search(self, word_keys):
        self.locator("xpath", "//*[@id='app']/section/div/div/div/div[1]/div[3]/input").send_keys(word_keys)
        self.wait(2)
        self.locator("xpath", "//*[@id='app']/section/div/div/div/div[1]/button[1]").click()
        self.wait(2)

    def button_reset(self):
        self.locator("xpath", "//*[@id='app']/section/div/div/div/div[1]/button[2]").click()
        self.wait(2)

    def button_action(self):
        self.locator("xpath", "//*[@id='app']/section/div/div/div/div[2]/div[5]/div[2]/table/tbody/tr/td[9]/div/button[1]").click()
        self.wait(2)
        self.enter_keys()
        self.wait(1)

    def button_edit(self):
        self.locator("xpath", "//*[@id='app']/section/div/div/div/div[2]/div[5]/div[2]/table/tbody/tr/td[9]/div/button[2]").click()
        self.wait(2)

    def button_remove(self):
        self.locator("xpath", "//*[@id='app']/section/div/div/div/div[2]/div[5]/div[2]/table/tbody/tr/td[9]/div/button[3]").click()
        self.wait(2)
        self.enter_keys()
        self.wait(2)
