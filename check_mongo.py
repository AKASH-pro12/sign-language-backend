import sys
import os
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

try:
    mongo_uri = os.environ.get('MONGO_URI')
    client = MongoClient(mongo_uri, serverSelectionTimeoutMS=2000)
    client.admin.command('ping')
    print('SUCCESS_CONNECTED')
    db = client['sign_language_db']
    count = db.detection_history.count_documents({})
    print(f'Count: {count}')
    if count > 0:
        print('Latest records:')
        docs = list(db.detection_history.find().sort('_id', -1).limit(5))
        for doc in docs:
            print(doc)
    else:
        print('No data stored yet. Start the backend and make some detections!')
except ConnectionFailure:
    print('FAILED_CONNECTION')
    sys.exit(1)
except Exception as e:
    print(f'ERROR: {e}')
    sys.exit(1)
