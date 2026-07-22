from abc import ABC, abstractmethod
from pymongo.errors import ServerSelectionTimeoutError, ConnectionFailure, OperationFailure, InvalidName, PyMongoError
from pymongo.results import UpdateResult
from src.data.database import MongoManager
from src.data.exceptions import MetaInfoNotFound, GetMetaInfoNotFound, ServerIsNotRunning, AuthError, \
    InCorrectNameDb, ConnectionError, DataBaseError
from src.data.models import DirMetaInfo, FileMetaInfo, MetaInfo, MetaInfoGet
from functools import wraps
from src.config import config
import logging

logger = logging.getLogger(config.logging.name_app_logger)

def set_collections(func):
    @wraps(func)
    def wrapper(self: MongoAdapter, meta: MetaInfoGet):
        try:
            if self.manager.client is None:
                self.connection()
            self.collection = self.manager.get_database()[
                str(meta.source.resolve())
            ]
            logger.debug('Получена коллекция mongodb: %s', self.collection)
            return func(self, meta)
        except ServerSelectionTimeoutError as e:
            msg = 'Сервер не запущен или недоступен'
            logger.error(msg + ' %s', str(e))
            raise ServerIsNotRunning(msg) from e
        except ConnectionFailure as e:
            msg = 'Не удалось подключиться к серверу, неверный порт, фаервол'
            logger.error(msg + ' %s', str(e))
            raise ConnectionError(msg) from e
        except OperationFailure as e:
            msg = f'Ошибка аунтификации, подробнее: {e}'
            logger.error(msg)
            raise AuthError(msg) from e
        except InvalidName as e:
            msg = f'Некорректное имя бд, подробнее: {e}'
            logger.error(msg)
            raise InCorrectNameDb(msg) from e
        except PyMongoError as e:
            raise DataBaseError.create(e, url=config.mongodb.url)
    return wrapper

class IRepository(ABC):
    @abstractmethod
    def get_metadata(self, meta: MetaInfoGet):
        pass

    @abstractmethod
    def save_metadata(self, meta: MetaInfo):
        pass

class MongoAdapter(IRepository):
    def __init__(self, manager: MongoManager):
        self.manager = manager
        self.collection = None

    def __setstate__(self, state):
        self.__dict__.update(state)

    def __getstate__(self):
        state = self.__dict__.copy()
        state['collection'] = None
        return state

    def connection(self):
        try:
            self.manager.connection()
        except DataBaseError:
            raise

    @set_collections
    def get_metadata(self, meta: MetaInfoGet):
        mapping = {
            meta.target_path.is_file: FileMetaInfo,
            meta.target_path.is_dir: DirMetaInfo
        }
        find_filter: dict = {
            'target_path': str(meta.target_path.resolve()),
        }
        metadata: dict | None = self.collection.find_one(
            find_filter,
            {'_id': 0}
        )
        if not metadata:
            logger.debug('Метаданные файла(папки) не найдены')
            raise MetaInfoNotFound(find_filter)
        for func, dto_type in mapping.items():
            if metadata and func():
                logger.debug('Получены метаданные файла(папки) %s', meta.target_path)
                return dto_type(**metadata)
        logger.warning('Ошибка получения метаданных файла(папки)')
        raise GetMetaInfoNotFound(
            str(meta.target_path.resolve()),
            metadata
        )

    @set_collections
    def save_metadata(self, meta: MetaInfo):
        filter_query = {
            'target_path': str(meta.target_path.resolve())
        }
        update_data = {
            '$setOnInsert': {
                'source': str(meta.source.resolve()),
                'target_path': str(meta.target_path.resolve()),
                'backup_path': str(meta.backup_path.resolve())
            },
            '$set': {
                'uid': meta.uid,
                'gid': meta.gid,
                'mode': meta.mode,
                'mtime': meta.mtime
            }
        }
        if meta.target_path.is_file():
            update_data['$setOnInsert']['hash'] = meta.hash
        result: UpdateResult = self.collection.update_one(
            filter_query,
            update_data,
            upsert=True
        )
        logger.debug('Обновление метаданных файла(папки), %s', meta.target_path.resolve())
        return result