// EAMS 电商平台配置
// 支持国内及跨境主流电商平台

export const PLATFORMS = {
  // ========== 国内电商平台 ==========
  
  // 阿里系
  taobao: { 
    id: 'taobao',
    name: '淘宝', 
    icon: '🍑', 
    color: '#ff5000', 
    category: 'domestic',
    type: 'b2c',
    company: '阿里巴巴'
  },
  tmall: { 
    id: 'tmall',
    name: '天猫', 
    icon: '🐱', 
    color: '#ff0036', 
    category: 'domestic',
    type: 'b2c',
    company: '阿里巴巴'
  },
  alibaba: { 
    id: 'alibaba',
    name: '1688', 
    icon: '🔶', 
    color: '#ff6a00', 
    category: 'domestic',
    type: 'b2b',
    company: '阿里巴巴'
  },
  
  // 京东
  jd: { 
    id: 'jd',
    name: '京东', 
    icon: '🐕', 
    color: '#e4393c', 
    category: 'domestic',
    type: 'b2c',
    company: '京东'
  },
  
  // 拼多多
  pdd: { 
    id: 'pdd',
    name: '拼多多', 
    icon: '🟥', 
    color: '#e02e24', 
    category: 'domestic',
    type: 'b2c',
    company: '拼多多'
  },
  
  // 抖店
  douyin: { 
    id: 'douyin',
    name: '抖店', 
    icon: '🎵', 
    color: '#000000', 
    category: 'domestic',
    type: 'social',
    company: '字节跳动'
  },
  
  // 小红书
  xiaohongshu: { 
    id: 'xiaohongshu',
    name: '小红书', 
    icon: '📕', 
    color: '#ff2442', 
    category: 'domestic',
    type: 'social',
    company: '小红书'
  },

  // ========== 跨境电商平台 ==========
  
  // 全球综合
  amazon: { 
    id: 'amazon',
    name: 'Amazon', 
    icon: '🅰️', 
    color: '#ff9900', 
    category: 'crossborder',
    type: 'b2c',
    company: 'Amazon',
    regions: ['US', 'EU', 'JP', 'UK', 'DE', 'FR', 'IT', 'ES', 'CA', 'AU']
  },
  ebay: { 
    id: 'ebay',
    name: 'eBay', 
    icon: '🛒', 
    color: '#e53238', 
    category: 'crossborder',
    type: 'c2c',
    company: 'eBay',
    regions: ['US', 'UK', 'DE', 'AU']
  },
  aliexpress: { 
    id: 'aliexpress',
    name: '速卖通', 
    icon: '🌍', 
    color: '#ff4747', 
    category: 'crossborder',
    type: 'b2c',
    company: '阿里巴巴',
    regions: ['RU', 'BR', 'FR', 'ES', 'PL']
  },
  
  // 东南亚
  shopee: { 
    id: 'shopee',
    name: 'Shopee', 
    icon: '🧡', 
    color: '#ee4d2d', 
    category: 'crossborder',
    type: 'b2c',
    company: 'Sea',
    regions: ['SG', 'MY', 'TH', 'VN', 'ID', 'PH', 'TW', 'BR']
  },
  lazada: { 
    id: 'lazada',
    name: 'Lazada', 
    icon: '💙', 
    color: '#0f156d', 
    category: 'crossborder',
    type: 'b2c',
    company: '阿里巴巴',
    regions: ['SG', 'MY', 'TH', 'VN', 'ID', 'PH']
  },
  
  // 新兴平台
  temu: { 
    id: 'temu',
    name: 'Temu', 
    icon: '🛍️', 
    color: '#fb7701', 
    category: 'crossborder',
    type: 'b2c',
    company: '拼多多',
    regions: ['US', 'EU', 'UK', 'CA', 'AU']
  },
  tiktokshop: { 
    id: 'tiktokshop',
    name: 'TikTok Shop', 
    icon: '🎵', 
    color: '#000000', 
    category: 'crossborder',
    type: 'social',
    company: 'ByteDance',
    regions: ['US', 'UK', 'ID', 'TH', 'VN', 'MY', 'PH', 'SG']
  },
  shein: { 
    id: 'shein',
    name: 'SHEIN', 
    icon: '👗', 
    color: '#000000', 
    category: 'crossborder',
    type: 'b2c',
    company: '希音',
    regions: ['US', 'EU', 'UK', 'CA', 'AU', 'ME']
  },
  
  // 区域平台
  mercadolibre: { 
    id: 'mercadolibre',
    name: 'Mercado Libre', 
    icon: '🌎', 
    color: '#ffe600', 
    category: 'crossborder',
    type: 'b2c',
    company: 'MercadoLibre',
    regions: ['BR', 'MX', 'AR', 'CL', 'CO']
  },
  rakuten: { 
    id: 'rakuten',
    name: 'Rakuten', 
    icon: '🎌', 
    color: '#bf0000', 
    category: 'crossborder',
    type: 'b2c',
    company: '乐天',
    regions: ['JP']
  },
  coupang: { 
    id: 'coupang',
    name: 'Coupang', 
    icon: '🇰🇷', 
    color: '#00a0e9', 
    category: 'crossborder',
    type: 'b2c',
    company: 'Coupang',
    regions: ['KR']
  },
  ozon: { 
    id: 'ozon',
    name: 'Ozon', 
    icon: '🇷🇺', 
    color: '#0066cc', 
    category: 'crossborder',
    type: 'b2c',
    company: 'Ozon',
    regions: ['RU']
  },
  allegro: { 
    id: 'allegro',
    name: 'Allegro', 
    icon: '🇵🇱', 
    color: '#ff5a00', 
    category: 'crossborder',
    type: 'b2c',
    company: 'Allegro',
    regions: ['PL', 'CZ', 'CZ']
  },
  joom: { 
    id: 'joom',
    name: 'Joom', 
    icon: '📦', 
    color: '#0096f2', 
    category: 'crossborder',
    type: 'b2c',
    company: 'Joom',
    regions: ['EU', 'RU']
  },
  wish: { 
    id: 'wish',
    name: 'Wish', 
    icon: '⭐', 
    color: '#2fb7ec', 
    category: 'crossborder',
    type: 'b2c',
    company: 'ContextLogic',
    regions: ['US', 'EU']
  },

  // ========== B2B平台 ==========
  madeinchina: { 
    id: 'madeinchina',
    name: 'Made-in-China', 
    icon: '🇨🇳', 
    color: '#c41230', 
    category: 'b2b',
    type: 'b2b',
    company: '焦点科技'
  },
  globalsources: { 
    id: 'globalsources',
    name: '环球资源', 
    icon: '🌐', 
    color: '#004b8d', 
    category: 'b2b',
    type: 'b2b',
    company: '环球资源'
  },
  dhgate: { 
    id: 'dhgate',
    name: '敦煌网', 
    icon: '🏛️', 
    color: '#ff6a00', 
    category: 'b2b',
    type: 'b2b',
    company: '敦煌网'
  },

  // ========== 独立站平台 ==========
  shopify: { 
    id: 'shopify',
    name: 'Shopify', 
    icon: '🛍️', 
    color: '#96bf48', 
    category: 'independent',
    type: 'saas',
    company: 'Shopify'
  },
  woocommerce: { 
    id: 'woocommerce',
    name: 'WooCommerce', 
    icon: '🌐', 
    color: '#96588a', 
    category: 'independent',
    type: 'plugin',
    company: 'Automattic'
  },
  bigcommerce: { 
    id: 'bigcommerce',
    name: 'BigCommerce', 
    icon: '🅱️', 
    color: '#34313f', 
    category: 'independent',
    type: 'saas',
    company: 'BigCommerce'
  },
  magento: { 
    id: 'magento',
    name: 'Magento', 
    icon: '🅼️', 
    color: '#f26322', 
    category: 'independent',
    type: 'opensource',
    company: 'Adobe'
  },
} as const;

export type PlatformType = keyof typeof PLATFORMS;

// 平台分类
export const PLATFORM_CATEGORIES = {
  domestic: {
    name: '国内电商',
    platforms: ['taobao', 'tmall', 'jd', 'pdd', 'douyin', 'xiaohongshu', 'alibaba']
  },
  crossborder: {
    name: '跨境电商',
    platforms: ['amazon', 'ebay', 'aliexpress', 'shopee', 'lazada', 'temu', 'tiktokshop', 'shein', 'mercadolibre', 'rakuten', 'coupang', 'ozon', 'allegro', 'joom', 'wish']
  },
  b2b: {
    name: 'B2B平台',
    platforms: ['alibaba', 'madeinchina', 'globalsources', 'dhgate']
  },
  independent: {
    name: '独立站',
    platforms: ['shopify', 'woocommerce', 'bigcommerce', 'magento']
  }
};

// 获取平台配置
export function getPlatformConfig(platformId: string) {
  return PLATFORMS[platformId as PlatformType];
}

// 获取平台图标
export function getPlatformIcon(platformId: string): string {
  return PLATFORMS[platformId as PlatformType]?.icon || '🏪';
}

// 获取平台名称
export function getPlatformName(platformId: string): string {
  return PLATFORMS[platformId as PlatformType]?.name || platformId;
}

// 获取平台颜色
export function getPlatformColor(platformId: string): string {
  return PLATFORMS[platformId as PlatformType]?.color || '#666';
}

// 获取平台类型
export function getPlatformType(platformId: string): string {
  return PLATFORMS[platformId as PlatformType]?.type || 'b2c';
}

// 获取Element Plus标签类型
export function getPlatformTagType(platformId: string): string {
  const typeMap: Record<string, string> = {
    taobao: 'warning',
    tmall: 'danger',
    jd: 'danger',
    pdd: 'success',
    douyin: 'info',
    xiaohongshu: 'danger',
    amazon: 'warning',
    ebay: 'danger',
    shopee: 'success',
    lazada: 'primary',
    aliexpress: 'primary',
  };
  return typeMap[platformId] || 'info';
}

// 按分类获取平台列表
export function getPlatformsByCategory(category: string): string[] {
  return PLATFORM_CATEGORIES[category as keyof typeof PLATFORM_CATEGORIES]?.platforms || [];
}

// 获取所有平台ID列表
export function getAllPlatformIds(): string[] {
  return Object.keys(PLATFORMS);
}

// 获取所有平台配置列表
export function getAllPlatforms() {
  return Object.values(PLATFORMS);
}
