# 从关键字文件导入基类
from yhproject_pkg.framework.key_word.keyword_web import WebKeys


class JkspPage(WebKeys):
    def input_search(self, words_key):
        self.locator("xpath", "//*[@id='app']/section/div/div[1]/div/form/div[1]/div/div/input").send_keys(words_key)
        self.wait(3)
        self.locator("xpath", "//*[@id='app']/section/div/div[1]/div/form/button[1]").click()
        self.wait(3)

    def button_reset(self):
        self.locator("xpath", "//*[@id='app']/section/div/div[1]/div/form/button[2]").click()
        self.wait(3)

    def button_tabcheck(self):
        self.locator("xpath", "//*[@id='tab-tabCheck']").click()

    def button_tabreviewed(self):
        self.locator("xpath", "//*[@id='tab-tabReviewed']").click()

    def button_check(self):
        el = self.locator("xpath", "//*[@id='app']/section/div/div[2]/div/div/div[2]/div[3]/div[4]/div[2]/table/tbody/tr/td[7]/div/button[1]/span/i")
        self.driver.execute_script('arguments[0].click();', el)  # 直接点击不可见的目标元素，不再先跳转。
        self.wait(2)

    def button_check_false(self):
        self.locator("xpath", "/html/body/div[2]/div/div[3]/button[1]").click()
        self.wait(5)

    def button_check_ture(self):
        self.locator("xpath", "/html/body/div[2]/div/div[3]/button[2]").click()
        self.wait(5)

