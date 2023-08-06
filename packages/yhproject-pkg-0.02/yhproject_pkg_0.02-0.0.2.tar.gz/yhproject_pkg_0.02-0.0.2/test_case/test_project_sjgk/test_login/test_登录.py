import pytest
import pyautogui
from yhproject_pkg.framework.data_driver.yaml_driver import load_yaml
from yhproject_pkg.framework.page.login_page.login_page import LoginPage
import allure
import logging

logger = logging.getLogger(__name__)


@allure.feature('测试登录')
@allure.title('打开登录页面')
@pytest.mark.parametrize('data', load_yaml('../../data/login/login1.yaml'))
def test_login(browser, data):
    page = LoginPage(browser)
    page.driver.maximize_window()
    page.open(data["url"])
    page.assert_att("赢和数据")
    logger.info('打开登录页面')


@allure.feature('测试登录')
@allure.title('账号密码均为空')
def test_login1(browser):
    page = LoginPage(browser)
    page.button_login()
    page.assert_att("用户名为空")
    logger.info("账号密码均为空")


@allure.feature('测试登录')
@allure.title('密码为空')
@pytest.mark.parametrize('data', load_yaml('../../data/login/login1.yaml'))
def test_login2(browser, data):
    page = LoginPage(browser)
    page.input_user(data["user"])
    page.button_login()
    page.assert_att("密码为空")
    page.clear_user()
    logger.info("密码为空")


@allure.feature('测试登录')
@allure.title('密码不正确')
@pytest.mark.parametrize('data', load_yaml('../../data/login/login1.yaml'))
def test_login3(browser, data):
    page = LoginPage(browser)
    page.input_user(data["user"])
    page.input_password("123456")
    page.button_login()
    page.assert_att("密码不正确")
    page.clear_user()
    page.clear_password()
    logger.info("密码不正确")


@allure.feature('测试登录')
@allure.title('密码账号正确登录成功')
@pytest.mark.parametrize('data', load_yaml('../../data/login/login1.yaml'))
def test_login4(browser, data):
    page = LoginPage(browser)
    page.clear_user()
    page.input_user(data["user"])
    page.clear_password()
    page.input_password(data["password"])
    page.button_remember()
    page.button_login()
# 登录跳转
    page.switch_window(-1)
    page.assert_att("数据管控")
    logger.info("登录成功")


@allure.feature('测试登录')
@allure.title('退出登录')
def test_login_logout(browser):
    page = LoginPage(browser)
    page.reback_iframe()
    page.button_user()
    pyautogui.click(2428, 391)
    page.wait(2)
    page.assert_att("赢和数据")
    logger.info('.....退出登录.....')

