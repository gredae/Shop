
import os,django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "shop_api.settings")
django.setup()
from .celery import app
from api.models import Order

@app.task
def deliver_goods(order_id):
    row = Order.objects.filter(order_id=order_id).update(order_status=2)
    print('已发货')

