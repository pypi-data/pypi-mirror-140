import pytest
import pyautogui
from yhproject_pkg.framework.data_driver.yaml_driver import load_yaml
from yhproject_pkg.framework.page.login_page.login_page import LoginPage
from yhproject_pkg.framework.page.login_page.menu_page import MenuPage
from yhproject_pkg.framework.page.sjgk_page.gzkgl_page import GzkglPage
import allure
import logging

logger = logging.getLogger(__name__)


@allure.feature('规则库管理')
@allure.title('登录')
@pytest.mark.parametrize('data', load_yaml('../../data/login/login1.yaml'))
def test_login_gzkgl(browser, data):
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
    logger.info('------------进入数据管控质量规则管理模块-------------')


@allure.feature('规则库管理')
@pytest.mark.parametrize('data', load_yaml('../../data/login/menu.yaml'))
@allure.title('打开菜单_规则库管理')
def test_menu_gzkgl(browser, data):
    page = MenuPage(browser)
    page.table_manage()
    page.menu_icon()
    page.menu_sjgk()
    page.sjgk_sjzl_gzkgl()
    # 切换iframe
    page.sjgk_gzkgl_iframe()
    page.assert_att("编码规则")
    logger.info('01进入菜单成功')


@allure.feature('规则库管理')
@pytest.mark.parametrize('data', load_yaml('../../data/sjgk/gzkgl.yaml'))
@allure.title('新增1_规则库管理')
def test_add_gzkgl(browser, data):
    page = GzkglPage(browser)
    page.button_add()
    page.assert_att("新增检查规则")
    page.input_checktheme(data['checktheme'])
    page.input_checkmodule()
    page.input_checkclass()
    page.input_checktitle(data['checktitle'])
    page.input_checkname(data['checkname'])
    page.input_checkrule(data['checkrule'])
    page.input_text(data['text'])
    page.core_switch()
    page.input_sjwdsm(data['sjwdsm'])
    page.icon_plus()
    page.input_wdsmora(data['wdsmora'])
    page.input_wdsmtable(data['wdsmtable'])
    page.input_wdsmcol(data['wdsmcol'])
    page.input_sos(data['sos'])
    page.input_dos(data['dos'])
    page.down_mouse()
    page.icon_pplus()
    page.input_stable(data['stable'])
    page.input_scol(data['scol'])
    page.input_dtable(data['dtable'])
    page.input_dcol(data['dcol'])
    page.button_nextstep()
    page.assert_att("美化SQL")
    logger.info('02新增--可视化编辑')


@allure.feature('规则库管理')
@pytest.mark.parametrize('data', load_yaml('../../data/sjgk/gzkgl.yaml'))
@allure.title('新增2_规则库管理')
def test_add2_gzkgl(browser, data):
    page = GzkglPage(browser)
    page.up_mouse()
    page.local_sql()
    page.allselect_keys()
    page.backspace_keys()
    page.key_word()
    page.button_mhsql()
    page.button_sumbit()
    page.assert_att("所有分类")
    logger.info('03新增--直接编辑')


@allure.feature('规则库管理')
@pytest.mark.parametrize('data', load_yaml('../../data/sjgk/gzkgl.yaml'))
@allure.title('查询_规则库管理')
def test_search_gzkgl(browser, data):
    page = GzkglPage(browser)
    page.input_search('error')
    page.assert_att('暂无数据')
    page.input_search(data['checkrule'])
    page.assert_att(data['checkrule'])
    logger.info('04查询成功')


@allure.feature('规则库管理')
@allure.title('启停_规则库管理')
def test_rulevalid_gzkgl(browser):
    page = GzkglPage(browser)
    page.button_checkvalid()
    page.assert_att("停用")
    page.button_checkvalid()
    page.assert_att("有效")
    logger.info('05启停成功')


@allure.feature('规则库管理')
@pytest.mark.parametrize('data', load_yaml('../../data/sjgk/gzkgl.yaml'))
@allure.title('编辑_规则库管理')
def test_edit_gzkgl(browser, data):
    page = GzkglPage(browser)
    page.button_edit()
    page.input_checkrule("s")
    page.button_nextstep()
    page.button_sumbit()
    page.input_search(data['checkrule']+'s')
    page.assert_att(data['checkrule']+'s')
    logger.info("06编辑成功")


@allure.feature('规则库管理')
@pytest.mark.parametrize('data', load_yaml('../../data/sjgk/gzkgl.yaml'))
@allure.title('删除_规则库管理')
def test_remove_gzkgl(browser, data):
    page = GzkglPage(browser)
    page.button_remove()
    page.assert_att('暂无数据')
    logger.info('07删除成功')


@allure.feature('规则库管理')
@allure.title('退出登录')
def test_gzkgl_logout(browser):
    page = LoginPage(browser)
    page.reback_iframe()
    page.button_user()
    pyautogui.click(2428, 391)
    page.wait(2)
    page.assert_att('赢和数据')
    logger.info('.....退出登录.....')

