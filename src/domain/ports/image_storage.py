from abc import ABC, abstractmethod
from typing import BinaryIO, Union
from enum import Enum


class ProfileImageType(Enum):
    PROFILE_PICTURE = "profile_picture"
    BACKGROUND_PICTURE = "background_picture"
class DailyCheckupImageType(Enum):
    DAILY_CHECKUP = "daily_checkup"

class ImageStorage(ABC):
    
    @abstractmethod
    async def upload(self, file: BinaryIO, filename: str, image_type: Union[ProfileImageType, None] = None) -> str:
        pass
    
    @abstractmethod
    async def delete(self, object_key: str) -> None:
        pass
    
    @abstractmethod
    def extract_key_from_url(self, url: str) -> str:
        pass
    
    @abstractmethod
    async def get_upload_url(self, filename: str, image_type: ProfileImageType) -> str:
        pass