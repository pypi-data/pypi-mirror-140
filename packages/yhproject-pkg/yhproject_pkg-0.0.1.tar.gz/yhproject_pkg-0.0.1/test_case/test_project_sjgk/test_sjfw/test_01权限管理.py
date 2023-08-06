import pytest
import pyautogui
from yhproject_pkg.framework.data_driver.yaml_driver import load_yaml
from yhproject_pkg.framework.page.login_page.login_page import LoginPage
from yhproject_pkg.framework.page.login_page.menu_page import MenuPage
from yhproject_pkg.framework.page.sjfw_page.qxgl_page import QxglPage
import allure
import logging

logger = logging.getLogger(__name__)


@allure.feature('权限管理')
@allure.title('登录')
@pytest.mark.run(order=15)
@pytest.mark.parametrize('data', load_yaml('../../data/login/login1.yaml'))
def test_login_gxgl(browser, data):
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
    logger.info('------------进入权限管理管理模块-------------')


@allure.feature('权限管理')
@pytest.mark.parametrize('data', load_yaml('../../data/login/menu.yaml'))
@pytest.mark.run(order=16)
@allure.title('打开菜单_权限管理')
def test_menu_qxgl(browser, data):
    page = MenuPage(browser)
    page.table_manage()
    page.menu_icon()
    page.menu_sjfw()
    page.sjfw_sjfw_qxgl()
# 切换iframe
    page.sjfw_qxgl_iframe()
    page.assert_att("用户名")
    logger.info('01打开菜单')


@allure.feature('权限管理')
@pytest.mark.parametrize('data', load_yaml('../../data/sjfw/qxgl.yaml'))
@pytest.mark.run(order=17)
@allure.title('查询用户')
def test_qxgl_search(browser, data):
    page = QxglPage(browser)
    page.input_user(data["user"])
    page.wait(2)
    page.assert_att("huxiaofeng")
    page.button_refresh()
    page.input_user("error")
    page.assert_att("暂无数据")
    page.button_refresh()
    logger.info("02授权用户查询成功")


@allure.feature('权限管理')
@pytest.mark.parametrize('data', load_yaml('../../data/sjfw/qxgl.yaml'))
@pytest.mark.run(order=18)
@allure.title('授权用户')
def test_qxgl_jksq(browser, data):
    page = QxglPage(browser)
    page.input_user(data["user"])
    page.button_jksq()
    page.assert_att("接口列表")
    page.box_alljk()
    page.button_sq()
    page.box_allsq()
    page.button_qxsq()
    page.input_jkls(data["jkls"])
    page.box_jkls()
    page.button_sq()
    page.box_sqls()
    page.button_qxsq()
    page.button_qr()
    logger.info("03授权/取消授权成功")


@allure.feature('权限管理')
@allure.title('退出登录')
def test_qxgl_logout(browser):
    page = LoginPage(browser)
    page.reback_iframe()
    page.button_user()
    pyautogui.click(2428, 391)
    page.wait(2)
    page.assert_att("赢和数据")
    logger.info('.....退出登录.....')

