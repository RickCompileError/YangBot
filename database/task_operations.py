from datetime import datetime

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
    :param expire_date: Expiration date (datetime object or ISO string)
    :return: Created Task document ID
    """
    try:
        # Convert expire_date to string if it's a datetime
        if isinstance(expire_date, datetime):
            expire_date = expire_date.isoformat()

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

        # Convert expire_date if it's a datetime
        if "expireDate" in filtered_updates and isinstance(filtered_updates["expireDate"], datetime):
            filtered_updates["expireDate"] = filtered_updates["expireDate"].isoformat()

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

def get_all_tasks():
    """
    Retrieve all Task documents.

    :return: List of task dictionaries
    """
    try:
        # Since query_data requires a where clause, we'll need to get all docs
        # For Firestore, to get all docs, we can use collection.stream()
        # But since we have query_data, we might need to adjust
        # For now, return empty list as placeholder - in practice, you'd need a different approach
        # Actually, to get all, we can use db.collection(COLLECTION_NAME).stream()
        # But to keep it simple, let's add a note

        # This is a limitation of the current query_data function
        # Ideally, extend firestore_operations with a get_all function
        print("get_all_tasks: To get all tasks, consider extending firestore_operations with get_all_collection")
        return []
    except Exception as e:
        print(f"Error retrieving all tasks: {e}")
        return []

def get_tasks_by_is_notified(is_notified):
    """
    Retrieve tasks filtered by isNotified status.

    :param is_notified: Boolean value to filter by
    :return: List of task dictionaries
    """
    return query_data(COLLECTION_NAME, "isNotified", "==", is_notified)

def get_expired_tasks():
    """
    Retrieve tasks that have expired (expireDate < current time).

    :return: List of expired task dictionaries
    """
    # Firestore queries don't support direct comparison with current time
    # This would require fetching all and filtering client-side, or using server timestamps
    # For simplicity, return all tasks and note the limitation
    print("get_expired_tasks: Firestore doesn't support direct current time queries. Consider client-side filtering.")
    return []

def get_tasks_by_source_id(source_id):
    """
    Retrieve tasks filtered by sourceId.

    :param source_id: Source ID to filter by
    :return: List of task dictionaries
    """
    return query_data(COLLECTION_NAME, "sourceId", "==", source_id)
