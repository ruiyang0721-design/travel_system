"""
智能路径规划总控引擎
====================
调度三个子模块完成完整的路线规划流程：
1. candidates.py → 候选景点召回（标签匹配 + 协同过滤 + 时间预算截断）
2. clustering.py → 空间聚类 + 时间容量均衡（K-means + 超载转移）
3. routing.py → 遗传算法路径优化（每天的最短路线）

还包含酒店锚点的智能处理：
  - 用户指定酒店 → 使用高德地图获取的经纬度
  - 未指定酒店 → 计算所有候选景点的质心作为推荐住宿区域
"""

from .candidates import generate_candidates
from .clustering import cluster_spots
from .routing import optimize_daily_route


def generate_itinerary_with_hotel(user_data, hotel_location=None, user=None, must_include_ids=None):
    """
    智能路径规划总控函数

    参数：
        user_data (dict): 用户输入数据，包含 city/days/tags 等字段
        hotel_location (dict, optional): 用户指定的酒店信息 {name, lat, lng}
        user (User, optional): Django User 对象，用于协同过滤
    
    返回：
        dict: 按天分组的路线字典
              格式如 {"第1天": [酒店, 景点A, 景点B, 酒店], "第2天": [...]}
              每个景点是 Spot 对象，酒店是 dict 节点
    """
    target_city = user_data.get('city', '北京')
    travel_days = int(user_data.get('days', 3))
    user_tags = user_data.get('tags', [])

    # ========== Step 1: 召回景点 ==========
    # 从数据库中筛选符合用户偏好的候选景点
    # 融合标签匹配 + 协同过滤，按时间预算动态截断
    candidates = generate_candidates(user_tags, travel_days, target_city, user=user, must_include_ids=must_include_ids)
    if not candidates:
        return {}

    # ========== Step 2: 空间聚类 ==========
    # K-means 按地理位置分组 + 时间容量均衡
    daily_clusters = cluster_spots(candidates, travel_days)

    # ========== Step 3: 酒店锚点智能处理 ==========
    hotel_node = None
    if hotel_location:
        # 分支 A：用户指定了具体酒店 → 使用高德地图获取的经纬度
        hotel_node = {
            'id': f"hotel_custom",
            'name': hotel_location.get('name', '🏨 您的住宿酒店'),
            'latitude': float(hotel_location['lat']),
            'longitude': float(hotel_location['lng']),
            'is_hotel': True,  # 标记为酒店节点，前端据此渲染不同样式
            'rating': '-', 'duration': 0, 'price': 0, 'tags': '出发地/休息区'
        }
    else:
        # 分支 B：用户没指定酒店 → 计算所有候选景点的质心作为推荐住宿区域
        # 质心 = 所有景点经纬度的平均值，即地理中心点
        avg_lat = sum(spot.latitude for spot in candidates) / len(candidates)
        avg_lng = sum(spot.longitude for spot in candidates) / len(candidates)
        
        hotel_node = {
            'id': f"hotel_ai_rec",
            'name': '推荐住宿区域',
            'latitude': avg_lat,
            'longitude': avg_lng,
            'is_hotel': True,
            'rating': '5.0', 'duration': 0, 'price': 0, 'tags': 'AI智能分析建议'
        }

    # ========== Step 4: 路径优化 ==========
    # 对每天的景点组使用遗传算法优化游览顺序
    # 带入酒店锚点约束，生成闭环路线：酒店 → 景点 → 酒店
    formatted_plan = {}
    for day_name, spots_in_cluster in daily_clusters.items():
        sorted_daily_route = optimize_daily_route(spots_in_cluster, hotel_node)
        formatted_plan[day_name] = sorted_daily_route

    return formatted_plan
