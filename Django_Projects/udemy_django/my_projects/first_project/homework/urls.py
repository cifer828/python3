from django.urls import path
from homework import views

app_name = "homework"

urlpatterns = [
    path('', views.index, name='index'),
    path('users', views.users, name='user'),
    path('register', views.register, name='register')
]
