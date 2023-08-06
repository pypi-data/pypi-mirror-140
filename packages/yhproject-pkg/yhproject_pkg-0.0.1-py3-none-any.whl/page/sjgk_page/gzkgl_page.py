# 从关键字文件导入基类
from pynput.keyboard import Controller

from yhproject_pkg.framework.key_word.keyword_web import WebKeys


class GzkglPage(WebKeys):
    def button_add(self):
        self.locator("xpath", "//*[@id='app']/section/div/div[2]/div/div[1]/div[1]/button[1]").click()
        self.wait(2)

    def input_checktheme(self, key_words):
        self.locator("xpath", "//*[@id='app']/section/div/div[2]/div/div[4]/div/div/div[2]/form/div/div[1]/div[1]/div/div/div/input").send_keys(key_words)
        self.down_keys()
        self.enter_keys()
        self.wait(2)

    def input_checkmodule(self):
        self.locator("xpath", "//*[@id='app']/section/div/div[2]/div/div[4]/div/div/div[2]/form/div/div[1]/div[3]/div/div/div[1]/input").click()
        self.down_keys()
        self.enter_keys()
        self.wait(2)

    def input_checkclass(self):
        self.locator("xpath", "//*[@id='app']/section/div/div[2]/div/div[4]/div/div/div[2]/form/div/div[1]/div[4]/div/div/div/input").click()
        self.down_keys()
        self.enter_keys()
        self.wait(2)

    def input_checktitle(self, key_words):
        self.locator("xpath", "//*[@id='app']/section/div/div[2]/div/div[4]/div/div/div[2]/form/div/div[1]/div[5]/div/div[1]/input").send_keys(key_words)
        self.wait(2)

    def input_checkname(self, key_words):
        self.locator("xpath", "//*[@id='app']/section/div/div[2]/div/div[4]/div/div/div[2]/form/div/div[1]/div[6]/div/div/input").send_keys(key_words)
        self.wait(2)

    def input_checkrule(self, key_words):
        self.locator("xpath", "//*[@id='app']/section/div/div[2]/div/div[4]/div/div/div[2]/form/div/div[1]/div[7]/div/div[1]/input").send_keys(key_words)
        self.wait(2)

    def input_text(self, key_words):
        self.locator("xpath", "//*[@id='app']/section/div/div[2]/div/div[4]/div/div/div[2]/form/div/div[1]/div[9]/div/div/textarea").send_keys(key_words)
        self.wait(3)

    def core_switch(self):
        self.locator("xpath", "//*[@id='app']/section/div/div[2]/div/div[4]/div/div/div[2]/form/div/div[2]/div[2]/div[1]/div/div/span[1]").click()

    def input_sjwdsm(self, key_words):
        self.locator("xpath", "//*[@id='app']/section/div/div[2]/div/div[4]/div/div/div[2]/form/div/div[2]/div[2]/div[2]/div/div/input").send_keys(key_words)

    def icon_plus(self):
        self.locator("xpath", "//*[@id='app']/section/div/div[2]/div/div[4]/div/div/div[2]/form/div/div[2]/div[2]/div[3]/div/div/div[2]/table/thead/tr/th[4]/div/div").click()

    def input_wdsmora(self, key_words):
        self.locator("xpath", "//*[@id='app']/section/div/div[2]/div/div[4]/div/div/div[2]/form/div/div[2]/div[2]/div[3]/div/div/div[3]/table/tbody/tr/td[1]/div/div/div/div/div/div/input").send_keys(key_words)
        self.wait(2)
        self.down_keys()
        self.enter_keys()
        self.wait(3)

    def input_wdsmtable(self, key_words):
        self.locator("xpath", "//*[@id='app']/section/div/div[2]/div/div[4]/div/div/div[2]/form/div/div[2]/div[2]/div[3]/div/div/div[3]/table/tbody/tr/td[2]/div/div/div/div/div/div/input").send_keys(key_words)
        self.wait(2)
        self.down_keys()
        self.enter_keys()
        self.wait(3)

    def input_wdsmcol(self, key_words):
        self.locator("xpath", "//*[@id='app']/section/div/div[2]/div/div[4]/div/div/div[2]/form/div/div[2]/div[2]/div[3]/div/div/div[3]/table/tbody/tr/td[3]/div/div/div/div/div/div/input").send_keys(key_words)
        self.wait(2)
        self.down_keys()
        self.enter_keys()
        self.wait(3)

    def input_sos(self, key_words):
        self.locator("xpath", "//*[@id='app']/section/div/div[2]/div/div[4]/div/div/div[2]/form/div/div[2]/div[2]/div[4]/div/div/div/input").send_keys(key_words)
        self.wait(2)
        self.down_keys()
        self.enter_keys()
        self.wait(3)

    def input_dos(self, key_words):
        self.locator("xpath", "//*[@id='app']/section/div/div[2]/div/div[4]/div/div/div[2]/form/div/div[2]/div[2]/div[6]/div/div/div/input").send_keys(key_words)
        self.wait(2)
        self.down_keys()
        self.enter_keys()
        self.wait(3)

    def icon_pplus(self):
        self.locator("xpath", "//*[@id='app']/section/div/div[2]/div/div[4]/div/div/div[2]/form/div/div[2]/div[2]/div[8]/div/div/div[2]/table/thead/tr[2]/th[5]/div/div").click()

    def input_stable(self, key_words):
        self.locator("xpath", "//*[@id='app']/section/div/div[2]/div/div[4]/div/div/div[2]/form/div/div[2]/div[2]/div[8]/div/div/div[3]/table/tbody/tr/td[1]/div/div/div/div/div/div/input").send_keys(key_words)
        self.wait(2)
        self.down_keys()
        self.enter_keys()
        self.wait(3)

    def input_scol(self, key_words):
        self.locator("xpath", "//*[@id='app']/section/div/div[2]/div/div[4]/div/div/div[2]/form/div/div[2]/div[2]/div[8]/div/div/div[3]/table/tbody/tr/td[2]/div/div/div/div/div/div[1]/input").send_keys(key_words)
        self.wait(2)
        self.down_keys()
        self.enter_keys()
        self.wait(3)

    def input_dtable(self, key_words):
        self.locator("xpath", "//*[@id='app']/section/div/div[2]/div/div[4]/div/div/div[2]/form/div/div[2]/div[2]/div[8]/div/div/div[3]/table/tbody/tr/td[3]/div/div/div/div/div/div/input").send_keys(key_words)
        self.wait(2)
        self.down_keys()
        self.enter_keys()
        self.wait(3)

    def input_dcol(self, key_words):
        self.locator("xpath", "//*[@id='app']/section/div/div[2]/div/div[4]/div/div/div[2]/form/div/div[2]/div[2]/div[8]/div/div/div[3]/table/tbody/tr/td[4]/div/div/div/div/div/div/input").send_keys(key_words)
        self.wait(2)
        self.down_keys()
        self.enter_keys()
        self.wait(3)

    def button_nextstep(self):
        self.locator("xpath", "//*[@id='app']/section/div/div[2]/div/div[4]/div/div/div[3]/span/button[2]/span").click()
        self.wait(2)

    def local_sql(self):
        el = self.locator("xpath", "//*[@id='app']/section/div/div[2]/div/div[4]/div/div/div[2]/form/div/div[2]/div[3]/div[1]/div/div[2]/div/div[6]/div[1]/div/div/div/div[5]/div[4]/pre")
        el.click()
        self.wait(3)

    def input_sql(self, key_words):
        self.locator("xpath", "//*[@id='app']/section/div/div[2]/div/div[4]/div/div/div[2]/form/div/div[2]/div[3]/div[1]/div/div[2]/div/div[6]/div[1]/div/div/div/div[5]/div/pre").send_keys(key_words)

    def button_sumbit(self):
        self.locator("xpath", "//*[@id='app']/section/div/div[2]/div/div[4]/div/div/div[3]/span/button[3]").click()
        self.wait(2)

    def key_word(self):
        keyboard = Controller()
        keyboard.type('SELECT X.S_VALUE, X.D_VALUE, X.DIFF_VALUE '
                      'FROM (SELECT SUM(CASE TYPE WHEN 1 THEN 1 ELSE 0 END) AS S_VALUE,SUM(CASE TYPE WHEN 2 THEN 1 ELSE 0 END) AS D_VALUE,'
                      'SUM((CASE TYPE WHEN 2 THEN 1 ELSE 0 END) - (CASE TYPE WHEN 1 THEN 1 ELSE 0 END)) AS DIFF_VALUE FROM (SELECT 1 AS TYPE,V1.OS FROM TEST_S_BF_LOG_LOGIN1  V1 GROUP BY V1.OS '
                      'UNION ALL SELECT 2 AS TYPE,E1.OS  FROM TEST_S_BF_LOG_LOGIN1  E1 GROUP BY E1.OS ) T) X WHERE ABS(DIFF_VALUE) > 0')
        self.wait(5)

    def button_mhsql(self):
        self.locator("xpath", "//*[@id='app']/section/div/div[2]/div/div[4]/div/div/div[2]/form/div/div[2]/div[3]/div[1]/div/div[1]/button/span").click()
        self.wait(2)

    def input_search(self, key_words):
        self.locator("xpath", "//*[@id='app']/section/div/div[2]/div/div[1]/div[2]/input").clear()
        self.wait(2)
        self.locator("xpath", "//*[@id='app']/section/div/div[2]/div/div[1]/div[2]/input").send_keys(key_words)
        self.wait(2)
        self.locator("xpath", "//*[@id='app']/section/div/div[2]/div/div[1]/button").click()
        self.wait(2)

    def button_checkvalid(self):
        self.locator("xpath", "//*[@id='app']/section/div/div[2]/div/div[2]/div[5]/div[2]/table/tbody/tr[1]/td[18]/div/button[1]").click()
        self.wait(2)
        self.enter_keys()
        self.wait(2)

    def button_edit(self):
        self.locator("xpath", "//*[@id='app']/section/div/div[2]/div/div[2]/div[5]/div[2]/table/tbody/tr[1]/td[18]/div/button[2]").click()
        self.wait(2)

    def button_remove(self):
        self.locator("xpath", "//*[@id='app']/section/div/div[2]/div/div[2]/div[5]/div[2]/table/tbody/tr[1]/td[18]/div/button[3]").click()
        self.wait(2)
        self.enter_keys()
        self.wait(2)






