from pymongo import MongoClient
import datetime
from bs4 import BeautifulSoup
import requests

# Authentication Database認證資料庫
stockDB='mydb'
dbname = 'test-good1'


def constructor_stock():
    client = MongoClient("mongodb://ms0075415:RBWzbWx85ENGTqjd@ac-elfhgej-shard-00-00.ymufszp.mongodb.net:27017,ac-elfhgej-shard-00-01.ymufszp.mongodb.net:27017,ac-elfhgej-shard-00-02.ymufszp.mongodb.net:27017/?ssl=true&replicaSet=atlas-sbs9e1-shard-0&authSource=admin&retryWrites=true&w=majority")
    db = client[stockDB]
    return db

#----------------------------更新暫存的股票名稱--------------------------
def update_my_stock(user_name,  stockNumber, condition , target_price):
    db=constructor_stock()
    collect = db[user_name]
    collect.update_many({"favorite_stock": stockNumber }, {'$set': {'condition':condition , "price": target_price}})
    content = f"股票{stockNumber}更新成功"
    return content
#   -----------    新增使用者的股票       -------------
def write_my_stock(userID, user_name, stockNumber, condition , target_price):
    db=constructor_stock()
    collect = db[user_name]
    is_exit = collect.find_one({"favorite_stock": stockNumber})
    if is_exit != None :
        content = update_my_stock(user_name, stockNumber, condition , target_price)
        return content
    else:
        collect.insert_one({
                "userID": userID,
                "favorite_stock": stockNumber,
                "condition" :  condition,
                "price" : target_price,
                "tag": "stock",
                "date_info": datetime.datetime.now()
            })
        return f"{stockNumber}已新增至您的股票清單"
