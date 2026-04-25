"""
EAMS Backend Launcher
"""
import sys
import os

# 设置工作目录
os.chdir(r'E:\EAMS-Project\eams-backend')

# 添加项目路径
sys.path.insert(0, r'E:\EAMS-Project\eams-backend')

import uvicorn

if __name__ == "__main__":
    print("Starting EAMS Backend...")
    print("API: http://localhost:8000")
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8080,
        reload=False,
        workers=1
    )
