import sys
from pydantic import ValidationError
from pathlib import Path
import time
from src.config import config
import logging

logger = logging.getLogger(config.logging.name_app_logger)

try:
    from src.presentation.exceptions import EnvReadFileError
    from src.config import config
    from src.business.backup_creator import BackUpCreator
    from src.data.database import mongo_manager
    from src.data.repositories import MongoAdapter

    from src.data.exceptions import UpdateMetaInfo, MongoDbException, DataException, AuthError, \
                    GetMetaInfoNotFound, \
                    MetaInfoNotFound, ConnectionError

except EnvReadFileError as e:
    logger.error('Не удалось прочитать env файл с переменными,'
          'убедитесь что ваш файл .env существует')

except Exception as e:
    logger.error('Внутренняя ошибка программы, детали: %s', str(e))
    sys.exit(1)


class CliClient:
    @staticmethod
    def backup(
            source_path: str,
            backup_path: str = '/home/roman/backup'
    ):
        try:
            mongo_repo = MongoAdapter(mongo_manager.get_database())
            service = BackUpCreator(
                source=Path(source_path),
                repository=mongo_repo,
                backup_path=Path(backup_path)
            )
            service.create_backup()
            logger.info('Backup создан!, путь: %s',
                    f'{backup_path}/{service.name_source_dir}')

        except ValidationError as e:
            logger.error(f'Ошибка валидации данных, %s', str(e))

        except TypeError as e:
            logger.error(f'Внутренняя ошибка программы, детали: %s', str(e))

        except FileNotFoundError as e:
            logger.error(f'Файл не найден, детали: %s', str(e))

        except MetaInfoNotFound as e:
            logger.error(f'Внутренняя ошибка программы, '
                  f'метаданные файла не найдены, детали: %s', str(e))

        except GetMetaInfoNotFound as e:
            logger.error(f'Внутренняя ошибка программы, '
                  f'метаданные файла не найдены, детали: %s', str(e))

        except UpdateMetaInfo as e:
            logger.error(f'Внутренняя ошибка программы, '
                  f'метаданные файла не удалось обновить, детали: %s', str(e))

        except ConnectionError as e:
            logger.error(f'Внутренняя ошибка программы, неудалось'
                  f'подключиться к бд с метаданными: %s', str(e))

        except AuthError as e:
            logger.error(f'Недостаточно прав для выполнения действий, детали %s', str(e))

        except MongoDbException as e:
            logger.error(f'Внутренняя ошибка программы: %s', str(e))

        except DataException as e:
            logger.error(f'Внутренняя ошибка программы: %s', str(e))

        except Exception as e:
            logger.error(f'Неизвестная внутренняя ошибка программы: %s', str(e))

        finally:
            logger.info('Завершение работы программмы ...')
            time.sleep(1)
            sys.exit(1)