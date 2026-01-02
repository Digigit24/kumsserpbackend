"""
S3 Storage configuration for Store app file uploads
Uses the same S3 credentials and bucket as the rest of the application
Stores files in: main-bucket-digitech/college/store/
"""
from decouple import config
from django.core.files.storage import FileSystemStorage

try:
    from storages.backends.s3boto3 import S3Boto3Storage

    class StoreS3Storage(S3Boto3Storage):
        """
        Custom S3 storage for store app files (quotations, POs, GRNs, invoices, etc.)
        Uses the same bucket and credentials as the core app

        Files will be stored at: s3://main-bucket-digitech/college/store/
        """
        # Store files in college/store/ subfolder (same prefix as core app + 'store')
        location = config('AWS_S3_PREFIX', default='college/') + 'store'

        # File handling settings
        file_overwrite = False  # Always create new files with unique names
        default_acl = 'private'  # Keep files private (not publicly accessible)

    # Check if S3 credentials are available
    use_s3 = bool(
        config('AWS_ACCESS_KEY_ID', default='') and
        config('AWS_SECRET_ACCESS_KEY', default='') and
        config('AWS_STORAGE_BUCKET_NAME', default='')
    )

    # Use S3 storage if credentials are configured, otherwise fall back to local storage
    if use_s3:
        store_file_storage = StoreS3Storage()
    else:
        # Fallback to local file storage for development
        store_file_storage = FileSystemStorage()

except ImportError:
    # If django-storages is not installed, use default file storage
    store_file_storage = FileSystemStorage()
