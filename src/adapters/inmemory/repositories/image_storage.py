from typing import BinaryIO, Union
from src.domain.ports.image_storage import ImageStorage, ProfileImageType

class InMemoryImageStorage(ImageStorage):
    """In-memory implementation for images testing"""
    
    def __init__(self):
        self._files: dict[str, bytes] = {}
        self._upload_urls: dict[str, str] = {}
    
    async def upload(self, file: BinaryIO, filename: str, image_type: Union[ProfileImageType, None] = None) -> str:
        """Store file content in memory and return mock URL"""
        content = file.read()
        self._files[filename] = content
        
        if image_type and isinstance(image_type, ProfileImageType):
            return f"http://localhost/mock/profile-pictures/{filename}"
        else:
            return f"http://localhost/mock/daily-checkups/{filename}"
    
    async def delete(self, object_key: str) -> None:
        """Remove file from memory storage"""
        self._files.pop(object_key, None)
    
    def extract_key_from_url(self, url: str) -> str:
        """Extract filename from mock URL"""
        return url.split("/")[-1]
    
    async def get_upload_url(self, filename: str, image_type: Union[ProfileImageType, None] = None) -> str:
        """Generate mock presigned upload URL"""
        if image_type and isinstance(image_type, ProfileImageType):
            url = f"http://localhost/mock/upload/profile-pictures/{filename}"
        else:
            url = f"http://localhost/mock/upload/daily-checkups/{filename}"
        self._upload_urls[filename] = url
        return url
    
    def get_stored_files(self) -> dict[str, bytes]:
        """Get all stored files (for testing)"""
        return self._files.copy()
    
    def file_exists(self, filename: str) -> bool:
        """Check if file exists in storage (for testing)"""
        return filename in self._files