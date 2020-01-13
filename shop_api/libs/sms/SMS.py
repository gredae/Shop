
from django.core.cache import cache
from django.conf import settings
import random

from qcloudsms_py import SmsSingleSender

from . import setting
from utils.log import logger

sender = SmsSingleSender(setting.appid, setting.appkey)

# 需要手机号、验证码、过期时间(min)
def send_sms(mobile, code, exp):
    try:
        response = sender.send_with_param(
            86,
            mobile,
            setting.template_id,
            params=[code, exp],
            sign=setting.sms_sign,
            extend="", ext="")
        if response and response.get('result') == 0:
            return True
        msg = response.get('result')  # 失败的状态码
    except Exception as msg:  # 失败的信息
        pass

    logger.error('短信发送失败：%s' % msg)
    return False


def get_code():
    code = ''
    for i in range(6):
        code += str(random.randint(0, 9))
    return str(code)

