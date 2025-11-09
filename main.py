import os
from datetime import datetime

from flask import Flask, abort, request
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import Configuration
from linebot.v3.webhooks import MessageEvent, PostbackEvent, TextMessageContent

# Initialize Firestore
from database.task_operations import create_task
from handlers.message_handlers import handle_tag_bot_message
from handlers.postback_handlers import handle_set_task_datetime_postback

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
    # Check if the bot is mentioned
    if event.message.mention != None and event.message.mention.mentionees[0].is_self:
        # split by empty space and trim each text
        split_text = [text.strip() for text in event.message.text.split(' ') if text.strip() != '']
        app.logger.info("split_text: " + str(split_text))
        return handle_tag_bot_message(event, split_text, line_bot_configuration, app)
    else:
        app.logger.info("Not tag bot, repeat message")

@handler.add(PostbackEvent)
def handle_postback(event):
    if event.postback.data.startswith("taskId="):
        return handle_set_task_datetime_postback(event, line_bot_configuration, app)

# Hello World entry point
@app.route("/")
def hello():
    return "Hello, World!"

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8080))
    app.run(debug=True, host='0.0.0.0', port=port)
