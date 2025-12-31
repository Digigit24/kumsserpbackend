# AWS S3 File Upload API Documentation

## Overview

This API provides endpoints for uploading, managing, and deleting files in AWS S3 storage. All files are uploaded to the S3 bucket `main-bucket-digitech` in the `ap-south-1` region with the prefix `college/`.

## Features

- ✅ Upload single file (documents and images)
- ✅ Upload multiple files (up to 5 at once)
- ✅ Each file gets a unique URL
- ✅ No file size limits
- ✅ Supports documents: PDF, DOC, DOCX, TXT, XLS, XLSX, PPT, PPTX
- ✅ Supports images: JPG, JPEG, PNG, GIF, BMP, WEBP, SVG
- ✅ Delete files from S3
- ✅ Generate presigned URLs for temporary access
- ✅ Automatic file validation
- ✅ Metadata tracking (uploaded by, username, description)

## Base URL

```
http://localhost:8000/api/core/upload/
```

## Authentication

All endpoints require authentication using Token Authentication.

**Header Required:**
```
Authorization: Token your-auth-token-here
```

---

## API Endpoints

### 1. Upload Single File

Upload a single document or image file to S3.

**Endpoint:** `POST /api/core/upload/single/`

**Request:**
- Method: `POST`
- Content-Type: `multipart/form-data`

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| file | File | Yes | The file to upload (document or image) |
| folder | String | No | Subfolder in S3 bucket (default: 'uploads') |
| description | String | No | Optional description/metadata |

**Example Request (cURL):**
```bash
curl -X POST http://localhost:8000/api/core/upload/single/ \
  -H "Authorization: Token your-auth-token" \
  -F "file=@/path/to/document.pdf" \
  -F "folder=student_documents" \
  -F "description=Student admission document"
```

**Example Request (JavaScript/Fetch):**
```javascript
const formData = new FormData();
formData.append('file', fileInput.files[0]);
formData.append('folder', 'student_documents');
formData.append('description', 'Student admission document');

fetch('http://localhost:8000/api/core/upload/single/', {
  method: 'POST',
  headers: {
    'Authorization': 'Token your-auth-token'
  },
  body: formData
})
.then(response => response.json())
.then(data => console.log(data));
```

**Success Response (200 OK):**
```json
{
  "success": true,
  "file_url": "https://main-bucket-digitech.s3.ap-south-1.amazonaws.com/college/student_documents/20251231_123456_document.pdf",
  "s3_key": "college/student_documents/20251231_123456_document.pdf",
  "filename": "document.pdf",
  "size": 102400,
  "content_type": "application/pdf"
}
```

**Error Response (400 Bad Request):**
```json
{
  "error": "File type '.exe' not allowed. Allowed types: .pdf, .doc, .docx, ..."
}
```

---

### 2. Upload Multiple Files

Upload up to 5 files at once. Each file gets a unique URL.

**Endpoint:** `POST /api/core/upload/multiple/`

**Request:**
- Method: `POST`
- Content-Type: `multipart/form-data`

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| files | File[] | Yes | Array of files to upload (max 5) |
| folder | String | No | Subfolder in S3 bucket (default: 'uploads') |
| description | String | No | Optional description/metadata |

**Example Request (cURL):**
```bash
curl -X POST http://localhost:8000/api/core/upload/multiple/ \
  -H "Authorization: Token your-auth-token" \
  -F "files=@/path/to/file1.pdf" \
  -F "files=@/path/to/file2.jpg" \
  -F "files=@/path/to/file3.docx" \
  -F "folder=fee_receipts" \
  -F "description=Monthly fee receipts"
```

**Example Request (JavaScript/Fetch):**
```javascript
const formData = new FormData();

// Add multiple files
for (let i = 0; i < fileInput.files.length; i++) {
  formData.append('files', fileInput.files[i]);
}

formData.append('folder', 'fee_receipts');
formData.append('description', 'Monthly fee receipts');

fetch('http://localhost:8000/api/core/upload/multiple/', {
  method: 'POST',
  headers: {
    'Authorization': 'Token your-auth-token'
  },
  body: formData
})
.then(response => response.json())
.then(data => console.log(data));
```

**Success Response (200 OK):**
```json
{
  "successful_uploads": [
    {
      "success": true,
      "file_url": "https://main-bucket-digitech.s3.ap-south-1.amazonaws.com/college/fee_receipts/20251231_123456_file1.pdf",
      "s3_key": "college/fee_receipts/20251231_123456_file1.pdf",
      "filename": "file1.pdf",
      "size": 102400,
      "content_type": "application/pdf"
    },
    {
      "success": true,
      "file_url": "https://main-bucket-digitech.s3.ap-south-1.amazonaws.com/college/fee_receipts/20251231_123457_file2.jpg",
      "s3_key": "college/fee_receipts/20251231_123457_file2.jpg",
      "filename": "file2.jpg",
      "size": 204800,
      "content_type": "image/jpeg"
    }
  ],
  "failed_uploads": [],
  "total_files": 2,
  "success_count": 2,
  "error_count": 0
}
```

**Partial Success Response (200 OK):**
```json
{
  "successful_uploads": [
    {
      "success": true,
      "file_url": "https://main-bucket-digitech.s3.ap-south-1.amazonaws.com/college/uploads/20251231_123456_file1.pdf",
      "s3_key": "college/uploads/20251231_123456_file1.pdf",
      "filename": "file1.pdf",
      "size": 102400,
      "content_type": "application/pdf"
    }
  ],
  "failed_uploads": [
    {
      "filename": "badfile.exe",
      "error": "File type '.exe' not allowed. Allowed types: .pdf, .doc, ..."
    }
  ],
  "total_files": 2,
  "success_count": 1,
  "error_count": 1
}
```

---

### 3. Delete File

Delete a file from S3 using its S3 key.

**Endpoint:** `DELETE /api/core/upload/delete/`

**Request:**
- Method: `DELETE`
- Content-Type: `application/json`

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| s3_key | String | Yes | S3 key of the file to delete |

**Example Request (cURL):**
```bash
curl -X DELETE http://localhost:8000/api/core/upload/delete/ \
  -H "Authorization: Token your-auth-token" \
  -H "Content-Type: application/json" \
  -d '{"s3_key": "college/uploads/20251231_123456_document.pdf"}'
```

**Example Request (JavaScript/Fetch):**
```javascript
fetch('http://localhost:8000/api/core/upload/delete/', {
  method: 'DELETE',
  headers: {
    'Authorization': 'Token your-auth-token',
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    s3_key: 'college/uploads/20251231_123456_document.pdf'
  })
})
.then(response => response.json())
.then(data => console.log(data));
```

**Success Response (200 OK):**
```json
{
  "message": "File deleted successfully",
  "s3_key": "college/uploads/20251231_123456_document.pdf"
}
```

---

### 4. Generate Presigned URL

Generate a temporary presigned URL for accessing a file without making it public.

**Endpoint:** `POST /api/core/upload/presigned-url/`

**Request:**
- Method: `POST`
- Content-Type: `application/json`

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| s3_key | String | Yes | S3 key of the file |
| expiration | Integer | No | URL expiration in seconds (default: 3600 = 1 hour, max: 604800 = 7 days) |

**Example Request (cURL):**
```bash
curl -X POST http://localhost:8000/api/core/upload/presigned-url/ \
  -H "Authorization: Token your-auth-token" \
  -H "Content-Type: application/json" \
  -d '{
    "s3_key": "college/uploads/20251231_123456_document.pdf",
    "expiration": 7200
  }'
```

**Example Request (JavaScript/Fetch):**
```javascript
fetch('http://localhost:8000/api/core/upload/presigned-url/', {
  method: 'POST',
  headers: {
    'Authorization': 'Token your-auth-token',
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    s3_key: 'college/uploads/20251231_123456_document.pdf',
    expiration: 7200
  })
})
.then(response => response.json())
.then(data => console.log(data));
```

**Success Response (200 OK):**
```json
{
  "presigned_url": "https://main-bucket-digitech.s3.ap-south-1.amazonaws.com/college/uploads/20251231_123456_document.pdf?AWSAccessKeyId=...&Signature=...&Expires=...",
  "s3_key": "college/uploads/20251231_123456_document.pdf",
  "expiration_seconds": 7200
}
```

---

## Supported File Types

### Documents
- `.pdf` - PDF documents
- `.doc` - Microsoft Word (old format)
- `.docx` - Microsoft Word (new format)
- `.txt` - Text files
- `.xls` - Microsoft Excel (old format)
- `.xlsx` - Microsoft Excel (new format)
- `.ppt` - Microsoft PowerPoint (old format)
- `.pptx` - Microsoft PowerPoint (new format)

### Images
- `.jpg`, `.jpeg` - JPEG images
- `.png` - PNG images
- `.gif` - GIF images
- `.bmp` - Bitmap images
- `.webp` - WebP images
- `.svg` - SVG vector images

---

## Common Use Cases

### Upload Student Documents
```bash
POST /api/core/upload/single/
folder: "student_documents"
file: admission_certificate.pdf
```

### Upload Fee Receipts
```bash
POST /api/core/upload/multiple/
folder: "fee_receipts"
files: [receipt1.pdf, receipt2.pdf, receipt3.pdf]
```

### Upload Student Photos
```bash
POST /api/core/upload/single/
folder: "student_photos"
file: student_123.jpg
```

### Upload Teacher Documents
```bash
POST /api/core/upload/multiple/
folder: "teacher_documents"
files: [resume.pdf, certificates.pdf, id_proof.jpg]
```

### Upload Exam Papers
```bash
POST /api/core/upload/single/
folder: "exam_papers"
file: mathematics_midterm.pdf
```

---

## Error Codes

| Status Code | Description |
|-------------|-------------|
| 200 | Success |
| 400 | Bad Request - Invalid data or file type |
| 401 | Unauthorized - Missing or invalid token |
| 500 | Internal Server Error - S3 upload failed |

---

## Important Notes

1. **File Size**: No size limits are enforced on the backend
2. **Max Files**: Maximum 5 files per upload in the multiple upload endpoint
3. **File Names**: Original filenames are preserved but sanitized and made unique with timestamps
4. **S3 Structure**: Files are organized as `college/{folder}/{timestamp}_{uuid}_{filename}`
5. **Metadata**: Each upload includes metadata about the uploader (user ID, username, description)
6. **Authentication**: All endpoints require valid authentication token
7. **CORS**: Make sure CORS is properly configured for your frontend domain

---

## Frontend Integration Example (React)

```javascript
import React, { useState } from 'react';

function FileUpload() {
  const [files, setFiles] = useState([]);
  const [uploading, setUploading] = useState(false);

  const handleUpload = async () => {
    setUploading(true);

    const formData = new FormData();
    files.forEach(file => {
      formData.append('files', file);
    });
    formData.append('folder', 'student_documents');
    formData.append('description', 'Student admission documents');

    try {
      const response = await fetch('http://localhost:8000/api/core/upload/multiple/', {
        method: 'POST',
        headers: {
          'Authorization': `Token ${localStorage.getItem('authToken')}`
        },
        body: formData
      });

      const data = await response.json();
      console.log('Upload results:', data);

      // Handle successful uploads
      data.successful_uploads.forEach(upload => {
        console.log('File URL:', upload.file_url);
      });
    } catch (error) {
      console.error('Upload failed:', error);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div>
      <input
        type="file"
        multiple
        onChange={(e) => setFiles(Array.from(e.target.files))}
        accept=".pdf,.doc,.docx,.jpg,.jpeg,.png"
      />
      <button onClick={handleUpload} disabled={uploading}>
        {uploading ? 'Uploading...' : 'Upload Files'}
      </button>
    </div>
  );
}

export default FileUpload;
```

---

## Security Configuration

The S3 credentials are stored securely in the `.env` file:

```env
AWS_ACCESS_KEY_ID=your-aws-access-key-id
AWS_SECRET_ACCESS_KEY=your-aws-secret-access-key
AWS_STORAGE_BUCKET_NAME=main-bucket-digitech
AWS_S3_REGION_NAME=ap-south-1
AWS_S3_PREFIX=college/
```

**⚠️ NEVER commit the `.env` file to version control!**

---

## Testing the API

You can test the API using:

1. **Postman**: Import the endpoints and test with your files
2. **cURL**: Use the command-line examples provided above
3. **Django REST Framework UI**: Visit the endpoints in your browser (when authenticated)
4. **Frontend Integration**: Use the React example provided

---

## Support

For issues or questions, please contact the development team or create an issue in the project repository.
