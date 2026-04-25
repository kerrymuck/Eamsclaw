"""
情感分析服务 - 分析买家情绪状态
"""

import logging
from typing import Dict, Tuple
from enum import Enum
import re

logger = logging.getLogger(__name__)


class SentimentType(Enum):
    """情感类型"""
    VERY_POSITIVE = "very_positive"    # 非常满意
    POSITIVE = "positive"               # 满意
    NEUTRAL = "neutral"                 # 中性
    NEGATIVE = "negative"               # 不满
    VERY_NEGATIVE = "very_negative"     # 非常不满/愤怒


class EmotionType(Enum):
    """情绪类型"""
    HAPPY = "happy"           # 开心
    EXCITED = "excited"       # 兴奋
    GRATEFUL = "grateful"     # 感激
    SATISFIED = "satisfied"   # 满意
    NEUTRAL = "neutral"       # 平静
    ANXIOUS = "anxious"       # 焦虑
    FRUSTRATED = "frustrated" # 沮丧
    ANGRY = "angry"           # 愤怒
    DISAPPOINTED = "disappointed"  # 失望
    WORRIED = "worried"       # 担心


class SentimentAnalyzer:
    """情感分析器"""
    
    # 情感词典
    POSITIVE_WORDS = [
        "好", "棒", "优秀", "完美", "喜欢", "爱", "满意", "感谢", "谢谢", "不错",
        "赞", "推荐", "值得", "开心", "高兴", "惊喜", "给力", "靠谱", "专业",
        "快", "及时", "贴心", "周到", "耐心", "热情", "友好", "漂亮", "好看",
        "质量好", "性价比高", "超值", "划算", "实惠", "正品", "好用", "方便"
    ]
    
    NEGATIVE_WORDS = [
        "差", "烂", "垃圾", "坑", "骗", "假", "失望", "生气", "愤怒", "无语",
        "慢", "迟", "拖延", "敷衍", "态度差", "不负责", "不靠谱", "糟糕",
        "坏了", "破", "旧", "脏", "异味", "质量问题", "瑕疵", "缺陷",
        "退货", "退款", "投诉", "举报", "差评", "曝光", "维权", "上当",
        "亏", "不值", "贵", "坑人", "忽悠", "套路", "虚假宣传"
    ]
    
    INTENSIFIERS = [
        "很", "非常", "特别", "太", "超级", "极其", "相当", "实在", "真的",
        "十分", "相当", "格外", "相当", "万分", "特别特别", "太太"
    ]
    
    NEGATIONS = ["不", "没", "无", "非", "别", "未", "不要", "没有"]
    
    # 愤怒/投诉信号词（高优先级）
    ANGER_SIGNALS = [
        "投诉", "举报", "曝光", "差评", "退一赔三", "假一赔十", "315",
        "消费者协会", "工商局", "法院", "起诉", "律师", "媒体", "微博",
        "抖音曝光", "太欺负人", "太过分", "忍无可忍", "必须解决"
    ]
    
    # 焦虑/催促信号词
    ANXIETY_SIGNALS = [
        "急", "着急", "急用", "等着", "快点", "赶紧", "马上", "立刻",
        "今天必须", "明天要用", "来不及了", "赶时间", "救命", "拜托了"
    ]
    
    def __init__(self):
        self._compile_patterns()
    
    def _compile_patterns(self):
        """编译正则表达式"""
        self.anger_pattern = re.compile("|".join(self.ANGER_SIGNALS))
        self.anxiety_pattern = re.compile("|".join(self.ANXIETY_SIGNALS))
    
    def analyze(self, message: str) -> Dict:
        """
        分析情感
        
        Args:
            message: 买家消息
            
        Returns:
            {
                "sentiment": "positive/negative/neutral",
                "sentiment_score": 0.75,  # -1到1
                "emotion": "happy/angry/anxious...",
                "emotion_score": 0.8,
                "urgency_level": "high/medium/low",  # 紧急程度
                "needs_attention": True,  # 是否需要特别关注
                "suggested_tone": "建议的回复语气"
            }
        """
        if not message:
            return self._default_result()
        
        message = message.strip()
        
        # 1. 检查愤怒/投诉信号（最高优先级）
        if self.anger_pattern.search(message):
            return {
                "sentiment": "very_negative",
                "sentiment_score": -0.9,
                "emotion": "angry",
                "emotion_score": 0.95,
                "urgency_level": "high",
                "needs_attention": True,
                "suggested_tone": "诚恳道歉，立即处理，必要时转人工"
            }
        
        # 2. 检查焦虑/催促信号
        if self.anxiety_pattern.search(message):
            return {
                "sentiment": "negative",
                "sentiment_score": -0.3,
                "emotion": "anxious",
                "emotion_score": 0.8,
                "urgency_level": "high",
                "needs_attention": True,
                "suggested_tone": "理解焦急，快速响应，给出明确时间"
            }
        
        # 3. 计算情感分数
        positive_score = self._count_matches(message, self.POSITIVE_WORDS)
        negative_score = self._count_matches(message, self.NEGATIVE_WORDS)
        
        # 考虑否定词（如"不好"=负面）
        negation_count = self._count_matches(message, self.NEGATIONS)
        if negation_count > 0:
            # 否定词会反转情感
            positive_score, negative_score = negative_score, positive_score
        
        # 考虑程度词
        intensifier_count = self._count_matches(message, self.INTENSIFIERS)
        intensity_multiplier = 1 + intensifier_count * 0.2
        
        # 计算最终分数
        total_score = (positive_score - negative_score) * intensity_multiplier
        
        # 归一化到 -1 到 1
        sentiment_score = max(-1, min(1, total_score / 5))
        
        # 判断情感类型
        sentiment, emotion = self._classify_sentiment(sentiment_score, message)
        
        # 判断紧急程度
        urgency = self._assess_urgency(sentiment_score, message)
        
        # 是否需要特别关注
        needs_attention = sentiment_score < -0.5 or urgency == "high"
        
        # 建议回复语气
        suggested_tone = self._get_suggested_tone(sentiment, emotion, urgency)
        
        return {
            "sentiment": sentiment,
            "sentiment_score": round(sentiment_score, 2),
            "emotion": emotion,
            "emotion_score": round(abs(sentiment_score), 2),
            "urgency_level": urgency,
            "needs_attention": needs_attention,
            "suggested_tone": suggested_tone
        }
    
    def _count_matches(self, message: str, word_list: list) -> int:
        """计算匹配词数"""
        count = 0
        for word in word_list:
            count += message.count(word)
        return count
    
    def _classify_sentiment(self, score: float, message: str) -> Tuple[str, str]:
        """分类情感"""
        if score >= 0.6:
            return "very_positive", "happy"
        elif score >= 0.2:
            return "positive", "satisfied"
        elif score > -0.2:
            return "neutral", "neutral"
        elif score > -0.6:
            return "negative", "disappointed"
        else:
            return "very_negative", "frustrated"
    
    def _assess_urgency(self, sentiment_score: float, message: str) -> str:
        """评估紧急程度"""
        # 消息长度（短消息可能更急）
        if len(message) < 10 and sentiment_score < 0:
            return "high"
        
        # 标点符号（多个感叹号表示情绪激动）
        if message.count("！") >= 2 or message.count("!") >= 2:
            return "high"
        
        # 负面情感
        if sentiment_score < -0.5:
            return "high"
        elif sentiment_score < -0.2:
            return "medium"
        
        return "low"
    
    def _get_suggested_tone(self, sentiment: str, emotion: str, urgency: str) -> str:
        """获取建议回复语气"""
        tone_map = {
            ("very_positive", "high"): "热情感谢，适当推荐",
            ("very_positive", "medium"): "热情友好，积极互动",
            ("very_positive", "low"): "友好亲切，保持联系",
            ("positive", "high"): "热情回应，快速处理",
            ("positive", "medium"): "友好专业，详细解答",
            ("positive", "low"): "温和耐心，细致服务",
            ("neutral", "high"): "专业高效，快速响应",
            ("neutral", "medium"): "专业友好，标准服务",
            ("neutral", "low"): "平和自然，正常交流",
            ("negative", "high"): "诚恳道歉，立即解决",
            ("negative", "medium"): "理解不满，积极处理",
            ("negative", "low"): "耐心解释，消除疑虑",
            ("very_negative", "high"): "深度道歉，紧急处理，转人工",
            ("very_negative", "medium"): "诚恳道歉，提供补偿",
            ("very_negative", "low"): "耐心安抚，了解原因"
        }
        
        return tone_map.get((sentiment, urgency), "友好专业，标准服务")
    
    def _default_result(self) -> Dict:
        """默认结果"""
        return {
            "sentiment": "neutral",
            "sentiment_score": 0.0,
            "emotion": "neutral",
            "emotion_score": 0.0,
            "urgency_level": "low",
            "needs_attention": False,
            "suggested_tone": "友好专业，标准服务"
        }
    
    def get_sentiment_emoji(self, sentiment: str) -> str:
        """获取情感对应的表情"""
        emoji_map = {
            "very_positive": "😄",
            "positive": "🙂",
            "neutral": "😐",
            "negative": "😕",
            "very_negative": "😠"
        }
        return emoji_map.get(sentiment, "😐")


# 单例
_sentiment_analyzer = None

def get_sentiment_analyzer() -> SentimentAnalyzer:
    """获取情感分析器实例"""
    global _sentiment_analyzer
    if _sentiment_analyzer is None:
        _sentiment_analyzer = SentimentAnalyzer()
    return _sentiment_analyzer
