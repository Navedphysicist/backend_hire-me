import os
from fastapi import UploadFile
import shutil
from typing import Optional
import base64

def get_file_url(filename: str) -> str:
    """Get the URL for a file based on the environment"""
    if os.environ.get("VERCEL"):
        # For now, return a placeholder URL that indicates it's a temporary solution
        return f"/temp/{filename}"
    else:
        # In local development, serve from static directory
        return f"/static/{filename}"

async def save_upload_file(upload_file: UploadFile, filename: str) -> Optional[str]:
    """Save an uploaded file and return its URL"""
    if os.environ.get("VERCEL"):
        # For now, we'll return a temporary URL
        # In production, you should implement proper file storage
        return get_file_url(filename)
    else:
        # Local development: save to static directory
        directory = os.path.join("static", os.path.dirname(filename))
        os.makedirs(directory, exist_ok=True)
        
        file_path = os.path.join("static", filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(upload_file.file, buffer)
        return get_file_url(filename)
