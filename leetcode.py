import random
import time
import re
from selenium import webdriver

import settings

USER_AGENT_LIST = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:54.0) Gecko/20100101 Firefox/54.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/603.3.8 (KHTML, like Gecko) Version/10.1.2 Safari/603.3.8",
]
chrome_options = webdriver.ChromeOptions()


class LeetCodeSpider:

    def __init__(self, driver, is_headless=False):
        self.opt = self.set_options(chrome_options, is_headless)  # 配置
        self.driver = webdriver.Chrome(driver, chrome_options=self.opt)  # 驱动器
        self.__cookies = None
        self.__daily = None

    def login(self, username, password):
        # 登录后返回到题库页面
        url = "https://leetcode.cn/accounts/login/?next=%2Fproblemset%2Fall%2F"
        self.driver.get(url)
        self._wait("正在启动浏览器...")

        # 防止js检测到selenium的属性
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        self._wait("防止js检测selenium...")

        # switch_to_signInWithPassword
        self.get_elements_by_xpath('//*[@id="lc-content"]/div/div/div/div/div[6]/div')[0].click()
        self._wait("登录中...（切为密码登录）")
        # T&C
        self.get_elements_by_xpath('//*[@id="lc-content"]/div/div/div/div/div[8]/div/span[1]')[0].click()
        self._wait("登录中...（勾选条款）")

        inputArray = self.get_elements_by_xpath("//input")
        self._wait("登录中...（获取登录DOM元素）")
        for inp in inputArray:
            attr = inp.get_attribute("placeholder")
            if attr == "手机/邮箱":
                inp.send_keys(username)
            elif attr == "输入密码":
                inp.send_keys(password)
            self._wait("登录中...（正在输入登录信息）")

        # 点击登录按钮
        self.get_elements_by_xpath('//*[@id="lc-content"]/div/div/div/div/button')[0].click()
        for _ in range(2):
            self._wait("等待页面切换...")

        self.__cookies = self.driver.get_cookies()
        return self.__cookies

    def daily_question(self):
        from datetime import datetime

        if not self.__cookies:
            raise Exception("请先登录！")

        # daily_href = self.__daily
        # 该对象今天已经访问过了，直接返回保存的对象
        if self.__daily and self.__daily[2] == datetime.now().day:
            return self.__daily
        elif self.__daily and self.__daily[2] != datetime.now().day:  # 若不是今日的每日一题
            self.driver.get("https://leetcode.cn/problemset/all/")

        daily_href = self.get_elements_by_xpath(f'//*[@id="__next"]/div/div[2]/div[1]/div[2]/div[1]/div/div[3]//a[{datetime.now().day}]')[0].get_attribute("href")
        print(daily_href)
        if not daily_href:
            raise Exception("获取每日一题失败！")
        self._wait("已获取每日一题URL...")

        # 访问每日一题
        self.driver.get(daily_href)
        self._wait("正在访问每日一题...")

        # 获取每日一题的内容
        title = self.get_elements_by_xpath('//*[@id="question-detail-main-tabs"]/div[2]/div/div[1]')[0].text
        content = self.get_elements_by_xpath('//*[@id="question-detail-main-tabs"]/div[2]/div/div[2]')[0].text

        title = " ".join(title.split('\n')[:-2])
        reg_content = re.compile("\s{2}.*?：")  # 匹配具有空格的：
        for i in reg_content.findall(content):
            r = re.split('\n[\s]*', i)[1]
            content = content.replace(i, "\n" + r)

        # self.__daily = daily_href  # test使用
        self.__daily = (title, content, datetime.now().day)
        print(title)
        print("=" * 50)
        print(content)
        return self.__daily

    def get_elements_by_xpath(self, _value):
        ele = self.driver.find_elements(by='xpath', value=_value)
        return ele

    @staticmethod
    def set_options(options, is_headless=False):
        # 是否不显示浏览器（默认显示）
        if is_headless:
            options.add_argument('--headless')
            options.add_argument('--disable-gpu')

        # User-agent
        options.add_argument(f"user-agent={random.choice(USER_AGENT_LIST)}")

        # Proxy
        # ...

        return options

    @staticmethod
    def _wait(info):
        print(info)
        time.sleep(2)
        return

    def close(self):
        self.driver.close()


if __name__ == '__main__':
    leet_code = LeetCodeSpider("./chromedriver_mac_arm64/chromedriver", is_headless=True)
    leet_code.login(settings.LEETCODE_USERNAME, settings.LEETCODE_PASSWORD)
    # while True:
    #     inp = input("switch:")
    #     if inp == "1":
    #         print(leet_code.daily_question())
    #     else:
    #         break
    leet_code.daily_question()
    leet_code.close()

#TODO 捕获报错
#TODO 代码测试功能
# （URL https://leetcode.cn/problems/determine-if-two-events-have-conflict/interpret_solution/ ）
# （METHOD POST）
# （DATA {
#     "question_id": "2536",
#     "lang": "cpp",
#     "typed_code": "class Solution {\npublic:\n    bool haveConflict(vector<string>& event1, vector<string>& event2) {\n        \n    }\n};",
#     "data_input": "[\"01:15\",\"02:00\"]\n[\"02:00\",\"03:00\"]",
#     "test_mode": false,
#     "judge_type": "large",
#     "test_judger": ""
# }）
