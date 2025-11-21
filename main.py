from flask import Flask, abort, request
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import Configuration
from linebot.v3.webhooks import MessageEvent, PostbackEvent, TextMessageContent

from database.task_operations import get_notify_tasks, update_task
from handlers.message_handlers import (build_notification_message,
                                       handle_tag_bot_message, push_message)
from handlers.postback_handlers import (handle_expire_date_postback,
                                        handle_notify_date_postback)
from utils.config import get_settings

app = Flask(__name__)
settings = get_settings()

app.logger.setLevel(settings.log_level.upper())

line_bot_configuration = Configuration(access_token=settings.line_channel_access_token)
handler = WebhookHandler(settings.line_channel_secret)

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
    postback_data: str = event.postback.data

    if postback_data.startswith("taskId=") and 'expireDate' in postback_data:
        return handle_expire_date_postback(event, line_bot_configuration, app)

    if postback_data.startswith("taskId=") and 'notifyDate' in postback_data:
        return handle_notify_date_postback(event, line_bot_configuration, app)

@app.route("/notify_check", methods=['GET'])
def notify_check():
    """Endpoint to manually trigger task notification check."""
    tasks = get_notify_tasks()

    if len(tasks) == 0:
        return 'No tasks to notify.'

    for task in tasks:
        notification_message = build_notification_message(task)
        state = push_message(
            line_bot_configuration=line_bot_configuration,
            to=task['notifiedId'],
            messages=[notification_message]
        )
        if state == 'OK':
            update_task(task['id'], {'isNotified': True})

    return 'OK'

# Hello World entry point
@app.route("/")
def hello():
    return "Hello, World!"

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=settings.port)
