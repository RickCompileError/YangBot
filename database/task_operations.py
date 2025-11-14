from datetime import datetime, timedelta

import pytz
from google.cloud import firestore

from .firestore_init import db
from .firestore_operations import (delete_data, query_data, read_data,
                                   update_data, write_data)

COLLECTION_NAME = "Task"

def create_task(message, source_id, notified_id, is_notified, expire_date):
    """
    Create a new Task document in Firestore.

    :param message: Task message/content
    :param source_id: Source identifier
    :param notified_id: Notification identifier
    :param is_notified: Boolean indicating if notification is enabled
    :param expire_date: Expiration date (datetime object only)
    :return: Created Task document ID
    """
    try:
        data = {
            "message": message,
            "sourceId": source_id,
            "notifiedId": notified_id,
            "isNotified": is_notified,
            "expireDate": expire_date
        }
        return write_data(COLLECTION_NAME, None, data)
    except Exception as e:
        print(f"Error creating task: {e}")
        return None


def get_task(task_id):
    """
    Retrieve a Task document by ID.

    :param task_id: Task ID (document ID)
    :return: Task data dictionary or None if not found
    """
    return read_data(COLLECTION_NAME, task_id)

def update_task(task_id, updates):
    """
    Update a Task document with given updates.

    :param task_id: Task ID (document ID)
    :param updates: Dictionary of fields to update
    :return: True if successful, False otherwise
    """
    try:
        # Validate that updates only include valid fields
        valid_fields = {"message", "sourceId", "notifiedId", "isNotified", "expireDate"}
        filtered_updates = {k: v for k, v in updates.items() if k in valid_fields}

        if not filtered_updates:
            print("No valid fields to update")
            return False

        update_data(COLLECTION_NAME, task_id, filtered_updates)
        return True
    except Exception as e:
        print(f"Error updating task: {e}")
        return False

def delete_task(task_id):
    """
    Delete a Task document by ID.

    :param task_id: Task ID (document ID)
    :return: True if successful, False otherwise
    """
    try:
        delete_data(COLLECTION_NAME, task_id)
        return True
    except Exception as e:
        print(f"Error deleting task: {e}")
        return False

def get_tasks_by_is_notified(is_notified):
    """
    Retrieve tasks filtered by isNotified status.

    :param is_notified: Boolean value to filter by
    :return: List of task dictionaries
    """
    return query_data(COLLECTION_NAME, "isNotified", "==", is_notified)

def get_tasks_by_source_id(source_id):
    """
    Retrieve tasks filtered by sourceId.

    :param source_id: Source ID to filter by
    :return: List of task dictionaries
    """
    return query_data(COLLECTION_NAME, "sourceId", "==", source_id)

def get_notify_tasks():
    """
    Retrieve tasks that need notification (expireDate within next day and isNotified is False).
    The timestamp range is from (now + 1 day - 1 minute) to (now + 1 day).

    :return: List of task dictionaries
    """
    one_day_from_now = datetime.now() + timedelta(days=1)
    one_day_minus_one_minute = one_day_from_now - timedelta(minutes=1)

    tasks_ref = db.collection(COLLECTION_NAME)
    results = tasks_ref.where(
        filter=firestore.FieldFilter("expireDate", ">=", one_day_minus_one_minute)
    ).where(
        filter=firestore.FieldFilter("expireDate", "<", one_day_from_now)
    ).where(
        filter=firestore.FieldFilter("isNotified", "==", False)
    ).stream()

    docs = []
    for doc in results:
        docs.append({**doc.to_dict(), 'id': doc.id})

    return docs
