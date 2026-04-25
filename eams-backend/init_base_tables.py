"""
创建完整的 shops 表
"""
import sys
sys.path.insert(0, r'E:\EAMS-Project\eams-backend')

from sqlalchemy import create_engine, text

engine = create_engine('sqlite:///E:\EAMS-Project\eams-backend\eams_dev.db')

with engine.connect() as conn:
    # 创建 shops 表
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS shops (
            id VARCHAR(36) PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            description TEXT,
            owner_id VARCHAR(36),
            status VARCHAR(20) DEFAULT 'active',
            settings TEXT DEFAULT '{}',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """))
    
    # 创建 users 表（简化版）
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS users (
            id VARCHAR(36) PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            email VARCHAR(100) UNIQUE,
            phone VARCHAR(20),
            real_name VARCHAR(50),
            avatar_url TEXT,
            role VARCHAR(20) DEFAULT 'customer_service',
            status VARCHAR(20) DEFAULT 'active',
            last_login_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """))
    
    # 插入测试数据
    from uuid import uuid4
    import uuid
    
    # 检查是否已有数据
    result = conn.execute(text("SELECT COUNT(*) FROM shops")).fetchone()
    if result[0] == 0:
        shop_id = str(uuid4())
        user_id = str(uuid4())
        
        # 插入测试用户
        conn.execute(text("""
            INSERT INTO users (id, username, password_hash, email, role, status)
            VALUES (:id, :username, :password_hash, :email, :role, :status)
        """), {
            'id': user_id,
            'username': 'admin',
            'password_hash': '$2b$12$xxxxx',
            'email': 'admin@test.com',
            'role': 'admin',
            'status': 'active'
        })
        
        # 插入测试商户
        conn.execute(text("""
            INSERT INTO shops (id, name, owner_id, status)
            VALUES (:id, :name, :owner_id, :status)
        """), {
            'id': shop_id,
            'name': '测试商户',
            'owner_id': user_id,
            'status': 'active'
        })
        
        print(f"[OK] Created test shop: {shop_id}")
        print(f"[OK] Created test user: {user_id}")
    
    conn.commit()
    print("[OK] Shops and users tables created")
