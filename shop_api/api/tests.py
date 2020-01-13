from django.test import TestCase

# Create your tests here.

# import pymysql, random
#
# con = pymysql.Connect(host='127.0.0.1', user='root', password="123456",
#                       database='shop', port=3306)
# cursor = con.cursor()
# sql = "insert into shop_good_detail(is_delete, is_show, create_time, update_time, good_id, old_price, new_price, parameter, quota) values('%d', '%d', '%s', '%s', '%d', '%s', '%s', '%s', '%s')"
# for i in range(1, 41):
#     price = 5000
#     new_price = price * random.random()
#     data = (
#     0, 1, '2019-12-23 20:08:08', '2019-12-23 20:08:08', i, price, int(new_price), '白色', 0)  # 插入数据(元组)
#     cursor.execute(sql % data)
#     price -= 500
#     new_price = price * random.random()
#     data = (
#     0, 1, '2019-12-23 20:08:08', '2019-12-23 20:08:08', i, price, int(new_price), '黑色', 0)  # 插入数据(元组)
#     cursor.execute(sql % data)
#     price -= 500
#     new_price = price * random.random()
#     data = (
#     0, 1, '2019-12-23 20:08:08', '2019-12-23 20:08:08', i, price, int(new_price), '黄色', 0)  # 插入数据(元组)
#     cursor.execute(sql % data)

# sql = "insert into shop_icon_img(is_delete, is_show, create_time, update_time, img, good_detail_id) values('%d', '%d', '%s', '%s', '%s', '%s')"
# for i in range(121, 151):
#     data = (
#     0, 1, '2019-12-23 20:08:08', '2019-12-23 20:08:08', 'good/icon/ef69ca3c055cd11c459bc4f171799a86.jpeg', i)  # 插入数据(元组)
#     cursor.execute(sql % data)
#     data = (
#         0, 1, '2019-12-23 20:08:08', '2019-12-23 20:08:08', 'good/icon/ef69ca3c055cd11c459bc4f171799a86.jpeg',
#         i)  # 插入数据(元组)
#     cursor.execute(sql % data)
#     data = (
#         0, 1, '2019-12-23 20:08:08', '2019-12-23 20:08:08', 'good/icon/ef69ca3c055cd11c459bc4f171799a86.jpeg',
#         i)  # 插入数据(元组)
#     cursor.execute(sql % data)


# sql = "INSERT INTO shop_stock(is_delete, is_show, create_time, update_time, stock, sold, good_detail_id) values('%d', '%d', '%s', '%s', '%d', '%d', '%s')"
#
# for i in range(1, 151):
#     stock = random.randint(3000,100000)
#     sold = 0
#     while stock > sold:
#         sold = random.randint(3000,100000)
#     data = (
#     0, 1, '2019-12-23 20:08:08', '2019-12-23 20:08:08', stock, sold, i)  # 插入数据(元组)
#     cursor.execute(sql % data)


# con.commit()
# import uuid
# print("".join(str(uuid.uuid4()).split("-")))
# import requests, json
#
# response = requests.get(url='https://www.kuaidi100.com/query?type=zhongtong&postid=73124161428372&temp=0.5313968069449448')
# json_dic = response.content.decode()
#
# dic = json.loads(json_dic)
# data = dic.get('data')
# for item in data:
#     print(item)

if __name__ == '__main__':
    from acelery.tasks import Deliver_goods
    from api import models
    Deliver_goods.delay('cd2a5ce703ad4a79ba62ec37c647dee5')


