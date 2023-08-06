from yhproject_pkg.framework.key_word.keyword_web import WebKeys
from selenium.webdriver.common.keys import Keys


class DdglPage(WebKeys):

    # 新增任务
    def button_add(self):
        self.locator("xpath", "//*[@id='app']/section/div/div[2]/div/div[1]/div[1]/button[1]").click()
        self.wait(3)

    def input_rwlx(self, word_keys):
        self.locator("xpath", "//*[@id='app']/section/div/div[3]/div/div/div[2]/div/form/div[1]/div/div/div/input").send_keys(word_keys)
        self.wait(2)
        self.down_keys()
        self.enter_keys()

    def input_rwmc(self, search_key):
        self.locator("xpath", "//*[@id='app']/section/div/div[3]/div/div/div[2]/div/form/div[2]/div/div[1]/div/input").send_keys(search_key)

    def input_url(self, search_key):
        self.locator("xpath", "//*[@id='app']/section/div/div[3]/div/div/div[2]/div/form/div[3]/div/div[1]/div/input").send_keys(search_key)

    def input_qqlx(self, search_key):
        self.locator("xpath", "//*[@id='app']/section/div/div[3]/div/div/div[2]/div/form/div[4]/div/div/div/input").send_keys(search_key)
        self.wait(1)
        self.down_keys()
        self.down_keys()
        self.wait(1)
        self.enter_keys()

    def input_jjrzx(self):
        self.locator("xpath", "//*[@id='app']/section/div/div[3]/div/div/div[2]/div/form/div[5]/div/label[2]/span[1]/span").click()

    def input_rwms(self, search_key):
        self.locator("xpath", "//*[@id='app']/section/div/div[3]/div/div/div[2]/div/form/div[6]/div/div/div/textarea").send_keys(search_key)

    def button_add_qr(self):
        self.locator("xpath", "//*[@id='app']/section/div/div[3]/div/div/div[3]/span/button[2]").click()
        self.wait(3)

    # 查询任务
    def search_rwmc(self, search_key):
        self.locator("xpath", "//*[@id='app']/section/div/div[1]/div/form/div[1]/div/div/div/input").clear()
        self.locator("xpath", "//*[@id='app']/section/div/div[1]/div/form/div[1]/div/div/div/input").send_keys(search_key)

    def search_rwlx(self, search_key):
        self.locator("xpath", "//*[@id='app']/section/div/div[1]/div/form/div[2]/div/div/div/input").send_keys(search_key)
        self.wait(2)
        self.down_keys()
        self.enter_keys()

    def button_search(self):
        self.locator("xpath", "//*[@id='app']/section/div/div[1]/div/form/div[3]/div/button[1]").click()
        self.wait(3)

    def button_refresh(self):
        self.locator("xpath", "//*[@id='app']/section/div/div[1]/div/form/div[3]/div/button[2]").click()

    # 停用/启用/编辑/删除
    def button_switch(self):
        self.locator("xpath", "//*[@id='app']/section/div/div[2]/div/div[2]/div/div/div[2]/div[2]/table/tbody/tr/td[10]/div/button[3]/i").click()
        self.wait(3)
        self.enter_keys()
        self.wait(2)

    def button_edit(self):
        self.locator("xpath", "//*[@id='app']/section/div/div[2]/div/div[2]/div/div/div[2]/div[2]/table/tbody/tr/td[10]/div/button[1]").click()

    def edit_rwmc(self, search_key):
        self.locator("xpath", "//*[@id='app']/section/div/div[3]/div/div/div[2]/div/form/div[2]/div/div/div/input").send_keys(search_key)

    def button_delete(self):
        self.locator("xpath", "//*[@id='app']/section/div/div[2]/div/div[2]/div/div/div[2]/div[2]/table/tbody/tr/td[10]/div/button[2]").click()

    def windows_enter(self):
        self.locator("xpath", "/html/body/div[6]/div").send_keys(Keys.ENTER)






