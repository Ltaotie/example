# -*- coding: utf-8 -*-
import scrapy
import redis
from scrapy_redis.spiders import RedisSpider
from try0312 import settings
from try0312.pipelines import Second_hands_Pipeline
from try0312.items import Second_hands
from scrapy.http import Request
import time
import re

class A58trySpider(RedisSpider):
    name = 'second_hands'
    allowed_domains = ['58.com']
    # start_urls = ['https://hz.58.com/xiaoqu/']
    redis_cli = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT,
                            decode_responses=True)
    redis_key = '58try:second_hands_url'

    def parse(self, response):
        second_hands = response.xpath(r"//div[@tongji_tag='fcpc_ersflist_gzcount']/a/@href").extract()
        name = response.xpath(r'//div[@class="community-info-detail-title"]/h3/text()').extract()
        print(f"爬取{name}中")
        for second in second_hands:
            second = re.sub(r'=(\d{9,11})', '=' + str(int(time.time())), second)
            yield Request(url=second,
                          callback=self.parse_second_html,
                          # errback=self.seconds_errback,
                          meta={'donwload_timeout': 5,
                                'dont_redirect':True,
                                'handle_httpstatus_list':[301,302]
                                },
                          priority=10,
                          dont_filter=True,
                          )

    def parse_second_html(self, response):
        # 生成二手房信息
        second_detail = Second_hands_Pipeline.parse_second_hands_house(response)
        second_item = Second_hands()
        if self.redis_cli.sismember('58value', second_item['id']) == 0:
            self.redis_cli.sadd('58value', second_item['id'])
            second_item.update(second_detail)
            print('community','*'*30,second_item['url'])
            yield second_item
        else:
            name = second_item['url']
            print(f"{name}已保存")