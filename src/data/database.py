from pymongo import MongoClient
from pymongo.errors import ConfigurationError, ServerSelectionTimeoutError, ConnectionFailure, OperationFailure, \
    InvalidName, PyMongoError
from src.config import config
from src.data.exceptions import InCorrectUrl, ServerIsNotRunning, AuthError, InCorrectNameDb


class MongoManager:
    def __init__(self, url: str = config.mongodb.url):
        self.url = url
        self.client = None
        self.database = None

    def connection(self):
        try:
            self.client = MongoClient(self.url)
            self.database = self.client['backup_db']
            self.client.admin.command('ping')

        except ConfigurationError as e:
            raise InCorrectUrl(str(e))

        except ServerSelectionTimeoutError as e:
            raise ServerIsNotRunning(str(e))

        except ConnectionFailure as e:
            raise ConnectionError(str(e))

        except OperationFailure as e:
            raise AuthError(str(e))

        except InvalidName as e:
            raise InCorrectNameDb(str(e))

    def get_database(self):
        try:
            if not(self.client and self.database):
                self.connection()
            return self.database

        except PyMongoError as e:
            raise

mongo_manager = MongoManager()