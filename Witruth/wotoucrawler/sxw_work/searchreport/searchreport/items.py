# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class SearchreportItem(scrapy.Item):
    # define the fields for your item here like:
    artname=scrapy.Field()
    arturl=scrapy.Field()
    arttype=scrapy.Field()
    artdate=scrapy.Field()
    artcompany=scrapy.Field()
    searchpeople=scrapy.Field()
    content=scrapy.Field()
    #pass
