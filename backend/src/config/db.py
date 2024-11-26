# from flask_mongoengine import MongoEngine
# import os
#
# db = MongoEngine()
#
#
# def connect_db(app):
#     app.config['MONGODB_HOST'] = os.getenv('DB_PATH')
#     print(os.getenv('DB_PATH'))
#     db.init_app(app)
#     print("Connected to MongoDB")

from mongoengine import connect
from mongoengine.connection import get_db
import os


def connect_db():
    try:
        db_name = os.getenv('DB_NAME')

        if not db_name:
            raise ValueError("DB_NAME not set in .env")

        db_path = os.getenv('DB_PATH')

        if not db_path:
            raise ValueError("DB_PATH not set in .env")

        if not db_path.startswith(('mongodb://', 'mongodb+srv://')):
            raise ValueError("Invalid MongoDB URL format. Must start with 'mongodb://' or 'mongodb+srv://'")

        connection = connect(db=db_name, host=db_path)
        print("Connected to MongoDB")

        #db = connection.get_database('eruim')
        #db = get_db()




        #collections = db.list_collection_names()
        #print(collections)
        # required_collections = ["cities", "events", "venues", "event_types", "users"]
        #
        # for collection in required_collections:
        #     if collection not in collections:
        #         db.create_collection(collection)
        #         print(f"Created collection: {collection}")
        return connection
    except Exception as e:
        print(f"Failed to connect to MongoDB: {str(e)}")
        raise
