# -*- coding: utf-8 -*-
"""
机构追踪法实现
"""
from spiders.track_asset import spider_simu as simu
from spiders.track_asset import spider_qichacha as qcc
import time
import pymysql
import datetime

conn = pymysql.connect(
    host='106.75.65.56',
    db='news',
    user='root',
    passwd='wotou',
    charset='utf8',
    use_unicode=True)
cursor = conn.cursor()

def need_update(manager, interval_days):
    cursor.execute("""select spider_date from white_list_manager where manager=%s """ , (manager,))
    ret = cursor.fetchone()[0]
    # print 'ret', ret
    if ret:
        spider_date = ret
        now = datetime.datetime.now()
        return (now - spider_date).days > interval_days
    return True

def white_list_track():
    """
    批量处理白名单投资人
    """
    cursor.execute("""select manager from white_list_manager""")
    manager_list = cursor.fetchall()
    result_dict = {}
    for w in manager_list:
        manager_name = w[0].encode('utf8')
        if need_update(manager_name, 30):
            new_result = track(manager_name)
            result_dict = dict(new_result, **result_dict )
            cursor.execute("""update white_list_manager set spider_date = %s where manager=%s""", (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), manager_name))
            conn.commit()
            if len(new_result[manager_name]['all_companies']) > 100:
                print('wait some time')
                time.sleep(60)
    return result_dict

def track(manager_keyword):
    '''
    :param manager_keyword: 输入基金管理人全程或关键字
    :return: Dict{基金管理人：{'wanted_companies': 符合要求公司, 'all_companies': 旗下所有公司}}
    '''
    manager_dict = simu.search_manager(manager_keyword)
    result = {}
    wanted_companies = []
    all_companies = []
    for manager in list(manager_dict.keys()):
        for assets in manager_dict[manager]:
            time.sleep(1)
            company_list = qcc.all_companies(assets.encode('utf8'))
            wanted_companies += company_list[0]
            all_companies += company_list[1]
    wanted_companies = list(set(wanted_companies))
    all_companies = list(set(all_companies))
    print('结果：')
    print('-----------------所有公司--------------------')
    for a in all_companies:
        print(a.decode('utf8'))
    print('------------------符合要求-------------------')
    for w in wanted_companies:
        print(w.decode('utf8'))
    print('\n\n')
    result[manager_keyword] = {'wanted_companies': wanted_companies, 'all_companies': all_companies}
    return result

def test(company_name):
    pass

if __name__ == '__main__':
    # print 1
    # print json.dumps(convert_to_dict('杭州维思投资合伙企业（有限合伙）'))
    # test2()
    # test('深圳同创伟业资产管理股份有限公司')
    # test('上海德同诚鼎股权投资基金管理有限公司')
    # test('广州德同广报投资管理有限公司')
    # track(raw_input('输入基金管理人名称：'))
    # track('浙商万嘉（北京）创业投资管理有限公司')
    track('杭州维思投资合伙企业')
    # print white_list_track()
    pass
