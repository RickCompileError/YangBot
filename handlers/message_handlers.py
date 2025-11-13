from datetime import datetime

from linebot.v3.messaging import (ApiClient, ButtonsTemplate,
                                  DatetimePickerAction, MessagingApi,
                                  PushMessageRequest, ReplyMessageRequest,
                                  TemplateMessage, TextMessage)

from database.task_operations import create_task


def reply_message(event, text, line_bot_configuration, app):
    with ApiClient(configuration=line_bot_configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_api.reply_message_with_http_info(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=text)]
            )
        )

    app.logger.info("Reply message: " + text)

    return 'OK'

def reply_introduction_message(event, line_bot_configuration, app):
    introduction_text = (
        "你好！我是家庭小幫手 YangBot 🤖。\n"
        "你可以在群組或聊天室中標註我，並使用以下指令來設定提醒：\n"
        "@YangBot 提醒 <你的提醒事項>\n"
        "例如：@YangBot 提醒 買牛奶\n"
        "我會幫你設定一個提醒，並讓你選擇提醒的日期和時間。"
    )
    return reply_message(event, introduction_text, line_bot_configuration, app)

def reply_datetime_picker_action_message(event, data, message, line_bot_configuration, app):
    with ApiClient(configuration=line_bot_configuration) as api_client:
        datetime_picker_action = DatetimePickerAction(label="選擇日期和時間", data=data, mode="datetime", initial=datetime.now().strftime('%Y-%m-%dT%H:%M'))
        line_bot_api = MessagingApi(api_client)
        line_bot_api.reply_message_with_http_info(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                # set initial date depend on the system time
                messages=[TemplateMessage(alt_text="設定到期日", template=ButtonsTemplate(title="設定到期日", text=message, actions=[datetime_picker_action]))]
            )
        )
    app.logger.info("Replied datetime picker message for " + data)

    return 'OK'

def handle_tag_bot_message(event, split_text, line_bot_configuration, app):
    if len(split_text) == 0:
        return reply_introduction_message(event, line_bot_configuration, app)
    
    # Handle "提醒" command, Ex. @botname 提醒 買牛奶
    if split_text[1] == "提醒" and len(split_text) >= 3:
        message = ' '.join(split_text[2:])
        user_id = event.source.user_id
        room_id = get_group_or_room_id(event.source)
        task_id = create_task(message, user_id, room_id, False, None)
        data = "taskId=" + task_id
        return reply_datetime_picker_action_message(event, data, message, line_bot_configuration, app)

def get_group_or_room_id(source):
    if source.type == "group":
        return source.group_id
    elif source.type == "room":
        return source.room_id
    return None

def send_notification_push_message(to, message, line_bot_configuration, app):
    with ApiClient(configuration=line_bot_configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_api.push_message_with_http_info(
            PushMessageRequest(
                to=to,
                messages=[TextMessage(text=message)]
            )
        )
    app.logger.info("Sent notification push message to " + to)

    return 'OK'
