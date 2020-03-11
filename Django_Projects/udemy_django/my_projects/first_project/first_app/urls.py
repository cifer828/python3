from django.urls import path
from first_app import views

# Template tagging
app_name = 'first_app'

urlpatterns = [
    path('', views.index, name='index'),
    path('register', views.register, name='register'),
    path('basics', views.basics, name='basics'),
    path('login', views.user_login, name='login'),
    path('logout', views.user_logout, name='logout'),
    path('special', views.special, name='special')
]