from abc import ABC, abstractmethod
from typing import BinaryIO, Union
from enum import Enum


class ProfileImageType(Enum):
    PROFILE_PICTURE = "profile_picture"
    BACKGROUND_PICTURE = "background_picture"


class ImageStorage(ABC):
    """Interface for image storage operations for profile images"""
    
    @abstractmethod
    async def upload(self, file: BinaryIO, filename: str, image_type: Union[ProfileImageType, None] = None) -> str:
        """Upload an image file to the profile pictures bucket and return the public URL"""
        pass
    
    @abstractmethod
    async def delete(self, object_key: str) -> None:
        """Delete an image by its object key from the profile pictures bucket"""
        pass
    
    @abstractmethod
    def extract_key_from_url(self, url: str) -> str:
        """Extract object key from a full URL"""
        pass
    
    @abstractmethod
    async def get_upload_url(self, filename: str, image_type: ProfileImageType) -> str:
        """Generate a presigned upload URL for direct client upload"""
        pass