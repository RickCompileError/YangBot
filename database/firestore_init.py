from google.cloud import firestore

database = "yang-line-bot-database"

def initialize_firestore():
    """
    Initialize Firestore client using google-cloud-firestore.
    """
    # Create Firestore client
    db = firestore.Client(database=database)
    return db

# Initialize Firestore when this module is imported
db = initialize_firestore()
