from .firestore_init import db


def write_data(collection_name, document_id, data):
    """
    Write data to a Firestore document.

    :param collection_name: Name of the collection
    :param document_id: ID of the document
    :param data: Dictionary of data to write
    """
    try:
        if document_id:
            doc_ref = db.collection(collection_name).document(document_id)
            doc_ref.set(data)
            return document_id
        else:
            doc_ref = db.collection(collection_name).add(data)
            generated_id = doc_ref[1].id
            print(f"Data written to {collection_name}/{generated_id}")
    except Exception as e:
        print(f"Error writing data: {e}")
        return None

def read_data(collection_name, document_id):
    """
    Read data from a Firestore document.

    :param collection_name: Name of the collection
    :param document_id: ID of the document
    :return: Document data as a dictionary, or None if not found
    """
    try:
        doc_ref = db.collection(collection_name).document(document_id)
        doc = doc_ref.get()
        if doc.exists:
            return {**doc.to_dict(), 'id': doc.id}
        else:
            print(f"Document {collection_name}/{document_id} not found")
            return None
    except Exception as e:
        print(f"Error reading data: {e}")
        return None

def update_data(collection_name, document_id, data):
    """
    Update data in a Firestore document.

    :param collection_name: Name of the collection
    :param document_id: ID of the document
    :param data: Dictionary of data to update
    """
    try:
        doc_ref = db.collection(collection_name).document(document_id)
        doc_ref.update(data)
        print(f"Data updated in {collection_name}/{document_id}")
    except Exception as e:
        print(f"Error updating data: {e}")

def delete_data(collection_name, document_id):
    """
    Delete a Firestore document.

    :param collection_name: Name of the collection
    :param document_id: ID of the document
    """
    try:
        doc_ref = db.collection(collection_name).document(document_id)
        doc_ref.delete()
        print(f"Document {collection_name}/{document_id} deleted")
    except Exception as e:
        print(f"Error deleting data: {e}")

def query_data(collection_name, field, operator, value):
    """
    Query data from a Firestore collection.

    :param collection_name: Name of the collection
    :param field: Field to query
    :param operator: Query operator (e.g., '==', '>', '<')
    :param value: Value to compare
    :return: List of documents matching the query
    """
    try:
        query = db.collection(collection_name).where(field, operator, value)
        results = query.stream()
        docs = []
        for doc in results:
            docs.append({**doc.to_dict(), 'id': doc.id})
        return docs
    except Exception as e:
        print(f"Error querying data: {e}")
        return []
