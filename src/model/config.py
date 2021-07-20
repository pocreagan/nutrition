import datetime
from dataclasses import dataclass

__all__ = [
    'Model',
]


@dataclass
class Model:
    USDA_API_KEY: str
    USDA_REST_ENDPOINT: str
    AGILE_FILE_PATH: str
    DATA_FILE_PATH: str
    CONNECTION_STRING_SUFFIX: str
    BUILD_VERSION: datetime.datetime = datetime.datetime.now()
    APP_VERSION: datetime.datetime = datetime.datetime.now()
