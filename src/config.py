from pydantic import SecretStr, ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
from src.presentation.exceptions import EnvReadFileError

BASE_DIR = Path(__file__).parent.parent

class MongoConfig(BaseSettings):
    host: str
    port: int
    username: str
    password: SecretStr
    express_url:str
    basicauth_enabled: bool
    basicauth_username: str
    basicauth_password: SecretStr

    @property
    def url(self):
        return f'mongodb://{self.username}:{self.password.get_secret_value()}@{self.host}:{self.port}/'

class Config(BaseSettings):
    mongodb: MongoConfig

    model_config = SettingsConfigDict(
        extra='ignore',
        env_file=f'{BASE_DIR}/.env',
        env_nested_delimiter='__'
    )

try:
    config = Config()
except ValidationError as e:
    raise EnvReadFileError(e)