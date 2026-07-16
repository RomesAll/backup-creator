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
