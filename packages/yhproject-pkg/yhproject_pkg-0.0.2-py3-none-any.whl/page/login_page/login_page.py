# 从关键字文件导入基类
from yhproject_pkg.framework.key_word.keyword_web import WebKeys


class LoginPage(WebKeys):
    # 输入账号
    def input_user(self, search_key):
        self.locator("id", "user").clear()
        self.wait(2)
        self.locator("id", "user").send_keys(search_key)

    # 清空账号
    def clear_user(self):
        self.locator("id", "user").clear()

    # 输入密码
    def input_password(self, search_key):
        self.locator("id", "password").send_keys(search_key)

    # 清空密码
    def clear_password(self):
        self.locator("id", "password").clear()

    # 记住我
    def button_remember(self):
        self.locator("xpath", "/html/body/section/section/div[2]/div[2]/div[1]/label[2]").click()

    # 登录
    def button_login(self):
        self.locator("xpath", "/html/body/section/section/div[2]/div[2]/div[5]/button").click()
        self.wait(2)

    # 点击用户
    def button_user(self):
        self.locator("xpath", "/html/body/section/div/section[1]/div[2]/div[2]/span").click()
        self.wait(2)

