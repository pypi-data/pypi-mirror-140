# 从关键字文件导入基类

from yhproject_pkg.framework.key_word.keyword_web import WebKeys
import pyautogui


class JkcjPage(WebKeys):
    # 创建接口
    def button_add(self):
        self.locator("xpath", "//*[@id='app']/section/div/div[2]/div/div[1]/button").click()
        self.wait(3)
        self.locator("xpath", "//*[@id='app']/section/div/div[2]/div/div[4]/div[1]/div/div[2]/div/span/p").click()
        self.wait(3)

    def input_sjymc(self, words_key):
        self.locator("xpath", "//*[@id='app']/section/div/div[2]/div/div[4]/div[1]/div/div[2]/div/form/div[1]/div[2]/div/div[1]/div/div/div/input").send_keys(words_key)
        self.down_keys()
        self.wait(2)
        self.enter_keys()
        self.wait(2)

    def input_sjbmc(self, words_key):
        self.locator("xpath", "//*[@id='app']/section/div/div[2]/div/div[4]/div[1]/div/div[2]/div/form/div[1]/div[2]/div/div[2]/div/input").send_keys(words_key)
        self.down_keys()
        self.wait(2)
        self.enter_keys()
        self.wait(2)

    def drog_aa(self):
        pyautogui.moveTo(x=400, y=800, duration=1, tween=pyautogui.linear)  # 移动鼠标
        pyautogui.dragTo(x=1000, y=600, duration=1, button='left')

        pyautogui.moveTo(x=400, y=900, duration=1, tween=pyautogui.linear)  # 移动鼠标
        pyautogui.dragTo(x=1000, y=600, duration=1, button='left')

        pyautogui.moveTo(x=400, y=1000, duration=1, tween=pyautogui.linear)  # 移动鼠标
        pyautogui.dragTo(x=1000, y=600, duration=1, button='left')

    def button_jkcs1(self):
        el_jkcs1 = self.locator("xpath", "//*[@id='app']/section/div/div[2]/div/div[4]/div[1]/div/div[2]/div/form/div[2]/div/div[2]/div[1]/div/button[4]")
        el_jkcs1.click()
        self.wait(2)

    def button_jkcs2(self):
        pyautogui.click(1500, 440)
        self.wait(2)

    def input_jkbm(self, words_key):
        self.locator("xpath", "//*[@id='app']/section/div/div[2]/div/div[4]/div[1]/div/div[2]/div/form/div[3]/div[1]/div/div/div/div[1]/input").send_keys(words_key)
        self.wait(2)

    def input_jkmc(self, words_key):
        self.locator("xpath", "//*[@id='app']/section/div/div[2]/div/div[4]/div[1]/div/div[2]/div/form/div[3]/div[3]/div/div/div/div[1]/input").send_keys(words_key)
        self.wait(2)

    def input_ywzt(self):
        self.locator("xpath", "//*[@id='app']/section/div/div[2]/div/div[4]/div[1]/div/div[2]/div/form/div[3]/div[4]/div/div/div/div/div[1]/div[1]/div[2]/input").click()
        self.enter_keys()
        self.wait(2)

    def input_jkms(self, words_key):
        self.locator("xpath", "//*[@id='app']/section/div/div[2]/div/div[4]/div[1]/div/div[2]/div/form/div[3]/div[5]/div/div/div/div/textarea").send_keys(words_key)

    def button_save(self):
        self.locator("xpath", "//*[@id='app']/section/div/div[2]/div/div[4]/div[1]/div/div[3]/div/button[2]").click()

    # 接口查询
    def input_seach_jkmc(self, search_key):
        self.locator("xpath", "//*[@id='app']/section/div/div[1]/div/form/div[1]/div/div/input").send_keys(search_key)

    def button_search(self):
        self.locator("xpath", "//*[@id='app']/section/div/div[1]/div/form/button[1]/span").click()
        self.wait(3)

    def button_reset(self):
        self.locator("xpath", "//*[@id='app']/section/div/div[1]/div/form/button[2]").click()

    # 接口测试
    def button_test(self):
        self.locator("xpath", "//*[@id='app']/section/div/div[2]/div/div[2]/div[4]/div[2]/table/tbody/tr/td[8]/div/button[2]/span").click()
        self.wait(2)

    def button_apitest(self):
        self.locator("xpath", "//*[@id='app']/section/div/div[2]/div/div[4]/div/div[2]/div/div/div/form/div/div[2]/div/div[7]/div/span[2]/button").click()
        self.wait(2)

    def input_edit_jkms(self, words_key):
        self.locator("xpath", "//*[@id='app']/section/div/div[2]/div/div[4]/div/div[2]/div/div/div/form/div/div[2]/div/div[10]/div/div/textarea").send_keys(words_key)

    def button_edit_save(self):
        self.locator("xpath", "//*[@id='app']/section/div/div[2]/div/div[4]/div/div[2]/div/div/div/form/div/div[2]/div/div[11]/button[1]").click()

    def button_edit_back(self):
        self.locator("xpath", "//*[@id='app']/section/div/div[2]/div/div[4]/div/div[2]/div/div/div/form/div/div[2]/div/div[11]/button[2]").click()
        self.wait(2)

    # 接口提交
    def button_submit(self):
        self.locator("xpath", "//*[@id='app']/section/div/div[2]/div/div[2]/div[4]/div[2]/table/tbody/tr[1]/td[8]/div/button[1]/span/i").click()
        self.wait(2)