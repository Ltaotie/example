from scrapy.cmdline import execute
import sys
import os
import redis

conn=redis.Redis(host='192.168.1.13',port=6379)
# conn.lpush('58try:second_hands_url','https://hz.58.com/ershoufang/?param1572=2128048')


execute(["scrapy", "crawl", "second_hands"])