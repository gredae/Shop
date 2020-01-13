
from rest_framework import serializers
from rest_framework_jwt.utils import jwt_payload_handler, jwt_encode_handler
from api import models
import re
from django.conf import settings
from django.core.cache import cache

class LoginSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        min_length=5,
        max_length=12,
        error_messages={
            'invalid': '用户名中包含非法字符',
            'required': '用户名不能为空',
            'blank': '用户名不能为空',
            'null': '用户名不能为空',
            'min_length': '用户名至少需要5个字符',
            'max_length': '用户名最多需要12个字符',
        }
    )
    password = serializers.CharField(
        min_length=8,
        max_length=18,
        error_messages={
            'invalid': '密码中包含非法字符',
            'required': '密码不能为空',
            'blank': '密码不能为空',
            'null': '密码不能为空',
            'min_length': '密码至少需要8个字符',
            'max_length': '密码最多需要12个字符',
        }
    )

    class Meta:
        model = models.User
        fields = ['username', 'password']

    def validate(self, attrs):

        # 多方式登录
        user_obj = self._many_login(**attrs)
        # 签发token
        payload = jwt_payload_handler(user_obj)
        token = jwt_encode_handler(payload)
        # 将信息保存
        self.username = user_obj.username
        self.is_admin = user_obj.is_admin
        self.token = token

        return attrs

    def _many_login(self, **attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        # 邮箱
        if re.match(r'.*@.*', username):
            user_obj = models.User.objects.filter(is_active=True, email=username).first()   # type: models.User
        # 手机号
        elif re.match(r'^1[3-9][0-9]{9}$', username):
            user_obj = models.User.objects.filter(is_active=True, phone=username).first()   # type: models.User
        # 用户名
        else:
            user_obj = models.User.objects.filter(is_active=True, username=username).first()   # type: models.User
        # 用户名不存在
        if not user_obj:
            raise serializers.ValidationError({'username': ['用户名不存在']})
        # 密码错误
        if not user_obj.check_password(password):
            raise serializers.ValidationError({'password': ['密码错误']})

        return user_obj


class RegisterModelSerializer(serializers.ModelSerializer):

    phone = serializers.CharField(
        min_length=11,
        max_length=11,
        error_messages={
            'invalid': '手机号中包含非法字符',
            'required': '手机号不能为空',
            'blank': '手机号不能为空',
            'null': '手机号不能为空',
            'min_length': '手机号长度为11个字符',
            'max_length': '手机号长度为11个字符',
        }
    )
    password = serializers.CharField(
        min_length=8,
        max_length=18,
        error_messages={
            'invalid': '密码中包含非法字符',
            'required': '密码不能为空',
            'blank': '密码不能为空',
            'null': '密码不能为空',
            'min_length': '密码至少需要8个字符',
            'max_length': '密码最多需要18个字符',
        }
    )
    re_password = serializers.CharField(
        min_length=8,
        max_length=18,
        error_messages={
            'invalid': '确认密码中包含非法字符',
            'required': '确认密码不能为空',
            'blank': '确认密码不能为空',
            'null': '确认密码不能为空',
            'min_length': '确认密码至少需要8个字符',
            'max_length': '确认密码最多需要18个字符',
        }
    )
    code = serializers.CharField(
        min_length=6,
        max_length=6,
        error_messages={
            'invalid': '验证码中包含非法字符',
            'required': '验证码不能为空',
            'blank': '验证码不能为空',
            'null': '验证码不能为空',
            'min_length': '验证码长度为6个字符',
            'max_length': '验证码长度为6个字符',
        }
    )

    class Meta:
        model = models.User
        fields = ['phone', 'password', 're_password', 'code']

    def validate_phone(self, value):

        if not re.match(r'^1[3-9][0-9]{9}$', value):
            raise serializers.ValidationError('手机号码有误')
        try:
            models.User.objects.get(is_active=True, phone=value)
        except:
            return value
        raise serializers.ValidationError('手机号已注册')

    def validate_code(self, value:str):

        if value.isdigit():
            return value
        raise serializers.ValidationError('验证码包含非法字符')

    def validate(self, attrs):
        # 获取数据
        phone = attrs.get('phone')
        code = attrs.pop('code')
        password = attrs.get('password')
        re_password = attrs.pop('re_password')
        if password != re_password:
            raise serializers.ValidationError({'re_password': '两次密码不一致'})
        # print(settings.SMS_KEY)
        old_code = cache.get(settings.SMS_KEY % phone)
        # 判断数据验证码是否一致
        if code == '000000':
        # if code == old_code:
            cache.set(settings.SMS_KEY % phone, '0000', 0)
            attrs['username'] = phone
            return attrs
        raise serializers.ValidationError({'code': ['验证码错误']})

    def create(self, validated_data):
        return models.User.objects.create_user(**validated_data)


class PwdSerializer(serializers.ModelSerializer):

    old_pwd = serializers.CharField(
        min_length=8,
        max_length=18,
        error_messages={
            'invalid': '旧密码中包含非法字符',
            'required': '旧密码不能为空',
            'blank': '旧密码不能为空',
            'null': '旧密码不能为空',
            'min_length': '旧密码至少需要8个字符',
            'max_length': '旧密码最多需要18个字符',
        }
    )
    pwd = serializers.CharField(
        min_length=8,
        max_length=18,
        error_messages={
            'invalid': '新密码中包含非法字符',
            'required': '新密码不能为空',
            'blank': '新密码不能为空',
            'null': '新密码不能为空',
            'min_length': '新密码至少需要8个字符',
            'max_length': '新密码最多需要18个字符',
        }
    )
    re_pwd = serializers.CharField(
        min_length=8,
        max_length=18,
        error_messages={
            'invalid': '确认密码中包含非法字符',
            'required': '确认密码不能为空',
            'blank': '确认密码不能为空',
            'null': '确认密码不能为空',
            'min_length': '确认密码至少需要8个字符',
            'max_length': '确认密码最多需要18个字符',
        }
    )

    class Meta:
        model = models.User
        fields = ['old_pwd', 'pwd', 're_pwd']

    def validate(self, attrs):
        # 获取数据
        pwd = attrs.get('pwd')
        re_pwd = attrs.pop('re_pwd')
        if pwd != re_pwd:
            raise serializers.ValidationError({'re_password': '两次密码不一致'})
        return attrs


class addrserializer(serializers.ModelSerializer):

    phone = serializers.CharField(
        min_length=11,
        max_length=11,
        error_messages={
            'invalid': '手机号码中包含非法字符',
            'required': '手机号码不能为空',
            'blank': '手机号码不能为空',
            'null': '手机号码不能为空',
            'min_length': '手机号码需要11个字符',
            'max_length': '手机号码需要11个字符',
        }
    )
    province = serializers.CharField(
        error_messages={
            'invalid': '省份中包含非法字符',
            'required': '省份不能为空',
            'blank': '省份不能为空',
            'null': '省份不能为空'
        }
    )
    city = serializers.CharField(
        error_messages={
            'invalid': '城市中包含非法字符',
            'required': '城市不能为空',
            'blank': '城市不能为空',
            'null': '城市不能为空'
        }
    )
    area = serializers.CharField(
        error_messages={
            'invalid': '区县中包含非法字符',
            'required': '区县不能为空',
            'blank': '区县不能为空',
            'null': '区县不能为空'
        }
    )
    detail_addr = serializers.CharField(
        error_messages={
            'invalid': '地址详情中包含非法字符',
            'required': '地址详情不能为空',
            'blank': '地址详情不能为空',
            'null': '地址详情不能为空'
        }
    )
    consignee = serializers.CharField(
        error_messages={
            'invalid': '收货人中包含非法字符',
            'required': '收货人不能为空',
            'blank': '收货人不能为空',
            'null': '收货人不能为空'
        }
    )
    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = models.Receiv_addr
        fields = ['province', 'city', 'area', 'detail_addr', 'consignee', 'phone', 'id']

    def validate_phone(self, value):
        if not re.match(r'^1[3-9][0-9]{9}$', value):
            raise serializers.ValidationError('手机号码有误')
        return value


class BannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Banner
        fields = ['good', 'img']


class CateSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Category
        fields = ['id', 'name', 'cate_self']


class TopSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Goods
        fields = ['id', 'name', 'create_time', 'icon']


class cate_goodSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Goods
        fields = ['id', 'name', 'icon', 'old_price', 'new_price', 'sold', 'info']


class Good_detailModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Good_detail
        fields = ['id', 'old_price', 'new_price', 'parameter', 'quota', 'stock1']


class Icon_imgModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Good_icon_img
        fields = ['id', 'img']


class imgModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Good_img
        fields = ['id', 'img']


class CommentModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Comment
        fields = ['fuser_avatar', 'user_name', 'grade', 'context']


class OrderModelSerializer(serializers.ModelSerializer):

    addr_id = serializers.CharField(write_only=True)
    numgood = serializers.DictField(write_only=True)
    express_id = serializers.CharField(write_only=True)
    order_remarks = serializers.CharField(write_only=True, allow_blank=True)

    class Meta:
        model = models.Order
        fields = [
            'addr_id',
            'numgood',
            'express_id',
            'order_remarks',
            'order_id',
            'pay_money',
            'create_time',
            'status',
        ]
        read_only_fields = [
            'order_id',
            'pay_money',
            'create_time',
            'status',
        ]


class OrderDetailModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Order
        fields = [
            'create_time',
            'order_id',
            'order_title',
            'order_status',
            'pay_money',
            'pay_type',
            'pay_time',
            'deliver_time',
            'confirm_receipt_time',
            'freight',
            'good_maney',
            'order_remarks',
            'logistics_number',
            'status',
            'pay_type_msg',
        ]


class Order_son_DetailModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Order_son
        fields = '__all__'



