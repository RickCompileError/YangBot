import threading
import time

import schedule
from flask import current_app as app
from linebot.v3.messaging import Configuration

from database.task_operations import get_notify_tasks, update_task
from handlers.message_handlers import send_notification_push_message
from utils.config import get_settings


def schedule_task():
    """
    Schedule a task to run at 60s intervals.
    Runs in a separate thread to avoid blocking the main thread.

    Args:
        func: The function to be scheduled.
    """
    def run_scheduler():
        # Keep the scheduler running
        while True:
            print("Running scheduled tasks...")
            schedule.run_pending()
            time.sleep(60)

    # Start the scheduler in a separate thread
    schedule.every(1).minute.do(check_and_notify_tasks)
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()
    print("Scheduler started.")

def check_and_notify_tasks():
    """
    Placeholder function to check tasks and send notifications.
    This function should be implemented to check for tasks that are due
    and send notifications accordingly.
    """
    tasks = get_notify_tasks()

    if len(tasks) == 0:
        return

    line_bot_configuration = Configuration(access_token=get_settings().line_channel_access_token)
    for task in tasks:
        state = send_notification_push_message(task['notifiedId'], task['message'], line_bot_configuration, app)
        if state == 'OK':
            update_task(task['id'], {'isNotified': True})
