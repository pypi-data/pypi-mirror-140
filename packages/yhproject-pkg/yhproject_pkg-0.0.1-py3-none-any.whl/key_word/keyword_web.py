import logging
from time import sleep
import os
import time
import win32api
import win32con
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys



# 构造工具包
class WebKeys():
    # 创建webdriver驱动
    def __init__(self, driver):
        self.driver = driver

    # 访问URL
    def open(self, url):
        self.driver.get(url)
        self.wait(2)

    # 退出
    def quit(self):
        self.driver.quit()

    # 元素定位
    def locator(self, name, value):
        return self.driver.find_element(name, value)

    def locators(self, name, value):
        return self.driver.find_elements(name, value)

    # 输入
    def input(self, name, value, txt):
        el = self.locator(name, value)
        el.clear()
        el.send_keys(txt)

    # 强制等待
    def wait(self, time_):
        sleep(time_)

    # 断言
    def assert_att(self, word):
        try:
            att = self.driver.find_element_by_xpath('//*[contains(text(),\"' + word + '\")]').text
            return True

        except AssertionError as e:
            logging.error("There is AssertError!")
            return False

    # 窗口切换
    def switch_window(self, n):
        self.driver.switch_to.window(self.driver.window_handles[n])

    # iframe切换
    def switch_iframe(self, name, value):
        self.driver.switch_to.frame(self.locator(name, value))

    # 释放iframe
    def reback_iframe(self):
        self.driver.switch_to.default_content()
        self.wait(2)

    # 截图方法
    def get_windows_img(self):
        file_path = os.path.dirname(os.path.abspath('')) + '/img/'  # 设置截图保存路径
        rq = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))  # 获取当前系统时间
        img_name = file_path + rq + '.png'  # 设置截图名称格式
        try:
            self.driver.get_screenshot_as_file(img_name)  # 指定截图存放路径和名称
            print("已将截图保存到文件夹/img/img")
        except NameError as e:
            print("截图保存失败! %s" % e)
            self.get_windows_img()

    # 模拟按键enter
    def enter_keys(self):
        ActionChains(self.driver).send_keys(Keys.ENTER).perform()
        self.wait(2)

    # 模拟按键下
    def down_keys(self):
        ActionChains(self.driver).send_keys(Keys.DOWN).perform()
        self.wait(1)

    # 模拟按键上
    def up_keys(self):
        ActionChains(self.driver).send_keys(Keys.UP).perform()
        self.wait(1)

    # 模拟回车键
    def backspace_keys(self):
        ActionChains(self.driver).send_keys(Keys.BACK_SPACE).perform()
        sleep(2)

    # 模拟全选键
    def allselect_keys(self):
        action = ActionChains(self.driver)
        action.key_down(Keys.CONTROL).send_keys('a').key_up(Keys.CONTROL)  # CTRL+A
        action.perform()  # 执行
        sleep(2)

    # 模拟鼠标中轴向下滚动
    def down_mouse(self):
        for i in range(1, 1500):
            win32api.mouse_event(win32con.MOUSEEVENTF_WHEEL, 0, 0, -1)
        sleep(1)

    # 模拟鼠标中轴向上滚动
    def up_mouse(self):
        for i in range(1, 1500):
            win32api.mouse_event(win32con.MOUSEEVENTF_WHEEL, 0, 0, 1)
        sleep(1)










