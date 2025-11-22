import json

from linebot.v3.messaging import (ApiClient, ButtonsTemplate, Configuration,
                                  DatetimePickerAction, FlexContainer,
                                  FlexMessage, Message, MessagingApi,
                                  PushMessageRequest, ReplyMessageRequest,
                                  TemplateMessage, TextMessage)

from database.task_operations import create_task
from utils.timer import get_line_datetime_string_format, to_local_datetime


def handle_tag_bot_message(event, split_text, line_bot_configuration, app):
    if len(split_text) == 1:
        return reply_introduction_message(event, line_bot_configuration, app)
    
    # Handle "提醒" command, Ex. @botname 提醒 買牛奶
    if len(split_text) >= 3 and split_text[1] == "提醒":
        message = ' '.join(split_text[2:])
        user_id = event.source.user_id
        room_id = get_group_or_room_id(event.source)
        task_id = create_task(message, user_id, room_id, False, None)
        expire_datetime_picker_message = build_expire_datetime_picker_message(event.timestamp, task_id)
        return reply_message(line_bot_configuration, event.reply_token, [expire_datetime_picker_message])

def get_group_or_room_id(source):
    if source.type == "group":
        return source.group_id
    elif source.type == "room":
        return source.room_id
    return None

def reply_introduction_message(event, line_bot_configuration, app):
    introduction_text = (
        "你好！我是家庭小幫手 YangBot 🤖。\n"
        "你可以在群組或聊天室中標註我，並使用以下指令來設定提醒：\n"
        "@YangBot 提醒 <你的提醒事項>\n"
        "例如：@YangBot 提醒 買牛奶\n"
        "我會幫你設定一個提醒，並讓你選擇提醒的日期和時間。"
    )

    return reply_message(line_bot_configuration, event.reply_token, [TextMessage(text=introduction_text)])

def build_expire_datetime_picker_message(timestamp: float, task_id: str) -> TemplateMessage:
    current_time = get_line_datetime_string_format(timestamp)
    datetime_picker_action = DatetimePickerAction(label="選擇日期和時間", data=f"taskId={task_id}&action=expireDate", mode="datetime", initial=current_time, min=current_time)

    template_message = TemplateMessage(
        alt_text="設定到期日",
        template=ButtonsTemplate(
            title="設定到期日",
            text="請選擇任務的到期日期和時間：",
            actions=[datetime_picker_action]
        )
    )

    return template_message

def build_notify_datetime_picker_message(timestamp: float, expire_date: str, task_id: str) -> TemplateMessage:
    current_time = get_line_datetime_string_format(timestamp)
    datetime_picker_action = DatetimePickerAction(label="選擇日期和時間", data=f"taskId={task_id}&action=notifyDate", mode="datetime", initial=current_time, min=current_time, max=expire_date)

    template_message = TemplateMessage(
        alt_text="設定提醒時間",
        template=ButtonsTemplate(
            title="設定提醒時間",
            text="請選擇任務的提醒日期和時間：",
            actions=[datetime_picker_action]
        )
    )

    return template_message

def build_task_created_message(task):
    flex_message_content = get_flex_message_content_template(task)
    flex_message_content["body"]["contents"][0]["text"] = '任務建立成功'
    return FlexMessage(
        alt_text="任務建立成功",
        contents = FlexContainer.from_dict(flex_message_content)
    )

def build_task_updated_message(task):
    flex_message_content = get_flex_message_content_template(task)
    flex_message_content["body"]["contents"][0]["text"] = '任務更新成功'
    return FlexMessage(
        alt_text="任務更新成功",
        contents = FlexContainer.from_dict(flex_message_content)
    )

def build_notification_message(task):
    flex_message_content = get_flex_message_content_template(task)
    flex_message_content["body"]["contents"][0]["text"] = '提醒'
    return FlexMessage(
        alt_text="任務即將到期通知",
        contents = FlexContainer.from_dict(flex_message_content)
    )

def get_flex_message_content_template(task):
    with open('handlers/task_created_flex_template.json', 'r', encoding='utf-8') as f:
        flex_message_content = json.load(f)
        flex_message_content["body"]["contents"][1]["text"] = task['message']
        flex_message_content["body"]["contents"][2]["text"] = f"{flex_message_content['body']['contents'][2]['text']}: {to_local_datetime(task['notifyDate']).strftime('%Y-%m-%d %H:%M')}" if task['notifyDate'] else "未設定"
        flex_message_content["body"]["contents"][3]["text"] = f"{flex_message_content['body']['contents'][3]['text']}: {to_local_datetime(task['expireDate']).strftime('%Y-%m-%d %H:%M')}" if task['expireDate'] else "未設定"
        flex_message_content["body"]["contents"][5]["contents"][1]["text"] = task['id']

    return flex_message_content

def reply_message(line_bot_configuration: Configuration, reply_token: str, messages: list[Message]):
    with ApiClient(configuration=line_bot_configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_api.reply_message_with_http_info(
            ReplyMessageRequest(
                reply_token=reply_token,
                messages=messages
            )
        )

    return 'OK'

def push_message(line_bot_configuration: Configuration, to: str, messages: list[Message]):
    with ApiClient(configuration=line_bot_configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_api.push_message_with_http_info(
            PushMessageRequest(
                to=to,
                messages=messages
            )
        )

    return 'OK'
