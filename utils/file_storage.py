import os
from fastapi import UploadFile
import shutil
from typing import Optional
import cloudinary
import cloudinary.uploader

# Configure Cloudinary
if os.getenv('VERCEL'):
    cloudinary.config(
        cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
        api_key=os.getenv('CLOUDINARY_API_KEY'),
        api_secret=os.getenv('CLOUDINARY_API_SECRET')
    )

def get_file_url(filename: str) -> str:
    """Get the URL for a file based on the environment"""
    if os.getenv("VERCEL"):
        # In production, URL will be from Cloudinary
        return filename
    else:
        # In local development, serve from static directory
        return f"/static/{filename}"

def save_upload_file(upload_file: UploadFile, filename: str,folder: Optional[str] = "") -> Optional[str]:
    """Save an uploaded file and return its URL"""
    filename_without_path = os.path.basename(filename)
    public_id = os.path.splitext(filename_without_path)[0]
    if os.getenv("VERCEL"):
        # Upload to Cloudinary in production
        result = cloudinary.uploader.upload(upload_file.file, public_id=public_id,folder=f"static/{folder}")
        return result["secure_url"]
    else:
        # Local development: save to static directory
        directory = os.path.join("static", os.path.dirname(filename))
        os.makedirs(directory, exist_ok=True)
        
        file_path = os.path.join("static", filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(upload_file.file, buffer)
        return get_file_url(filename)
