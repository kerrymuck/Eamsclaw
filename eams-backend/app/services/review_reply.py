"""
评价回复服务 - 自动回复买家评价
"""

import logging
from datetime import datetime
from typing import List, Dict, Optional
from sqlalchemy.orm import Session

from app.services.ai.gateway import get_ai_gateway
from app.services.ai_power.billing import BillingService
from app.services.sentiment_analysis import get_sentiment_analyzer

logger = logging.getLogger(__name__)


class ReviewReplyService:
    """评价回复服务"""
    
    # 评价类型
    REVIEW_TYPES = {
        "positive": "好评",
        "neutral": "中评",
        "negative": "差评"
    }
    
    # 回复模板
    REPLY_TEMPLATES = {
        "positive": [
            "感谢您的支持和认可！您的满意是我们最大的动力，期待您的再次光临~ 😊",
            "非常感谢亲的好评！我们会继续努力提供更好的产品和服务~ 🙏",
            "感谢亲的认可！有任何问题随时联系我们，祝您生活愉快~ 🌟"
        ],
        "neutral": [
            "感谢您的评价，我们会继续努力改进。如果您有任何建议，欢迎随时联系我们~ 🤝",
            "感谢亲的反馈，我们会认真对待每一条建议，努力做得更好~ 💪",
            "感谢您的中肯评价，如有任何不满意的地方，请联系我们解决~ 🙏"
        ],
        "negative": [
            "非常抱歉给您带来了不好的体验，我们已经收到您的反馈，会立即改进。请您联系客服，我们一定给您一个满意的解决方案~ 🙏",
            "亲，真的很抱歉让您失望了。我们非常重视您的问题，请私信客服，我们会全力解决~ 😔",
            "对不起，我们的服务没有让您满意。请给我们一个弥补的机会，联系客服我们马上处理~ 🙇"
        ]
    }
    
    def __init__(self, db: Session):
        self.db = db
        self.ai_gateway = get_ai_gateway()
        self.billing_service = BillingService()
        self.sentiment_analyzer = get_sentiment_analyzer()
    
    async def analyze_review(
        self,
        review_content: str,
        rating: int
    ) -> Dict:
        """
        分析评价内容
        
        Args:
            review_content: 评价内容
            rating: 评分（1-5星）
            
        Returns:
            {
                "type": "positive/neutral/negative",
                "sentiment": "情感分析结果",
                "needs_reply": True/False,
                "priority": "high/medium/low"
            }
        """
        # 根据评分判断评价类型
        if rating >= 4:
            review_type = "positive"
        elif rating == 3:
            review_type = "neutral"
        else:
            review_type = "negative"
        
        # 情感分析
        sentiment = self.sentiment_analyzer.analyze(review_content)
        
        # 判断是否需要回复
        needs_reply = True
        priority = "low"
        
        if review_type == "negative":
            needs_reply = True
            priority = "high"
        elif review_type == "neutral":
            needs_reply = True
            priority = "medium"
        elif "问题" in review_content or "建议" in review_content:
            needs_reply = True
            priority = "medium"
        
        return {
            "type": review_type,
            "sentiment": sentiment,
            "needs_reply": needs_reply,
            "priority": priority
        }
    
    async def generate_reply(
        self,
        shop_id: str,
        review: Dict,
        use_ai: bool = True
    ) -> Dict:
        """
        生成评价回复
        
        Args:
            shop_id: 商户ID
            review: 评价信息
            use_ai: 是否使用AI生成
            
        Returns:
            {
                "success": True/False,
                "reply": "回复内容",
                "type": "ai/template",
                "cost": 0.0
            }
        """
        try:
            review_type = review.get("type", "neutral")
            review_content = review.get("content", "")
            rating = review.get("rating", 5)
            
            if not use_ai:
                # 使用模板回复
                import random
                reply = random.choice(self.REPLY_TEMPLATES[review_type])
                return {
                    "success": True,
                    "reply": reply,
                    "type": "template",
                    "cost": 0
                }
            
            # 检查余额
            account_info = await self.billing_service.get_account_info(shop_id)
            if account_info['total_available'] <= 0:
                # 余额不足，使用模板
                import random
                reply = random.choice(self.REPLY_TEMPLATES[review_type])
                return {
                    "success": True,
                    "reply": reply,
                    "type": "template",
                    "cost": 0
                }
            
            # 构建提示词
            prompt = self._build_reply_prompt(review)
            
            # 调用AI生成回复
            response = await self.ai_gateway.chat_completion(
                shop_id=shop_id,
                model_name="kimi-k2.5",
                messages=[
                    {"role": "system", "content": "你是一个专业的电商客服，擅长回复买家评价。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            
            if response.get("success"):
                reply = response["data"]["choices"][0]["message"]["content"]
                return {
                    "success": True,
                    "reply": reply,
                    "type": "ai",
                    "cost": response["usage"]["total_cost"]
                }
            else:
                # AI失败，使用模板
                import random
                reply = random.choice(self.REPLY_TEMPLATES[review_type])
                return {
                    "success": True,
                    "reply": reply,
                    "type": "template",
                    "cost": 0
                }
                
        except Exception as e:
            logger.error(f"生成评价回复失败: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }
    
    def _build_reply_prompt(self, review: Dict) -> str:
        """构建回复提示词"""
        review_type = review.get("type", "neutral")
        review_content = review.get("content", "")
        rating = review.get("rating", 5)
        product_name = review.get("product_name", "商品")
        
        type_guidance = {
            "positive": "表达感谢，可以适当邀请再次购买或推荐朋友",
            "neutral": "感谢反馈，表示会改进，邀请再次体验",
            "negative": "诚恳道歉，承认问题，提供解决方案，邀请联系客服"
        }
        
        prompt = f"""请为以下买家评价生成一条回复：

评价信息：
- 商品：{product_name}
- 评分：{rating}星
- 评价类型：{self.REVIEW_TYPES[review_type]}
- 评价内容：{review_content}

回复要求：
1. {type_guidance[review_type]}
2. 语气真诚友好，不要过于官方
3. 适当使用表情符号增加亲和力
4. 字数控制在80字以内
5. 不要出现"此回复由AI生成"等字样

请生成回复："""
        
        return prompt
    
    async def batch_reply_reviews(
        self,
        shop_id: str,
        reviews: List[Dict],
        auto_reply: bool = True
    ) -> List[Dict]:
        """
        批量回复评价
        
        Args:
            shop_id: 商户ID
            reviews: 评价列表
            auto_reply: 是否自动发送
            
        Returns:
            回复结果列表
        """
        results = []
        
        for review in reviews:
            # 分析评价
            analysis = await self.analyze_review(
                review.get("content", ""),
                review.get("rating", 5)
            )
            
            if not analysis["needs_reply"]:
                results.append({
                    "review_id": review.get("id"),
                    "skipped": True,
                    "reason": "无需回复"
                })
                continue
            
            # 生成回复
            reply_result = await self.generate_reply(shop_id, review)
            
            if reply_result["success"]:
                result = {
                    "review_id": review.get("id"),
                    "reply": reply_result["reply"],
                    "type": reply_result["type"],
                    "cost": reply_result.get("cost", 0)
                }
                
                if auto_reply:
                    # TODO: 调用平台API发送回复
                    result["sent"] = True
                    result["sent_at"] = datetime.utcnow().isoformat()
                
                results.append(result)
            else:
                results.append({
                    "review_id": review.get("id"),
                    "success": False,
                    "error": reply_result.get("error")
                })
        
        return results
    
    async def get_pending_reviews(
        self,
        shop_id: str,
        platform: Optional[str] = None
    ) -> List[Dict]:
        """获取待回复的评价"""
        # TODO: 从数据库查询
        # 临时返回模拟数据
        return [
            {
                "id": "RV001",
                "buyer_nick": "买家A",
                "rating": 5,
                "content": "商品很好，物流很快，非常满意！",
                "product_name": "示例商品1",
                "platform": "taobao",
                "created_at": datetime.utcnow().isoformat()
            },
            {
                "id": "RV002",
                "buyer_nick": "买家B",
                "rating": 3,
                "content": "还可以吧，就是包装有点简陋",
                "product_name": "示例商品2",
                "platform": "taobao",
                "created_at": datetime.utcnow().isoformat()
            },
            {
                "id": "RV003",
                "buyer_nick": "买家C",
                "rating": 1,
                "content": "质量太差了，完全不值这个价",
                "product_name": "示例商品3",
                "platform": "jd",
                "created_at": datetime.utcnow().isoformat()
            }
        ]
