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
            message=f'Ошибка конфигурации url пути к бд',
            original_exc=original_exc,
        )

class ServerIsNotRunning(MongoDbException):
    def __init__(self, original_exc: str):
        self.original_exc = original_exc
        super().__init__(
            message=f'Сервер не запущен или недоступен',
            original_exc=original_exc,
        )

class ConnectionError(MongoDbException):
    def __init__(self, original_exc: str):
        self.original_exc = original_exc
        super().__init__(
            message=f'Не удалось подключиться к серверу, неверный порт, фаервол',
            original_exc=original_exc,
        )

class AuthError(MongoDbException):
    def __init__(self, original_exc: str):
        self.original_exc = original_exc
        super().__init__(
            message=f'Ошибка аунтификации, подробнее',
            original_exc=original_exc,
        )

class InCorrectNameDb(MongoDbException):
    def __init__(self, original_exc: str):
        self.original_exc = original_exc
        super().__init__(
            message=f'Некорректное имя бд',
            original_exc=original_exc,
        )