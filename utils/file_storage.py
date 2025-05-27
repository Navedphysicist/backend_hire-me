import os
from fastapi import UploadFile
import shutil
from typing import Optional
import cloudinary
import cloudinary.uploader
from pathlib import Path
from core.config import settings

# Configure Cloudinary
if os.getenv('VERCEL'):
    cloudinary.config(
        cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
        api_key=os.getenv('CLOUDINARY_API_KEY'),
        api_secret=os.getenv('CLOUDINARY_API_SECRET')
    )

def save_upload_file(upload_file: UploadFile, filename: str,folder: Optional[str] = "",resource_type:Optional[str]= ""):
    path = Path(filename)
    public_id = path.stem

    if settings.VERCEL:

        result = cloudinary.uploader.upload(
            upload_file.file,
            public_id=public_id,folder=f"static/{folder}",
            resource_type=resource_type)
        return result["secure_url"]
    else:
        directory = Path("static")/folder 
        directory.mkdir(parents=True, exist_ok=True)
        file_path = directory / path.name
        with open(file_path,"wb") as buffer:
            shutil.copyfileobj(upload_file.file, buffer)
        return str(file_path)