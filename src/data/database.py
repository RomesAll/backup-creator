from pymongo import MongoClient
from pymongo.errors import ConfigurationError, ConnectionFailure, PyMongoError
from .exceptions import InCorrectConfig, ConnectionDataBaseError, DataBaseError
from src.config import config
import logging

logger = logging.getLogger(config.logging.name_app_logger)

class MongoManager:
    def __init__(self, url: str = config.mongodb.url):
        self.url = url
        self.client = None
        self.database = None

    def __setstate__(self, state):
        self.__dict__.update(state)

    def __getstate__(self):
        state = self.__dict__.copy()
        state['client'] = None
        state['database'] = None
        return state

    def connection(self):
        try:
            self.client = MongoClient(
                self.url,
                socketTimeoutMS=5000,
                connectTimeoutMS=5000,
                serverSelectionTimeoutMS=5000,
            )
            self.database = self.client['backup_db']
            self.client.admin.command('ping')
            logger.debug('Подключение к бд mongodb прошло успешно')
        except (ConfigurationError, ValueError) as e:
            raise InCorrectConfig.create(e, url=self.url) from e
        except ConnectionFailure as e:
            raise ConnectionDataBaseError.create(e, url=self.url) from e
        except PyMongoError as e:
            raise DataBaseError.create(e, url=self.url)

    def get_database(self):
        try:
            if self.client is None and self.database is None:
                self.connection()
            return self.database
        except DataBaseError:
            raise