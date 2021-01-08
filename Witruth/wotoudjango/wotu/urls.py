#coding:utf-8
from django.conf.urls import url
from wotu import views as wotu_views


urlpatterns = [
url(r'^$',wotu_views.home, name='index'),
url(r'^home', wotu_views.home, name='home'),
url(r'^login',wotu_views.log_in, name='log_in'),
url(r'^logout',wotu_views.log_out, name='log_out'),
url(r'^regist', wotu_views.regist, name='regist'),

url(r'^showresult', wotu_views.showresult, name='showresult'),
url(r'^showresult_one', wotu_views.showresult_one, name='showresult_one'),

url(r'^xiansuotiqu1', wotu_views.xiansuotiqu1, name='xiansuotiqu1'),
url(r'^xiansuo_iframe', wotu_views.xiansuo_iframe, name='xiansuo_iframe'),
url(r'^xiansuo_frame', wotu_views.xiansuo_frame, name='xiansuo_frame'),
url(r'^xiansuo_frame_zixun', wotu_views.xiansuo_frame_zixun, name='xiansuo_frame_zixun'),
url(r'^xiansuo_frame_weibo', wotu_views.xiansuo_frame_weibo, name='xiansuo_frame_weibo'),
url(r'^xiansuo_frame_wechat', wotu_views.xiansuo_frame_wechat, name='xiansuo_frame_wechat'),
url(r'^xiansuo_frame_qita', wotu_views.xiansuo_frame_qita, name='xiansuo_frame_qita'),

url(r'^xiansuo_TMT', wotu_views.xiansuo_TMT, name='xiansuo_TMT'),
url(r'^xiansuo_TMT_iframe', wotu_views.xiansuo_TMT_iframe, name='xiansuo_TMT_iframe'),
url(r'^xiansuo_TMT_frame', wotu_views.xiansuo_TMT_frame, name='xiansuo_TMT_frame'),
url(r'^xiansuo_TMT_frame_zixun', wotu_views.xiansuo_TMT_frame_zixun, name='xiansuo_TMT_frame_zixun'),
url(r'^xiansuo_TMT_frame_weibo', wotu_views.xiansuo_TMT_frame_weibo, name='xiansuo_TMT_frame_weibo'),
url(r'^xiansuo_TMT_frame_wechat', wotu_views.xiansuo_TMT_frame_wechat, name='xiansuo_TMT_frame_wechat'),
url(r'^xiansuo_TMT_frame_qita', wotu_views.xiansuo_TMT_frame_qita, name='xiansuo_TMT_frame_qita'),

url(r'^zhuanlifa', wotu_views.zhuanlifa, name='zhuanlifa'),

url(r'^keywords_show', wotu_views.keywords_show, name='keywords_show'),
url(r'^jigougenzong', wotu_views.jigougenzong, name='jigougenzong'),
url(r'^zixungenzong', wotu_views.zixungenzong, name='zixungenzong'),
url(r'^for_track', wotu_views.for_track, name='for_track'),

url(r'^study_xiansuo', wotu_views.study_xiansuo, name='study_xiansuo'),
url(r'^yaopinshoushen', wotu_views.yaopinshoushen, name='yaopinshoushen'),

url(r'^patent_details', wotu_views.patent_details, name='patent_details'),
url(r'^list_method', wotu_views.list_method, name='list_method'),
url(r'^firm_steer', wotu_views.firm_steer, name='firm_steer'),
url(r'^business_change', wotu_views.business_change, name='business_change'),

url(r'^test_wayne', wotu_views.test_wayne, name='test_wayne'), # test
url(r'^track_asset', wotu_views.track_asset, name='track_asset'),
url(r'^medicine_trial', wotu_views.medicine_trial, name='medicine_trial'),
url(r'^clinical_data', wotu_views.clinical_data, name='clinical_data'),
url(r'^removekeyword', wotu_views.removekeyword, name='remove_keyword'),
# regex 匹配URL请求
# view 需要调用的视图模板
# kwargs 任何关键字参数都可以以字典的形式传递给目标视图
# name 命名URL,可以在Django的任何地方通过名称来明确的引用这个URL
#
]