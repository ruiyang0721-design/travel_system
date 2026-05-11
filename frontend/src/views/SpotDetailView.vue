<!--
  SpotDetailView.vue - 景点详情页面
  ====================================
  功能概述：
    展示单个景点的完整信息，包括：
    - 顶部大图 + 基本信息卡片（城市、地址、门票、游玩时长、标签）
    - 收藏/取消收藏功能（需登录）
    - 快速加入规划功能
    - 旅行攻略列表（用户发布的攻略内容）
    - 发布攻略弹窗（需登录）

  页面结构：
    1. 返回按钮 + 景点名称标题
    2. 两栏布局：左侧大图，右侧信息面板 + 操作按钮
    3. 攻略区域（攻略列表 + 写攻略按钮）
    4. 写攻略弹窗（类型选择 + 标题 + 内容）
-->
<template>
  <div class="detail-page" v-loading="loading">
    <div v-if="spot" class="detail-content">
      <!-- 返回按钮（返回上一页）+ 景点名称 -->
      <el-page-header @back="$router.back()" style="margin-bottom: 20px;">
        <template #content>
          <span class="text-large font-600">{{ spot.name }}</span>
        </template>
      </el-page-header>

      <!-- ===== 顶部两栏布局：左侧大图 + 右侧信息面板 ===== -->
      <el-row :gutter="24">
        <!-- 左侧：景点大图 + 评分角标 -->
        <el-col :span="14">
          <div class="hero-image">
            <img :src="`https://picsum.photos/seed/${spot.name}/800/500`" />
            <!-- 右上角评分角标 -->
            <div class="image-badge">
              <el-tag effect="dark" type="warning" size="large">⭐ {{ spot.rating }} 分</el-tag>
            </div>
          </div>
        </el-col>
        <!-- 右侧：信息面板（名称、简介、详细信息、操作按钮） -->
        <el-col :span="10">
          <el-card shadow="never" class="info-panel">
            <h2 style="margin-top: 0;">{{ spot.name }}</h2>
            <p class="desc-text">{{ spot.description || '暂无简介' }}</p>
            
            <!-- 景点详细信息表格 -->
            <el-descriptions :column="1" border size="small">
              <el-descriptions-item label="城市">{{ spot.city }}</el-descriptions-item>
              <el-descriptions-item label="地址">{{ spot.address || '暂无' }}</el-descriptions-item>
              <el-descriptions-item label="门票">
                <span style="color: #f56c6c; font-weight: bold; font-size: 18px;">¥ {{ spot.price }}</span>
                <!-- 免费景点显示绿色标签 -->
                <el-tag v-if="spot.price == 0" type="success" size="small" style="margin-left: 10px;">免费</el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="游玩时间">{{ spot.duration }} 小时</el-descriptions-item>
              <el-descriptions-item label="标签">
                <el-tag v-for="tag in (spot.tags || '').split(',')" :key="tag" size="small" type="success" style="margin-right: 5px;">{{ tag }}</el-tag>
              </el-descriptions-item>
            </el-descriptions>

            <!-- 操作按钮区域：收藏 -->
            <div class="action-buttons">
              <el-button type="primary" size="large" @click="toggleFav" :loading="favLoading">
                {{ isFavorite ? '💖 已收藏' : '🤍 收藏景点' }}
              </el-button>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <!-- ===== 攻略区域 ===== -->
      <!-- 展示该景点下的所有用户攻略，支持发布新攻略 -->
      <el-card shadow="never" style="margin-top: 24px;">
        <template #header>
          <div class="card-header">
            <h3>📋 旅行攻略 ({{ tips.length }})</h3>
            <!-- 写攻略按钮（弹出发布弹窗） -->
            <el-button type="primary" size="small" @click="showTipDialog = true">✏️ 写攻略</el-button>
          </div>
        </template>

        <!-- 空状态：暂无攻略 -->
        <div v-if="tips.length === 0" class="empty-tips">
          <el-empty description="还没有攻略，快来写第一条吧！" />
        </div>

        <!-- 攻略列表 -->
        <div v-else>
          <div v-for="tip in tips" :key="tip.id" class="tip-item">
            <div class="tip-header">
              <!-- 攻略类型标签（不同类型不同颜色） -->
              <el-tag :type="getTipTagType(tip.tip_type)" size="small">{{ tip.type_display }}</el-tag>
              <span class="tip-title">{{ tip.title }}</span>
              <span class="tip-meta">{{ tip.username }} · {{ formatDate(tip.created_at) }}</span>
            </div>
            <p class="tip-content">{{ tip.content }}</p>
          </div>
        </div>
      </el-card>

      <!-- ===== 写攻略弹窗 ===== -->
      <el-dialog v-model="showTipDialog" title="发布攻略" width="500px">
        <el-form :model="tipForm" label-width="60px">
          <!-- 攻略类型选择 -->
          <el-form-item label="类型">
            <el-select v-model="tipForm.tip_type" style="width: 100%">
              <el-option label="实用建议" value="实用建议" />
              <el-option label="避坑指南" value="避坑指南" />
              <el-option label="美食推荐" value="美食推荐" />
              <el-option label="交通攻略" value="交通攻略" />
              <el-option label="拍照技巧" value="拍照技巧" />
            </el-select>
          </el-form-item>
          <!-- 攻略标题 -->
          <el-form-item label="标题">
            <el-input v-model="tipForm.title" placeholder="一句话概括" />
          </el-form-item>
          <!-- 攻略内容 -->
          <el-form-item label="内容">
            <el-input v-model="tipForm.content" type="textarea" :rows="5" placeholder="分享你的经验..." />
          </el-form-item>
        </el-form>
        <template #footer>
          <el-button @click="showTipDialog = false">取消</el-button>
          <el-button type="primary" @click="submitTip" :loading="tipSubmitting">发布</el-button>
        </template>
      </el-dialog>

    </div>
  </div>
</template>

<script setup>
/**
 * SpotDetailView.vue - 景点详情页逻辑
 * 
 * 主要功能：
 * - 根据路由参数获取景点详情和攻略列表
 * - 收藏/取消收藏（需登录，调用 toggle API）
 * - 加入规划（跳转到规划结果页）
 * - 发布攻略（需登录）
 */
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'

/** 路由对象（获取路径参数） */
const route = useRoute()
/** 路由实例（用于编程式导航） */
const router = useRouter()

/** 景点详情数据 */
const spot = ref(null)
/** 页面加载状态 */
const loading = ref(true)
/** 是否已收藏 */
const isFavorite = ref(false)
/** 收藏操作加载状态 */
const favLoading = ref(false)
/** 攻略列表 */
const tips = ref([])
/** 是否显示写攻略弹窗 */
const showTipDialog = ref(false)
/** 攻略提交加载状态 */
const tipSubmitting = ref(false)

/**
 * 攻略表单数据
 * @property {string} tip_type - 攻略类型
 * @property {string} title - 攻略标题
 * @property {string} content - 攻略内容
 */
const tipForm = ref({
  tip_type: '实用建议',
  title: '',
  content: ''
})

/** JWT token（用于需要认证的 API 请求） */
const token = localStorage.getItem('access_token')
/** 请求头（带认证信息） */
const authHeaders = token ? { Authorization: `Bearer ${token}` } : {}

/**
 * 从后端获取景点详情和攻略列表
 */
const fetchSpot = async () => {
  try {
    const res = await axios.get(`http://127.0.0.1:8000/api/spots/${route.params.name}/`)
    spot.value = res.data.data
    tips.value = res.data.data.tips || []
  } catch (err) {
    ElMessage.error('景点不存在或加载失败')
    router.back()
  } finally {
    loading.value = false
  }
}

/**
 * 检查当前用户是否已收藏该景点
 * 仅在用户已登录时调用
 */
const checkFav = async () => {
  if (!token || !spot.value) return
  try {
    const res = await axios.get(`http://127.0.0.1:8000/api/favorites/check/${spot.value.id}/`, {
      headers: authHeaders
    })
    isFavorite.value = res.data.is_favorite
  } catch (err) {
    // 忽略检查失败（如 token 过期）
  }
}

/**
 * 切换收藏状态（收藏/取消收藏）
 * 未登录时跳转到登录页
 */
const toggleFav = async () => {
  if (!token) {
    ElMessageBox.confirm(
      '请先登录后再收藏景点',
      '提示',
      { confirmButtonText: '去登录', cancelButtonText: '取消', type: 'warning' }
    ).then(() => { router.push('/login') }).catch(() => {})
    return
  }
  if (!spot.value) return
  favLoading.value = true
  try {
    const res = await axios.post('http://127.0.0.1:8000/api/favorites/toggle/', 
      { spot_id: spot.value.id },
      { headers: authHeaders }
    )
    // 根据后端返回的 action 字段判断是收藏还是取消
    isFavorite.value = res.data.action === 'added'
    ElMessage.success(res.data.message)
  } catch (err) {
    ElMessage.error('操作失败')
  } finally {
    favLoading.value = false
  }
}

/**
 * 提交攻略到后端
 * 校验必填项后发送 POST 请求，成功后刷新页面数据
 */
const submitTip = async () => {
  if (!token) {
    ElMessage.warning('请先登录！')
    return
  }
  if (!tipForm.value.title || !tipForm.value.content) {
    ElMessage.warning('请填写标题和内容')
    return
  }
  tipSubmitting.value = true
  try {
    await axios.post('http://127.0.0.1:8000/api/tips/create/', {
      spot: spot.value.id,
      ...tipForm.value
    }, { headers: authHeaders })
    ElMessage.success('攻略发布成功！')
    showTipDialog.value = false
    // 重置表单
    tipForm.value = { tip_type: '实用建议', title: '', content: '' }
    fetchSpot() // 刷新攻略列表
  } catch (err) {
    ElMessage.error('发布失败，请先登录')
  } finally {
    tipSubmitting.value = false
  }
}

/**
 * 根据攻略类型返回对应的标签颜色
 * @param {string} type - 攻略类型名称
 * @returns {string} Element Plus 标签类型
 */
const getTipTagType = (type) => {
  const map = {
    '实用建议': 'primary',
    '避坑指南': 'danger',
    '美食推荐': 'warning',
    '交通攻略': 'info',
    '拍照技巧': 'success'
  }
  return map[type] || 'info'
}

/**
 * 格式化日期为中文本地格式
 * @param {string} dateStr - ISO 日期字符串
 * @returns {string} 格式化后的日期
 */
const formatDate = (dateStr) => {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleDateString('zh-CN')
}

// 组件挂载时获取景点详情和检查收藏状态
onMounted(async () => {
  await fetchSpot()
  checkFav()
})
</script>

<style scoped>
/* 页面整体布局 */
.detail-page {
  padding: 20px 8%;
  max-width: 1200px;
  margin: 0 auto;
}

/* 左侧大图容器（带圆角和阴影） */
.hero-image {
  position: relative;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(0,0,0,0.1);
}
.hero-image img {
  width: 100%;
  height: 400px;
  object-fit: cover;
}
/* 右上角评分角标定位 */
.image-badge {
  position: absolute;
  top: 15px;
  right: 15px;
}

/* 右侧信息面板 */
.info-panel {
  height: 100%;
  border-radius: 12px;
}
.info-panel h2 {
  color: #303133;
  margin-bottom: 10px;
}
/* 景点简介文字样式 */
.desc-text {
  color: #606266;
  font-size: 14px;
  line-height: 1.8;
  margin-bottom: 20px;
}

/* 操作按钮区域 */
.action-buttons {
  margin-top: 20px;
  display: flex;
  gap: 10px;
}
.action-buttons .el-button {
  flex: 1;
}

/* 攻略区域卡片头部 */
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.card-header h3 {
  margin: 0;
}

/* 单条攻略项 */
.tip-item {
  padding: 15px 0;
  border-bottom: 1px solid #f0f0f0;
}
.tip-item:last-child {
  border-bottom: none;
}
/* 攻略头部：类型标签 + 标题 + 作者/时间 */
.tip-header {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
}
.tip-title {
  font-weight: bold;
  margin-left: 10px;
  color: #303133;
}
.tip-meta {
  margin-left: auto;
  font-size: 12px;
  color: #c0c4cc;
}
/* 攻略内容文字 */
.tip-content {
  color: #606266;
  font-size: 14px;
  line-height: 1.6;
  margin: 0;
}
/* 空攻略区域 */
.empty-tips {
  padding: 30px;
}
</style>
