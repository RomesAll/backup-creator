import sys
from pydantic import ValidationError
from pathlib import Path
import time

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
    print('[MESSAGE]: Не удалось прочитать env файл с переменными,'
          'убедитесь что ваш файл .env соотвествует шаблону:'
          '\nMONGODB__USERNAME1=root'
          '\nMONGODB__PASSWORD=example'
          '\nMONGODB__HOST=127.0.0.1'
          '\nMONGODB__PORT=27017'
          '\nME_CONFIG_MONGODB_URL: mongodb://root:example@mongo:27017/'
          '\nME_CONFIG_BASICAUTH_ENABLED: true'
          '\nME_CONFIG_BASICAUTH_USERNAME: mongoexpressuser'
          '\nME_CONFIG_BASICAUTH_PASSWORD: mongoexpresspass')
    print('')

except Exception as e:
    print(f'[MESSAGE]: Внутренняя ошибка программы, детали: {e}')
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
            print(f'[MESSAGE]: Backup создан!, путь: '
                    f'{backup_path}/{service.name_source_dir}')

        except ValidationError as e:
            print(f'[MESSAGE]: Ошибка валидации данных, {e}')

        except TypeError as e:
            print(f'[MESSAGE]: Внутренняя ошибка программы, детали: {e}')

        except FileNotFoundError as e:
            print(f'[MESSAGE]: Файл не найден, детали: {e}')

        except MetaInfoNotFound as e:
            print(f'[MESSAGE]: Внутренняя ошибка программы, '
                  f'метаданные файла не найдены, детали: {e}')

        except GetMetaInfoNotFound as e:
            print(f'[MESSAGE]: Внутренняя ошибка программы, '
                  f'метаданные файла не найдены, детали: {e}')

        except UpdateMetaInfo as e:
            print(f'[MESSAGE]: Внутренняя ошибка программы, '
                  f'метаданные файла не удалось обновить, детали: {e}')

        except ConnectionError as e:
            print(f'[MESSAGE]: Внутренняя ошибка программы, неудалось'
                  f'подключиться к бд с метаданными: {e}')

        except AuthError as e:
            print(f'[MESSAGE]: недостаточно прав для выполнения действий, детали {e}')

        except MongoDbException as e:
            print(f'[MESSAGE]: Внутренняя ошибка программы: {e}')

        except DataException as e:
            print(f'[MESSAGE]: Внутренняя ошибка программы: {e}')

        except Exception as e:
            print(f'[MESSAGE]: Неизвестная внутренняя ошибка программы: {e}')

        finally:
            print('[MESSAGE]: Завершение работы программмы ...')
            time.sleep(1)
            sys.exit(1)