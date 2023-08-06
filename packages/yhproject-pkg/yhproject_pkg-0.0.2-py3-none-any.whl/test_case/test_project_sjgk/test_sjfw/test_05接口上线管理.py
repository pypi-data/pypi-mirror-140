import pytest
import pyautogui
from yhproject_pkg.framework.data_driver.yaml_driver import load_yaml
from yhproject_pkg.framework.page.login_page.login_page import LoginPage
from yhproject_pkg.framework.page.login_page.menu_page import MenuPage
from yhproject_pkg.framework.page.sjfw_page.jksxgl_page import JksxglPage
import allure
import logging

logger = logging.getLogger(__name__)


@allure.feature('接口上线管理')
@allure.title('登录')
@pytest.mark.parametrize('data', load_yaml('../../data/login/login1.yaml'))
def test_login_jksxgl(browser, data):
    page = LoginPage(browser)
    page.driver.maximize_window()
    page.open(data["url"])
    page.wait(3)
    page.input_user(data["user"])
    page.input_password(data["password"])
    page.button_remember()
    page.button_login()
    page.wait(2)
# 登录跳转
    page.switch_window(-1)
    page.assert_att("赢和数据")
    logger.info("接口上线管理_登录成功")


@allure.feature('接口上线管理')
@pytest.mark.parametrize('data', load_yaml('../../data/login/menu.yaml'))
@allure.title('打开菜单_接口上线管理')
def test_menu_jksxgl(browser, data):
    page = MenuPage(browser)
    page.table_manage()
    page.menu_icon()
    page.menu_sjfw()
    page.sjfw_sjfw_jksxgl()
    logger.info('打开菜单_接口上线管理')
    # 切换iframe
    page.sjfw_jksxgl_iframe()
    logger.info('进入接口上线管理模块')
    page.assert_att("状态")


@allure.feature('接口上线管理')
@pytest.mark.parametrize('data', load_yaml('../../data/sjfw/cjjk.yaml'))
@allure.title('查询接口')
def test_jksxgl_search(browser, data):
    page = JksxglPage(browser)
    page.input_search('error')
    page.button_search()
    page.assert_att('暂无数据')
    page.button_reset()
    page.input_search(data['jkmc2'])
    page.button_search()
    page.assert_att(data['jkmc2'])
    logger.info("接口上线管理_查询接口正常")


@allure.feature('接口上线管理')
@allure.title('测试接口')
def test_jksxgl_select(browser):
    page = JksxglPage(browser)
    page.button_select()
    page.assert_att("API测试")
    page.button_apitest()
    page.assert_att('200')
    page.button_back()
    logger.info('接口上线管理_测试接口')


@allure.feature('接口上线管理')
@allure.title('接口上下线')
def test_jksxgl_line(browser):
    page = JksxglPage(browser)
    page.button_line()
    page.wait(3)
    page.enter_keys()
    page.assert_att("离线")
    page.button_line()
    page.wait(3)
    page.enter_keys()
    page.assert_att('上线')
    logger.info('接口上线管理_接口上下线')


@allure.feature('接口上线管理')
@allure.title('退出登录')
def test_jksxgl_logout(browser):
    page = LoginPage(browser)
    page.reback_iframe()
    page.button_user()
    pyautogui.click(2428, 391)
    page.wait(2)
    page.assert_att("赢和数据")
    logger.info('.....退出登录.....')






