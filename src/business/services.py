from main import Sha256Hash
import os
from pathlib import Path
import shutil
import json

from src.data.models import MetaInfoGet, mapping_dto
from src.data.repositories import IRepository

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
        source_dir = self.source.parts[-1]
        backup_with_source = self.backup_path / source_dir
        backup_with_source.mkdir(parents=True, exist_ok=True)
        stat = os.stat(self.source)
        os.chown(backup_with_source, stat.st_uid, stat.st_gid)
        os.chmod(backup_with_source, stat.st_mode)
        os.utime(backup_with_source, (stat.st_mtime, stat.st_mtime))
