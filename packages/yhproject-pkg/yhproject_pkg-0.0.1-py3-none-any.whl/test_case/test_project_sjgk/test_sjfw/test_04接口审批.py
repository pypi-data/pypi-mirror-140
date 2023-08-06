import pytest
import pyautogui
from yhproject_pkg.framework.data_driver.yaml_driver import load_yaml
from yhproject_pkg.framework.page.login_page.login_page import LoginPage
from yhproject_pkg.framework.page.login_page.menu_page import MenuPage
from yhproject_pkg.framework.page.sjfw_page.jksp_page import JkspPage
import allure
import logging

logger = logging.getLogger(__name__)


@allure.feature('接口审批')
@allure.title('登录')
@pytest.mark.parametrize('data', load_yaml('../../data/login/login1.yaml'))
def test_login_jksp(browser, data):
    page = LoginPage(browser)
    page.driver.maximize_window()
    page.open(data["url"])
    page.input_user(data["user"])
    page.input_password(data["password"])
    page.button_remember()
    page.button_login()
# 登录跳转
    page.switch_window(-1)
    page.assert_att("赢和数据")
    logger.info("接口审批_登录成功")


@allure.feature('接口审批')
@pytest.mark.parametrize('data', load_yaml('../../data/login/menu.yaml'))
@allure.title('打开菜单_接口审批')
def test_menu_jksp(browser, data):
    page = MenuPage(browser)
    page.table_manage()
    page.menu_icon()
    page.menu_sjfw()
    page.sjfw_sjfw_jksp()
    logger.info('打开菜单_接口审批')
    # 切换iframe
    page.sjfw_jksp_iframe()
    logger.info('进入审批接口模块')
    page.assert_att("审批类型")


@allure.feature('接口审批')
@pytest.mark.parametrize('data', load_yaml('../../data/sjfw/cjjk.yaml'))
@allure.title('查询接口')
def test_jksp_search(browser, data):
    page = JkspPage(browser)
    page.input_search('error')
    page.assert_att('暂无数据')
    page.button_reset()
    page.input_search(data['jkmc1'])
    page.assert_att(data['jkmc1'])
    page.wait(3)
    logger.info("接口审批_查询接口正常")


@allure.feature('接口审批')
@pytest.mark.parametrize('data', load_yaml('../../data/sjfw/cjjk.yaml'))
@allure.title('审核接口')
def test_jksp_check(browser, data):
    page = JkspPage(browser)
    page.button_reset()
    page.input_search(data['jkmc1'])
    page.wait(3)
    page.button_check()
    page.button_check_false()
    page.assert_att("暂无数据")
    page.button_reset()
    page.input_search(data['jkmc2'])
    page.button_check()
    page.button_check_ture()
    page.assert_att("暂无数据")
    page.button_tabreviewed()
    page.input_search(data['jkmc1'])
    page.assert_att("不通过")
    page.button_reset()
    page.input_search(data['jkmc2'])
    page.assert_att("通过")
    logger.info("接口审批_审批通过与否")


@allure.feature('接口审批')
@allure.title('退出登录')
def test_jksp_logout(browser):
    page = LoginPage(browser)
    page.reback_iframe()
    page.button_user()
    pyautogui.click(2428, 391)
    page.wait(2)
    page.assert_att("赢和数据")
    logger.info('.....退出登录.....')





