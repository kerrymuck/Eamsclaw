# EAMS 多店铺管理功能开发

## 需求分析

### 管理端多店铺管理
- 支持一个商家管理多个电商平台店铺
- 每个平台可绑定多个店铺
- 店铺维度数据隔离
- 统一登录，切换店铺

### 用户端优化
- 店铺标识展示
- 平台-specific功能
- 更好的用户体验

---

## 数据库模型更新

### 店铺模型 (Shop)
```python
class Shop:
    id: UUID
    name: str                    # 店铺名称
    platform: str               # 平台类型: taobao/jd/pdd
    platform_shop_id: str       # 平台店铺ID
    platform_auth: JSON         # 平台授权信息
    owner_id: UUID              # 所属商家
    status: str                 # active/inactive
    settings: JSON              # 店铺配置
    created_at: datetime
```

### 商家模型 (Merchant)
```python
class Merchant:
    id: UUID
    name: str                   # 商家名称
    owner_id: UUID              # 主账号用户ID
    shops: List[Shop]           # 店铺列表
    settings: JSON              # 全局配置
```

---

## API接口设计

### 店铺管理
- `GET /api/v1/shops` - 获取店铺列表
- `POST /api/v1/shops` - 添加店铺
- `GET /api/v1/shops/{id}` - 获取店铺详情
- `PUT /api/v1/shops/{id}` - 更新店铺
- `DELETE /api/v1/shops/{id}` - 删除店铺
- `POST /api/v1/shops/{id}/auth` - 平台授权

### 平台对接
- `GET /api/v1/platform/taobao/auth-url` - 获取淘宝授权链接
- `POST /api/v1/platform/taobao/callback` - 淘宝授权回调
- `GET /api/v1/platform/jd/auth-url` - 获取京东授权链接
- `POST /api/v1/platform/jd/callback` - 京东授权回调
- `GET /api/v1/platform/pdd/auth-url` - 获取拼多多授权链接
- `POST /api/v1/platform/pdd/callback` - 拼多多授权回调

---

## 前端页面设计

### 店铺管理页面
- 店铺列表展示
- 添加店铺（平台选择）
- 授权状态管理
- 店铺设置

### 统一收件箱优化
- 按店铺筛选
- 店铺标识显示
- 店铺维度统计
