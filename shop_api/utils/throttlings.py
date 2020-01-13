
from rest_framework.throttling import SimpleRateThrottle
from utils import IP

class SmsThrottling(SimpleRateThrottle):
    scope = 'Sms_time'

    def get_cache_key(self, request, view):
        # ip = IP.get_ip(request)

        return 'mobile_'+request.data.get('phone')


