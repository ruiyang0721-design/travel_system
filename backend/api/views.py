"""
视图函数模块
============
定义所有 API 接口的业务逻辑，共 20+ 个视图函数，分为以下几组：

1. 景点相关：列表、详情、城市统计
2. 路线规划：调用算法引擎生成行程
3. 用户认证：注册、登录（JWT）
4. 收藏功能：收藏/取消收藏、检查收藏状态
5. 旅行日记：发布、查看、删除日记
6. 景点攻略：发布攻略、获取攻略列表
7. 个人中心：用户信息、修改密码、用户自己的日记/攻略
8. AI 对话：接入 DeepSeek 大模型的流式对话
9. 行程管理：保存、查看、删除行程
"""

from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.db.models import Count, Avg
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from .models import Spot, Favorite, TravelDiary, SpotTip, SavedPlan
from .serializers import SpotSerializer, FavoriteSerializer, TravelDiarySerializer, SpotTipSerializer, SavedPlanSerializer
from .planner.planner import generate_itinerary_with_hotel

import json
from django.http import StreamingHttpResponse
from openai import OpenAI


# ==================== 景点相关 ====================

@api_view(['GET'])
def get_spot_list(request):
    """
    获取景点列表接口
    
    URL: GET /api/spots/
    
    查询参数（均可选）：
    - search: 按景点名称模糊搜索
    - tag: 按兴趣标签筛选
    - city: 按城市筛选
    
    返回：景点列表的 JSON 数据
    """
    search_query = request.query_params.get('search', '')
    tag_query = request.query_params.get('tag', '')
    city_query = request.query_params.get('city', '')

    spots = Spot.objects.all()

    # 按条件逐步过滤
    if city_query:
        spots = spots.filter(city=city_query)
    if search_query:
        spots = spots.filter(name__icontains=search_query)
    if tag_query:
        spots = spots.filter(tags__icontains=tag_query)

    serializer = SpotSerializer(spots, many=True)
    return Response({
        "status": "success",
        "data": serializer.data
    })


@api_view(['GET'])
def get_spot_detail(request, spot_name):
    """
    获取单个景点详情接口
    
    URL: GET /api/spots/<spot_name>/
    
    返回：景点详情 + 该景点的攻略列表（最多10条）
    """
    try:
        spot = Spot.objects.get(name=spot_name)
    except Spot.DoesNotExist:
        return Response({"status": "error", "message": "景点不存在"}, status=404)

    spot_data = SpotSerializer(spot).data
    # 附带该景点的攻略（最多返回10条）
    tips = SpotTip.objects.filter(spot=spot)[:10]
    spot_data['tips'] = SpotTipSerializer(tips, many=True).data

    return Response({"status": "success", "data": spot_data})


@api_view(['GET'])
def get_cities(request):
    """
    获取所有城市列表及景点数量
    
    URL: GET /api/cities/
    
    返回：每个城市的名称和景点数量，按景点数降序排列
    """
    cities = Spot.objects.values('city').annotate(count=Count('id')).order_by('-count')
    return Response({"status": "success", "data": list(cities)})


@api_view(['GET'])
def get_city_stats(request):
    """
    获取城市统计信息
    
    URL: GET /api/city-stats/?city=北京
    
    返回：城市的景点数、平均评分、平均门票、免费景点数、所有标签
    """
    city = request.query_params.get('city', '')
    if not city:
        return Response({"status": "error", "message": "请提供城市参数"}, status=400)

    spots = Spot.objects.filter(city=city)
    if not spots.exists():
        return Response({"status": "error", "message": f"暂未收录{city}的数据"}, status=404)

    stats = {
        'city': city,
        'total_spots': spots.count(),
        'avg_rating': round(spots.aggregate(avg=Avg('rating'))['avg'], 1),
        'avg_price': round(float(spots.aggregate(avg=Avg('price'))['avg']), 0),
        'free_spots': spots.filter(price=0).count(),
        'tags': list(set(
            tag.strip()
            for spot in spots
            for tag in spot.tags.replace('，', ',').split(',')
            if tag.strip()
        )),
    }
    return Response({"status": "success", "data": stats})


# ==================== 路线规划 ====================

def build_recommendation_explanation(user_data, formatted_itinerary, budget, user=None, must_include_ids=None):
    """
    构建推荐结果解释文案

    说明：
    - 不依赖大模型，直接基于用户输入和算法输出生成稳定、可解释的说明。
    - 前端用于展示"为什么这样推荐"，提升推荐结果可信度。
    """
    city = user_data.get('city', '北京')
    days = int(user_data.get('days', 1))
    tags = user_data.get('tags', []) or []
    tag_text = '、'.join(tags) if tags else '综合兴趣'
    must_include_count = len(must_include_ids or [])
    has_hotel = bool(user_data.get('hotel'))

    all_spots = []
    daily_explanations = []

    for day_name, route_nodes in formatted_itinerary.items():
        day_spots = [
            node for node in route_nodes
            if not (isinstance(node, dict) and node.get('is_hotel'))
        ]
        all_spots.extend(day_spots)

        day_cost = sum(float(spot.price) if spot.price else 0 for spot in day_spots)
        day_duration = sum(spot.duration if spot.duration else 0 for spot in day_spots)
        matched_tags = sorted(set(
            tag.strip()
            for spot in day_spots
            for tag in spot.tags.replace('，', ',').split(',')
            if tag.strip() and (not tags or tag.strip() in tags)
        ))
        high_rating_spots = [spot.name for spot in day_spots if spot.rating >= 4.8][:3]

        tag_sentence = (
            f"覆盖了{ '、'.join(matched_tags) }等偏好标签"
            if matched_tags else
            "兼顾了评分、游玩时长和空间位置"
        )
        rating_sentence = (
            f"其中{ '、'.join(high_rating_spots) }评分较高"
            if high_rating_spots else
            "整体安排保持了较均衡的游玩强度"
        )

        daily_explanations.append({
            "day": day_name,
            "spot_count": len(day_spots),
            "duration": round(day_duration, 1),
            "cost": int(round(day_cost, 0)),
            "text": (
                f"{day_name}安排了{len(day_spots)}个景点，预计游玩{round(day_duration, 1)}小时，"
                f"门票约{int(round(day_cost, 0))}元。系统将地理位置相近的景点聚合在同一天，"
                f"{tag_sentence}，{rating_sentence}。"
            )
        })

    spot_count = len(all_spots)
    avg_rating = round(sum(spot.rating for spot in all_spots) / spot_count, 1) if spot_count else 0

    reasons = [
        f"根据你选择的{city}、{days}天和{tag_text}偏好，优先召回标签匹配度高的景点。",
        "候选景点综合考虑标签匹配、景点评分和游玩时长，避免行程过满。",
        "系统使用 K-means 按经纬度将景点分天，让同一天的景点尽量集中，减少跨区域奔波。",
        "每天内部会枚举不同游览顺序，选择总距离更短的路线。"
    ]

    if user and user.is_authenticated:
        city_favorite_count = Favorite.objects.filter(user=user, spot__city=city).count()
        if city_favorite_count > 0:
            reasons.insert(1, f"你在{city}已有{city_favorite_count}个收藏景点，系统会结合收藏行为进行个性化加权。")
        else:
            reasons.insert(1, "当前账号在该城市暂无收藏记录，本次主要依据兴趣标签和景点评分进行推荐。")

    if must_include_count > 0:
        reasons.append(f"你指定了{must_include_count}个必去收藏景点，系统已优先纳入候选行程。")

    if has_hotel:
        reasons.append("你指定了住宿位置，因此每天路线按酒店出发并返回酒店的闭环方式组织。")
    else:
        reasons.append("你未指定酒店，系统根据候选景点中心位置生成推荐住宿区域。")

    return {
        "summary": (
            f"本次为你生成了{city}{days}天{tag_text}主题行程，"
            f"共包含{spot_count}个景点，平均评分约{avg_rating}分，"
            f"总门票约{int(round(budget.get('total_cost', 0), 0))}元，"
            f"预计总游玩时长{budget.get('total_duration', 0)}小时。"
        ),
        "reasons": reasons,
        "daily": daily_explanations,
    }


@api_view(['POST'])
def recommend_spots(request):
    """
    智能路线规划接口（系统核心功能）
    
    URL: POST /api/recommend/
    
    请求体：
    {
        "city": "北京",          # 目标城市（必填）
        "days": 3,               # 游玩天数（必填）
        "tags": ["历史", "文化"], # 兴趣标签（必填）
        "hotel": {               # 酒店信息（可选）
            "name": "全季酒店",
            "lat": 39.909,
            "lng": 116.397
        }
    }
    
    返回：
    {
        "status": "success",
        "city": "北京",
        "data": {
            "第1天": [酒店节点, 景点A, 景点B, 酒店节点],
            "第2天": [...],
            ...
        },
        "budget": {
            "total_cost": 180.0,      # 门票总计
            "total_duration": 24.5,   # 总游玩时长
            "days": 3
        }
    }
    """
    user_data = request.data
    city = user_data.get('city', '北京')
    client_hotel = user_data.get('hotel', None)
    must_include_ids = user_data.get('must_include', [])
    
    # 获取当前登录用户（用于协同过滤），匿名用户传 None
    user = request.user if request.user.is_authenticated else None
    
    # 调用算法引擎生成行程
    try:
        formatted_itinerary = generate_itinerary_with_hotel(user_data, client_hotel, user=user, must_include_ids=must_include_ids)
    except ValueError as e:
        return Response({"status": "error", "message": str(e)}, status=400)
    if not formatted_itinerary:
        return Response({"status": "error", "message": f"暂未收录 {city} 的数据。"}, status=400)

    # 计算预算汇总
    total_cost = 0
    total_duration = 0
    for day, route_nodes in formatted_itinerary.items():
        for node in route_nodes:
            # 跳过酒店节点（酒店不是收费景点）
            if not (isinstance(node, dict) and node.get('is_hotel')):
                total_cost += float(node.price) if node.price else 0
                total_duration += node.duration if node.duration else 0

    # 序列化行程数据（将 Spot 对象转为 JSON）
    serialized_plan = {}
    for day, route_nodes in formatted_itinerary.items():
        daily_json = []
        for node in route_nodes:
            if isinstance(node, dict) and node.get('is_hotel'):
                daily_json.append(node)  # 酒店节点已经是 dict，直接使用
            else:
                daily_json.append(SpotSerializer(node).data)  # 景点对象需要序列化
        serialized_plan[day] = daily_json

    budget = {
        "total_cost": total_cost,
        "total_duration": round(total_duration, 1),
        "days": int(user_data.get('days', 1)),
    }
    explanation = build_recommendation_explanation(
        user_data,
        formatted_itinerary,
        budget,
        user=user,
        must_include_ids=must_include_ids
    )

    return Response({
        "status": "success",
        "city": city,
        "data": serialized_plan,
        "budget": budget,
        "explanation": explanation,
    })


# ==================== 用户认证 ====================

@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    """
    用户注册接口
    
    URL: POST /api/register/
    
    请求体：{"username": "test", "password": "123456"}
    
    返回：注册成功/失败的消息
    """
    username = request.data.get('username')
    password = request.data.get('password')

    if not username or not password:
        return Response({"error": "用户名和密码不能为空！"}, status=status.HTTP_400_BAD_REQUEST)

    if User.objects.filter(username=username).exists():
        return Response({"error": "该用户名已经被注册了，换一个吧~"}, status=status.HTTP_400_BAD_REQUEST)

    # 使用 make_password 加密存储密码（PBKDF2 算法）
    user = User.objects.create(
        username=username,
        password=make_password(password)
    )

    return Response({
        "status": "success",
        "message": "注册成功！欢迎加入智能旅游平台！"
    })


# ==================== 收藏功能 ====================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_favorites(request):
    """
    获取当前用户的收藏列表
    
    URL: GET /api/favorites/
    认证：需要 JWT Token
    
    返回：用户收藏的景点列表（包含完整的景点信息）
    """
    favorites = Favorite.objects.filter(user=request.user)
    serializer = FavoriteSerializer(favorites, many=True)
    return Response({"status": "success", "data": serializer.data})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_favorite(request):
    """
    收藏/取消收藏接口（切换模式）
    
    URL: POST /api/favorites/toggle/
    认证：需要 JWT Token
    
    请求体：{"spot_id": 1}
    
    逻辑：
    - 如果未收藏 → 创建收藏记录
    - 如果已收藏 → 删除收藏记录
    """
    spot_id = request.data.get('spot_id')
    if not spot_id:
        return Response({"status": "error", "message": "缺少景点ID"}, status=400)

    try:
        spot = Spot.objects.get(id=spot_id)
    except Spot.DoesNotExist:
        return Response({"status": "error", "message": "景点不存在"}, status=404)

    # get_or_create: 如果不存在则创建，存在则获取
    fav, created = Favorite.objects.get_or_create(user=request.user, spot=spot)
    if not created:
        # 已收藏 → 取消收藏
        fav.delete()
        return Response({"status": "success", "action": "removed", "message": "已取消收藏"})
    
    # 新收藏
    return Response({"status": "success", "action": "added", "message": "已收藏"})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_favorite(request, spot_id):
    """
    检查是否已收藏某景点
    
    URL: GET /api/favorites/check/<spot_id>/
    认证：需要 JWT Token
    
    返回：{"is_favorite": true/false}
    """
    is_fav = Favorite.objects.filter(user=request.user, spot_id=spot_id).exists()
    return Response({"status": "success", "is_favorite": is_fav})


# ==================== 旅行日记 ====================

@api_view(['GET'])
def get_diaries(request):
    """
    获取旅行日记列表（日记广场）
    
    URL: GET /api/diaries/
    查询参数：city（可选，按城市筛选）
    
    返回：最多20条日记，按创建时间倒序
    """
    city = request.query_params.get('city', '')
    diaries = TravelDiary.objects.all()
    if city:
        diaries = diaries.filter(city=city)
    diaries = diaries[:20]  # 限制返回数量
    serializer = TravelDiarySerializer(diaries, many=True)
    return Response({"status": "success", "data": serializer.data})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_diary(request):
    """
    发布旅行日记
    
    URL: POST /api/diaries/create/
    认证：需要 JWT Token
    
    请求体：{"title": "...", "city": "北京", "content": "...", "rating": 5}
    """
    data = request.data.copy()
    serializer = TravelDiarySerializer(data=data)
    if serializer.is_valid():
        serializer.save(user=request.user)  # 自动关联当前登录用户
        return Response({"status": "success", "data": serializer.data}, status=201)
    return Response({"status": "error", "errors": serializer.errors}, status=400)


@api_view(['GET'])
def get_diary_detail(request, diary_id):
    """
    获取日记详情
    
    URL: GET /api/diaries/<diary_id>/
    """
    try:
        diary = TravelDiary.objects.get(id=diary_id)
    except TravelDiary.DoesNotExist:
        return Response({"status": "error", "message": "日记不存在"}, status=404)
    serializer = TravelDiarySerializer(diary)
    return Response({"status": "success", "data": serializer.data})


# ==================== 景点攻略 ====================

@api_view(['GET'])
def get_spot_tips(request, spot_name):
    """
    获取某景点的所有攻略
    
    URL: GET /api/spots/<spot_name>/tips/
    """
    try:
        spot = Spot.objects.get(name=spot_name)
    except Spot.DoesNotExist:
        return Response({"status": "error", "message": "景点不存在"}, status=404)
    tips = SpotTip.objects.filter(spot=spot)
    serializer = SpotTipSerializer(tips, many=True)
    return Response({"status": "success", "data": serializer.data})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_tip(request):
    """
    发布景点攻略

    URL: POST /api/tips/create/
    认证：需要 JWT Token

    请求体：{"spot": 1, "title": "...", "content": "...", "tip_type": "实用建议"}
    """
    data = request.data.copy()
    serializer = SpotTipSerializer(data=data)
    if serializer.is_valid():
        serializer.save(user=request.user)  # 自动关联当前登录用户
        return Response({"status": "success", "data": serializer.data}, status=201)
    return Response({"status": "error", "errors": serializer.errors}, status=400)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_tip(request, tip_id):
    """
    编辑景点攻略（只能编辑自己的攻略）

    URL: PUT /api/tips/<tip_id>/update/
    认证：需要 JWT Token
    请求体：{"title": "...", "content": "...", "tip_type": "实用建议"}
    """
    try:
        tip = SpotTip.objects.get(id=tip_id, user=request.user)
    except SpotTip.DoesNotExist:
        return Response({"status": "error", "message": "攻略不存在或无权编辑"}, status=404)

    serializer = SpotTipSerializer(tip, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({"status": "success", "data": serializer.data})
    return Response({"status": "error", "errors": serializer.errors}, status=400)


# ==================== 个人中心 ====================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_profile(request):
    """
    获取用户个人信息及统计
    
    URL: GET /api/profile/
    认证：需要 JWT Token
    
    返回：用户名、邮箱、注册时间、收藏数、日记数、攻略数
    """
    user = request.user
    stats = {
        'username': user.username,
        'email': user.email,
        'date_joined': user.date_joined,
        'favorites_count': Favorite.objects.filter(user=user).count(),
        'diaries_count': TravelDiary.objects.filter(user=user).count(),
        'trips_count': 0,
        'tips_count': SpotTip.objects.filter(user=user).count(),
    }
    return Response({"status": "success", "data": stats})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    """
    修改密码接口
    
    URL: POST /api/profile/change-password/
    认证：需要 JWT Token
    
    请求体：{"old_password": "...", "new_password": "..."}
    """
    old_password = request.data.get('old_password')
    new_password = request.data.get('new_password')

    if not old_password or not new_password:
        return Response({"status": "error", "message": "请提供旧密码和新密码"}, status=400)

    # 验证旧密码是否正确
    if not request.user.check_password(old_password):
        return Response({"status": "error", "message": "旧密码不正确"}, status=400)

    if len(new_password) < 6:
        return Response({"status": "error", "message": "新密码至少需要6位"}, status=400)

    request.user.set_password(new_password)
    request.user.save()
    return Response({"status": "success", "message": "密码修改成功"})


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_diary(request, diary_id):
    """
    删除旅行日记（只能删除自己的日记）

    URL: DELETE /api/diaries/<diary_id>/delete/
    认证：需要 JWT Token
    """
    try:
        diary = TravelDiary.objects.get(id=diary_id, user=request.user)
        diary.delete()
        return Response({"status": "success", "message": "日记已删除"})
    except TravelDiary.DoesNotExist:
        return Response({"status": "error", "message": "日记不存在或无权删除"}, status=404)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_diary(request, diary_id):
    """
    编辑旅行日记（只能编辑自己的日记）

    URL: PUT /api/diaries/<diary_id>/update/
    认证：需要 JWT Token
    请求体：{"title": "...", "city": "...", "content": "...", "rating": 5}
    """
    try:
        diary = TravelDiary.objects.get(id=diary_id, user=request.user)
    except TravelDiary.DoesNotExist:
        return Response({"status": "error", "message": "日记不存在或无权编辑"}, status=404)

    serializer = TravelDiarySerializer(diary, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({"status": "success", "data": serializer.data})
    return Response({"status": "error", "errors": serializer.errors}, status=400)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_diaries(request):
    """
    获取当前用户的旅行日记
    
    URL: GET /api/profile/diaries/
    认证：需要 JWT Token
    """
    diaries = TravelDiary.objects.filter(user=request.user)
    serializer = TravelDiarySerializer(diaries, many=True)
    return Response({"status": "success", "data": serializer.data})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_tips(request):
    """
    获取当前用户发布的攻略
    
    URL: GET /api/profile/tips/
    认证：需要 JWT Token
    """
    tips = SpotTip.objects.filter(user=request.user)
    serializer = SpotTipSerializer(tips, many=True)
    return Response({"status": "success", "data": serializer.data})


# ==================== AI 智能规划 ====================

# DeepSeek API 配置
DEEPSEEK_API_KEY = 'sk-7f6b37aa618c4409811cdbd2ea91f342'
DEEPSEEK_BASE_URL = 'https://api.deepseek.com'


def build_spot_context(city=None):
    """
    从数据库读取景点数据，构建 AI 上下文
    
    将景点信息格式化为文本，作为 DeepSeek 大模型的 System Prompt 一部分，
    让 AI 了解系统中有哪些景点可用。
    """
    spots = Spot.objects.all()
    if city:
        spots = spots.filter(city=city)
    spots = spots[:50]

    lines = []
    for s in spots:
        lines.append(
            f"- {s.name}({s.city}) | 标签:{s.tags} | 评分:{s.rating} | "
            f"门票:¥{s.price} | 游玩:{s.duration}h | 坐标:({s.latitude},{s.longitude})"
        )
    return "\n".join(lines)


# AI 对话的 System Prompt，定义 AI 的角色和行为规范
SYSTEM_PROMPT = """你是一个旅行需求收集助手，服务于一个拥有路线规划引擎的旅游推荐系统。

你的核心职责：通过对话收集用户的旅行需求参数，而不是自己生成行程。

你需要做的事：
1. 理解用户想去哪里、玩几天、有什么偏好
2. 如果信息不完整，主动追问（比如没说城市就问城市，没说天数就问天数）
3. 当所有关键信息齐全时，输出结构化的规划参数 JSON，交给后端引擎生成行程

你不需要做的事：
- 不要生成具体的行程安排（如"第一天去XX，第二天去XX"）
- 不要推荐具体景点
- 不要计算费用和路线
- 这些都交给后端的路线规划引擎处理

你的回复风格：
- 友好、简洁，适当使用 emoji
- 可以介绍系统功能、询问偏好、确认信息
- 收集到足够信息后，告诉用户"已为你整理好需求，点击下方按钮生成行程"

收集参数的标准：
- city：城市名（必填）
- days：天数（必填）
- tags：兴趣标签，如 历史/文化/自然/美食/亲子/现代/夜景/园林（至少1个）
- budget：预算等级 low/mid/high（可选，默认 mid）

当你准备好时，在回复末尾单独输出一个 JSON 块：
```json
{"action": "plan", "city": "城市名", "days": 天数, "tags": ["标签1", "标签2"], "budget": "low/mid/high"}
```
注意：只有在用户明确了城市和天数，并且至少有一个兴趣标签时才输出这个 JSON。如果信息不完整，继续对话询问。"""


@api_view(['POST'])
@permission_classes([AllowAny])
def ai_chat(request):
    """
    AI 对话式旅行规划接口（SSE 流式返回）
    
    URL: POST /api/ai/chat/
    
    请求体：
    {
        "message": "我想去北京玩3天",
        "history": [{"role": "user", "content": "..."}, ...]
    }
    
    返回：SSE (Server-Sent Events) 流式响应
    - type: "text" → AI 的文本回复（逐步推送）
    - type: "plan" → AI 提取的规划参数 JSON（当信息完整时）
    - type: "error" → 错误信息
    """
    user_message = request.data.get('message', '').strip()
    history = request.data.get('history', [])

    if not user_message:
        return Response({"status": "error", "message": "请输入内容"}, status=400)

    # 从用户消息中猜测城市，提取对应景点数据作为 AI 上下文
    city_keywords = ['北京', '上海', '成都', '西安', '杭州', '重庆', '广州']
    detected_city = None
    for c in city_keywords:
        if c in user_message:
            detected_city = c
            break

    spot_context = build_spot_context(detected_city)

    # 构建发送给 DeepSeek 的消息列表
    messages = [{"role": "system", "content": SYSTEM_PROMPT + "\n\n当前系统中的景点数据：\n" + spot_context}]
    # 加入对话历史（最多保留最近10轮）
    for h in history[-10:]:
        messages.append({"role": h.get("role", "user"), "content": h.get("content", "")})
    messages.append({"role": "user", "content": user_message})

    def stream_generator():
        """
        SSE 流式生成器
        
        逐步接收 DeepSeek API 的流式响应，
        并以 SSE 格式推送给前端。
        """
        try:
            client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL)
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=messages,
                stream=True,
                max_tokens=2000,
                temperature=0.7,
            )
            full_text = ""
            for chunk in response:
                if chunk.choices and chunk.choices[0].delta.content:
                    text = chunk.choices[0].delta.content
                    full_text += text
                    # 推送文本片段
                    yield f"data: {json.dumps({'type': 'text', 'content': text}, ensure_ascii=False)}\n\n"

            # 检查 AI 回复中是否有结构化的 plan JSON
            # 当 AI 收集到完整信息时，会在回复末尾输出 JSON 块
            if '"action": "plan"' in full_text or '"action":"plan"' in full_text:
                try:
                    # 提取 JSON 块
                    json_start = full_text.rfind('```json')
                    json_end = full_text.rfind('```')
                    if json_start != -1 and json_end > json_start:
                        json_str = full_text[json_start + 7:json_end].strip()
                        plan_data = json.loads(json_str)
                        # 推送规划参数
                        yield f"data: {json.dumps({'type': 'plan', 'data': plan_data}, ensure_ascii=False)}\n\n"
                except (json.JSONDecodeError, ValueError):
                    pass

            yield "data: [DONE]\n\n"
        except Exception as e:
            import traceback
            error_detail = traceback.format_exc()
            print("===== AI 调用异常 =====")
            print(error_detail)
            print("========================")
            yield f"data: {json.dumps({'type': 'error', 'content': f'{type(e).__name__}: {str(e)}'}, ensure_ascii=False)}\n\n"
            yield "data: [DONE]\n\n"

    # 返回 SSE 流式响应
    response = StreamingHttpResponse(stream_generator(), content_type='text/event-stream')
    response['Cache-Control'] = 'no-cache'
    response['X-Accel-Buffering'] = 'no'  # 禁用 Nginx 缓冲
    return response


# ==================== 行程管理 ====================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_saved_plans(request):
    """
    获取当前用户保存的行程列表
    
    URL: GET /api/plans/
    认证：需要 JWT Token
    """
    plans = SavedPlan.objects.filter(user=request.user)
    serializer = SavedPlanSerializer(plans, many=True)
    return Response({"status": "success", "data": serializer.data})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def save_plan(request):
    """
    保存行程规划
    
    URL: POST /api/plans/save/
    认证：需要 JWT Token
    
    请求体：{"name": "北京3天行程", "city": "北京", "days": 3, "tags": "历史,文化", "budget": "mid", "plan_data": {...}}
    """
    data = request.data.copy()
    serializer = SavedPlanSerializer(data=data)
    if serializer.is_valid():
        serializer.save(user=request.user)
        return Response({"status": "success", "data": serializer.data}, status=201)
    return Response({"status": "error", "errors": serializer.errors}, status=400)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_saved_plan(request, plan_id):
    """
    删除保存的行程（只能删除自己的行程）
    
    URL: DELETE /api/plans/<plan_id>/delete/
    认证：需要 JWT Token
    """
    try:
        plan = SavedPlan.objects.get(id=plan_id, user=request.user)
        plan.delete()
        return Response({"status": "success", "message": "已删除"})
    except SavedPlan.DoesNotExist:
        return Response({"status": "error", "message": "行程不存在或无权删除"}, status=404)
