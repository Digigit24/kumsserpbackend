"""
S3 file upload utilities for AWS S3 integration.
Handles file uploads, validation, and URL generation.
"""
import os
import uuid
import mimetypes
from datetime import datetime
from typing import List, Dict, Any, Optional
from decouple import config
import boto3
from botocore.exceptions import ClientError, BotoCoreError
from django.core.exceptions import ValidationError


class S3FileUploader:
    """
    Service class for handling file uploads to AWS S3.

    Supported file types: documents (pdf, doc, docx) and images (jpg, jpeg, png, gif)
    """

    # Allowed file extensions for documents and images
    ALLOWED_EXTENSIONS = {
        'documents': ['.pdf', '.doc', '.docx', '.txt', '.xls', '.xlsx', '.ppt', '.pptx'],
        'images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg']
    }

    # MIME types mapping
    ALLOWED_MIME_TYPES = {
        # Documents
        'application/pdf': '.pdf',
        'application/msword': '.doc',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document': '.docx',
        'text/plain': '.txt',
        'application/vnd.ms-excel': '.xls',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': '.xlsx',
        'application/vnd.ms-powerpoint': '.ppt',
        'application/vnd.openxmlformats-officedocument.presentationml.presentation': '.pptx',
        # Images
        'image/jpeg': '.jpg',
        'image/jpg': '.jpg',
        'image/png': '.png',
        'image/gif': '.gif',
        'image/bmp': '.bmp',
        'image/webp': '.webp',
        'image/svg+xml': '.svg',
    }

    def __init__(self):
        """Initialize S3 client with credentials from environment variables."""
        self.aws_access_key_id = config('AWS_ACCESS_KEY_ID', default='')
        self.aws_secret_access_key = config('AWS_SECRET_ACCESS_KEY', default='')
        self.bucket_name = config('AWS_STORAGE_BUCKET_NAME', default='')
        self.region_name = config('AWS_S3_REGION_NAME', default='ap-south-1')
        self.prefix = config('AWS_S3_PREFIX', default='college/')

        if not all([self.aws_access_key_id, self.aws_secret_access_key, self.bucket_name]):
            raise ValueError("AWS S3 credentials not properly configured in environment variables")

        # Initialize S3 client
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key,
            region_name=self.region_name
        )

    def validate_file(self, file) -> tuple[bool, Optional[str]]:
        """
        Validate uploaded file for type and extension.

        Args:
            file: Django UploadedFile object

        Returns:
            tuple: (is_valid, error_message)
        """
        if not file:
            return False, "No file provided"

        # Get file extension
        file_name = file.name.lower()
        file_ext = os.path.splitext(file_name)[1]

        # Check if extension is allowed
        all_allowed_extensions = (
            self.ALLOWED_EXTENSIONS['documents'] +
            self.ALLOWED_EXTENSIONS['images']
        )

        if file_ext not in all_allowed_extensions:
            return False, f"File type '{file_ext}' not allowed. Allowed types: {', '.join(all_allowed_extensions)}"

        # Validate MIME type
        content_type = file.content_type
        if content_type not in self.ALLOWED_MIME_TYPES:
            return False, f"Invalid file MIME type: {content_type}"

        return True, None

    def generate_unique_filename(self, original_filename: str, folder: str = '') -> str:
        """
        Generate a unique filename with timestamp and UUID.

        Args:
            original_filename: Original name of the file
            folder: Optional subfolder path

        Returns:
            str: Unique S3 key path
        """
        # Get file extension
        file_ext = os.path.splitext(original_filename)[1].lower()

        # Generate unique filename: timestamp_uuid_originalname
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_id = str(uuid.uuid4())[:8]

        # Clean original filename (remove extension, sanitize)
        base_name = os.path.splitext(original_filename)[0]
        base_name = "".join(c for c in base_name if c.isalnum() or c in (' ', '-', '_')).strip()
        base_name = base_name.replace(' ', '_')[:50]  # Limit length

        unique_filename = f"{timestamp}_{unique_id}_{base_name}{file_ext}"

        # Build full S3 key with prefix and folder
        if folder:
            s3_key = f"{self.prefix}{folder}/{unique_filename}"
        else:
            s3_key = f"{self.prefix}{unique_filename}"

        return s3_key

    def upload_file(
        self,
        file,
        folder: str = 'uploads',
        metadata: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Upload a single file to S3.

        Args:
            file: Django UploadedFile object
            folder: Subfolder in S3 bucket (default: 'uploads')
            metadata: Optional metadata dictionary

        Returns:
            dict: Upload result containing file_url, s3_key, filename, size

        Raises:
            ValidationError: If file validation fails
            Exception: If S3 upload fails
        """
        # Validate file
        is_valid, error_message = self.validate_file(file)
        if not is_valid:
            raise ValidationError(error_message)

        # Generate unique filename
        s3_key = self.generate_unique_filename(file.name, folder)

        try:
            # Prepare upload parameters
            extra_args = {
                'ContentType': file.content_type,
            }

            # Add metadata if provided
            if metadata:
                extra_args['Metadata'] = metadata

            # Upload file to S3
            self.s3_client.upload_fileobj(
                file,
                self.bucket_name,
                s3_key,
                ExtraArgs=extra_args
            )

            # Generate file URL
            file_url = f"https://{self.bucket_name}.s3.{self.region_name}.amazonaws.com/{s3_key}"

            return {
                'success': True,
                'file_url': file_url,
                's3_key': s3_key,
                'filename': file.name,
                'size': file.size,
                'content_type': file.content_type
            }

        except (ClientError, BotoCoreError) as e:
            raise Exception(f"Failed to upload file to S3: {str(e)}")

    def upload_multiple_files(
        self,
        files: List,
        folder: str = 'uploads',
        metadata: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Upload multiple files to S3 (max 5 files at a time).

        Args:
            files: List of Django UploadedFile objects
            folder: Subfolder in S3 bucket (default: 'uploads')
            metadata: Optional metadata dictionary

        Returns:
            dict: Results with successful uploads and errors
        """
        if not files:
            raise ValidationError("No files provided")

        if len(files) > 5:
            raise ValidationError("Maximum 5 files allowed per upload")

        results = {
            'successful_uploads': [],
            'failed_uploads': [],
            'total_files': len(files),
            'success_count': 0,
            'error_count': 0
        }

        for file in files:
            try:
                upload_result = self.upload_file(file, folder, metadata)
                results['successful_uploads'].append(upload_result)
                results['success_count'] += 1
            except (ValidationError, Exception) as e:
                results['failed_uploads'].append({
                    'filename': file.name if hasattr(file, 'name') else 'unknown',
                    'error': str(e)
                })
                results['error_count'] += 1

        return results

    def delete_file(self, s3_key: str) -> bool:
        """
        Delete a file from S3.

        Args:
            s3_key: S3 key of the file to delete

        Returns:
            bool: True if deletion successful, False otherwise
        """
        try:
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=s3_key
            )
            return True
        except (ClientError, BotoCoreError) as e:
            print(f"Error deleting file from S3: {str(e)}")
            return False

    def generate_presigned_url(self, s3_key: str, expiration: int = 3600) -> Optional[str]:
        """
        Generate a presigned URL for temporary file access.

        Args:
            s3_key: S3 key of the file
            expiration: URL expiration time in seconds (default: 1 hour)

        Returns:
            str: Presigned URL or None if generation fails
        """
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': s3_key
                },
                ExpiresIn=expiration
            )
            return url
        except (ClientError, BotoCoreError) as e:
            print(f"Error generating presigned URL: {str(e)}")
            return None
