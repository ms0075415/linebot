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