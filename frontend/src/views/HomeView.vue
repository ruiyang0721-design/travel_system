<!--
  HomeView.vue —— 首页
  ====================
  系统的入口页面，包含以下模块：

  页面结构：
  ├── hero-section（轮播图区域）
  │   └── el-carousel（5张热门目的地轮播图，5秒自动切换）
  │
  ├── cta-section（行动号召区域）
  │   ├── 标题文字 "探索中国最美城市"
  │   └── "开始规划旅行" 按钮 → 跳转 /plan
  │
  └── recommend-section（推荐内容区域）
      ├── city-shortcuts（热门城市快捷入口）
      │   ├── section-title-bar（标题栏："热门目的地"）
      │   ├── city-grid（城市标签网格，7个城市）
      │   │   └── city-chip（城市标签：hover变蓝+动画，点击跳转 /spots?city=XX）
      │   └── expand-bar（展开/收起按钮，城市>6个时显示）
      │
      ├── section-header（热门景点标题 + "查看更多"按钮）
      │
      └── hotSpots（热门景点卡片列表）
          └── el-card（景点卡片：图片+评分角标+名称+标签+价格）
              └── el-dialog（景点快速预览弹窗：图片+详细信息+跳转详情按钮）
-->

<template>
  <div class="home-container">
    
    <!-- ==================== 轮播图区域 ==================== -->
    <!-- 展示5张热门目的地的风景图，每5秒自动切换 -->
    <div class="hero-section">
      <el-carousel height="45vh" indicator-position="none" :interval="5000">
        <el-carousel-item v-for="item in carouselItems" :key="item.id">
          <!-- 轮播背景图：使用 Unsplash 的高质量图片 -->
          <div class="carousel-bg" :style="{ backgroundImage: `url(${item.img})` }">
            <div class="carousel-content">
              <h2>{{ item.title }}</h2>
              <p>{{ item.desc }}</p>
            </div>
          </div>
        </el-carousel-item>
      </el-carousel>
    </div>

    <!-- ==================== 行动号召区域 (CTA) ==================== -->
    <!-- 引导用户点击"开始规划旅行"按钮 -->
    <div class="cta-section">
      <div class="cta-inner">
        <div class="cta-text">
          <h2>探索中国最美城市</h2>
          <p>发现精彩景点，规划专属旅程</p>
        </div>
        <!-- 点击跳转到旅行规划页 /plan -->
        <el-button type="primary" size="large" round @click="$router.push('/plan')" class="cta-btn">
          开始规划旅行
        </el-button>
      </div>
    </div>

    <!-- ==================== 热门城市快捷入口 ==================== -->
    <div class="recommend-section">
      <div class="city-shortcuts">
        <!-- 标题栏 -->
        <div class="section-title-bar">
          <h3>热门目的地</h3>
          <span class="section-subtitle">发现中国最值得一去的城市</span>
        </div>
        
        <!-- 城市标签网格 -->
        <div class="city-grid">
          <div
            class="city-chip"
            :class="{ 'city-chip-active': hoveredCity === city.name }"
            v-for="(city, index) in displayedCities"
            :key="city.name"
            :style="{ '--delay': index * 0.06 + 's' }"
            @mouseenter="onCityHover(city.name)"
            @mouseleave="onCityLeave"
            @click="goToSpots(city.name)"
          >
            <span class="city-name">{{ city.name }}</span>
            <span class="city-arrow">→</span>
          </div>
        </div>
        
        <!-- 展开/收起按钮：城市数量 > 6 时显示 -->
        <div class="expand-bar" v-if="cityList.length > 6" @click="citiesExpanded = !citiesExpanded">
          <span class="expand-text">{{ citiesExpanded ? '收起' : '展开更多' }}</span>
          <span class="expand-arrow" :class="{ 'arrow-up': citiesExpanded }">▾</span>
        </div>
      </div>

      <!-- ==================== 热门景点推荐 ==================== -->
      <!-- 标题会根据 hover 的城市动态变化 -->
      <div class="section-header" style="margin-top: 50px;">
        <h2>{{ hoveredCity ? hoveredCity + ' · 热门景点' : '热门景点推荐' }}</h2>
        <el-button text type="primary" @click="$router.push('/spots')">查看更多 →</el-button>
      </div>
      
      <!-- 景点卡片网格（4列） -->
      <el-row :gutter="20">
        <el-col :span="6" v-for="spot in hotSpots" :key="spot.id">
          <el-card shadow="hover" class="hot-card" :body-style="{ padding: '0px' }" style="cursor: pointer;" @click="openSpotDetail(spot)">
            <!-- 景点图片区域 -->
            <div class="img-wrapper">
              <!-- 使用 picsum 随机图片服务，seed 保证同一景点图片一致 -->
              <img :src="`https://picsum.photos/seed/${spot.name}/400/250`" class="hot-img" />
              <!-- 评分角标 -->
              <div class="img-overlay">
                <el-tag effect="dark" type="warning" size="small">⭐ {{ spot.rating }}</el-tag>
              </div>
            </div>
            <!-- 景点信息区域 -->
            <div style="padding: 14px">
              <span class="hot-name">{{ spot.name }}</span>
              <p class="hot-tags">{{ spot.city }} · {{ spot.tags }}</p>
              <div class="hot-bottom">
                <el-rate v-model="spot.rating" disabled size="small" />
                <span class="hot-price">¥{{ spot.price }}起</span>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>

    <!-- ==================== 景点快速预览弹窗 ==================== -->
    <!-- 点击景点卡片时弹出，展示详细信息，可跳转到完整详情页 -->
    <SpotPreviewDialog v-model:visible="dialogVisible" :spot="currentSpot" />
    </div>
  </div>
</template>

<script setup>
/**
 * 首页逻辑
 * 
 * 功能：
 * 1. 轮播图数据（静态配置的5个热门目的地）
 * 2. 城市列表（7个城市，支持展开/收起）
 * 3. 热门景点数据（从后端 API 获取）
 * 4. 城市 hover 联动：hover 某城市时，景点列表切换为该城市的景点
 * 5. 景点快速预览弹窗
 */
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import SpotPreviewDialog from '../components/SpotPreviewDialog.vue'

const router = useRouter()

// ===== 轮播图数据（静态配置） =====
const carouselItems = [
  { id: 1, title: '登长城 · 揽胜景', desc: '感受不到长城非好汉的气魄', img: 'https://images.unsplash.com/photo-1508804185872-d7badad00f7d?q=80&w=2070&auto=format&fit=crop' },
  { id: 2, title: '漫步外滩 · 璀璨上海', desc: '领略东方明珠与万国建筑群的交响', img: 'https://images.unsplash.com/photo-1474181487882-5abf3f0ba6c2?q=80&w=2070&auto=format&fit=crop' },
  { id: 3, title: '成都安逸 · 寻味锦里', desc: '在烟火气中遇见最慢的生活方式', img: 'https://images.unsplash.com/photo-1564507004663-b6dfb3c824d5?q=80&w=2070&auto=format&fit=crop' },
  { id: 4, title: '杭州西湖 · 人间天堂', desc: '欲把西湖比西子，淡妆浓抹总相宜', img: 'https://images.unsplash.com/photo-1598887142487-3c854d51eabb?q=80&w=2070&auto=format&fit=crop' },
  { id: 5, title: '重庆山城 · 魔幻都市', desc: '8D魔幻城市，火锅与夜景的碰撞', img: 'https://images.unsplash.com/photo-1533929736458-ca588d08c8be?q=80&w=2070&auto=format&fit=crop' },
]

// ===== 城市列表 =====
const cityList = [
  { name: '北京' },
  { name: '上海' },
  { name: '成都' },
  { name: '西安' },
  { name: '杭州' },
  { name: '重庆' },
  { name: '广州' },
]

// ===== 响应式状态 =====
const hotSpots = ref([])          // 当前展示的景点列表
const allHotSpots = ref([])       // 全部热门景点（默认展示）
const hoveredCity = ref('')       // 当前 hover 的城市名称
const citiesExpanded = ref(false) // 城市列表是否展开
const dialogVisible = ref(false)  // 景点预览弹窗是否显示
const currentSpot = ref({})       // 当前预览的景点数据
let hoverTimer = null             // hover 防抖定时器

// 计算属性：根据展开状态决定显示前6个还是全部城市
const displayedCities = computed(() => {
  return citiesExpanded.value ? cityList : cityList.slice(0, 6)
})

// 打开景点预览弹窗
const openSpotDetail = (spot) => {
  currentSpot.value = spot
  dialogVisible.value = true
}

// 跳转到景点大厅并自动筛选该城市
const goToSpots = (city) => {
  router.push({ path: '/spots', query: { city } })
}

// 鼠标进入城市标签：清除定时器，加载该城市的景点
const onCityHover = (cityName) => {
  clearTimeout(hoverTimer)
  hoveredCity.value = cityName
  fetchCitySpots(cityName)
}

// 鼠标离开城市标签：延迟恢复默认景点列表（防抖）
const onCityLeave = () => {
  clearTimeout(hoverTimer)
  hoverTimer = setTimeout(() => {
    hoveredCity.value = ''
    hotSpots.value = allHotSpots.value
  }, 200)
}

// 获取指定城市的景点列表
const fetchCitySpots = async (city) => {
  try {
    const res = await axios.get('http://127.0.0.1:8000/api/spots/', { params: { city, tag: '', search: '' } })
    hotSpots.value = res.data.data.slice(0, 8)  // 最多显示8个
  } catch (err) {
    console.error('获取城市景点失败', err)
  }
}

// 获取全部热门景点（默认展示）
const fetchHotSpots = async () => {
  try {
    const res = await axios.get('http://127.0.0.1:8000/api/spots/', { params: { tag: '', search: '' } })
    allHotSpots.value = res.data.data.slice(0, 8)
    hotSpots.value = allHotSpots.value
  } catch (err) {
    console.error('获取热门景点失败', err)
  }
}

// 组件挂载时加载热门景点数据
onMounted(() => {
  fetchHotSpots()
})
</script>

<style scoped>
/* ===== 轮播图区域样式 ===== */
.hero-section {
  position: relative;
}
.carousel-bg {
  height: 100%;
  background-size: cover;
  background-position: center;
  display: flex;
  align-items: center;
  justify-content: center;
}
.carousel-content {
  text-align: center;
  color: white;
  background: rgba(0,0,0,0.35);
  padding: 16px 60px;
  border-radius: 12px;
  transform: translateY(-40px);
}
.carousel-content h2 { font-size: 2.5rem; margin-bottom: 10px; }
.carousel-content p { font-size: 1.1rem; opacity: 0.9; }

/* ===== CTA 行动号召区域样式 ===== */
.cta-section {
  background: linear-gradient(135deg, #409EFF 0%, #66b1ff 50%, #a0cfff 100%);
  padding: 28px 10%;
}
.cta-inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  max-width: 1200px;
  margin: 0 auto;
}
.cta-text h2 {
  margin: 0 0 4px;
  font-size: 1.5rem;
  color: white;
  font-weight: 700;
}
.cta-text p {
  margin: 0;
  font-size: 0.95rem;
  color: rgba(255,255,255,0.85);
}
.cta-btn {
  font-size: 16px;
  padding: 12px 32px;
  background: white !important;
  color: #409EFF !important;
  border: none !important;
  font-weight: 600;
  box-shadow: 0 4px 16px rgba(0,0,0,0.15);
  transition: transform 0.3s, box-shadow 0.3s;
}
.cta-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 24px rgba(0,0,0,0.2);
}

/* ===== 推荐内容区域样式 ===== */
.recommend-section {
  padding: 20px 10% 40px;
}
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 25px;
}

/* ===== 景点卡片样式 ===== */
.img-wrapper {
  position: relative;
  overflow: hidden;
}
.hot-img { 
  width: 100%; 
  height: 200px; 
  object-fit: cover;
  transition: transform 0.4s;
}
.hot-card:hover .hot-img {
  transform: scale(1.05);  /* hover 时图片微放大 */
}
.img-overlay {
  position: absolute;
  top: 10px;
  right: 10px;
}
.hot-name { font-weight: bold; font-size: 1.1rem; }
.hot-tags { font-size: 12px; color: #909399; margin: 5px 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.hot-bottom { display: flex; justify-content: space-between; align-items: center; margin-top: 10px; }
.hot-price { color: #f56c6c; font-weight: bold; }

/* ===== 城市快捷入口样式 ===== */
.city-shortcuts {
  margin-top: 10px;
  padding-top: 20px;
  border-top: 1px solid #ebeef5;
}
.section-title-bar {
  display: flex;
  align-items: baseline;
  gap: 12px;
  margin-bottom: 24px;
}
.section-title-bar h3 {
  margin: 0;
  color: #1a1a2e;
  font-size: 22px;
  font-weight: 700;
  letter-spacing: 0.5px;
}
.section-subtitle {
  font-size: 13px;
  color: #909399;
}
.city-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 14px;
}
.city-chip {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 28px;
  background: linear-gradient(135deg, #f8faff 0%, #eef2ff 100%);
  border: 1px solid #e0e6f6;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  min-width: 100px;
  animation: chipFadeIn 0.5s ease both;
  animation-delay: var(--delay);  /* 交错入场动画延迟 */
}
/* 城市标签入场动画 */
@keyframes chipFadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
.city-chip:hover {
  background: linear-gradient(135deg, #409EFF 0%, #66b1ff 100%);
  color: white;
  border-color: #409EFF;
  transform: translateY(-3px);
  box-shadow: 0 8px 24px rgba(64, 158, 255, 0.25);
}
.city-chip:hover .city-name { color: white; }
.city-chip:hover .city-arrow { opacity: 1; transform: translateX(0); color: white; }
.city-chip-active {
  background: linear-gradient(135deg, #409EFF 0%, #66b1ff 100%) !important;
  color: white !important;
  border-color: #409EFF !important;
  transform: translateY(-3px);
  box-shadow: 0 8px 24px rgba(64, 158, 255, 0.25);
}
.city-chip-active .city-name { color: white !important; }
.city-chip-active .city-arrow { opacity: 1 !important; transform: translateX(0) !important; color: white !important; }
.city-name {
  font-size: 15px;
  font-weight: 600;
  color: #303133;
  transition: color 0.3s;
  letter-spacing: 1px;
}
.city-arrow {
  font-size: 14px;
  color: #409EFF;
  opacity: 0;
  transform: translateX(-6px);
  transition: all 0.3s;
  margin-left: 8px;
}

/* ===== 展开/收起按钮样式 ===== */
.expand-bar {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  margin-top: 24px;
  padding: 12px 0;
  cursor: pointer;
  transition: all 0.3s;
  border-radius: 8px;
}
.expand-bar:hover { background: #f5f7fa; }
.expand-text {
  font-size: 13px;
  color: #909399;
  transition: color 0.3s;
}
.expand-bar:hover .expand-text { color: #409EFF; }
.expand-arrow {
  font-size: 16px;
  color: #909399;
  transition: all 0.3s;
  display: inline-block;
}
.expand-bar:hover .expand-arrow { color: #409EFF; }
.arrow-up { transform: rotate(180deg); }
</style>
