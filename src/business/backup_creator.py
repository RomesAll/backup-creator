from .hash_adapter import Sha256Hash
import os
from pathlib import Path
import shutil
from src.data.models import MetaInfoGet, mapping_dto
from src.data.repositories import IRepository
from ..data.exceptions import MetaInfoNotFound, GetMetaInfoNotFound, DataException
from src.config import config
import logging

logger = logging.getLogger(config.logging.name_app_logger)

class BackUpCreator:
    def __init__(
            self,
            source: Path,
            repository: IRepository,
            backup_path: Path = Path('/home/roman/backup')
    ):
        self.source: Path = source
        self.backup_path: Path = backup_path
        self.name_source_dir = self.source.parts[-1]
        self.repo = repository
        self.create_root_dir()

    def create_root_dir(self):
        if not self.source.exists():
            raise FileNotFoundError(f'Путь к source файлу не сущесвует, {self.source}')
        source_dir = self.source.parts[-1]
        backup_with_source = self.backup_path / source_dir
        backup_with_source.mkdir(parents=True, exist_ok=True)
        stat = os.stat(self.source)
        os.chown(backup_with_source, stat.st_uid, stat.st_gid)
        os.chmod(backup_with_source, stat.st_mode)
        os.utime(backup_with_source, (stat.st_mtime, stat.st_mtime))
        logger.debug('Создание корневой папки для backup')

    @staticmethod
    def scan_folders(path: Path):
        for item in path.iterdir():
            yield item
            if item.is_dir():
                yield from BackUpCreator.scan_folders(item)

    @staticmethod
    def generation_hash(file: Path) -> str:
        if not file.exists():
            raise Exception('File not found')
        target_hasher = Sha256Hash()
        with open(file, mode='rb') as f:
            while True:
                chunk = f.read(65536)
                if not chunk:
                    break
                target_hasher.append_hash_chunk(chunk)
        return target_hasher.hashed_data

    def construct_path_backup_file(self, target: Path) -> Path:
        target_path_part = target.parts
        backup_start = self.backup_path
        target_start_ind = target_path_part.index(self.name_source_dir)
        target_start = str('/'.join(
            target_path_part[target_start_ind:]
        ))
        backup_full_file = Path(backup_start.resolve() / target_start)
        return backup_full_file

    def refresh_stat(
            self,
            target: Path,
            backup: Path,
            target_data_hash: str | None
    ):
        if not backup.exists():
            backup.mkdir(exist_ok=True, parents=True)
        stat = os.stat(target)
        os.chown(backup, stat.st_uid, stat.st_gid)
        os.chmod(backup, stat.st_mode)
        os.utime(backup, (stat.st_mtime, stat.st_mtime))
        result_dto = mapping_dto(target)
        self.repo.save_metadata(result_dto(
            source=self.source,
            target_path=target,
            backup_path=backup,
            uid=stat.st_uid,
            gid=stat.st_gid,
            mode=stat.st_mode,
            mtime=stat.st_mtime,
            hash=target_data_hash
        ))
        logger.debug('Обновление метаданных для файла(папки)')

    def create_backup(self):
        for item in self.scan_folders(self.source):
            logger.debug('Процесс копирование для ресурса: %s', item.resolve())
            backup: Path = self.construct_path_backup_file(item)
            target_data_hash: str | None = None
            if item.is_file():
                target_data_hash = self.generation_hash(item)
                try:
                    backup_meta= self.repo.get_metadata(MetaInfoGet(
                        source=self.source,
                        target_path=item
                    ))
                except FileNotFoundError as e:
                    backup_meta = None
                except DataException as e:
                    backup_meta = None
                if not backup_meta:
                    shutil.copy2(item, backup)
                if backup_meta and target_data_hash != backup_meta.hash:
                    shutil.copy2(item, backup)
            self.refresh_stat(item, backup, target_data_hash)
            logger.debug('Процесс копирование для ресурса: %s выполнен успешно', item.resolve())