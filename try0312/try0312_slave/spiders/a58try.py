# -*- coding: utf-8 -*-
import redis
from scrapy_redis.spiders import RedisSpider
from try0312_slave import settings
from scrapy.http import Request

class A58trySpider(RedisSpider):
    name = '58_slave'
    allowed_domains = ['58.com']
    # start_urls = ['https://hz.58.com/xiaoqu/']
    redis_cli = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT,
                            decode_responses=True)
    redis_key = '58try:start_url'
    XIAOQU_PAGE = 1

    def parse(self, response):
        xiaoqu_list_cell = response.xpath(r'//div[@class="list-cell"]/a/@href').extract()
        for cell in xiaoqu_list_cell:
            self.redis_cli.rpush('58try:xiaoqu_url', cell)

        second_hands = response.xpath(r"//span[@class='detail-link'][1]//a[@target='_blank']/@href").extract()
        for second in second_hands:
            yield Request(url=second,
                          callback=self.parse_second_html,
                          errback=self.seconds_errback,
                          # priority=7,
                          meta={'start_url':second,
                                "index":0},
                          dont_filter=True,
                          )
        # 全部页数爬取
        # active = response.xpath(r"//a[@class='next next-active']")
        # if len(active) == 1:
        #     xiaoqu_page = "p" + str(self.XIAOQU_PAGE + 1)
        #     ex_xiaoqu_page = "p" + str(self.XIAOQU_PAGE)
        #     xiaoqu_next_url = str(response.url).replace(ex_xiaoqu_page, xiaoqu_page)
        #     self.XIAOQU_PAGE += 1
        #     yield Request(url=xiaoqu_next_url,
        #                   callback=self.parse,
        #                   errback=self.seconds_errback,
        #                   dont_filter=True,
        #                   )

    def parse_second_html(self, response):
        # 取得二手房url
        urls = response.xpath(r"//div[@tongji_tag='fcpc_ersflist_gzcount']/a/@href").extract()
        for url in urls:
            self.redis_cli.rpush('58try:second_hands_url', url)
        forbid = response.xpath(r"//a[@class='next click-forbid']")
        if len(forbid)==0:
            ex = response.meta['start_url'].split("?")
            i = response.meta['index']
            next_url = ex[0] + f"p{str(i)}/?" + ex[1]
            i += 1
            second =  response.meta['start_url']
            yield Request(
                url = next_url,
                callback=self.parse_second_html,
                errback=self.seconds_errback,
                meta={'start_url': second,
                      "index": i},
                dont_filter=True,
            )

    def seconds_errback(self, failure):
        self.logger.info(repr(failure))
        self.crawler.stats.inc_value('Failed_Request_Seconds')
