
from rest_framework.pagination import PageNumberPagination

class CoursePageNumberPagination(PageNumberPagination):

    # 默认一页条数
    page_size = 5
    # 选择哪一页的key
    page_query_param = 'page'
    # 用户自定义一页条数
    page_size_query_param = 'page_size'
    # 用户自定义一页最大控制条数
    # 只有当page_size_query_param配置了的时候才需要配置
    # 也可以不配置，配置了限制最大条数（一般会做限制）
    max_page_size = 10


class GoodPageNumberPagination(PageNumberPagination):

    # 默认一页条数
    page_size = 20
    # 选择哪一页的key
    page_query_param = 'page'
    # # 允许用户自定义一页条数并设置关键字
    # page_size_query_param = 'page_size'
    # 用户自定义一页最大控制条数
    # 只有当page_size_query_param配置了的时候才需要配置
    # 也可以不配置，配置了限制最大条数（一般会做限制）
    # max_page_size = 10


