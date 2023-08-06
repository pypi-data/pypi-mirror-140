# import pytest
# from selenium import webdriver
# from framework.data_driver.yaml_driver import load_yaml
# from framework.page.demo_page0 import BaiduPage
#
#
#
#
# class TestLogin:
#     driver = webdriver.Chrome()
#
#     @pytest.mark.parametrize('data', load_yaml('../../data/demo/login_demo2.yaml'))
#     def test_login012(self,data,t):
#         page = BaiduPage(self.driver)
#         print("还在当前页面")
#         tpage.locator(data["name1"], data["value2"]).click()
#         page.wait(1)
#         print('测试3')
#
#
#
#
