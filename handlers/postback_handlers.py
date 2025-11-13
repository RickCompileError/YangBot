from datetime import datetime
from urllib.parse import parse_qs

import pytz
from linebot.v3.messaging import (ApiClient, MessagingApi, ReplyMessageRequest,
                                  TextMessage)

from database.task_operations import get_task, update_task
from handlers.message_handlers import reply_task_created_message


def handle_set_task_datetime_postback(event, line_bot_configuration, app):
    """
    Handle postback event to set datetime for a task.

    Parses the postback data to extract task ID and selected datetime,
    then updates the Task document in Firestore.

    :param event: PostbackEvent object
    :param line_bot_configuration: LINE bot configuration
    :param app: Flask app instance
    :return: 'OK' if successful
    """
    try:
        # Parse postback data (expected format: taskId=<id>)
        params = parse_qs(event.postback.data)
        if 'taskId' not in params:
            raise ValueError("Missing taskId or datetime in postback data")

        task_id = params['taskId'][0]

        # Convert string to datetime object with utc+8
        utc_8 = pytz.timezone('Asia/Taipei')
        selected_datetime = datetime.fromisoformat(event.postback.params['datetime']).astimezone(utc_8)

        # Update the task in Firestore
        updates = {"expireDate": selected_datetime}
        success = update_task(task_id, updates)
        message = get_task(task_id)['message']

        reply_task_created_message(event, get_task(task_id), line_bot_configuration)

        if success:
            # Mandarin reply
            reply_text = f"任務 [{message}] 的到期時間已設定為 {selected_datetime.strftime('%Y-%m-%d %H:%M')}。"
        else:
            reply_text = "設定提醒時間失敗，請稍後再試。"

    except Exception as e:
        app.logger.error(f"Error handling set task datetime postback: {e}")
        reply_text = "設定提醒時間時發生錯誤，請稍後再試。"

    return 'OK'
