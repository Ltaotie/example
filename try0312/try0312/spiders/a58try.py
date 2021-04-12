# -*- coding: utf-8 -*-
import redis
from scrapy_redis.spiders import RedisSpider
from try0312 import settings
from try0312.pipelines import ParserPipeline
from try0312.items import Community

class A58trySpider(RedisSpider):
    name = '58try'
    allowed_domains = ['58.com']
    # start_urls = ['https://hz.58.com/xiaoqu/']
    redis_cli = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT,
                            decode_responses=True)
    redis_key = '58try:xiaoqu_url'

    def parse(self, response):
        community_detail = ParserPipeline.parse_community_detail(response)
        community_item = Community()
        if self.redis_cli.sismember('58value', community_item['id']) == 0:
            self.redis_cli.sadd('58value', community_item['id'])
            print("second_hands_house", '*' * 30, community_item['url'])
            community_item.update(community_detail)
            yield community_item
        else:
            name = community_item['url']
            print(f"{name}已保存")