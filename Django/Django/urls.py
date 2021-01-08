"""Django URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/dev/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from DjangoTest import views as my_views  # new

urlpatterns = [
    url(r'^$', my_views.index, name="index"),
    url(r'^home/$', my_views.home, name="home"),
    url(r'^check/$', my_views.check, name="check"),
    url(r'^addPhotos/$', my_views.addPhotos, name="addPhotos"),
    url(r'^admin/', admin.site.urls),
]

