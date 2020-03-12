# def get_text(elem):
#     rc = []
#     for node in elem.itertext():
#         rc.append(node.strip())
#     return ''.join(rc)
#
# def modify_time(og_time):
#     time_list=og_time.split('-')
#     new_time=time_list[0]+'-'
#     if len(time_list[1])==1:
#         new_time+=('0'+time_list[1]+'-')
#     else:
#         new_time+=(time_list[1]+'-')
#     if len(time_list[2])==1:
#         new_time+=('0'+time_list[2])
#     else:
#         new_time+=(time_list[2])
#     return new_time
#
# def type_search():
#     base_url='http://www.bioon.com/'
#     r=requests.get(base_url)
#     dom=lxml.html.document_fromstring(r.content)
#     li_len = len(dom.xpath('//div[@class="index_left_menu"]/ul/li'))
#     li_list=dom.xpath('//div[@class="index_left_menu"]/ul/li')
#     type_list=[]
#     for i in range(1, li_len):
#         types=li_list[i].xpath('./p/a')
#         for type in types:
#             if type.text!='' and type.text !=None:
#                 href=type.get('href')
#                 type_list.append([type.text.strip(),href])
#
#
#     #print type_list
#
#     return type_list
#
#
# def get_new_content(href):
#     base_url='http://news.bioon.com'
#     url=base_url+href
#     r=requests.get(url)
#     dom=lxml.html.document_fromstring(r.content)
#     text = get_text(dom.xpath('//div[@class="text3"]')[0])
#     #print (text)
#     dr = re.compile(r'<[^>]+>', re.S)
#     text = dr.sub('', text)
#     text = text.strip()
#     return text
#
# def get_news(type,href,conn,cur,day):
#     headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:44.0) Gecko/20100101 Firefox/44.0'}
#     end_time = datetime.datetime.now()
#     start_time = end_time + datetime.timedelta(days=-day)
#     end_day = modify_time('-'.join([str(end_time.year), str(end_time.month), str(end_time.day)]))
#     start_day = modify_time('-'.join([str(start_time.year), str(start_time.month), str(start_time.day)]))
#     flag=True
#     page=1
#     typelist=[]
#     while flag:
#         url=href+'list-'+str(page)+'.html'
#         r=requests.get(url,headers=headers)
#         #print url
#         dom=lxml.html.document_fromstring(r.content)
#         #print r.content
#         news_list=dom.xpath('//ul[@id="cms_list"]/li')
#         #print len(news_list)
#         for new in news_list:
#             try:
#                 time=modify_time(new.xpath('./div[2]/div')[0].text)
#                 #print time,start_day
#                 #print time>start_day
#                 if time>start_day:
#
#                     new_title=new.xpath('./div[2]/h4/a')[0].text
#                     #print new_title,type
#                     new_href=new.xpath('./div[2]/h4/a')[0].get('href')
#                     content=get_new_content(new_href)
#                     #print content
#                     typelist.append([new_title,new_href,type,content])
#                     cur.execute('insert into bioon(title,url,type,content) values(%s,%s,%s,%s)',
#                                  (new_title,new_href,type,content))
#                     conn.commit()
#
#                 else:
#                     flag=False
#             except:
#                 continue
#         page+=1
#     return typelist
#
#
#
#
#
# def process(type_list,conn,cur,day):
#     for type in type_list:
#         href=type[1]
#         name=type[0]
#         print name,href
#
#         news_list.extend(get_news(name,href,conn,cur,day))
#
#
#
# def start(conn,cur,day):
#     global news_list
#     news_list=[]
#     type_list=type_search()
#     splitlist = [0, len(type_list) / 4, len(type_list) / 4 * 2, len(type_list) / 4 * 3, len(type_list)]
#     process_dict={}
#     for i in range(4):
#         process_dict[i] = multiprocessing.Process(target=process, args=(type_list[splitlist[i]:splitlist[i + 1]],conn,cur,day))
#         print i
#         process_dict[i].start()
#     while True:
#         if not (process_dict[0].is_alive() or process_dict[1].is_alive() or process_dict[2].is_alive() or process_dict[3].is_alive()):
#             break
#     return news_list
#
# conn = pymysql.Connect(host='106.75.65.56', user='root', passwd='wotou', charset='utf8', db='news')
# cur = conn.cursor()
# new_list=start(conn,cur,7)
# print len(new_list)

import os,sys

def crawl_bioon():
    # try:
    #     configure_logging()
    #
    #     settings = Settings({'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
    #                          'DOWNLOAD_DELAY':1,
    #                          'ITEM_PIPELINES': {'shengwugu_crawl.shengwugu_crawl.pipelines.ShengwuguCrawlPipeline': 300}},
    #                         )
    #     process = CrawlerRunner(settings)
    #
    #     d=process.crawl(shengwuguSpider)
    #
    #     # the script will block here until the crawling is finished
    #
    #     d.addBoth(lambda _: reactor.stop())
    #     reactor.run()
    # except:
    #     return
    os.system('cd '+sys.path[0]+'/wotu/spiders/shengwugu_crawl/shengwugu_crawl/spiders && scrapy crawl bioon')
    print('cd '+sys.path[0]+'/wotu/spiders/shengwugu_crawl/shengwugu_crawl/spiders && scrapy crawl bioon')

if __name__ == '__main__':
    crawl_bioon()

