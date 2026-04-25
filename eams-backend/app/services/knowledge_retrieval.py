"""
知识库检索服务 - 为AI客服提供知识库问答支持
"""

import logging
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
import numpy as np

from app.models.knowledge import Knowledge, KnowledgeCategory

logger = logging.getLogger(__name__)


class KnowledgeRetrieval:
    """知识库检索服务"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def search(
        self,
        shop_id: str,
        query: str,
        top_k: int = 3,
        category_id: Optional[str] = None
    ) -> List[Dict]:
        """
        检索知识库
        
        Args:
            shop_id: 商户ID
            query: 查询问题
            top_k: 返回结果数量
            category_id: 分类筛选
            
        Returns:
            [
                {
                    "id": "知识ID",
                    "question": "问题",
                    "answer": "答案",
                    "category": "分类",
                    "similarity": 0.95
                }
            ]
        """
        try:
            # 构建查询
            q = self.db.query(Knowledge).filter(
                Knowledge.shop_id == shop_id,
                Knowledge.is_active == True
            )
            
            if category_id:
                q = q.filter(Knowledge.category_id == category_id)
            
            # 关键词匹配（简单实现，后续可升级为向量检索）
            keywords = self._extract_keywords(query)
            
            if keywords:
                # 使用OR条件匹配标题或内容
                conditions = []
                for kw in keywords:
                    conditions.append(Knowledge.title.contains(kw))
                    conditions.append(Knowledge.content.contains(kw))
                
                q = q.filter(or_(*conditions))
            
            # 获取候选结果
            candidates = q.limit(top_k * 2).all()
            
            # 计算相似度并排序
            results = []
            for item in candidates:
                similarity = self._calculate_similarity(query, item.title, item.content)
                if similarity > 0.3:  # 相似度阈值
                    results.append({
                        "id": str(item.id),
                        "question": item.title,
                        "answer": item.content,
                        "category": item.category.name if item.category else "未分类",
                        "similarity": similarity
                    })
            
            # 按相似度排序，取top_k
            results.sort(key=lambda x: x["similarity"], reverse=True)
            return results[:top_k]
            
        except Exception as e:
            logger.error(f"知识库检索失败: {e}", exc_info=True)
            return []
    
    async def get_faq_list(
        self,
        shop_id: str,
        category_id: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict]:
        """获取常见问题列表"""
        q = self.db.query(Knowledge).filter(
            Knowledge.shop_id == shop_id,
            Knowledge.is_active == True
        )
        
        if category_id:
            q = q.filter(Knowledge.category_id == category_id)
        
        items = q.order_by(Knowledge.view_count.desc()).limit(limit).all()
        
        return [
            {
                "id": str(item.id),
                "question": item.title,
                "answer": item.content[:200] + "..." if len(item.content) > 200 else item.content,
                "view_count": item.view_count
            }
            for item in items
        ]
    
    async def increment_view_count(self, knowledge_id: str):
        """增加知识查看次数"""
        try:
            item = self.db.query(Knowledge).filter(
                Knowledge.id == knowledge_id
            ).first()
            
            if item:
                item.view_count += 1
                self.db.commit()
        except Exception as e:
            logger.error(f"增加查看次数失败: {e}")
    
    def _extract_keywords(self, text: str) -> List[str]:
        """提取关键词"""
        # 简单的关键词提取：去除停用词，保留名词性词汇
        stop_words = {'的', '了', '是', '我', '有', '和', '就', '不', '人', '都', '一', '一个', '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好', '自己', '这'}
        
        # 分词（简单实现，可用jieba等库优化）
        words = []
        for word in text.split():
            # 去除停用词和标点
            clean_word = word.strip('，。？！；：""''（）【】')
            if clean_word and clean_word not in stop_words and len(clean_word) > 1:
                words.append(clean_word)
        
        return words
    
    def _calculate_similarity(self, query: str, title: str, content: str) -> float:
        """
        计算相似度
        
        简单实现：基于关键词匹配
        后续可升级为：向量相似度（余弦相似度）
        """
        query_keywords = set(self._extract_keywords(query))
        title_keywords = set(self._extract_keywords(title))
        content_keywords = set(self._extract_keywords(content))
        
        if not query_keywords:
            return 0
        
        # 标题匹配权重更高
        title_match = len(query_keywords & title_keywords) / len(query_keywords)
        content_match = len(query_keywords & content_keywords) / len(query_keywords)
        
        # 标题权重0.6，内容权重0.4
        similarity = title_match * 0.6 + content_match * 0.4
        
        return min(1.0, similarity)


# 知识库提示词模板
KNOWLEDGE_PROMPT_TEMPLATE = """你是一个专业的电商客服助手。请根据以下知识库内容回答买家问题。

【知识库相关内容】
{context}

【回答要求】
1. 如果知识库中有直接答案，请基于知识库内容回答
2. 如果知识库中没有相关内容，请根据你的知识回答，但要说明这是通用建议
3. 回答要简洁友好，使用表情符号增加亲和力
4. 如果不确定，引导买家联系人工客服

请回答买家的问题。"""


def build_knowledge_context(knowledge_items: List[Dict]) -> str:
    """构建知识库上下文"""
    if not knowledge_items:
        return "（暂无相关知识库内容）"
    
    context_parts = []
    for i, item in enumerate(knowledge_items, 1):
        context_parts.append(f"{i}. 问题：{item['question']}\n   答案：{item['answer']}")
    
    return "\n\n".join(context_parts)
