# -*- coding: utf-8 -*-
"""
Created by ustinian on 2021/2/28
@author: Administrator
"""
import requests
import redis
from try0312.settings import REDIS_HOST, REDIS_PORT, IP_URL
import time
from scrapy.cmdline import execute
import sys
import os

class ip_pool():

    def __init__(self):
        self.rd = redis.Redis(host=REDIS_HOST, port=REDIS_PORT)

    def run(self):
        while True:
            if self.rd.llen('ip') < 14:
                self.get_ip()
            else:
                time.sleep(1)

    def get_ip(self):
        res = requests.get(IP_URL).text
        ip_list = res.split("\n")[:-1]
        print(ip_list)
        print("-"*50, "获取ip", '-'*50)
        for i in ip_list:
            self.rd.lpush('ip', i)

if __name__ == '__main__':
    conn = redis.Redis(host='192.168.1.13', port=6379)
    conn.lpush('58try:start_url', 'https://hz.58.com/xiaoqu/p1/')
    ip_run = ip_pool()
    ip_run.run()