from abc import ABC, abstractmethod
from pymongo.database import Database
from pymongo.errors import ServerSelectionTimeoutError, ConnectionFailure, OperationFailure, InvalidName
from pymongo.results import UpdateResult

from src.data.exceptions import MetaInfoNotFound, GetMetaInfoNotFound, UpdateMetaInfo, ServerIsNotRunning, AuthError, \
    InCorrectNameDb, ConnectionError
from src.data.models import DirMetaInfo, FileMetaInfo, MetaInfo, MetaInfoGet
from functools import wraps

def set_collections(func):
    @wraps(func)
    def wrapper(self, meta: MetaInfoGet):
        try:
            self.collection = self.database[
                str(meta.source.resolve())
            ]
            return func(self, meta)
        except ServerSelectionTimeoutError as e:
            raise ServerIsNotRunning(f'Сервер не запущен или недоступен')
        except ConnectionFailure as e:
            raise ConnectionError(f'Не удалось подключиться к серверу, неверный порт, фаервол')
        except OperationFailure as e:
            raise AuthError(f'Ошибка аунтификации, подробнее: {e}')
        except InvalidName as e:
            raise InCorrectNameDb(f'Некорректное имя бд, подробнее: {e}')
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
            raise MetaInfoNotFound(find_filter)
        for func, dto_type in mapping.items():
            if metadata and func():
                return dto_type(**metadata)
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
        if result.matched_count != 1:
            raise UpdateMetaInfo(update_data, result.matched_count)
        return result