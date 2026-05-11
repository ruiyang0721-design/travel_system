"""
基于物品的协同过滤模块 (Item-based Collaborative Filtering)
============================================================
使用收藏数据构建用户-景点交互矩阵，计算景点间余弦相似度，
为当前用户预测未访问景点的 CF 分数。

算法原理：
1. 构建用户-景点二元矩阵（行为用户，列为景点，值为1表示收藏过）
2. 对矩阵转置后计算景点间的余弦相似度（物品协同过滤）
3. 对当前用户未收藏的候选景点，计算它与已收藏景点的加权平均相似度
4. 归一化到 [0, 1] 范围

使用场景：
  被 candidates.py 调用，为候选景点提供协同过滤加分。
  当用户已登录且有收藏记录时生效；否则返回空字典，退化为基础评分方案。

前提条件（任一不满足则返回空）：
  - 用户已登录（非匿名）
  - 用户有该城市的收藏记录
  - 该城市至少有 2 个不同用户的收藏数据
"""

import numpy as np
from collections import defaultdict
from ..models import Favorite, Spot


def build_item_cf_scores(user, target_city, candidate_spot_ids):
    """
    为指定用户计算候选景点的协同过滤分数。

    参数：
        user: 当前登录用户（Django User 对象），可为 None（匿名用户）
        target_city (str): 目标城市名称
        candidate_spot_ids (list): 候选景点的 ID 列表
    
    返回：
        dict: {spot_id: cf_score}，分数范围 [0, 1]
              匿名用户或数据不足时返回空字典
    """
    # --- 前置条件检查 ---
    # 匿名用户或未登录，无法获取收藏数据，返回空
    if user is None or not user.is_authenticated:
        return {}

    # --- 1. 构建用户-景点交互矩阵 ---
    # 获取该城市所有景点的ID集合
    city_spot_ids = set(
        Spot.objects.filter(city=target_city).values_list('id', flat=True)
    )
    if not city_spot_ids:
        return {}

    # 获取所有用户的收藏记录（限定在该城市范围内）
    favorites = Favorite.objects.filter(
        spot__city=target_city,
        spot_id__in=city_spot_ids
    ).values_list('user_id', 'spot_id')

    if not favorites:
        return {}

    # 构建 user -> set(spot_id) 映射
    # 例如：{user1: {spot1, spot3}, user2: {spot2, spot3, spot5}}
    user_items = defaultdict(set)
    for user_id, spot_id in favorites:
        user_items[user_id].add(spot_id)

    # 当前用户收藏的景点（限该城市）
    current_user_favs = user_items.get(user.id, set())
    if not current_user_favs:
        return {}  # 当前用户没有收藏该城市景点，无法做 CF

    # --- 2. 计算景点间的余弦相似度 ---
    # 收集所有出现过的景点 ID，排序后建立索引映射
    all_spot_ids = city_spot_ids
    spot_list = sorted(all_spot_ids)
    spot_index = {sid: i for i, sid in enumerate(spot_list)}  # spot_id -> 矩阵列索引
    n_spots = len(spot_list)
    n_users = len(user_items)

    # 如果只有一个用户（就是当前用户），CF 没有意义（没有"其他用户"的数据）
    if n_users < 2:
        return {}

    # 构建用户-物品矩阵 (n_users × n_spots)
    # 值为 1.0 表示该用户收藏了该景点，0.0 表示未收藏
    user_list = sorted(user_items.keys())
    user_index = {uid: i for i, uid in enumerate(user_list)}

    matrix = np.zeros((n_users, n_spots), dtype=np.float32)
    for uid, spots in user_items.items():
        ui = user_index[uid]
        for sid in spots:
            if sid in spot_index:
                matrix[ui, spot_index[sid]] = 1.0

    # 计算物品共现矩阵 & 余弦相似度
    # item_matrix: 转置为 (n_spots × n_users)，每行是一个景点的用户向量
    item_matrix = matrix.T  # (n_spots, n_users)

    # 余弦相似度公式: cos(a,b) = (a·b) / (|a| × |b|)
    # 计算每个景点向量的L2范数
    norms = np.linalg.norm(item_matrix, axis=1, keepdims=True)  # (n_spots, 1)
    # 避免除零（全零向量的范数设为1）
    norms[norms == 0] = 1.0
    # L2归一化
    normalized = item_matrix / norms  # (n_spots, n_users)

    # 相似度矩阵 = 归一化矩阵 × 归一化矩阵的转置
    # 结果是 (n_spots × n_spots) 的方阵，每个元素是两个景点的余弦相似度
    sim_matrix = normalized @ normalized.T  # 余弦相似度

    # --- 3. 为当前用户预测 CF 分数 ---
    cf_scores = {}
    for cand_id in candidate_spot_ids:
        if cand_id not in spot_index:
            continue
        cand_idx = spot_index[cand_id]

        # 跳过已收藏的景点（不需要再推荐给用户）
        if cand_id in current_user_favs:
            cf_scores[cand_id] = 0.0
            continue

        # 计算该候选景点与用户已收藏景点的加权相似度之和
        # 思路：如果候选景点和用户喜欢的景点很相似，那用户可能也喜欢它
        weighted_sum = 0.0
        sim_count = 0.0
        for fav_id in current_user_favs:
            if fav_id not in spot_index:
                continue
            fav_idx = spot_index[fav_id]
            sim = sim_matrix[cand_idx, fav_idx]
            if sim > 0:
                weighted_sum += sim
                sim_count += 1.0

        # CF分数 = 与已收藏景点的平均相似度
        if sim_count > 0:
            cf_scores[cand_id] = weighted_sum / sim_count
        else:
            cf_scores[cand_id] = 0.0

    # --- 4. 归一化到 [0, 1] ---
    # 将最大CF分数映射为1.0，其余按比例缩放
    if cf_scores:
        max_score = max(cf_scores.values())
        if max_score > 0:
            cf_scores = {sid: s / max_score for sid, s in cf_scores.items()}

    return cf_scores
