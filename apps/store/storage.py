"""
S3 Storage configuration for Store app file uploads
SOP requirement: Use S3 for storing quotation attachments and other files
"""
from django.conf import settings

# Check if django-storages is installed
try:
    from storages.backends.s3boto3 import S3Boto3Storage

    class S3MediaStorage(S3Boto3Storage):
        """
        Custom S3 storage for store app media files
        """
        location = 'store'
        file_overwrite = False
        default_acl = 'private'

    # Export the storage class to use in models
    store_file_storage = S3MediaStorage() if getattr(settings, 'USE_S3', False) else None

except ImportError:
    # If django-storages not installed, use default storage
    store_file_storage = None
