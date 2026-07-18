from pathlib import Path
from src.business.backup_creator import BackUpCreator
import re

class TestBackupCreator:
    def test_gen_hash_file_data(self, mock_open_file, mock_path):
        hash_file_data: str = BackUpCreator.generation_hash(Path('/dev/null'))
        assert bool(re.match(r'[0-9A-Fa-f]{64}', hash_file_data)) == True

    def test_scan_folders(self, setup_dirs):
        result = list(BackUpCreator.scan_folders(setup_dirs))
        assert len(result) == 3

    def test_create_backup(
            self,
            setup_dirs,
            mock_open_file,
            mock_path,
            mock_repo,
            mock_shutil_copy,
            mock_refresh_stat
    ):
        try:
            backup = BackUpCreator(
                source=setup_dirs,
                backup_path=setup_dirs.parent / 'backup',
                repository=mock_repo
            )
            backup.create_backup()
        except StopIteration as e:
            pass
