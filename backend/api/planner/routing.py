"""
暴力穷举路径优化模块
====================
智能路线规划的第三步：为每天的景点组找到最短游览路线。

算法选择理由：
  每天的景点数不超过 5 个（受 8 小时时间预算约束），
  5! = 120 种全排列，暴力穷举可在毫秒级内求出精确最优解，
  比遗传算法更快、更准、代码更简洁。

算法流程：
  1. 枚举所有景点排列（itertools.permutations）
  2. 对每种排列计算总距离（含酒店锚点闭环）
  3. 取总距离最短的排列作为最优路线

酒店锚点约束：
  - 有酒店时：路线为 [酒店 → 景点排列 → 酒店] 闭环
  - 无酒店时：直接优化景点排列顺序
"""

import itertools
import math


def calc_distance(spot1, spot2):
    """
    计算两个景点之间的欧氏距离

    兼容处理：
    - Spot 模型对象：通过 .latitude/.longitude 属性取值
    - 字典对象（酒店节点）：通过 ['latitude']/['longitude'] 键取值
    """
    lat1 = spot1['latitude'] if isinstance(spot1, dict) else spot1.latitude
    lng1 = spot1['longitude'] if isinstance(spot1, dict) else spot1.longitude
    lat2 = spot2['latitude'] if isinstance(spot2, dict) else spot2.latitude
    lng2 = spot2['longitude'] if isinstance(spot2, dict) else spot2.longitude

    return math.sqrt((lng1 - lng2)**2 + (lat1 - lat2)**2)


def _total_distance(route):
    """计算一条路线的总距离"""
    return sum(calc_distance(route[i], route[i+1]) for i in range(len(route) - 1))


def optimize_daily_route(day_spots, hotel_node=None):
    """
    使用暴力穷举优化一天的景点游览顺序（支持酒店锚点闭环）

    参数：
        day_spots (list): 当天的景点列表（Spot对象）
        hotel_node (dict, optional): 酒店节点，包含 name/latitude/longitude/is_hotel 等字段

    返回：
        list: 优化后的路线节点列表
              有酒店时：[酒店, 景点A, 景点B, ..., 酒店]
              无酒店时：[景点A, 景点B, ...]
    """
    n_spots = len(day_spots)
    if n_spots == 0:
        return []

    # 单个或两个景点，直接返回，无需穷举
    if n_spots <= 2:
        if hotel_node:
            return [hotel_node] + day_spots + [hotel_node]
        else:
            return day_spots

    # --- 暴力穷举所有排列，找最短路线 ---
    best_route = None
    best_dist = float('inf')

    for perm in itertools.permutations(day_spots):
        if hotel_node:
            # 闭环路线：酒店 → 景点排列 → 酒店
            full_route = [hotel_node] + list(perm) + [hotel_node]
        else:
            full_route = list(perm)

        dist = _total_distance(full_route)
        if dist < best_dist:
            best_dist = dist
            best_route = full_route

    return best_route
