from .firestore_init import db
from .firestore_operations import query_data, update_data

COLLECTION_NAME = "Army"

def reset_state(army_id):
    """
    Reset the state of a specific army member to default values.
    
    This function resets an army member's activity state by updating their
    action, location, return method, and return time to default values.
    
    Args:
        army_id: The unique identifier of the army member whose state should be reset.
    
    Returns:
        bool: True if the state was successfully reset, False if an error occurred.
    
    Raises:
        Catches all exceptions and returns False, logging the error message.
    """
    try:
        updates = {
            "action": "休息",
            "place": "家裡",
            "returnMethod": "車子",
            "returnTime": "1800"
        }
        update_data(COLLECTION_NAME, army_id, updates)
        return True
    except Exception as e:
        print(f"Error resetting state for army {army_id}: {e}")
        return False

def set_state(army_id, *args):
    """
    Set the action and place for the given Army document.
    
    :param army_id: Army ID (document ID)
    :param args: action and place values
    """
    try:
        # unpack args, value corresponds to action, place, returnMethod, returnTime, if length not enough, use default values
        updates = {
            "place": args[0] if len(args) >= 1 else "家裡",
            "action": args[1] if len(args) >= 2 else "休息",
            "returnMethod": args[2] if len(args) >= 3 else "車子",
            "returnTime": args[3] if len(args) >= 4 else "18:00"
        }
        update_data(COLLECTION_NAME, army_id, updates)
        return True
    except Exception as e:
        print(f"Error setting state for army {army_id}: {e}")
        return False

def get_army_by_user_id(user_id):
    """
    Retrieve Army documents by user_id.

    :param user_id: User ID to filter by
    :return: List of army dictionaries matching the user_id
    """
    return query_data(COLLECTION_NAME, "userId", "==", user_id)

def get_all_armies():
    """
    Retrieve all Army documents, sorted by Id.

    :return: List of all army dictionaries sorted by Id
    """
    docs = db.collection(COLLECTION_NAME).order_by('Id').stream()
    return [{**doc.to_dict(), 'id': doc.id} for doc in docs]
