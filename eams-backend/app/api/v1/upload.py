"""
文件上传API
处理图片等文件的上传和存储
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
import os
import uuid
import shutil
from datetime import datetime
from typing import Optional
import logging

from app.core.database import get_db
from app.core.config import settings
from app.api.v1.auth import get_current_active_user
from app.models.user import User

router = APIRouter()
logger = logging.getLogger(__name__)

# 上传目录
UPLOAD_DIR = os.path.join(os.getcwd(), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# 允许的文件类型
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}
ALLOWED_FILE_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp", 
                      "application/pdf", "text/plain", "application/msword"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


@router.post("/image")
async def upload_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    上传图片
    
    - 支持格式: jpg, png, gif, webp
    - 最大大小: 10MB
    """
    # 检查文件类型
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的文件类型: {file.content_type}. 仅支持: {', '.join(ALLOWED_IMAGE_TYPES)}"
        )
    
    # 检查文件大小
    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"文件过大，最大支持 {MAX_FILE_SIZE / 1024 / 1024}MB"
        )
    
    # 生成文件名
    file_ext = os.path.splitext(file.filename)[1].lower()
    if not file_ext:
        file_ext = ".jpg"  # 默认扩展名
    
    unique_filename = f"{uuid.uuid4().hex}{file_ext}"
    
    # 按日期组织目录
    today = datetime.now().strftime("%Y%m%d")
    user_dir = os.path.join(UPLOAD_DIR, "images", str(current_user.id), today)
    os.makedirs(user_dir, exist_ok=True)
    
    file_path = os.path.join(user_dir, unique_filename)
    
    # 保存文件
    with open(file_path, "wb") as f:
        f.write(contents)
    
    # 生成访问URL
    file_url = f"/uploads/images/{current_user.id}/{today}/{unique_filename}"
    
    logger.info(f"图片上传成功: {file_url}, 用户: {current_user.username}")
    
    return {
        "code": 1,
        "message": "上传成功",
        "data": {
            "filename": unique_filename,
            "original_name": file.filename,
            "url": file_url,
            "size": len(contents),
            "content_type": file.content_type
        }
    }


@router.post("/file")
async def upload_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    上传文件
    
    - 支持格式: 图片、PDF、Word、文本
    - 最大大小: 10MB
    """
    # 检查文件类型
    if file.content_type not in ALLOWED_FILE_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的文件类型: {file.content_type}"
        )
    
    # 检查文件大小
    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"文件过大，最大支持 {MAX_FILE_SIZE / 1024 / 1024}MB"
        )
    
    # 生成文件名
    file_ext = os.path.splitext(file.filename)[1].lower()
    unique_filename = f"{uuid.uuid4().hex}{file_ext}"
    
    # 按日期组织目录
    today = datetime.now().strftime("%Y%m%d")
    user_dir = os.path.join(UPLOAD_DIR, "files", str(current_user.id), today)
    os.makedirs(user_dir, exist_ok=True)
    
    file_path = os.path.join(user_dir, unique_filename)
    
    # 保存文件
    with open(file_path, "wb") as f:
        f.write(contents)
    
    # 生成访问URL
    file_url = f"/uploads/files/{current_user.id}/{today}/{unique_filename}"
    
    logger.info(f"文件上传成功: {file_url}, 用户: {current_user.username}")
    
    return {
        "code": 1,
        "message": "上传成功",
        "data": {
            "filename": unique_filename,
            "original_name": file.filename,
            "url": file_url,
            "size": len(contents),
            "content_type": file.content_type
        }
    }


@router.get("/images/{user_id}/{date}/{filename}")
async def get_image(
    user_id: str,
    date: str,
    filename: str
):
    """获取图片文件"""
    file_path = os.path.join(UPLOAD_DIR, "images", user_id, date, filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="文件不存在")
    
    return FileResponse(file_path)


@router.get("/files/{user_id}/{date}/{filename}")
async def get_file(
    user_id: str,
    date: str,
    filename: str
):
    """获取文件"""
    file_path = os.path.join(UPLOAD_DIR, "files", user_id, date, filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="文件不存在")
    
    return FileResponse(file_path)


@router.delete("/delete")
async def delete_file(
    file_url: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """删除文件"""
    # 从URL解析文件路径
    # URL格式: /uploads/images/user_id/date/filename
    try:
        parts = file_url.replace("/uploads/", "").split("/")
        if len(parts) < 4:
            raise HTTPException(status_code=400, detail="无效的文件URL")
        
        file_type = parts[0]  # images 或 files
        user_id = parts[1]
        date = parts[2]
        filename = parts[3]
        
        # 检查权限（只能删除自己的文件，管理员除外）
        if str(current_user.id) != user_id and current_user.role != "admin":
            raise HTTPException(status_code=403, detail="无权删除此文件")
        
        file_path = os.path.join(UPLOAD_DIR, file_type, user_id, date, filename)
        
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="文件不存在")
        
        os.remove(file_path)
        
        logger.info(f"文件删除成功: {file_url}, 用户: {current_user.username}")
        
        return {
            "code": 1,
            "message": "删除成功"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除文件失败: {e}")
        raise HTTPException(status_code=500, detail="删除文件失败")
