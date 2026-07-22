import re
from pymongo.errors import ServerSelectionTimeoutError, NetworkTimeout, AutoReconnect

class DataException(Exception):
    def __init__(
            self,
            message: str = 'Неизвестная ошибка в data слое',
            detail: str | dict = '-'
    ):
        self.message = f'{message}, детали: {detail}'
        self.detail = detail

class MetaInfoNotFound(DataException):
    def __init__(self, filter_info: dict):
        self.filter_info = filter_info
        super().__init__(
            message=f'Ну удалось найти запись в '
                    f'mongodb по: \n{filter_info}',
        )

class GetMetaInfoNotFound(DataException):
    def __init__(self, target_path: str, metadata: dict):
        self.metadata = metadata
        self.target_path= target_path
        super().__init__(
            message=f'Ошибка обработки полученого документа из mongodb, '
                    f'запись найдена, но путь к ресурсу '
                    f'target_path={target_path} некорректен, возможно'
                    f'во время работы программы он был удален',
            detail=metadata
        )

class UpdateMetaInfo(DataException):
    def __init__(self, data_update: dict, matched_count):
        self.data_update = data_update
        self.matched_count = matched_count
        super().__init__(
            message=f'Не удалось найти данные по фильтру,'
                    f'кол-во документов подошедший под условие: {matched_count}',
            detail=data_update
        )

class MongoDbException(DataException):
    def __init__(
            self,
            message: str = 'Неизвестная ошибка mongodb',
            original_exc: str = '-',
            detail: dict | str = '-'
    ):
        self.original_exc = original_exc
        super().__init__(
            message=f'{message}, оригинальная ошибка: {original_exc}',
            detail=detail
        )

class InCorrectUrl(MongoDbException):
    def __init__(self, original_exc: str):
        self.original_exc = original_exc
        super().__init__(
            message='Ошибка конфигурации url пути к бд',
            original_exc=original_exc,
        )

class ServerIsNotRunning(MongoDbException):
    def __init__(self, original_exc: str):
        self.original_exc = original_exc
        super().__init__(
            message='Сервер не запущен или недоступен',
            original_exc=original_exc,
        )

class ConnectionError(MongoDbException):
    def __init__(self, original_exc: str):
        self.original_exc = original_exc
        super().__init__(
            message='Не удалось подключиться к серверу, неверный порт, фаервол',
            original_exc=original_exc,
        )

class AuthError(MongoDbException):
    def __init__(self, original_exc: str):
        self.original_exc = original_exc
        super().__init__(
            message='Ошибка аунтификации, подробнее',
            original_exc=original_exc,
        )

class InCorrectNameDb(MongoDbException):
    def __init__(self, original_exc: str):
        self.original_exc = original_exc
        super().__init__(
            message='Некорректное имя бд',
            original_exc=original_exc,
        )


class DataBaseError(Exception):
    def __init__(self, msg, original, context=None):
        self.msg = msg
        self.original = original
        self.context = context or {}
        super().__init__(f'{msg}, доп. инфо: {context.get('url', '-')}')

    @classmethod
    def create(cls, error, url):
        return cls(
            msg=str(error),
            original=error,
            context={'url': url}
        )

class InCorrectConfig(DataBaseError):
    def __init__(self, msg, original, context=None):
        super().__init__(msg, original, context)

    @classmethod
    def create(cls, error, url):
        msg = ''
        context = {'url': url}
        original_error = str(error)
        if re.search(r'empty host', original_error, re.IGNORECASE):
            msg = 'Неверно указан хост в uri'
        if re.search(r'invalid uri', original_error, re.IGNORECASE):
            msg = ('Неверно указан uri подключения к БД, '
                   'ожидается mongodb://.. или mongodb+driver://')
        if match := re.search(r'(unknown option:) (\w+)\.', original_error, re.IGNORECASE):
            msg = f'Передан неизвестный параметр: {match.group(2)}'
        if re.search('reserved characters', original_error, re.IGNORECASE):
            msg = 'Передан неверный uri, возможно пропущен зарезервированный символ : или /'
        if re.search(r'authMechanism', original_error, re.IGNORECASE):
            msg = ("Передан неверный authMechanism в параметр, должно быть "
                   "['SCRAM-SHA-1', 'GSSAPI', 'MONGODB-OIDC', 'SCRAM-SHA-256', "
                   "'DEFAULT', 'MONGODB-AWS', 'PLAIN', 'MONGODB-X509']")
        return cls(
            msg=msg,
            original=error,
            context=context
        )

class ConnectionDataBaseError(DataBaseError):
    def __init__(self, msg, original, context=None):
        super().__init__(msg, original, context)

    @classmethod
    def create(cls, error, url):
        msg = ''
        context = {'url': url}
        match error:
            case ServerSelectionTimeoutError():
                msg = ('Не удалось подключиться к серверу, '
                       'возможно был неверно указан DNS, порт')
            case NetworkTimeout():
                msg = 'Таймаут сети'
            case AutoReconnect():
                msg = 'Потеря соединения'
        return cls(
            msg=msg,
            original=error,
            context=context
        )
