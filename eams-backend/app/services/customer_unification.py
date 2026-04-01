"""
跨平台用户数据关联服务
识别同一客户在不同平台的身份
"""

from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass
from datetime import datetime
import re
import hashlib
from collections import defaultdict


@dataclass
class CustomerIdentity:
    """客户身份标识"""
    customer_id: str
    platform: str
    platform_shop_id: str
    
    # 身份属性
    phone: Optional[str] = None
    email: Optional[str] = None
    name: Optional[str] = None
    
    # 设备信息
    device_id: Optional[str] = None
    
    # 地址信息（用于关联）
    address_hash: Optional[str] = None
    
    def get_key(self) -> str:
        """获取唯一标识键"""
        return f"{self.platform}:{self.platform_shop_id}:{self.customer_id}"


@dataclass
class UnifiedCustomer:
    """统一客户档案"""
    unified_id: str  # 统一客户ID
    
    # 关联的平台身份
    identities: List[CustomerIdentity]
    
    # 合并的用户信息
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    avatar: Optional[str] = None
    
    # 用户画像
    tags: List[str] = None
    vip_level: str = "normal"
    
    # 统计信息
    total_orders: int = 0
    total_spent: float = 0.0
    first_contact_at: Optional[datetime] = None
    last_contact_at: Optional[datetime] = None
    
    # 关联时间
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()
    
    def get_all_platforms(self) -> Set[str]:
        """获取客户关联的所有平台"""
        return set(identity.platform for identity in self.identities)
    
    def get_identity(self, platform: str, platform_shop_id: str) -> Optional[CustomerIdentity]:
        """获取指定平台的身份"""
        for identity in self.identities:
            if identity.platform == platform and identity.platform_shop_id == platform_shop_id:
                return identity
        return None


class CustomerIdentityMatcher:
    """
    客户身份匹配器
    使用多种算法识别同一客户
    """
    
    # 匹配权重配置
    MATCH_WEIGHTS = {
        "phone_exact": 1.0,        # 手机号完全匹配
        "email_exact": 1.0,        # 邮箱完全匹配
        "name_phone_similar": 0.8,  # 姓名+手机号相似
        "address_similar": 0.7,     # 地址相似
        "device_id": 0.9,          # 设备ID相同
        "name_similar": 0.5,       # 姓名相似
        "behavior_similar": 0.4,    # 行为相似
    }
    
    # 匹配阈值
    MATCH_THRESHOLD = 0.75
    
    @classmethod
    def calculate_similarity(
        cls,
        identity1: CustomerIdentity,
        identity2: CustomerIdentity
    ) -> float:
        """
        计算两个身份的相似度
        
        Returns:
            0-1之间的相似度分数
        """
        scores = []
        
        # 1. 手机号匹配（最高优先级）
        if identity1.phone and identity2.phone:
            if identity1.phone == identity2.phone:
                scores.append(("phone_exact", cls.MATCH_WEIGHTS["phone_exact"]))
        
        # 2. 邮箱匹配
        if identity1.email and identity2.email:
            if identity1.email.lower() == identity2.email.lower():
                scores.append(("email_exact", cls.MATCH_WEIGHTS["email_exact"]))
        
        # 3. 设备ID匹配
        if identity1.device_id and identity2.device_id:
            if identity1.device_id == identity2.device_id:
                scores.append(("device_id", cls.MATCH_WEIGHTS["device_id"]))
        
        # 4. 地址匹配
        if identity1.address_hash and identity2.address_hash:
            if identity1.address_hash == identity2.address_hash:
                scores.append(("address_similar", cls.MATCH_WEIGHTS["address_similar"]))
        
        # 5. 姓名相似度
        if identity1.name and identity2.name:
            name_sim = cls._calculate_name_similarity(identity1.name, identity2.name)
            if name_sim > 0.8:
                scores.append(("name_similar", cls.MATCH_WEIGHTS["name_similar"] * name_sim))
        
        # 计算加权平均分
        if not scores:
            return 0.0
        
        total_weight = sum(score for _, score in scores)
        max_possible = sum(cls.MATCH_WEIGHTS[s[0]] for s in scores)
        
        return total_weight / max_possible if max_possible > 0 else 0.0
    
    @staticmethod
    def _calculate_name_similarity(name1: str, name2: str) -> float:
        """计算姓名相似度"""
        # 简单的相似度计算，实际可使用更复杂的算法
        name1 = name1.lower().strip()
        name2 = name2.lower().strip()
        
        if name1 == name2:
            return 1.0
        
        # 编辑距离相似度
        from difflib import SequenceMatcher
        return SequenceMatcher(None, name1, name2).ratio()
    
    @classmethod
    def should_merge(
        cls,
        identity1: CustomerIdentity,
        identity2: CustomerIdentity
    ) -> bool:
        """判断是否应该合并两个身份"""
        similarity = cls.calculate_similarity(identity1, identity2)
        return similarity >= cls.MATCH_THRESHOLD


class CustomerUnificationService:
    """
    客户统一服务
    管理跨平台客户身份关联
    """
    
    def __init__(self):
        # 统一客户档案存储
        # unified_id -> UnifiedCustomer
        self.unified_customers: Dict[str, UnifiedCustomer] = {}
        
        # 身份索引
        # identity_key -> unified_id
        self.identity_index: Dict[str, str] = {}
        
        # 手机号索引
        # phone -> unified_id
        self.phone_index: Dict[str, str] = {}
        
        # 邮箱索引
        # email -> unified_id
        self.email_index: Dict[str, str] = {}
    
    def _generate_unified_id(self, identity: CustomerIdentity) -> str:
        """生成统一客户ID"""
        # 基于手机号或邮箱生成稳定的ID
        if identity.phone:
            return hashlib.md5(f"phone:{identity.phone}".encode()).hexdigest()[:16]
        elif identity.email:
            return hashlib.md5(f"email:{identity.email}".encode()).hexdigest()[:16]
        else:
            # 基于平台身份生成
            return hashlib.md5(identity.get_key().encode()).hexdigest()[:16]
    
    async def register_identity(
        self,
        identity: CustomerIdentity,
        auto_merge: bool = True
    ) -> UnifiedCustomer:
        """
        注册新客户身份
        
        Args:
            identity: 客户身份
            auto_merge: 是否自动合并相似身份
            
        Returns:
            统一客户档案
        """
        identity_key = identity.get_key()
        
        # 检查是否已存在
        if identity_key in self.identity_index:
            unified_id = self.identity_index[identity_key]
            return self.unified_customers[unified_id]
        
        # 尝试查找匹配的统一客户
        matched_unified_id = None
        
        # 1. 通过手机号查找
        if identity.phone and identity.phone in self.phone_index:
            matched_unified_id = self.phone_index[identity.phone]
        
        # 2. 通过邮箱查找
        elif identity.email and identity.email in self.email_index:
            matched_unified_id = self.email_index[identity.email]
        
        # 3. 通过相似度匹配
        elif auto_merge:
            for unified_id, customer in self.unified_customers.items():
                for existing_identity in customer.identities:
                    if CustomerIdentityMatcher.should_merge(identity, existing_identity):
                        matched_unified_id = unified_id
                        break
                if matched_unified_id:
                    break
        
        if matched_unified_id:
            # 添加到现有的统一客户
            unified_customer = self.unified_customers[matched_unified_id]
            unified_customer.identities.append(identity)
            unified_customer.updated_at = datetime.now()
            
            # 更新索引
            self.identity_index[identity_key] = matched_unified_id
            if identity.phone:
                self.phone_index[identity.phone] = matched_unified_id
            if identity.email:
                self.email_index[identity.email] = matched_unified_id
            
            # 合并用户信息
            self._merge_customer_info(unified_customer, identity)
            
            return unified_customer
        
        else:
            # 创建新的统一客户
            unified_id = self._generate_unified_id(identity)
            
            unified_customer = UnifiedCustomer(
                unified_id=unified_id,
                identities=[identity],
                name=identity.name,
                phone=identity.phone,
                email=identity.email,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            self.unified_customers[unified_id] = unified_customer
            
            # 建立索引
            self.identity_index[identity_key] = unified_id
            if identity.phone:
                self.phone_index[identity.phone] = unified_id
            if identity.email:
                self.email_index[identity.email] = unified_id
            
            return unified_customer
    
    def _merge_customer_info(
        self,
        customer: UnifiedCustomer,
        new_identity: CustomerIdentity
    ):
        """合并客户信息"""
        # 优先使用非空值
        if not customer.name and new_identity.name:
            customer.name = new_identity.name
        if not customer.phone and new_identity.phone:
            customer.phone = new_identity.phone
        if not customer.email and new_identity.email:
            customer.email = new_identity.email
    
    async def get_unified_customer(
        self,
        platform: str,
        platform_shop_id: str,
        customer_id: str
    ) -> Optional[UnifiedCustomer]:
        """
        获取统一客户档案
        
        Args:
            platform: 平台标识
            platform_shop_id: 平台店铺ID
            customer_id: 平台客户ID
            
        Returns:
            统一客户档案，未找到返回None
        """
        identity_key = f"{platform}:{platform_shop_id}:{customer_id}"
        unified_id = self.identity_index.get(identity_key)
        
        if unified_id:
            return self.unified_customers.get(unified_id)
        
        return None
    
    async def get_or_create_unified_customer(
        self,
        platform: str,
        platform_shop_id: str,
        customer_id: str,
        customer_info: Dict = None
    ) -> UnifiedCustomer:
        """
        获取或创建统一客户档案
        
        Args:
            platform: 平台标识
            platform_shop_id: 平台店铺ID
            customer_id: 平台客户ID
            customer_info: 客户信息（用于创建新档案）
            
        Returns:
            统一客户档案
        """
        existing = await self.get_unified_customer(platform, platform_shop_id, customer_id)
        if existing:
            return existing
        
        # 创建新身份
        info = customer_info or {}
        identity = CustomerIdentity(
            customer_id=customer_id,
            platform=platform,
            platform_shop_id=platform_shop_id,
            phone=info.get("phone"),
            email=info.get("email"),
            name=info.get("name"),
            device_id=info.get("device_id"),
            address_hash=info.get("address_hash")
        )
        
        return await self.register_identity(identity)
    
    async def update_customer_stats(
        self,
        unified_id: str,
        order_amount: float = 0,
        is_new_order: bool = False
    ):
        """更新客户统计信息"""
        customer = self.unified_customers.get(unified_id)
        if not customer:
            return
        
        if is_new_order:
            customer.total_orders += 1
        
        customer.total_spent += order_amount
        customer.updated_at = datetime.now()
    
    async def add_customer_tag(self, unified_id: str, tag: str):
        """添加客户标签"""
        customer = self.unified_customers.get(unified_id)
        if customer and tag not in customer.tags:
            customer.tags.append(tag)
            customer.updated_at = datetime.now()
    
    async def remove_customer_tag(self, unified_id: str, tag: str):
        """移除客户标签"""
        customer = self.unified_customers.get(unified_id)
        if customer and tag in customer.tags:
            customer.tags.remove(tag)
            customer.updated_at = datetime.now()
    
    async def find_related_customers(
        self,
        unified_id: str,
        min_similarity: float = 0.6
    ) -> List[Tuple[UnifiedCustomer, float]]:
        """
        查找相关的客户
        
        Args:
            unified_id: 统一客户ID
            min_similarity: 最小相似度
            
        Returns:
            (相关客户, 相似度) 列表
        """
        customer = self.unified_customers.get(unified_id)
        if not customer:
            return []
        
        related = []
        
        for other_id, other_customer in self.unified_customers.items():
            if other_id == unified_id:
                continue
            
            # 计算两个统一客户之间的相似度
            max_similarity = 0.0
            for identity1 in customer.identities:
                for identity2 in other_customer.identities:
                    sim = CustomerIdentityMatcher.calculate_similarity(identity1, identity2)
                    max_similarity = max(max_similarity, sim)
            
            if max_similarity >= min_similarity:
                related.append((other_customer, max_similarity))
        
        # 按相似度排序
        related.sort(key=lambda x: x[1], reverse=True)
        return related
    
    def get_customer_platforms(self, unified_id: str) -> List[str]:
        """获取客户关联的所有平台"""
        customer = self.unified_customers.get(unified_id)
        if not customer:
            return []
        
        return list(customer.get_all_platforms())
    
    async def merge_customers(
        self,
        unified_id_1: str,
        unified_id_2: str
    ) -> Optional[UnifiedCustomer]:
        """
        手动合并两个客户档案
        
        Args:
            unified_id_1: 第一个客户ID
            unified_id_2: 第二个客户ID
            
        Returns:
            合并后的客户档案
        """
        customer1 = self.unified_customers.get(unified_id_1)
        customer2 = self.unified_customers.get(unified_id_2)
        
        if not customer1 or not customer2:
            return None
        
        # 合并身份
        customer1.identities.extend(customer2.identities)
        
        # 合并统计信息
        customer1.total_orders += customer2.total_orders
        customer1.total_spent += customer2.total_spent
        
        # 合并标签
        customer1.tags = list(set(customer1.tags + customer2.tags))
        
        # 更新索引
        for identity in customer2.identities:
            self.identity_index[identity.get_key()] = unified_id_1
            if identity.phone:
                self.phone_index[identity.phone] = unified_id_1
            if identity.email:
                self.email_index[identity.email] = unified_id_1
        
        # 删除第二个客户
        del self.unified_customers[unified_id_2]
        
        customer1.updated_at = datetime.now()
        return customer1


# 全局服务实例
_unification_service: Optional[CustomerUnificationService] = None


def get_unification_service() -> CustomerUnificationService:
    """获取客户统一服务实例"""
    global _unification_service
    if _unification_service is None:
        _unification_service = CustomerUnificationService()
    return _unification_service
