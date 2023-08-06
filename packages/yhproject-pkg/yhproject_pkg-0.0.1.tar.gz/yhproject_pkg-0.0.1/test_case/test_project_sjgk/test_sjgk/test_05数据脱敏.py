import pytest
import pyautogui
from yhproject_pkg.framework.data_driver.yaml_driver import load_yaml
from yhproject_pkg.framework.page.login_page.login_page import LoginPage
from yhproject_pkg.framework.page.login_page.menu_page import MenuPage
from yhproject_pkg.framework.page.sjgk_page.sjtm_page import SjtmPage
import allure
import logging

logger = logging.getLogger(__name__)


@allure.feature('数据脱敏')
@allure.title('登录')
@pytest.mark.parametrize('data', load_yaml('../../data/login/login1.yaml'))
def test_login_sjtm(browser, data):
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
    logger.info('------------进入数据脱敏模块-------------')


@allure.feature('数据脱敏')
@pytest.mark.parametrize('data', load_yaml('../../data/login/menu.yaml'))
@allure.title('打开菜单_数据脱敏')
def test_menu_sjtm(browser, data):
    page = MenuPage(browser)
    browser.get(data['url'])
    page.driver.maximize_window()
    page.table_manage()
    page.menu_icon()
    page.menu_sjgk()
    page.sjgk_sjaq_sjtm()
    # 切换iframe
    page.sjgk_sjtm_iframe()
    page.assert_att("数据脱敏配置")
    logger.info('01进入菜单成功')


@allure.feature('数据脱敏')
@pytest.mark.parametrize('data', load_yaml('../../data/sjgk/tmgz.yaml'))
@allure.title('定位_数据库表')
def test_local_sjtm(browser, data):
    page = SjtmPage(browser)
    page.input_ora('SHUJUYUAN')
    page.icon_ora()
    page.input_ora(data['table'])
    page.icon_tab()
    page.assert_att(data['table'])
    logger.info('02数据库表定位成功')


@allure.feature('数据脱敏')
@pytest.mark.parametrize('data', load_yaml('../../data/sjgk/tmgz.yaml'))
@allure.title('查询_数据库表')
def test_place_sjtm(browser, data):
    page = SjtmPage(browser)
    page.input_col('error')
    page.assert_att("暂无数据")
    page.button_reset()
    page.input_col(data['col'])
    page.input_rule(data['gzmc2'])
    page.assert_att(data['gzmc2'])
    logger.info('03配置后查询成功')


@allure.feature('数据脱敏')
@allure.title('退出登录')
def test_tmgl_logout(browser):
    page = LoginPage(browser)
    page.reback_iframe()
    page.button_user()
    pyautogui.click(2428, 391)
    page.wait(2)
    page.assert_att("赢和数据")
    logger.info('.....退出登录.....')
