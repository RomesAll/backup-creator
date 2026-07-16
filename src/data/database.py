from pymongo import MongoClient

client = MongoClient('mongodb://root:example@mongo:27017/')
database = client['backup_db']