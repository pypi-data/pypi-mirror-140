import pytest
import pyautogui
import random
from yhproject_pkg.framework.data_driver.yaml_driver import load_yaml
from yhproject_pkg.framework.page.login_page.login_page import LoginPage
from yhproject_pkg.framework.page.login_page.menu_page import MenuPage
from yhproject_pkg.framework.page.sjfw_page.jkcj_page import JkcjPage
import allure
import logging

logger = logging.getLogger(__name__)


@allure.feature('接口创建')
@allure.title('登录')
@pytest.mark.parametrize('data', load_yaml('../../data/login/login1.yaml'))
def test_login_jkcj(browser, data):
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
    logger.info("创建接口_登录成功")


@allure.feature('接口创建')
@pytest.mark.parametrize('data', load_yaml('../../data/login/menu.yaml'))
@allure.title('打开菜单_接口创建')
def test_menu_jkcj(browser, data):
    page = MenuPage(browser)
    page.table_manage()
    page.menu_icon()
    page.menu_sjfw()
    page.sjfw_sjfw_jkcj()
    # 切换iframe
    page.sjfw_jkcj_iframe()
    page.assert_att("接口名称")
    logger.info('打开菜单_接口创建')


@allure.feature('接口创建')
@pytest.mark.parametrize('data', load_yaml('../../data/sjfw/cjjk.yaml'))
@allure.title('新增接口1')
def test_jkcj_add1(browser, data):
    page = JkcjPage(browser)
    page.button_add()
    rand = random.randint(0, 100000)
    page.input_sjymc(data["sjymc"])
    page.input_sjbmc(data["sjbmc"])
    page.drog_aa()
    page.wait(3)
    page.button_jkcs1()
    page.button_jkcs2()
    page.input_jkbm(data['jkbm1'])
    page.input_jkbm(rand)
    page.input_jkmc(data['jkmc1'])
    page.input_ywzt()
    page.input_jkms(data['jkms1'])
    page.button_save()
    page.wait(1)
    page.assert_att("操作成功")
    logger.info("新增接口_新增接口成功")


@allure.feature('接口创建')
@pytest.mark.parametrize('data', load_yaml('../../data/sjfw/cjjk.yaml'))
@allure.title('新增接口2')
def test_jkcj_add2(browser, data):
    page = JkcjPage(browser)
    page.button_add()
    rand = random.randint(0, 100000)
    page.input_sjymc(data["sjymc"])
    page.input_sjbmc(data["sjbmc"])
    page.drog_aa()
    page.wait(3)
    page.button_jkcs1()
    page.button_jkcs2()
    page.input_jkbm(data['jkbm2'])
    page.input_jkbm(rand)
    page.input_jkmc(data['jkmc2'])
    page.input_ywzt()
    page.input_jkms(data['jkms2'])
    page.button_save()
    page.wait(1)
    page.assert_att("操作成功")
    logger.info("新增接口_新增接口成功")


@allure.feature('接口创建')
@pytest.mark.parametrize('data', load_yaml('../../data/sjfw/cjjk.yaml'))
@allure.title('查询接口')
def test_jkcj_search(browser, data):
    page = JkcjPage(browser)
    page.input_seach_jkmc('error')
    page.button_search()
    page.assert_att('暂无数据')
    page.button_reset()
    page.input_seach_jkmc(data['jkmc1'])
    page.button_search()
    page.assert_att(data['jkmc1'])
    logger.info("查询接口正常")


@allure.feature('接口创建')
@pytest.mark.parametrize('data', load_yaml('../../data/sjfw/cjjk.yaml'))
@allure.title('接口测试')
def test_jkcj_apitest(browser, data):
    page = JkcjPage(browser)
    page.button_reset()
    page.input_seach_jkmc(data['jkmc1'])
    page.button_search()
    page.button_test()
    page.assert_att("接口信息")
    page.button_apitest()
    page.assert_att("200")
    page.input_edit_jkms("已经测试")
    page.button_edit_save()
    page.button_edit_back()
    page.button_search()
    page.assert_att("已经测试")
    logger.info("编辑测试成功")


@allure.feature('接口创建')
@pytest.mark.parametrize('data', load_yaml('../../data/sjfw/cjjk.yaml'))
@allure.title('提交接口')
def test_jkcj_sumbit(browser, data):
    page = JkcjPage(browser)
    page.button_reset()
    page.input_seach_jkmc(data['jkmc1'])
    page.button_search()
    page.button_submit()
    page.enter_keys()
    page.assert_att('审核中')
    page.button_reset()
    page.input_seach_jkmc(data['jkmc2'])
    page.button_search()
    page.button_submit()
    page.enter_keys()
    page.assert_att('审核中')
    logger.info('新增接口_提交接口审核')


@allure.feature('接口创建')
@allure.title('退出登录')
def test_jkcj_logout(browser):
    page = LoginPage(browser)
    page.reback_iframe()
    page.button_user()
    pyautogui.click(2428, 391)
    page.wait(2)
    page.assert_att("赢和数据")
    logger.info('.....退出登录.....')


