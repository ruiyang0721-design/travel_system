"""
空间聚类 + 时间容量均衡模块
============================
智能路线规划的第二步：将候选景点按天分组。

分两个阶段：
阶段一：K-means 空间聚类
  - 输入：候选景点的经纬度坐标矩阵
  - 聚类数 K = 游玩天数（3天就分3组）
  - 效果：地理位置靠近的景点被分到同一天，减少当天来回跑

阶段二：时间容量均衡
  - K-means 只考虑空间不管时间，可能出现某天塞了5个大景点(超8小时)
  - 解决方案：迭代检查每组总时长，超载的景点转移到最近的空闲天
  - 转移策略：优先踢出离质心最远的景点（对当天路线紧凑性影响最小）
"""

import numpy as np
import math
from sklearn.cluster import KMeans

# 每日有效游玩时间上限（小时），与 candidates.py 保持一致
DAILY_TIME_BUDGET = 8.0


def _calc_distance(spot1_lat, spot1_lng, spot2_lat, spot2_lng):
    """
    计算两个经纬度点之间的欧氏距离
    
    注意：这里用的是简化的欧氏距离，不是精确的地理距离(Haversine)。
    对于同一城市内的景点比较，误差可忽略不计。
    """
    return math.sqrt((spot1_lng - spot2_lng) ** 2 + (spot1_lat - spot2_lat) ** 2)


def _get_cluster_centroid(spots):
    """
    计算一组景点的质心（中心点经纬度）
    
    质心 = 所有景点经纬度的算术平均值
    用途：判断哪些景点离该组中心最远（优先转出）
    """
    if not spots:
        return 0, 0
    avg_lat = sum(s.latitude for s in spots) / len(spots)
    avg_lng = sum(s.longitude for s in spots) / len(spots)
    return avg_lat, avg_lng


def _get_cluster_duration(spots):
    """
    计算一组景点的总游玩时长
    用途：判断该天是否超载（总时长 > 8小时）
    """
    return sum(s.duration for s in spots)


def cluster_spots(candidates, travel_days):
    """
    空间聚类 + 时间容量均衡主函数

    参数：
        candidates (list): 第一步选出的候选 Spot 对象列表
        travel_days (int): 旅游天数（即聚类数量 K）
    
    返回：
        dict: 按天分组的景点字典，如 {"第1天": [spotA, spotB], "第2天": [spotC, spotD]}
    """
    # 边界条件保护：如果候选景点比天数还少，那有几天只能排1个景点
    
    k_clusters = min(len(candidates), travel_days)
    # ========== 阶段一：K-means 空间聚类 ==========
    coords = np.array([[spot.longitude, spot.latitude] for spot in candidates])
    
    # K-means 参数说明：
    # - n_clusters: 聚类数 = 游玩天数
    # - n_init=10: 运行10次取最优，避免陷入局部最优解
    # - random_state=42: 固定随机种子，保证结果可复现
    kmeans = KMeans(n_clusters=k_clusters, n_init=10, random_state=42)
    labels = kmeans.fit_predict(coords)

    # 按簇分组：labels[i] 表示第 i 个景点被分到了哪个簇
    clusters = {i: [] for i in range(k_clusters)}
    for i, spot in enumerate(candidates):
        clusters[labels[i]].append(spot)

    # ========== 阶段二：时间容量均衡 ==========
    # 最多迭代10轮，每轮处理所有超载簇
    for _ in range(10):
        # 计算每个簇的质心和总时长
        centroids = {}
        durations = {}
        for idx, spots in clusters.items():
            centroids[idx] = _get_cluster_centroid(spots)
            durations[idx] = _get_cluster_duration(spots)

        # 找出超载的簇（总时长超过每日预算8小时）
        overloaded = [idx for idx in clusters if durations[idx] > DAILY_TIME_BUDGET]
        if not overloaded:
            break  # 所有簇都在预算内，均衡完成

        for src_idx in overloaded:
            src_spots = clusters[src_idx]
            src_centroid = centroids[src_idx]

            # 按距离质心从远到近排序，优先转移最远的景点
            # 原因：离质心最远的景点本来就是"硬塞进来"的，转走它对当天路线紧凑性影响最小
            src_spots.sort(
                key=lambda s: _calc_distance(s.latitude, s.longitude, src_centroid[0], src_centroid[1]),
                reverse=True
            )

            # 逐个转移，直到该簇总时长回到预算内
            while _get_cluster_duration(src_spots) > DAILY_TIME_BUDGET and len(src_spots) > 1:
                # 取出离质心最远的景点
                overflow_spot = src_spots.pop(0)

                # 找最近的、还有空余的簇
                best_target = None
                best_distance = float('inf')
                for tgt_idx, tgt_spots in clusters.items():
                    if tgt_idx == src_idx:
                        continue  # 跳过自己
                    tgt_duration = _get_cluster_duration(tgt_spots)
                    # 只考虑还没超载的簇（留一点余量，允许轻微超出）
                    if tgt_duration < DAILY_TIME_BUDGET:
                        dist = _calc_distance(
                            overflow_spot.latitude, overflow_spot.longitude,
                            centroids[tgt_idx][0], centroids[tgt_idx][1]
                        )
                        if dist < best_distance:
                            best_distance = dist
                            best_target = tgt_idx

                if best_target is not None:
                    # 找到了合适的接收簇，转移景点
                    clusters[best_target].append(overflow_spot)
                    # 更新目标簇的质心（近似更新）
                    tgt_spots = clusters[best_target]
                    centroids[best_target] = _get_cluster_centroid(tgt_spots)
                else:
                    # 所有簇都满了，放回原簇（避免景点丢失）
                    src_spots.append(overflow_spot)
                    break

    # 打包成前端需要的格式
    daily_itinerary = {}
    for idx in sorted(clusters.keys()):
        spots = clusters[idx]
        if spots:  # 跳过空天
            daily_itinerary[f"第{idx+1}天"] = spots

    return daily_itinerary
