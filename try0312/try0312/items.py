# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class Try0312Item(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class Community(scrapy.Item):
    table = 'community'
    id = scrapy.Field()  # 唯一标识
    url = scrapy.Field()
    av_price = scrapy.Field()  # 2月挂牌均价
    Shan_Quan_f = scrapy.Field()  # 商圈，第一个
    Shan_Quan_s = scrapy.Field()  # 商圈，第2个
    detail_address = scrapy.Field()  # 	详细地址
    building_category = scrapy.Field()
    housholds = scrapy.Field()
    property_category = scrapy.Field()
    volume_rate = scrapy.Field()
    property_expenses = scrapy.Field()
    tunure = scrapy.Field()
    construction_age = scrapy.Field()
    greening_rate = scrapy.Field()
    construction_area = scrapy.Field()
    parking_space = scrapy.Field()
    property_company = scrapy.Field()
    developer = scrapy.Field()
    on_sale = scrapy.Field()
    on_rental = scrapy.Field()

class Second_hands(scrapy.Item):
    table = 'second_hands'
    id = scrapy.Field()  # 唯一标识
    url = scrapy.Field()
    price = scrapy.Field()
    avgprice_price = scrapy.Field()
    info_1 = scrapy.Field()
    info_2 = scrapy.Field()
    info_3 = scrapy.Field()
    info_4 = scrapy.Field()
    info_5 = scrapy.Field()
    info_6 = scrapy.Field()
    xiao_qu = scrapy.Field()
    qu_yu = scrapy.Field()
