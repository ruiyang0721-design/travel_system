/**
 * Vue Router 路由配置
 * ===================
 * 定义系统中所有页面的 URL 路由映射，共 9 个页面：
 *
 * 页面路由表：
 * | 路径            | 页面组件          | 说明         |
 * |----------------|-------------------|-------------|
 * | /              | HomeView          | 首页         |
 * | /plan          | PlanView          | 旅行规划页    |
 * | /plan-result   | PlanResultView    | 规划结果页    |
 * | /spots         | SpotsView         | 景点大厅      |
 * | /spot/:id      | SpotDetailView    | 景点详情页    |
 * | /favorites     | FavoritesView     | 我的收藏      |
 * | /profile       | ProfileView       | 个人中心      |
 * | /diaries       | DiariesView       | 旅行日记广场   |
 * | /login         | LoginView         | 登录注册页    |
 *
 * 所有页面组件使用懒加载 (import())，首屏只加载当前页面的代码
 */

import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Home',
    // 首页：轮播图 + 城市快捷入口 + 热门景点推荐 + AI 对话入口
    component: () => import('../views/HomeView.vue')
  },
  {
    path: '/plan',
    name: 'Plan',
    // 旅行规划页：表单模式（城市/天数/偏好/酒店）+ AI 对话模式
    component: () => import('../views/PlanView.vue')
  },
  {
    path: '/plan-result',
    name: 'PlanResult',
    // 规划结果页：行程明细（拖拽排序）+ 路线地图 + 预算汇总 + 天气
    // 通过 query 参数接收规划参数：city, days, tags, hotelName, hotelLat, hotelLng
    component: () => import('../views/PlanResultView.vue')
  },
  {
    path: '/spots',
    name: 'Spots',
    // 景点大厅：全部景点浏览，支持搜索/城市/标签筛选
    // 支持从首页城市快捷入口通过 query.city 参数自动筛选
    component: () => import('../views/SpotsView.vue')
  },
  {
    path: '/spot/:name',
    name: 'SpotDetail',
    // 景点详情页：大图展示 + 完整信息 + 收藏 + 攻略列表 + 发布攻略
    // :name 是动态路由参数，表示景点名称
    component: () => import('../views/SpotDetailView.vue')
  },
  {
    path: '/favorites',
    name: 'Favorites',
    // 我的收藏页：登录用户的收藏景点列表，支持取消收藏
    component: () => import('../views/FavoritesView.vue')
  },
  {
    path: '/profile',
    name: 'Profile',
    // 个人中心：概览统计 + 我的收藏 + 我的日记 + 我的攻略 + 我的行程 + 账号设置
    component: () => import('../views/ProfileView.vue')
  },
  {
    path: '/diaries',
    name: 'Diaries',
    // 旅行日记广场：浏览所有用户的旅行日记，支持按城市筛选
    component: () => import('../views/DiariesView.vue')
  },
  {
    path: '/login',
    name: 'Login',
    // 登录注册页：Tab 切换登录/注册表单
    component: () => import('../views/LoginView.vue')
  }
]

// 创建路由实例
// history: createWebHistory() 使用 HTML5 History 模式，URL 不带 # 号
const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
