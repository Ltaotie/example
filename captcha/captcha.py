# -*- coding: utf-8 -*-
"""
Created by ustinian on 2021/4/14
@author: Administrator
"""
import warnings
warnings.filterwarnings("ignore")
from lxml import etree
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from PIL import Image
import time
import numpy as np
from selenium.webdriver.common.action_chains import ActionChains
import random
import math
from fake_useragent import UserAgent
from io import BytesIO
import requests
from hashlib import md5
from captcha import setting
import os

class Chaojiying_Client(object):

    def __init__(self, username, password, soft_id):
        self.username = username
        password = password.encode('utf8')
        self.password = md5(password).hexdigest()
        self.soft_id = soft_id
        self.base_params = {
            'user': self.username,
            'pass2': self.password,
            'softid': self.soft_id,
        }
        self.headers = {
            'Connection': 'Keep-Alive',
            'User-Agent': 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0)',
        }

    def PostPic(self, im, codetype):
        """
        im: 图片字节
        codetype: 题目类型 参考 http://www.chaojiying.com/price.html
        """
        params = {
            'codetype': codetype,
        }
        params.update(self.base_params)
        files = {'userfile': ('ccc.jpg', im)}
        r = requests.post('http://upload.chaojiying.net/Upload/Processing.php', data=params, files=files, headers=self.headers)
        return r.json()

    def ReportError(self, im_id):
        """
        im_id:报错题目的图片ID
        """
        params = {
            'id': im_id,
        }
        params.update(self.base_params)
        r = requests.post('http://upload.chaojiying.net/Upload/ReportError.php', data=params, headers=self.headers)
        return r.json()

class Slide(object):

    def __init__(self):
        self.root = setting.PATH
        self.headers ={
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN, zh;',
            'Connection': 'Keep-Alive',
            'User-Agent': UserAgent().random
        }

    def pic_download(self, url, name):
        try:
            r = requests.get(url, verify=False, headers=self.headers)
            path = self.root + name + ".jpg"
            with open(path, "wb") as f:
                f.write(r.content)
            print("验证码已保存")
        except Exception as e:
            print("获取失败!" + str(e))

    def run(self, distance, brow, xpath):
        element = brow.find_element_by_xpath(xpath)
        ActionChains(brow).click_and_hold(element).perform()
        remaining_dist = distance
        while remaining_dist > 0:
            ratio = remaining_dist / distance
            if ratio < 0.2:
                # 开始阶段移动较慢
                span = random.randint(5, 8)
            elif ratio > 0.8:
                # 结束阶段移动较慢
                span = random.randint(8, 12)
            else:
                # 中间部分移动快
                span = random.randint(10, 16)
            ActionChains(brow).move_by_offset(span, random.randint(-5, 5)).perform()
            remaining_dist -= span
            time.sleep(random.uniform(0.05,0.15))

        ActionChains(brow).move_by_offset(remaining_dist, random.randint(-5, 5)).perform()
        ActionChains(brow).release(on_element=element).perform()
        time.sleep(2)

def selenium_setting():
    chrome_options = webdriver.ChromeOptions()
    # chrome_options.add_argument("--headless")  # => 为Chrome配置无头模式
    chrome_options.add_experimental_option(
        "excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument('lang=zh-CN,zh,zh-TW,en-US,en')
    chrome_options.add_argument(
        f'user-agent={UserAgent().random}')
    chrome_options.add_argument("disable-blink-features=AutomationControlled")  # 就是这一行告诉chrome去掉了webdriver痕迹
    brow = webdriver.Chrome(setting.CHROME_PATH, chrome_options=chrome_options)
    return brow

# 知乎登录滑动验证码
def selenium_zhihu(usr, passw):
    brow = selenium_setting()
    brow.get(r"https://www.zhihu.com/signin?")
    WebDriverWait(brow, 10).until(EC.element_to_be_clickable((By.XPATH, "//div[@class='SignFlow-tab']")))
    brow.find_element_by_xpath(r"//div[@class='SignFlow-tab']").click()
    account = brow.find_element_by_name("username")
    account.clear()
    account.send_keys(usr)
    pwd = brow.find_element_by_name("password")
    pwd.clear()
    time.sleep(random.random())
    pwd.send_keys(passw)
    time.sleep(random.random())
    brow.find_element_by_xpath(r'//*[@id="root"]/div/main/div/div/div/div[1]/div/form/button').click()
    pic = WebDriverWait(brow, 10).until(EC.element_to_be_clickable((By.XPATH, r"//div[@class='yidun_bgimg']")))
    while pic:
        try:
            bg = brow.find_element_by_xpath('//img[@class="yidun_bg-img"]').get_attribute("src")
            slide = Slide()
            slide.pic_download(bg, "zhihu")
            chaojiying = Chaojiying_Client('', '', '')    #用户中心>>软件ID 生成一个替换 911742
            im = open(os.path.join(setting.PATH, 'zhihu.jpg'), 'rb').read()    #本地图片文件路径 来替换 a.jpg 有时WIN系统须要//
            code = chaojiying.PostPic(im, 9101)['pic_str'] #9004 验证码类型  官方网站>>价格体系
            print('code:',code)
            distance = int(code.split(",")[0])-9
            xpath = r'//span[@class="yidun_slider__icon"]'
            slide.run(distance, brow, xpath)
            print("已划完")
            element = brow.find_element_by_xpath(r'//span[@class="yidun_slider__icon"]')
            if element:
                pass
            else:
                button = brow.find_element_by_xpath(r'//*[@id="root"]/div/main/div/div/div/div[1]/div/form/button/text()')
                time.sleep(random.uniform(1,2))
                print(button)
                if button:
                    button.click()

        except:
            flag = brow.find_element_by_xpath(r"//div[@class='css-vurnku']")
            if flag:
                break
            print("未知错误")
            break

class meizu():

    def __init__(self):
        self.brow = selenium_setting()

    def node_exist(self, xpath):
        try:
            self.brow.find_element_by_xpath(xpath)
            return True
        except:
            return False

    def geetest_item_img(self):
        while True:
            try:
                self.brow.find_element_by_class_name("geetest_item_img")
                # 点触验证码
                print("点触验证码")
                self.brow.maximize_window()
                time.sleep(random.uniform(1, 2))
                geetest_item_img =  self.brow.find_element_by_class_name("geetest_item_img").get_attribute("src")
                slide = Slide()
                slide.pic_download(geetest_item_img, "meizu_touch")
                chaojiying = Chaojiying_Client('', '', '')  # 用户中心>>软件ID 生成一个替换 911742
                im = open(os.path.join(setting.PATH, 'meizu_touch.jpg'), 'rb').read()  # 本地图片文件路径 来替换 a.jpg 有时WIN系统须要//
                pic_str = chaojiying.PostPic(im, 9004)['pic_str']  # 9004 验证码类型  官方网站>>价格体系
                print('pic_str:', pic_str)
                pic_list = pic_str.split("|")
                img_element = self.brow.find_element_by_class_name('geetest_item_img')
                for pic in pic_list:
                    x, y = pic.split(',')
                    ActionChains(self.brow).move_to_element_with_offset(img_element, int(x),int(y)+4).click().perform()  # 一定要使用动作链完成！
                    time.sleep(random.uniform(0.5,1.5))
                self.brow.find_element_by_class_name("geetest_commit_tip").click()
                print("已点完")
                time.sleep(1.5)
                element = self.brow.find_element_by_xpath("/html/body/div[5]").get_attribute("style")
                if "block" in element:
                    print("pass")
                    pass
                else:
                    print("点击")
                    self.brow.find_element_by_xpath('//*[@id="login"]').click()
            except:
                nickname = self.brow.find_element_by_id("nickName")
                if nickname:
                    print("登录成功")
                    break
                print("不是点触验证码")
                break

    def geetest_slider_button(self):
        while True:
            try:
                self.brow.find_element_by_class_name("geetest_slider_button")
                print("滑动验证码")
                self.brow.maximize_window()
                screenshot = self.brow.get_screenshot_as_png()
                screenshot = Image.open(BytesIO(screenshot))
                captcha = screenshot.crop((1276, 545, 1600, 744))
                captcha.save(os.path.join(setting.PATH, "meizu_slide.jpg"))
                chaojiying = Chaojiying_Client('', '', '')  # 用户中心>>软件ID 生成一个替换 911742
                im = open(os.path.join(setting.PATH, "meizu_slide.jpg"), 'rb').read()  # 本地图片文件路径 来替换 a.jpg 有时WIN系统须要//
                code = chaojiying.PostPic(im, 9101)['pic_str']  # 9004 验证码类型  官方网站>>价格体系
                print('code:', code)
                distance = int(code.split(",")[0]) - 9
                slide = Slide()
                xpath = r'//div[@class="geetest_slider_button"]'
                slide.run(distance, self.brow, xpath)
                print("已划完")
                time.sleep(random.uniform(1, 2))
                self.brow.find_element_by_xpath('//*[@id="login"]').click()
                # element = brow.find_element_by_xpath(r'//div[@class="geetest_slider_button"]')
            except:
                nickname = self.brow.find_element_by_id("nickName")
                if nickname:
                    print("登录成功")
                    break
                print("不是滑动验证码")
                break

    def selenium_meizu(self, usr, passw):
        self.brow.get(r"https://login.flyme.cn")
        WebDriverWait(self.brow, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="cycode-box"]')))
        account = self.brow.find_element_by_id("account")
        account.clear()
        account.send_keys(usr)
        pwd = self.brow.find_element_by_id("password")
        pwd.clear()
        time.sleep(random.random())
        pwd.send_keys(passw)
        time.sleep(random.random())
        self.brow.find_element_by_xpath(r'//div[@class="geetest_radar_tip"]').click()
        time.sleep(1)
        style_flag = self.node_exist("//div[@class='geetest_fullpage_click_box']/div")
        style = ""
        if style_flag:
            style = self.brow.find_element_by_xpath("//div[@class='geetest_fullpage_click_box']/div").get_attribute("class")
            print(style)
        if style == "geetest_holder geetest_silver":
            self.geetest_item_img()

        if style == "geetest_holder geetest_mobile geetest_ant geetest_embed":
            self.geetest_slider_button()

        self.brow.find_element_by_class_name("fullBtnBlue").click()

if __name__ == '__main__':
    # selenium_zhihu("", "")
    meizu = meizu()
    meizu.selenium_meizu("", "")