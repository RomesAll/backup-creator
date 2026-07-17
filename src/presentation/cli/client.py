
from src.business.backup_creator import BackUpCreator
from src.data.database import database
from src.data.repositories import MongoAdapter
from pathlib import Path

class CliClient:
    @staticmethod
    def backup(
            source_path: str,
            backup_path: str = '/home/roman/backup'
    ):
        mongo_repo = MongoAdapter(database)
        service = BackUpCreator(
            source=Path(source_path),
            repository=mongo_repo,
            backup_path=Path(backup_path)
        )
        service.create_backup()
        return 'ok'