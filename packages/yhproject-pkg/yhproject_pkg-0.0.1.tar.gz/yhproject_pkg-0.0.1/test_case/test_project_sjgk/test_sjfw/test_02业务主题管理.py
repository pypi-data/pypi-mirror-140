import pytest
import pyautogui
from yhproject_pkg.framework.data_driver.yaml_driver import load_yaml
from yhproject_pkg.framework.page.login_page.login_page import LoginPage
from yhproject_pkg.framework.page.login_page.menu_page import MenuPage
from yhproject_pkg.framework.page.sjfw_page.ywztgl_page import YwztglPage
import allure
import logging

logger = logging.getLogger(__name__)


@allure.feature('业务主题管理')
@allure.title('登录')
@pytest.mark.parametrize('data', load_yaml('../../data/login/login1.yaml'))
def test_login_ztgl(browser, data):
    page = LoginPage(browser)
    page.open(data["url"])
    page.driver.maximize_window()
    page.input_user(data["user"])
    page.input_password(data["password"])
    page.button_remember()
    page.button_login()
# 登录跳转
    page.switch_window(-1)
    page.assert_att("赢和数据")
    logger.info('------------进入业务主题管理模块-------------')


@allure.feature('业务主题管理')
@pytest.mark.parametrize('data', load_yaml('../../data/login/menu.yaml'))
@allure.title('打开菜单_业务主题管理')
def test_menu_ztgl(browser, data):
    page = MenuPage(browser)
    page.table_manage()
    page.menu_icon()
    page.menu_sjfw()
    page.sjfw_sjfw_ywztgl()
    logger.info('业务主题管理_打开菜单')
    # 切换iframe
    page.sjfw_yeztgl_iframe()
    page.assert_att("主题名称")
    logger.info('01进入菜单')


@allure.feature('业务主题管理')
@pytest.mark.parametrize('data', load_yaml('../../data/sjfw/ywztgl.yaml'))
@allure.title('新增业务主题')
def test_ztgl_add(browser, data):
    page = YwztglPage(browser)
    page.button_add()
    page.input_ztmc(data["ztmc001"])
    page.input_order(data["order001"])
    page.input_ztms(data["ztms001"])
    page.button_qr()
    page.assert_att('操作成功')
    logger.info("02新增主题成功")


@allure.feature('业务主题管理')
@pytest.mark.parametrize('data', load_yaml('../../data/sjfw/ywztgl.yaml'))
@allure.title('查询业务主题')
def test_ztgl_search(browser, data):
    page = YwztglPage(browser)
    page.input_search("error")
    page.assert_att("暂无数据")
    page.button_reset()
    page.input_search(data["ztmc001"])
    page.assert_att(data["ztmc001"])
    logger.info("业务主题管理管理_查询成功")


@allure.feature('业务主题管理')
@pytest.mark.parametrize('data', load_yaml('../../data/sjfw/ywztgl.yaml'))
@allure.title('编辑业务主题')
def test_ztgl_edit(browser, data):
    page = YwztglPage(browser)
    page.button_edit()
    page.input_ztms('s')
    page.button_qr()
    page.assert_att(data["ztms001"]+'s')
    logger.info("04编辑业务主题成功")


@allure.feature('业务主题管理')
@pytest.mark.parametrize('data', load_yaml('../../data/sjfw/ywztgl.yaml'))
@allure.title('删除业务主题')
def test_ztgl_remove(browser, data):
    page = YwztglPage(browser)
    page.button_remove()
    page.enter_keys()
    page.assert_att("暂无数据")
    logger.info("05删除主题成功")


@allure.feature('业务主题管理')
@allure.title('退出登录')
def test_ywztgl_logout(browser):
    page = LoginPage(browser)
    page.reback_iframe()
    page.button_user()
    pyautogui.click(2428, 391)
    page.wait(2)
    page.assert_att("赢和数据")
    logger.info('.....退出登录.....')



