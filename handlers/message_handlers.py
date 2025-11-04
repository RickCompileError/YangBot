from datetime import datetime

from linebot.v3.messaging import (ApiClient, ButtonsTemplate, Configuration,
                                  DatetimePickerAction, MessageAction,
                                  MessagingApi, ReplyMessageRequest,
                                  TemplateMessage, TextMessage)


def reply_greeting_message(event, line_bot_configuration, app):
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

def reply_message_action_message(event, line_bot_configuration, app):
    with ApiClient(configuration=line_bot_configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_api.reply_message_with_http_info(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                # set initial date depend on the system time
                messages=[TemplateMessage(alt_text="輸入提醒事項", template=ButtonsTemplate(title="提醒輸入", text="請輸入提醒", actions=[message_action]))]
            )
        )

    app.logger.info("Replied message: 好的，請選擇日期和時間")

    return 'OK'

def reply_datetime_picker_action_message(event, line_bot_configuration, app):
    with ApiClient(configuration=line_bot_configuration) as api_client:
        message_action = MessageAction(text="點我選日期", label="選日期")
        datetime_picker_action = DatetimePickerAction(label="選擇日期和時間", data="action=select_datetime", mode="datetime", initial=datetime.now().strftime('%Y-%m-%dT%H:%M'))
        line_bot_api = MessagingApi(api_client)
        line_bot_api.reply_message_with_http_info(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                # set initial date depend on the system time
                messages=[TemplateMessage(alt_text="設定到期日", template=ButtonsTemplate(title="提醒設定", text="請選擇日期和時間", actions=[datetime_picker_action, message_action]))]
            )
        )

    app.logger.info("Replied message: 好的，請選擇日期和時間")

    return 'OK'


def reply_repeat_message(event, line_bot_configuration, app):
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


def handle_tag_bot_message(event, split_text, line_bot_configuration, app):
    if len(split_text) == 1:
        return reply_greeting_message(event, line_bot_configuration, app)

    if split_text[1] == "提醒":
        return reply_datetime_picker_action_message(event, line_bot_configuration, app)
