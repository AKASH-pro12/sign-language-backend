import os
from pymongo import MongoClient

# Initialize connection
mongo_uri = os.environ.get('MONGO_URI')
client = MongoClient(mongo_uri)
try:
    db = client.get_default_database()
except Exception:
    db = client['sign_language_db']

# db.detection_history can be used directly for operations
