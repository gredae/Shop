"""shop_api URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
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
from django.views.static import serve
from django.conf import settings
from api import views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^media/(?P<path>.*)$', serve, {"document_root": settings.MEDIA_ROOT}),

    url(r'^user/login$', views.Login.as_view()),
    url(r'^user/check_phone$', views.Checkphone.as_view()),
    url(r'^user/sms$', views.SMSAPIView.as_view()),
    url(r'^user/register$', views.RegisterAPIView.as_view()),
    url(r'^user/info$', views.Userinfo.as_view()),
    url(r'^user/detail$', views.Userdetail.as_view()),
    url(r'^user/pwd$', views.Reset_pwd.as_view()),
    url(r'^user/addr$', views.Addr.as_view()),
    url(r'^user/addr/(?P<id>\d+)$', views.Addr.as_view()),

    url(r'^good/banner$', views.Banner.as_view()),
    url(r'^good/cate$', views.Cate.as_view()),
    url(r'^good/top$', views.Top.as_view()),
    url(r'^good/cate_good$', views.Cate_good.as_view()),
    url(r'^good/detail/(?P<id>\d+)$', views.GoodDetail.as_view()),
    url(r'^push/comment/(?P<id>.+)$', views.Push_comment.as_view()),
    url(r'^good/comment/(?P<id>\d+)$', views.CommentListAPIView.as_view()),
    url(r'^good$', views.Goods.as_view()),

    url(r'^car/info$', views.Car_info.as_view()),
    url(r'^create_order$', views.Order.as_view()),
    url(r'^order$', views.OrderListAPIView.as_view()),
    url(r'^order/detail/(?P<id>.+?)$', views.Order_detail.as_view()),
    url(r'^pay_success$', views.Pay_success.as_view()),
    url(r'^order_success/(?P<id>.+?)$', views.Order_success.as_view()),

    url(r'^util/ip$', views.Getip.as_view()),
    url(r'^checkAdmin$', views.CheckAdmin.as_view()),
    url(r'^add_good_img/(?P<id>\d+?)$', views.Add_good_img.as_view()),
    url(r'.*', views.ERROR),
]
