## Models类

```python
from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class BaseModel(models.Model):
    is_delete = models.BooleanField(default=False, verbose_name='是否删除')
    is_show = models.BooleanField(default=True, verbose_name='是否显示')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True,verbose_name='更新时间')
    order = models.IntegerField(verbose_name='排序字段')

    class Meta:
        abstract = True
        verbose_name_plural = '基表'


class User(AbstractUser):
    avate = models.ImageField(upload_to='/icon', default='/icon/default.jpg', verbose_name='头像')
    name = models.CharField(max_length=20, verbose_name='昵称')
    consume = models.IntegerField(verbose_name='消费金额', default=0)

    class Meta:
        db_table = 'shop_user'
        verbose_name_plural = '用户表'
        
        
class User_detail(models.Model):
    user = models.OneToOneField(to='User', db_constraint=False, related_name='detail', verbose_name='关联的用户')
    choice_sex = ((1, '男'), (2, '女'), (3, '保密'))
    sex = models.IntegerField(choices=choice_sex, verbose_name='性别', default=3)
    addr = models.CharField(max_length=64, verbose_name='居住地')
    is_delete = models.BooleanField(default=False, verbose_name='是否删除')

    class Meta:
        db_table = 'shop_user_detail'
        verbose_name_plural = '用户详情表'
        
        
class Receiv_addr(BaseModel):
    user = models.ForeignKey(to='User', db_constraint=False, related_name='receiv_addr')
    is_default = models.BooleanField(default=False, verbose_name='是否是默认地址')
    phone = models.CharField(max_length=11, verbose_name='手机号')
    tag = models.CharField(max_length=20, verbose_name='地址标签')
    Consignee = models.CharField(max_length=16, verbose_name='收货人')
    # 在视图函数中转换成省
    province = models.IntegerField(verbose_name='省')
    # 在视图函数中转换成市
    city = models.IntegerField(verbose_name='市')
    # 在视图函数中转换成区/县
    county = models.IntegerField(verbose_name='区/县')
    detail_addr = models.CharField(max_length=128, verbose_name='详细地址')
    
    class Meta:
        db_table = 'shop_receiv_addr'
        verbose_name_plural = '收货地址表'
        
        
class Category(BaseModel):
    name = models.CharField(max_length=16, verbose_name='分类名')
    cate_self = models.ForeignKey(to='self', db_constraint=False, related_name='cate_son', verbose_name='二级分类')

    class Meta:
        db_table = 'shop_cate'
        verbose_name_plural = '商品分类表'


class Goods(BaseModel):
    name = models.CharField(max_length=64, verbose_name='商品名')
    cate = models.ForeignKey(to='Category', db_constraint=False, related_name='good', verbose_name='商品分类')
    start_time = models.DateTimeField(verbose_name='商品秒杀结束时间', null=True)
    end_time = models.DateTimeField(verbose_name='商品秒杀结束时间', null=True)
    old_price = models.DecimalField(max_digits=8, decimal_places=2, verbose_name='商品原价')
    new_price = models.DecimalField(max_digits=8, decimal_places=2, verbose_name='商品现价')
    is_seckill = models.BooleanField(default=False, verbose_name='是否为秒杀商品')
    is_fresh = models.BooleanField(default=False, verbose_name='是否是生鲜商品')
    Fraction = models.DecimalField(max_digits=5, decimal_places=1, default=5, verbose_name='商品评分')

    class Meta:
        db_table = 'shop_goods'
        verbose_name_plural = '商品表'


class Good_detail(BaseModel):
    good = models.ForeignKey(to='Goods', db_constraint=False, related_name='detail', verbose_name='商品')
    info = models.TextField(verbose_name='商品介绍')
    command_count = models.IntegerField(verbose_name='评论数')
    month_sales = models.IntegerField(verbose_name='月售数')
    parameter = models.CharField(max_length=255, verbose_name='商品参数')  # 使用json字符串
    quota = models.IntegerField(verbose_name='限购数量')

    class Meta:
        db_table = 'shop_good_detail'
        verbose_name_plural = '商品详情表'


class Img(BaseModel):
    img = models.ImageField(upload_to='/img', verbose_name='图片路径')
    md5 = models.CharField(max_length=128, verbose_name='图片md5值')
    title = models.CharField(max_length=32, verbose_name='图片标题')
    isicon = models.BooleanField(verbose_name='是否是商品图标')
    goods = models.ForeignKey(to='Good_detail', db_constraint=False, related_name='img', verbose_name='商品展示图片')

    class Meta:
        db_table = 'shop_img'
        verbose_name_plural = '商品图片表'


class Stock(BaseModel):
    good_detail = models.ForeignKey(to='Good_detail', db_constraint=False, related_name='stock', verbose_name='商品id')
    stock = models.IntegerField(verbose_name='库存数')
    Sold = models.IntegerField(verbose_name='已售数')

    class Meta:
        db_table = 'shop_stock'
        verbose_name_plural = '库存表'


class Banner(BaseModel):
    good = models.ForeignKey(to='Goods', db_constraint=False, related_name='banner', verbose_name='链接的商品')
    img = models.ImageField(upload_to='/banner', verbose_name='轮播图表')
    title = models.CharField(max_length=64, verbose_name='轮播图标题')

    class Meta:
        db_table = 'shop_banner'
        verbose_name_plural = '轮播图表'


class Comment(BaseModel):
    good = models.ForeignKey(to='Goods', db_constraint=False, related_name='comment', verbose_name='评论的商品')
    user = models.ForeignKey(to='User', db_constraint=False, related_name='comment', verbose_name='评论人')
    user_avate = models.CharField(max_length=128, verbose_name='评论人头像')
    user_name = models.CharField(max_length=20, verbose_name='评论人昵称')
    choice_grade = ((1, '差评'),(3, '中评'),(5, '好评'),)
    grade = models.IntegerField(choices=choice_grade, verbose_name='商品评价')
    context = models.CharField(max_length=128, verbose_name='评论内容')
    comment_self = models.ForeignKey(to='self', db_constraint=False, related_name='comment', verbose_name='追评')
    # 后期加商品图片

    class Meta:
        db_table = 'shop_comment'
        verbose_name_plural = '评论表'


class Order(BaseModel):
    order_number = models.CharField(max_length=32, verbose_name='订单号')
    order_title = models.CharField(max_length=32, verbose_name='订单标题')
    serial_number = models.CharField(max_length=32, verbose_name='流水号')
    order_status_choice = (
        (0, '未付款'),
        (1, '待发货'),
        (2, '待收货'),
        (3, '待评价'),
        (4, '已评价'),
        (5, '退款中'),
        (6, '已退款'),
        (7, '已取消'),
    )
    order_status = models.IntegerField(choices=order_status_choice, verbose_name='订单状态')
    order_user = models.ForeignKey(to='User', db_constraint=False, related_name='order', verbose_name='下单用户')
    pay_money = models.DecimalField(max_digits=8, decimal_places=2, verbose_name='支付金额')
    pay_type_choice = ((1, '支付宝'), (2, '微信'),)
    pay_type = models.IntegerField(default=1, verbose_name='支付方式')
    pay_time = models.DateTimeField(verbose_name='支付时间')
    deliver_time = models.DateTimeField(verbose_name='发货时间')
    confirm_receipt_time = models.DateTimeField(verbose_name='确认收货时间')
    freight = models.DecimalField(max_digits=8, decimal_places=2, verbose_name='运费')
    good_maney = models.DecimalField(max_digits=8, decimal_places=2, verbose_name='商品金额')
    order_remarks = models.CharField(max_length=120, verbose_name='备注')
    logistics_number = models.CharField(max_length=20, default='73124161428372', verbose_name='物流单号')

    class Meta:
        db_table = 'shop_order'
        verbose_name_plural = '订单表'


class Order_son(BaseModel):
    order = models.ForeignKey(to='Order', db_constraint=False, related_name='order_son', verbose_name='链接的订单')
    good = models.ForeignKey(to='Goods', db_constraint=False, related_name='order_son', verbose_name='关联的商品')
    good_name = models.CharField(max_length=32, verbose_name='商品名称')
    good_cate_name = models.CharField(max_length=16, verbose_name='商品分类')
    good_price = models.DecimalField(max_digits=8, decimal_places=2, verbose_name='商品单价')
    good_number = models.IntegerField(verbose_name='商品数量')
    count_maney = models.DecimalField(max_digits=8, decimal_places=2, verbose_name='商品小计')

    class Meta:
        db_table = 'shop_order_son'
        verbose_name_plural = '订单子表'


class Return_goods(BaseModel):
    order = models.ForeignKey(to='Order', db_constraint=False, related_name='return', verbose_name='退货订单')
    return_money = models.DecimalField(max_digits=8, decimal_places=2, verbose_name='退款金额')
    return_msg = models.CharField(max_length=120, verbose_name='退款原因')
    return_number = models.CharField(max_length=20, verbose_name='退款编号')

    class Meta:
        db_table = 'shop_return_goods'
        verbose_name_plural = '退款退货表'


```

