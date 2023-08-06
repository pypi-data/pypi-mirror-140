import pytest
import pyautogui
from yhproject_pkg.framework.data_driver.yaml_driver import load_yaml
from yhproject_pkg.framework.page.login_page.login_page import LoginPage
from yhproject_pkg.framework.page.login_page.menu_page import MenuPage
from yhproject_pkg.framework.page.sjkf_page.ddgl_page import DdglPage
import allure
import logging

logger = logging.getLogger(__name__)


@allure.feature('调度管理')
@allure.title('登录')
@pytest.mark.parametrize('data', load_yaml('../../data/login/login1.yaml'))
def test_login_ddgl(browser, data):
    page = LoginPage(browser)
    page.driver.maximize_window()
    page.open(data["url"])
    page.input_user(data["user"])
    page.input_password(data["password"])
    page.button_remember()
    page.button_login()
    page.wait(2)
# 登录跳转
    page.switch_window(-1)
    page.assert_att("赢和数据")
    logger.info('------------进入元调度管理模块-------------')


@allure.feature('调度管理')
@pytest.mark.parametrize('data', load_yaml('../../data/login/menu.yaml'))
@allure.title('打开菜单_调度管理')
def test_menu_ddgl(browser, data):
    page = MenuPage(browser)
    page.table_manage()
    page.menu_icon()
    page.menu_sjkf()
    page.sjkf_cjzx_ddgl()
    logger.info('打开菜单_调度管理')
# 切换iframe
    page.sjkf_ddgl_iframe()
    page.assert_att("任务名称")
    logger.info('01打开菜单_调度管理')


@allure.feature('调度管理')
@pytest.mark.parametrize('data', load_yaml('../../data/sjkf/ddgl.yaml'))
@allure.title('新增调度任务')
def test_ddgl_add(browser, data):
    page = DdglPage(browser)
    page.button_add()
    page.input_rwlx(data["rwlx"])
    page.input_rwmc(data["rwmc"])
    page.input_url(data["url"])
    page.input_qqlx(data["qqlx"])
    page.input_jjrzx()
    page.input_rwms(data["rwms"])
    page.button_add_qr()
    page.assert_att(data["rwmc"])
    logger.info('02新增调度任务成功')


@allure.feature('调度管理')
@pytest.mark.parametrize('data', load_yaml('../../data/sjkf/ddgl.yaml'))
@allure.title('查询调度任务')
def test_ddgl_search(browser, data):
    page = DdglPage(browser)
    page.search_rwmc(data["rwmc"])
    page.search_rwlx(data['rwlx'])
    page.button_search()
    page.assert_att(data["rwmc"])
    page.button_refresh()
    page.search_rwmc("error")
    page.button_search()
    page.assert_att("暂无数据")
    page.button_refresh()
    page.button_search()
    page.assert_att(data["rwmc"])
    logger.info("03查询调度任务正常")


@allure.feature('调度管理')
@pytest.mark.parametrize('data', load_yaml('../../data/sjkf/ddgl.yaml'))
@allure.title('切换调度启停开关')
def test_ddgl_switch(browser, data):
    page = DdglPage(browser)
    page.search_rwmc(data["rwmc"])
    page.button_search()
    page.button_switch()
    page.assert_att("停用")
    page.button_switch()
    page.assert_att("启用")
    logger.info("04切换调度启停开关正常")


@allure.feature('调度管理')
@pytest.mark.parametrize('data', load_yaml('../../data/sjkf/ddgl.yaml'))
@allure.title('编辑调度任务')
def test_ddgl_edit(browser, data):
    page = DdglPage(browser)
    page.search_rwmc(data["rwmc"])
    page.button_search()
    page.button_switch()
    page.button_edit()
    page.edit_rwmc('s')
    page.button_add_qr()
    page.button_refresh()
    page.search_rwmc(data["rwmc"]+'s')
    page.button_search()
    page.assert_att(data["rwmc"]+'s')
    logger.info("05编辑调度任务正常")


@allure.feature('调度管理')
@pytest.mark.parametrize('data', load_yaml('../../data/sjkf/ddgl.yaml'))
@allure.title('删除调度任务')
def test_ddgl_remove(browser, data):
    page = DdglPage(browser)
    page.search_rwmc(data["rwmc"]+'s')
    page.button_delete()
    page.enter_keys()
    page.search_rwmc(data["rwmc"]+'s')
    page.assert_att("暂无数据")
    logger.info("06删除调度任务正常")


@allure.feature('调度管理')
@allure.title('退出登录')
def test_ddgl_logout(browser):
    page = LoginPage(browser)
    page.reback_iframe()
    page.button_user()
    pyautogui.click(2428, 391)
    page.wait(2)
    page.assert_att("赢和数据")
    logger.info('.....退出登录.....')


