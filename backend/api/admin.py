"""
Django 管理后台配置模块
======================
基于 SimpleUI 美化主题的管理后台，包含：

1. 数据看板 (DashboardAdmin) —— 独立模块
   - 景点数量、用户数量、日记数量统计
   - 城市景点分布图表（柱状图）
   - 兴趣标签分布图表（饼图）

2. 模型管理类（5个 ModelAdmin）
   - SpotAdmin: 景点管理
   - FavoriteAdmin: 收藏管理
   - TravelDiaryAdmin: 日记管理
   - SpotTipAdmin: 攻略管理
   - SavedPlanAdmin: 行程管理

每个管理类配置了：
- list_display: 列表页显示的字段
- list_filter: 右侧筛选器
- search_fields: 搜索框可搜索的字段
- fieldsets: 详情页的字段分组
"""

import json
from collections import Counter
from django.contrib import admin
from django.contrib.auth.models import User
from django.db.models import Count
from .models import Spot, Favorite, TravelDiary, SpotTip, SavedPlan, DashboardProxy


# ==================== 站点标题配置 ====================
# 自定义管理后台的标题和品牌信息
admin.site.site_header = '🧳 智能旅游推荐系统 - 管理后台'
admin.site.site_title = '旅游管理系统'
admin.site.index_title = '系统管理'


# ==================== 数据看板（独立模块） ====================

@admin.register(DashboardProxy)
class DashboardAdmin(admin.ModelAdmin):
    """
    数据看板 —— 独立管理模块，与景点列表同级

    通过代理模型 DashboardProxy 注册为独立的管理后台条目，
    访问 /admin/api/dashboardproxy/ 即可查看数据看板。
    """
    change_list_template = 'admin/dashboard.html'

    def changelist_view(self, request, extra_context=None):
        # 基础统计数据
        spot_count = Spot.objects.count()
        user_count = User.objects.count()
        diary_count = TravelDiary.objects.count()

        # 各城市景点数量（用于柱状图）
        city_data = (
            Spot.objects.values('city')
            .annotate(count=Count('id'))
            .order_by('city')
        )
        city_labels = [d['city'] for d in city_data]
        city_counts = [d['count'] for d in city_data]

        # 兴趣标签分布（用于饼图）
        tag_counter = Counter()
        for spot in Spot.objects.values_list('tags', flat=True):
            if spot:
                for tag in spot.split(','):
                    tag = tag.strip()
                    if tag:
                        tag_counter[tag] += 1
        tag_top = tag_counter.most_common(8)
        tag_labels = [t[0] for t in tag_top]
        tag_counts = [t[1] for t in tag_top]

        extra_context = extra_context or {}
        extra_context.update({
            'spot_count': spot_count,
            'user_count': user_count,
            'diary_count': diary_count,
            'city_labels': json.dumps(city_labels, ensure_ascii=False),
            'city_counts': json.dumps(city_counts),
            'tag_labels': json.dumps(tag_labels, ensure_ascii=False),
            'tag_counts': json.dumps(tag_counts),
            'title': '数据看板',
        })
        return super().changelist_view(request, extra_context)


# ==================== 景点管理 ====================

@admin.register(Spot)
class SpotAdmin(admin.ModelAdmin):
    """
    景点管理后台配置

    功能：
    - 列表页：显示 ID、名称、城市、价格、游玩时长、评分、标签
    - 支持按城市和评分筛选
    - 支持按名称/城市/标签/地址搜索
    - 价格和评分支持列表页直接编辑
    - 详情页分三组：基础信息、消费与规划、算法特征
    """
    list_display = ('id', 'name', 'city', 'price', 'duration', 'rating', 'tags')
    list_display_links = ('id', 'name')  # ID 和名称可点击进入详情
    list_filter = ('city', 'rating')     # 右侧筛选器
    search_fields = ('name', 'city', 'tags', 'address')  # 搜索框
    list_editable = ('price', 'rating')  # 列表页可直接编辑
    ordering = ('city', '-rating')       # 默认排序：城市升序，评分降序
    list_per_page = 20                   # 每页显示20条

    # 详情页字段分组
    fieldsets = (
        ('基础信息', {
            'fields': ('name', 'city', 'address', 'description', 'image_url')
        }),
        ('消费与规划', {
            'fields': ('price', 'duration')
        }),
        ('算法特征', {
            'fields': ('longitude', 'latitude', 'tags', 'rating'),
            'description': '经纬度和标签用于路线规划算法'
        }),
    )


# ==================== 收藏管理 ====================

@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    """
    用户收藏管理后台配置

    功能：查看和管理用户的收藏记录
    支持按收藏时间筛选、按用户名和景点名搜索
    """
    list_display = ('id', 'user', 'spot', 'created_at')
    list_display_links = ('id',)
    list_filter = ('created_at',)
    search_fields = ('user__username', 'spot__name')  # 支持关联字段搜索
    ordering = ('-created_at',)
    list_per_page = 20
    readonly_fields = ('created_at',)  # 收藏时间只读


# ==================== 旅行日记管理 ====================

@admin.register(TravelDiary)
class TravelDiaryAdmin(admin.ModelAdmin):
    """
    旅行日记管理后台配置

    功能：查看和管理用户发布的旅行日记
    详情页分三组：基本信息、日记内容、时间信息
    支持按城市/评分/时间筛选
    """
    list_display = ('id', 'title', 'user', 'city', 'rating', 'created_at')
    list_display_links = ('id', 'title')
    list_filter = ('city', 'rating', 'created_at')
    search_fields = ('title', 'user__username', 'city', 'content')
    ordering = ('-created_at',)
    list_per_page = 20
    readonly_fields = ('created_at', 'updated_at')

    # 详情页字段分组
    fieldsets = (
        ('基本信息', {
            'fields': ('user', 'title', 'city')
        }),
        ('日记内容', {
            'fields': ('content', 'rating')
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)  # 默认折叠
        }),
    )


# ==================== 景点攻略管理 ====================

@admin.register(SpotTip)
class SpotTipAdmin(admin.ModelAdmin):
    """
    景点攻略管理后台配置

    功能：查看和管理用户发布的景点攻略
    支持按攻略类型筛选
    """
    list_display = ('id', 'title', 'spot', 'user', 'tip_type', 'created_at')
    list_display_links = ('id', 'title')
    list_filter = ('tip_type', 'created_at')
    search_fields = ('title', 'spot__name', 'user__username', 'content')
    ordering = ('-created_at',)
    list_per_page = 20
    readonly_fields = ('created_at',)


# ==================== 行程管理 ====================

@admin.register(SavedPlan)
class SavedPlanAdmin(admin.ModelAdmin):
    """
    行程管理后台配置

    功能：查看和管理用户保存的行程规划
    支持按城市/预算等级筛选
    """
    list_display = ('id', 'name', 'user', 'city', 'days', 'budget', 'created_at')
    list_display_links = ('id', 'name')
    list_filter = ('city', 'budget', 'created_at')
    search_fields = ('name', 'user__username', 'city')
    ordering = ('-created_at',)
    list_per_page = 20
    readonly_fields = ('created_at',)
