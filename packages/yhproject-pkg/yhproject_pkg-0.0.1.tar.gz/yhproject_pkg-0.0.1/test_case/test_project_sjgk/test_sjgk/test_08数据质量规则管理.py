import pytest
import pyautogui
from yhproject_pkg.framework.data_driver.yaml_driver import load_yaml
from yhproject_pkg.framework.page.login_page.login_page import LoginPage
from yhproject_pkg.framework.page.login_page.menu_page import MenuPage
from yhproject_pkg.framework.page.sjgk_page.sjzlgzgl_page import SjzlgzglPage
import allure
import logging

logger = logging.getLogger(__name__)


@allure.feature('数据质量规则管理')
@allure.title('登录')
@pytest.mark.parametrize('data', load_yaml('../../data/login/login1.yaml'))
def test_login_zlgzgl(browser, data):
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
    logger.info('------------进入数据管控质量规则管理模块-------------')


@allure.feature('数据质量规则管理')
@pytest.mark.parametrize('data', load_yaml('../../data/login/menu.yaml'))
@allure.title('打开菜单_质量规则管理')
def test_menu_zlgzgl(browser, data):
    page = MenuPage(browser)
    page.table_manage()
    page.menu_icon()
    page.menu_sjgk()
    page.sjgk_sjzl_sjzlgzgl()
    # 切换iframe
    page.sjgk_sjzlgzgl_iframe()
    page.assert_att("任务名称")
    logger.info('01进入菜单成功')


@allure.feature('数据质量规则管理')
@pytest.mark.parametrize('data', load_yaml('../../data/sjgk/sjzlgzgl.yaml'))
@allure.title('新增_质量规则管理')
def test_add_zlgzgl(browser, data):
    page = SjzlgzglPage(browser)
    page.button_add()
    page.input_rwmc(data['rwmc'])
    page.input_rulecode(data['rulecode'])
    page.button_qr()
    page.assert_att('操作成功')
    logger.info('02新增成功')


@allure.feature('数据质量规则管理')
@pytest.mark.parametrize('data', load_yaml('../../data/sjgk/sjzlgzgl.yaml'))
@allure.title('查询_质量规则管理')
def test_search_zlgzgl(browser, data):
    page = SjzlgzglPage(browser)
    page.input_search('error')
    page.assert_att('暂无数据')
    page.button_reset()
    page.input_search(data['rwmc'])
    page.assert_att(data['rwmc'])
    logger.info('03查询成功')


@allure.feature('数据质量规则管理')
@pytest.mark.parametrize('data', load_yaml('../../data/sjgk/sjzlgzgl.yaml'))
@allure.title('执行_质量规则管理')
def test_aciton_zlgzgl(browser, data):
    page = SjzlgzglPage(browser)
    page.button_action()
    page.assert_att('操作成功')
    logger.info('04执行规则成功')


@allure.feature('数据质量规则管理')
@pytest.mark.parametrize('data', load_yaml('../../data/sjgk/sjzlgzgl.yaml'))
@allure.title('编辑_质量规则管理')
def test_edit_zlgzgl(browser, data):
    page = SjzlgzglPage(browser)
    page.button_edit()
    page.input_rwmc('s')
    page.button_qr()
    page.button_reset()
    page.input_search(data['rwmc']+'s')
    page.assert_att(data['rwmc']+'s')
    logger.info('05编辑成功')


@allure.feature('数据质量规则管理')
@pytest.mark.parametrize('data', load_yaml('../../data/sjgk/sjzlgzgl.yaml'))
@allure.title('删除_质量规则管理')
def test_remove_zlgzgl(browser, data):
    page = SjzlgzglPage(browser)
    page.button_remove()
    page.assert_att('暂无数据')
    logger.info('06删除成功')


@allure.feature('数据质量规则管理')
@allure.title('退出登录')
def test_zlgzgl_logout(browser):
    page = LoginPage(browser)
    page.reback_iframe()
    page.button_user()
    pyautogui.click(2428, 391)
    page.wait(2)
    page.assert_att("赢和数据")
    logger.info('.....退出登录.....')




