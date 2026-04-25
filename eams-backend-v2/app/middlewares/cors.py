from fastapi.middleware.cors import CORSMiddleware


def setup_cors(app):
    """配置CORS"""
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # 生产环境需要限制
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
