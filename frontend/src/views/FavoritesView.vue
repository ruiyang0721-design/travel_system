<!--
  FavoritesView.vue - 我的收藏页面
  ===================================
  功能概述：
    展示当前登录用户收藏的所有景点，支持取消收藏操作。
    未登录时显示登录提示，无收藏时显示空状态。

  页面结构：
    1. 页面标题（💖 我的收藏）
    2. 未登录提示（引导去登录）
    3. 加载状态
    4. 空收藏提示（引导去逛逛景点）
    5. 收藏景点卡片网格（4列布局，含图片、评分、价格、取消收藏按钮）
-->
<template>
  <div class="favorites-page">
    <!-- 页面标题 -->
    <h1 class="page-title">💖 我的收藏</h1>

    <!-- 未登录状态：显示登录引导 -->
    <div v-if="!token" class="login-prompt">
      <el-empty description="请先登录后查看收藏">
        <el-button type="primary" @click="showLoginDialog">去登录</el-button>
      </el-empty>
    </div>

    <!-- 加载中状态 -->
    <div v-else-if="loading" v-loading="true" style="height: 300px;"></div>

    <!-- 无收藏状态：引导用户去浏览景点 -->
    <div v-else-if="favorites.length === 0">
      <el-empty description="还没有收藏任何景点">
        <el-button type="primary" @click="$router.push('/spots')">去逛逛</el-button>
      </el-empty>
    </div>

    <!-- ===== 收藏景点卡片网格 ===== -->
    <div v-else>
      <el-row :gutter="20">
        <el-col :span="6" v-for="fav in favorites" :key="fav.id" style="margin-bottom: 20px;">
          <el-card shadow="hover" class="fav-card" :body-style="{ padding: '0px' }">
            <!-- 景点图片（点击跳转详情页）+ 评分角标 -->
            <div class="img-wrapper" style="cursor: pointer;" @click="$router.push(`/spot/${fav.spot.name}`)">
              <img :src="`https://picsum.photos/seed/${fav.spot.name}/400/250`" class="fav-img" />
              <!-- 右上角评分标签 -->
              <div class="img-overlay">
                <el-tag effect="dark" type="warning" size="small">⭐ {{ fav.spot.rating }}</el-tag>
              </div>
            </div>
            <!-- 卡片内容：名称、城市地址、价格、取消收藏按钮 -->
            <div style="padding: 14px;">
              <h3 style="margin: 0 0 8px 0; font-size: 16px; cursor: pointer;" @click="$router.push(`/spot/${fav.spot.name}`)">
                {{ fav.spot.name }}
              </h3>
              <p style="font-size: 12px; color: #909399; margin: 0 0 8px 0;">{{ fav.spot.city }} · {{ fav.spot.address }}</p>
              <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="color: #f56c6c; font-weight: bold;">¥{{ fav.spot.price }}</span>
                <el-button type="danger" size="small" plain @click="removeFav(fav)">取消收藏</el-button>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script setup>
/**
 * FavoritesView.vue - 我的收藏页面逻辑
 * 
 * 主要功能：
 * - 获取当前用户的收藏列表（GET /api/favorites/）
 * - 取消收藏（POST /api/favorites/toggle/）
 * - 未登录时显示登录引导
 */
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'

/** 收藏列表数据 */
const favorites = ref([])

/** 数据加载状态 */
const loading = ref(true)

/** JWT token（从 localStorage 获取，用于判断登录状态和认证请求） */
const token = localStorage.getItem('access_token')

const router = useRouter()

/**
 * 显示登录提示弹窗
 */
const showLoginDialog = () => {
  ElMessageBox.confirm(
    '请先登录后查看收藏',
    '提示',
    { confirmButtonText: '去登录', cancelButtonText: '取消', type: 'warning' }
  ).then(() => { router.push('/login') }).catch(() => {})
}

/**
 * 从后端获取收藏列表
 * 未登录时直接返回，不发送请求
 */
const fetchFavorites = async () => {
  if (!token) {
    loading.value = false
    return
  }
  try {
    const res = await axios.get('http://127.0.0.1:8000/api/favorites/', {
      headers: { Authorization: `Bearer ${token}` }
    })
    favorites.value = res.data.data
  } catch (err) {
    console.error('获取收藏失败', err)
  } finally {
    loading.value = false
  }
}

/**
 * 取消收藏
 * 调用 toggle 接口后从本地列表中移除该收藏项（避免重新请求）
 * @param {Object} fav - 收藏对象，包含 fav.spot.id
 */
const removeFav = async (fav) => {
  try {
    await axios.post('http://127.0.0.1:8000/api/favorites/toggle/', 
      { spot_id: fav.spot.id },
      { headers: { Authorization: `Bearer ${token}` } }
    )
    // 从本地列表中移除（乐观更新，无需重新请求）
    favorites.value = favorites.value.filter(f => f.id !== fav.id)
    ElMessage.success('已取消收藏')
  } catch (err) {
    ElMessage.error('操作失败')
  }
}

// 组件挂载时获取收藏列表
onMounted(fetchFavorites)
</script>

<style scoped>
/* 页面整体布局 */
.favorites-page {
  padding: 20px 8%;
  max-width: 1200px;
  margin: 0 auto;
}
.page-title {
  color: #303133;
  margin-bottom: 30px;
}

/* 收藏卡片：圆角 + 悬停上浮效果 */
.fav-card {
  border-radius: 12px;
  overflow: hidden;
  transition: transform 0.3s;
}
.fav-card:hover {
  transform: translateY(-5px);
}

/* 图片容器（用于定位评分角标） */
.img-wrapper {
  position: relative;
  overflow: hidden;
}
.fav-img {
  width: 100%;
  height: 180px;
  object-fit: cover;
  transition: transform 0.4s;
}
/* 卡片悬停时图片放大 */
.fav-card:hover .fav-img {
  transform: scale(1.05);
}
/* 评分角标定位 */
.img-overlay {
  position: absolute;
  top: 10px;
  right: 10px;
}
/* 未登录提示区域 */
.login-prompt {
  padding: 100px 0;
}
</style>
