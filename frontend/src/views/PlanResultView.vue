<!--
  PlanResultView.vue - 行程结果展示页面
  =========================================
  功能概述：
    展示由后端智能规划生成的旅行行程，支持以下交互：
    - 按天查看景点列表，支持拖拽排序
    - 查看每日预算、时长、景点数量等统计信息
    - 移除不需要的景点
    - 保存行程到个人账号 / 导出为文本文件
    - 路线地图可视化（调用 MapContainer 组件）

  页面结构：
    1. 页面头部（返回按钮 + 标题）
    2. 统计信息栏（预算 / 时长 / 景点数 三张卡片）
    3. 加载状态提示
    4. 行程明细面板（按天 Tab 切换 + 时间线 + 拖拽排序）
    5. 路线地图（MapContainer 组件）
-->
<template>
  <div class="result-page">
    <!-- ================= 页面头部 ================= -->
    <!-- 返回规划页按钮 + 页面标题 -->
    <el-page-header @back="$router.push('/plan')" title="返回规划" style="margin-bottom: 20px;">
      <template #content>
        <span class="text-large font-600 mr-3">您的专属定制行程</span>
      </template>
    </el-page-header>

    <!-- ================= 预算和景点信息栏 ================= -->
    <!-- 三张统计卡片：行程预算、游玩时长、总共景点 -->
    <el-row :gutter="20" style="margin-bottom: 20px;" v-if="!loading && itinerary">
      <el-col :span="8">
        <StatsCard title="行程预算" :value="'¥ ' + budgetInfo.total_cost" :subtitle="'门票总计 · ' + budgetInfo.days + '天行程'" color="red" />
      </el-col>
      <el-col :span="8">
        <StatsCard title="游玩时长" :value="budgetInfo.total_duration + ' 小时'" :subtitle="'建议分 ' + budgetInfo.days + ' 天完成'" color="blue" />
      </el-col>
      <el-col :span="8">
        <StatsCard title="总共景点" :value="totalSpots + ' 个'" :subtitle="route.query.city + ' · ' + budgetInfo.days + '天行程'" color="green" />
      </el-col>
    </el-row>

    <!-- ================= 推荐总结与解释 ================= -->
    <!-- 展示后端基于算法输入和规划结果生成的解释，提升推荐可信度 -->
    <el-card v-if="!loading && itinerary && explanation" class="explanation-card" shadow="never">
      <template #header>
        <div class="card-header">
          <h3>为什么这样推荐</h3>
          <span class="sub-text">基于兴趣偏好、评分、空间聚类和路线优化生成</span>
        </div>
      </template>

      <div class="explanation-summary">
        {{ explanation.summary }}
      </div>

      <div class="explanation-grid">
        <div class="explanation-block">
          <h4>推荐依据</h4>
          <ul class="reason-list">
            <li v-for="(reason, index) in explanation.reasons" :key="index">
              {{ reason }}
            </li>
          </ul>
        </div>

        <div class="explanation-block">
          <h4>每日安排说明</h4>
          <div class="daily-explanation" v-for="item in explanation.daily" :key="item.day">
            <div class="daily-title">
              <strong>{{ item.day }}</strong>
              <span>{{ item.spot_count }}个景点 · {{ item.duration }}小时 · ¥{{ item.cost }}</span>
            </div>
            <p>{{ item.text }}</p>
          </div>
        </div>
      </div>
    </el-card>

    <!-- ================= 加载状态 ================= -->
    <!-- 规划中时显示 loading 动画和提示文字 -->
    <div v-if="loading" v-loading="true" style="height: 400px; display: flex; justify-content: center; align-items: center;">
      <h3 style="color: #909399;">正在为您智能规划路线，请稍候...</h3>
    </div>

    <div v-else-if="itinerary">
       
      <!-- ================= 行程明细面板 ================= -->
      <!-- 按天展示景点列表，支持拖拽排序和景点移除 -->
      <el-card class="itinerary-card" shadow="never">
        <template #header>
          <!-- 卡片头部：标题 + 拖拽提示 + 保存/导出按钮 -->
          <div class="card-header">
            <h3>行程明细</h3>
            <span class="sub-text">({{ route.query.city }} · {{ route.query.days }}天)</span>
            <el-tag type="info" style="margin-left: 15px;" effect="plain">按住卡片左侧图标可拖拽排序</el-tag>
            <div style="flex-grow: 1;"></div>
            <!-- 保存行程按钮：将行程数据提交到后端 -->
            <el-button type="primary" size="small" @click="savePlan" :loading="saving">
              保存行程
            </el-button>
            <!-- 导出行程按钮：生成文本文件供下载 -->
            <el-button type="success" size="small" @click="exportPlan" style="margin-left: 10px;">
              导出行程
            </el-button>
          </div>
        </template>
        
        <!-- 按天 Tab 切换：每天一个标签页 -->
        <el-tabs v-model="activeDay" class="day-tabs">
          <el-tab-pane v-for="(spots, dayName) in itinerary" :key="dayName" :label="dayName" :name="dayName">
            
            <!-- 当日小结标签：显示景点数、当日预算、当日时长 -->
            <div class="day-summary">
              <el-tag type="info" effect="plain">{{ spots.filter(s => !s.is_hotel).length }} 个景点</el-tag>
              <el-tag type="warning" effect="plain" style="margin-left: 10px;">¥{{ getDayCost(spots) }}</el-tag>
              <el-tag type="success" effect="plain" style="margin-left: 10px;">{{ getDayDuration(spots) }}h</el-tag>
            </div>

            <!-- 景点时间线列表（支持拖拽排序） -->
            <el-timeline style="margin-top: 20px;">
              <draggable
                v-model="itinerary[dayName]"
                item-key="id"
                handle=".drag-handle"
                animation="300"
                @end="onDragEnd"
              >
                <template #item="{ element, index }">
                  <el-timeline-item :timestamp="element.is_hotel ? '住宿点' : `第 ${index} 站`" 
                                      placement="top" 
                                      :color="element.is_hotel ? '#f56c6c' : '#409eff'">
                    <!-- 景点详情卡片（酒店用虚线红色边框区分） -->
                    <el-card shadow="hover" class="spot-detail-card" :style="element.is_hotel ? 'border: 2px dashed #f56c6c;' : ''">
                    <div class="spot-info">
                      <div class="spot-title-group">
                        <!-- 拖拽手柄图标（酒店不显示） -->
                        <div class="drag-handle" title="按住拖拽排序" v-if="!element.is_hotel">
                          <span>✋</span>
                        </div>
                        
                        <!-- 景点名称 + 详情链接 -->
                        <h4 class="spot-name" :style="element.is_hotel ? 'color: #f56c6c;' : ''">
                          {{ element.name }}
                        </h4>
                        <el-button v-if="!element.is_hotel" type="primary" link size="small" @click="$router.push(`/spot/${element.name}`)" style="margin-left: 10px;">
                          详情 →
                        </el-button>
                      </div>
                      
                      <!-- 操作区域：评分标签 + 移除按钮（酒店不显示） -->
                      <div class="spot-actions">
                        <template v-if="!element.is_hotel">
                          <el-tag size="small" type="warning" class="rating-tag">⭐ {{ element.rating }} 分</el-tag>
                          <el-button type="danger" size="small" plain @click="removeSpot(dayName, index)" style="margin-left: 15px;">
                            移除
                          </el-button>
                        </template>
                      </div>
                    </div>
                    
                    <!-- 景点元信息：游玩时长、门票价格、标签（酒店不显示） -->
                    <div class="spot-meta" v-if="!element.is_hotel">
                      <span>建议游玩: <strong>{{ element.duration }}</strong> 小时</span>
                      <el-divider direction="vertical" />
                      <span>门票: <strong>{{ element.price }}</strong> 元</span>
                      <el-divider direction="vertical" />
                      <span class="tags-text">特色: {{ element.tags }}</span>
                    </div>
                  </el-card>
                </el-timeline-item>
                </template>
              </draggable>
            </el-timeline>

          </el-tab-pane>
        </el-tabs>
      </el-card>

      <!-- ================= 路线地图 ================= -->
      <!-- 使用 MapContainer 组件展示景点连线地图 -->
      <el-card class="map-card" shadow="never" style="margin-top: 20px;">
        <template #header>
          <div class="card-header">
            <h3>路线轨迹图</h3>
          </div>
        </template>
        <!-- key 变化时强制重新渲染地图（用于拖拽/移除后刷新） -->
        <MapContainer :key="mapKey" :itinerary="itinerary" />
      </el-card>

    </div>
  </div>
</template>

<script setup>
/**
 * PlanResultView.vue - 行程结果页逻辑
 * 
 * 主要功能：
 * - 从路由参数获取规划请求，调用后端 API 生成行程
 * - 展示行程统计信息（预算、时长、景点数）
 * - 支持拖拽排序、移除景点
 * - 保存行程到账号 / 导出为文本文件
 */
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'
import MapContainer from '../components/MapContainer.vue'
import StatsCard from '../components/StatsCard.vue'
import draggable from 'vuedraggable'

/** 路由对象，用于获取 URL 查询参数 */
const route = useRoute()
const router = useRouter()

/** 从 localStorage 获取 JWT token（用于身份认证） */
const token = localStorage.getItem('access_token')

/**
 * 行程数据（后端返回的按天分组字典）
 * 结构示例：{ "第1天": [景点A, 景点B], "第2天": [景点C] }
 */
const itinerary = ref(null)

/** 页面加载状态 */
const loading = ref(true)

/** 当前选中的天数 Tab（如 "第1天"） */
const activeDay = ref('')

/** 地图组件的 key，变化时强制重新渲染 */
const mapKey = ref(0)

/**
 * 预算统计信息
 * @property {number} total_cost - 总费用
 * @property {number} total_duration - 总时长（小时）
 * @property {number} days - 总天数
 */
const budgetInfo = ref({ total_cost: 0, total_duration: 0, days: 1 })

/**
 * 推荐解释信息
 * 后端根据用户输入、推荐算法和最终行程生成，用于说明推荐依据
 */
const explanation = ref(null)

/**
 * 计算属性：排除酒店后的景点总数
 */
const totalSpots = computed(() => {
  if (!itinerary.value) return 0
  return Object.values(itinerary.value).flat().filter(s => !s.is_hotel).length
})

/**
 * 计算某天的门票总费用
 * @param {Array} spots - 当天的景点数组
 * @returns {string} 格式化后的费用（整数）
 */
const getDayCost = (spots) => {
  return spots.reduce((sum, s) => sum + (s.is_hotel ? 0 : parseFloat(s.price || 0)), 0).toFixed(0)
}

/**
 * 计算某天的总游玩时长
 * @param {Array} spots - 当天的景点数组
 * @returns {string} 格式化后的时长（保留一位小数）
 */
const getDayDuration = (spots) => {
  return spots.reduce((sum, s) => sum + (s.is_hotel ? 0 : parseFloat(s.duration || 0)), 0).toFixed(1)
}

/**
 * 从后端获取规划结果
 * 将路由参数组装为请求体，POST 到推荐 API
 */
const fetchPlan = async () => {
  const { city, days, tags, hotelName, hotelLat, hotelLng } = route.query 
  try {
    const payload = {
      city,
      days: parseInt(days),
      tags: tags ? tags.split(',') : []
    }

    // 如果用户指定了酒店位置，添加到请求体
    if (hotelLat && hotelLng) {
      payload.hotel = {
        name: hotelName,
        lat: parseFloat(hotelLat),
        lng: parseFloat(hotelLng)
      }
    }

    // 如果有 must_include 参数（从收藏中选择的景点），添加到请求体
    const { must_include } = route.query
    if (must_include) {
      payload.must_include = must_include.split(',').map(Number)
    }

    const res = await axios.post(
      'http://127.0.0.1:8000/api/recommend/',
      payload,
      token ? { headers: { Authorization: `Bearer ${token}` } } : {}
    )
    
    // 存储行程数据和预算信息
    itinerary.value = res.data.data
    budgetInfo.value = res.data.budget || { total_cost: 0, total_duration: 0, days: parseInt(days) }
    explanation.value = res.data.explanation || null
    
    // 默认选中第一天的 Tab
    if (itinerary.value && Object.keys(itinerary.value).length > 0) {
      activeDay.value = Object.keys(itinerary.value)[0]
    }
  } catch (err) {
    console.error(err)
    ElMessage.error("规划失败，请检查后端服务")
  } finally {
    loading.value = false
  }
}

/**
 * 拖拽排序完成回调
 * 提示用户并刷新地图（地图会根据新顺序重新连线）
 */
const onDragEnd = () => {
  ElMessage.success('路线顺序已更新，地图正在重新规划连线！')
  mapKey.value += 1 // 触发地图组件重新渲染
}

/**
 * 从当天行程中移除指定景点
 * @param {string} dayName - 天数名称（如 "第1天"）
 * @param {number} index - 景点在数组中的索引
 */
const removeSpot = (dayName, index) => {
  itinerary.value[dayName].splice(index, 1)
  ElMessage.warning('已将该景点移出今日行程！')
  mapKey.value += 1 // 触发地图刷新
}

/** 保存按钮的加载状态 */
const saving = ref(false)

/**
 * 保存行程到后端
 * 将当前行程数据 POST 到保存接口，需要用户已登录
 */
const savePlan = async () => {
  if (!itinerary.value) return
  // 检查是否已登录
  if (!token) {
    ElMessageBox.confirm(
      '请先登录后再保存行程',
      '提示',
      { confirmButtonText: '去登录', cancelButtonText: '取消', type: 'warning' }
    ).then(() => { router.push('/login') }).catch(() => {})
    return
  }
  saving.value = true
  try {
    await axios.post('http://127.0.0.1:8000/api/plans/save/', {
      name: `${route.query.city}${route.query.days}天行程`,
      city: route.query.city,
      days: parseInt(route.query.days),
      tags: route.query.tags || '',
      budget: route.query.budget || 'mid',
      plan_data: itinerary.value
    }, { headers: { Authorization: `Bearer ${token}` } })
    ElMessage.success('行程已保存')
  } catch (err) {
    ElMessage.error(err.response?.data?.errors ? JSON.stringify(err.response.data.errors) : (err.response?.data?.message || '保存失败'))
  } finally {
    saving.value = false
  }
}

/**
 * 导出行程为文本文件
 * 生成格式化的行程文本，通过 Blob 创建下载链接
 */
const exportPlan = () => {
  if (!itinerary.value) return
  
  // 拼接行程文本内容
  let text = `🧳 我的旅行计划 - ${route.query.city} (${route.query.days}天)\n`
  text += `${'='.repeat(50)}\n\n`
  
  for (const [day, spots] of Object.entries(itinerary.value)) {
    text += `📅 ${day}\n`
    text += `${'-'.repeat(30)}\n`
    spots.forEach((spot, i) => {
      if (spot.is_hotel) {
        text += `  🏠 ${spot.name}\n`
      } else {
        text += `  ${i}. ${spot.name} (⭐${spot.rating} · ¥${spot.price} · ${spot.duration}h)\n`
      }
    })
    text += '\n'
  }
  
  text += `\n💰 总预算: ¥${budgetInfo.value.total_cost}\n`
  text += `⏱️ 总时长: ${budgetInfo.value.total_duration} 小时\n`
  
  // 创建 Blob 并触发浏览器下载
  const blob = new Blob([text], { type: 'text/plain;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `旅行计划_${route.query.city}_${route.query.days}天.txt`
  a.click()
  URL.revokeObjectURL(url) // 释放内存
  
  ElMessage.success('行程已导出！')
}

// 组件挂载时自动获取行程数据
onMounted(fetchPlan)
</script>

<style scoped>
/* 页面整体布局：左右留白居中 */
.result-page { padding: 30px 8%; max-width: 1400px; margin: 0 auto; }

/* 卡片头部 flex 布局 */
.card-header { display: flex; align-items: center; }
.card-header h3 { margin: 0; color: #303133; }
.sub-text { margin-left: 10px; color: #909399; font-size: 14px; }

/* 统计信息卡片通用样式（已提取为 StatsCard 组件） */

/* 推荐解释卡片 */
.explanation-card {
  border-radius: 8px;
  margin-bottom: 20px;
  border: 1px solid #ebeef5;
}

.explanation-summary {
  background: #f5f7fa;
  border-left: 4px solid #409eff;
  color: #303133;
  line-height: 1.8;
  padding: 14px 16px;
  border-radius: 6px;
  margin-bottom: 18px;
  font-size: 14px;
}

.explanation-grid {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(0, 1.2fr);
  gap: 20px;
}

.explanation-block {
  min-width: 0;
}

.explanation-block h4 {
  margin: 0 0 12px;
  color: #303133;
  font-size: 15px;
  font-weight: 600;
}

.reason-list {
  margin: 0;
  padding-left: 18px;
  color: #606266;
  font-size: 13px;
  line-height: 1.8;
}

.reason-list li {
  margin-bottom: 6px;
}

.daily-explanation {
  padding: 12px 0;
  border-bottom: 1px solid #f0f2f5;
}

.daily-explanation:first-of-type {
  padding-top: 0;
}

.daily-explanation:last-child {
  border-bottom: none;
  padding-bottom: 0;
}

.daily-title {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 6px;
  color: #303133;
  font-size: 13px;
}

.daily-title span {
  color: #909399;
  flex-shrink: 0;
}

.daily-explanation p {
  margin: 0;
  color: #606266;
  font-size: 13px;
  line-height: 1.7;
}

/* 当日小结标签行 */
.day-summary {
  display: flex;
  align-items: center;
  padding: 10px 0;
}

/* 景点详情卡片 */
.spot-detail-card { border-radius: 8px; }
/* 景点信息行：名称和操作按钮左右分布 */
.spot-info { display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px; }
.spot-title-group { display: flex; align-items: center; flex: 1; }
.spot-name { margin: 0; font-size: 16px; color: #303133; }
.spot-actions { display: flex; align-items: center; }
/* 景点元信息行（时长、价格、标签） */
.spot-meta { font-size: 13px; color: #606266; display: flex; align-items: center; }
.tags-text { color: #909399; }

/* 拖拽手柄样式：鼠标悬停时显示抓取手势 */
.drag-handle {
  cursor: grab;
  margin-right: 12px;
  font-size: 20px;
  color: #909399;
  padding: 5px;
  border-radius: 4px;
  background-color: #f4f4f5;
  transition: all 0.3s;
}
.drag-handle:active {
  cursor: grabbing;
  background-color: #e9e9eb;
}
</style>
