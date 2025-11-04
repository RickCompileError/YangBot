import threading
import time

import schedule


def schedule_task(func, time_param):
    """
    Schedule a task to run at specified intervals using the schedule library.
    Runs in a separate thread to avoid blocking the main thread.

    Args:
        func: The function to be scheduled.
        time_param: Time parameter for scheduling (e.g., 'every 5 minutes', 'daily at 8:00').
    """
    def run_scheduler():
        # Parse time_param to configure schedule
        if 'minutes' in time_param:
            minutes = int(time_param.split()[1])
            schedule.every(minutes).minutes.do(func)
        elif 'hours' in time_param:
            hours = int(time_param.split()[1])
            schedule.every(hours).hours.do(func)
        elif 'days' in time_param:
            days = int(time_param.split()[1])
            schedule.every(days).days.do(func)
        elif time_param == 'daily at 8:00':
            schedule.every().day.at("08:00").do(func)
        else:
            # Default to every hour if parsing fails
            schedule.every().hour.do(func)

        # Keep the scheduler running
        while True:
            schedule.run_pending()
            time.sleep(60)

    # Start the scheduler in a separate thread
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()
