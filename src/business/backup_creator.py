import shutil
from functools import partial
from multiprocessing import Pool
from pathlib import Path
from src.config import config
from src.data import MongoAdapter, IRepository
from hashlib import sha256
import pickle
import os
import logging
from src.data.database import MongoManager
from src.data.exceptions import DataException, DataBaseError
from src.data.models import mapping_dto, MetaInfoGet, FileMetaInfo

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

    def __setstate__(self, state):
        logger.debug('Восстановление объекта класса дочернем процессе')
        self.__dict__.update(state)

    def __getstate__(self):
        logger.debug('Сериализация объекта класса для передачи дочернему процессу')
        state = self.__dict__.copy()
        return state

    def create_root_dir(self):
        if not self.source.exists():
            raise FileNotFoundError(f'Путь к source файлу не существует, {self.source}')
        source_dir = self.source.parts[-1]
        backup_with_source = self.backup_path / source_dir
        backup_with_source.mkdir(parents=True, exist_ok=True)
        stat = os.stat(self.source)
        os.chown(backup_with_source, stat.st_uid, stat.st_gid)
        os.chmod(backup_with_source, stat.st_mode)
        os.utime(backup_with_source, (stat.st_mtime, stat.st_mtime))
        logger.debug('Создание корневой папки для backup: %s', backup_with_source.resolve())

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
        target_hasher = sha256()
        with open(file, mode='rb') as f:
            while True:
                chunk = f.read(65536)
                if not chunk:
                    break
                target_hasher.update(chunk)
        logger.debug(
            'Хеш содержимого файла %s сгенерирован: %s ...',
            file.resolve(),
            target_hasher.hexdigest()[:10]
        )
        return target_hasher.hexdigest()

    def construct_path_backup_file(self, target: Path) -> Path:
        target_path_part = target.parts
        backup_start = self.backup_path
        target_start_ind = target_path_part.index(self.name_source_dir)
        target_start = str('/'.join(
            target_path_part[target_start_ind:]
        ))
        backup_full_file = Path(backup_start.resolve() / target_start)
        logger.debug(
            'Путь для backup построен: %s',
            backup_full_file.resolve()
        )
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
        logger.debug('Обновление метаданных для файла(папки) %s', backup.resolve())

    def _get_data_hash(self, meta: FileMetaInfo | None, backup_path: Path):
        if not meta:
            return self.generation_hash(backup_path)
        return meta.hash

    def create(self, item: Path):
        try:
            logger.debug('Процесс копирование для ресурса: %s', item.resolve())
            backup: Path = self.construct_path_backup_file(item)
            target_data_hash: str | None = None
            if not item.exists():
                raise FileNotFoundError(f'Файл или папка не сущ.: {item.resolve()}')
            if item.is_file():
                target_data_hash = self.generation_hash(item)
                need_copy = False
                try:
                    backup_meta = self.repo.get_metadata(MetaInfoGet(
                        source=self.source,
                        target_path=item
                    ))
                except DataException:
                    backup_meta = None
                if not backup.exists():
                    need_copy = True
                else:
                    backup_data_hash = self._get_data_hash(backup_meta, backup)
                    if target_data_hash != backup_data_hash:
                            need_copy = True
                if need_copy:
                    shutil.copy2(item, backup)
            self.refresh_stat(item, backup, target_data_hash)
            logger.debug('Процесс копирование для ресурса: %s выполнен успешно', item.resolve())
            return {
                'status': 'ok',
                'msg': 'Файл или папка успешно скопирована',
                'detail': backup.resolve()
            }
        except DataBaseError:
            logger.error('Ошибка подключения к бд')
            return {'status': 'error', 'msg': 'Ошибка подключения к бд', 'detail': item.resolve()}
        except FileNotFoundError:
            logger.error('Ошибка создания backup, файла или папки не сущ.: %s', item.resolve())
            return {'status': 'error', 'msg': 'Файла или папки не сущ.', 'detail': item.resolve()}
        except PermissionError:
            logger.error('Нет прав для копирования файла')
            return {'status': 'error', 'msg': 'Нет прав для копирование файла, папки', 'detail': item.resolve()}
        except Exception as e:
            logger.error('Ошибка создания backup, причина, %s', e)
            return {'status': 'error', 'msg': 'Неизвестная ошибка', 'detail': item.resolve()}

def worker(item, backup_creator_state):
    backup_creator: BackUpCreator = pickle.loads(backup_creator_state)
    return backup_creator.create(item)

def create_backup_worker_processes(source, backup):
    logger.info(f'Начало создания backup ресурса: {source}, в: {backup}')
    repo = MongoAdapter(MongoManager(config.mongodb.url))
    backup_creator: BackUpCreator = BackUpCreator(
        source=Path(source),
        repository=repo,
        backup_path=Path(backup)
    )
    state = pickle.dumps(backup_creator)
    worker_with_params = partial(worker, backup_creator_state=state)
    count_error = 0
    with Pool(4) as pool:
        results = pool.imap(worker_with_params, backup_creator.scan_folders(backup_creator.source))
        for result in results:
            logger.info(
                'статус: %s, сообщение: %s, детали: %s',
                result.get('status', '-'),
                result.get('msg', '-'),
                result.get('detail', '-'),
            )
            if result['status'] == 'error':
                count_error += 1
    logger.info(f'Завершение работы программы, кол-во ошибок: {count_error}')