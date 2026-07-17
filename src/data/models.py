from pathlib import Path
from pydantic import BaseModel, field_validator, ValidationError, ConfigDict
import re

class SourcePath(BaseModel):
    source: Path
    model_config = ConfigDict(extra='ignore')

    @field_validator('source')
    @classmethod
    def validate_path(cls, value: Path):
        if not value.exists():
            raise FileNotFoundError('Ресурс для backup не найден')
        return value


class MetaInfoGet(SourcePath):
    target_path: Path

    @field_validator('target_path')
    @classmethod
    def validate_path(cls, value: Path):
        return super().validate_path(value)

class MetaInfo(MetaInfoGet):
    backup_path: Path
    uid: int
    gid: int
    mode: int
    mtime: float

    @field_validator('backup_path')
    @classmethod
    def validate_path(cls, value: Path):
        return super().validate_path(value)

class DirMetaInfo(MetaInfo):
    pass

class FileMetaInfo(MetaInfo):
    hash: str

    @field_validator('hash')
    @classmethod
    def validate_hash(cls, value: str):
        pattern = r"[0-9A-Fa-f]{64}"
        if bool(re.match(pattern, value)):
            return value
        raise ValidationError(f"Хеш не подходит под паттерн '{pattern}'")

def mapping_dto(path: Path) -> type[MetaInfo] | None:
    mapping = {
        path.is_file: FileMetaInfo,
        path.is_dir: DirMetaInfo
    }
    for func, dto in mapping.items():
        if func():
            return dto
    return None