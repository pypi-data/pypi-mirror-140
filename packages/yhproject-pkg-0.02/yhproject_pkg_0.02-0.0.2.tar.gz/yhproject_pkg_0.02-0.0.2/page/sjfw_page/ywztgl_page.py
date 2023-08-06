# 从关键字文件导入基类
from yhproject_pkg.framework.key_word.keyword_web import WebKeys


class YwztglPage(WebKeys):
    # 新增
    def button_add(self):
        self.locator("xpath", "//*[@id='app']/section/div/div[2]/div/div[1]/button[1]").click()

    def input_ztmc(self, words_key):
        self.locator("xpath", "//*[@id='app']/section/div/div[2]/div/div[3]/div/div/div[2]/form/div[1]/div[1]/div/div/div[1]/div/input").send_keys(words_key)
        self.wait(3)

    def input_sjzt(self, words_key):
        self.locator("xpath", "//*[@id='app']/section/div/div[2]/div/div[3]/div/div/div[2]/form/div[1]/div[2]/div/div/div/div[1]/div[1]/div[2]/input").send_keys(words_key)
        self.down_keys()
        self.enter_keys()

    def input_order(self, words_key):
        self.locator("xpath", "//*[@id='app']/section/div/div[2]/div/div[3]/div/div/div[2]/form/div[2]/div[2]/div/div/div/div/input").send_keys(words_key)

    def input_ztms(self, words_key):
        self.locator("xpath", "//*[@id='app']/section/div/div[2]/div/div[3]/div/div/div[2]/form/div[3]/div/div/div/textarea").send_keys(words_key)

    def button_qr(self):
        self.locator("xpath", "//*[@id='app']/section/div/div[2]/div/div[3]/div/div/div[3]/span/button[2]").click()
        self.wait(3)

    # 查询
    def input_search(self, search_key):
        self.locator("xpath", "//*[@id='app']/section/div/div[1]/form/div/div[1]/div/div/div/input").send_keys(search_key)
        self.wait(1)
        self.locator("xpath", "//*[@id='app']/section/div/div[1]/form/div/div[2]/div/div/button[1]").click()
        self.wait(2)

    def button_reset(self):
        self.locator("xpath", "//*[@id='app']/section/div/div[1]/form/div/div[2]/div/div/button[2]").click()
        self.wait(2)

    # 编辑
    def button_edit(self):
        self.locator("xpath", "//*[@id='app']/section/div/div[2]/div/div[2]/div/div/div[2]/div[2]/table/tbody/tr[1]/td[6]/div/button[1]").click()
        self.wait(2)

    # 删除
    def button_remove(self):
        self.locator("xpath", "//*[@id='app']/section/div/div[2]/div/div[2]/div/div/div[2]/div[2]/table/tbody/tr[1]/td[6]/div/button[2]").click()
        self.wait(2)
