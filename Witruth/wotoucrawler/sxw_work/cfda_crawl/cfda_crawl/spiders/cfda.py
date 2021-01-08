# -*- coding: utf-8 -*-
import scrapy
import urllib
import math
import re
import cfda_crawl.items
from cfda_crawl.items import DomesticdrugItem
from cfda_crawl.items import DomesticdruggoodsItem
from cfda_crawl.items import ImporteddrugItem
from cfda_crawl.items import ImporteddruggoodsItem
from cfda_crawl.items import DrugprotectionItem
from cfda_crawl.items import ProductionCompanyItem
from cfda_crawl.items import ManagementCompanyItem
from cfda_crawl.items import ChineseMediInstrumentItem
from cfda_crawl.items import ImportedMediInstrumentItem
from cfda_crawl.items import MediInstrumentRecordsItem


class BaiTengSpider(scrapy.Spider):
    name = "cfda"
    allowed_domains = ["qy1.sfda.gov.cn",'app1.sfda.gov.cn']
    needCt = 0
    realGetCt = 0
    connector = ''  #数据库连接接口
    start_urls = [
        "http://qy1.sfda.gov.cn/datasearch/face3/dir.html"
    ]
    base_url='http://app1.sfda.gov.cn/datasearch/face3/'
    SEARCH_URL = 'http://app1.sfda.gov.cn/datasearch/face3/search.jsp?'
    CONTENT_URL = 'http://app1.sfda.gov.cn/datasearch/face3/content.jsp?'
    #location:该类别对应的网页上的位置
    #tableId
    #tableName
    #title:对应类别中文转换成字符序列
    #bcId
    #item:每个类别所需要创建的不同的item
    #itemdict：每个item所需要爬取的字段，每个字段对应有两个数，第一个数是所在行数，第二个数是标示是否有超链接

    indexdict={
        u'国产药品':
            {'location':(7,1,1),
             'tableId':'25',
             'tableName':'TABLE25',
             'title':'%B9%FA%B2%FA%D2%A9%C6%B7',
             'bcId':'124356560303886909015737447882',
             'tableView':'%E9%8D%A5%E6%88%92%E9%AA%87%E9%91%BD%EE%88%9A%E6%90%A7',
             'viewtitleName':'COLUMN167',
             'item':DomesticdrugItem(),
             'itemdict':{'permit_num':[2,0],'english_name':[4,0],'chinese_name':[3,0],'dosage':[5,0],'produce_com':[8,1],'product_type':[10,0],
                        'medicine_benwei_code':[13,0],'approval_date':[11,0]}},
        u'国产药品商品名':
            {'location':(7,2,1),
             'tableId':'32',
             'tableName':'TABLE32',
             'title':'%B9%FA%B2%FA%D2%A9%C6%B7%C9%CC%C6%B7%C3%FB',
             'bcId':'124356639813072873644420336632',
             'tableView':'%E5%9B%BD%E4%BA%A7%E8%8D%AF%E5%93%81%E5%95%86%E5%93%81%E5%90%8D',
             'viewtitleName': 'COLUMN302',
             'item':DomesticdruggoodsItem(),
             'itemdict':{'permit_num':[2,0],'english_name':[5,0],'chinese_name':[4,0],'dosage':[9,0],'produce_com':[7,1],
                        'product_type':[10,0],'medicine_benwei_code':[13,0],'approval_date':[11,0],'goods_name':[6,0]}},
        u'进口药品商品名':
            {'location':(7,4,1),
             'tableId':'60',
             'tableName':'TABLE60',
             'title':'%BD%F8%BF%DA%D2%A9%C6%B7%C9%CC%C6%B7%C3%FB',
             'bcId':'124356657303811869543019763051',
             'tableView': '%E8%BF%9B%E5%8F%A3%E8%8D%AF%E5%93%81%E5%95%86%E5%93%81%E5%90%8D',
             'viewtitleName': 'COLUMN649',
             'item':ImporteddruggoodsItem(),
             'itemdict':{'registration_number':[2,0],'product_type':[30,0],'dosage':[16,0],'goods_chinese_name':[8,0],'goods_english_name':[9,0],
                        'english_name':[7,0],'chinese_name':[6,0],'company_chinese_name':[10,0],'company_english_name':[11,0],
                        'nation_chinese_name':[14,0],'nation_english_name':[15,0],'producer_chinese_name':[19,0],'producer_english_name':[20,0],
                        'producer_nation_chinese_name':[23,0],'producer_nation_english_name':[24,0],'limited_date':[26,0],'certificated_issue_date':[25,0]}},
        u'中药保护品种':
            {'location':(7,6,1),
             'tableId':'22',
             'tableName':'TABLE22',
             'title':'%D6%D0%D2%A9%B1%A3%BB%A4%C6%B7%D6%D6',
             'bcId':'124356646179610926452650807501',
             'tableView': '%E4%B8%AD%E8%8D%AF%E4%BF%9D%E6%8A%A4%E5%93%81%E7%A7%8D',
             'viewtitleName': 'COLUMN141',
             'item':DrugprotectionItem(),
             'itemdict':{'produce_com':[2,0],'medicine_name':[3,0],'permit_num':[5,0],'protect_degree':[6,0],'protect_start_date':[8,0],
                        'protect_end_date':[9,0],'medicine_production_company':[10,0],'dosage':[11,0],'limited_date':[12,0]}},
        u'进口药品':
            {'location':(7,3,2),
             'tableId':'36',
             'tableName':'TABLE36',
             'title':'%BD%F8%BF%DA%D2%A9%C6%B7',
             'bcId':'124356651564146415214424405468',
             'tableView': '%E8%BF%9B%E5%8F%A3%E8%8D%AF%E5%93%81',
             'viewtitleName': 'COLUMN361',
             'item':ImporteddrugItem(),
             'itemdict':{'registration_number':[2,0],'product_type':[31,0],'dosage':[16,0],'goods_chinese_name':[14,0],'goods_english_name':[15,0],
                        'english_name':[12,0],'chinese_name':[13,0],'medicine_benwei_code':[32,0],'company_chinese_name':[6,0],'company_english_name':[7,0],
                        'nation_chinese_name':[10,0],'nation_english_name':[11,0],'producer_chinese_name':[19,0],'producer_english_name':[20,0],
                        'producer_nation_chinese_name':[23,0],'producer_nation_english_name':[24,0],'limited_date':[26,0],'certificated_issue_date':[25,0]}},
        u'药品生产企业':
            {'location':(7,3,3),
             'tableId':'34',
             'tableName':'TABLE34',
             'title':'%D2%A9%C6%B7%C9%FA%B2%FA%C6%F3%D2%B5',
             'bcId':'118103348874362715907884020353',
             'tableView': '%E8%8D%AF%E5%93%81%E7%94%9F%E4%BA%A7%E4%BC%81%E4%B8%9A',
             'viewtitleName': 'COLUMN322',
             'item':ProductionCompanyItem(),
             'itemdict':{'pc_name':[6,0],'pc_code':[2,0],'pc_org_code':[3,0],'pc_class_num':[4,0],'pc_position':[5,0],'pc_com_name':[10,0],
                        'pc_pro_pos':[11,0],'pc_cer_issue_date':[13,0],'pc_limit_date':[14,0],'pc_cer_issue_org':[15,0],'pc_cer_issue_per':[16,0],
                        'pc_supervision_org':[17,0]}},
        u'药品经营企业':
            {'location':(7,4,3),
             'tableId':'41',
             'tableName':'TABLE41',
             'title':'%D2%A9%C6%B7%BE%AD%D3%AA%C6%F3%D2%B5',
             'bcId':'118715854214917952033010551784',
             'tableView': '%E8%8D%AF%E5%93%81%E7%BB%8F%E8%90%A5%E4%BC%81%E4%B8%9A',
             'viewtitleName': 'COLUMN438',
             'item':ManagementCompanyItem(),
             'itemdict':{'mc_certif_num':[2,0],'mc_name':[3,0],'mc_pos':[4,0],'mc_stoc_pos':[5,0],'mc_lagal_rep':[6,0],'mc_law_manager':[7,0],
                        'mc_qua_manager':[8,0],'mc_manage_style':[9,0],'mc_manage_scope':[10,0],'mc_certif_issue':[11,0],'mc_limit_date':[12,0],
                        'mc_issue_department':[13,0]}},
        u'国产器械':
            {'location':(6,1,1),
             'tableId':'26',
             'tableName':'TABLE26',
             'title':'%B9%FA%B2%FA%C6%F7%D0%B5',
             'bcId':'11810305861702708383870670156',
             'tableView': '%E5%9B%BD%E4%BA%A7%E5%99%A8%E6%A2%B0',
             'viewtitleName': 'COLUMN184',
             'item':ChineseMediInstrumentItem(),
             'itemdict':{'cmi_register_num':[2,0],'cmi_register_per_name':[3,0],'cmi_register_per_address':[4,0],'cmi_name':[8,0],
                        'cmi_type_spec_name':[9,0],'cmi_stru':[10,0],'cmi_application_range':[11,0],'cmi_permit_date':[14,0],'cmi_limit_date':[15,0],
                        'cmi_product_standard':[17,0],'cmi_ingredient':[20,0],'cmi_expect_usage':[21,0],'cmi_save_condition':[22,0],
                        'cmi_apprve_org':[23,0],'cmi_change_info':[24,0]}},
        u'进口器械':
            {'location':(6,2,1),
             'tableId':'27',
             'tableName':'TABLE27',
             'title':'%BD%F8%BF%DA%C6%F7%D0%B5',
             'bcId':'118103063506935484150101953610',
             'tableView': '%E8%BF%9B%E5%8F%A3%E5%99%A8%E6%A2%B0',
             'viewtitleName': 'COLUMN200',
             'item':ImportedMediInstrumentItem(),
             'itemdict':{'imi_product_name':[2,0],'imi_register_num':[3,0],'imi_register_per_name':[4,0],'imi_register_per_address':[5,0],
                        'imi_production_pos':[6,0],'imi_agent_per_name':[7,0],'imi_agent_per_address':[8,0],'imi_type_spec_name':[9.0],
                        'imi_stru':[10,0],'imi_application_range':[11,0],'imi_produce_english_name':[12,0],'imi_permit_date':[16,0],
                        'imi_limit_date':[17,0],'imi_producer_chinese_name':[18,0],'imi_product_chinese_name':[19,0],'imi_product_standard':[20,0],
                        'imi_produce_nation_chinese_name':[21,0],'imi_services':[22,0],'imi_ingredient':[24,0],'imi_expect_usage':[25,0],
                        'imi_save_condition':[26,0],'imi_apprve_org':[27,0],'imi_change_info':[28,0]}},
        u'第一类医疗器械（含第一类体外诊断试剂）备案信息':
            {'location':(6,3,3),
             'tableId':'104',
             'tableName':'TABLE104',
             'title':'%B5%DA%D2%BB%C0%E0%D2%BD%C1%C6%C6%F7%D0%B5%A3%A8%BA%AC%B5%DA%D2%BB%C0%E0%CC%E5%CD%E2%D5%EF%B6%CF%CA%D4%BC%C1%A3%A9%B1%B8%B0%B8%D0%C5%CF%A2',
             'bcId':'140599784696472870332308528649',
             'tableView': '%E7%AC%AC%E4%B8%80%E7%B1%BB%E5%8C%BB%E7%96%97%E5%99%A8%E6%A2%B0%EF%BC%88%E5%90%AB%E7%AC%AC%E4%B8%80%E7%B1%BB%E4%BD%93%E5%A4%96%E8%AF%8A%E6%96%AD%E8%AF%95%E5%89%82%EF%BC%89%E5%A4%87%E6%A1%88%E4%BF%A1%E6%81%AF',
             'viewtitleName': 'COLUMN1384',
             'item':MediInstrumentRecordsItem(),
             'itemdict':{'mir_num':[2,0],'mir_medicine_type':[3,0],'mir_record_name':[4,0],'mir_record_org':[5,0],'mir_record_register_address':[6,0],
                        'mir_produce_pos':[7,0],'mir_production_name':[10,0],'mir_type_spec_name':[11,0],'mir_limit_date':[12,0],'mir_ingredient':[13,0],
                        'mir_application_expection':[14,0],'mir_note':[15,0],'mir_record_depart':[16,0],'mir_record_date':[17,0],
                        'mir_change_situation':[18,0],'mir_record_status':[19,0]}},
    }
    def parse(self, response):
        for key,value in self.indexdict.items():
            location=value['location']


            #index_url=self.base_dir+urllib.urlencode(parameter)
            #页面显示的网址存在中文，需要自行拼接
            #index_url=''.join(response.xpath('/html/body/center/table[5]/tr['+str(location[0])+']/td/table/tr[2]/td/table/tr['
                                   #  +str(location[1])+']/td['+str(location[2])+']/a/@href').extract())
            #页面上显示的text
            #text=''.join(response.xpath('/html/body/center/table[5]/tr['+str(location[0])+']/td/table/tr[2]/td/table/tr['
                                   #  +str(location[1])+']/td['+str(location[2])+']/a/text()').extract())
            count=''.join(response.xpath('/html/body/center/table[5]/tr['+str(location[0])+']/td/table/tr[2]/td/table/tr['
                                     +str(location[1])+']/td['+str(location[2])+']/a/font/text()').extract())[1:-1]
            #print index_url
            #print text
            print (count)
            pagecount=int(math.ceil(int(count)/15.0))
            parameter=dict()
            parameter['tableId']=value['tableId']
            parameter['tableName']=value['tableName']
            parameter['viewtitleName']=value['viewtitleName']
            parameter['bcId']=value['bcId']
            parameter['tableView']=value['tableView']

            for i in range(1,pagecount+1):
            #for i in range(1,2):
                parameter['curstart']=str(i)
                url=self.SEARCH_URL+urllib.urlencode(parameter)
                yield scrapy.Request(url,callback=self.search_parse,meta={'type':key})


    def search_parse(self,response):
        #item_len=len(response.xpath('/body/table[2]/tr'))
        item_len = len(response.xpath('body/table[2]/tr'))
        #print item_len
        type=response.meta['type']
        parameter=dict()
        parameter['tableId']=self.indexdict[type]['tableId']
        parameter['tableName']=self.indexdict[type]['tableName']
        parameter['tableView']=self.indexdict[type]['title']

        for i in range(1,item_len,2):
        #for i in range(1,2):
            item_raw_href=''.join(response.xpath('body/table[2]/tr['+str(i)+']/td/p/a/@href').extract())
            #print item_raw_href
            pattern = re.compile(r'.*Id=([0-9]+)')
            id=pattern.search(item_raw_href).group(1)
            parameter['Id']=str(id)
            url=self.CONTENT_URL+urllib.urlencode(parameter)
            #print url
            yield scrapy.Request(url,callback=self.item_parse,meta={'type':type})


    def item_parse(self,response):
        tr_len=len(response.xpath('//div[@class="listmain"]/div/table/tr'))
        type=response.meta['type']


        item=self.indexdict[type]['item']
        item['type']=type
        for key,value in self.indexdict[type]['itemdict'].items():
            if value[1]==0:
                item[key]=''.join(response.xpath('//div[@class="listmain"]/div/table/tr['+str(value[0])+']/td[2]/text()').extract())
            else:
                item[key]=''.join(response.xpath('//div[@class="listmain"]/div/table/tr['+str(value[0])+']/td[2]/a/text()').extract())
        yield item



























