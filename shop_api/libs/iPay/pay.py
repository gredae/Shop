
from alipay import AliPay
from . import setting

alipay = AliPay(
    appid=setting.APPID,
    app_notify_url=None,
    app_private_key_string=setting.APP_PRIVATE_KEY_STRING,
    alipay_public_key_string=setting.ALIPAY_PUBLIC_KEY_STRING,
    sign_type=setting.SIGN_TYPE,
    debug=setting.DEBUG
)


