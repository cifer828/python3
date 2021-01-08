#-*-coding:utf-8-*-#
import pymongo
import xlwt

conn = pymongo.MongoClient('106.75.65.56', 27017)
db=conn['CFDA']

account_qcc=db['qcc_important']
account_baiteng=db['baiteng']
company_dict=dict()
book=xlwt.Workbook()
sheet1=book.add_sheet('total',cell_overwrite_ok=True)
sheet1.write(0,0,u'公司名称')
sheet1.write(0,1,u'经营范围')
sheet1.write(0,2,u'所属行业')
sheet1.write(0,3,u'公司简介')
sheet1.write(0,4,u'软件著作权数量')
sheet1.write(0,5,u'专利数量')
row=1
for item in account_qcc.find():
    #company_dict[item[u'公司名称']]=dict()
    #value=company_dict[item[u'公司名称']]
    sheet1.write(row,0,item[u'公司名称'])
    if u'经营范围' in item.keys():
        #value['经营范围']=item[u'经营范围']
        sheet1.write(row,1,item[u'经营范围'])
    else:
        #value['经营范围'] =''
        sheet1.write(row,1,'')

    if u'所属行业' in item.keys():
        #value['所属行业']=item[u'所属行业']
        sheet1.write(row,2,item[u'所属行业'])
    else:
        #value['所属行业'] =''
        sheet1.write(row,2,'')

    if u'公司简介' in item.keys():
        #value['公司简介'] = item[u'公司简介']
        sheet1.write(row,3,item[u'公司简介'])
    else:
        #value['公司简介'] = ''
        sheet1.write(row,3,'')

    if u'软件著作权' in item.keys():
        sheet1.write(row,4,len(item[u'软件著作权'].keys()))
    else:
        sheet1.write(row,4,0)


    baiteng_item = account_baiteng.find_one({u'公司名称':item[u'公司名称']})
    sheet1.write(row,5,len(baiteng_item[u'专利'].keys()))
    row+=1

book.save('total.xls')





    #print company_name