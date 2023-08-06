# import sys
# sys.path.append(r"C:\Users\胡小锋\PycharmProjects\pythonProject")
import logging
import pytest
from yhproject_pkg.framework.data_driver.yaml_driver import load_yaml
from yhproject_pkg.framework.page.demo_page0 import BaiduPage
import allure

logger = logging.getLogger(__name__)


@allure.feature('百度搜索')


class TestLogin():
    @pytest.mark.parametrize('data', load_yaml('../../data/demo/login_demo2.yaml'))
    def test_login012(self, data, t):
        page = BaiduPage(t)
        print("还在当前页面")

        # t.WebKeys.locator(data["name_xpath"],data["value2"]).click()
        page.button_ssgs()
        # t.find_element_by_xpath(data["value2"]).click
        print("点击成功")
        # assert "上市" in t.find_element_by_link_text("上市公司").text
        # page.assert_att("上市公司")

        page.wait(1)
        page.quit()
        print('测试3')


logger.info("TestLogin")



if __name__ == '__main__':
    pytest.main(['test_demo1.py'])

