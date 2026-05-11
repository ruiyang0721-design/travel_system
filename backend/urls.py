"""
URL 路由配置模块
================
定义所有 API 端点的 URL 映射，将 URL 路径分发到对应的视图函数。

路由分组：
1. 管理后台：/admin/
2. 景点相关：/api/spots/、/api/cities/、/api/city-stats/
3. 路线规划：/api/recommend/
4. 用户认证：/api/register/、/api/login/
5. 收藏功能：/api/favorites/
6. 旅行日记：/api/diaries/
7. 景点攻略：/api/tips/
8. 个人中心：/api/profile/
9. AI 对话：/api/ai/chat/
10. 行程管理：/api/plans/
"""

from django.contrib import admin
from django.urls import path
from backend.api.views import (
    # 景点相关
    get_spot_list, get_spot_detail, get_cities, get_city_stats,
    # 路线规划
    recommend_spots,
    # 用户认证
    register_user,
    # 收藏功能
    get_favorites, toggle_favorite, check_favorite,
    # 旅行日记
    get_diaries, create_diary, get_diary_detail, delete_diary, update_diary,
    # 景点攻略
    get_spot_tips, create_tip, update_tip,
    # 个人中心
    get_user_profile, change_password, get_user_diaries, get_user_tips,
    # AI 对话
    ai_chat,
    # 行程管理
    get_saved_plans, save_plan, delete_saved_plan,
)
# JWT Token 视图：登录时自动生成 access + refresh token
from rest_framework_simplejwt.views import TokenObtainPairView

urlpatterns = [
    # 管理后台（SimpleUI 美化主题）
    path('admin/', admin.site.urls),

    # ========== 景点相关 ==========
    path('api/spots/', get_spot_list),                          # 景点列表（支持搜索/标签/城市筛选）
    path('api/spots/<str:spot_name>/', get_spot_detail),          # 景点详情（含攻略）
    path('api/spots/<str:spot_name>/tips/', get_spot_tips),       # 某景点的攻略列表
    path('api/cities/', get_cities),                            # 城市列表及景点数量
    path('api/city-stats/', get_city_stats),                    # 城市统计信息

    # ========== 路线规划 ==========
    path('api/recommend/', recommend_spots),                    # 智能路线规划（核心接口）

    # ========== 用户认证 ==========
    path('api/register/', register_user),                       # 用户注册
    path('api/login/', TokenObtainPairView.as_view()),          # 用户登录（返回 JWT Token）

    # ========== 收藏功能 ==========
    path('api/favorites/', get_favorites),                      # 获取收藏列表（需登录）
    path('api/favorites/toggle/', toggle_favorite),             # 收藏/取消收藏（需登录）
    path('api/favorites/check/<int:spot_id>/', check_favorite), # 检查是否已收藏（需登录）

    # ========== 旅行日记 ==========
    path('api/diaries/', get_diaries),                          # 日记列表（支持城市筛选）
    path('api/diaries/create/', create_diary),                  # 发布日记（需登录）
    path('api/diaries/<int:diary_id>/', get_diary_detail),      # 日记详情
    path('api/diaries/<int:diary_id>/delete/', delete_diary),   # 删除日记（需登录，只能删自己的）
    path('api/diaries/<int:diary_id>/update/', update_diary),   # 编辑日记（需登录，只能改自己的）

    # ========== 景点攻略 ==========
    path('api/tips/create/', create_tip),                       # 发布攻略（需登录）
    path('api/tips/<int:tip_id>/update/', update_tip),          # 编辑攻略（需登录，只能改自己的）

    # ========== 个人中心 ==========
    path('api/profile/', get_user_profile),                     # 用户信息及统计
    path('api/profile/change-password/', change_password),      # 修改密码
    path('api/profile/diaries/', get_user_diaries),             # 用户的日记列表
    path('api/profile/tips/', get_user_tips),                   # 用户的攻略列表

    # ========== AI 智能规划 ==========
    path('api/ai/chat/', ai_chat),                              # AI 对话式旅行规划（SSE 流式）

    # ========== 行程管理 ==========
    path('api/plans/', get_saved_plans),                        # 获取保存的行程列表（需登录）
    path('api/plans/save/', save_plan),                         # 保存行程（需登录）
    path('api/plans/<int:plan_id>/delete/', delete_saved_plan), # 删除行程（需登录）
]
