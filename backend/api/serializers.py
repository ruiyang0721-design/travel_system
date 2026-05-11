"""
DRF 序列化器模块
================
定义 Django REST Framework 的序列化器，负责：
1. 将数据库模型实例转换为 JSON 格式（序列化）
2. 将前端提交的 JSON 数据验证并转换为模型实例（反序列化）

共 5 个序列化器，与 models.py 中的 5 个模型一一对应。
"""

from rest_framework import serializers
from .models import Spot, Favorite, TravelDiary, SpotTip, SavedPlan


class SpotSerializer(serializers.ModelSerializer):
    """
    景点序列化器
    
    用途：
    - 景点列表接口 (GET /api/spots/) 返回景点数据
    - 景点详情接口 (GET /api/spots/<id>/) 返回单个景点
    - 规划结果中序列化每个景点节点
    
    fields='__all__' 表示包含 Spot 模型的所有字段
    """
    class Meta:
        model = Spot
        fields = '__all__'


class FavoriteSerializer(serializers.ModelSerializer):
    """
    收藏序列化器
    
    用途：收藏列表接口 (GET /api/favorites/) 返回用户的收藏记录
    
    字段说明：
    - spot: 嵌套的景点序列化器（只读），用于展示收藏的景点详情
    - spot_id: 写入字段，用于创建收藏时接收景点ID
    - created_at: 收藏时间（自动填充）
    
    读取时返回完整的景点信息，写入时只需要 spot_id
    """
    spot = SpotSerializer(read_only=True)  # 嵌套序列化：读取时展开景点详情
    spot_id = serializers.IntegerField(write_only=True)  # 写入时只需要景点ID

    class Meta:
        model = Favorite
        fields = ['id', 'spot', 'spot_id', 'created_at']


class TravelDiarySerializer(serializers.ModelSerializer):
    """
    旅行日记序列化器
    
    用途：
    - 日记列表接口 (GET /api/diaries/) 返回日记列表
    - 日记详情接口 (GET /api/diaries/<id>/) 返回单篇日记
    - 创建日记接口 (POST /api/diaries/create/) 接收日记数据
    
    额外字段：
    - username: 从关联的 user 对象中提取用户名（只读），用于前端展示作者名
    """
    username = serializers.CharField(source='user.username', read_only=True)
    class Meta:
        model = TravelDiary
        fields = ['id', 'title', 'city', 'content', 'rating', 'username', 'created_at', 'updated_at']
        read_only_fields = ['username']  # username 只读，由后端自动填充


class SpotTipSerializer(serializers.ModelSerializer):
    """
    景点攻略序列化器
    
    用途：
    - 攻略列表接口 (GET /api/spots/<id>/tips/) 返回某景点的攻略
    - 创建攻略接口 (POST /api/tips/create/) 接收攻略数据
    
    额外字段：
    - username: 发布者用户名（只读）
    - type_display: 攻略类型的中文显示值（只读），如 "实用建议"
    - spot_name: 关联景点的名称（只读），用于攻略列表展示
    """
    username = serializers.CharField(source='user.username', read_only=True)
    type_display = serializers.CharField(source='get_tip_type_display', read_only=True)
    spot_name = serializers.CharField(source='spot.name', read_only=True)

    class Meta:
        model = SpotTip
        fields = ['id', 'spot', 'spot_name', 'title', 'content', 'tip_type', 'type_display', 'username', 'created_at']
        read_only_fields = ['username']


class SavedPlanSerializer(serializers.ModelSerializer):
    """
    行程序列化器
    
    用途：
    - 行程列表接口 (GET /api/plans/) 返回用户保存的行程
    - 保存行程接口 (POST /api/plans/save/) 接收行程数据
    
    plan_data 字段存储完整的 JSON 行程数据（按天分组的景点列表）
    """
    class Meta:
        model = SavedPlan
        fields = ['id', 'name', 'city', 'days', 'tags', 'budget', 'plan_data', 'created_at']
        read_only_fields = ['id', 'created_at']
