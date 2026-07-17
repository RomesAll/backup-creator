from pymongo import MongoClient
from pymongo.errors import ConfigurationError, ServerSelectionTimeoutError, ConnectionFailure, OperationFailure, \
    InvalidName, PyMongoError
from src.data.exceptions import InCorrectUrl, ServerIsNotRunning, AuthError, InCorrectNameDb
from src.config import config
import logging

logger = logging.getLogger(config.logging.name_app_logger)

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
            logger.debug('Подключение к бд mongodb прошло успешно')
        except ConfigurationError as e:
            logger.error('Неверный путь url к бд mongodb: %s', str(e))
            raise InCorrectUrl(str(e))

        except ServerSelectionTimeoutError as e:
            logger.error('Сервер с mongodb не работает: %s', str(e))
            raise ServerIsNotRunning(str(e))

        except ConnectionFailure as e:
            logger.error('Неудалось подключиться к mongodb: %s', str(e))
            raise ConnectionError(str(e))

        except OperationFailure as e:
            logger.error('Неудалось выполнить операции с mongodb: %s', str(e))
            raise AuthError(str(e))

        except InvalidName as e:
            logger.error('Неправильное имя бд: %s', str(e))
            raise InCorrectNameDb(str(e))

    def get_database(self):
        try:
            if not(self.client and self.database):
                self.connection()
            return self.database

        except PyMongoError as e:
            raise

mongo_manager = MongoManager()