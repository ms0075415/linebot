from line_bot_api import *

def about_us_event(event):

    emoji = [
            {
                "index":0,
                "productId":"5ac1bfd5040ab15980c9b435",
                "emojiID":"082"
            },
            {
                "index":17,
                "productId":"5ac1bfd5040ab15980c9b435",
                "emojiID":"082"
            }
        ]
    text_message = TextSendMessage(text='''$ Master Finance $
Hello! 您好，歡迎您成為 Master Finance的好友!

我是Master財經小幫手

-這裡有股票，匯率資訊喔~
-直接點選下方【圖中】選單功能  

-期待您的光臨!''', emojis=emoji)

    sticker_message = StickerSendMessage(
        package_id='11537',
        sticker_id='52002738'
    )
    line_bot_api.reply_message(
        event.reply_token,
        [text_message, sticker_message])
