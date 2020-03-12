#coding:utf-8
indexdict={
        u'国产药品':
            {'table':'domesticdrug',
             'itemdict':{'permit_num':[2,0],'english_name':[4,0],'chinese_name':[3,0],'dosage':[5,0],'produce_com':[8,1],'product_type':[10,0],
                        'medicine_benwei_code':[13,0],'approval_date':[11,0]}},
        u'国产药品商品名':
            { 'table':'domesticdruggoods',
             'itemdict':{'permit_num':[2,0],'english_name':[5,0],'chinese_name':[4,0],'dosage':[9,0],'produce_com':[7,1],
                        'product_type':[10,0],'medicine_benwei_code':[13,0],'approval_date':[11,0],'goods_name':[6,0]}},
        u'进口药品商品名':
            {'table':'importeddruggoods',
             'itemdict':{'registration_number':[2,0],'product_type':[30,0],'dosage':[16,0],'goods_chinese_name':[8,0],'goods_english_name':[9,0],
                        'english_name':[7,0],'chinese_name':[6,0],'company_chinese_name':[10,0],'company_english_name':[11,0],
                        'nation_chinese_name':[14,0],'nation_english_name':[15,0],'producer_chinese_name':[19,0],'producer_english_name':[20,0],
                        'producer_nation_chinese_name':[23,0],'producer_nation_english_name':[24,0],'limited_date':[26,0],'certificated_issue_date':[25,0]}},
        u'中药保护品种':
            {'table':'drugprotection',
             'itemdict':{'produce_com':[2,0],'medicine_name':[3,0],'permit_num':[5,0],'protect_degree':[6,0],'protect_start_date':[8,0],
                        'protect_end_date':[9,0],'medicine_production_company':[10,0],'dosage':[11,0],'limited_date':[12,0]}},
        u'进口药品':
            {'table':'importeddrug',
             'itemdict':{'registration_number':[2,0],'product_type':[31,0],'dosage':[16,0],'goods_chinese_name':[14,0],'goods_english_name':[15,0],
                        'english_name':[12,0],'chinese_name':[13,0],'medicine_benwei_code':[32,0],'company_chinese_name':[6,0],'company_english_name':[7,0],
                        'nation_chinese_name':[10,0],'nation_english_name':[11,0],'producer_chinese_name':[19,0],'producer_english_name':[20,0],
                        'producer_nation_chinese_name':[23,0],'producer_nation_english_name':[24,0],'limited_date':[26,0],'certificated_issue_date':[25,0]}},
        u'药品生产企业':
            {'table':'productioncompany',
             'itemdict':{'pc_name':[6,0],'pc_code':[2,0],'pc_org_code':[3,0],'pc_class_num':[4,0],'pc_position':[5,0],'pc_com_name':[10,0],
                        'pc_pro_pos':[11,0],'pc_cer_issue_date':[13,0],'pc_limit_date':[14,0],'pc_cer_issue_org':[15,0],'pc_cer_issue_per':[16,0],
                        'pc_supervision_org':[17,0]}},
        u'药品经营企业':
            {'table':'managementcompany',
             'itemdict':{'mc_certif_num':[2,0],'mc_name':[3,0],'mc_pos':[4,0],'mc_stoc_pos':[5,0],'mc_lagal_rep':[6,0],'mc_law_manager':[7,0],
                        'mc_qua_manager':[8,0],'mc_manage_style':[9,0],'mc_manage_scope':[10,0],'mc_certif_issue':[11,0],'mc_limit_date':[12,0],
                        'mc_issue_department':[13,0]}},
        u'国产器械':
            {'table':'chinesemediinstrument',
             'itemdict':{'cmi_register_num':[2,0],'cmi_register_per_name':[3,0],'cmi_register_per_address':[4,0],'cmi_name':[8,0],
                        'cmi_type_spec_name':[9,0],'cmi_stru':[10,0],'cmi_application_range':[11,0],'cmi_permit_date':[14,0],'cmi_limit_date':[15,0],
                        'cmi_product_standard':[17,0],'cmi_ingredient':[20,0],'cmi_expect_usage':[21,0],'cmi_save_condition':[22,0],
                        'cmi_apprve_org':[23,0],'cmi_change_info':[24,0]}},
        u'进口器械':
            {'table':'importedmediinstrument',
             'itemdict':{'imi_product_name':[2,0],'imi_register_num':[3,0],'imi_register_per_name':[4,0],'imi_register_per_address':[5,0],
                        'imi_production_pos':[6,0],'imi_agent_per_name':[7,0],'imi_agent_per_address':[8,0],'imi_type_spec_name':[9.0],
                        'imi_stru':[10,0],'imi_application_range':[11,0],'imi_produce_english_name':[12,0],'imi_permit_date':[16,0],
                        'imi_limit_date':[17,0],'imi_producer_chinese_name':[18,0],'imi_product_chinese_name':[19,0],'imi_product_standard':[20,0],
                        'imi_produce_nation_chinese_name':[21,0],'imi_services':[22,0],'imi_ingredient':[24,0],'imi_expect_usage':[25,0],
                        'imi_save_condition':[26,0],'imi_apprve_org':[27,0],'imi_change_info':[28,0]}},
        u'第一类医疗器械（含第一类体外诊断试剂）备案信息':
            {'table':'mediinstrumentrecords',
             'itemdict':{'mir_num':[2,0],'mir_medicine_type':[3,0],'mir_record_name':[4,0],'mir_record_org':[5,0],'mir_record_register_address':[6,0],
                        'mir_produce_pos':[7,0],'mir_production_name':[10,0],'mir_type_spec_name':[11,0],'mir_limit_date':[12,0],'mir_ingredient':[13,0],
                        'mir_application_expection':[14,0],'mir_note':[15,0],'mir_record_depart':[16,0],'mir_record_date':[17,0],
                        'mir_change_situation':[18,0],'mir_record_status':[19,0]}},
    }

for key,value in indexdict.items():
    table=value['table']
    valuedict=value['itemdict']
    list1=[]
    for i in range(len(valuedict.keys())):
        list1.append('%s')
    sstr=','.join(list1)
    valuelist = ','.join(["item['" + str(x) + "']" for x in valuedict.keys()])
    str1='insert into '+table+'('+','.join(list(valuedict.keys()))+') values('+sstr+')'



    print str1
    print valuelist
