from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent

class MongoConfig(BaseSettings):
    host: str
    port: int
    username: str
    password: SecretStr

    @property
    def url(self):
        return f'mongodb://{self.username}:{self.password.get_secret_value()}@{self.host}:{self.port}/'

class Config(BaseSettings):
    mongodb: MongoConfig

    model_config = SettingsConfigDict(
        env_file=f'{BASE_DIR}/.env',
        env_nested_delimiter='__'
    )

config = Config()