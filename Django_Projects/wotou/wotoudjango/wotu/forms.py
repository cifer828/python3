# coding:utf-8
from django import forms


PROJ_TYPE = (('web', 'WEB网站设计'), ('pic', '图像处理算法'), ('deep', '深度学习应用'))
PROJ_LAN = (('j', 'Java'), ('p', 'Python'), ('c', 'C++'), ('php', 'Php'), ('o', '无特殊要求'))


class AddForm(forms.Form):
    keyword = forms.CharField(error_messages={'required':'关键字不能为空'},widget=forms.TextInput(attrs={'class': 'form-control'}))

class LoginForm(forms.Form):
    user_name = forms.CharField(widget=forms.TextInput(attrs={'name':'form-username','placeholder':'Username...','class':'form-username form-control','id':'form-username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'name':'form-password','placeholder':'Password...','class':'form-password form-control','id':'form-password'}))

class SignupForm(forms.Form):
    email = forms.CharField(widget=forms.TextInput(
        attrs={'name': 'form-email', 'placeholder': 'Email...', 'class': 'form-email form-control',
               'id': 'form-email'}))
    user_name = forms.CharField(widget=forms.TextInput(
        attrs={'name': 'form-username', 'placeholder': 'Username...', 'class': 'form-username form-control',
               'id': 'form-username'}))
    password = forms.CharField(widget=forms.PasswordInput(
        attrs={'name': 'form-password', 'placeholder': 'Password...', 'class': 'form-password form-control',
               'id': 'form-password'}))
    password2 = forms.CharField(widget=forms.PasswordInput(
        attrs={'name': 'form-password', 'placeholder': 'input your Password again...', 'class': 'form-password form-control',
               'id': 'form-password'}))

class CompanyForm(forms.Form):
  company_name=forms.CharField(max_length=100)
  company_registdate=forms.CharField(max_length=100)
  company_mail=forms.CharField(max_length=100)
  company_preniumplan=forms.CharField(max_length=100)

class businesschangeForm(forms.Form):
  pro_name=forms.CharField(max_length=100)
  change_date=forms.CharField(max_length=100)
  before_mail=forms.CharField(max_length=100)
  after_mail=forms.CharField(max_length=100)


class XiansuoForm(forms.Form):
    keyword = forms.CharField(error_messages={'required':'关键字不能为空'},widget=forms.TextInput(attrs={'class': 'datainp'}))

class ZhuanliForm(forms.Form):
    #search_type = forms.IntegerField(error_messages={'required': '关键字不能为空'},widget=forms.TextInput(attrs={'class': 'form-control'}))
    keyword = forms.CharField(error_messages={'required':'关键字不能为空'},widget=forms.TextInput(attrs={'class': 'form-control'}))
    search_type = forms.ChoiceField(label='搜索类型：',
                                     choices=(('1', '企业'), ('2', '关键词')),
                                     widget=forms.RadioSelect())