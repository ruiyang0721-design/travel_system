<!--
  App.vue —— 根组件
  ==================
  整个应用的最顶层组件，包含：
  
  结构：
  ├── el-header（顶部导航栏）
  │   ├── el-menu（导航菜单）
  │   │   ├── 首页菜单项 → /
  │   │   ├── 旅行规划菜单项 → /plan
  │   │   ├── 景点大厅菜单项 → /spots
  │   │   ├── 旅行日记菜单项 → /diaries
  │   │   ├── 弹性间隔（flex-grow: 1）
  │   │   └── 右侧用户区（已登录：头像+用户名+退出按钮 / 未登录：登录入口）
  │   └── position: sticky 吸顶效果
  │
  └── el-main（主内容区）
      └── router-view（路由视图，根据当前 URL 渲染对应页面组件）
          └── transition（页面切换淡入淡出动画）
-->

<template>
  <div class="common-layout">
    <el-container>
      <!-- ==================== 顶部导航栏 ==================== -->
      <el-header>
        <!-- 水平导航菜单，手动处理路由跳转 -->
        <el-menu
          mode="horizontal"
          :default-active="activeRoute"
          background-color="#409EFF"
          text-color="#fff"
          active-text-color="#ffd04b"
          :ellipsis="false"
        >
          <!-- 首页 -->
          <el-menu-item index="/" @click="$router.push('/')">
            <el-icon><HomeFilled /></el-icon>
            首页
          </el-menu-item>
          <!-- 旅行规划 -->
          <el-menu-item index="/plan" @click="$router.push('/plan')">
            <el-icon><Promotion /></el-icon>
            旅行规划
          </el-menu-item>
          <!-- 景点大厅 -->
          <el-menu-item index="/spots" @click="$router.push('/spots')">
            <el-icon><Location /></el-icon>
            景点大厅
          </el-menu-item>
          <!-- 旅行日记 -->
          <el-menu-item index="/diaries" @click="$router.push('/diaries')">
            <el-icon><Notebook /></el-icon>
            旅行日记
          </el-menu-item>
          
          <!-- 弹性间隔：将右侧用户区域推到最右边 -->
          <div style="flex-grow: 1;"></div>
          
          <!-- ===== 右侧用户区域（条件渲染） ===== -->
          
          <!-- 已登录状态：显示头像、用户名、退出按钮 -->
          <template v-if="username">
            <el-menu-item index="/profile" @click="$router.push('/profile')">
              <el-icon><User /></el-icon>
              个人中心
            </el-menu-item>
            <div style="display: flex; align-items: center; padding: 0 20px;">
              <!-- 用户头像：取用户名首字母大写显示 -->
              <el-avatar :size="32" style="margin-right: 10px; background: #ffd04b; color: #303133;">
                {{ username.charAt(0).toUpperCase() }}
              </el-avatar>
              <span style="color: white; margin-right: 15px; font-weight: bold;">{{ username }}</span>
              <!-- 退出登录按钮 -->
              <el-button type="danger" size="small" plain @click="handleLogout">退出</el-button>
            </div>
          </template>
          
          <!-- 未登录状态：显示登录/注册入口 -->
          <template v-else>
            <el-menu-item index="/login" @click="$router.push('/login')">登录 / 注册</el-menu-item>
          </template>
        </el-menu>
      </el-header>

      <!-- ==================== 主内容区 ==================== -->
      <el-main>
        <!-- router-view：根据当前 URL 渲染对应的页面组件 -->
        <router-view v-slot="{ Component }">
          <transition name="fade">
            <component :is="Component" />
          </transition>
        </router-view>
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
/**
 * 根组件逻辑
 * 
 * 功能：
 * 1. 从 localStorage 读取登录用户名，控制导航栏右侧显示
 * 2. 计算当前路由路径，高亮对应的导航菜单项
 * 3. 退出登录：清除 localStorage 中的 token 和用户名，刷新页面
 */
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { HomeFilled, Location, Notebook, User, Promotion } from '@element-plus/icons-vue'

// 获取当前路由对象，用于计算高亮的菜单项
const route = useRoute()

// 当前登录的用户名（从 localStorage 读取）
const username = ref('')

// 计算当前活跃的路由路径，用于菜单高亮
const activeRoute = computed(() => route.path)

// 组件挂载时从 localStorage 读取用户名
onMounted(() => {
  username.value = localStorage.getItem('username') || ''
})

/**
 * 退出登录处理
 * 清除 localStorage 中的认证信息，跳转到首页
 */
const handleLogout = () => {
  localStorage.removeItem('access_token')  // 清除 JWT Token
  localStorage.removeItem('username')       // 清除用户名
  username.value = ''
  window.location.href = '/'  // 强制刷新跳转首页
}
</script>

<style>
/* ===== 全局基础样式 ===== */
body {
  margin: 0;
  padding: 0;
  font-family: "Helvetica Neue", Helvetica, "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", Arial, sans-serif;
  background: #f5f7fa;
}

/* 导航栏吸顶效果 */
.el-header {
  padding: 0;
  box-shadow: 0 2px 12px rgba(0,0,0,0.1);  /* 底部阴影 */
  position: sticky;  /* 滚动时固定在顶部 */
  top: 0;
  z-index: 1000;     /* 确保在其他内容之上 */
}

/* ===== 页面切换动画 ===== */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.25s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
