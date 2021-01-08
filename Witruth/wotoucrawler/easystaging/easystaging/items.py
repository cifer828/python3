# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.item import Field


class EasystagingItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class XizhiItem(scrapy.Item):
    registerId = Field()
    companyName = Field()            #公司名
    phoneNumber = Field()            #联系方式
    emailAddress = Field()           #联系邮箱
    webLinks = Field()               #网站链接
    locate = Field()                 #公司地址
    opreateCondition = Field()       #经营状况
    companyType = Field()            #公司类别
    registerTime = Field()           #注册时间
    legalPersonName = Field()        #法定代表
    registerMoney = Field()          #注册资本
    businessType = Field()           #所属行业
    businessScope = Field()          #经营范围
    shareHolderInfo = Field()        #股东信息
    investment = Field()             #对外投资情况
    crawlTime = Field()
    key = Field()

    def toString(self):
        return self.registrationNumber

class QichachaItem(scrapy.Item):
    registerId = Field()
    companyName = Field()            #公司名
    phoneNumber = Field()            #联系方式
    emailAddress = Field()           #联系邮箱
    webLinks = Field()               #网站链接
    locate = Field()                 #公司地址
    opreateCondition = Field()       #经营状况
    companyType = Field()            #公司类别
    registerTime = Field()           #注册时间
    legalPersonName = Field()        #法定代表
    registerMoney = Field()          #注册资本
    businessType = Field()           #所属行业
    businessScope = Field()          #经营范围
    shareHolderInfo = Field()        #股东信息
    investment = Field()             #对外投资情况
    crawlTime = Field()
    key = Field()
    def toString(self):
        return self.registrationNumber
class QiduoweiItem(scrapy.Item):
    registerId = Field()
    companyName = Field()            #公司名
    phoneNumber = Field()            #联系方式
    emailAddress = Field()           #联系邮箱
    webLinks = Field()               #网站链接
    locate = Field()                 #公司地址
    opreateCondition = Field()       #经营状况
    companyType = Field()            #公司类别
    registerTime = Field()           #注册时间
    legalPersonName = Field()        #法定代表
    registerMoney = Field()          #注册资本
    businessType = Field()           #所属行业
    businessScope = Field()          #经营范围
    shareHolderInfo = Field()        #股东信息
    investment = Field()             #对外投资情况
    crawlTime = Field()
    key = Field()

    def toString(self):
        return self.registrationNumber
class FundItem(scrapy.Item):
    managerName = Field()
    registerId = Field()
    crawlTime = Field()
    officeLocate = Field()
    registerMoney = Field()
    realRegisterMoney = Field()
    establishTime = Field()
    manageFundType = Field()
    webLink = Field()
    specialMessage = Field()
    fundName = Field()
    fundId = Field()

class BaiTengItem(scrapy.Item):
    patentName = Field()
    applyPerson = Field()
    patentTime = Field()
    applyId = Field()
    state = Field()
    abstract = Field()
    companyName = Field()
    crawlTime = Field()
#region 药智网Item
# 药智网五个数据库有五个Item,分别以名字相对应,item里出了每个数据库必须字段,加了一个databasetType字段用于数据库操作区分
# 其数值1-5,对应分别为：1, 国产药片数据库;2, 进口药品数据库;3, 药品注册与受理数据库;4, 中国临床试验数据库;5, 国外新药及新剂型数据库
class YaoZhiGuoChanItem(scrapy.Item):
    id = Field()
    medicineName = Field()
    englishName = Field()
    medicineSpecification = Field()
    produceIndustry = Field()
    approvalNumber = Field()
    approvalDate = Field()
    dosageForms = Field()
    medicineType = Field()
    crawlTime = Field()
    databaseType = Field()

class YaoZhiJinKouItem(scrapy.Item):
    id = Field()
    medicineName = Field()
    companyName = Field()
    date = Field()
    databaseType = Field()
    crawlTime = Field()

class YaoZhiZhuCeItem(scrapy.Item):
    id = Field()
    medicineName = Field()
    registerType = Field()
    applyType = Field()
    companyName = Field()
    processState = Field()
    stateStartDate = Field()
    crawlTime = Field()
    valueResult = Field()
    databaseType = Field()

class YaoZhiLinChuangItem(scrapy.Item):
    id = Field()
    expName = Field()
    indication = Field()
    expState = Field()
    expStage = Field()
    registerDate = Field()
    crawlTime = Field()
    databaseType = Field()

class YaoZhiGuoWaiXinYaoItem(scrapy.Item):
    id = Field()
    medicineName = Field()
    type = Field()
    companyName = Field()
    approvalCountry = Field()
    approvalDate = Field()
    effects = Field()
    introduction = Field()
    crawlTime = Field()
    databaseType = Field()

#endregion
