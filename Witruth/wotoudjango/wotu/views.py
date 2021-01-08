# coding:utf-8
import time

import pandas as pd
import pymysql
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import redirect
from django.shortcuts import render
from django.shortcuts import render_to_response

from .ML import TFIDF
from .ML import ML_stopword
from .spiders.baiteng import baiteng
from .spiders import bioon
from .spiders.track_asset import spider_medicine
from .forms import AddForm,ZhuanliForm
from .forms import CompanyForm
from .forms import LoginForm
from .forms import SignupForm
from .forms import XiansuoForm
from .forms import businesschangeForm
from .models import Company
from .models import Project
from .models import User
from . spiders.baidu_new_spider import *
from . spiders.track_asset import spider_track_asset as sta
import pymongo
from wotu.config.config import MONGO_SERVER
from wotu.config.config import MONGO_PORT


def regist(req):
    if req.method == 'POST':
        uf = SignupForm(req.POST)
        if uf.is_valid():
            email=uf.cleaned_data['email']
            user_name = uf.cleaned_data['user_name']
            password = uf.cleaned_data['password']
            password2 = uf.cleaned_data['password2']
            if password==password2:
                u = User.objects.create_user(username=user_name,email=email)
                u.set_password(password)
                u.save()
            url = req.GET.get('source_url', '/login')
            return redirect(url)
    else:
        uf = SignupForm()
    return render(req, 'regist.html', {'uf': uf})
    #return render_to_response('regist.html',{'uf':uf}, context_instance=RequestContext(req))

def log_in(request):
    if request.method == 'GET':
      form = LoginForm()
      return render(request,'login.html',{'form':form})
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['user_name']
            password = form.cleaned_data['password']
            user = authenticate(username=username,password=password)
            if user is not None:
                login(request,user)
                url = request.POST.get('source_url','/home')
                return redirect(url)
            else:
                return render(request,'login.html',{'form':form,'error':'password or username is not ture!'})
        else:
            return render(request,'login.html',{'form':form})

@login_required(login_url='login/')
def home(request):
    if request.method == 'POST':
      form = AddForm(request.POST)#form 包含提交的数据
      if form.is_valid():# 如果提交的数据合法
        keyword = form.cleaned_data['keyword']
        projects_list = list(Company.objects.filter(company_name__contains=keyword).values_list())
        projects_num = len(projects_list)
        field_num = 0

        if projects_num!=0:
          field_num = len(projects_list[0])
          return render(request,'showresult.html',{'project_list':json.dumps(projects_list),'projects_num':projects_num,'field_num':field_num})
        else:
          return HttpResponse("no info!")

    else:
        form = AddForm()
    return render(request, 'home.html', {'form': form})

@login_required(login_url='login')
def log_out(request):
    url = request.POST.get('source_url', '/login')
    logout(request)
    return redirect(url)

def showresult(request):
  return render(request, 'showresult.html')

def showresult_one(request):
  return render(request, 'showresult_one.html')

# @login_required(login_url='login/')
def xiansuotiqu1(request):
    if request.method=="POST":
        form=XiansuoForm(request.POST)
        if form.is_valid():

            TFIDF.tf_idf_cal()

            CONN = pymongo.MongoClient(MONGO_SERVER, MONGO_PORT)
            db = CONN['news']
            collection = db['bioon']
            df = collection.find({})

            content_list = []
            title_list = []
            keyword_list = []

            for i in df:
                content_list.append(i['content'])
                title_list.append(i['title'])
                keyword_list.append(i['keyword'])
            # content_list = df['content'].values.tolist()
            # title_list = df['title'].values.tolist()
            # keyword_list = df['keyword'].values.tolist()
            # keyword_list = [list(x.split(' ')) for x in keyword_list]
            data_list = []

            for t in range(len(content_list)):
                data_list.append([title_list[t],content_list[t],keyword_list[t]])

            #count,topics=ML.LDA.lda1()
            # print count
            # print topics
            # for k in topics.keys():
            #     topics[k]=','.join(topics[k])
            return render(request,'xiansuotiqu1_result.html',{'data_list':data_list,'count':len(content_list)})


        else:
            return HttpResponse("No info!")

    else:
        form=XiansuoForm()
        return render(request, 'xiansuotiqu1.html',{'form':form})


def removekeyword(request):

    check_box_list = request.POST.getlist('check_box_list')
    print(check_box_list)
    for word in check_box_list:
        ML_stopword.add_stopword(word)
    TFIDF.tf_idf_cal()
    insert_time = str(time.strftime('%Y-%m-%d'))
    #insert_time = '2017-04-19'
    conn = pymysql.Connect(host='106.75.65.56', user='root', passwd='wotou', charset='utf8', db='news')
    cur = conn.cursor()
    df = pd.read_sql('select title,content,keyword from bioon where spidertime="' + insert_time + '" and content<>""',
                     conn)
    content_list = df['content'].values.tolist()
    title_list = df['title'].values.tolist()
    keyword_list = df['keyword'].values.tolist()
    keyword_list = [list(x.split(' ')) for x in keyword_list]
    data_list = []
    print(len(title_list))
    print(len(content_list))
    print(len(keyword_list))
    for t in range(len(content_list)):
        data_list.append([title_list[t], content_list[t], keyword_list[t]])

    # count,topics=ML.LDA.lda1()
    # print count
    # print topics
    # for k in topics.keys():
    #     topics[k]=','.join(topics[k])
    return render(request, 'xiansuotiqu1_result.html', {'data_list': data_list, 'count': len(content_list)})
    # @login_required(login_url='login/')
def xiansuo_iframe(request):
    return render(request, 'xiansuo_iframe.html')

# @login_required(login_url='login/')
def xiansuo_frame(request):
    return render(request, 'xiansuo_frame.html')

# @login_required(login_url='login/')
def xiansuo_frame_zixun(request):
    return render(request, 'xiansuo_frame_zixun.html')

# @login_required(login_url='login/')
def xiansuo_frame_weibo(request):
    return render(request, 'xiansuo_frame_weibo.html')

# @login_required(login_url='login/')
def xiansuo_frame_wechat(request):
    return render(request, 'xiansuo_frame_wechat.html')

# @login_required(login_url='login/')
def xiansuo_frame_qita(request):
    return render(request, 'xiansuo_frame_qita.html')

# @login_required(login_url='login/')
def xiansuo_TMT(request):
    return render(request, 'xiansuo_TMT.html')

def xiansuo_TMT_iframe(request):
    return render(request, 'xiansuo_TMT_iframe.html')

def xiansuo_TMT_frame(request):
  return render(request, 'xiansuo_TMT_frame.html')

def xiansuo_TMT_frame_zixun(request):
  return render(request, 'xiansuo_TMT_frame_zixun.html')

def xiansuo_TMT_frame_weibo(request):
  return render(request, 'xiansuo_TMT_frame_weibo.html')

def xiansuo_TMT_frame_wechat(request):
  return render(request, 'xiansuo_TMT_frame_wechat.html')

def xiansuo_TMT_frame_qita(request):
  return render(request, 'xiansuo_TMT_frame_qita.html')

def zhuanlifa(request):

    if request.method == 'POST':
        form = AddForm(request.POST)

        if form.is_valid():
            print(form.cleaned_data)
            keyword = form.cleaned_data['keyword']
            search_type = form.data['search_type']
            print(search_type)
            if search_type == 1 or search_type == '1' :
                intent_dict, company_list= baiteng.findInMongo(keyword)
                print(len(list(intent_dict.keys())))
                # print len(company_list)
                return render(request, 'zhuanlifa_result.html', {'intent': intent_dict, 'company': company_list})
            else:
                intent_dict = baiteng.search(keyword)
                return render(request, 'zhuanlifa_result.html', {'intent': intent_dict})

    else:
        form = ZhuanliForm()
        return render(request, 'zhuanlifa.html', {'form': form})

def keywords_show(request):
    return render(request, 'keywords_show.html')

def yaopinshoushen(request):
    return render(request, 'yaopinshoushen.html')

def study_xiansuo(request):
  return render(request, 'study_xiansuo.html')

def jigougenzong(request):
  if request.method == 'POST':
    form = AddForm(request.POST)#form 包含提交的数据
    # zif form.is_valid():# 如果提交的数据合法
  #           keyword = form.cleaned_data['keyword']
  #           projects_list = list(Company.objects.filter(company_name__contains=keyword).values_list())
  #           projects_num = len(projects_list)
  #           field_num = 0
  #           if projects_num!=0:
  #               field_num = len(projects_list[0])
  #           return render(request,'showresult.html',{'project_list':json.dumps(projects_list),'projects_num':projects_num,'field_num':field_num})
  #       else:
  #             #return HttpResponse("no info!")
  #             return render(request, 'zhuanlifa.html' {'form': form})
  else:
    form = AddForm()
  return render(request, 'jigougenzong.html', {'form': form})

def zixungenzong(request):
  news_list =[]
  if request.method == 'POST':
    form = AddForm(request.POST)#form 包含提交的数据
    if form.is_valid():
        keyword = form.cleaned_data['keyword']
        print (keyword)
        news_list = baidu_news_search(keyword,3,5) # 通过关键词搜取百度新闻
        print (news_list)
    else:
        return HttpResponse("No info!")
  else:
    form = AddForm()
  return render(request, 'zixungenzong.html', {'form': form, 'news_list':news_list})


def for_track(request):
  return render(request, 'for_track.html')

def business_change(request):
  form=businesschangeForm()
  projectss=Project.objects.all()
  return render_to_response('business_change.html',locals())

def firm_steer(request):
  return render(request, 'firm_steer.html')


def list_method(request):
  form=CompanyForm()
  companys=Company.objects.all()
  return render_to_response('list_method.html',locals())


def patent_details(request):
  return render(request, 'patent_details.html')


def test_wayne(request):
    out = ['this is a test1','this a test2']
    context = {'out': out}
    my_choice = request.POST['choice']
    print(my_choice)
    out.append(my_choice)
    context = {'out': out}

    # return HttpResponse(out_list)
    return render(request,'test_wayne.html', context)

def track_asset(request):
    """
    机构跟踪法
    Dict{基金管理人：{'wanted_companies': 符合要求公司, 'all_companies': 旗下所有公司}}
    """
    if request.method == 'POST':
        form = AddForm(request.POST)
        if form.is_valid():
            keyword = form.cleaned_data['keyword'].split()
            result_dict = {}
            for key in keyword:
                result_dict = dict(sta.track(key), **result_dict)
                # result_list.append(sta.track(key))
            return render(request, 'track_asset_result.html', {'result': result_dict})
    else:
        form = AddForm()
        return render(request, 'track_asset.html', {'form': form})

def medicine_trial(request):
    """
    药品受审企业推荐
    2017.4.28
    为方便测试仅输出公司名称
    调整接口函数的输出可获取更多信息
    """
    print(request.method)
    if request.method == 'POST':
        result_list = spider_medicine.search_by_qichacha()
        # result_list = ['company1', 'company2']
        return render(request, 'medicine_trial_result.html', {'result': result_list})
    else:
        form = AddForm()
        return render(request, 'medicine_trial.html', {'form': form})

def clinical_data(request):
    """
    临床批文企业推荐
    类似药品受审企业推荐
    """
    print(request.method)
    if request.method == 'POST':
        result_list = spider_medicine.search_by_qichacha(30)
        return render(request, 'clinical_data_result.html', {'result': result_list})
    else:
        form = AddForm()
        return render(request, 'clinical_data.html', {'form': form})

