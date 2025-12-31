"""
API views for S3 file upload functionality.
Provides endpoints for uploading, deleting, and managing files in AWS S3.
"""
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from django.core.exceptions import ValidationError

from .s3_utils import S3FileUploader
from .upload_serializers import (
    SingleFileUploadSerializer,
    MultipleFileUploadSerializer,
    FileUploadResponseSerializer,
    MultipleFileUploadResponseSerializer,
    FileDeleteSerializer,
    PresignedUrlSerializer
)


class SingleFileUploadView(APIView):
    """
    API endpoint for uploading a single file to S3.

    POST /api/upload/single/
    - Upload a single document or image file
    - Returns file URL and metadata
    """
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    @extend_schema(
        request=SingleFileUploadSerializer,
        responses={
            200: FileUploadResponseSerializer,
            400: {'description': 'Validation error or upload failed'}
        },
        description="Upload a single file (document or image) to AWS S3. Returns the file URL and metadata.",
        examples=[
            OpenApiExample(
                'Success Response',
                value={
                    'success': True,
                    'file_url': 'https://main-bucket-digitech.s3.ap-south-1.amazonaws.com/college/uploads/20251231_a1b2c3d4_mydocument.pdf',
                    's3_key': 'college/uploads/20251231_a1b2c3d4_mydocument.pdf',
                    'filename': 'mydocument.pdf',
                    'size': 102400,
                    'content_type': 'application/pdf'
                },
                response_only=True
            )
        ]
    )
    def post(self, request):
        """Handle single file upload."""
        serializer = SingleFileUploadSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                {'error': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        file = serializer.validated_data['file']
        folder = serializer.validated_data.get('folder', 'uploads')
        description = serializer.validated_data.get('description', '')

        # Prepare metadata
        metadata = {
            'uploaded_by': str(request.user.id),
            'username': request.user.username,
        }
        if description:
            metadata['description'] = description

        try:
            # Initialize S3 uploader
            uploader = S3FileUploader()

            # Upload file
            result = uploader.upload_file(file, folder, metadata)

            return Response(result, status=status.HTTP_200_OK)

        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': f'Upload failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class MultipleFileUploadView(APIView):
    """
    API endpoint for uploading multiple files to S3.

    POST /api/upload/multiple/
    - Upload up to 5 files at once
    - Each file gets a unique URL
    - Returns results for successful and failed uploads
    """
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    @extend_schema(
        request=MultipleFileUploadSerializer,
        responses={
            200: MultipleFileUploadResponseSerializer,
            400: {'description': 'Validation error or upload failed'}
        },
        description="Upload multiple files (max 5) to AWS S3. Each file gets a unique URL. Returns results for all uploads.",
        examples=[
            OpenApiExample(
                'Success Response',
                value={
                    'successful_uploads': [
                        {
                            'success': True,
                            'file_url': 'https://main-bucket-digitech.s3.ap-south-1.amazonaws.com/college/uploads/20251231_a1b2c3d4_file1.pdf',
                            's3_key': 'college/uploads/20251231_a1b2c3d4_file1.pdf',
                            'filename': 'file1.pdf',
                            'size': 102400,
                            'content_type': 'application/pdf'
                        },
                        {
                            'success': True,
                            'file_url': 'https://main-bucket-digitech.s3.ap-south-1.amazonaws.com/college/uploads/20251231_b2c3d4e5_file2.jpg',
                            's3_key': 'college/uploads/20251231_b2c3d4e5_file2.jpg',
                            'filename': 'file2.jpg',
                            'size': 204800,
                            'content_type': 'image/jpeg'
                        }
                    ],
                    'failed_uploads': [],
                    'total_files': 2,
                    'success_count': 2,
                    'error_count': 0
                },
                response_only=True
            )
        ]
    )
    def post(self, request):
        """Handle multiple file uploads."""
        serializer = MultipleFileUploadSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                {'error': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        files = serializer.validated_data['files']
        folder = serializer.validated_data.get('folder', 'uploads')
        description = serializer.validated_data.get('description', '')

        # Prepare metadata
        metadata = {
            'uploaded_by': str(request.user.id),
            'username': request.user.username,
        }
        if description:
            metadata['description'] = description

        try:
            # Initialize S3 uploader
            uploader = S3FileUploader()

            # Upload files
            results = uploader.upload_multiple_files(files, folder, metadata)

            return Response(results, status=status.HTTP_200_OK)

        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': f'Upload failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class FileDeleteView(APIView):
    """
    API endpoint for deleting a file from S3.

    DELETE /api/upload/delete/
    - Delete a file using its S3 key
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=FileDeleteSerializer,
        responses={
            200: {'description': 'File deleted successfully'},
            400: {'description': 'Validation error'},
            500: {'description': 'Deletion failed'}
        },
        description="Delete a file from AWS S3 using its S3 key."
    )
    def delete(self, request):
        """Handle file deletion."""
        serializer = FileDeleteSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                {'error': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        s3_key = serializer.validated_data['s3_key']

        try:
            # Initialize S3 uploader
            uploader = S3FileUploader()

            # Delete file
            success = uploader.delete_file(s3_key)

            if success:
                return Response(
                    {'message': 'File deleted successfully', 's3_key': s3_key},
                    status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {'error': 'Failed to delete file'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        except Exception as e:
            return Response(
                {'error': f'Deletion failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class PresignedUrlView(APIView):
    """
    API endpoint for generating presigned URLs for temporary file access.

    POST /api/upload/presigned-url/
    - Generate a temporary URL for accessing a file
    - URL expires after specified time (default: 1 hour)
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=PresignedUrlSerializer,
        responses={
            200: {'description': 'Presigned URL generated successfully'},
            400: {'description': 'Validation error'},
            500: {'description': 'URL generation failed'}
        },
        description="Generate a presigned URL for temporary access to a file in S3."
    )
    def post(self, request):
        """Generate presigned URL."""
        serializer = PresignedUrlSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                {'error': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        s3_key = serializer.validated_data['s3_key']
        expiration = serializer.validated_data.get('expiration', 3600)

        try:
            # Initialize S3 uploader
            uploader = S3FileUploader()

            # Generate presigned URL
            url = uploader.generate_presigned_url(s3_key, expiration)

            if url:
                return Response(
                    {
                        'presigned_url': url,
                        's3_key': s3_key,
                        'expiration_seconds': expiration
                    },
                    status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {'error': 'Failed to generate presigned URL'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        except Exception as e:
            return Response(
                {'error': f'URL generation failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
