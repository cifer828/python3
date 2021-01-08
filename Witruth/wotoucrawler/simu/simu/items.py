# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class SimuItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    id = scrapy.Field()
    fundName = scrapy.Field()
    fundNo = scrapy.Field()
    managerName = scrapy.Field()
    managerType = scrapy.Field()
    workingState = scrapy.Field()
    putOnRecordDate = scrapy.Field()
    lastQuarterUpdate =  scrapy.Field()
    isDeputeManage = scrapy.Field()
    url = scrapy.Field()
    establishDate = scrapy.Field()
    managerUrl = scrapy.Field()

