from pymongo import MongoClient

# Initialize connection
client = MongoClient('mongodb://localhost:27017/')
db = client['sign_language_db']

# db.detection_history can be used directly for operations
