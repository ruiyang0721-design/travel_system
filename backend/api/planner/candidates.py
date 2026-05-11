"""
候选景点召回模块
================
智能路线规划的第一步：从数据库中筛选出符合用户偏好的候选景点。

算法流程：
1. 按城市过滤所有景点
2. 硬性排除：单个景点游玩时长 > 8 小时的不合理（如迪士尼需要整天）
3. 计算每个景点的基础分 = 0.7 × 标签匹配率 + 0.3 × (评分/5.0)
4. 融合协同过滤分数（Item-based CF）：最终分 = 0.6 × 基础分 + 0.4 × CF分
5. 按最终分降序排列，基于时间预算动态截断（而非固定数量）

时间预算截断策略：
  总预算 = 游玩天数 × 8小时/天
  依次累加景点游玩时长，直到累计时长超过预算为止
  这样 1 天行程选的景点少，5 天行程选的多，自动适配
"""

from ..models import Spot
from .cf import build_item_cf_scores

# 每日有效游玩时间预算（小时），用于控制候选池总量
# 8小时约为一天合理游玩时间上限
DAILY_TIME_BUDGET = 8.0

# 融合权重常量
ALPHA = 0.6  # 原始分数（标签匹配 + 评分）的权重
BETA = 0.4   # 协同过滤分数的权重


def generate_candidates(user_tags, travel_days, target_city, user=None, must_include_ids=None):
    """
    候选景点生成主函数 —— 基于时间预算的动态召回
    
    融合标签匹配评分与协同过滤评分，按综合分数从高到低排序，
    依次累加游玩时长，直到总时长超过 用户游玩天数×每日时间预算。

    参数：
        user_tags (list): 用户选择的兴趣标签列表，如 ["历史", "文化"]
        travel_days (int): 游玩天数，如 3
        target_city (str): 目标城市名称，如 "北京"
        user (User, optional): Django User 对象，用于协同过滤。匿名用户传 None
        must_include_ids (list, optional): 用户指定必须包含的景点 ID 列表
    
    返回：
        list[Spot]: 候选景点对象列表，按融合分降序排列
    
    异常：
        ValueError: 当 must_include 景点总时长超过时间预算时
    """
    # 计算总时间预算：3天 × 8小时/天 = 24小时
    total_time_budget = travel_days * DAILY_TIME_BUDGET

    # Step 1: 从数据库查询该城市的所有景点
    all_spots = Spot.objects.filter(city=target_city)
    if not all_spots.exists():
        return []

    # --- 处理 must_include 景点（直接进候选池，跳过评分筛选） ---
    must_include_spots = []
    must_include_id_set = set()
    if must_include_ids:
        must_include_spots = list(Spot.objects.filter(id__in=must_include_ids, city=target_city))
        must_include_id_set = {s.id for s in must_include_spots}
        # 检查 must_include 景点总时长是否超过时间预算
        must_total_duration = sum(s.duration for s in must_include_spots)
        if must_total_duration > total_time_budget:
            raise ValueError(
                f"您选择的收藏景点总游玩时长（{must_total_duration}小时）已超过"
                f"{travel_days}天的时间预算（{total_time_budget}小时），"
                f"请增加游玩天数或减少收藏景点数量。"
            )

    scored_spots = []
    user_tags_set = set(user_tags) if user_tags else set()

    # Step 2: 遍历景点，计算每个景点的基础分（跳过 must_include 的景点）
    for spot in all_spots:
        # must_include 景点已在上面单独处理，跳过
        if spot.id in must_include_id_set:
            continue

        # 硬性排除：单个景点超过8小时的不合理（如主题乐园需要整天，无法搭配其他景点）
        if spot.duration > 8.0:
            continue

        # --- 标签匹配计算 ---
        spot_tags = set(spot.tags.replace('，', ',').split(','))
        match_score = len(spot_tags & user_tags_set) / len(user_tags_set) if user_tags_set else 0.5

        # --- 原始综合评分 ---
        base_score = 0.7 * match_score + 0.3 * (spot.rating / 5.0)
        scored_spots.append({'spot': spot, 'base_score': base_score})

    # --- Step 3: 协同过滤加分 ---
    candidate_ids = [item['spot'].id for item in scored_spots]
    cf_scores = build_item_cf_scores(user, target_city, candidate_ids)

    # --- Step 4: 融合分数 ---
    for item in scored_spots:
        sid = item['spot'].id
        cf = cf_scores.get(sid, 0.0)
        if cf_scores:
            item['score'] = ALPHA * item['base_score'] + BETA * cf
        else:
            item['score'] = item['base_score']

    # Step 5: 按融合分数降序排序
    scored_spots.sort(key=lambda x: x['score'], reverse=True)

    # --- Step 6: 基于时间预算的动态截断 ---
    # must_include 景点已占用的时长要从预算中扣除
    must_duration = sum(s.duration for s in must_include_spots)
    remaining_budget = total_time_budget - must_duration

    candidates = []
    accumulated_duration = 0.0

    for item in scored_spots:
        candidates.append(item['spot'])
        accumulated_duration += item['spot'].duration
        if accumulated_duration > remaining_budget:
            break

    # must_include 景点放在前面，保证优先级
    return must_include_spots + candidates
