import asyncio
import boto3
import mimetypes
import os
from typing import BinaryIO
from botocore.exceptions import ClientError

from src.domain.ports.image_storage import ImageStorage, ProfileImageType


class MinioImageStorage(ImageStorage):
    """Minio implementation for profile images storage"""
    
    def __init__(self):
        # Single bucket for profile images (both profile and background pictures)
        self.bucket_name = os.getenv("MINIO_BUCKET_PP", "profile-pictures")
        
        # Minio configuration
        self.region = os.getenv("MINIO_REGION", "us-east-1")
        self.public_url = os.getenv("MINIO_PUBLIC_URL", "http://localhost:9000")
        
        # S3 client
        self.s3_client = boto3.client(
            "s3",
            endpoint_url=os.getenv("MINIO_ENDPOINT", "http://localhost:9000"),
            aws_access_key_id=os.getenv("MINIO_ACCESS_KEY"),
            aws_secret_access_key=os.getenv("MINIO_SECRET_KEY"),
            region_name=self.region,
        )
    
    def _guess_mime_type(self, filename: str) -> str:
        """Guess MIME type from filename"""
        mime, _ = mimetypes.guess_type(filename)
        return mime or "application/octet-stream"

    def extract_key_from_url(self, url: str) -> str:
        """Extract object key from full URL"""
        return url.split(f"{self.bucket_name}/")[-1]

    async def upload(self, file: BinaryIO, filename: str, image_type: ProfileImageType) -> str:
        """Upload file to Minio bucket and return public URL"""
        try:
            # Run the synchronous boto3 operation in a thread pool
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                lambda: self.s3_client.upload_fileobj(
                    Fileobj=file,
                    Bucket=self.bucket_name,
                    Key=filename,
                    ExtraArgs={
                        "ContentType": self._guess_mime_type(filename),
                        "ContentDisposition": "inline"
                    }
                )
            )
            
            # Return the public URL
            return f"{self.public_url}/{self.bucket_name}/{filename}"
            
        except ClientError as e:
            raise Exception(f"Failed to upload {image_type.value}: {str(e)}")

    async def delete(self, object_key: str) -> None:
        """Delete object from Minio bucket"""
        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                lambda: self.s3_client.delete_object(
                    Bucket=self.bucket_name, 
                    Key=object_key
                )
            )
        except ClientError as e:
            # Don't raise exception if object doesn't exist
            if e.response['Error']['Code'] != 'NoSuchKey':
                raise Exception(f"Failed to delete image: {str(e)}")

    async def get_upload_url(self, filename: str, image_type: ProfileImageType) -> str:
        """Generate presigned URL for direct upload"""
        try:
            loop = asyncio.get_event_loop()
            url = await loop.run_in_executor(
                None,
                lambda: self.s3_client.generate_presigned_url(
                    'put_object',
                    Params={
                        'Bucket': self.bucket_name,
                        'Key': filename,
                        'ContentType': self._guess_mime_type(filename)
                    },
                    ExpiresIn=3600  # 1 hour
                )
            )
            return url
        except ClientError as e:
            raise Exception(f"Failed to generate upload URL for {image_type.value}: {str(e)}")