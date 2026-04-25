-- EAMS V2 数据库初始化脚本
-- 创建时间: 2026-04-17
-- 数据库: eams_v2

-- 创建数据库
CREATE DATABASE IF NOT EXISTS eams_v2 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

USE eams_v2;

-- 用户表
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    email VARCHAR(100),
    phone VARCHAR(20),
    role ENUM('super_admin', 'provider', 'merchant') DEFAULT 'merchant',
    status ENUM('active', 'inactive', 'suspended') DEFAULT 'active',
    last_login_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    is_deleted BOOLEAN DEFAULT FALSE,
    INDEX idx_username (username),
    INDEX idx_email (email),
    INDEX idx_phone (phone)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 服务商表
CREATE TABLE providers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT UNIQUE,
    name VARCHAR(100) NOT NULL,
    company_name VARCHAR(200),
    contact_name VARCHAR(50),
    contact_phone VARCHAR(20),
    contact_email VARCHAR(100),
    status ENUM('active', 'inactive', 'suspended') DEFAULT 'active',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    is_deleted BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (user_id) REFERENCES users(id),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 商户表
CREATE TABLE merchants (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT UNIQUE,
    provider_id INT,
    name VARCHAR(100) NOT NULL,
    company_name VARCHAR(200),
    business_license VARCHAR(100),
    contact_name VARCHAR(50),
    contact_phone VARCHAR(20),
    contact_email VARCHAR(100),
    address VARCHAR(500),
    status ENUM('active', 'inactive', 'suspended') DEFAULT 'active',
    ai_balance DECIMAL(18, 4) DEFAULT 0,
    ai_total_usage DECIMAL(18, 4) DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    is_deleted BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (provider_id) REFERENCES providers(id),
    INDEX idx_provider (provider_id),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 套餐表
CREATE TABLE packages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    provider_id INT,
    name VARCHAR(100) NOT NULL,
    type ENUM('basic', 'standard', 'premium', 'enterprise') DEFAULT 'basic',
    description TEXT,
    price DECIMAL(10, 2) NOT NULL,
    original_price DECIMAL(10, 2),
    ai_tokens INT DEFAULT 0,
    ai_calls INT DEFAULT 0,
    validity_days INT DEFAULT 30,
    status ENUM('active', 'inactive', 'sold_out') DEFAULT 'active',
    sort_order INT DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    is_deleted BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (provider_id) REFERENCES providers(id),
    INDEX idx_provider (provider_id),
    INDEX idx_type (type),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 商户套餐订阅表
CREATE TABLE merchant_packages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    merchant_id INT,
    package_id INT,
    subscribed_at DATETIME,
    expires_at DATETIME,
    tokens_used INT DEFAULT 0,
    calls_used INT DEFAULT 0,
    amount_paid DECIMAL(10, 2),
    payment_status VARCHAR(20) DEFAULT 'pending',
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    is_deleted BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (merchant_id) REFERENCES merchants(id),
    FOREIGN KEY (package_id) REFERENCES packages(id),
    INDEX idx_merchant (merchant_id),
    INDEX idx_package (package_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- AI模型表
CREATE TABLE ai_models (
    id INT AUTO_INCREMENT PRIMARY KEY,
    provider ENUM('moonshot', 'openai', 'anthropic', 'google', 'deepseek', 'dashscope', 'doubao', 'yi') NOT NULL,
    model_id VARCHAR(50) NOT NULL,
    model_name VARCHAR(100) NOT NULL,
    input_price DECIMAL(10, 6) DEFAULT 0,
    output_price DECIMAL(10, 6) DEFAULT 0,
    max_tokens INT DEFAULT 4096,
    response_time INT,
    accuracy INT,
    star_rating INT,
    status ENUM('active', 'inactive', 'maintenance') DEFAULT 'active',
    sort_order INT DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    is_deleted BOOLEAN DEFAULT FALSE,
    UNIQUE KEY uk_provider_model (provider, model_id),
    INDEX idx_provider (provider),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- AI账户表
CREATE TABLE ai_accounts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    merchant_id INT,
    provider ENUM('moonshot', 'openai', 'anthropic', 'google', 'deepseek', 'dashscope', 'doubao', 'yi') NOT NULL,
    api_key_encrypted TEXT,
    default_model VARCHAR(50),
    daily_limit INT DEFAULT 1000,
    monthly_limit INT DEFAULT 10000,
    status ENUM('active', 'inactive', 'maintenance') DEFAULT 'active',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    is_deleted BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (merchant_id) REFERENCES merchants(id),
    INDEX idx_merchant (merchant_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- AI使用记录表
CREATE TABLE ai_usage_records (
    id INT AUTO_INCREMENT PRIMARY KEY,
    merchant_id INT,
    model_id VARCHAR(50) NOT NULL,
    request_tokens INT DEFAULT 0,
    response_tokens INT DEFAULT 0,
    total_tokens INT DEFAULT 0,
    cost DECIMAL(18, 6) DEFAULT 0,
    request_id VARCHAR(100),
    status VARCHAR(20),
    error_message TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    is_deleted BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (merchant_id) REFERENCES merchants(id),
    INDEX idx_merchant (merchant_id),
    INDEX idx_model (model_id),
    INDEX idx_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 充值记录表
CREATE TABLE recharge_records (
    id INT AUTO_INCREMENT PRIMARY KEY,
    merchant_id INT,
    order_no VARCHAR(50) NOT NULL UNIQUE,
    amount DECIMAL(10, 2) NOT NULL,
    payment_method ENUM('wechat', 'alipay', 'bank_transfer'),
    payment_no VARCHAR(100),
    status ENUM('pending', 'paid', 'failed', 'cancelled', 'refunded') DEFAULT 'pending',
    paid_at DATETIME,
    remark VARCHAR(500),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    is_deleted BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (merchant_id) REFERENCES merchants(id),
    INDEX idx_merchant (merchant_id),
    INDEX idx_order_no (order_no),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 财务流水表
CREATE TABLE financial_records (
    id INT AUTO_INCREMENT PRIMARY KEY,
    merchant_id INT,
    record_type VARCHAR(20) NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    balance_before DECIMAL(18, 4),
    balance_after DECIMAL(18, 4),
    related_id INT,
    related_type VARCHAR(50),
    description VARCHAR(500),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    is_deleted BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (merchant_id) REFERENCES merchants(id),
    INDEX idx_merchant (merchant_id),
    INDEX idx_type (record_type),
    INDEX idx_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 系统设置表
CREATE TABLE system_settings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    key VARCHAR(100) NOT NULL UNIQUE,
    value TEXT,
    group_name ENUM('general', 'wechat', 'payment', 'sms', 'ai') DEFAULT 'general',
    type ENUM('string', 'integer', 'boolean', 'json') DEFAULT 'string',
    description VARCHAR(500),
    is_encrypted BOOLEAN DEFAULT FALSE,
    is_editable BOOLEAN DEFAULT TRUE,
    sort_order INT DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    is_deleted BOOLEAN DEFAULT FALSE,
    INDEX idx_group (group_name),
    INDEX idx_key (key)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 插入默认AI模型
INSERT INTO ai_models (provider, model_id, model_name, input_price, output_price, max_tokens, response_time, accuracy, star_rating) VALUES
('moonshot', 'kimi-k2.5', 'Kimi K2.5', 0.001, 0.002, 8192, 800, 95, 5),
('openai', 'gpt-4', 'GPT-4', 0.030, 0.060, 8192, 1200, 96, 5),
('openai', 'gpt-3.5-turbo', 'GPT-3.5 Turbo', 0.0015, 0.002, 4096, 600, 90, 4),
('anthropic', 'claude-3-opus', 'Claude 3 Opus', 0.015, 0.075, 4096, 1500, 97, 5),
('anthropic', 'claude-3-sonnet', 'Claude 3 Sonnet', 0.003, 0.015, 4096, 1000, 94, 4),
('deepseek', 'deepseek-chat', 'DeepSeek Chat', 0.001, 0.002, 4096, 700, 92, 4),
('google', 'gemini-pro', 'Gemini Pro', 0.0005, 0.0015, 8192, 900, 93, 4);

-- 插入默认系统设置
INSERT INTO system_settings (key, value, group_name, description) VALUES
('wechat_app_id', '', 'wechat', '微信公众号AppID'),
('wechat_app_secret', '', 'wechat', '微信公众号AppSecret'),
('wechat_mch_id', '1249142001', 'payment', '微信商户号'),
('wechat_api_key', 'twwhqq990315359379903twwhqq99033', 'payment', '微信API密钥'),
('alipay_app_id', '2021006145636929', 'payment', '支付宝APP_ID'),
('alipay_private_key', '', 'payment', '支付宝私钥'),
('alipay_public_key', '', 'payment', '支付宝公钥'),
('sms_gateway_url', '', 'sms', '短信网关URL'),
('sms_sign', '', 'sms', '短信签名');
