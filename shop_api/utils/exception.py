
from rest_framework.views import exception_handler as drf_exception_handler
from rest_framework.views import Response
from rest_framework import status
from utils.log import logger


def exception_handler(exc, context):
    response = drf_exception_handler(exc, context)

    if response is None:

        # 异常模块就是记录项目的错误日志
        logger.error('%s - %s - %s' % (context['view'], context['request'].method, exc))

        return Response({
            'detail': '%s' % exc
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR, exception=True)
    return response