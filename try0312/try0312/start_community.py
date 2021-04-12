from scrapy.cmdline import execute
import redis

conn=redis.Redis(host='192.168.1.13',port=6379)
# conn.lpush('58try:xiaoqu_url','https://hz.58.com/xiaoqu/hzfudingjiayuanxiaofengyuan/')
# print(conn.lrange('58try:xiaoqu_url', 0, -1))

execute(["scrapy", "crawl", "58try"])
