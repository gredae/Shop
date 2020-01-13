from django.contrib import admin
from . import models
# Register your models here.

admin.site.register(models.User)
admin.site.register(models.User_detail)
admin.site.register(models.Receiv_addr)
admin.site.register(models.Category)
admin.site.register(models.Goods)
admin.site.register(models.Good_detail)
admin.site.register(models.Good_img)
admin.site.register(models.Good_icon_img)
admin.site.register(models.Stock)
admin.site.register(models.Banner)
admin.site.register(models.Comment)
admin.site.register(models.Comment_img)
admin.site.register(models.Order)
admin.site.register(models.Order_son)
admin.site.register(models.Return_goods)
