import pytest
import pyautogui
from yhproject_pkg.framework.data_driver.yaml_driver import load_yaml
from yhproject_pkg.framework.page.login_page.login_page import LoginPage
from yhproject_pkg.framework.page.login_page.menu_page import MenuPage
from yhproject_pkg.framework.page.sjgk_page.tmgz_page import TmgzPage
import allure
import logging

logger = logging.getLogger(__name__)


@allure.feature('脱敏规则')
@allure.title('登录')
@pytest.mark.parametrize('data', load_yaml('../../data/login/login1.yaml'))
def test_login_tmgz(browser, data):
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
    logger.info('------------进入脱敏规则模块-------------')


@allure.feature('脱敏规则')
@pytest.mark.parametrize('data', load_yaml('../../data/login/menu.yaml'))
@allure.title('打开菜单_脱敏规则')
def test_menu_tmgz(browser, data):
    page = MenuPage(browser)
    page.open(data["url"])
    page.table_manage()
    page.menu_icon()
    page.menu_sjgk()
    page.sjgk_sjaq_tmgz()
    # 切换iframe
    page.sjgk_tmgz_iframe()
    page.assert_att("规则名称")
    logger.info('01进入菜单')


@allure.feature('脱敏规则')
@pytest.mark.parametrize('data', load_yaml('../../data/sjgk/tmgz.yaml'))
@allure.title('新增_脱敏规则')
def test_add_tmgz(browser, data):
    page = TmgzPage(browser)
    page.button_add()
    page.input_gzmc(data['gzmc'])
    page.input_gzbm(data['gzbm'])
    page.input_gzdj(data['gzdj'])
    page.input_bds('2', '4')
    page.input_thfh('***')
    page.input_gzms(data['gzms'])
    page.button_save()
    logger.info('02新增成功1')


@allure.feature('脱敏规则')
@pytest.mark.parametrize('data', load_yaml('../../data/sjgk/tmgz.yaml'))
@allure.title('新增_脱敏规则1')
def test_add1_tmgz(browser, data):
    page = TmgzPage(browser)
    page.button_add()
    page.input_gzmc(data['gzmc1'])
    page.input_gzbm(data['gzbm1'])
    page.input_gzdj(data['gzdj1'])
    page.input_gzlx()
    page.input_gzmy(data['gzmy1'])
    page.input_gzms(data['gzms1'])
    page.button_save()
    logger.info('03新增成功2')


@allure.feature('脱敏规则')
@pytest.mark.parametrize('data', load_yaml('../../data/sjgk/tmgz.yaml'))
@allure.title('新增_脱敏规则2')
def test_add2_tmgz(browser, data):
    page = TmgzPage(browser)
    page.button_add()
    page.input_gzmc(data['gzmc2'])
    page.input_gzbm(data['gzbm2'])
    page.input_gzdj(data['gzdj2'])
    page.input_bds('2', '4')
    page.input_thfh('***')
    page.input_gzms(data['gzms2'])
    page.button_save()
    logger.info('04新增成功3')


@allure.feature('脱敏规则')
@pytest.mark.parametrize('data', load_yaml('../../data/sjgk/tmgz.yaml'))
@allure.title('搜索_脱敏规则')
def test_search_tmgz(browser, data):
    page = TmgzPage(browser)
    page.input_search('error')
    page.assert_att('暂无数据')
    page.button_reset()
    page.input_search(data['gzmc'])
    page.assert_att(data["gzmc"])
    logger.info('05查询成功')


@allure.feature('脱敏规则')
@pytest.mark.parametrize('data', load_yaml('../../data/sjgk/tmgz.yaml'))
@allure.title('编辑_脱敏规则')
def test_edit_tmgz(browser, data):
    page = TmgzPage(browser)
    page.button_setting()
    page.assert_att("编辑")
    page.button_edit()
    page.assert_att('编辑')
    page.input_egzmc('sss')
    page.button_esave()
    page.button_reset()
    page.input_search('sss')
    page.assert_att('sss')
    logger.info('06编辑成功')


@allure.feature('脱敏规则')
@pytest.mark.parametrize('data', load_yaml('../../data/sjgk/tmgz.yaml'))
@allure.title('删除_脱敏规则')
def test_remove_tmgz(browser, data):
    page = TmgzPage(browser)
    page.button_eremove()
    page.assert_att('暂无数据')
    logger.info('07删除成功')


@allure.feature('脱敏规则')
@pytest.mark.parametrize('data', load_yaml('../../data/sjgk/tmgz.yaml'))
@allure.title('批量删除_脱敏规则')
def test_remove_etmgz(browser, data):
    page = TmgzPage(browser)
    page.button_reset()
    page.input_search(data['gzmc1'])
    page.assert_att(data['gzmc1'])
    page.box_check()
    page.button_remove()
    page.assert_att('暂无数据')
    logger.info('08批量删除成功')


@allure.feature('脱敏规则')
@allure.title('退出登录')
def test_tmgl_logout(browser):
    page = LoginPage(browser)
    page.reback_iframe()
    page.button_user()
    pyautogui.click(2428, 391)
    page.wait(2)
    page.assert_att("赢和数据")
    logger.info('.....退出登录.....')

