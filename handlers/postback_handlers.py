from urllib.parse import parse_qs

from linebot.v3.messaging import TextMessage

from database.task_operations import get_task, update_task
from handlers.message_handlers import (build_notify_datetime_picker_message,
                                       build_task_created_message,
                                       build_task_updated_message,
                                       reply_message)
from utils.timer import is_earlier_than_now, to_utc_datetime


def handle_expire_date_postback(event, line_bot_configuration, app):
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
        # Parse postback data (expected format: taskId=<id>&action=expireDate)
        params = parse_qs(event.postback.data)
        if 'taskId' not in params or 'action' not in params:
            raise ValueError("Missing taskId or datetime in postback data")

        task_id = params['taskId'][0]
        expire_date = event.postback.params['datetime']
        utc_expire_date = to_utc_datetime(expire_date)

        # Validate that expire_date is not earlier than now
        if is_earlier_than_now(utc_expire_date):
            reply_text = "設定的到期時間不能早於現在時間，請重新選擇。"
            reply_message(line_bot_configuration, event.reply_token, [TextMessage(text=reply_text)])
            return 'OK'

        # Update the task in Firestore
        updates = {"expireDate": utc_expire_date, "notifyDate": utc_expire_date}
        update_task(task_id, updates)
        task = get_task(task_id)

        notify_datetime_picker_message = build_notify_datetime_picker_message(event.timestamp, expire_date, task_id)
        task_created_message = build_task_created_message(task)
        reply_message(line_bot_configuration, event.reply_token, [notify_datetime_picker_message, task_created_message])

    except Exception as e:
        app.logger.error(f"Error handling set task datetime postback: {e}")

    return 'OK'

def handle_notify_date_postback(event, line_bot_configuration, app):
    """
    Handle postback event to set notify datetime for a task.

    Parses the postback data to extract task ID and selected datetime,
    then updates the Task document in Firestore.

    :param event: PostbackEvent object
    :param line_bot_configuration: LINE bot configuration
    :param app: Flask app instance
    :return: 'OK' if successful
    """
    try:
        # Parse postback data (expected format: taskId=<id>&action=notifyDate)
        params = parse_qs(event.postback.data)
        if 'taskId' not in params or 'action' not in params:
            raise ValueError("Missing taskId or datetime in postback data")

        task_id = params['taskId'][0]
        notify_date = event.postback.params['datetime']
        utc_notify_date = to_utc_datetime(notify_date)
        task = get_task(task_id)

        # Validate that notify_date is not earlier than now
        if is_earlier_than_now(utc_notify_date):
            reply_text = "設定的提醒時間不能早於現在時間，請重新選擇。"
            reply_message(line_bot_configuration, event.reply_token, [TextMessage(text=reply_text)])
            return 'OK'

        # Validate that notify_date is not later than expire_date
        if utc_notify_date > task['expireDate']:
            reply_text = "設定的提醒時間不能晚於到期時間，請重新選擇。"
            reply_message(line_bot_configuration, event.reply_token, [TextMessage(text=reply_text)])
            return 'OK'

        # Update the task in Firestore
        updates = {"notifyDate": utc_notify_date}
        update_task(task_id, updates)
        task = get_task(task_id)

        task_update_message = build_task_updated_message(task)
        reply_message(line_bot_configuration, event.reply_token, [task_update_message])

    except Exception as e:
        app.logger.error(f"Error handling set task notify datetime postback: {e}")

    return 'OK'
