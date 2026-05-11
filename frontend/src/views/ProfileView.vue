<!--
  ProfileView.vue - 个人中心页面
  =================================
  功能概述：
    用户个人中心，包含左侧导航和右侧内容区域，支持以下模块：
    - 个人概览：收藏数、日记数、攻略数统计卡片 + 最近动态
    - 我的收藏：已收藏景点列表，支持取消收藏
    - 我的日记：已发布日记列表，支持删除
    - 我的攻略：已发布攻略列表
    - 我的行程：已保存行程列表，支持查看和删除
    - 账号设置：修改密码、查看账号信息

  页面结构：
    1. 左侧导航栏（用户头像 + 用户名 + 导航菜单，带未读数量角标）
    2. 右侧内容区域（根据 activeTab 切换显示不同模块）
-->
<template>
  <div class="profile-page">
    <el-row :gutter="24">
      <!-- ===== 左侧导航栏 ===== -->
      <el-col :span="5">
        <div class="side-card">
          <!-- 用户信息区域：头像 + 用户名 + 加入日期 -->
          <div class="user-info">
            <div class="avatar-ring">
              <el-avatar :size="72" class="user-avatar">
                {{ username.charAt(0).toUpperCase() }}
              </el-avatar>
            </div>
            <h3 class="username">{{ username }}</h3>
            <p class="join-date">加入于 {{ formatDate(profile.date_joined) }}</p>
          </div>

          <!-- 导航菜单：每个菜单项可点击切换右侧内容 -->
          <div class="side-nav">
            <div
              v-for="item in navItems"
              :key="item.key"
              class="nav-item"
              :class="{ active: activeTab === item.key }"
              @click="activeTab = item.key"
            >
              <span class="nav-label">{{ item.label }}</span>
              <!-- 未读数量角标（仅部分菜单显示） -->
              <span v-if="item.count !== undefined" class="nav-badge">{{ item.count }}</span>
            </div>
          </div>
        </div>
      </el-col>

      <!-- ===== 右侧内容区域 ===== -->
      <el-col :span="19">

        <!-- ===== 个人概览模块 ===== -->
        <div v-if="activeTab === 'overview'">
          <div class="section-header">
            <h2 class="section-title">个人概览</h2>
          </div>

          <!-- 统计卡片行：收藏数、日记数、攻略数（点击可跳转对应模块） -->
          <el-row :gutter="20" class="stats-row">
            <el-col :span="8">
              <StatsCard title="收藏景点" :value="profile.favorites_count" color="red" clickable @click="activeTab = 'favorites'" />
            </el-col>
            <el-col :span="8">
              <StatsCard title="旅行日记" :value="profile.diaries_count" color="blue" clickable @click="activeTab = 'diaries'" />
            </el-col>
            <el-col :span="8">
              <StatsCard title="发布攻略" :value="profile.tips_count" color="orange" clickable @click="activeTab = 'tips'" />
            </el-col>
          </el-row>

          <!-- 最近动态列表（展示最近的收藏和日记操作） -->
          <div class="recent-card">
            <div class="recent-header">最近动态</div>
            <div v-if="recentItems.length === 0" class="empty-hint">
              还没有动态，快去探索吧
            </div>
            <div v-for="item in recentItems" :key="item.id" class="recent-item">
              <!-- 彩色圆点标识不同类型动态 -->
              <div class="recent-dot" :class="item.dotClass"></div>
              <div class="recent-content">
                <span class="recent-title">{{ item.title }}</span>
                <span class="recent-time">{{ item.time }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- ===== 我的收藏模块 ===== -->
        <div v-if="activeTab === 'favorites'">
          <div class="section-header">
            <h2 class="section-title">我的收藏</h2>
            <span class="section-count">共 {{ favorites.length }} 个</span>
          </div>

          <!-- 空收藏状态 -->
          <div v-if="favorites.length === 0" class="empty-state">
            <p class="empty-text">还没有收藏任何景点</p>
            <el-button type="primary" @click="$router.push('/spots')">去逛逛</el-button>
          </div>

          <!-- 收藏景点卡片网格（3列布局） -->
          <el-row :gutter="20" v-else>
            <el-col :span="8" v-for="fav in favorites" :key="fav.id" style="margin-bottom: 20px;">
              <div class="fav-card">
                <!-- 景点图片（点击跳转详情）+ 评分角标 -->
                <div class="img-wrapper" @click="$router.push(`/spot/${fav.spot.name}`)">
                  <img :src="`https://picsum.photos/seed/${fav.spot.name}/400/250`" class="card-img" />
                  <div class="img-rating">{{ fav.spot.rating }}</div>
                </div>
                <!-- 景点信息：名称、城市、价格、取消收藏 -->
                <div class="fav-body">
                  <h3 class="fav-name" @click="$router.push(`/spot/${fav.spot.name}`)">{{ fav.spot.name }}</h3>
                  <p class="fav-city">{{ fav.spot.city }}</p>
                  <div class="fav-bottom">
                    <span class="fav-price">{{ fav.spot.price == 0 ? '免费' : '¥' + fav.spot.price }}</span>
                    <el-button type="danger" size="small" plain @click="removeFav(fav)">取消收藏</el-button>
                  </div>
                </div>
              </div>
            </el-col>
          </el-row>
        </div>

        <!-- ===== 我的日记模块 ===== -->
        <div v-if="activeTab === 'diaries'">
          <div class="section-header">
            <h2 class="section-title">我的日记</h2>
            <span class="section-count">共 {{ myDiaries.length }} 篇</span>
          </div>

          <!-- 空日记状态 -->
          <div v-if="myDiaries.length === 0" class="empty-state">
            <p class="empty-text">还没有写过日记</p>
            <el-button type="primary" @click="$router.push('/diaries')">去看看</el-button>
          </div>

          <!-- 日记卡片列表 -->
          <div v-else>
            <div v-for="diary in myDiaries" :key="diary.id" class="diary-card">
              <div class="diary-header">
                <h3 class="diary-title">{{ diary.title }}</h3>
                <div class="diary-tags">
                  <span class="tag tag-blue">{{ diary.city }}</span>
  
                </div>
              </div>
              <!-- 日记内容（最多显示3行） -->
              <p class="diary-content">{{ diary.content }}</p>
              <!-- 日记底部：星级评分 + 发布时间 + 删除按钮 -->
              <div class="diary-footer">
                <div class="diary-rating">
                  <span v-for="i in 5" :key="i" class="star" :class="{ 'star-active': i <= diary.rating }">&#9733;</span>
                </div>
                <div class="diary-actions">
                  <span class="diary-time">{{ formatDate(diary.created_at) }}</span>
                  <el-button type="primary" size="small" plain @click="openEditDiary(diary)">编辑</el-button>
                  <el-button type="danger" size="small" plain @click="deleteDiary(diary)">删除</el-button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- ===== 我的攻略模块 ===== -->
        <div v-if="activeTab === 'tips'">
          <div class="section-header">
            <h2 class="section-title">我的攻略</h2>
            <span class="section-count">共 {{ myTips.length }} 篇</span>
          </div>

          <!-- 空攻略状态 -->
          <div v-if="myTips.length === 0" class="empty-state">
            <p class="empty-text">还没有发布过攻略</p>
            <el-button type="primary" @click="$router.push('/spots')">去逛逛</el-button>
          </div>

          <!-- 攻略卡片列表 -->
          <div v-else>
            <div v-for="tip in myTips" :key="tip.id" class="tip-card">
              <div class="tip-header">
                <span class="tag tag-blue">{{ tip.tip_type }}</span>
                <span class="tip-spot">{{ tip.spot_name || '景点' }}</span>
              </div>
              <h3 class="tip-title">{{ tip.title }}</h3>
              <!-- 攻略内容（最多显示3行） -->
              <p class="tip-content">{{ tip.content }}</p>
              <div class="tip-footer">
                <span class="tip-time">{{ formatDate(tip.created_at) }}</span>
                <el-button type="primary" size="small" plain @click="openEditTip(tip)" style="margin-left: auto;">编辑</el-button>
              </div>
            </div>
          </div>
        </div>

        <!-- ===== 我的行程模块 ===== -->
        <div v-if="activeTab === 'plans'">
          <div class="section-header">
            <h2 class="section-title">我的行程</h2>
            <span class="section-count">共 {{ savedPlans.length }} 个</span>
          </div>

          <!-- 空行程状态 -->
          <div v-if="savedPlans.length === 0" class="empty-state">
            <p class="empty-text">还没有保存过行程</p>
            <el-button type="primary" @click="$router.push('/')">去规划</el-button>
          </div>

          <!-- 行程卡片列表 -->
          <div v-else>
            <div v-for="plan in savedPlans" :key="plan.id" class="plan-card">
              <div class="plan-card-header">
                <div>
                  <h3 class="plan-name">{{ plan.name }}</h3>
                  <!-- 行程标签：城市、天数、偏好 -->
                  <div class="plan-meta">
                    <span class="tag tag-blue">{{ plan.city }}</span>
                    <span class="tag tag-green">{{ plan.days }}天</span>
                    <span v-if="plan.tags" class="tag tag-orange">{{ plan.tags }}</span>
                  </div>
                </div>
                <!-- 操作按钮：查看行程 / 删除 -->
                <div class="plan-actions">
                  <el-button type="primary" size="small" @click="viewPlan(plan)">查看行程</el-button>
                  <el-button type="danger" size="small" plain @click="deletePlan(plan)">删除</el-button>
                </div>
              </div>
              <p class="plan-time">保存于 {{ formatDate(plan.created_at) }}</p>
            </div>
          </div>
        </div>

        <!-- ===== 账号设置模块 ===== -->
        <div v-if="activeTab === 'settings'">
          <div class="section-header">
            <h2 class="section-title">账号设置</h2>
          </div>

          <!-- 修改密码表单 -->
          <div class="settings-card">
            <h3 class="settings-subtitle">修改密码</h3>
            <el-form :model="passwordForm" label-width="80px" style="max-width: 420px;">
              <el-form-item label="旧密码">
                <el-input v-model="passwordForm.old_password" type="password" show-password placeholder="请输入旧密码" />
              </el-form-item>
              <el-form-item label="新密码">
                <el-input v-model="passwordForm.new_password" type="password" show-password placeholder="至少6位" />
              </el-form-item>
              <el-form-item label="确认密码">
                <el-input v-model="passwordForm.confirm_password" type="password" show-password placeholder="再输入一次" />
              </el-form-item>
              <el-form-item>
                <el-button type="primary" @click="handleChangePassword">保存修改</el-button>
              </el-form-item>
            </el-form>
          </div>

          <!-- 账号信息展示（只读） -->
          <div class="settings-card" style="margin-top: 20px;">
            <h3 class="settings-subtitle">账号信息</h3>
            <div class="info-grid">
              <div class="info-row">
                <span class="info-label">用户名</span>
                <span class="info-value">{{ username }}</span>
              </div>
              <div class="info-row">
                <span class="info-label">邮箱</span>
                <span class="info-value">{{ profile.email || '未设置' }}</span>
              </div>
              <div class="info-row">
                <span class="info-label">注册时间</span>
                <span class="info-value">{{ formatDate(profile.date_joined) }}</span>
              </div>
            </div>
          </div>
        </div>

      </el-col>
    </el-row>

    <!-- ===== 编辑日记弹窗 ===== -->
    <el-dialog v-model="diaryDialogVisible" title="编辑日记" width="520px" destroy-on-close>
      <el-form :model="editDiaryForm" label-width="70px">
        <el-form-item label="标题">
          <el-input v-model="editDiaryForm.title" placeholder="日记标题" />
        </el-form-item>
        <el-form-item label="城市">
          <el-input v-model="editDiaryForm.city" placeholder="旅行城市" />
        </el-form-item>
        <el-form-item label="评分">
          <el-rate v-model="editDiaryForm.rating" :max="5" />
        </el-form-item>
        <el-form-item label="内容">
          <el-input v-model="editDiaryForm.content" type="textarea" :rows="6" placeholder="日记内容" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="diaryDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitEditDiary">保存修改</el-button>
      </template>
    </el-dialog>

    <!-- ===== 编辑攻略弹窗 ===== -->
    <el-dialog v-model="tipDialogVisible" title="编辑攻略" width="520px" destroy-on-close>
      <el-form :model="editTipForm" label-width="70px">
        <el-form-item label="标题">
          <el-input v-model="editTipForm.title" placeholder="攻略标题" />
        </el-form-item>
        <el-form-item label="类型">
          <el-select v-model="editTipForm.tip_type" placeholder="选择类型">
            <el-option label="实用建议" value="实用建议" />
            <el-option label="避坑指南" value="避坑指南" />
            <el-option label="美食推荐" value="美食推荐" />
            <el-option label="交通攻略" value="交通攻略" />
            <el-option label="拍照技巧" value="拍照技巧" />
          </el-select>
        </el-form-item>
        <el-form-item label="内容">
          <el-input v-model="editTipForm.content" type="textarea" :rows="6" placeholder="攻略内容" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="tipDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitEditTip">保存修改</el-button>
      </template>
    </el-dialog>

  </div>
</template>

<script setup>
/**
 * ProfileView.vue - 个人中心页面逻辑
 * 
 * 主要功能：
 * - 获取用户个人资料（GET /api/profile/）
 * - 获取收藏、日记、攻略、行程等列表数据
 * - 取消收藏、删除日记、删除行程等操作（均带确认弹窗）
 * - 修改密码（POST /api/profile/change-password/）
 * - 最近动态聚合（合并收藏和日记，按时间排序）
 */
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'
import StatsCard from '../components/StatsCard.vue'

/** 当前登录用户名（从 localStorage 获取） */
const username = localStorage.getItem('username') || ''

/** JWT token */
const token = localStorage.getItem('access_token')

/** 路由实例 */
const router = useRouter()

/** 当前激活的导航模块 */
const activeTab = ref('overview')

/**
 * 用户个人资料
 * @property {string} username - 用户名
 * @property {string} email - 邮箱
 * @property {string} date_joined - 注册时间
 * @property {number} favorites_count - 收藏数
 * @property {number} diaries_count - 日记数
 * @property {number} trips_count - 行程数
 * @property {number} tips_count - 攻略数
 */
const profile = ref({
  username: '', email: '', date_joined: '',
  favorites_count: 0, diaries_count: 0, trips_count: 0, tips_count: 0
})

/** 收藏列表 */
const favorites = ref([])
/** 我的日记列表 */
const myDiaries = ref([])
/** 我的攻略列表 */
const myTips = ref([])
/** 已保存的行程列表 */
const savedPlans = ref([])

/** 修改密码表单 */
const passwordForm = ref({
  old_password: '',
  new_password: '',
  confirm_password: ''
})

/** 编辑日记弹窗 */
const diaryDialogVisible = ref(false)
const editDiaryForm = ref({ id: null, title: '', city: '', content: '', rating: 5 })

/** 编辑攻略弹窗 */
const tipDialogVisible = ref(false)
const editTipForm = ref({ id: null, title: '', content: '', tip_type: '实用建议' })

/**
 * 计算属性：左侧导航菜单项配置
 * 包含标签名称和数据数量角标
 */
const navItems = computed(() => [
  { key: 'overview', label: '个人概览' },
  { key: 'favorites', label: '我的收藏', count: profile.value.favorites_count },
  { key: 'diaries', label: '我的日记', count: profile.value.diaries_count },
  { key: 'tips', label: '我的攻略', count: profile.value.tips_count },
  { key: 'plans', label: '我的行程', count: savedPlans.value.length },
  { key: 'settings', label: '账号设置' },
])

/**
 * 计算属性：最近动态列表
 * 合并最近的收藏和日记操作，取前6条显示
 * 不同类型用不同颜色圆点标识
 */
const recentItems = computed(() => {
  const items = []
  // 收藏动态（红色圆点）
  favorites.value.slice(0, 3).forEach(f => {
    items.push({ id: `fav-${f.id}`, title: `收藏了 ${f.spot.name}`, time: formatDate(f.created_at), dotClass: 'dot-red' })
  })
  // 日记动态（蓝色圆点）
  myDiaries.value.slice(0, 3).forEach(d => {
    items.push({ id: `diary-${d.id}`, title: `发布了日记《${d.title}》`, time: formatDate(d.created_at), dotClass: 'dot-blue' })
  })
  // 按时间排序，取最近6条
  return items.slice(0, 6)
})

/**
 * 智能日期格式化
 * 根据时间差自动选择显示格式：
 * - 1分钟内：刚刚
 * - 1小时内：X分钟前
 * - 24小时内：X小时前
 * - 7天内：X天前
 * - 超过7天：YYYY-MM-DD
 * @param {string} dateStr - ISO 日期字符串
 * @returns {string} 格式化后的时间描述
 */
const formatDate = (dateStr) => {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  const now = new Date()
  const diff = now - d
  const minutes = Math.floor(diff / 60000)
  const hours = Math.floor(diff / 3600000)
  const days = Math.floor(diff / 86400000)

  if (minutes < 1) return '刚刚'
  if (minutes < 60) return `${minutes}分钟前`
  if (hours < 24) return `${hours}小时前`
  if (days < 7) return `${days}天前`
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
}

/** 通用请求头（带 JWT 认证） */
const headers = { Authorization: `Bearer ${token}` }

/** 获取用户个人资料 */
const fetchProfile = async () => {
  try {
    const res = await axios.get('http://127.0.0.1:8000/api/profile/', { headers })
    profile.value = res.data.data
  } catch (err) {
    console.error('获取用户信息失败:', err)
  }
}

/** 获取收藏列表 */
const fetchFavorites = async () => {
  try {
    const res = await axios.get('http://127.0.0.1:8000/api/favorites/', { headers })
    favorites.value = res.data.data
  } catch (err) {
    console.error('获取收藏失败:', err)
  }
}

/** 获取我的日记列表 */
const fetchDiaries = async () => {
  try {
    const res = await axios.get('http://127.0.0.1:8000/api/profile/diaries/', { headers })
    myDiaries.value = res.data.data
  } catch (err) {
    console.error('获取日记失败:', err)
  }
}

/** 获取我的攻略列表 */
const fetchTips = async () => {
  try {
    const res = await axios.get('http://127.0.0.1:8000/api/profile/tips/', { headers })
    myTips.value = res.data.data
  } catch (err) {
    console.error('获取攻略失败:', err)
  }
}

/**
 * 删除日记（带确认弹窗）
 * @param {Object} diary - 要删除的日记对象
 */
const deleteDiary = async (diary) => {
  try {
    await ElMessageBox.confirm('确定要删除这篇日记吗？', '提示', { type: 'warning' })
    await axios.delete(`http://127.0.0.1:8000/api/diaries/${diary.id}/delete/`, { headers })
    myDiaries.value = myDiaries.value.filter(d => d.id !== diary.id)
    profile.value.diaries_count--
    ElMessage.success('日记已删除')
  } catch (err) {
    if (err !== 'cancel') ElMessage.error('删除失败')
  }
}

/** 获取已保存的行程列表 */
const fetchSavedPlans = async () => {
  try {
    const res = await axios.get('http://127.0.0.1:8000/api/plans/', { headers })
    savedPlans.value = res.data.data
  } catch (err) {
    console.error('获取行程失败:', err)
  }
}

/**
 * 删除行程（带确认弹窗）
 * @param {Object} plan - 要删除的行程对象
 */
const deletePlan = async (plan) => {
  try {
    await ElMessageBox.confirm('确定要删除这个行程吗？', '提示', { type: 'warning' })
    await axios.delete(`http://127.0.0.1:8000/api/plans/${plan.id}/delete/`, { headers })
    savedPlans.value = savedPlans.value.filter(p => p.id !== plan.id)
    profile.value.trips_count = savedPlans.value.length
    ElMessage.success('已删除')
  } catch (err) {
    if (err !== 'cancel') ElMessage.error('删除失败')
  }
}

/**
 * 查看行程详情（跳转到规划结果页）
 * @param {Object} plan - 行程对象
 */
const viewPlan = (plan) => {
  router.push({
    name: 'PlanResult',
    query: {
      city: plan.city,
      days: plan.days,
      tags: plan.tags,
      budget: plan.budget
    }
  })
}

/**
 * 取消收藏（带确认弹窗）
 * @param {Object} fav - 收藏对象
 */
const removeFav = async (fav) => {
  try {
    await ElMessageBox.confirm('确定要取消收藏这个景点吗？', '提示', { type: 'warning' })
    await axios.post('http://127.0.0.1:8000/api/favorites/toggle/', { spot_id: fav.spot.id }, { headers })
    favorites.value = favorites.value.filter(f => f.id !== fav.id)
    profile.value.favorites_count--
    ElMessage.success('已取消收藏')
  } catch (err) {
    if (err !== 'cancel') ElMessage.error('操作失败')
  }
}

/**
 * 打开编辑日记弹窗
 * @param {Object} diary - 要编辑的日记对象
 */
const openEditDiary = (diary) => {
  editDiaryForm.value = {
    id: diary.id,
    title: diary.title,
    city: diary.city,
    content: diary.content,
    rating: diary.rating
  }
  diaryDialogVisible.value = true
}

/**
 * 提交编辑日记
 */
const submitEditDiary = async () => {
  if (!editDiaryForm.value.title || !editDiaryForm.value.content) {
    ElMessage.warning('标题和内容不能为空')
    return
  }
  try {
    const res = await axios.put(
      `http://127.0.0.1:8000/api/diaries/${editDiaryForm.value.id}/update/`,
      editDiaryForm.value,
      { headers }
    )
    // 更新本地列表数据
    const idx = myDiaries.value.findIndex(d => d.id === editDiaryForm.value.id)
    if (idx !== -1) {
      myDiaries.value[idx] = { ...myDiaries.value[idx], ...editDiaryForm.value }
    }
    diaryDialogVisible.value = false
    ElMessage.success('日记已更新')
  } catch (err) {
    ElMessage.error(err.response?.data?.message || '更新失败')
  }
}

/**
 * 打开编辑攻略弹窗
 * @param {Object} tip - 要编辑的攻略对象
 */
const openEditTip = (tip) => {
  editTipForm.value = {
    id: tip.id,
    title: tip.title,
    content: tip.content,
    tip_type: tip.tip_type
  }
  tipDialogVisible.value = true
}

/**
 * 提交编辑攻略
 */
const submitEditTip = async () => {
  if (!editTipForm.value.title || !editTipForm.value.content) {
    ElMessage.warning('标题和内容不能为空')
    return
  }
  try {
    const res = await axios.put(
      `http://127.0.0.1:8000/api/tips/${editTipForm.value.id}/update/`,
      editTipForm.value,
      { headers }
    )
    // 更新本地列表数据
    const idx = myTips.value.findIndex(t => t.id === editTipForm.value.id)
    if (idx !== -1) {
      myTips.value[idx] = { ...myTips.value[idx], ...editTipForm.value }
    }
    tipDialogVisible.value = false
    ElMessage.success('攻略已更新')
  } catch (err) {
    ElMessage.error(err.response?.data?.message || '更新失败')
  }
}

/**
 * 修改密码
 * 校验：旧密码非空、新密码一致、新密码至少6位
 */
const handleChangePassword = async () => {
  if (!passwordForm.value.old_password || !passwordForm.value.new_password) {
    ElMessage.warning('请填写完整')
    return
  }
  if (passwordForm.value.new_password !== passwordForm.value.confirm_password) {
    ElMessage.warning('两次输入的密码不一致')
    return
  }
  if (passwordForm.value.new_password.length < 6) {
    ElMessage.warning('新密码至少需要6位')
    return
  }
  try {
    await axios.post('http://127.0.0.1:8000/api/profile/change-password/', {
      old_password: passwordForm.value.old_password,
      new_password: passwordForm.value.new_password
    }, { headers })
    ElMessage.success('密码修改成功，请重新登录')
    // 清空表单
    passwordForm.value = { old_password: '', new_password: '', confirm_password: '' }
  } catch (err) {
    ElMessage.error(err.response?.data?.message || '修改失败')
  }
}

/**
 * 组件挂载时初始化
 * 未登录时提示并返回，已登录时并行获取所有数据
 */
onMounted(() => {
  if (!token) {
    ElMessage.warning('请先登录')
    return
  }
  // 并行获取所有模块数据，提升加载速度
  fetchProfile()
  fetchFavorites()
  fetchDiaries()
  fetchTips()
  fetchSavedPlans()
})
</script>

<style scoped>
/* 页面整体布局 */
.profile-page {
  padding: 24px 6%;
  max-width: 1400px;
  margin: 0 auto;
  min-height: calc(100vh - 120px);
}

/* ===== 左侧导航栏 ===== */
.side-card {
  background: #fff;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
}

/* 用户信息区域 */
.user-info {
  text-align: center;
  padding: 28px 20px 20px;
  border-bottom: 1px solid #f0f0f0;
}

/* 头像外圈渐变环（装饰效果） */
.avatar-ring {
  display: inline-block;
  padding: 3px;
  border-radius: 50%;
  background: linear-gradient(135deg, #409eff, #67c23a);
}

/* 用户头像样式 */
.user-avatar {
  background: #fff;
  color: #409eff;
  font-size: 28px;
  font-weight: bold;
  border: 3px solid #fff;
}

.username {
  margin: 12px 0 4px;
  color: #303133;
  font-size: 18px;
  font-weight: 600;
}

.join-date {
  font-size: 12px;
  color: #909399;
  margin: 0;
}

/* 导航菜单区域 */
.side-nav {
  padding: 8px 0;
}

/* 导航菜单项 */
.nav-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 13px 24px;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 14px;
  color: #606266;
}

/* 菜单项悬停效果 */
.nav-item:hover {
  background: #f5f7fa;
  color: #409eff;
}

/* 菜单项激活状态（蓝色背景 + 右侧蓝色边框） */
.nav-item.active {
  background: #ecf5ff;
  color: #409eff;
  font-weight: 600;
  border-right: 3px solid #409eff;
}

/* 数量角标 */
.nav-badge {
  background: #f0f0f0;
  color: #909399;
  font-size: 12px;
  padding: 2px 8px;
  border-radius: 10px;
  min-width: 20px;
  text-align: center;
}

/* 激活状态的角标变蓝 */
.nav-item.active .nav-badge {
  background: #409eff;
  color: #fff;
}

/* ===== 右侧通用样式 ===== */
.section-header {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
}

.section-title {
  color: #303133;
  font-size: 20px;
  font-weight: 600;
  margin: 0;
}

.section-count {
  margin-left: 12px;
  font-size: 13px;
  color: #909399;
}

/* ===== 统计卡片（已提取为 StatsCard 组件） ===== */
.stats-row {
  margin-bottom: 24px;
}

/* ===== 最近动态区域 ===== */
.recent-card {
  background: #fff;
  border-radius: 12px;
  padding: 20px 24px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
}

.recent-header {
  font-weight: 600;
  font-size: 15px;
  color: #303133;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #f0f0f0;
}

/* 单条动态项 */
.recent-item {
  display: flex;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid #fafafa;
}

.recent-item:last-child {
  border-bottom: none;
}

/* 动态彩色圆点 */
.recent-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  margin-right: 12px;
  flex-shrink: 0;
}

.dot-red { background: #f56c6c; }   /* 收藏动态 */
.dot-blue { background: #409eff; }  /* 日记动态 */
.dot-green { background: #67c23a; }

.recent-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex: 1;
}

.recent-title {
  color: #303133;
  font-size: 14px;
}

.recent-time {
  color: #c0c4cc;
  font-size: 12px;
  flex-shrink: 0;
  margin-left: 12px;
}

/* ===== 空状态 ===== */
.empty-state {
  text-align: center;
  padding: 60px 0;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
}

.empty-text {
  color: #909399;
  font-size: 14px;
  margin-bottom: 16px;
}

.empty-hint {
  text-align: center;
  color: #909399;
  padding: 30px 0;
  font-size: 14px;
}

/* ===== 自定义标签样式 ===== */
.tag {
  display: inline-block;
  font-size: 12px;
  padding: 2px 10px;
  border-radius: 4px;
  margin-right: 6px;
}

.tag-blue { background: #ecf5ff; color: #409eff; }
.tag-green { background: #f0f9eb; color: #67c23a; }
.tag-orange { background: #fdf6ec; color: #e6a23c; }
.tag-gray { background: #f4f4f5; color: #909399; }

/* ===== 收藏卡片 ===== */
.fav-card {
  background: #fff;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
  transition: transform 0.3s, box-shadow 0.3s;
}

.fav-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.1);
}

.img-wrapper {
  position: relative;
  overflow: hidden;
  cursor: pointer;
}

.card-img {
  width: 100%;
  height: 160px;
  object-fit: cover;
  transition: transform 0.4s;
}

.fav-card:hover .card-img {
  transform: scale(1.05);
}

/* 评分角标（半透明黑色背景） */
.img-rating {
  position: absolute;
  top: 10px;
  right: 10px;
  background: rgba(0, 0, 0, 0.6);
  color: #ffd04b;
  font-size: 12px;
  font-weight: bold;
  padding: 2px 8px;
  border-radius: 4px;
}

.fav-body {
  padding: 14px;
}

.fav-name {
  margin: 0 0 6px;
  font-size: 15px;
  color: #303133;
  cursor: pointer;
  font-weight: 600;
}

.fav-name:hover {
  color: #409eff;
}

.fav-city {
  font-size: 12px;
  color: #909399;
  margin: 0 0 10px;
}

.fav-bottom {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.fav-price {
  color: #f56c6c;
  font-weight: bold;
  font-size: 15px;
}

/* ===== 日记卡片 ===== */
.diary-card {
  background: #fff;
  border-radius: 12px;
  padding: 20px 24px;
  margin-bottom: 14px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
  transition: box-shadow 0.2s;
}

.diary-card:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}

.diary-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.diary-title {
  margin: 0;
  font-size: 16px;
  color: #303133;
  font-weight: 600;
}

.diary-tags {
  display: flex;
  gap: 6px;
}

/* 日记内容（限制3行，超出省略） */
.diary-content {
  color: #606266;
  font-size: 14px;
  line-height: 1.7;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
  margin: 0 0 12px;
}

.diary-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

/* 星级评分 */
.diary-rating .star {
  color: #dcdfe6;
  font-size: 14px;
}

/* 已激活的星星（金色） */
.diary-rating .star-active {
  color: #f7ba2a;
}

.diary-time {
  font-size: 12px;
  color: #c0c4cc;
  margin-right: 10px;
}

.diary-actions {
  display: flex;
  align-items: center;
}

/* ===== 攻略卡片 ===== */
.tip-card {
  background: #fff;
  border-radius: 12px;
  padding: 20px 24px;
  margin-bottom: 14px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
  transition: box-shadow 0.2s;
}

.tip-card:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}

.tip-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 10px;
}

.tip-spot {
  font-size: 12px;
  color: #909399;
}

.tip-title {
  margin: 0 0 8px;
  font-size: 16px;
  color: #303133;
  font-weight: 600;
}

/* 攻略内容（限制3行） */
.tip-content {
  color: #606266;
  font-size: 14px;
  line-height: 1.7;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
  margin: 0 0 12px;
}

.tip-footer {
  display: flex;
  justify-content: flex-end;
  align-items: center;
}

.tip-time {
  font-size: 12px;
  color: #c0c4cc;
}

/* ===== 设置模块 ===== */
.settings-card {
  background: #fff;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
}

.settings-subtitle {
  margin: 0 0 20px;
  font-size: 16px;
  color: #303133;
  font-weight: 600;
}

.info-grid {
  max-width: 420px;
}

/* 账号信息行 */
.info-row {
  display: flex;
  padding: 12px 0;
  border-bottom: 1px solid #f5f5f5;
}

.info-row:last-child {
  border-bottom: none;
}

.info-label {
  width: 80px;
  color: #909399;
  font-size: 14px;
  flex-shrink: 0;
}

.info-value {
  color: #303133;
  font-size: 14px;
}


/* ===== 行程卡片 ===== */
.plan-card {
  background: #fff;
  border-radius: 12px;
  padding: 20px 24px;
  margin-bottom: 14px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
  transition: box-shadow 0.2s;
}

.plan-card:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}

/* 行程卡片头部：名称+标签 和 按钮 左右分布 */
.plan-card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.plan-name {
  margin: 0 0 10px;
  font-size: 16px;
  color: #303133;
  font-weight: 600;
}

.plan-meta {
  display: flex;
  gap: 6px;
}

.plan-actions {
  display: flex;
  gap: 8px;
  flex-shrink: 0;
}

.plan-time {
  margin-top: 12px;
  font-size: 12px;
  color: #c0c4cc;
}

</style>
