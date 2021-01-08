# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.item import Item, Field


class TutorialItem(scrapy.Item):
    # define the fields for your item here like:
    # name = Field()
    pass

class wotouItem(scrapy.Item):
    companyName = Field()            #公司名
    phoneNumber = Field()            #联系方式
    emailAddress = Field()           #联系邮箱
    webLinks = Field()               #网站链接
    locate = Field()                 #公司地址
    opreateCondition = Field()       #经营状况
    companyType = Field()            #公司类别
    establishDate = Field()          #成立日期
    legalPersonName = Field()        #法定代表
    registerCapital = Field()        #注册资本
    businessType = Field()           #所属行业
    businessScope = Field()          #经营范围
    shareHolderInfor = Field()       #股东信息
    employeeMember = Field()         #从业人数
    sponsor = Field()                #发起人
    fundingInfor = Field()           #出资情况
    investment = Field()             #对外投资情况
