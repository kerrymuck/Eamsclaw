"""
意图识别服务 - 识别买家咨询意图
"""

import logging
import re
from typing import Dict, List, Optional, Tuple
from enum import Enum

logger = logging.getLogger(__name__)


class BuyerIntent(Enum):
    """买家意图类型"""
    PRICE_INQUIRY = "price_inquiry"           # 询价
    PRODUCT_INQUIRY = "product_inquiry"       # 产品咨询
    STOCK_INQUIRY = "stock_inquiry"           # 库存咨询
    SHIPPING_INQUIRY = "shipping_inquiry"     # 物流咨询
    AFTER_SALES = "after_sales"               # 售后问题
    REFUND = "refund"                         # 退款
    RETURN = "return"                         # 退货
    EXCHANGE = "exchange"                     # 换货
    COMPLAINT = "complaint"                   # 投诉
    URGENT_ORDER = "urgent_order"             # 催单
    PAYMENT_ISSUE = "payment_issue"           # 支付问题
    COUPON_INQUIRY = "coupon_inquiry"         # 优惠券咨询
    RECOMMENDATION = "recommendation"         # 求推荐
    COMPARISON = "comparison"                 # 对比询问
    GREETING = "greeting"                     # 打招呼
    THANKS = "thanks"                         # 感谢
    GOODBYE = "goodbye"                       # 告别
    UNKNOWN = "unknown"                       # 未知


class IntentRecognizer:
    """意图识别器"""
    
    # 意图关键词映射
    INTENT_KEYWORDS = {
        BuyerIntent.PRICE_INQUIRY: [
            "多少钱", "价格", "优惠", "便宜", "折扣", "活动价", "原价", "现价",
            "怎么卖", "什么价", "报价", "贵不贵", "能便宜", "可以优惠", "最低价"
        ],
        BuyerIntent.PRODUCT_INQUIRY: [
            "什么材质", "什么尺寸", "规格", "参数", "功能", "怎么用", "效果",
            "质量", "品牌", "产地", "保质期", "成分", "适合", "推荐"
        ],
        BuyerIntent.STOCK_INQUIRY: [
            "有货吗", "库存", "还有吗", "能拍吗", "缺货", "什么时候有货",
            "补货", "现货", "预售", "多久发货"
        ],
        BuyerIntent.SHIPPING_INQUIRY: [
            "多久到", "快递", "物流", "运费", "包邮", "发货", "送到", "配送",
            "什么时候到", "几天到", "发什么快递", "能到吗"
        ],
        BuyerIntent.AFTER_SALES: [
            "保修", "售后", "维修", "质保", "坏了", "质量问题", "故障",
            "怎么用", "不会用", "安装", "教程"
        ],
        BuyerIntent.REFUND: [
            "退款", "退钱", "不要了", "取消订单", "能退吗", "怎么退款",
            "退款多久", "退款到账"
        ],
        BuyerIntent.RETURN: [
            "退货", "退回去", "不满意", "不喜欢", "不合适", "质量问题",
            "怎么退货", "退货地址", "退货运费"
        ],
        BuyerIntent.EXCHANGE: [
            "换货", "换尺码", "换颜色", "换型号", "换大小", "能换吗",
            "怎么换货", "换货流程"
        ],
        BuyerIntent.COMPLAINT: [
            "投诉", "差评", "举报", "欺骗", "虚假宣传", "态度差",
            "不满意", "生气", "太过分", "坑人", "骗子"
        ],
        BuyerIntent.URGENT_ORDER: [
            "催单", "快点", "急用", "加急", "什么时候发货", "还没发货",
            "怎么还没", "等很久了", "发货了吗", "到哪了"
        ],
        BuyerIntent.PAYMENT_ISSUE: [
            "支付", "付款", "付不了", "支付失败", "怎么付款", "可以分期",
            "货到付款", "微信支付", "支付宝"
        ],
        BuyerIntent.COUPON_INQUIRY: [
            "优惠券", "代金券", "红包", "满减", "活动", "促销", "领券",
            "怎么领", "能用吗", "有效期"
        ],
        BuyerIntent.RECOMMENDATION: [
            "推荐", "哪个好", "怎么选", "建议", "适合我", "哪款",
            "有什么推荐", "哪个合适"
        ],
        BuyerIntent.COMPARISON: [
            "对比", "区别", "哪个好", "有什么不同", "和", "比",
            "差别", "优缺点", "哪个更值得"
        ],
        BuyerIntent.GREETING: [
            "你好", "在吗", "有人吗", "客服", "亲", "您好", "在不在",
            "在嘛", "哈喽", "hi", "hello"
        ],
        BuyerIntent.THANKS: [
            "谢谢", "感谢", "多谢", "麻烦了", "辛苦", "谢谢亲",
            "太感谢", "谢谢客服"
        ],
        BuyerIntent.GOODBYE: [
            "再见", "拜拜", "bye", "好的", "知道了", "明白", "就这样",
            "先这样", "有问题再找你"
        ]
    }
    
    # 意图优先级（高优先级意图优先匹配）
    INTENT_PRIORITY = [
        BuyerIntent.COMPLAINT,      # 投诉最优先处理
        BuyerIntent.URGENT_ORDER,   # 催单次之
        BuyerIntent.REFUND,
        BuyerIntent.RETURN,
        BuyerIntent.EXCHANGE,
        BuyerIntent.AFTER_SALES,
        BuyerIntent.PRICE_INQUIRY,
        BuyerIntent.PRODUCT_INQUIRY,
        BuyerIntent.STOCK_INQUIRY,
        BuyerIntent.SHIPPING_INQUIRY,
        BuyerIntent.PAYMENT_ISSUE,
        BuyerIntent.COUPON_INQUIRY,
        BuyerIntent.RECOMMENDATION,
        BuyerIntent.COMPARISON,
        BuyerIntent.GREETING,
        BuyerIntent.THANKS,
        BuyerIntent.GOODBYE,
    ]
    
    def __init__(self):
        self._compile_patterns()
    
    def _compile_patterns(self):
        """编译正则表达式模式"""
        self.patterns = {}
        for intent, keywords in self.INTENT_KEYWORDS.items():
            # 构建正则：匹配任意一个关键词
            pattern = "|".join(re.escape(kw) for kw in keywords)
            self.patterns[intent] = re.compile(pattern, re.IGNORECASE)
    
    def recognize(self, message: str) -> Tuple[BuyerIntent, float]:
        """
        识别买家意图
        
        Args:
            message: 买家消息
            
        Returns:
            (意图类型, 置信度)
        """
        if not message:
            return BuyerIntent.UNKNOWN, 0.0
        
        message = message.strip().lower()
        
        # 按优先级匹配
        for intent in self.INTENT_PRIORITY:
            pattern = self.patterns.get(intent)
            if pattern and pattern.search(message):
                # 计算置信度（匹配到的关键词数量）
                matches = len(pattern.findall(message))
                confidence = min(0.3 + matches * 0.2, 0.95)
                return intent, confidence
        
        return BuyerIntent.UNKNOWN, 0.0
    
    def get_intent_description(self, intent: BuyerIntent) -> str:
        """获取意图描述"""
        descriptions = {
            BuyerIntent.PRICE_INQUIRY: "询价",
            BuyerIntent.PRODUCT_INQUIRY: "产品咨询",
            BuyerIntent.STOCK_INQUIRY: "库存咨询",
            BuyerIntent.SHIPPING_INQUIRY: "物流咨询",
            BuyerIntent.AFTER_SALES: "售后问题",
            BuyerIntent.REFUND: "退款",
            BuyerIntent.RETURN: "退货",
            BuyerIntent.EXCHANGE: "换货",
            BuyerIntent.COMPLAINT: "投诉",
            BuyerIntent.URGENT_ORDER: "催单",
            BuyerIntent.PAYMENT_ISSUE: "支付问题",
            BuyerIntent.COUPON_INQUIRY: "优惠券咨询",
            BuyerIntent.RECOMMENDATION: "求推荐",
            BuyerIntent.COMPARISON: "对比询问",
            BuyerIntent.GREETING: "打招呼",
            BuyerIntent.THANKS: "感谢",
            BuyerIntent.GOODBYE: "告别",
            BuyerIntent.UNKNOWN: "未知"
        }
        return descriptions.get(intent, "未知")
    
    def get_suggested_response_strategy(self, intent: BuyerIntent) -> Dict:
        """
        获取建议的回复策略
        
        Returns:
            {
                "strategy": "策略名称",
                "tone": "语气",
                "priority": "优先级",
                "actions": ["建议动作"]
            }
        """
        strategies = {
            BuyerIntent.COMPLAINT: {
                "strategy": "安抚优先",
                "tone": "诚恳道歉，积极解决",
                "priority": "urgent",
                "actions": ["立即道歉", "了解具体问题", "提供解决方案", "必要时转人工"]
            },
            BuyerIntent.URGENT_ORDER: {
                "strategy": "快速响应",
                "tone": "理解焦急，积极跟进",
                "priority": "high",
                "actions": ["查询订单状态", "说明预计时间", "承诺跟进", "提供补偿方案"]
            },
            BuyerIntent.REFUND: {
                "strategy": "挽留优先",
                "tone": "理解决定，提供帮助",
                "priority": "high",
                "actions": ["了解退款原因", "尝试挽留", "说明退款流程", "承诺快速处理"]
            },
            BuyerIntent.RETURN: {
                "strategy": "解决问题",
                "tone": "理解不满，积极处理",
                "priority": "high",
                "actions": ["了解退货原因", "提供退货地址", "说明运费政策", "承诺质检后退款"]
            },
            BuyerIntent.PRICE_INQUIRY: {
                "strategy": "价值强调",
                "tone": "热情介绍，突出性价比",
                "priority": "normal",
                "actions": ["说明价格优势", "介绍当前活动", "推荐套餐", "强调品质价值"]
            },
            BuyerIntent.PRODUCT_INQUIRY: {
                "strategy": "详细介绍",
                "tone": "专业耐心，详细解答",
                "priority": "normal",
                "actions": ["详细介绍产品", "说明使用方法", "提供对比信息", "推荐相关商品"]
            },
            BuyerIntent.GREETING: {
                "strategy": "热情欢迎",
                "tone": "亲切友好，主动服务",
                "priority": "low",
                "actions": ["热情问候", "主动询问需求", "介绍当前活动"]
            }
        }
        
        return strategies.get(intent, {
            "strategy": "标准回复",
            "tone": "友好专业",
            "priority": "normal",
            "actions": ["理解需求", "提供信息", "询问是否还有其他问题"]
        })


# 单例
_intent_recognizer = None

def get_intent_recognizer() -> IntentRecognizer:
    """获取意图识别器实例"""
    global _intent_recognizer
    if _intent_recognizer is None:
        _intent_recognizer = IntentRecognizer()
    return _intent_recognizer
