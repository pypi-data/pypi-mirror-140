# 从关键字文件导入基类
from yhproject_pkg.framework.key_word.keyword_web import WebKeys


class SjtmPage(WebKeys):
    def input_ora(self, word_keys):
        self.locator("xpath", "//*[@id='app']/section/div/div/div[1]/div/div/div[2]/div[1]/input").clear()
        self.wait(2)
        self.locator("xpath", "//*[@id='app']/section/div/div/div[1]/div/div/div[2]/div[1]/input").send_keys(word_keys)
        self.wait(5)

    def input_col(self, word_keys):
        self.locator("xpath", "//*[@id='app']/section/div/div/div[2]/div/div/div[1]/div[2]/div/input").send_keys(word_keys)
        self.wait(2)
        self.locator("xpath", "//*[@id='app']/section/div/div/div[2]/div/div/div[1]/div[2]/button[1]").click()
        self.wait(2)

    def icon_ora(self):
        self.locator("xpath", "//*[@id='app']/section/div/div/div[1]/div/div/div[2]/div[2]/div[2]/div[2]/div/div[2]/div/div[2]/div/div[1]/div/div/span").click()
        self.wait(2)

    def icon_tab(self):
        self.locator("xpath", "//*[@id='app']/section/div/div/div[1]/div/div/div[2]/div[2]/div[2]/div[2]/div/div[2]/div/div[2]/div/div[2]/div[50]/div[1]/div/div/span").click()
        self.wait(5)

    def button_reset(self):
        self.locator("xpath", "//*[@id='app']/section/div/div/div[2]/div/div/div[1]/div[2]/button[2]").click()
        self.wait(2)

    def input_rule(self, word_keys):
        self.locator("xpath", "//*[@id='app']/section/div/div/div[2]/div/div/div[2]/div[3]/table/tbody/tr/td[6]/div/div/div/input").send_keys(word_keys)
        self.up_keys()
        self.enter_keys()
        self.wait(5)






