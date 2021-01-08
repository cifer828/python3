# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from twisted.enterprise import adbapi
import MySQLdb
import MySQLdb.cursors
from scrapy.crawler import Settings as settings

class CfdaCrawlPipeline(object):
    def __init__(self):
        dbargs = dict(
            host='localhost',
            db='dataapp',
            user='root',  # replace with you user name
            passwd='0845',  # replace with you password
            charset='utf8',
            cursorclass=MySQLdb.cursors.DictCursor,
            use_unicode=True,
        )
        self.dbpool = adbapi.ConnectionPool('MySQLdb', **dbargs)


    '''
    The default pipeline invoke function
    '''

    def process_item(self, item, spider):
        res = self.dbpool.runInteraction(self.insert_into_table, item)
        return item

    def insert_into_table(self, conn, item):
        type=item['type']

        if type==u'国产药品':
            conn.execute('insert into wotou_app_domesticdrug(permit_num,english_name,chinese_name,dosage,produce_com,'
                         'product_type,medicine_benwei_code,approval_date) '
                        'values(%s,%s,%s,%s,%s,%s,%s,%s)',
                        (item['permit_num'],item['english_name'],item['chinese_name'],item['dosage'],item['produce_com'],
                        item['product_type'],item['medicine_benwei_code'],item['approval_date']))

        if type==u'国产药品商品名':
            conn.execute('insert into wotou_app_domesticdruggoods(permit_num,english_name,chinese_name,'
                         'goods_name,dosage,produce_com,product_type,medicine_benwei_code,approval_date) '
                        'values(%s,%s,%s,%s,%s,%s,%s,%s,%s)',
                        (item['permit_num'],item['english_name'],item['chinese_name'],item['goods_name'],item['dosage'],
                         item['produce_com'],item['product_type'],item['medicine_benwei_code'],item['approval_date']))

          # 发证日期
        if type==u'进口药品商品名':
            conn.execute('insert into wotou_app_importeddruggoods(producer_chinese_name,company_english_name,product_type,'
                         'goods_english_name,producer_nation_english_name,limited_date,chinese_name,certificated_issue_date,'
                         'producer_nation_chinese_name,nation_chinese_name,nation_english_name,goods_chinese_name,english_name,'
                         'company_chinese_name,producer_english_name,dosage,registration_number) '
                         'values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',
                         (item['producer_chinese_name'],item['company_english_name'],item['product_type'],item['goods_english_name'],
                          item['producer_nation_english_name'],item['limited_date'],item['chinese_name'],item['certificated_issue_date'],
                          item['producer_nation_chinese_name'],item['nation_chinese_name'],item['nation_english_name'],
                          item['goods_chinese_name'],item['english_name'],item['company_chinese_name'],item['producer_english_name'],
                          item['dosage'],item['registration_number']))

        if type==u'中药保护品种':
            conn.execute('insert into wotou_app_drugprotection(limited_date,medicine_production_company,produce_com,permit_num,'
                         'medicine_name,dosage,protect_end_date,protect_degree,protect_start_date) '
                         'values(%s,%s,%s,%s,%s,%s,%s,%s,%s)',
                        (item['limited_date'],item['medicine_production_company'],item['produce_com'],item['permit_num'],
                         item['medicine_name'],item['dosage'],item['protect_end_date'],item['protect_degree'],item['protect_start_date']))


        if type==u'进口药品':
            conn.execute('insert into wotou_app_importeddrug(producer_chinese_name,company_english_name,product_type,goods_english_name,'
                         'producer_nation_english_name,limited_date,chinese_name,certificated_issue_date,producer_nation_chinese_name,'
                         'nation_chinese_name,nation_english_name,goods_chinese_name,english_name,company_chinese_name,producer_english_name,'
                         'dosage,registration_number,medicine_benwei_code) '
                         'values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',
                        (item['producer_chinese_name'],item['company_english_name'],item['product_type'],item['goods_english_name'],
                         item['producer_nation_english_name'],item['limited_date'],item['chinese_name'],item['certificated_issue_date'],
                         item['producer_nation_chinese_name'],item['nation_chinese_name'],item['nation_english_name'],item['goods_chinese_name'],
                         item['english_name'],item['company_chinese_name'],item['producer_english_name'],item['dosage'],item['registration_number'],
                         item['medicine_benwei_code']))

        if type==u'药品生产企业':
            conn.execute('insert into wotou_app_productioncompany(pc_pro_pos,pc_org_code,pc_cer_issue_per,pc_code,pc_cer_issue_org,'
                         'pc_name,pc_com_name,pc_supervision_org,pc_cer_issue_date,pc_limit_date,pc_class_num,pc_position) '
                         'values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',
                        (item['pc_pro_pos'],item['pc_org_code'],item['pc_cer_issue_per'],item['pc_code'],item['pc_cer_issue_org'],
                         item['pc_name'],item['pc_com_name'],item['pc_supervision_org'],item['pc_cer_issue_date'],item['pc_limit_date'],
                         item['pc_class_num'],item['pc_position']))

        if type==u'药品经营企业':
            conn.execute('insert into wotou_app_managementcompany(mc_name,mc_qua_manager,mc_pos,mc_manage_style,mc_stoc_pos,mc_issue_department,'
                         'mc_law_manager,mc_certif_num,mc_lagal_rep,mc_limit_date,mc_manage_scope,mc_certif_issue) '
                         'values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',
                        (item['mc_name'],item['mc_qua_manager'],item['mc_pos'],item['mc_manage_style'],item['mc_stoc_pos'],
                         item['mc_issue_department'],item['mc_law_manager'],item['mc_certif_num'],item['mc_lagal_rep'],item['mc_limit_date'],
                         item['mc_manage_scope'],item['mc_certif_issue']))

        if type==u'国产器械':
            conn.execute('insert into wotou_app_chinesemediinstrument(cmi_save_condition,cmi_register_per_name,cmi_stru,cmi_change_info,'
                         'cmi_name,cmi_register_num,cmi_permit_date,cmi_apprve_org,cmi_type_spec_name,cmi_ingredient,cmi_product_standard,'
                         'cmi_register_per_address,cmi_application_range,cmi_limit_date,cmi_expect_usage) '
                         'values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',
                        (item['cmi_save_condition'],item['cmi_register_per_name'],item['cmi_stru'],item['cmi_change_info'],
                         item['cmi_name'],item['cmi_register_num'],item['cmi_permit_date'],item['cmi_apprve_org'],item['cmi_type_spec_name'],
                         item['cmi_ingredient'],item['cmi_product_standard'],item['cmi_register_per_address'],item['cmi_application_range'],
                         item['cmi_limit_date'],item['cmi_expect_usage']))

        if type==u'进口器械':
            conn.execute('insert into wotou_app_importedmediinstrument(imi_ingredient,imi_type_spec_name,imi_application_range,imi_produce_english_name,'
                         'imi_stru,imi_expect_usage,imi_register_per_name,imi_agent_per_name,imi_limit_date,imi_producer_chinese_name,'
                         'imi_produce_nation_chinese_name,imi_apprve_org,imi_permit_date,imi_change_info,imi_product_name,imi_product_standard,'
                         'imi_product_chinese_name,imi_register_per_address,imi_register_num,imi_save_condition,imi_services,'
                         'imi_production_pos,imi_agent_per_address) '
                         'values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',
                        (item['imi_ingredient'],item['imi_type_spec_name'],item['imi_application_range'],item['imi_produce_english_name'],
                         item['imi_stru'],item['imi_expect_usage'],item['imi_register_per_name'],item['imi_agent_per_name'],item['imi_limit_date'],
                         item['imi_producer_chinese_name'],item['imi_produce_nation_chinese_name'],item['imi_apprve_org'],item['imi_permit_date'],
                         item['imi_change_info'],item['imi_product_name'],item['imi_product_standard'],item['imi_product_chinese_name'],
                         item['imi_register_per_address'],item['imi_register_num'],item['imi_save_condition'],item['imi_services'],
                         item['imi_production_pos'],item['imi_agent_per_address']))

        if type==u'第一类医疗器械（含第一类体外诊断试剂）备案信息':
            conn.execute('insert into wotou_app_mediinstrumentrecords(mir_medicine_type,mir_ingredient,mir_limit_date,mir_record_date,mir_record_name,'
                         'mir_note,mir_application_expection,mir_record_depart,mir_record_register_address,mir_type_spec_name,mir_record_status,'
                         'mir_produce_pos,mir_change_situation,mir_num,mir_production_name,mir_record_org) '
                         'values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',
                        (item['mir_medicine_type'],item['mir_ingredient'],item['mir_limit_date'],item['mir_record_date'],item['mir_record_name'],
                         item['mir_note'],item['mir_application_expection'],item['mir_record_depart'],item['mir_record_register_address'],
                         item['mir_type_spec_name'],item['mir_record_status'],item['mir_produce_pos'],item['mir_change_situation'],
                         item['mir_num'],item['mir_production_name'],item['mir_record_org']))


