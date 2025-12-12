import json
from re import split

from linebot.v3.messaging import (ApiClient, ButtonsTemplate, Configuration,
                                  DatetimePickerAction, FlexContainer,
                                  FlexMessage, Message, MessagingApi,
                                  PushMessageRequest, ReplyMessageRequest,
                                  TemplateMessage, TextMessage)

from database.army_operations import (get_all_armies, get_army_by_user_id,
                                      reset_state, set_state)
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

    # Handle "設定狀態" command, Ex. @botname 設定狀態 公司 工作
    if split_text[1] == "設定狀態" and len(split_text) >= 3:
        army = get_army_by_user_id(event.source.user_id)
        set_state(army[0]['id'], *split_text[2:])
        confirmation_text = f"已更新大兵 {army[0]['name']} 的狀態"
        confirmation_message = TextMessage(text=confirmation_text)
        return reply_message(line_bot_configuration, event.reply_token, [confirmation_message])

    # Handle "放假" command, Ex. @botname 放假
    if split_text[1] == "放假":
        army = get_army_by_user_id(event.source.user_id)
        vacation_message = build_vacation_message(army[0])
        return reply_message(line_bot_configuration, event.reply_token, [vacation_message])

    # Handle "收假" command, Ex. @botname 收假
    if split_text[1] == "收假":
        army = get_army_by_user_id(event.source.user_id)
        return_message = build_return_army_message(army[0])
        return reply_message(line_bot_configuration, event.reply_token, [return_message])

    if split_text[1] == "重置回報":
        armies = get_all_armies()
        for army in armies:
            reset_state(army['id'])
        confirmation_text = "已重置所有人的狀態回報為預設值。"
        confirmation_message = TextMessage(text=confirmation_text)
        return reply_message(line_bot_configuration, event.reply_token, [confirmation_message])

    if split_text[1] == "放假總結":
        try:
            report_time = 18 if len(split_text) < 3 else int(split_text[2])
        except ValueError:
            reply_text = "設定的回報時間只能是數字。"
            reply_message(line_bot_configuration, event.reply_token, [TextMessage(text=reply_text)])
        armies = get_all_armies()
        messages = []
        for army in armies:
            messages.append(build_vacation_message(army, report_time).text)
        summary_text = "第十班：\n\n" + "\n\n".join(messages)
        summary_message = TextMessage(text=summary_text)
        return reply_message(line_bot_configuration, event.reply_token, [summary_message])
    
    if split_text[1] == "收假總結":
        try:
            report_time = 11 if len(split_text) < 3 else int(split_text[2])
        except ValueError:
            reply_text = "設定的回報時間只能是數字。"
            reply_message(line_bot_configuration, event.reply_token, [TextMessage(text=reply_text)])
        armies = get_all_armies()
        messages = []
        for army in armies:
            messages.append(build_return_army_message(army, report_time).text)
        summary_text = "第十班：\n\n" + "\n\n".join(messages)
        summary_message = TextMessage(text=summary_text)
        return reply_message(line_bot_configuration, event.reply_token, [summary_message])

    if split_text[1] == "大兵登記":
        user_id_message = TextMessage(text=f"你的用戶ID是: {event.source.user_id}，請將此ID提供給管理員進行大兵資料登記。")
        return reply_message(line_bot_configuration, event.reply_token, [user_id_message])
    

def get_group_or_room_id(source):
    if source.type == "group":
        return source.group_id
    elif source.type == "room":
        return source.room_id
    return None

def reply_introduction_message(event, line_bot_configuration, app):
    # introduction_text = (
    #     "你好！我是家庭小幫手 YangBot 🤖。\n"
    #     "你可以在群組或聊天室中標註我，並使用以下指令來設定提醒：\n"
    #     "@YangBot 提醒 <你的提醒事項>\n"
    #     "例如：@YangBot 提醒 買牛奶\n"
    #     "我會幫你設定一個提醒，並讓你選擇提醒的日期和時間。"
    # )
    introduction_text = """📌 LINE Bot 功能總覽

🔸@YangBot 提醒 <事項>：建立提醒並在時間到時通知

🔸@YangBot 設定狀態 <地點> <做什麼> <返營方式> <預計抵達時間>
👉 四個欄位為固定順序，需依序填寫，沒填滿則套用預設值

🔸@YangBot 放假：顯示大兵放假資訊

🔸@YangBot 收假：顯示大兵收假資訊

🔸@YangBot 放假總結 <回報時間>：查看全體放假狀態，可輸入數字調整回報時間

🔸@YangBot 收假總結 <回報時間>：查看全體收假狀態，可輸入數字調整回報時間

🔸@YangBot 重置回報：重置所有大兵收放假資料

🔸@YangBot 大兵登記：管理員提供 ID 建立大兵資料"""

    return reply_message(line_bot_configuration, event.reply_token, [TextMessage(text=introduction_text)])

def build_vacation_message(army, time = 18) -> TextMessage:
    vacation_text = f"""放假日回報（{time}00-{time + 1}00）
{army['Id']} {army['name']}
地點：{army['place']}
做什麼：{army['action']}
有無飲酒：無
自己電話：{army['phone']}"""
    return TextMessage(text=vacation_text)

def build_return_army_message(army, time = 11) -> TextMessage:
    return_text = f"""收假日回報（{time}00-{time + 1}00）
{army['Id']} {army['name']}
地點：{army['place']}
做什麼：{army['action']}
有無飲酒：無
自己電話：{army['phone']}
返營方式：{army['returnMethod']}
預計返營(抵達)時間：{army['returnTime']}"""
    return TextMessage(text=return_text)

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
