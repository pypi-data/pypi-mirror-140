# 从关键字文件导入基类
from yhproject_pkg.framework.key_word.keyword_web import WebKeys


class TmgzPage(WebKeys):
    def input_search(self, word_keys):
        self.locator("xpath", "//*[@id='app']/section/div/div/div/div/div/div[1]/div[1]/div/input").send_keys(word_keys)
        self.wait(2)
        self.locator("xpath", "//*[@id='app']/section/div/div/div/div/div/div[1]/div[1]/button[1]").click()
        self.wait(5)

    def button_reset(self):
        self.locator("xpath", "//*[@id='app']/section/div/div/div/div/div/div[1]/div[1]/button[2]").click()
        self.wait(2)

    def button_remove(self):
        self.locator("xpath", "//*[@id='app']/section/div/div/div/div/div/div[1]/div[2]/button[2]").click()
        self.wait(2)
        self.enter_keys()
        self.wait(2)

    # 新增
    def button_add(self):
        self.locator("xpath", "//*[@id='app']/section/div/div/div/div/div/div[1]/div[2]/button[1]").click()
        self.wait(2)

    def input_gzmc(self, word_keys):
        self.locator("xpath", "//*[@id='app']/section/div/div/div/div/div/div[4]/div/div[2]/div/form/div[1]/div/div[1]/input").send_keys(word_keys)
        self.wait(2)

    def input_egzmc(self, word_keys):
        self.locator("xpath", "//*[@id='app']/section/div/div/div/div/div/div[5]/div/div[2]/div/form/div[1]/div/div/input").send_keys(word_keys)
        self.wait(2)

    def input_gzbm(self, word_keys):
        self.locator("xpath", "//*[@id='app']/section/div/div/div/div/div/div[4]/div/div[2]/div/form/div[2]/div/div[1]/input").send_keys(word_keys)
        self.wait(2)

    def input_gzdj(self, word_keys):
        self.locator("xpath", "//*[@id='app']/section/div/div/div/div/div/div[4]/div/div[2]/div/form/div[3]/div/div/div/input").clear()
        self.locator("xpath", "//*[@id='app']/section/div/div/div/div/div/div[4]/div/div[2]/div/form/div[3]/div/div/div/input").send_keys(word_keys)
        self.wait(2)

    def input_bds(self, word_keys, word_keys1):
        self.locator("xpath", "//*[@id='app']/section/div/div/div/div/div/div[4]/div/div[2]/div/form/div[5]/div/div[1]/input").send_keys(word_keys)
        self.locator("xpath", "//*[@id='app']/section/div/div/div/div/div/div[4]/div/div[2]/div/form/div[5]/div/div[2]/input").send_keys(word_keys1)
        self.wait(2)

    def input_thfh(self, word_keys):
        self.locator("xpath", "//*[@id='app']/section/div/div/div/div/div/div[4]/div/div[2]/div/form/div[6]/div/div[1]/input").send_keys(word_keys)
        self.wait(2)

    def input_gzlx(self):
        self.locator("xpath", "//*[@id='app']/section/div/div/div/div/div/div[4]/div/div[2]/div/form/div[4]/div/div/div/input").click()
        self.wait(1)
        self.up_keys()
        self.wait(1)
        self.enter_keys()
        self.wait(2)

    def input_gzmy(self, word_keys):
        self.locator("xpath", "//*[@id='app']/section/div/div/div/div/div/div[4]/div/div[2]/div/form/div[6]/div/div[1]/input").send_keys(word_keys)

    def input_gzms(self, word_keys):
        self.locator("xpath", "//*[@id='app']/section/div/div/div/div/div/div[4]/div/div[2]/div/form/div[7]/div/div/textarea").send_keys(word_keys)

    def button_save(self):
        self.locator("xpath", "//*[@id='app']/section/div/div/div/div/div/div[4]/div/div[3]/div/button[2]").click()

    def button_esave(self):
        self.locator("xpath", "//*[@id='app']/section/div/div/div/div/div/div[5]/div/div[3]/div/button[2]").click()
        self.wait(5)

    def button_setting(self):
        self.locator("xpath", "//*[@id='app']/section/div/div/div/div/div/div[1]/div[2]/button[2]").click()
        self.wait(2)

    def button_edit(self):
        self.locator("xpath", "//*[@id='app']/section/div/div/div/div/div/div[2]/div[5]/div[2]/table/tbody/tr[1]/td[13]/div/div/button[1]").click()
        self.wait(2)

    def button_eremove(self):
        self.locator("xpath", "//*[@id='app']/section/div/div/div/div/div/div[2]/div[5]/div[2]/table/tbody/tr[1]/td[13]/div/div/button[2]").click()
        self.wait(2)
        self.enter_keys()
        self.wait(5)

    def box_check(self):
        self.locator("xpath", "//*[@id='app']/section/div/div/div/div/div/div[2]/div[4]/div[2]/table/tbody/tr/td[1]/div/label/span/span").click()
        self.wait(2)




