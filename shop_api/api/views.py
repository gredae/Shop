from django.shortcuts import HttpResponse
from rest_framework.response import Response
from rest_framework.views import APIView
from utils.response import APIResponse
from utils import filter as myfilter
from utils.coursePage import CoursePageNumberPagination, GoodPageNumberPagination
from rest_framework.filters import SearchFilter
from . import serializers
import re, os, hashlib, random
from . import models
from utils import throttlings, IP
from libs.sms import SMS
from django.core.cache import cache
from django.conf import settings
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.views.decorators.csrf import csrf_exempt
from rest_framework import generics
from libs.iPay.pay import alipay
from libs.iPay.setting import GATEWAY
import requests, json, datetime
from django_filters.rest_framework import DjangoFilterBackend


# Create your views here.
@csrf_exempt
def ERROR(request):
    return HttpResponse(status=404)


class Login(APIView):
    permission_classes = []
    authentication_classes = []

    def post(self, request, *args, **kwargs):
        serializer = serializers.LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return APIResponse(msg='登录成功', results={
            'username': serializer.username,
            'token': serializer.token,
            'is_admin': serializer.is_admin
        })


class Checkphone(APIView):
    permission_classes = []
    authentication_classes = []

    def post(self, request, *args, **kwargs):
        phone = request.data.get('phone')
        if not phone:
            return APIResponse(msg='参数有误', http_status=400)
        if not re.match(r'^1[3-9][0-9]{9}$', phone):
            return APIResponse(status=1, msg='手机号有误', http_status=400)
        try:
            user_obj = models.User.objects.get(is_active=True, phone=phone)
        except:
            return APIResponse(msg='手机号未注册')
        return APIResponse(msg='手机号已注册')


class SMSAPIView(APIView):
    permission_classes = []
    authentication_classes = []
    throttle_classes = [throttlings.SmsThrottling]

    def post(self, request, *args, **kwargs):
        phone = request.data.get('phone')
        if not phone:
            return APIResponse(msg='参数有误', http_status=400)
        # 只需判断是否正确，不需要判断是否注册
        if not re.match(r'^1[3-9][0-9]{9}$', phone):
            return APIResponse(status=1, msg='手机号有误', http_status=400)

        code = SMS.get_code()
        if SMS.send_sms(phone, code, settings.SMS_EXP):
            cache.set(settings.SMS_KEY % phone, code, settings.SMS_EXP * 60)
            return APIResponse(msg="信息发送成功")
        return APIResponse(status=1, msg='信息发送失败', http_status=500)


class RegisterAPIView(APIView):
    permission_classes = []
    authentication_classes = []

    def post(self, request, *args, **kwargs):
        serializer = serializers.RegisterModelSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_obj = serializer.save()
        models.Good_detail.objects.create(user=request.user)
        return APIResponse(msg="用户注册成功")


class Getip(APIView):

    def get(self, request, *args, **kwargs):
        ip = IP.get_ip(request)
        return APIResponse(data=ip)


class CheckAdmin(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        return APIResponse(results=request.user.is_admin)


class Userinfo(APIView):

    def get(self, request, *args, **kwargs):
        detail = models.User_detail.objects.filter(user=request.user, is_delete=False).first()
        consume = request.user.consume
        name = request.user.name if request.user.name else request.user.username
        order_ls = models.Order.objects.filter(order_user=request.user, is_delete=False)
        count0 = list(filter(lambda order: order.order_status == 0, order_ls))  # type: list
        count1 = list(filter(lambda order: order.order_status == 1, order_ls))
        count2 = list(filter(lambda order: order.order_status == 2, order_ls))
        count3 = list(filter(lambda order: order.order_status == 3, order_ls))
        order_all = order_ls
        return APIResponse(
            name=name,
            consume='普通会员' if consume < 5000 else '高级会员' if consume < 500000 else '终生会员',
            phone=request.user.phone,
            email=request.user.email,
            avate=settings.BASE_URL + str(request.user.avate),
            count0=len(count0),
            count1=len(count1),
            count2=len(count2),
            count3=len(count3),
            order_all=len(order_all)
        )


class Userdetail(APIView):

    def get(self, request, *args, **kwargs):
        detail = models.User_detail.objects.filter(user=request.user, is_delete=False).first()
        consume = request.user.consume
        name = request.user.name if request.user.name else request.user.username
        return APIResponse(
            name=name,
            consume='普通会员' if consume < 5000 else '高级会员' if consume < 500000 else '终生会员',
            phone=request.user.phone,
            email=request.user.email,
            avate=settings.BASE_URL + str(request.user.avate),
            sex=detail.gender,
            province=detail.province,
            city=detail.city,
            area=detail.area
        )

    def post(self, request, *args, **kwargs):
        file_obj = request.FILES.get('file', None)
        if not file_obj:
            return APIResponse(status=1, msg='上传文件失败', http_status=400)
        type = file_obj.name.split('.')[-1]
        m5 = hashlib.md5()
        # 对二进制进行MD5计算
        m5.update(file_obj.file.read())
        file_obj.name = m5.hexdigest() + '.' + type
        if os.path.exists(os.path.join(settings.MEDIA_ROOT, 'user/icon', file_obj.name)):
            request.user.avate = 'user/icon/' + file_obj.name
        else:
            request.user.avate = file_obj
        request.user.save()

        return APIResponse(avatar='http://127.0.0.1:8086/media/' + str(request.user.avate))

    def put(self, request, *args, **kwargs):
        user_obj = request.user  # type:models.User
        detail = user_obj.detail
        # 修改昵称
        user_obj.name = request.data.get('name')
        # 修改邮箱
        email = request.data.get('email')
        if not re.match(r'.*@.*', email):
            return APIResponse(http_status=400, msg='错误的邮箱地址')
        user_obj.email = email
        user_obj.save()
        # 修改性别
        detail.sex = 1 if request.data.get('sex') == '男' else 2 if request.data.get('sex') == '女' else 3
        # 修改省份
        detail.province = request.data.get('province')
        # 修改城市
        detail.city = request.data.get('city')
        # 修改区县
        detail.area = request.data.get('area')
        detail.save()

        return APIResponse(msg='信息修改成功')


class Reset_pwd(APIView):
    def put(self, request, *args, **kwargs):
        serializer = serializers.PwdSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        old_pwd = serializer.validated_data.get('old_pwd')
        pwd = serializer.validated_data.get('pwd')
        if not request.user.check_password(old_pwd):
            return APIResponse(status=1, msg='旧密码错误', http_status=400)
        request.user.set_password(pwd)
        request.user.save()
        return APIResponse(msg='密码修改成功')


class Addr(APIView):

    def get(self, request, id=None, *args, **kwargs):
        print(id)
        if not id:
            addrs = models.Receiv_addr.objects.filter(user=request.user, is_delete=False)
            return APIResponse(results=serializers.addrserializer(addrs, many=True).data)
        try:
            addrs = models.Receiv_addr.objects.get(user=request.user, pk=id, is_delete=False)
        except:
            return APIResponse(status=1, msg='参数错误', http_status=400)
        return APIResponse(results=serializers.addrserializer(addrs).data)

    def post(self, request, id=None, *args, **kwargs):
        if id:
            return APIResponse(status=1, msg='参数错误', http_status=400)
        serializer = serializers.addrserializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        addr_obj = models.Receiv_addr.objects.create(**serializer.validated_data, user=request.user, is_delete=False)
        return APIResponse(msg='添加收货地址成功')

    def delete(self, request, id=None, *args, **kwargs):

        if not id:
            return APIResponse(status=1, msg='参数错误', http_status=400)
        try:
            row = models.Receiv_addr.objects.filter(user=request.user, pk=id, is_delete=False).update(is_delete=True)
            if not row:
                return APIResponse(msg='删除收货地址失败')
        except:
            return APIResponse(status=1, msg='发生未知错误，请联系管理员', http_status=500)
        return APIResponse(msg='收货地址删除成功')

    def put(self, request, id=None, *args, **kwargs):

        if not id:
            return APIResponse(status=1, msg='参数错误', http_status=400)
        serializer = serializers.addrserializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            row = models.Receiv_addr.objects.filter(user=request.user, pk=id, is_delete=False).update(
                **serializer.validated_data)
            if not row:
                return APIResponse(msg='修改收货信息错误')
        except:
            return APIResponse(status=1, msg='发生未知错误，请联系管理员', http_status=500)
        return APIResponse(msg='修改收货信息成功')


class Banner(generics.ListAPIView):
    authentication_classes = []
    permission_classes = []
    queryset = models.Banner.objects.filter(is_delete=False, is_show=True)
    serializer_class = serializers.BannerSerializer


class Cate(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, *args, **kwargs):
        query_set = models.Category.objects.filter(is_delete=False, is_show=True, cate_self=None)
        ls = []
        for cate in query_set:
            cate_obj = serializers.CateSerializer(cate).data
            serializer = serializers.CateSerializer(cate.cate_son.all(), many=True)
            cate_obj['cate_self'] = serializer.data
            ls.append(cate_obj)

        return APIResponse(results=ls)


class Top(generics.ListAPIView):
    authentication_classes = []
    permission_classes = []
    queryset = [top.good for top in models.Top_good.objects.filter(is_delete=False, is_show=True)[:4]]
    serializer_class = serializers.TopSerializer


class Cate_good(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, *args, **kwargs):
        query_set = models.Category.objects.filter(is_delete=False, is_show=True, cate_self=None)
        ls = []
        for cate in query_set:
            cate_obj = serializers.CateSerializer(cate).data
            serializer = serializers.CateSerializer(cate.cate_son.all(), many=True)

            good_id = [ca.id for ca in cate.cate_son.all()]
            good_id.append(cate.id)
            goods = random.sample([good for good in models.Goods.objects.filter(cate__in=good_id)], 5)
            ser = serializers.cate_goodSerializer(goods, many=True, context={"request": request})
            cate_obj['goods'] = ser.data

            cate_obj['cate_self'] = serializer.data
            ls.append(cate_obj)

        return APIResponse(results=ls)

# 当时批量上传图片使用的接口 （建议直接弃用）
class Add_good_img(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request, id=None, *args, **kwargs):

        if not id:
            return APIResponse(http_status=400)
        file_obj = request.FILES.get('file', None)
        if not file_obj:
            return APIResponse(status=1, msg='上传文件失败', http_status=400)
        type = file_obj.name.split('.')[-1]
        m5 = hashlib.md5()
        # 对二进制进行MD5计算
        m5.update(file_obj.file.read())
        file_obj.name = m5.hexdigest() + '.' + type
        good_img_obj = models.Good_icon_img(good_detail_id=id)
        if os.path.exists(os.path.join(settings.MEDIA_ROOT, 'good/icon', file_obj.name)):
            good_img_obj.img = 'good/icon/' + file_obj.name
        else:
            good_img_obj.img = file_obj
        good_img_obj.save()

        return APIResponse()


class GoodDetail(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, id=None, *args, **kwargs):
        if id:
            good_obj = models.Goods.objects.filter(pk=id, is_delete=False, is_show=True).first()
            if not good_obj:
                return APIResponse(status=1, msg='参数错误', http_status=400)
            good_detail_ls = models.Good_detail.objects.filter(good=good_obj, is_delete=False, is_show=True)
            good_data = serializers.cate_goodSerializer(good_obj, context={"request": request}).data
            good_data['detail'] = []
            for good_detail in good_detail_ls:
                icon_img = models.Good_icon_img.objects.filter(good_detail=good_detail)
                detail_data = serializers.Good_detailModelSerializer(good_detail).data
                icon_data = serializers.Icon_imgModelSerializer(icon_img, many=True, context={"request": request}).data
                detail_data['img'] = icon_data
                good_data['detail'].append(detail_data)

            top_good_ls = random.sample(
                [good for good in models.Goods.objects.exclude(pk=id, is_delete=False, is_show=True)], 8)
            top_good_data = serializers.TopSerializer(top_good_ls, many=True, context={"request": request}).data
            good_data['top_good'] = top_good_data
            img_ls = models.Good_img.objects.filter(good=good_obj)
            img_data = serializers.imgModelSerializer(img_ls, many=True, context={"request": request}).data
            good_data['img'] = img_data

            return APIResponse(results=good_data)

        return APIResponse(status=1, msg='参数错误', http_status=400)


class Goods(generics.ListAPIView):

    authentication_classes = []
    permission_classes = []

    # 设置搜索字段
    search_fields = ['name']
    # 过滤器
    filter_backends = [DjangoFilterBackend, SearchFilter]
    # 自定义高级过滤
    filter_class = myfilter.GoodAdvancedFilter
    # 分页器
    pagination_class = GoodPageNumberPagination

    queryset = models.Goods.objects.filter(is_delete=False, is_show=True)
    serializer_class = serializers.cate_goodSerializer


class CommentListAPIView(generics.ListAPIView):
    authentication_classes = []
    permission_classes = []
    queryset = models.Comment.objects.filter(is_delete=False, is_show=True)
    serializer_class = serializers.CommentModelSerializer

    # 过滤器
    filter_backends = [DjangoFilterBackend]
    # 自定义高级过滤
    filter_class = myfilter.CommentAdvancedFilter
    # 自定义分页器
    pagination_class = CoursePageNumberPagination


    def get(self, request, id=None, *args, **kwargs):
        if not id:
            return APIResponse(status=1, msg='参数错误', http_status=400)

        CommentListAPIView.queryset = self.queryset.filter(good_id=id)

        response = super(CommentListAPIView, self).get(self, request, *args, **kwargs)
        CommentListAPIView.queryset = models.Comment.objects.filter(is_delete=False, is_show=True)
        return response


class Push_comment(APIView):

    def post(self, request, id=None, *args, **kwargs):

        form = request.data
        comment_ls = []
        for k, v in form.items():

            comment_obj = models.Comment(
                good_id=k,
                user=request.user,
                user_avate=request.user.avate,
                user_name=request.user.name,
                grade=v.get('score'),
                context=v.get('context') if v.get('context') else '该用户没有作出评论'

            )
            comment_ls.append(comment_obj)
        row = models.Comment.objects.bulk_create(comment_ls)

        order_obj = models.Order.objects.filter(order_id=id)
        if not order_obj:
            return APIResponse(status=1, msg='参数错误', http_status=400)

        row = order_obj.update(order_status=4)

        return APIResponse(msg='发布评论成功')


class Car_info(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, *args, **kwargs):
        ids = request.query_params.get('ids').split(',')
        detail_ls = models.Good_detail.objects.filter(pk__in=ids)
        ls = []
        for detail in detail_ls:
            good_obj = detail.good
            good_data = serializers.TopSerializer(good_obj, context={"request": request}).data
            detail_data = serializers.Good_detailModelSerializer(detail).data
            detail_data['icon'] = good_data['icon']
            detail_data['name'] = good_data['name']
            ls.append(detail_data)

        return APIResponse(results=ls)


from uuid import uuid4


class Order(APIView):

    def get(self, request, *args, **kwargs):
        order_id = request.query_params.get('order_id')
        try:
            order_obj = models.Order.objects.get(order_id=order_id, is_show=True, is_delete=False)
        except:
            return APIResponse(status=1, msg='参数错误', http_status=400)

        pay_url = alipay.api_alipay_trade_page_pay(
            subject=order_obj.order_title,  # 订单标题
            out_trade_no=order_obj.order_id,  # 订单号
            total_amount=str(order_obj.pay_money),  # 订单金额
            return_url=settings.PAY_RETURN_URL,  # 前端回调函数
            notify_url=settings.PAY_NOTIFY_URL,  # 后端回调函数
            timeout_express=settings.PAY_EXP,  # 订单超时时间
        )

        return APIResponse(results=GATEWAY + pay_url)

    def post(self, request, *args, **kwargs):

        serializer = serializers.OrderModelSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        addr_id = serializer.validated_data.get('addr_id')  # 地址id
        numgood = serializer.validated_data.get('numgood')  # type: dict   # 商品id 与 数量 字典
        express_id = serializer.validated_data.get('express_id')  # 配送方式
        order_remarks = serializer.validated_data.get('order_remarks')  # 备注
        order_son_ls = []
        good_money = 0
        try:
            addr_obj = models.Receiv_addr.objects.get(user=request.user, pk=addr_id, is_show=True, is_delete=False)
            for k, v in numgood.items():
                good_obj = models.Good_detail.objects.get(pk=k, is_delete=False, is_show=True)
                order_son_obj = models.Order_son(
                    good=good_obj,
                    good_name=good_obj.good.name,
                    good_price=good_obj.new_price,
                    good_number=v,
                    count_maney=good_obj.new_price * int(v)
                )
                good_money += order_son_obj.count_maney
                order_son_ls.append(order_son_obj)
            order_obj = models.Order.objects.create(
                order_id="".join(str(uuid4()).split("-")),
                order_title="".join(str(uuid4()).split("-")),
                order_user=request.user,
                pay_money=good_money + int(express_id),
                freight=express_id,
                good_maney=good_money,
                order_remarks=order_remarks,
                receiv_addr=addr_obj
            )
            if not order_obj:
                return APIResponse(status=1, msg='参数错误', http_status=400)
            for order_son in order_son_ls:
                order_son.order_id = order_obj.id
            row = models.Order_son.objects.bulk_create(order_son_ls)
            if not row:
                return APIResponse(status=1, msg='参数错误', http_status=400)

        except:
            return APIResponse(status=1, msg='参数错误', http_status=400)
        pay_url = alipay.api_alipay_trade_page_pay(
            subject=order_obj.order_title,  # 订单标题
            out_trade_no=order_obj.order_id,  # 订单号
            total_amount=str(order_obj.pay_money),  # 订单金额
            return_url=settings.PAY_RETURN_URL,  # 前端回调函数
            notify_url=settings.PAY_NOTIFY_URL,  # 后端回调函数
            timeout_express=settings.PAY_EXP,  # 订单超时时间
        )

        return APIResponse(results=GATEWAY + pay_url)


class OrderListAPIView(generics.ListAPIView):
    queryset = models.Order.objects.filter(is_delete=False, is_show=True)
    serializer_class = serializers.OrderModelSerializer

    # 过滤器
    filter_backends = [DjangoFilterBackend]
    # 自定义分页器
    pagination_class = CoursePageNumberPagination
    # 自定义高级过滤
    filter_class = myfilter.OrderAdvancedFilter

    def get(self, request, *args, **kwargs):
        OrderListAPIView.queryset = self.queryset.filter(order_user=request.user)

        response = super(OrderListAPIView, self).get(request, *args, **kwargs)
        OrderListAPIView.queryset = models.Order.objects.filter(is_delete=False, is_show=True)
        return response


class Pay_success(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request, *args, **kwargs):
        serial_number = request.data.get('trade_no')
        pay_time = request.data.get('gmt_payment')
        order_id = request.data.get('out_trade_no')
        row = models.Order.objects.filter(order_id=order_id).update(
            order_status=1,
            pay_time=pay_time,
            serial_number=serial_number
        )

        from order_celery.tasks import deliver_goods
        from utils.eta_util import eta_minutes
        # 一分钟后发货
        deliver_goods.apply_async(args=(order_id,), eta=eta_minutes(1))
        
        return Response('success')


class Order_detail(APIView):

    def get(self, request, id=None, *args, **kw):
        if not id:
            return APIResponse(status=1, msg='参数错误', http_status=400)
        order_obj = models.Order.objects.filter(order_id=id, is_delete=False, is_show=True).first()
        order_data = serializers.OrderDetailModelSerializer(order_obj).data
        order_son_ls = order_obj.order_son.all()
        good_ls = []
        for order_son in order_son_ls:
            good_detail_obj = order_son.good
            good_obj = good_detail_obj.good
            good_detail_data = serializers.Good_detailModelSerializer(good_detail_obj).data
            good_detail_data['count'] = order_son.good_number
            good_detail_data['name'] = good_obj.name
            good_detail_data['icon'] = str(good_detail_obj.icon_img.all().first().img)
            good_ls.append(good_detail_data)
        addr_obj = order_obj.receiv_addr
        addr_data = serializers.addrserializer(addr_obj).data

        logistics = []

        response = requests.get(
            url='https://www.kuaidi100.com/query?type=zhongtong&postid=73124161428372&temp=0.5313968069449448')
        json_dic = response.content.decode()

        dic = json.loads(json_dic)
        data = dic.get('data')
        for item in data:
            dic = {
                'time': item.get('time'),
                'context': item.get('context')
            }
            logistics.append(dic)

        return APIResponse(results={
            "order_info": order_data,
            "order_son_info": good_ls,
            "addr_info": addr_data,
            "logistics_info": logistics
        })


class Order_success(APIView):

    def post(self, request, id=None, *args, **kwargs):

        if not id:
            return APIResponse(status=1, msg='参数错误', http_status=400)

        row = models.Order.objects.filter(order_user=request.user, order_id=id).update(order_status=3, confirm_receipt_time=datetime.datetime.now())

        return APIResponse(msg='状态更新成功')


