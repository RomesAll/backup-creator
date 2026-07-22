import sys
from pydantic import ValidationError
import time
from src.config import config
import logging

logger = logging.getLogger(config.logging.name_app_logger)

try:
    from src.config import config
    from src.business.backup_creator import create_backup_worker_processes


except ValidationError:
    logger.error('Не удалось прочитать env файл с переменными,'
          'убедитесь что ваш файл .env существует')

except Exception as e:
    logger.error('Внутренняя ошибка программы, детали: %s', str(e))
    sys.exit(1)


class CliClient:
    @staticmethod
    def backup(
            source_path: str,
            backup_path: str
    ):
        create_backup_worker_processes(
            source_path,
            backup_path
        )
        logger.info('Backup создан!, путь: %s',
                f'{backup_path}')
        logger.info('Завершение работы программмы ...')
        time.sleep(1)
        sys.exit(1)