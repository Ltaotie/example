# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import hashlib
import logging
import pymysql
from try0312.items import Community, Second_hands
import requests
import base64

def hex(url):
    if isinstance(url, str):
        url = url.encode("utf-8")
        m = hashlib.md5()
        m.update(url)
        return m.hexdigest()

class Try0312Pipeline(object):
    def process_item(self, item, spider):
        return item

class ParserPipeline(object):

    @classmethod
    def parse_community_detail(cls, response):
        """
        解析小区详情
        """
        result = dict()
        try:
            result['url'] = response.url.split('/')[-2]
            result['av_price'] = response.xpath("//span[@class='price']/text()").extract_first().strip()
            result['Shan_Quan_f'] = response.xpath("//a[@class='sq-link'][1]/text()").extract_first().strip()
            result['Shan_Quan_s'] = str(response.xpath("//a[@class='sq-link'][2]/text()").extract_first().strip())
            infos = response.xpath("//td[@class='desc']/text()").extract()
            result['detail_address'] = infos[3].strip()
            result['building_category'] = infos[4].strip()
            result['housholds'] = infos[5].strip()
            result['property_category'] = infos[6].strip()
            result['property_expenses'] = infos[7].strip()
            result['tunure'] = infos[8].strip()
            result['volume_rate'] = infos[9].strip()
            result['construction_age'] = infos[10].strip()
            result['greening_rate'] = infos[11].strip()
            result['construction_area'] = infos[12].strip()
            result['parking_space'] = infos[13].strip()
            result['property_company'] = infos[14].strip()
            result['developer'] = infos[15].strip()
            on = response.xpath("//a[@class='fy-link']/span/text()").extract()
            if len(on) == 2:
                result['on_sale'] = on[0].strip()
                result['on_rental'] = on[1].strip()
            else:
                result['on_sale'] = response.xpath("//span[@class='fy-link']/text()").extract()[0]
                result['on_rental'] = response.xpath("///a[@class='fy-link']/span/text()").extract()[0]
            id = "".join(result)
            result['id'] = hex(id)
            return result

        except Exception as e:
            print(e)


class MysqlPipeline:
    def __init__(self):
        self.connect = pymysql.connect(host='localhost', user='root', db='58city', port=3306,charset="utf8")
        self.cursor = self.connect.cursor()
    def process_item(self, item, spider):
        if isinstance(item, Community):
            self.cursor.execute("insert into community VALUES ('{}','{}','{}','{}','{}','{}','{}','{}','{}','{}',\
                                        '{}','{}','{}','{}','{}','{}','{}','{}','{}','{}')".format(
                item['id'],
                item['url'],
                item['av_price'],
                item['Shan_Quan_f'],
                item['Shan_Quan_s'],
                item['detail_address'],
                item['building_category'],
                item['housholds'],
                item['property_category'],
                item['volume_rate'],
                item['property_expenses'],
                item['tunure'],
                item['construction_age'],
                item['greening_rate'],
                item['construction_area'],
                item['parking_space'],
                item['property_company'],
                item['developer'],
                item['on_sale'],
                item['on_rental'],
            ))
            self.connect.commit()
        if isinstance(item, Second_hands):
            self.cursor.execute("insert into second_hands VALUES ('{}','{}','{}','{}','{}','{}','{}','{}','{}','{}',\
                                        '{}','{}')".format(
            item['id'],
            item['url'],
            item['price'],
            item['avgprice_price'],
            item['info_1'],
            item['info_2'],
            item['info_3'],
            item['info_4'],
            item['info_5'],
            item['info_6'],
            item['xiao_qu'],
            item['qu_yu'],
            ))
            self.connect.commit()
        return item
    def close_spider(self,spider):
        self.cursor.close()
        self.connect.close()

class Second_hands_Pipeline(object):

    @classmethod
    def parse_second_hands_house(cls, response):
        """
        解析二手房详情
        """
        result = dict()
        try:
            result['url'] = response.url.split(".shtml")[0].split('/')[-1]
            result['id'] = hex(result['url'])
            result['price'] = response.xpath("//span[@class='maininfo-price-num']/text()").extract_first().strip() + '万'
            result['avgprice_price'] = response.xpath("//div[@class='maininfo-avgprice-price']/text()").extract_first().split('/')[0].strip()
            maininfo = response.xpath("//div[@class='maininfo-model-strong']")
            result['info_1'] = ''.join(maininfo[0].xpath(r".//text()").extract_first().strip())  # 3室2厅2卫
            result['info_2'] = ''.join(maininfo[1].xpath(r".//text()").extract_first().strip())  # 184.77㎡
            result['info_3'] = ''.join(maininfo[2].xpath(r".//text()").extract_first().strip())  # 南北
            weaks = response.xpath(r"//div[@class='maininfo-model-weak']/text()").extract()
            result['info_4'] = weaks[0].strip()  # 低层(共17层)
            result['info_5'] = weaks[1].strip()  # 简单装修
            result['info_6'] = pymysql.escape_string(weaks[2].strip())  # 2005年竣工/普通住宅
            result['xiao_qu'] = response.xpath(r'//a[@tongji_tag="fcpc_detail_esf_hz_xiaoqu"]/text()').extract_first().strip()
            names = response.xpath(r'//span[@class="maininfo-community-item-name"]/a[@class="anchor anchor-weak"]/text()').extract()
            result['qu_yu'] = names[0].strip() + names[1].strip()
            id = "".join(result)
            result['id'] = hex(id)
            return result
        except Exception as e:
            print(e)