# 从关键字文件导入基类
from yhproject_pkg.framework.key_word.keyword_web import WebKeys
import pyautogui


class FlglPage(WebKeys):
    # 新增分类
    def button_add(self):
        self.locator("xpath", "//*[@id='app']/section/div/div[1]/div/div/div[1]/button").click()

    def input_flmc(self, words_key):
        self.locator("xpath", "//*[@id='app']/section/div/div[3]/div/div/div[2]/form/div[1]/div/div[1]/input").send_keys(words_key)

    def input_flcj(self, words_key):
        self.locator("xpath", "//*[@id='app']/section/div/div[3]/div/div/div[2]/form/div[2]/div/div/div/input").send_keys(words_key)
        self.wait(2)
        self.down_keys()
        self.wait(2)
        self.enter_keys()

    def button_flqr(self):
        self.locator("xpath", "//*[@id='app']/section/div/div[3]/div/div/div[3]/span/button[2]").click()
        self.wait(1)

    # 关键字搜索
    def input_treesearch(self, search_key):
        self.locator("xpath", "//*[@id='app']/section/div/div[1]/div/div/div[2]/div[1]/input").clear()
        self.wait(1)
        self.locator("xpath", "//*[@id='app']/section/div/div[1]/div/div/div[2]/div[1]/input").send_keys(search_key)
        self.wait(2)

    def icon_add(self):
        pyautogui.click(694, 554)
        self.wait(3)
        pyautogui.click(710, 620)
        self.wait(2)

    def icon_edit(self):
        pyautogui.click(737, 605)
        self.wait(3)
        pyautogui.click(807, 670)
        self.wait(2)

    def icon_remove(self):
        pyautogui.click(737, 605)
        self.wait(3)
        pyautogui.click(750, 723)
        self.wait(2)
        self.enter_keys()
        self.wait(1)

    def icon_sremove(self):
        pyautogui.click(739, 558)
        self.wait(3)
        pyautogui.click(805, 673)
        self.wait(2)
        self.enter_keys()
        self.wait(1)

    def icon_flmc(self):
        self.locator("xpath", "//*[@id='app']/section/div/div[1]/div/div/div[2]/div[2]/div[15]/div[1]/div/span").click()
        self.wait(3)

    # 分类明细
    def button_sjadd(self):
        self.locator("xpath", "//*[@id='app']/section/div/div[2]/div/div/div/div/div/div/div[1]/div[1]/button[1]").click()
        self.wait(3)

    def button_sjremove(self):
        self.locator("xpath", "//*[@id='app']/section/div/div[2]/div/div/div/div/div/div/div[1]/div[1]/button[2]").click()
        self.wait(2)
        self.enter_keys()
        self.wait(2)

    def input_sjflmc(self, word_keys):
        self.locator("xpath", "//*[@id='app']/section/div/div[2]/div/div/div/div/div/div/div[4]/div/div/div[2]/form/div[1]/div/div[1]/input").send_keys(word_keys)
        self.wait(1)
        self.up_keys()
        self.enter_keys()
        self.wait(1)

    def input_sjyjfl(self, word_keys):
        self.locator("xpath", "//*[@id='app']/section/div/div[2]/div/div/div/div/div/div/div[4]/div/div/div[2]/form/div[2]/div/div/div/input").send_keys(word_keys)
        self.wait(1)
        self.up_keys()
        self.enter_keys()
        self.wait(1)

    def input_sjejfl(self, word_keys):
        self.locator("xpath", "//*[@id='app']/section/div/div[2]/div/div/div/div/div/div/div[4]/div/div/div[2]/form/div[3]/div/div[1]/div/input").send_keys(word_keys)
        self.wait(1)
        self.up_keys()
        self.enter_keys()
        self.wait(1)

    def input_sjsjsyz(self):
        self.locator("xpath", "//*[@id='app']/section/div/div[2]/div/div/div/div/div/div/div[4]/div/div/div[2]/form/div[4]/div/div/div/input").click()
        self.wait(1)
        self.up_keys()
        self.enter_keys()
        self.wait(1)

    def input_sjtext(self, word_keys):
        self.locator("xpath", "//*[@id='app']/section/div/div[2]/div/div/div/div/div/div/div[4]/div/div/div[2]/form/div[5]/div/div[1]/textarea").send_keys(word_keys)
        self.wait(2)

    def button_sjqr(self):
        self.locator("xpath", "//*[@id='app']/section/div/div[2]/div/div/div/div/div/div/div[4]/div/div/div[3]/span/button[2]").click()
        self.wait(1)

    def input_sjsearch(self, search_key):
        self.locator("xpath", "//*[@id='app']/section/div/div[2]/div/div/div/div/div/div/div[1]/div[2]/input").send_keys(search_key)
        self.wait(2)

    def button_sjsearch(self):
        self.locator("xpath", "//*[@id='app']/section/div/div[2]/div/div/div/div/div/div/div[1]/button[1]/span").click()
        self.wait(2)

    def icon_boxcheck(self):
        self.locator("xpath", "//*[@id='app']/section/div/div[2]/div/div/div/div/div/div/div[2]/div[4]/div[2]/table/tbody/tr[1]/td[1]/div/label/span/span").click()

    def icon_sjedit(self):
        self.locator("xpath", "//*[@id='app']/section/div/div[2]/div/div/div/div/div/div/div[2]/div[5]/div[2]/table/tbody/tr[1]/td[10]/div/button[1]").click()
        self.wait(2)

    def button_sjreset(self):
        self.locator("xpath", "//*[@id='app']/section/div/div[2]/div/div/div/div/div/div/div[1]/button[2]").click()

    def icon_sjremove(self):
        self.locator("xpath", "//*[@id='app']/section/div/div[2]/div/div/div/div/div/div/div[2]/div[5]/div[2]/table/tbody/tr[1]/td[10]/div/button[2]").click()
        self.wait(2)
        self.enter_keys()
        self.wait(1)
