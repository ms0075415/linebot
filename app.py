#載入LineBot所需要的套件
from line_bot_api import *
from events.basic import *
from events.oil import *
from events.Msg_Template import *
from events.EXRate import *
from model.mongodb import *
import re
import twstock
import datetime
from bs4 import BeautifulSoup

app = Flask(__name__)

#抓使用者設定它關心的股票
def cache_users_stock():
    db = constructor_stock()
    nameList = db.list_collection_names()
    users = []
    for i in range(len(nameList)):
        collect = db[nameList[i]]
        cel = list(collect.find({"tag":'stock'}))
        users.append(cel)
    return users

#監聽所有來自callback的 Post Request
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

#處理訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    profile = line_bot_api.get_profile(event.source.user_id)
    uid = profile.user_id #使用者ID
    message_text = str(event.message.text).lower()
    msg = str(event.message.text).upper().strip() #使用者輸入的內容
    emsg = event.message.text
    user_name = profile.display_name #使用者名稱
   
############################ 使用說明 選單 最新油價############################
    if message_text == '@使用說明':
        about_us_event(event)
        Usage(event)

    if event.message.text == "想知道油價":
        content = oil_price()
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=content))
    if message_text == '使用說123':
        about_us_event(event)
        Usage(event)

        
############################ 使用說明 選單 股票看板 ############################
    if event.message.text == "股價查詢":
        line_bot_api.push_message(uid, TextSendMessage("請輸入#加股票代號...."))
    
    #股價查詢
    if re.match("想知道股價", msg):
        stockNumber = msg[5:]
        # = msg[5:]
        btn_msg = stock_reply_other(stockNumber)
        line_bot_api.push_message(uid, btn_msg)
        return 0
    
    #新增使用者關注的股票到mongodb
    if re.match('關注[0-9]{4}[<>][0-9]', msg): #使用者新增股票至股票清單
        stockNumber = msg[2:]
        line_bot_api.push_message(uid, TextSendMessage("加入股票代號"+stockNumber))
        content = write_my_stock(uid, user_name, stockNumber, msg[6:7], msg[7:])
        line_bot_api.push_message(uid, TextSendMessage(content))
        return 0
    

    #查詢股票篩選條件清單
    if re.match('股票清單', msg):
        line_bot_api.push_message(uid, TextSendMessage('稍等一下,股票查詢中...'))
        content = show_stock_setting(user_name, uid)
        line_bot_api.push_message(uid, TextSendMessage(content))
        return 0    #可以不用寫這行
    
    #刪除存在資料庫裏面的股票
    if re.match('刪除[0-9]{4}', msg):
        content = delete_my_stock(user_name, msg[2:])
        line_bot_api.push_message(uid, TextSendMessage(Content))
        return 0
    
    #清空存在資料庫裏面的股票
    if re.match('清空股票', msg):
        content = delete_my_allstock(user_name, uid)
        line_bot_api.push_message(uid, TextSendMessage(Content))
        return 0
    
    # else:
    #     content = write_my_stock(uid, user_name, stockNumber, "未設定", "未設定")
    #     line_bot_api.push_message(uid, TextSendMessage(content))
    #     return 0

    if(emsg.startswith('#')):
            text = emsg[1:]
            content = ''

            stock_rt = twstock.realtime.get(text)
            my_datetime = datetime.datetime.fromtimestamp(stock_rt['timestamp']+8*60*60)
            my_time = my_datetime.strftime('%H:%M:%S')

            content += '%s (%s) %s\n' %(
                stock_rt['info']['name'],
                stock_rt['info']['code'],
                my_time)
            content += '現價: %s / 開盤: %s\n'%(
                stock_rt['realtime']['latest_trade_price'],
                stock_rt['realtime']['open'])
            content += '最高: %s / 最低: %s\n' %(
                stock_rt['realtime']['high'],
                stock_rt['realtime']['low'])
            content += '量: %s\n' %(stock_rt['realtime']['accumulate_trade_volume'])

            stock = twstock.Stock(text) #twstock.Stock('2330')
            content += '----\n'
            content += '最近五日價格: \n'
            price5 = stock.price[-5:][::-1]
            date5 = stock.date[-5:][::-1]
            for i in range(len(price5)):
                #content += '[%s] %s\n' %(date5[i].strftime("%Y-%m-%d %H:%M:%S"), price5[i])
                content += '[%s] %s\n' %(date5[i].strftime("%Y-%m-%d"), price5[i])

            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=content)
            )
############################ 匯率區 ############################
    if re.match('幣別種類', emsg):
        message = show_Button()
        line_bot_api.reply_message(event.reply_token, message)

    if re.match('[A-Z]{3}', msg):  #if re.match('查詢匯率[A-Z]{3}', msg):
        msg = msg[::]               #msg = msg[4:]
        content = showCurrency(msg)
        line_bot_api.push_message(uid, TextSendMessage(content))

    if re.match("換匯[A-Z]{3}/[A-Z{3}]",msg):
        line_bot_api.push_message(uid,TextSendMessage("將為您做外匯計算...."))
        content = getExchangeRate(msg)
        line_bot_api.push_message(uid, TextSendMessage(content))

############################ 股價提醒 ############################
    if re.match("股價提醒", msg):
            line_bot_api.push_message(uid, TextSendMessage("請稍等..."))
            import schedule
            import time
            #查看當前股價
            def look_stock_price(stock, condition, price, userID):
                print(userID)
                url = "https://tw.stock.yahoo.com/q/q?s=" + stock
                list_req = requests.get(url)
                soup = BeautifulSoup(list_req.content, "html.parser")
                getstock = soup.findAll('span')[11].text
                content = stock + "當前股市價格為:" + getstock
                if condition == '<':
                    content += "\n篩選條件為: <" + price
                    if float(getstock) < float(price):
                        content += "\n符合" + getstock + "<" + price + "的篩選條件"
                        line_bot_api.push_message(userID, TextSendMessage(text = content))
                elif condition == '>':
                    content += "\n篩選條件為: >" + price
                    if float(getstock) > float(price):
                        content += "\n符合" + getstock + ">" + price + "的篩選條件"
                        line_bot_api.push_message(userID, TextSendMessage(text = content))
                elif condition == '<':
                    content += "\n篩選條件為: =" + price
                    if float(getstock) == float(price):
                        content += "\n符合" + getstock + "=" + price + "的篩選條件"
                        line_bot_api.push_message(userID, TextSendMessage(text = content))
            def job():
                print('HH')
                line_bot_api.push_message(uid, TextSendMessage("問就是直接ALL IN"))
                dataList = cache_users_stock()
                for i in range(len(dataList)):
                    for k in range(len(dataList[i])):
                        look_stock_price(dataList[i][k]['favorite_stock'], dataList[i][k]['condition'], dataList[i][k]['price'], dataList[i][k]['userID'])
            schedule.every(5).seconds.do(job).tag('daily-tasks-stock' + uid, "second")
        
            while True:
                schedule.run_pending()
                time.sleep(1)
##########################################
    # if re.match("關閉提醒", msg):
    #     import schedule
    #     schedule.clear()
    # if re.match("股價提醒", msg):
    #     import  schedule
    #     import time
        
    #     #查看當前股價
    #     def look_stock_price(stock, condition, price, userID):
    #         print(userID)
    #         url = 'https://tw.stock.yahoo.com/q/q?s=' + stock
    #         list_req = requests.get(url)
    #         soup = BeautifulSoup(list_req.content, "html.parser")
    #         getstock = soup.findAll('span')[11].text
    #         content = stock +"當前股市價為: " +getstock
    #         if condition == '<':
    #             content += "\n篩選條件為: <" + price
    #             if float(getstock) < float(price):
    #                 content += "\n符合" + getstock +"<" + price + "的篩選條件"
    #                 line_bot_api.push_message(userID, TextSendMessage(text=content))
    #         elif condition == '>':
    #             content += "\n篩選條件為: >" + price
    #             if float(getstock) > float(price):
    #                 content += "\n符合" + getstock +">" + price + "的篩選條件"
    #                 line_bot_api.push_message(userID, TextSendMessage(text=content))
    #         elif condition == '=':
    #             content += "\n篩選條件為: =" + price
    #             if float(getstock) == float(price):
    #                 content += "\n符合" + getstock +"=" + price + "的篩選條件"
    #                 line_bot_api.push_message(userID, TextSendMessage(text=content))
    # def job():
    #     print('HH')
    #     line_bot_api.push_message(uid, TextSendMessage("快買股票喔!"))
    #     dataList = cache_users_stock()
    #     #print(dataList)
    #     for i in range(len(dataList)):
    #         for k in range(len(dataList[i])):
    #             #print(dataList[i][k])
    #             look_stock_price(dataList[i][k]['favorite_stock'], dataList[i][k]['condition'], dataList[i][k]['price'], dataList[i][k]['userID'])
    # schedule.every(30).seconds.do(job).tag('daily-task-stock'+uid, 'second') #每30秒執行一次
    #schedule.every().hour.do(job) #每小時執行一次
    #schedule.every().day.at("17:19").do(job) #每天9點30執行一次
    #schedule.every().monday.do(job) #每周執行一次
    #schedule.every().wednesday.at("14:45").do(job) #每周三14點45執行一次
    #無窮迴圈
    # while True:
    #     schedule.run_pending()
    #     time.sleep(1)
############################ 粉絲/封鎖 訊息狀態 ############################

@handler.add(FollowEvent)
def handle_follow(event):
    welcome_msg = """Hello! 您好，歡迎您成為Master Finance的好友!

我是Master財經小幫手

-這裡有股票、匯率資訊唷~
-直接點選下方【圖中】選單功能

-期待您的光臨!"""

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=welcome_msg))
    
@handler.add(UnfollowEvent)
def handle_unfollow(event):
    print(event)

#     message = TextSendMessage(text=event.message.text)
#     line_bot_api.reply_message(event.reply_token, message) #回覆你輸入的訊息(重複你說的話)

if __name__ =="__main__":
    app.run()



