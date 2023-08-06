import pytest
from selenium import webdriver
import allure
# 作者-上海悠悠 QQ交流群:717225969
# blog地址 https://www.cnblogs.com/yoyoketang/

def test_login(browser):
    with allure.step("step1：打开登录首页"):
        browser.get("http://www.manongjc.com/detail/14-pcbktsxmwrmyvrx.html")
    # 故意断言失败，看是否会截图
    assert browser.title == "悠悠"