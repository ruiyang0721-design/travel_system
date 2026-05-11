<!--
  SpotsView.vue - 景点大厅页面
  ================================
  功能概述：
    展示所有景点的列表页面，提供多维度筛选和搜索功能。
    用户可以按关键词搜索、按城市筛选、按标签分类浏览景点。
    点击景点卡片可弹窗预览详情，或跳转到详情页。

  页面结构：
    1. 页面标题（景点大厅）
    2. 筛选区域（搜索框 + 城市选择 + 标签单选）
    3. 结果数量统计
    4. 景点卡片网格（4列布局，含图片、评分、标签、价格）
    5. 空状态提示
    6. 景点快速预览弹窗
-->
<template>
  <div class="spots-container">
    <!-- 页面标题 -->
    <h1 class="page-title">🏛️ 景点大厅</h1>

    <!-- ===== 筛选区域 ===== -->
    <div class="filter-section">
      <!-- 关键词搜索框（支持回车触发搜索） -->
      <el-input
        v-model="searchKeyword"
        placeholder="输入景点名称搜索 (例如：故宫)"
        clearable
        @keyup.enter="fetchSpots"
        style="width: 250px; margin-right: 15px;"
      >
        <template #append>
          <el-button @click="fetchSpots">搜索</el-button>
        </template>
      </el-input>

      <!-- 城市下拉选择（变更时自动触发搜索） -->
      <el-select v-model="selectedCity" placeholder="选择城市" clearable @change="fetchSpots" style="width: 130px; margin-right: 15px;">
        <el-option label="全部城市" value="" />
        <el-option label="北京" value="北京" />
        <el-option label="上海" value="上海" />
        <el-option label="成都" value="成都" />
        <el-option label="西安" value="西安" />
        <el-option label="杭州" value="杭州" />
        <el-option label="重庆" value="重庆" />
        <el-option label="广州" value="广州" />
      </el-select>

      <!-- 标签分类单选按钮组 -->
      <el-radio-group v-model="selectedTag" @change="fetchSpots">
        <el-radio-button label="">全部</el-radio-button>
        <el-radio-button label="历史">历史</el-radio-button>
        <el-radio-button label="园林">园林</el-radio-button>
        <el-radio-button label="亲子">亲子</el-radio-button>
        <el-radio-button label="文化">文化</el-radio-button>
        <el-radio-button label="自然">自然</el-radio-button>
        <el-radio-button label="美食">美食</el-radio-button>
        <el-radio-button label="夜景">夜景</el-radio-button>
      </el-radio-group>
    </div>

    <!-- 搜索结果数量统计 -->
    <div class="result-count" v-if="spotsList.length > 0">
      共找到 <strong>{{ spotsList.length }}</strong> 个景点
    </div>

    <!-- ===== 景点卡片网格 ===== -->
    <!-- 每行4列，每个景点一张卡片，点击打开详情弹窗 -->
    <el-row :gutter="20">
      <el-col :span="6" v-for="spot in spotsList" :key="spot.id" style="margin-bottom: 20px;">
        <el-card shadow="hover" class="spot-card" style="cursor: pointer;" @click="openSpotDetail(spot)">
          <!-- 景点图片区域（带价格角标） -->
          <div class="img-wrapper">
            <el-image 
              :src="`https://picsum.photos/seed/${spot.id}/300/200`" 
              class="spot-image" 
              fit="cover"
            />
            <!-- 价格角标：收费显示金额，免费显示绿色标签 -->
            <div class="price-badge" v-if="spot.price > 0">¥{{ spot.price }}</div>
            <div class="price-badge free" v-else>免费</div>
          </div>
          <!-- 卡片内容区域 -->
          <div class="card-content">
            <!-- 景点名称和城市标签 -->
            <div class="card-top">
              <h3 class="spot-name">{{ spot.name }}</h3>
              <span class="spot-city">{{ spot.city }}</span>
            </div>
            <!-- 评分星级（只读） -->
            <el-rate v-model="spot.rating" disabled show-score text-color="#ff9900" />
            <!-- 标签列表（最多显示3个） -->
            <p class="spot-tags">
              <el-tag v-for="tag in (spot.tags || '').split(',').slice(0, 3)" :key="tag" size="small" type="info" style="margin-right: 4px; margin-bottom: 4px;">{{ tag }}</el-tag>
            </p>
            <!-- 建议游玩时长 -->
            <p class="spot-time">建议游玩：{{ spot.duration }} 小时</p>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 空状态：无搜索结果时显示 -->
    <el-empty v-if="spotsList.length === 0 && !loading" description="没有找到符合条件的景点~" />
    
    <!-- ===== 景点快速预览弹窗 ===== -->
    <!-- 点击卡片后弹出，展示景点的详细信息 -->
    <SpotPreviewDialog v-model:visible="dialogVisible" :spot="currentSpot" />
  </div>
</template>

<script setup>
/**
 * SpotsView.vue - 景点大厅页面逻辑
 * 
 * 主要功能：
 * - 获取并展示景点列表
 * - 支持按关键词、城市、标签多维度筛选
 * - 支持从首页城市快捷入口跳转后自动筛选
 * - 景点快速预览弹窗
 */
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'
import SpotPreviewDialog from '../components/SpotPreviewDialog.vue'

/** 路由对象（用于读取 URL 查询参数） */
const route = useRoute()

/** 景点列表数据 */
const spotsList = ref([])

/** 搜索关键词 */
const searchKeyword = ref('')

/** 当前选中的标签筛选 */
const selectedTag = ref('')

/** 当前选中的城市筛选 */
const selectedCity = ref('')

/** 数据加载状态 */
const loading = ref(false)

/** 预览弹窗是否可见 */
const dialogVisible = ref(false)

/** 当前预览的景点对象 */
const currentSpot = ref({})

/**
 * 打开景点快速预览弹窗
 * @param {Object} spot - 景点数据对象
 */
const openSpotDetail = (spot) => {
  currentSpot.value = spot
  dialogVisible.value = true
}

/**
 * 从后端获取景点列表
 * 将搜索关键词、标签、城市作为查询参数发送
 */
const fetchSpots = async () => {
  loading.value = true
  try {
    const response = await axios.get('http://127.0.0.1:8000/api/spots/', {
      params: {
        search: searchKeyword.value,
        tag: selectedTag.value,
        city: selectedCity.value
      }
    })
    spotsList.value = response.data.data
  } catch (error) {
    console.error('获取景点失败:', error)
  } finally {
    loading.value = false
  }
}

/**
 * 组件挂载时初始化：
 * 1. 检查 URL 中是否有 city 参数（从首页快捷入口跳转时携带）
 * 2. 自动设置城市筛选并请求数据
 */
onMounted(() => {
  // 支持从首页城市快捷入口跳转过来时自动筛选
  const cityParam = route.query.city
  if (cityParam) {
    selectedCity.value = cityParam
  }
  fetchSpots()
})
</script>

<style scoped>
/* 页面容器内边距 */
.spots-container {
  padding: 20px 40px;
}
/* 页面标题样式 */
.page-title {
  color: #303133;
  margin-bottom: 30px;
}
/* 筛选区域布局 */
.filter-section {
  display: flex;
  align-items: center;
  margin-bottom: 15px;
  flex-wrap: wrap;
  gap: 0;
}
/* 结果统计文字 */
.result-count {
  font-size: 13px;
  color: #909399;
  margin-bottom: 20px;
}

/* 景点图片容器（用于定位价格角标） */
.img-wrapper {
  position: relative;
  overflow: hidden;
}
/* 景点卡片图片 */
.spot-image {
  width: 100%;
  height: 180px;
  transition: transform 0.4s;
}
/* 卡片悬停时图片放大效果 */
.spot-card:hover .spot-image {
  transform: scale(1.05);
}
/* 价格角标（右上角圆形标签） */
.price-badge {
  position: absolute;
  top: 10px;
  right: 10px;
  background: rgba(245, 108, 108, 0.9);
  color: white;
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: bold;
}
/* 免费景点的绿色角标 */
.price-badge.free {
  background: rgba(103, 194, 58, 0.9);
}

/* 卡片内容区域 */
.card-content {
  padding: 10px;
}
/* 卡片顶部：名称和城市标签左右分布 */
.card-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 8px;
}
.spot-name {
  margin: 0;
  font-size: 16px;
  color: #303133;
}
/* 城市标签（灰色圆角背景） */
.spot-city {
  font-size: 12px;
  color: #909399;
  background: #f4f4f5;
  padding: 2px 8px;
  border-radius: 10px;
}
/* 标签列表间距 */
.spot-tags {
  margin: 8px 0;
}
/* 建议游玩时长文字 */
.spot-time {
  font-size: 13px;
  color: #909399;
  margin: 8px 0 0 0;
}
</style>
