#載入LineBot所需要的套件
from flask import Flask, request, abort
from linebot import(LineBotApi, WebhookHandler, exceptions)
from linebot.exceptions import (InvalidSignatureError)
from linebot.models import *

app = Flask(__name__)

#Channel access token #在line Developers的providers的Basic settings
line_bot_api = LineBotApi('cnaDYjmpA18litOws+4t7x/j/PJXiiZJhhrkkYokCf+V0MyQXbeANnpb4A3pwOsBXy5ZqU4MmkK0+RgWPcdMpUnU4vVvWxNUDxplTFmn22oTMXObi4SoM7VugLAnEhz4iLFad39QjB0IDUK8M+94pQdB04t89/1O/w1cDnyilFU=')

#Channel secret  #在line Developers的providers的Messaging API
handler = WebhookHandler('d5d1d84e419c4bcfa7d6a092a6de9339')

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
    message = TextSendMessage(text=event.message.text)
    line_bot_api.reply_message(event.reply_token, message)

if __name__ =="__main__":
    app.run()

