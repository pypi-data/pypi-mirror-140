# 从关键字文件导入基类
from yhproject_pkg.framework.key_word.keyword_web import WebKeys


class QxglPage(WebKeys):
    def input_user(self, search_key):
        self.locator("xpath", "//*[@id='app']/section/div/div[1]/div/form/div/div/div/input").send_keys(search_key)
        self.wait(2)
        self.locator("xpath", "//*[@id='app']/section/div/div[1]/div/form/button[1]/span").click()
        self.wait(2)

    def button_refresh(self):
        self.locator("xpath", "//*[@id='app']/section/div/div[1]/div/form/button[2]/span").click()

    def button_jksq(self):
        self.locator("xpath", "//*[@id='app']/section/div/div[2]/div/div[1]/div[4]/div[2]/table/tbody/tr/td[7]/div/button").click()
        self.wait(2)

    def input_jkls(self, search_key):
        self.locator("xpath", "//*[@id='app']/section/div/div[3]/div/div/div[2]/div[2]/div[1]/div/div[1]/input").send_keys(search_key)
        self.wait(2)

    def box_alljk(self):
        self.locator("xpath", "//*[@id='app']/section/div/div[3]/div/div/div[2]/div[2]/div[1]/p/label/span[1]").click()

    def box_allsq(self):
        self.locator("xpath", "//*[@id='app']/section/div/div[3]/div/div/div[2]/div[2]/div[3]/p/label/span[1]").click()

    def box_jkls(self):
        self.locator("xpath", "//*[@id='app']/section/div/div[3]/div/div/div[2]/div[2]/div[1]/div/div[2]/label/span[1]").click()

    def box_sqls(self):
        self.locator("xpath", "//*[@id='app']/section/div/div[3]/div/div/div[2]/div[2]/div[3]/div/div[2]/label/span[1]").click()

    def button_sq(self):
        self.locator("xpath", "//*[@id='app']/section/div/div[3]/div/div/div[2]/div[2]/div[2]/button[2]").click()

    def button_qxsq(self):
        self.locator("xpath", "//*[@id='app']/section/div/div[3]/div/div/div[2]/div[2]/div[2]/button[1]").click()

    def button_qr(self):
        self.locator("xpath", "//*[@id='app']/section/div/div[3]/div/div/div[3]/span/button[2]").click()
