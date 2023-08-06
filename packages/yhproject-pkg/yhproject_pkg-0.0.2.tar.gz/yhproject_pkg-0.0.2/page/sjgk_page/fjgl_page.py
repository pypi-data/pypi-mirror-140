from yhproject_pkg.framework.key_word.keyword_web import WebKeys


class FjglPage(WebKeys):
    def button_fjgl(self):
        self.locator("xpath", "//*[@id='tab-tab1']").click()
        self.wait(2)

    # 新建
    def button_sjadd(self):
        self.locator("xpath", "//*[@id='pane-tab1']/div/div/div/div[1]/div[1]/button[1]").click()
        self.wait(2)

    def input_sjlevel(self, words_key):
        self.locator("xpath", "//*[@id='pane-tab1']/div/div/div/div[4]/div/div/div[2]/form/div[1]/div/div/div/input").send_keys(words_key)
        self.wait(2)
        self.up_keys()
        self.enter_keys()

    def input_sjlevelname(self, words_key):
        self.locator("xpath", "//*[@id='pane-tab1']/div/div/div/div[4]/div/div/div[2]/form/div[2]/div/div/input").send_keys(words_key)
        self.wait(2)

    def input_sjleveldetail(self, words_key):
        self.locator("xpath", "//*[@id='pane-tab1']/div/div/div/div[4]/div/div/div[2]/form/div[3]/div/div[1]/input").send_keys(words_key)

    def input_sjremark(self, words_key):
        self.locator("xpath", "//*[@id='pane-tab1']/div/div/div/div[4]/div/div/div[2]/form/div[4]/div/div/input").send_keys(words_key)
        self.wait(2)

    def button_sjqr(self):
        self.locator("xpath", "//*[@id='pane-tab1']/div/div/div/div[4]/div/div/div[3]/span/button[2]").click()
        self.wait(1)

    # 编辑
    def button_sjedit(self):
        self.locator("xpath", "//*[@id='pane-tab1']/div/div/div/div[2]/div[5]/div[2]/table/tbody/tr/td[9]/div/button[1]").click()
        self.wait(2)

    # 删除
    def button_remove(self):
        self.locator("xpath", "//*[@id='pane-tab1']/div/div/div/div[2]/div[5]/div[2]/table/tbody/tr/td[9]/div/button[2]").click()
        self.wait(2)
        self.enter_keys()
        self.wait(2)

    # 查询
    def input_search(self, word_keys):
        self.locator("xpath", "//*[@id='pane-tab1']/div/div/div/div[1]/div[2]/input").send_keys(word_keys)
        self.wait(2)
        self.locator("xpath", "//*[@id='pane-tab1']/div/div/div/div[1]/button[1]").click()
        self.wait(2)

    def button_reset(self):
        self.locator("xpath", "//*[@id='pane-tab1']/div/div/div/div[1]/button[2]").click()
        self.wait(2)

    # 版本管理
    def button_vermg(self):
        self.locator("xpath", "//*[@id='tab-tab2']").click()
        self.wait(3)

    def button_veradd(self):
        self.locator("xpath", "//*[@id='pane-tab2']/div/div/div/div[1]/div[1]/button[1]").click()

    def input_verid(self, word_keys):
        self.locator("xpath", "//*[@id='pane-tab2']/div/div/div/div[4]/div/div/div[2]/form/div[1]/div[1]/div/div/div[1]/input").send_keys(word_keys)

    def input_vername(self, word_keys):
        self.locator("xpath", "//*[@id='pane-tab2']/div/div/div/div[4]/div/div/div[2]/form/div[1]/div[2]/div/div/div[1]/input").send_keys(word_keys)

    def input_vertext(self, word_keys):
        self.locator("xpath","//*[@id='pane-tab2']/div/div/div/div[4]/div/div/div[2]/form/div[2]/div/div[1]/input").send_keys(word_keys)
        self.wait(2)

    def button_addline(self):
        self.locator("xpath", "//*[@id='pane-tab2']/div/div/div/div[4]/div/div/div[2]/form/div[4]/div/button").click()
        self.wait(2)

    def input_mglevelid(self, word_keys):
        self.locator("xpath", "//*[@id='pane-tab2']/div/div/div/div[4]/div/div/div[2]/form/div[5]/div/div/div[3]/table/tbody/tr/td[2]/div/div/div/div/div/div/input").send_keys(word_keys)
        self.wait(1)
        self.up_keys()
        self.enter_keys()

    def input_mglevelname(self, word_keys):
        self.locator("xpath", "//*[@id='pane-tab2']/div/div/div/div[4]/div/div/div[2]/form/div[5]/div/div/div[3]/table/tbody/tr/td[3]/div/div/div/div/div[1]/input").send_keys(word_keys)

    def input_mgleveldetail(self, word_keys):
        self.locator("xpath", "//*[@id='pane-tab2']/div/div/div/div[4]/div/div/div[2]/form/div[5]/div/div/div[3]/table/tbody/tr/td[4]/div/div/div/div/div[1]/input").send_keys(word_keys)

    def box_checkture(self):
        self.locator("xpath", "//*[@id='pane-tab2']/div/div/div/div[4]/div/div/div[2]/form/div[5]/div/div/div[3]/table/tbody/tr/td[6]/div/button[1]").click()

    def input_mglevelid1(self, word_keys):
        self.locator("xpath", "//*[@id='pane-tab2']/div/div/div/div[4]/div/div/div[2]/form/div[5]/div/div/div[3]/table/tbody/tr[2]/td[2]/div/div/div/div/div/div/input").send_keys(word_keys)
        self.wait(1)
        self.up_keys()
        self.enter_keys()

    def input_mglevelname1(self, word_keys):
        self.locator("xpath", "//*[@id='pane-tab2']/div/div/div/div[4]/div/div/div[2]/form/div[5]/div/div/div[3]/table/tbody/tr[2]/td[3]/div/div/div/div/div[1]/input").send_keys(word_keys)

    def input_mgleveldetail1(self, word_keys):
        self.locator("xpath", "//*[@id='pane-tab2']/div/div/div/div[4]/div/div/div[2]/form/div[5]/div/div/div[3]/table/tbody/tr[2]/td[4]/div/div/div/div/div[1]/input").send_keys(word_keys)

    def box_checkture1(self):
        self.locator("xpath", "//*[@id='pane-tab2']/div/div/div/div[4]/div/div/div[2]/form/div[5]/div/div/div[3]/table/tbody/tr[2]/td[6]/div/button[1]").click()

    def button_levelqr(self):
        self.locator("xpath", "//*[@id='pane-tab2']/div/div/div/div[4]/div/div/div[3]/span/button[2]").click()
        self.wait(2)

    def input_mgsearch(self, search_key):
        self.locator("xpath", "//*[@id='pane-tab2']/div/div/div/div[1]/div[2]/input").send_keys(search_key)
        self.wait(2)
        self.locator("xpath", "//*[@id='pane-tab2']/div/div/div/div[1]/button[1]").click()
        self.wait(2)

    def button_mgreset(self):
        self.locator("xpath", "//*[@id='pane-tab2']/div/div/div/div[1]/button[2]").click()

    # 开关切换
    def button_switch(self):
        self.locator("xpath", "//*[@id='pane-tab2']/div/div/div/div[2]/div[5]/div[2]/table/tbody/tr/td[10]/div/button[1]/span").click()
        self.wait(2)
        self.enter_keys()
        self.wait(2)

    # 编辑
    def button_veredit(self):
        self.locator("xpath", "//*[@id='pane-tab2']/div/div/div/div[2]/div[5]/div[2]/table/tbody/tr/td[10]/div/button[2]").click()
        self.wait(2)

    def button_verremove(self):
        self.locator("xpath", "//*[@id='pane-tab2']/div/div/div/div[2]/div[5]/div[2]/table/tbody/tr/td[10]/div/button[3]").click()
        self.wait(2)








