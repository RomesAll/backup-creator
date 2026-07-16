from pathlib import Path
from typing import Callable

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