from pymongo import MongoClient
from src.config import config

class MongoManager:
    def __init__(self):
        client = MongoClient(config.mongodb.url)
        database = client['backup_db']

    def connection(self):
        pass

    def get_database(self):
        pass