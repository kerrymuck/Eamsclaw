# EAMS Frontend

电商客服智能体前端应用

## 技术栈

- Vue 3
- TypeScript
- Element Plus
- Pinia
- Vue Router
- Axios
- ECharts

## 项目结构

```
eams-frontend/
├── src/
│   ├── components/       # 公共组件
│   │   ├── ChatWindow/
│   │   ├── Sidebar/
│   │   └── StatsCard/
│   ├── views/            # 页面视图
│   │   ├── Login/
│   │   ├── Dashboard/
│   │   ├── Conversations/
│   │   ├── Knowledge/
│   │   └── Settings/
│   ├── stores/           # Pinia状态管理
│   │   ├── user.ts
│   │   ├── conversation.ts
│   │   └── knowledge.ts
│   ├── api/              # API接口
│   │   ├── auth.ts
│   │   ├── dialog.ts
│   │   └── index.ts
│   ├── utils/            # 工具函数
│   │   ├── request.ts
│   │   ├── storage.ts
│   │   └── format.ts
│   ├── App.vue
│   └── main.ts
├── public/
└── package.json
```

## 快速开始

```bash
# 安装依赖
npm install

# 开发模式
npm run dev

# 构建
npm run build
```

## 开发团队

- 前端：青龙
