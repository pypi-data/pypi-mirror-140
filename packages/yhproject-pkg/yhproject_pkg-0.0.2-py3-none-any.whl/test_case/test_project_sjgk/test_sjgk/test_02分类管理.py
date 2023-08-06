import pytest
import pyautogui
from yhproject_pkg.framework.data_driver.yaml_driver import load_yaml
from yhproject_pkg.framework.page.login_page.login_page import LoginPage
from yhproject_pkg.framework.page.login_page.menu_page import MenuPage
from yhproject_pkg.framework.page.sjgk_page.flgl_page import FlglPage
import allure
import logging

logger = logging.getLogger(__name__)


@allure.feature('分类管理')
@allure.title('登录')
@pytest.mark.parametrize('data', load_yaml('../../data/login/login1.yaml'))
def test_login_flgl(browser, data):
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
    logger.info('------------进入分类管理模块-------------')


@allure.feature('分类管理')
@pytest.mark.parametrize('data', load_yaml('../../data/login/menu.yaml'))
@allure.title('打开菜单_分类管理')
def test_menu_flgl(browser, data):
    page = MenuPage(browser)
    page.table_manage()
    page.menu_icon()
    page.menu_sjgk()
    page.sjgk_sjflfj_sjfl()
    # 切换iframe
    page.sjgk_sjfl_iframe()
    page.assert_att("数据分类管理")
    logger.info('01进入菜单成功')


@allure.feature('分类管理')
@pytest.mark.parametrize('data', load_yaml('../../data/sjgk/flgl.yaml'))
@allure.title('分类管理_新增分类')
def test_flgl_add(browser, data):
    page = FlglPage(browser)
    page.button_add()
    page.input_flmc(data["flmc"])
    page.input_flcj(data["flcj"])
    page.button_flqr()
    logger.info('02新增分类成功')


@allure.feature('分类管理')
@pytest.mark.parametrize('data', load_yaml('../../data/sjgk/flgl.yaml'))
@allure.title('分类管理_新增子分类')
def test_flgl_add01(browser, data):
    page = FlglPage(browser)
    page.input_treesearch(data['flmc'])
    page.icon_add()
    page.input_flmc(data['flmc1'])
    page.button_flqr()
    page.input_treesearch(data['flmc'])
    page.icon_add()
    page.input_flmc(data['flmc2'])
    page.button_flqr()
    page.input_treesearch(data['flmc'])
    page.assert_att(data['flmc1'])
    page.assert_att(data['flmc2'])
    logger.info('03新增子分类成功')


@allure.feature('分类管理')
@pytest.mark.parametrize('data', load_yaml('../../data/sjgk/flgl.yaml'))
@allure.title('分类管理_编辑子分类')
def test_flgl_edit(browser, data):
    page = FlglPage(browser)
    page.input_treesearch(data['flmc'])
    page.icon_edit()
    page.input_flmc('s')
    page.button_flqr()
    page.input_treesearch(data['flmc'])
    page.assert_att(data['flmc1']+'s')
    logger.info("04编辑子分类成功")


@allure.feature('分类管理')
@pytest.mark.parametrize('data', load_yaml('../../data/sjgk/flgl.yaml'))
@allure.title('分类管理_删除子分类')
def test_flgl_remove(browser, data):
    page = FlglPage(browser)
    page.input_treesearch(data['flmc'])
    page.icon_remove()
    page.assert_att("操作成功")
    logger.info("05子分类删除成功")


@allure.feature('分类管理')
@pytest.mark.parametrize('data', load_yaml('../../data/sjgk/flgl1.yaml'))
@allure.title('分类管理_新增数据')
def test_flgl_sjadd(browser, data):
    page = FlglPage(browser)
    page.input_treesearch(data['flmc1'])
    page.icon_flmc()
    page.button_sjadd()
    page.input_sjflmc(data['sjflmc'])
    page.input_sjyjfl(data['flmc1'])
    page.input_sjejfl(data['flmc2'])
    page.input_sjsjsyz()
    page.input_sjtext(data['sjtext'])
    page.button_sjqr()
    page.assert_att('操作成功')
    logger.info('06新增数据成功')


@allure.feature('分类管理')
@pytest.mark.parametrize('data', load_yaml('../../data/sjgk/flgl1.yaml'))
@allure.title('分类管理_查询数据')
def test_flgl_sjsearch(browser, data):
    page = FlglPage(browser)
    page.button_sjreset()
    page.input_sjsearch(data['sjflmc'])
    page.button_sjsearch()
    page.assert_att(data['sjtext'])
    logger.info("07查询数据成功")


@allure.feature('分类管理')
@pytest.mark.parametrize('data', load_yaml('../../data/sjgk/flgl.yaml'))
@allure.title('分类管理_删除数据')
def test_flgl_sjremove(browser, data):
    page = FlglPage(browser)
    page.input_treesearch(data['flmc'])
    page.icon_flmc()
    page.icon_sjremove()
    page.assert_att("删除成功")
    page.icon_boxcheck()
    page.button_sjremove()
    page.input_treesearch(data['flmc1'])
    page.assert_att("暂无数据")
    logger.info("08删除数据成功")


@allure.feature('分类管理')
@pytest.mark.parametrize('data', load_yaml('../../data/sjgk/flgl.yaml'))
@allure.title('分类管理_编辑数据')
def test_flgl_sjedit(browser, data):
    page = FlglPage(browser)
    page.input_treesearch(data['flmc'])
    page.icon_flmc()
    page.icon_sjedit()
    page.input_sjtext('aaa')
    page.button_sjqr()
    page.input_sjsearch('error')
    page.button_sjsearch()
    page.assert_att("暂无数据")
    page.button_sjreset()
    page.input_sjsearch("aaa")
    page.button_sjsearch()
    page.assert_att("aaa")
    logger.info("09编辑数据成功")


@allure.feature('分类管理')
@pytest.mark.parametrize('data', load_yaml('../../data/sjgk/flgl.yaml'))
@allure.title('分类管理_删除总分类')
def test_flgl_sremove(browser, data):
    page = FlglPage(browser)
    page.input_treesearch(data['flmc'])
    page.icon_sremove()
    page.input_treesearch(data['flmc'])
    page.assert_att("暂无数据")
    logger.info("10子分类删除成功")


@allure.feature('分类管理')
@allure.title('退出登录')
def test_flgl_logout(browser):
    page = LoginPage(browser)
    page.reback_iframe()
    page.button_user()
    pyautogui.click(2428, 391)
    page.wait(2)
    page.assert_att("赢和数据")
    logger.info('.....退出登录.....')









