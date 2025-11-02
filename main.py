import os

from flask import Flask, abort, request
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (ApiClient, Configuration, MessagingApi,
                                  ReplyMessageRequest, TextMessage)
from linebot.v3.webhooks import MessageEvent, TextMessageContent

app = Flask(__name__)
app.logger.setLevel(os.getenv('LOG_LEVEL', 'INFO').upper())

# your channel access token
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', '6wz47KLG3CbbEFRoj6/sOyt7zlSoyPMmFLgv0pTInBumDdcghwm8+DifFykaj4u2ZufP21x7wMfrb6ASoj//lI9zyA1R04olsOPmkNlN4I2ue88DWgRvGaoreg9ZbYmUtE40ike7iMQQzsBB5J9rtQdB04t89/1O/w1cDnyilFU=')
# your channel secret key
channel_secret = os.getenv('LINE_CHANNEL_SECRET', '3aa09f4c3f60bf08489f8cae16896a4d')

line_bot_configuration = Configuration(access_token=channel_access_token)
handler = WebhookHandler(channel_secret)

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

@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    if event.message.mention != None and event.message.mention.mentionees[0].is_self:
        # split by empty space and trim each text
        split_text = [text.strip() for text in event.message.text.split(' ') if text.strip() != '']
        app.logger.info("split_text: " + str(split_text))
        return reply_greeting_message(event)
    else:
        app.logger.info("Not tag bot, repeat message")
        return reply_repeat_message(event)
        
def reply_greeting_message(event):
    with ApiClient(configuration=line_bot_configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_api.reply_message_with_http_info(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text="閉嘴")]
            )
        )

    app.logger.info("Replied message: 閉嘴")

    return 'OK'

def reply_repeat_message(event):
    with ApiClient(configuration=line_bot_configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_api.reply_message_with_http_info(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=event.message.text)]
            )
        )

    app.logger.info("Replied message: " + event.message.text)

    return 'OK'

# Hello World entry point
@app.route("/")
def hello():
    return "Hello, World!"

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8080))
    app.run(debug=True, host='0.0.0.0', port=port)
