import hashlib
from unittest.mock import patch, MagicMock
import pytest
from pathlib import Path
import shutil

from src.business import BackUpCreator
from src.data import FileMetaInfo
from src.data.repositories import MongoAdapter

@pytest.fixture(scope='session')
def mock_open_file():
    patcher = patch('builtins.open')
    mock_open = patcher.start()
    mock_file = mock_open.return_value.__enter__.return_value
    mock_file.read.side_effect = [
        'данные для хеша1'.encode(),
        'данные для хеша2'.encode(),
        ''.encode()
    ]
    mock_file.write.return_value = None
    yield mock_file
    patcher.stop()

@pytest.fixture(scope='session')
def mock_path():
    patcher_exists = patch.object(Path, 'exists')
    mock_exists = patcher_exists.start()
    mock_exists.return_value = True
    yield mock_exists
    patcher_exists.stop()

@pytest.fixture(scope='session')
def mock_repo():
    repo = MagicMock()
    repo.get_metadata.return_value = None
    repo.get_metadata.side_effect = [
        None,
        FileMetaInfo(
            source=Path('/dev/null'),
            target_path=Path('/dev/null'),
            backup_path=Path('/dev/null'),
            uid=1000,
            gid=1000,
            mode=755,
            mtime=1244325,
            hash=hashlib.sha256('test'.encode()).hexdigest()
        ),
        ''
    ]
    repo.save_metadata.return_value = None
    return repo

@pytest.fixture(scope='session')
def mock_refresh_stat():
    patcher = patch.object(BackUpCreator, 'refresh_stat')
    mock = patcher.start()
    mock.return_value = None
    yield mock
    patcher.stop()

@pytest.fixture(scope='session')
def mock_shutil_copy():
    patcher = patch.object(shutil, 'copy2')
    mock = patcher.start()
    yield mock
    patcher.stop()

@pytest.fixture(scope='function')
def setup_dirs(tmp_path):
    dir1 = tmp_path / "folder1"
    dir1.mkdir()
    file1 = dir1 / "file1.txt"
    file1.touch()
    file2 = tmp_path / "file2.txt"
    file2.touch()
    yield tmp_path