"""
Serializers for file upload functionality.
Handles validation and data structure for S3 file uploads.
"""
from rest_framework import serializers


class SingleFileUploadSerializer(serializers.Serializer):
    """
    Serializer for single file upload to S3.
    """
    file = serializers.FileField(
        required=True,
        help_text="File to upload (documents: pdf, doc, docx, etc. | images: jpg, png, gif, etc.)"
    )
    folder = serializers.CharField(
        required=False,
        default='uploads',
        max_length=100,
        help_text="Subfolder in S3 bucket (optional, default: 'uploads')"
    )
    description = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=500,
        help_text="Optional description/metadata for the file"
    )

    def validate_file(self, value):
        """Validate that a file is provided."""
        if not value:
            raise serializers.ValidationError("No file was submitted.")
        return value


class MultipleFileUploadSerializer(serializers.Serializer):
    """
    Serializer for multiple file uploads to S3 (max 5 files).
    """
    files = serializers.ListField(
        child=serializers.FileField(),
        required=True,
        max_length=5,
        min_length=1,
        help_text="List of files to upload (max 5 files)"
    )
    folder = serializers.CharField(
        required=False,
        default='uploads',
        max_length=100,
        help_text="Subfolder in S3 bucket (optional, default: 'uploads')"
    )
    description = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=500,
        help_text="Optional description/metadata for the files"
    )

    def validate_files(self, value):
        """Validate file list."""
        if not value:
            raise serializers.ValidationError("No files were submitted.")

        if len(value) > 5:
            raise serializers.ValidationError("Maximum 5 files allowed per upload.")

        return value


class FileUploadResponseSerializer(serializers.Serializer):
    """
    Serializer for file upload response.
    """
    success = serializers.BooleanField(read_only=True)
    file_url = serializers.URLField(read_only=True)
    s3_key = serializers.CharField(read_only=True)
    filename = serializers.CharField(read_only=True)
    size = serializers.IntegerField(read_only=True)
    content_type = serializers.CharField(read_only=True)


class MultipleFileUploadResponseSerializer(serializers.Serializer):
    """
    Serializer for multiple file upload response.
    """
    successful_uploads = FileUploadResponseSerializer(many=True, read_only=True)
    failed_uploads = serializers.ListField(read_only=True)
    total_files = serializers.IntegerField(read_only=True)
    success_count = serializers.IntegerField(read_only=True)
    error_count = serializers.IntegerField(read_only=True)


class FileDeleteSerializer(serializers.Serializer):
    """
    Serializer for file deletion from S3.
    """
    s3_key = serializers.CharField(
        required=True,
        max_length=500,
        help_text="S3 key of the file to delete"
    )

    def validate_s3_key(self, value):
        """Validate S3 key."""
        if not value:
            raise serializers.ValidationError("S3 key is required.")
        return value


class PresignedUrlSerializer(serializers.Serializer):
    """
    Serializer for generating presigned URLs.
    """
    s3_key = serializers.CharField(
        required=True,
        max_length=500,
        help_text="S3 key of the file"
    )
    expiration = serializers.IntegerField(
        required=False,
        default=3600,
        min_value=60,
        max_value=604800,  # Max 7 days
        help_text="URL expiration time in seconds (default: 3600 = 1 hour)"
    )

    def validate_s3_key(self, value):
        """Validate S3 key."""
        if not value:
            raise serializers.ValidationError("S3 key is required.")
        return value
