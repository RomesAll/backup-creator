from pymongo import MongoClient
from pymongo.errors import ConfigurationError, ServerSelectionTimeoutError, ConnectionFailure, OperationFailure, \
    InvalidName, PyMongoError
from src.config import config

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
            print(f'Ошибка конфигурации url пути к бд, подробнее: {e}')
        except ServerSelectionTimeoutError as e:
            print(f'Сервер не запущен или недоступен')
        except ConnectionFailure as e:
            print(f'Не удалось подключиться к серверу, неверный порт, фаервол')
        except OperationFailure as e:
            print(f'Ошибка аунтификации, подробнее: {e}')
        except InvalidName as e:
            print(f'Некорректное имя бд, подробнее: {e}')

    def get_database(self):
        try:
            if not(self.client and self.database):
                self.connection()
            return self.database
        except PyMongoError as e:
            print('Ошибка ', e)