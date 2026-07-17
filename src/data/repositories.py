from abc import ABC, abstractmethod
from pymongo.database import Database
from pymongo.errors import ServerSelectionTimeoutError, ConnectionFailure, OperationFailure, InvalidName
from pymongo.results import UpdateResult
from src.data.exceptions import MetaInfoNotFound, GetMetaInfoNotFound, UpdateMetaInfo, ServerIsNotRunning, AuthError, \
    InCorrectNameDb, ConnectionError
from src.data.models import DirMetaInfo, FileMetaInfo, MetaInfo, MetaInfoGet
from functools import wraps
from src.config import config
import logging

logger = logging.getLogger(config.logging.name_app_logger)

def set_collections(func):
    @wraps(func)
    def wrapper(self, meta: MetaInfoGet):
        try:
            self.collection = self.database[
                str(meta.source.resolve())
            ]
            logger.debug('Получена коллекция mongodb: %s', self.collection)
            return func(self, meta)
        except ServerSelectionTimeoutError as e:
            msg = 'Сервер не запущен или недоступен'
            logger.error(msg + ' %s', str(e))
            raise ServerIsNotRunning(msg)
        except ConnectionFailure as e:
            msg = 'Не удалось подключиться к серверу, неверный порт, фаервол'
            logger.error(msg + ' %s', str(e))
            raise ConnectionError(msg)
        except OperationFailure as e:
            msg = f'Ошибка аунтификации, подробнее: {e}'
            logger.error(msg)
            raise AuthError(msg)
        except InvalidName as e:
            msg = f'Некорректное имя бд, подробнее: {e}'
            logger.error(msg)
            raise InCorrectNameDb(msg)
    return wrapper

class IRepository(ABC):
    @abstractmethod
    def get_metadata(self, meta: MetaInfoGet):
        pass

    @abstractmethod
    def save_metadata(self, meta: MetaInfo):
        pass

class MongoAdapter(IRepository):
    def __init__(self, database: Database):
        self.database = database
        self.collection = None

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
            logger.warning('Метаданные файла(папки) не найдены')
            raise MetaInfoNotFound(find_filter)
        for func, dto_type in mapping.items():
            if metadata and func():
                logger.debug('Получены метаданные файла(папки) %s', metadata)
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
        if result.matched_count != 1:
            logger.warning('Ошибка обновление метаданных файла(папки), %s', meta.target_path.resolve())
            raise UpdateMetaInfo(update_data, result.matched_count)
        return result