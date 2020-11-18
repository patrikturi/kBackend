"""kbackend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.contrib import admin
from django.urls import path, include

from . import views
from core.decorators import login_wrapper

admin.autodiscover()
admin.site.login = login_wrapper(admin.site.login)


urlpatterns = [
    path('adminsite/', admin.site.urls),
    path('api/v1/core/csrf-token/', views.CsrfView.as_view()),
    path('api/v1/users/', include('users.urls')),
    path('api/v1/soccer/', include('soccer.urls')),
]

if settings.IS_TEST:
    test_pattern = path('test/basic-auth/', views.BasicAuthTestView.as_view())
    urlpatterns.append(test_pattern)
