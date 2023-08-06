import pytest
import pyautogui
from yhproject_pkg.framework.data_driver.yaml_driver import load_yaml
from yhproject_pkg.framework.page.login_page.login_page import LoginPage
from yhproject_pkg.framework.page.login_page.menu_page import MenuPage
from yhproject_pkg.framework.page.sjfw_page.jkcx_page import JkcxPage
from yhproject_pkg.framework.page.sjfw_page.jksp_page import JkspPage
import allure
import logging

logger = logging.getLogger(__name__)


@allure.feature('接口查询')
@allure.title('登录')
@pytest.mark.parametrize('data', load_yaml('../../data/login/login1.yaml'))
def test_login_jkcx(browser, data):
    page = LoginPage(browser)
    page.driver.maximize_window()
    page.open(data["url"])
    page.wait(3)
    page.input_user(data["user1"])
    page.input_password(data["password1"])
    page.button_remember()
    page.button_login()
    page.wait(2)
# 登录跳转
    page.switch_window(-1)
    page.assert_att("赢和数据")
    logger.info("接口查询_登录成功")


@allure.feature('接口查询')
@allure.title('打开菜单_接口查询')
def test_menu_jkcx(browser):
    page = MenuPage(browser)
    page.table_manage()
    page.menu_icon()
    page.menu_sjfw()
    page.sjfw_sjfw_jkcx()
    logger.info('打开菜单_接口查询管理')
    # 切换iframe
    page.sjfw_jkcx_iframe()
    logger.info('进入接口查询管理模块')
    page.assert_att("状态")


@allure.feature('接口查询')
@pytest.mark.parametrize('data', load_yaml('../../data/sjfw/cjjk.yaml'))
@allure.title('查询接口')
def test_jkcx_search(browser, data):
    page = JkcxPage(browser)
    page.input_search('error')
    page.assert_att('暂无数据')
    page.button_reset()
    page.input_search(data['jkmc2'])
    page.assert_att('不可用')
    logger.info("接口查询_查询接口正常")


@allure.feature('接口查询')
@pytest.mark.parametrize('data', load_yaml('../../data/sjfw/cjjk.yaml'))
@allure.title('申请接口')
def test_jkcx_apply(browser, data):
    page = JkcxPage(browser)
    page.button_apply()
    page.enter_keys()
    page.wait(1)
    page.assert_att("操作成功")
    page.wait(5)
    page.button_apply()
    page.enter_keys()
    page.wait(1)
    page.assert_att("该接口正在申请中")
    page.wait(3)
    logger.info('接口查询_接口权限申请')


@allure.feature('接口查询')
@allure.title('查看密钥')
def test_jkcx_appkey(browser):
    page = JkcxPage(browser)
    page.button_appkey()
    page.wait(2)
    page.assert_att("appKey")
    page.button_close()
    logger.info('接口查询_接口查询密钥')


@allure.feature('接口查询')
@pytest.mark.parametrize('data', load_yaml('../../data/sjfw/cjjk.yaml'))
@allure.title('打开菜单_接口审批管理')
def test_menu_jksp(browser, data):
    page = MenuPage(browser)
    page.reback_iframe()
    page.menu_sjfw()
    page.sjfw_sjfw_jksp()
    page.sjfw_jksp_iframe()
    logger.info('接口查询_进入接口审批管理模块')


@allure.feature('接口查询')
@pytest.mark.parametrize('data', load_yaml('../../data/sjfw/cjjk.yaml'))
@allure.title('接口审批管理通过')
def test_jksp_check(browser, data):
    page = JkspPage(browser)
    page.button_reset()
    page.input_search(data['jkmc2'])
    page.wait(3)
    page.button_check()
    page.wait(1)
    page.button_check_ture()
    page.wait(3)
    logger.info("接口查询_接口审批通过")


@allure.feature('接口查询')
@pytest.mark.parametrize('data', load_yaml('../../data/login/menu.yaml'))
@allure.title('打开菜单_接口查询管理')
def test_remenu_jkcx1(browser, data):
    page = MenuPage(browser)
    page.reback_iframe()
    page.menu_sjfw()
    page.wait(10)
    page.sjfw_sjfw_jkcx()
    page.wait(10)
    page.sjfw_jkcx_iframe()
    page.wait(3)
    page.assert_att("状态")
    logger.info('接口查询_进入接口查询模块')


@allure.feature('接口查询')
@pytest.mark.parametrize('data', load_yaml('../../data/sjfw/cjjk.yaml'))
@allure.title('查询接口')
def test_rejkcx_search1(browser, data):
    page = JkcxPage(browser)
    page.button_reset()
    page.input_search(data['jkmc2'])
    page.assert_att('可用')
    page.wait(3)
    logger.info("接口查询_接口申请成功")


@allure.feature('接口查询')
@allure.title('查询接口')
def test_rejkcx_apitest(browser):
    page = JkcxPage(browser)
    page.button_apply()
    page.wait(2)
    page.button_apitest()
    page.wait(2)
    page.assert_att('200')
    page.button_reback()
    page.wait(2)
    logger.info('接口查询_APItest')


@allure.feature('接口查询')
@allure.title('退出登录')
def test_jksxgl_logout(browser):
    page = LoginPage(browser)
    page.reback_iframe()
    page.button_user()
    pyautogui.click(2428, 391)
    page.wait(2)
    page.assert_att("赢和数据")
    logger.info('.....退出登录.....')


