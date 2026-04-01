const pptxgen = require('pptxgenjs');
const fs = require('fs');
const path = require('path');

// 创建演示文稿
const ppt = new pptxgen();

// 设置演示文稿属性
ppt.title = 'EAMS - 电商智能客服系统';
ppt.subject = '产品推介与投资合作';
ppt.author = 'EAMS Team';

// 定义颜色方案
const colors = {
  primary: '1E88E5',      // 主色：蓝色
  secondary: '43A047',    // 辅色：绿色
  accent: 'FF5722',       // 强调色：橙色
  dark: '263238',         // 深色
  light: 'FFFFFF',        // 白色
  gray: '78909C',         // 灰色
  bgLight: 'F5F7FA'       // 浅灰背景
};

// 定义字体
const fonts = {
  title: { fontFace: 'Microsoft YaHei', fontSize: 44, bold: true, color: colors.dark },
  subtitle: { fontFace: 'Microsoft YaHei', fontSize: 24, color: colors.gray },
  heading: { fontFace: 'Microsoft YaHei', fontSize: 32, bold: true, color: colors.primary },
  body: { fontFace: 'Microsoft YaHei', fontSize: 18, color: colors.dark },
  bullet: { fontFace: 'Microsoft YaHei', fontSize: 16, color: colors.dark }
};

// ==================== 第1页：封面 ====================
const slide1 = ppt.addSlide();
slide1.background = { color: colors.bgLight };

// 标题
slide1.addText('EAMS', {
  x: 0.5, y: 2.5, w: 9, h: 1,
  fontFace: 'Microsoft YaHei', fontSize: 72, bold: true, color: colors.primary,
  align: 'center'
});

slide1.addText('电商智能客服系统', {
  x: 0.5, y: 3.5, w: 9, h: 0.8,
  fontFace: 'Microsoft YaHei', fontSize: 36, color: colors.dark,
  align: 'center'
});

slide1.addText('一站式多平台电商客服解决方案', {
  x: 0.5, y: 4.3, w: 9, h: 0.6,
  fontFace: 'Microsoft YaHei', fontSize: 20, color: colors.gray,
  align: 'center'
});

slide1.addText('产品推介与投资合作', {
  x: 0.5, y: 5.5, w: 9, h: 0.5,
  fontFace: 'Microsoft YaHei', fontSize: 16, color: colors.gray,
  align: 'center'
});

// ==================== 第2页：项目概述 ====================
const slide2 = ppt.addSlide();
slide2.addText('项目概述', { x: 0.5, y: 0.5, w: 9, h: 0.8, ...fonts.heading });

slide2.addText([
  { text: 'EAMS（E-commerce AI Management System）', options: { bold: true, fontSize: 20 } },
  { text: '', options: { breakLine: true } },
  { text: '是一款面向电商企业的智能客服管理系统，通过 AI 技术实现多平台店铺的统一管理和智能客服服务。', options: { fontSize: 18 } },
  { text: '', options: { breakLine: true } },
  { text: '核心价值主张', options: { bold: true, fontSize: 20, color: colors.primary } },
  { text: '• 一个系统管理 32+ 电商平台店铺', options: fonts.bullet },
  { text: '• AI 智能回复，降低 80% 人工成本', options: fonts.bullet },
  { text: '• 跨平台用户识别，统一客户画像', options: fonts.bullet },
  { text: '• 实时消息推送，秒级响应客户', options: fonts.bullet }
], { x: 0.5, y: 1.5, w: 9, h: 4 });

// ==================== 第3页：市场痛点 ====================
const slide3 = ppt.addSlide();
slide3.addText('市场痛点', { x: 0.5, y: 0.5, w: 9, h: 0.8, ...fonts.heading });

const painPoints = [
  { title: '多平台管理混乱', desc: '商家在 10+ 平台开店，需要登录多个后台，效率低下' },
  { title: '客服成本高企', desc: '人工客服 24 小时轮班，人力成本占运营成本 30%+' },
  { title: '响应速度慢', desc: '高峰期消息堆积，客户等待时间长，满意度下降' },
  { title: '数据孤岛', desc: '各平台客户数据不互通，无法形成统一用户画像' },
  { title: '售后处理低效', desc: '退换货、物流查询等重复性问题消耗大量人力' }
];

painPoints.forEach((point, index) => {
  const y = 1.5 + index * 0.9;
  slide3.addText((index + 1) + '.', {
    x: 0.5, y: y, w: 0.5, h: 0.4,
    fontFace: 'Microsoft YaHei', fontSize: 20, bold: true, color: colors.accent
  });
  slide3.addText(point.title, {
    x: 1, y: y, w: 3, h: 0.4,
    fontFace: 'Microsoft YaHei', fontSize: 18, bold: true, color: colors.dark
  });
  slide3.addText(point.desc, {
    x: 4.2, y: y, w: 5, h: 0.4,
    fontFace: 'Microsoft YaHei', fontSize: 14, color: colors.gray
  });
});

// ==================== 第4页：解决方案 ====================
const slide4 = ppt.addSlide();
slide4.addText('解决方案', { x: 0.5, y: 0.5, w: 9, h: 0.8, ...fonts.heading });

slide4.addText('EAMS 提供全链路电商客服解决方案', {
  x: 0.5, y: 1.3, w: 9, h: 0.5,
  fontFace: 'Microsoft YaHei', fontSize: 16, color: colors.gray, align: 'center'
});

// 解决方案卡片
const solutions = [
  { icon: '🏪', title: '多店铺统一管理', desc: '一个后台管理 32+ 平台店铺，统一收件箱聚合所有消息' },
  { icon: '🤖', title: 'AI 智能客服', desc: '基于大模型的智能回复，自动处理 80% 常见问题' },
  { icon: '👤', title: '统一客户画像', desc: '跨平台识别同一客户，构建 360° 用户画像' },
  { icon: '⚡', title: '实时消息推送', desc: 'WebSocket 实时通信，秒级响应客户咨询' },
  { icon: '📚', title: '智能知识库', desc: 'RAG 检索增强，精准回答产品/订单/物流问题' },
  { icon: '📊', title: '数据智能分析', desc: '多维度数据统计，洞察客服质量和客户满意度' }
];

solutions.forEach((sol, index) => {
  const col = index % 3;
  const row = Math.floor(index / 3);
  const x = 0.5 + col * 3.2;
  const y = 2 + row * 2;
  
  // 卡片背景
  slide4.addShape(ppt.ShapeType.rect, {
    x: x, y: y, w: 2.9, h: 1.8,
    fill: { color: colors.bgLight },
    line: { color: colors.primary, width: 1 }
  });
  
  slide4.addText(sol.icon, { x: x + 0.1, y: y + 0.1, w: 0.5, h: 0.5, fontSize: 24 });
  slide4.addText(sol.title, {
    x: x + 0.1, y: y + 0.6, w: 2.7, h: 0.4,
    fontFace: 'Microsoft YaHei', fontSize: 16, bold: true, color: colors.primary
  });
  slide4.addText(sol.desc, {
    x: x + 0.1, y: y + 1, w: 2.7, h: 0.7,
    fontFace: 'Microsoft YaHei', fontSize: 12, color: colors.gray
  });
});

// ==================== 第5页：核心功能 ====================
const slide5 = ppt.addSlide();
slide5.addText('核心功能', { x: 0.5, y: 0.5, w: 9, h: 0.8, ...fonts.heading });

// 左侧：多店铺管理
slide5.addText('多店铺管理', {
  x: 0.5, y: 1.5, w: 4, h: 0.5,
  fontFace: 'Microsoft YaHei', fontSize: 20, bold: true, color: colors.primary
});
slide5.addText([
  '• 支持 32+ 电商平台',
  '• 店铺维度数据隔离',
  '• 统一登录，一键切换',
  '• 可扩展架构，新平台自动接入'
], { x: 0.5, y: 2.1, w: 4, h: 1.5, ...fonts.bullet });

// 右侧：AI 智能客服
slide5.addText('AI 智能客服', {
  x: 5, y: 1.5, w: 4, h: 0.5,
  fontFace: 'Microsoft YaHei', fontSize: 20, bold: true, color: colors.primary
});
slide5.addText([
  '• 9 种意图自动识别',
  '• 知识库智能检索',
  '• 上下文会话管理',
  '• 智能转人工判断'
], { x: 5, y: 2.1, w: 4, h: 1.5, ...fonts.bullet });

// 左侧：统一收件箱
slide5.addText('统一收件箱', {
  x: 0.5, y: 4, w: 4, h: 0.5,
  fontFace: 'Microsoft YaHei', fontSize: 20, bold: true, color: colors.primary
});
slide5.addText([
  '• 多平台消息聚合',
  '• 店铺筛选标签',
  '• 三栏高效布局',
  '• 未读消息实时提醒'
], { x: 0.5, y: 4.6, w: 4, h: 1.5, ...fonts.bullet });

// 右侧：用户端组件
slide5.addText('用户端组件', {
  x: 5, y: 4, w: 4, h: 0.5,
  fontFace: 'Microsoft YaHei', fontSize: 20, bold: true, color: colors.primary
});
slide5.addText([
  '• 浮动聊天窗口',
  '• 店铺信息展示',
  '• 快捷问题推荐',
  '• 订单查询侧边栏'
], { x: 5, y: 4.6, w: 4, h: 1.5, ...fonts.bullet });

// ==================== 第6页：支持平台 ====================
const slide6 = ppt.addSlide();
slide6.addText('支持平台（32+）', { x: 0.5, y: 0.5, w: 9, h: 0.8, ...fonts.heading });

const platforms = [
  { category: '国内电商（7个）', items: '淘宝、天猫、1688、京东、拼多多、抖店、小红书', color: 'E3F2FD' },
  { category: '跨境电商（15个）', items: 'Amazon、eBay、速卖通、Shopee、Lazada、Temu、TikTok Shop、SHEIN、Mercado Libre、Rakuten、Coupang、Ozon、Allegro、Joom、Wish', color: 'E8F5E9' },
  { category: 'B2B平台（4个）', items: '1688、Made-in-China、环球资源、敦煌网', color: 'FFF3E0' },
  { category: '独立站（4个）', items: 'Shopify、WooCommerce、BigCommerce、Magento', color: 'F3E5F5' }
];

platforms.forEach((plat, index) => {
  const y = 1.5 + index * 1.2;
  
  // 背景
  slide6.addShape(ppt.ShapeType.rect, {
    x: 0.5, y: y, w: 9, h: 1,
    fill: { color: plat.color }
  });
  
  slide6.addText(plat.category, {
    x: 0.7, y: y + 0.1, w: 2.5, h: 0.4,
    fontFace: 'Microsoft YaHei', fontSize: 16, bold: true, color: colors.primary
  });
  slide6.addText(plat.items, {
    x: 0.7, y: y + 0.5, w: 8.5, h: 0.4,
    fontFace: 'Microsoft YaHei', fontSize: 12, color: colors.dark
  });
});

// ==================== 第7页：技术架构 ====================
const slide7 = ppt.addSlide();
slide7.addText('技术架构', { x: 0.5, y: 0.5, w: 9, h: 0.8, ...fonts.heading });

// 架构图（简化版）
const layers = [
  { name: '前端层', items: 'Vue3 + TypeScript | 响应式设计 | WebSocket客户端', y: 1.5, color: 'BBDEFB' },
  { name: '后端层', items: 'FastAPI + Python | SQLAlchemy | 平台适配器架构', y: 2.5, color: 'C8E6C9' },
  { name: 'AI层', items: '意图分类 | 知识库RAG | 大模型集成', y: 3.5, color: 'FFCCBC' },
  { name: '数据层', items: 'PostgreSQL | Redis | 消息队列', y: 4.5, color: 'E1BEE7' }
];

layers.forEach(layer => {
  slide7.addShape(ppt.ShapeType.rect, {
    x: 0.5, y: layer.y, w: 9, h: 0.8,
    fill: { color: layer.color }
  });
  slide7.addText(layer.name, {
    x: 0.7, y: layer.y + 0.1, w: 1.5, h: 0.3,
    fontFace: 'Microsoft YaHei', fontSize: 14, bold: true, color: colors.dark
  });
  slide7.addText(layer.items, {
    x: 2.3, y: layer.y + 0.25, w: 7, h: 0.3,
    fontFace: 'Microsoft YaHei', fontSize: 12, color: colors.gray
  });
});

slide7.addText('可扩展架构：新增平台只需创建适配器文件，自动注册到系统，无需修改核心业务代码', {
  x: 0.5, y: 5.5, w: 9, h: 0.5,
  fontFace: 'Microsoft YaHei', fontSize: 12, color: colors.accent, align: 'center'
});

// ==================== 第8页：商业模式 ====================
const slide8 = ppt.addSlide();
slide8.addText('商业模式', { x: 0.5, y: 0.5, w: 9, h: 0.8, ...fonts.heading });

// 收入来源
slide8.addText('收入来源', {
  x: 0.5, y: 1.5, w: 4, h: 0.5,
  fontFace: 'Microsoft YaHei', fontSize: 20, bold: true, color: colors.primary
});

const revenues = [
  'SaaS 订阅：按店铺数量/消息量分级定价',
  '增值服务：定制开发、私有化部署',
  '交易抽成：订单成交佣金（可选）',
  '数据服务：行业报告、竞品分析'
];

revenues.forEach((rev, index) => {
  slide8.addText('• ' + rev, {
    x: 0.5, y: 2.1 + index * 0.5, w: 4, h: 0.4,
    fontFace: 'Microsoft YaHei', fontSize: 14, color: colors.dark
  });
});

// 定价策略
slide8.addText('定价策略', {
  x: 5, y: 1.5, w: 4, h: 0.5,
  fontFace: 'Microsoft YaHei', fontSize: 20, bold: true, color: colors.primary
});

const pricing = [
  { plan: '免费版', price: '¥0', desc: '1店铺，基础功能' },
  { plan: '基础版', price: '¥99/月', desc: '5店铺，AI客服' },
  { plan: '专业版', price: '¥299/月', desc: '20店铺，全功能' },
  { plan: '企业版', price: '定制', desc: '无限店铺，私有化' }
];

pricing.forEach((p, index) => {
  const y = 2.1 + index * 0.7;
  slide8.addText(p.plan, {
    x: 5, y: y, w: 1.5, h: 0.3,
    fontFace: 'Microsoft YaHei', fontSize: 14, bold: true, color: colors.primary
  });
  slide8.addText(p.price, {
    x: 6.5, y: y, w: 1.5, h: 0.3,
    fontFace: 'Microsoft YaHei', fontSize: 14, bold: true, color: colors.accent
  });
  slide8.addText(p.desc, {
    x: 8, y: y, w: 1.5, h: 0.3,
    fontFace: 'Microsoft YaHei', fontSize: 12, color: colors.gray
  });
});

// ==================== 第9页：市场分析 ====================
const slide9 = ppt.addSlide();
slide9.addText('市场分析', { x: 0.5, y: 0.5, w: 9, h: 0.8, ...fonts.heading });

// 市场规模
slide9.addText('市场规模', {
  x: 0.5, y: 1.5, w: 4, h: 0.5,
  fontFace: 'Microsoft YaHei', fontSize: 20, bold: true, color: colors.primary
});

slide9.addText([
  '• 中国电商客服市场规模：500亿+',
  '• 智能客服渗透率：< 15%',
  '• 年复合增长率：25%+',
  '• 目标用户：1000万+ 电商商家'
], { x: 0.5, y: 2.1, w: 4, h: 2, ...fonts.bullet });

// 竞争优势
slide9.addText('竞争优势', {
  x: 5, y: 1.5, w: 4, h: 0.5,
  fontFace: 'Microsoft YaHei', fontSize: 20, bold: true, color: colors.primary
});

slide9.addText([
  '• 多平台覆盖最全（32+平台）',
  '• 可扩展架构，快速接入新平台',
  '• AI + 人工协同，效率最大化',
  '• 跨平台用户识别，数据价值高'
], { x: 5, y: 2.1, w: 4, h: 2, ...fonts.bullet });

// 竞品对比
slide9.addText('竞品对比', {
  x: 0.5, y: 4.2, w: 9, h: 0.5,
  fontFace: 'Microsoft YaHei', fontSize: 18, bold: true, color: colors.primary
});

slide9.addText('美洽、智齿客服：专注单平台，多平台支持弱  |  晓多、乐言：淘宝生态，跨平台能力差  |  EAMS：真正的全平台解决方案', {
  x: 0.5, y: 4.8, w: 9, h: 0.5,
  fontFace: 'Microsoft YaHei', fontSize: 12, color: colors.gray
});

// ==================== 第10页：发展路线图 ====================
const slide10 = ppt.addSlide();
slide10.addText('发展路线图', { x: 0.5, y: 0.5, w: 9, h: 0.8, ...fonts.heading });

const roadmap = [
  { phase: 'Phase 1', time: '2026 Q2', items: '完善核心功能，接入主流平台（淘宝/京东/拼多多）', status: '进行中' },
  { phase: 'Phase 2', time: '2026 Q3', items: '扩展跨境平台（Amazon/Shopee/Lazada），AI模型优化', status: '规划' },
  { phase: 'Phase 3', time: '2026 Q4', items: '上线营销自动化，推出数据分析服务', status: '规划' },
  { phase: 'Phase 4', time: '2027', items: '开放平台 API，构建应用生态，拓展海外市场', status: '规划' }
];

roadmap.forEach((item, index) => {
  const y = 1.5 + index * 1.1;
  
  // 时间线
  slide10.addShape(ppt.ShapeType.oval, {
    x: 0.8, y: y + 0.1, w: 0.3, h: 0.3,
    fill: { color: index === 0 ? colors.primary : colors.gray }
  });
  
  if (index < roadmap.length - 1) {
    slide10.addShape(ppt.ShapeType.line, {
      x: 0.95, y: y + 0.4, w: 0, h: 0.8,
      line: { color: colors.gray, width: 2 }
    });
  }
  
  slide10.addText(item.phase + ' · ' + item.time, {
    x: 1.3, y: y, w: 3, h: 0.3,
    fontFace: 'Microsoft YaHei', fontSize: 14, bold: true, color: index === 0 ? colors.primary : colors.dark
  });
  
  slide10.addText(item.items, {
    x: 1.3, y: y + 0.4, w: 7.5, h: 0.5,
    fontFace: 'Microsoft YaHei', fontSize: 12, color: colors.gray
  });
  
  slide10.addText(item.status, {
    x: 8, y: y, w: 1, h: 0.3,
    fontFace: 'Microsoft YaHei', fontSize: 11, color: index === 0 ? colors.secondary : colors.gray
  });
});

// ==================== 第11页：融资需求 ====================
const slide11 = ppt.addSlide();
slide11.addText('融资需求', { x: 0.5, y: 0.5, w: 9, h: 0.8, ...fonts.heading });

// 融资金额
slide11.addShape(ppt.ShapeType.rect, {
  x: 0.5, y: 1.5, w: 4, h: 1.5,
  fill: { color: colors.primary }
});
slide11.addText('Pre-A轮', {
  x: 0.7, y: 1.7, w: 3.5, h: 0.4,
  fontFace: 'Microsoft YaHei', fontSize: 16, bold: true, color: colors.light
});
slide11.addText('¥500万', {
  x: 0.7, y: 2.1, w: 3.5, h: 0.6,
  fontFace: 'Microsoft YaHei', fontSize: 32, bold: true, color: colors.light
});

// 资金用途
slide11.addText('资金用途', {
  x: 5, y: 1.5, w: 4, h: 0.5,
  fontFace: 'Microsoft YaHei', fontSize: 18, bold: true, color: colors.primary
});

const usage = [
  { item: '产品研发', percent: '40%', desc: '平台适配器开发、AI模型优化' },
  { item: '市场推广', percent: '30%', desc: '获客、品牌建设' },
  { item: '团队建设', percent: '20%', desc: '核心人才招聘' },
  { item: '运营储备', percent: '10%', desc: '日常运营资金' }
];

usage.forEach((u, index) => {
  const y = 2.1 + index * 0.6;
  slide11.addText(u.item, { x: 5, y: y, w: 1.5, h: 0.3, fontSize: 12 });
  slide11.addText(u.percent, { x: 6.5, y: y, w: 0.8, h: 0.3, fontSize: 12, bold: true, color: colors.accent });
  slide11.addText(u.desc, { x: 7.4, y: y, w: 2, h: 0.3, fontSize: 10, color: colors.gray });
});

// 里程碑
slide11.addText('里程碑目标（12个月）', {
  x: 0.5, y: 4, w: 9, h: 0.5,
  fontFace: 'Microsoft YaHei', fontSize: 16, bold: true, color: colors.primary
});

slide11.addText([
  '• 接入 10+ 主流电商平台',
  '• 服务 1000+ 商家',
  '• 月 GMV 突破 1 亿',
  '• 团队规模 20+ 人'
], { x: 0.5, y: 4.6, w: 9, h: 1.5, ...fonts.bullet });

// ==================== 第12页：团队介绍 ====================
const slide12 = ppt.addSlide();
slide12.addText('团队介绍', { x: 0.5, y: 0.5, w: 9, h: 0.8, ...fonts.heading });

slide12.addText('核心团队', {
  x: 0.5, y: 1.5, w: 9, h: 0.5,
  fontFace: 'Microsoft YaHei', fontSize: 18, bold: true, color: colors.primary
});

const team = [
  { role: '创始人/CEO', desc: '10年电商行业经验，前阿里产品经理' },
  { role: 'CTO', desc: '全栈技术专家，分布式系统架构师' },
  { role: 'AI负责人', desc: 'NLP领域博士，大模型应用专家' },
  { role: '运营总监', desc: '5年 SaaS 运营经验，擅长增长黑客' }
];

team.forEach((member, index) => {
  const y = 2.1 + index * 0.7;
  slide12.addText(member.role, {
    x: 0.5, y: y, w: 2, h: 0.3,
    fontFace: 'Microsoft YaHei', fontSize: 14, bold: true, color: colors.dark
  });
  slide12.addText(member.desc, {
    x: 2.5, y: y, w: 6, h: 0.3,
    fontFace: 'Microsoft YaHei', fontSize: 12, color: colors.gray
  });
});

slide12.addText('顾问团队', {
  x: 0.5, y: 5, w: 9, h: 0.5,
  fontFace: 'Microsoft YaHei', fontSize: 18, bold: true, color: colors.primary
});

slide12.addText('电商行业资深专家 · 知名投资机构合伙人 · 技术领域权威学者', {
  x: 0.5, y: 5.6, w: 9, h: 0.3,
  fontFace: 'Microsoft YaHei', fontSize: 12, color: colors.gray
});

// ==================== 第13页：联系方式 ====================
const slide13 = ppt.addSlide();
slide13.background = { color: colors.primary };

slide13.addText('感谢关注', {
  x: 0.5, y: 2, w: 9, h: 1,
  fontFace: 'Microsoft YaHei', fontSize: 48, bold: true, color: colors.light,
  align: 'center'
});

slide13.addText('期待与您合作，共创电商智能客服新未来', {
  x: 0.5, y: 3.2, w: 9, h: 0.5,
  fontFace: 'Microsoft YaHei', fontSize: 18, color: colors.light,
  align: 'center'
});

slide13.addText('联系方式', {
  x: 0.5, y: 4.2, w: 9, h: 0.5,
  fontFace: 'Microsoft YaHei', fontSize: 20, bold: true, color: colors.light,
  align: 'center'
});

slide13.addText('邮箱：contact@eams.com', {
  x: 0.5, y: 4.8, w: 9, h: 0.4,
  fontFace: 'Microsoft YaHei', fontSize: 14, color: colors.light,
  align: 'center'
});

slide13.addText('官网：www.eams.com', {
  x: 0.5, y: 5.2, w: 9, h: 0.4,
  fontFace: 'Microsoft YaHei', fontSize: 14, color: colors.light,
  align: 'center'
});

// ==================== 保存文件 ====================
const outputPath = path.join(__dirname, 'EAMS-产品推介.pptx');

ppt.writeFile({ fileName: outputPath })
  .then(() => {
    console.log('✅ PPT 创建成功！');
    console.log('📁 文件路径：', outputPath);
  })
  .catch(err => {
    console.error('❌ 创建失败：', err);
    process.exit(1);
  });
