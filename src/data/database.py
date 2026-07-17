from pymongo import MongoClient

client = MongoClient('mongodb://root:example@127.0.0.1:27017/')
database = client['backup_db']