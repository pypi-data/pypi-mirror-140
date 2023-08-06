import pytest
import pyautogui
from yhproject_pkg.framework.data_driver.yaml_driver import load_yaml
from yhproject_pkg.framework.page.login_page.login_page import LoginPage
from yhproject_pkg.framework.page.login_page.menu_page import MenuPage
from yhproject_pkg.framework.page.sjgk_page.fjgl_page import FjglPage
import allure
import logging

logger = logging.getLogger(__name__)


@allure.feature('分级管理')
@allure.title('登录')
@pytest.mark.parametrize('data', load_yaml('../../data/login/login1.yaml'))
def test_login_fjgl(browser, data):
    page = LoginPage(browser)
    browser.maximize_window()
    page.open(data["url"])
    page.input_user(data["user"])
    page.input_password(data["password"])
    page.button_remember()
    page.button_login()
# 登录跳转
    page.switch_window(-1)
    page.assert_att("赢和数据")
    logger.info('------------进入分级管理模块-------------')


@allure.feature('分级管理')
@pytest.mark.parametrize('data', load_yaml('../../data/login/menu.yaml'))
@allure.title('打开菜单_分类管理')
def test_menu_fjgl(browser, data):
    page = MenuPage(browser)
    page.table_manage()
    page.menu_icon()
    page.menu_sjgk()
    page.sjgk_sjflfj_sjfj()
    # 切换iframe
    page.sjgk_sjfj_iframe()
    page.assert_att("分级管理")
    logger.info('01进入菜单成功')


@allure.feature('分级管理')
@allure.title('版本管理_分级管理')
def test_local_verfjgl(browser):
    page = FjglPage(browser)
    page.button_vermg()
    page.assert_att("版本名称")
    logger.info("02切换tab版本管理成功")


@allure.feature('分级管理')
@pytest.mark.parametrize('data', load_yaml('../../data/sjgk/fjgl.yaml'))
@allure.title('版本新增_分级管理')
def test_add_verfjgl(browser, data):
    page = FjglPage(browser)
    page.button_veradd()
    page.wait(2)
    page.input_verid(data['verid'])
    page.input_vername(data['vername'])
    page.input_vertext(data['vertext'])
    page.button_addline()
    page.input_mglevelid(data['mglevelid'])
    page.input_mglevelname(data['mglevelname'])
    page.input_mgleveldetail(data['mgleveldetail'])
    page.box_checkture()
    page.button_addline()
    page.input_mglevelid1(data['mglevelid1'])
    page.input_mglevelname1(data['mglevelname1'])
    page.input_mgleveldetail1(data['mgleveldetail1'])
    page.box_checkture1()
    page.button_levelqr()
    page.assert_att("操作成功")
    logger.info("03版本新增成功")


@allure.feature('分级管理')
@pytest.mark.parametrize('data', load_yaml('../../data/sjgk/fjgl.yaml'))
@allure.title('版本查询_分级管理')
def test_search_verfjgl(browser, data):
    page = FjglPage(browser)
    page.input_mgsearch('error')
    page.assert_att('暂无数据')
    page.button_mgreset()
    page.input_mgsearch(data["verid"])
    page.assert_att(data["verid"])
    logger.info('04版本查询成功')


@allure.feature('分级管理')
@pytest.mark.parametrize('data', load_yaml('../../data/sjgk/fjgl.yaml'))
@allure.title('版本启用_分级管理')
def test_switch_verfjgl(browser, data):
    page = FjglPage(browser)
    page.button_switch()
    page.assert_att("禁用")
    page.button_fjgl()
    page.button_reset()
    page.assert_att(data['mglevelname'])
    page.assert_att(data['mglevelname1'])
    logger.info('05版本启用并切换tab分级管理成功')


@allure.feature('分级管理')
@pytest.mark.parametrize('data', load_yaml('../../data/sjgk/fjgl.yaml'))
@allure.title('新增分级_分级管理')
def test_add_fjgl(browser, data):
    page = FjglPage(browser)
    page.button_sjadd()
    page.input_sjlevel(data['level'])
    page.input_sjlevelname(data['levelname'])
    page.input_sjleveldetail(data['leveldetail'])
    page.input_sjremark(data['remark'])
    page.button_sjqr()
    page.assert_att("操作成功")
    logger.info('06新增分级成功')


@allure.feature('分级管理')
@pytest.mark.parametrize('data', load_yaml('../../data/sjgk/fjgl.yaml'))
@allure.title('查询分级_分级管理')
def test_search_fjgl(browser, data):
    page = FjglPage(browser)
    page.input_search('error')
    page.assert_att("暂无数据")
    page.button_reset()
    page.input_search(data["levelname"])
    page.assert_att(data['levelname'])
    logger.info('07分级查询成功')


@allure.feature('分级管理')
@pytest.mark.parametrize('data', load_yaml('../../data/sjgk/fjgl.yaml'))
@allure.title('编辑分级_分级管理')
def test_edit_fjgl(browser, data):
    page = FjglPage(browser)
    page.button_sjedit()
    page.input_sjremark('aaa')
    page.button_sjqr()
    page.button_reset()
    page.input_search('aaa')
    page.assert_att('aaa')
    logger.info('08分级编辑成功')


@allure.feature('分级管理')
@pytest.mark.parametrize('data', load_yaml('../../data/sjgk/fjgl.yaml'))
@allure.title('删除分级_分级管理')
def test_remove_fjgl(browser, data):
    page = FjglPage(browser)
    page.button_remove()
    page.assert_att('暂无数据')
    logger.info('09分级删除成功')


@allure.feature('分级管理')
@pytest.mark.parametrize('data', load_yaml('../../data/sjgk/fjgl.yaml'))
@allure.title('版本编辑_分级管理')
def test_edit_verfjgl(browser, data):
    page = FjglPage(browser)
    page.button_vermg()
    page.button_veredit()
    page.input_vertext("sss")
    page.button_levelqr()
    page.button_mgreset()
    page.input_mgsearch(data['vertext']+'sss')
    page.assert_att(data['vertext']+'sss')
    logger.info('10版本编辑成功')


@allure.feature('分级管理')
@pytest.mark.parametrize('data', load_yaml('../../data/sjgk/fjgl.yaml'))
@allure.title('版本删除_分级管理')
def test_remove_verfjgl(browser, data):
    page = FjglPage(browser)
    page.button_verremove()
    page.assert_att("请先禁用该版本")
    page.button_switch()
    page.button_verremove()
    page.enter_keys()
    page.assert_att("操作成功")
    page.button_mgreset()
    page.input_mgsearch(data["verid"])
    page.assert_att("暂无数据")
    logger.info('11版本删除成功')


@allure.feature('分级管理')
@allure.title('退出登录')
def test_fjgl_logout(browser):
    page = LoginPage(browser)
    page.reback_iframe()
    page.button_user()
    pyautogui.click(2428, 391)
    page.wait(2)
    page.assert_att("赢和数据")
    logger.info('.....退出登录.....')
