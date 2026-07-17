from .database import client, database
from .models import DirMetaInfo, FileMetaInfo, MetaInfo, MetaInfoGet, SourcePath
from .repositories import IRepository, MongoAdapter

__version__ = 'v1.0.0'
__author__ = 'Romesky'

__all__ = [
    'client',
    'database',
    'DirMetaInfo',
    'FileMetaInfo',
    'MetaInfo',
    'MongoAdapter',
    'MetaInfoGet',
    'SourcePath',
    'IRepository',
]