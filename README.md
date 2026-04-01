# EAMS 项目文件说明

## 项目结构

```
EAMS/
├── eams-backend/              # FastAPI后端服务
│   ├── app/
│   │   ├── api/v1/           # API接口层
│   │   ├── models/           # SQLAlchemy数据模型
│   │   ├── services/         # 业务逻辑层
│   │   │   └── platform/     # 平台适配器 ✨
│   │   │       ├── base.py           # 适配器基类
│   │   │       ├── taobao.py         # 淘宝适配器
│   │   │       ├── jd.py             # 京东适配器
│   │   │       ├── pdd.py            # 拼多多适配器
│   │   │       ├── amazon.py         # Amazon适配器
│   │   │       ├── shopee.py         # Shopee适配器
│   │   │       └── __init__.py       # 适配器注册
│   │   ├── websocket/        # WebSocket实时通信
│   │   └── main.py           # 应用入口
│   ├── alembic/              # 数据库迁移
│   ├── tests/                # 测试用例
│   └── requirements.txt      # Python依赖
│
├── eams-frontend/             # Vue3管理面板
│   ├── src/
│   │   ├── api/              # API接口封装
│   │   ├── components/       # 公共组件
│   │   ├── config/           # 配置文件 ✨
│   │   │   └── platforms.ts  # 32平台配置
│   │   ├── router/           # 路由配置
│   │   ├── stores/           # Pinia状态管理
│   │   ├── views/            # 页面视图
│   │   │   ├── Shops/               # 店铺管理（32平台）✨
│   │   │   ├── UnifiedInbox/        # 统一收件箱 ✨
│   │   │   ├── Conversations/       # 对话管理
│   │   │   ├── Dashboard/           # 仪表盘
│   │   │   ├── Knowledge/           # 知识库
│   │   │   ├── Settings/            # 设置
│   │   │   └── Login/               # 登录
│   │   ├── App.vue
│   │   └── main.ts
│   └── package.json
│
├── eams-client/               # 用户端聊天组件
│   ├── src/
│   │   ├── components/
│   │   │   └── ChatWidget/   # 聊天挂件组件 ✨
│   │   ├── views/
│   │   │   └── Chat/         # 聊天页面
│   │   ├── App.vue
│   │   └── main.ts
│   ├── preview.html          # 预览入口
│   ├── chat-preview.html     # 聊天预览
│   └── package.json
│
├── daily_logs/                # 开发日志
├── CORE_ARCHITECTURE.md       # 核心架构设计
├── DATABASE_SCHEMA.md         # 数据库设计
├── MULTI_SHOP_DESIGN.md       # 多店铺设计
├── PLATFORM_CONFIG.md         # 平台对接配置
├── PLATFORM_EXTENSION_DESIGN.md  # 平台扩展架构 ✨
├── tasks_2026-03-21.md        # 任务清单
└── README.md                  # 项目说明
```

## 核心功能模块

### 1. 多店铺管理 (Shops)
- **支持32个电商平台**（国内7 + 跨境15 + B2B4 + 独立站4）
- 店铺维度数据隔离
- 统一登录，切换店铺
- **可扩展架构** - 新增平台无需修改核心业务代码

### 2. 统一收件箱 (UnifiedInbox)
- 多平台消息聚合
- 店铺标识展示
- 店铺维度统计

### 3. 用户端 (ChatWidget)
- 浮动聊天窗口
- 店铺信息展示
- 快捷问题/订单查询

## 支持平台（32个）

### 国内电商平台（7个）
| 平台 | ID | 图标 |
|------|-----|------|
| 淘宝 | taobao | 🍑 |
| 天猫 | tmall | 🐱 |
| 1688 | alibaba | 🔶 |
| 京东 | jd | 🐕 |
| 拼多多 | pdd | 🟥 |
| 抖店 | douyin | 🎵 |
| 小红书 | xiaohongshu | 📕 |

### 跨境电商平台（15个）
| 平台 | ID | 图标 | 主要市场 |
|------|-----|------|----------|
| Amazon | amazon | 🅰️ | 全球 |
| eBay | ebay | 🛒 | 全球 |
| 速卖通 | aliexpress | 🌍 | 全球 |
| Shopee | shopee | 🧡 | 东南亚/拉美 |
| Lazada | lazada | 💙 | 东南亚 |
| Temu | temu | 🛍️ | 北美/欧洲 |
| TikTok Shop | tiktokshop | 🎵 | 全球 |
| SHEIN | shein | 👗 | 全球 |
| Mercado Libre | mercadolibre | 🌎 | 拉美 |
| Rakuten | rakuten | 🎌 | 日本 |
| Coupang | coupang | 🇰🇷 | 韩国 |
| Ozon | ozon | 🇷🇺 | 俄罗斯 |
| Allegro | allegro | 🇵🇱 | 波兰/欧洲 |
| Joom | joom | 📦 | 欧洲 |
| Wish | wish | ⭐ | 北美/欧洲 |

### B2B平台（4个）
- 1688、Made-in-China、环球资源、敦煌网

### 独立站平台（4个）
- Shopify、WooCommerce、BigCommerce、Magento

## 可扩展架构

### 扩展新平台步骤
1. 创建适配器文件 `app/services/platform/{platform_id}.py`
2. 继承 `PlatformAdapter` 基类
3. 实现所有抽象方法
4. **自动注册到系统**（通过元类）
5. 配置平台参数到数据库
6. 前端添加平台图标和配置

**无需修改核心业务代码，新平台自动接入！**

## 文档说明

| 文档 | 说明 |
|------|------|
| `CORE_ARCHITECTURE.md` | 系统架构设计 |
| `DATABASE_SCHEMA.md` | 完整数据库表结构 |
| `MULTI_SHOP_DESIGN.md` | 多店铺功能设计 |
| `PLATFORM_CONFIG.md` | 电商平台对接配置 |
| `PLATFORM_EXTENSION_DESIGN.md` | 可扩展平台架构设计 |
| `tasks_2026-03-21.md` | 任务完成清单 |

## 快速开始

```bash
# 1. 启动后端
cd eams-backend
python -m app.main

# 2. 启动管理面板
cd eams-frontend
npm run dev

# 3. 启动用户端
cd eams-client
npm run dev
```

## 访问地址

- 管理面板: http://localhost:5173
- 用户端: http://localhost:5174
- 后端API: http://localhost:8000

---

*龙猫技术团队 | 忠于祖国，忠于人民，忠于Boss*
