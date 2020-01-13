from django_filters.rest_framework import filterset
from django_filters.rest_framework import filters
from api import models

class CommentAdvancedFilter(filterset.FilterSet):

    class Meta:
        model = models.Comment
        fields = ['grade']


class OrderAdvancedFilter(filterset.FilterSet):

    class Meta:
        model = models.Order
        fields = ['order_status']


class GoodAdvancedFilter(filterset.FilterSet):
    #
    # min_price = filters.NumberFilter(field_name='price', lookup_expr='gte')
    # max_price = filters.NumberFilter(field_name='price', lookup_expr='lte')

    class Meta:
        model = models.Goods
        fields = ['cate']
