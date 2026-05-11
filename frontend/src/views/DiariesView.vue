<!--
  DiariesView.vue - 旅行日记广场页面
  =====================================
  功能概述：
    展示所有用户发布的旅行日记，支持按城市筛选。
    登录用户可以发布新的旅行日记（含城市、标题、评分、内容）。

  页面结构：
    1. 页面标题 + 写日记按钮
    2. 城市筛选栏（单选按钮组）
    3. 加载状态
    4. 空状态提示
    5. 日记卡片列表（每张卡片含头像、作者、日期、城市标签、评分、标题、内容）
    6. 写日记弹窗（城市选择、标题、评分、内容）
-->
<template>
  <div class="diaries-page">
    <!-- 页面标题栏：标题 + 写日记按钮 -->
    <div class="page-header">
      <h1 class="page-title">📓 旅行日记广场</h1>
      <el-button type="primary" @click="onWriteDiaryClick">
        ✏️ 写日记
      </el-button>
    </div>

    <!-- ===== 城市筛选栏 ===== -->
    <div class="filter-bar">
      <CityFilter v-model="selectedCity" @change="fetchDiaries" />
    </div>

    <!-- 加载中状态 -->
    <div v-if="loading" v-loading="true" style="height: 300px;"></div>

    <!-- 空状态：暂无日记 -->
    <div v-else-if="diaries.length === 0">
      <el-empty description="还没有人写日记，来写第一篇吧！" />
    </div>

    <!-- ===== 日记列表 ===== -->
    <div v-else class="diary-list">
      <el-card v-for="diary in diaries" :key="diary.id" shadow="hover" class="diary-card">
        <!-- 日记头部：头像 + 作者信息 + 城市标签 + 评分 -->
        <div class="diary-header">
          <div class="diary-meta">
            <!-- 用户头像（取用户名首字母大写） -->
            <el-avatar :size="36" style="background: #409EFF; margin-right: 12px;">
              {{ diary.username?.charAt(0)?.toUpperCase() || '?' }}
            </el-avatar>
            <div>
              <div class="diary-author">{{ diary.username || '匿名用户' }}</div>
              <div class="diary-date">{{ formatDate(diary.created_at) }}</div>
            </div>
          </div>
          <div class="diary-tags">
            <el-tag size="small" type="primary">{{ diary.city }}</el-tag>
            <el-rate v-model="diary.rating" disabled size="small" style="margin-left: 10px;" />
          </div>
        </div>
        
        <!-- 日记标题和内容 -->
        <h3 class="diary-title">{{ diary.title }}</h3>
        <p class="diary-content">{{ diary.content }}</p>
      </el-card>
    </div>

    <!-- ===== 写日记弹窗 ===== -->
    <el-dialog v-model="showCreateDialog" title="📝 写旅行日记" width="600px">
      <el-form :model="diaryForm" label-width="80px">
        <!-- 旅行城市选择 -->
        <el-form-item label="旅行城市">
          <el-select v-model="diaryForm.city" placeholder="选择城市" style="width: 100%">
            <el-option label="北京" value="北京" />
            <el-option label="上海" value="上海" />
            <el-option label="成都" value="成都" />
            <el-option label="西安" value="西安" />
            <el-option label="杭州" value="杭州" />
            <el-option label="重庆" value="重庆" />
            <el-option label="广州" value="广州" />
          </el-select>
        </el-form-item>
        <!-- 日记标题 -->
        <el-form-item label="日记标题">
          <el-input v-model="diaryForm.title" placeholder="给这次旅行起个标题" />
        </el-form-item>
        <!-- 旅行评分（1-5星，带文字描述） -->
        <el-form-item label="旅行评分">
          <el-rate v-model="diaryForm.rating" show-text :texts="['失望', '一般', '还行', '不错', '完美']" />
        </el-form-item>
        <!-- 日记内容（多行文本框） -->
        <el-form-item label="日记内容">
          <el-input v-model="diaryForm.content" type="textarea" :rows="6" placeholder="记录你的旅行故事..." />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="submitDiary" :loading="submitting">发布日记</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
/**
 * DiariesView.vue - 旅行日记广场页面逻辑
 * 
 * 主要功能：
 * - 获取并展示所有用户的旅行日记列表
 * - 支持按城市筛选日记
 * - 登录用户可发布新日记（POST /api/diaries/create/）
 */
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'
import CityFilter from '../components/CityFilter.vue'

const router = useRouter()

/** 日记列表数据 */
const diaries = ref([])

/** 数据加载状态 */
const loading = ref(true)

/** 当前选中的城市筛选 */
const selectedCity = ref('')

/** 是否显示创建日记弹窗 */
const showCreateDialog = ref(false)

/** 日记提交加载状态 */
const submitting = ref(false)

/** JWT token（用于认证请求） */
const token = localStorage.getItem('access_token')

/**
 * 点击"写日记"按钮：检查登录状态，未登录则提示并跳转登录页
 */
const onWriteDiaryClick = () => {
  if (!token) {
    ElMessageBox.confirm(
      '请先登录后再写日记',
      '提示',
      { confirmButtonText: '去登录', cancelButtonText: '取消', type: 'warning' }
    ).then(() => { router.push('/login') }).catch(() => {})
    return
  }
  showCreateDialog.value = true
}

/**
 * 日记表单数据
 * @property {string} city - 旅行城市
 * @property {string} title - 日记标题
 * @property {number} rating - 旅行评分（1-5）
 * @property {string} content - 日记内容
 */
const diaryForm = ref({
  city: '',
  title: '',
  rating: 5,
  content: ''
})

/**
 * 从后端获取日记列表
 * 支持按城市筛选（通过 URL 查询参数）
 */
const fetchDiaries = async () => {
  loading.value = true
  try {
    const params = {}
    if (selectedCity.value) params.city = selectedCity.value
    const res = await axios.get('http://127.0.0.1:8000/api/diaries/', { params })
    diaries.value = res.data.data
  } catch (err) {
    console.error('获取日记失败', err)
  } finally {
    loading.value = false
  }
}

/**
 * 提交新日记
 * 校验必填项后发送 POST 请求，成功后关闭弹窗、重置表单、刷新列表
 */
const submitDiary = async () => {
  if (!diaryForm.value.title || !diaryForm.value.content || !diaryForm.value.city) {
    ElMessage.warning('请填写完整信息')
    return
  }
  submitting.value = true
  try {
    await axios.post('http://127.0.0.1:8000/api/diaries/create/', diaryForm.value, {
      headers: { Authorization: `Bearer ${token}` }
    })
    ElMessage.success('日记发布成功！')
    showCreateDialog.value = false
    // 重置表单
    diaryForm.value = { city: '', title: '', rating: 5, content: '' }
    fetchDiaries() // 刷新列表
  } catch (err) {
    ElMessage.error('发布失败，请先登录')
  } finally {
    submitting.value = false
  }
}

/**
 * 格式化日期为中文长日期格式
 * @param {string} dateStr - ISO 日期字符串
 * @returns {string} 如 "2024年1月15日"
 */
const formatDate = (dateStr) => {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return d.toLocaleDateString('zh-CN', { year: 'numeric', month: 'long', day: 'numeric' })
}

// 组件挂载时获取日记列表
onMounted(fetchDiaries)
</script>

<style scoped>
/* 页面整体布局 */
.diaries-page {
  padding: 20px 8%;
  max-width: 1000px;
  margin: 0 auto;
}
/* 标题栏：标题和按钮左右分布 */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}
.page-title {
  color: #303133;
  margin: 0;
}
/* 城市筛选栏底部间距 */
.filter-bar {
  margin-bottom: 24px;
}

/* 日记卡片样式 */
.diary-card {
  margin-bottom: 20px;
  border-radius: 12px;
  transition: transform 0.3s;
}
/* 卡片悬停上浮效果 */
.diary-card:hover {
  transform: translateY(-3px);
}
/* 日记头部：头像+作者 和 城市+评分 左右分布 */
.diary-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}
.diary-meta {
  display: flex;
  align-items: center;
}
.diary-author {
  font-weight: bold;
  color: #303133;
}
.diary-date {
  font-size: 12px;
  color: #c0c4cc;
}
.diary-tags {
  display: flex;
  align-items: center;
}
/* 日记标题 */
.diary-title {
  margin: 0 0 10px 0;
  font-size: 18px;
  color: #303133;
}
/* 日记内容（保留换行符） */
.diary-content {
  color: #606266;
  font-size: 14px;
  line-height: 1.8;
  margin: 0;
  white-space: pre-wrap;
}
</style>
