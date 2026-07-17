from abc import ABC, abstractmethod
from pymongo.database import Database
from src.data.models import DirMetaInfo, FileMetaInfo, MetaInfo, MetaInfoGet
from hashlib import sha256
from functools import wraps

def set_collections(func):
    @wraps(func)
    def wrapper(self, meta: MetaInfoGet):
        # self.source_hash = sha256(
        #     str(meta.source.resolve()).encode()
        # ).hexdigest()
        self.collection = self.database[
            str(meta.source.resolve())
        ]
        return func(self, meta)
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
        self.collection = database['base_collection']

    @set_collections
    def get_metadata(self, meta: MetaInfoGet):
        mapping = {
            meta.target_path.is_file: FileMetaInfo,
            meta.target_path.is_dir: DirMetaInfo
        }
        metadata: dict | None = self.collection.find_one({
            'target_path': str(meta.target_path.resolve()),
        }, {'_id': 0})
        if not metadata:
            return None
        for func, dto_type in mapping.items():
            if metadata and func():
                return dto_type(**metadata)
        return metadata

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
        result = self.collection.update_one(
            filter_query,
            update_data,
            upsert=True
        )
        return result