
from yhproject_pkg.framework.data_driver.yaml_driver import load_yaml
from yhproject_pkg.framework.page.demo_page0 import BaiduPage
import pytest
import allure

@allure.feature('百度搜索')
# class TestBaidu():
#     @classmethod
#     def setup_class(cls):
#         cls.driver = webdriver.Chrome()

@allure.title('测试用例1')
@pytest.mark.parametrize('data', load_yaml('../../data/demo/login_demo1.yaml'))
@pytest.mark.run(order=1)
def test_login00(data, browser):
    browser.get(data['url'])
    page = BaiduPage(browser)
    page.driver.maximize_window()
    page.wait(5)
    print('打开浏览器成功')
    page.locator(data["name1"], data["value1"]).click()
    print('测试1')
    page.assert_att("huxiaofeng")

@allure.title('测试用例2')
@pytest.mark.parametrize('data', load_yaml('../../data/demo/login_demo1.yaml'))
@pytest.mark.run(order=2.1)
def test_login01(data, browser):
    page = BaiduPage(browser)
    page.locator(data["name1"], data["value4"]).click()
    page.wait(5)

@allure.title('测试用例3')
@pytest.mark.parametrize('data', load_yaml('../../data/demo/login_demo1.yaml'))
@pytest.mark.run(order=2.2)
def test_login02(data, browser):
    page = BaiduPage(browser)
    page.locator(data["name1"], data["value5"]).click()
    page.wait(5)

@allure.title('测试用例4')
@pytest.mark.parametrize('data', load_yaml('../../data/demo/login_demo1.yaml'))
@pytest.mark.run(order=3)
def test_loginxp(data, browser):
    page = BaiduPage(browser)
    page.locator(data["name1"], data["value6"]).click()
    page.wait(5)




