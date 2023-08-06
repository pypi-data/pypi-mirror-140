import pytest
import pyautogui
from yhproject_pkg.framework.data_driver.yaml_driver import load_yaml
from yhproject_pkg.framework.page.login_page.login_page import LoginPage
from yhproject_pkg.framework.page.login_page.menu_page import MenuPage
from yhproject_pkg.framework.page.sjgk_page.tmgl_page import TmglPage
from yhproject_pkg.framework.page.sjgk_page.tmgz_page import TmgzPage
import allure
import logging

logger = logging.getLogger(__name__)


@allure.feature('脱敏管理')
@allure.title('登录')
@pytest.mark.parametrize('data', load_yaml('../../data/login/login1.yaml'))
def test_login_tmgl(browser, data):
    page = LoginPage(browser)
    browser.get(data['url'])
    page.driver.maximize_window()
    page.wait(3)
    page.input_user(data["user"])
    page.input_password(data["password"])
    page.button_remember()
    page.button_login()
    # 登录跳转
    page.switch_window(-1)
    page.assert_att("赢和数据")
    logger.info('------------进入脱敏管理模块-------------')


@allure.feature('脱敏管理')
@pytest.mark.parametrize('data', load_yaml('../../data/login/menu.yaml'))
@allure.title('打开菜单_脱敏管理')
def test_menu_tmgl(browser, data):
    page = MenuPage(browser)
    page.driver.maximize_window()
    page.table_manage()
    page.menu_icon()
    page.menu_sjgk()
    page.sjgk_sjaq_tmgl()
    # 切换iframe
    page.sjgk_tmgl_iframe()
    page.assert_att("脱敏规则")
    logger.info('01进入菜单')


@allure.feature('脱敏管理')
@pytest.mark.parametrize('data', load_yaml('../../data/sjgk/tmgz.yaml'))
@allure.title('查询_脱敏管理')
def test_search_tmgl(browser, data):
    page = TmglPage(browser)
    page.input_search('error')
    page.assert_att('暂无数据')
    page.button_reset()
    page.input_search(data['table'])
    page.assert_att(data['table'])
    logger.info('02查询成功')


@allure.feature('脱敏管理')
@allure.title('管理_脱敏管理')
def test_mgtmgl(browser):
    page = TmglPage(browser)
    page.button_manage()
    page.core_switch()
    page.core_switch()
    logger.info('03启停成功')


@allure.feature('脱敏管理')
@allure.title('删除_脱敏管理')
def test_rmtmgl(browser):
    page = TmglPage(browser)
    page.button_remove()
    page.assert_att("暂无数据")
    logger.info('04删除成功')


@allure.feature('脱敏管理')
@allure.title('返回_脱敏规则')
def test_rebacktmgz(browser):
    page = MenuPage(browser)
    page.reback_iframe()
    page.menu_sjgk()
    page.sjgk_sjaq_tmgz()
    page.sjgk_tmgz_iframe()
    page.assert_att("规则名称")
    logger.info('05重返脱敏规则菜单')


@allure.feature('脱敏管理')
@pytest.mark.parametrize('data', load_yaml('../../data/sjgk/tmgz.yaml'))
@allure.title('删除_脱敏规则')
def test_rmtmgz(browser, data):
    page = TmgzPage(browser)
    page.input_search(data['gzmc2'])
    page.button_setting()
    page.button_eremove()
    page.assert_att("暂无数据")
    logger.info('06删除脱敏规则数据')


@allure.feature('脱敏管理')
@allure.title('退出登录')
def test_tmgl_logout(browser):
    page = LoginPage(browser)
    page.reback_iframe()
    page.button_user()
    pyautogui.click(2428, 391)
    page.wait(2)
    page.assert_att("赢和数据")
    logger.info('.....退出登录.....')
