"""
数据模型定义模块
================
定义系统中所有数据库表结构，共 5 个模型：
- Spot: 景点信息表（核心数据，82条记录覆盖7个城市）
- Favorite: 用户收藏表（用户-景点多对多关系）
- TravelDiary: 旅行日记表（用户发布的UGC内容）
- SpotTip: 景点攻略表（用户发布的实用建议）
- SavedPlan: 行程保存表（用户保存的规划结果）

E-R 关系：
  User 1:N Favorite N:1 Spot
  User 1:N TravelDiary
  User 1:N SpotTip N:1 Spot
  User 1:N SavedPlan
"""

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User


class Spot(models.Model):
    """
    景点信息表 —— 系统核心数据模型
    
    存储所有景点的基础信息、消费属性和算法特征。
    其中 longitude/latitude/tags/rating 是路线规划算法的关键输入字段。
    """
    
    # --- 1. 基础信息 ---
    name = models.CharField(max_length=100, verbose_name="景点名称")
    city = models.CharField(max_length=50, default="北京", verbose_name="所属城市")
    address = models.CharField(max_length=200, blank=True, null=True, verbose_name="详细地址")
    description = models.TextField(blank=True, null=True, verbose_name="景点简介")
    image_url = models.URLField(max_length=500, blank=True, null=True, verbose_name="图片链接")
    
    # --- 2. 消费与规划属性 ---
    # price: 用于预算计算模块，免费景点为 0
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0.00, verbose_name="门票价格(元)")
    # duration: 建议游玩时长(小时)，用于候选景点召回的时间预算截断和聚类时间均衡
    duration = models.FloatField(verbose_name="游玩时间(小时)")
    
    # --- 3. 算法核心特征 ---
    # longitude/latitude: 经纬度坐标，用于 K-means 空间聚类和遗传算法距离计算
    longitude = models.FloatField(verbose_name="经度")
    latitude = models.FloatField(verbose_name="纬度")
    # tags: 兴趣标签(逗号分隔)，用于标签匹配评分，如 "历史,文化,园林"
    tags = models.CharField(max_length=200, verbose_name="兴趣标签")
    # rating: 景点评分(0-5)，用于候选景点的基础评分公式中的归一化评分
    rating = models.FloatField(verbose_name="评分", validators=[
            MinValueValidator(0),
            MaxValueValidator(5)
        ])

    class Meta:
        verbose_name = '景点'
        verbose_name_plural = '景点'

    def __str__(self):
        return f"{self.name} ({self.city})"


class Favorite(models.Model):
    """
    用户收藏表 —— 记录用户收藏的景点
    
    用于两个场景：
    1. 前端"我的收藏"页面展示
    2. 协同过滤算法(Item-based CF)的用户-景点交互矩阵数据源
       cf.py 通过 Favorite 表构建 user-spot 矩阵，计算景点间余弦相似度
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites', verbose_name="用户")
    spot = models.ForeignKey(Spot, on_delete=models.CASCADE, related_name='favorited_by', verbose_name="景点")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="收藏时间")

    class Meta:
        unique_together = ('user', 'spot')  # 联合唯一约束，防止同一用户重复收藏同一景点
        ordering = ['-created_at']  # 按收藏时间倒序排列
        verbose_name = "收藏"
        verbose_name_plural = "收藏"

    def __str__(self):
        return f"{self.user.username} 收藏了 {self.spot.name}"


class TravelDiary(models.Model):
    """
    旅行日记表 —— 用户发布的旅行记录
    
    功能：用户可以发布旅行日记，记录旅行经历和感受。
    支持按城市筛选浏览，在"旅行日记广场"页面展示。
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='diaries', verbose_name="用户")
    title = models.CharField(max_length=200, verbose_name="日记标题")
    city = models.CharField(max_length=50, verbose_name="旅行城市")
    content = models.TextField(verbose_name="日记内容")
    rating = models.IntegerField(default=5, verbose_name="旅行评分", validators=[
        MinValueValidator(1), MaxValueValidator(5)
    ])
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        ordering = ['-created_at']  # 最新的日记排在前面
        verbose_name = "旅行日记"
        verbose_name_plural = "旅行日记"

    def __str__(self):
        return f"{self.title} - {self.user.username}"


class SpotTip(models.Model):
    """
    景点攻略表 —— 用户发布的实用建议
    
    功能：用户可以在景点详情页发布攻略，分享旅行经验。
    支持 5 种类型：实用建议/避坑指南/美食推荐/交通攻略/拍照技巧
    """
    spot = models.ForeignKey(Spot, on_delete=models.CASCADE, related_name='tips', verbose_name="景点")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tips', verbose_name="发布者")
    title = models.CharField(max_length=100, verbose_name="标题")
    content = models.TextField(verbose_name="内容")
    # tip_type: 攻略分类，使用 choices 限制可选值
    tip_type = models.CharField(max_length=20, default='实用建议', verbose_name="类型", choices=[
        ('实用建议', '实用建议'),
        ('避坑指南', '避坑指南'),
        ('美食推荐', '美食推荐'),
        ('交通攻略', '交通攻略'),
        ('拍照技巧', '拍照技巧'),
    ])
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="发布时间")

    class Meta:
        ordering = ['-created_at']
        verbose_name = "景点攻略"
        verbose_name_plural = "景点攻略"

    def __str__(self):
        return f"{self.spot.name} - {self.title}"


class SavedPlan(models.Model):
    """
    行程保存表 —— 用户保存的规划结果
    
    功能：用户在规划结果页点击"保存行程"后，行程数据以 JSON 格式存储。
    plan_data 字段存储完整的按天分组的景点列表（含酒店节点），
    格式如 {"第1天": [{id, name, ...}, ...], "第2天": [...]}
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_plans', verbose_name="用户")
    name = models.CharField(max_length=200, verbose_name="行程名称")
    city = models.CharField(max_length=50, verbose_name="城市")
    days = models.IntegerField(verbose_name="天数")
    tags = models.CharField(max_length=200, blank=True, verbose_name="兴趣标签")
    budget = models.CharField(max_length=20, default='mid', verbose_name="预算等级")
    # plan_data: JSON 格式存储完整行程数据，包含每天的景点列表和酒店节点
    plan_data = models.JSONField(verbose_name="行程数据")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        ordering = ['-created_at']
        verbose_name = "行程管理"
        verbose_name_plural = "行程管理"

    def __str__(self):
        return f"{self.name} - {self.user.username}"


class DashboardProxy(Spot):
    """数据看板代理模型 —— 用于在管理后台独立展示数据看板"""
    class Meta:
        proxy = True
        verbose_name = '数据看板'
        verbose_name_plural = '数据看板'
