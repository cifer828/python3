#encoding=utf-8


from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Company(models.Model):
    
    company_name = models.CharField(max_length=100)
    company_mail = models.CharField(max_length=100,null=True)
    company_registdate = models.CharField(max_length=100,null=True)
    company_preniumplan = models.CharField(max_length=100,null=True)

    # company_phone = models.CharField(max_length=100)
    # company_url = models.CharField(max_length=100)
    # company_address = models.CharField(max_length=200)
    # company_legal_representative = models.CharField(max_length=30)
    # company_status = models.CharField(max_length=100)#状态
    # company_field = models.CharField(max_length=20)#行业
    # registered_capital = models.FloatField(max_length=100,null=True)
    # registered_time = models.DateTimeField(max_length=10,null=True)
    # company_type = models.CharField(max_length=30)
    # business_term = models.FloatField(null=True)#营业期限
    # registered_organization = models.CharField(max_length=100)
    # uni_business_code = models.CharField(max_length=100)
    # business_scope = models.CharField(max_length=100)

class Project(models.Model):
	project_name=models.CharField(max_length=100)
	change_date=models.CharField(max_length=100)
	before_mail=models.CharField(max_length=100)
	after_mail=models.CharField(max_length=100)