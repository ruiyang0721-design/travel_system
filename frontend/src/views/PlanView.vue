<!--
  PlanView.vue - 智能旅行规划页面
  ===================================
  功能概述：
    提供两种旅行规划模式 ——「填表规划」和「AI 对话规划」
    - 填表模式：用户选择城市、天数、预算、兴趣标签、入住酒店等参数，提交后跳转到行程结果页
    - AI 对话模式：通过 SSE 流式对话与 AI 助手交互，AI 提取规划参数后可一键生成行程
  
  页面结构：
    1. 页面标题区域（标题 + 副标题）
    2. 模式切换按钮（填表 / AI 对话）
    3. 表单模式卡片（城市、天数、预算、标签、酒店搜索）
    4. AI 对话模式区域（消息列表 + 快捷提示 + 输入框 + 规划确认栏）
-->
<template>
  <!-- ===== 页面主容器 ===== -->
  <div class="plan-container">
    <!-- 页面标题区域：展示主标题和引导语 -->
    <div class="plan-header">
      <h1>智能旅行规划</h1>
      <p>选择目的地和偏好，为您量身定制专属行程</p>
    </div>

    <!-- 模式切换：在"填表规划"和"AI 对话规划"之间切换 -->
    <div class="mode-switch">
      <div class="switch-btn" :class="{ active: mode === 'form' }" @click="mode = 'form'">
        填表规划
      </div>
      <div class="switch-btn" :class="{ active: mode === 'chat' }" @click="mode = 'chat'">
        AI 对话规划
      </div>
    </div>

    <!-- ===== 表单模式 ===== -->
    <el-card v-if="mode === 'form'" class="plan-card" shadow="hover">
      <el-form label-position="top">
        <!-- 第一行：目标城市、游玩天数、预算范围 -->
        <el-row :gutter="24">
          <el-col :span="8">
            <el-form-item label="目标城市">
              <el-select v-model="form.city" placeholder="去哪儿？" style="width: 100%">
                <el-option label="北京" value="北京" />
                <el-option label="上海" value="上海" />
                <el-option label="成都" value="成都" />
                <el-option label="西安" value="西安" />
                <el-option label="杭州" value="杭州" />
                <el-option label="重庆" value="重庆" />
                <el-option label="广州" value="广州" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="游玩天数">
              <el-input-number v-model="form.days" :min="1" :max="7" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="预算范围">
              <el-select v-model="form.budget" placeholder="不限" style="width: 100%" clearable>
                <el-option label="经济型 (<500)" value="low" />
                <el-option label="舒适型 (500-2000)" value="mid" />
                <el-option label="豪华型 (>2000)" value="high" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <!-- 第二行：兴趣偏好（多选标签）、入住酒店搜索 -->
        <el-row :gutter="24">
          <el-col :span="12">
            <el-form-item label="兴趣偏好">
              <el-select v-model="form.tags" multiple collapse-tags placeholder="选择你感兴趣的标签" style="width: 100%">
                <el-option label="历史" value="历史" />
                <el-option label="园林" value="园林" />
                <el-option label="文化" value="文化" />
                <el-option label="亲子" value="亲子" />
                <el-option label="现代" value="现代" />
                <el-option label="自然" value="自然" />
                <el-option label="美食" value="美食" />
                <el-option label="夜景" value="夜景" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="入住酒店 (选填)">
              <!-- 酒店自动补全搜索框，调用高德 API 获取 POI 建议 -->
              <el-autocomplete
                v-model="form.hotelSearch"
                :fetch-suggestions="queryGaodeAPI"
                placeholder="如：全季酒店"
                @select="handleHotelSelect"
                @input="clearHotelData"
                style="width: 100%"
                clearable
              >
                <!-- 自定义下拉项：显示酒店名称和地址 -->
                <template #default="{ item }">
                  <div style="font-weight: bold; line-height: 1.2; margin-top: 5px;">{{ item.name }}</div>
                  <span style="font-size: 12px; color: #999;">{{ item.address }}</span>
                </template>
              </el-autocomplete>
            </el-form-item>
          </el-col>
        </el-row>

        <!-- 第三行：从收藏中选择景点（选填） -->
        <div v-if="form.city && formFavorites.length > 0" class="favorites-section">
          <div class="favorites-label">
            <span>从收藏中选择景点 (选填)</span>
          </div>
          <el-checkbox-group v-model="form.mustInclude">
            <el-checkbox
              v-for="fav in formFavorites"
              :key="fav.spot.id"
              :label="fav.spot.id"
              border
              size="small"
              class="fav-checkbox"
            >
              {{ fav.spot.name }}
            </el-checkbox>
          </el-checkbox-group>
        </div>

        <!-- 提交按钮：校验后跳转到行程结果页 -->
        <el-button
          type="primary"
          size="large"
          style="width: 100%; margin-top: 10px; font-weight: bold; height: 48px; font-size: 16px;"
          @click="goToPlanning"
        >
          智能规划路线
        </el-button>
      </el-form>
    </el-card>

    <!-- ===== AI 对话模式 ===== -->
    <div v-if="mode === 'chat'" class="chat-container">
      <!-- 消息列表区域：包含欢迎语、消息气泡、打字动画 -->
      <div class="chat-messages" ref="chatBox">
        <!-- 欢迎区域：仅在无消息时显示，提供快捷提问入口 -->
        <div class="chat-welcome" v-if="messages.length === 0">
          
          <h3>你好！我是你的 AI 旅行助手</h3>
          <p>告诉我你想去哪里、玩几天、有什么偏好，我会帮你整理需求并生成专属行程</p>
          <!-- 快捷提示标签：点击可快速发送预设消息 -->
          <div class="quick-prompts">
            <div class="prompt-chip" v-for="p in quickPrompts" :key="p" @click="sendMessage(p)">{{ p }}</div>
          </div>
        </div>

        <!-- 遍历渲染每条消息：用户消息靠右，AI 消息靠左 -->
        <div v-for="(msg, i) in messages" :key="i" :class="['msg-row', msg.role === 'user' ? 'msg-user' : 'msg-ai']">
          <div class="msg-avatar" v-if="msg.role === 'assistant'">🤖</div>
          <div class="msg-bubble">
            <div class="msg-text" v-html="renderMarkdown(msg.content)"></div>
          </div>
        </div>

        <!-- AI 正在输入时显示打字动画（三个跳动的点） -->
        <div v-if="loading" class="msg-row msg-ai">
          <div class="msg-avatar">🤖</div>
          <div class="msg-bubble">
            <span class="typing-dots"><span>.</span><span>.</span><span>.</span></span>
          </div>
        </div>
      </div>

      <!-- AI 返回规划参数时显示确认栏：用户可一键生成行程 -->
      <div class="plan-confirm" v-if="planReady">
        <div class="confirm-inner">
          <span>已为你生成规划参数：</span>
          <strong>{{ planData.city }}</strong> · {{ planData.days }}天 ·
          <el-tag size="small" type="success" v-for="t in planData.tags" :key="t" style="margin-left: 4px;">{{ t }}</el-tag>
        </div>
        <!-- 从收藏中选择景点（AI 对话模式） -->
        <div v-if="chatFavorites.length > 0" class="chat-favorites">
          <div class="favorites-label">
            <span>从收藏中选择景点 (选填)</span>
          </div>
          <el-checkbox-group v-model="chatMustInclude">
            <el-checkbox
              v-for="fav in chatFavorites"
              :key="fav.spot.id"
              :label="fav.spot.id"
              border
              size="small"
              class="fav-checkbox"
            >
              {{ fav.spot.name }}
            </el-checkbox>
          </el-checkbox-group>
        </div>
        <div class="confirm-actions">
          <el-button type="primary" size="small" @click="executePlan">
            立即生成行程
          </el-button>
          <el-button size="small" @click="planReady = false">取消</el-button>
        </div>
      </div>

      <!-- 输入框区域：用户输入消息并发送 -->
      <div class="chat-input">
        <el-input
          v-model="inputText"
          placeholder="告诉我目的地、天数和偏好，比如：去西安玩3天，喜欢历史..."
          @keyup.enter="sendMessage()"
          :disabled="loading"
          size="large"
        >
          <template #append>
            <el-button type="primary" @click="sendMessage()" :loading="loading" style="font-size: 16px;">
              发送
            </el-button>
          </template>
        </el-input>
      </div>
    </div>
  </div>
</template>

<script setup>
/**
 * PlanView.vue - 智能旅行规划页面逻辑
 * 
 * 主要功能：
 * - 表单模式：收集用户旅行偏好，跳转到行程结果页
 * - AI 对话模式：通过 SSE 流式请求与后端 AI 交互，解析规划参数
 * - 酒店搜索：调用高德地图 API 实现 POI 自动补全
 */
import { ref, nextTick, watch } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'

// 路由实例，用于页面跳转
const router = useRouter()

/** JWT token（用于判断登录状态） */
const token = localStorage.getItem('access_token')

/**
 * 显示登录提示弹窗
 */
const showLoginDialog = () => {
  ElMessageBox.confirm(
    '请先登录后再进行规划',
    '提示',
    {
      confirmButtonText: '去登录',
      cancelButtonText: '取消',
      type: 'warning',
    }
  ).then(() => {
    router.push('/login')
  }).catch(() => {})
}

// 当前模式：'form'（填表）或 'chat'（AI 对话）
const mode = ref('form')

/**
 * 表单数据对象
 * @property {string} city - 目标城市
 * @property {number} days - 游玩天数
 * @property {string[]} tags - 兴趣偏好标签数组
 * @property {string} hotelSearch - 酒店搜索关键词
 * @property {number|null} hotelLat - 酒店纬度
 * @property {number|null} hotelLng - 酒店经度
 * @property {string} budget - 预算范围 (low/mid/high)
 * @property {number[]} mustInclude - 从收藏中选择的景点 ID 列表
 */
const form = ref({
  city: '',
  days: 3,
  tags: [],
  hotelSearch: '',
  hotelLat: null,
  hotelLng: null,
  budget: '',
  mustInclude: []
})

/** 当前城市下的收藏景点列表 */
const formFavorites = ref([])

/**
 * 监听城市变化，自动获取该城市的收藏景点
 * 前端过滤：从全部收藏中筛选出属于所选城市的
 */
watch(() => form.value.city, async (newCity) => {
  form.value.mustInclude = []
  formFavorites.value = []
  if (!newCity || !token) return
  try {
    const res = await axios.get('http://127.0.0.1:8000/api/favorites/', {
      headers: { Authorization: `Bearer ${token}` }
    })
    if (res.data.status === 'success') {
      formFavorites.value = res.data.data.filter(f => f.spot && f.spot.city === newCity)
    }
  } catch {}
})

// ===== 表单模式逻辑 =====

/**
 * 高德地图 POI 输入提示查询
 * 调用高德 API 获取酒店/地点建议列表，用于自动补全
 * @param {string} queryString - 用户输入的搜索关键词
 * @param {Function} callback - 回调函数，接收格式化后的建议列表
 */
const queryGaodeAPI = async (queryString, callback) => {
  if (!queryString) { callback([]); return }
  try {
    const key = 'dd8b58daef8620b0cfa9b8e842dd57fa' // 高德 API Key
    const res = await axios.get(`https://restapi.amap.com/v3/assistant/inputtips?key=${key}&keywords=${queryString}&city=${form.value.city}&datatype=poi`)
    if (res.data.status === '1' && res.data.tips) {
      // 过滤掉没有经纬度的结果，格式化为组件需要的数据结构
      callback(res.data.tips.filter(i => i.location).map(i => ({
        value: i.name, name: i.name, address: i.district + i.address, location: i.location
      })))
    } else { callback([]) }
  } catch { callback([]) }
}

/**
 * 用户从下拉列表选择酒店后，解析经纬度并存入表单
 * @param {Object} item - 选中的酒店项，包含 location 字段（格式："经度,纬度"）
 */
const handleHotelSelect = (item) => {
  const [lng, lat] = item.location.split(',')
  form.value.hotelLng = lng; form.value.hotelLat = lat; form.value.hotelSearch = item.name
}

/**
 * 清除酒店经纬度数据（当用户手动修改搜索框内容时触发）
 */
const clearHotelData = () => { form.value.hotelLng = null; form.value.hotelLat = null }

/**
 * 表单提交：校验必填项后，携带参数跳转到行程结果页
 */
const goToPlanning = () => {
  if (!token) {
    showLoginDialog()
    return
  }
  if (!form.value.city || !form.value.days || form.value.tags.length === 0) {
    ElMessage.warning('请完整填写城市、天数和偏好哦！'); return
  }
  router.push({
    name: 'PlanResult',
    query: {
      city: form.value.city, days: form.value.days, tags: form.value.tags.join(','),
      hotelName: form.value.hotelSearch, hotelLat: form.value.hotelLat, hotelLng: form.value.hotelLng, budget: form.value.budget,
      ...(form.value.mustInclude.length > 0 ? { must_include: form.value.mustInclude.join(',') } : {})
    }
  })
}

// ===== AI 对话模式逻辑 =====

/** 消息列表：存放所有对话消息（role: 'user' | 'assistant'） */
const messages = ref([])
/** 输入框文本 */
const inputText = ref('')
/** AI 是否正在回复（控制加载状态和打字动画） */
const loading = ref(false)
/** 消息列表 DOM 引用，用于自动滚动到底部 */
const chatBox = ref(null)
/** AI 是否已返回规划参数（控制确认栏显示） */
const planReady = ref(false)
/** AI 返回的规划参数数据（city, days, tags, budget） */
const planData = ref(null)
/** AI 对话模式下的收藏景点列表 */
const chatFavorites = ref([])
/** AI 对话模式下用户勾选的景点 ID */
const chatMustInclude = ref([])

/**
 * 监听 AI 返回的规划参数，自动获取该城市的收藏景点
 */
watch(planData, async (newData) => {
  chatFavorites.value = []
  chatMustInclude.value = []
  if (!newData || !newData.city || !token) return
  try {
    const res = await axios.get('http://127.0.0.1:8000/api/favorites/', {
      headers: { Authorization: `Bearer ${token}` }
    })
    if (res.data.status === 'success') {
      chatFavorites.value = res.data.data.filter(f => f.spot && f.spot.city === newData.city)
    }
  } catch {}
})

/**
 * 快捷提问预设列表
 * 用户可点击快速发送，降低输入门槛
 */
const quickPrompts = [
  '我想去北京玩2天',
  '带父母去成都，3天左右',
  '杭州2天，预算不高',
  '重庆3天，想吃美食看夜景'
]

/**
 * 简易 Markdown 渲染器
 * 将文本中的 **加粗**、换行、`代码` 转换为 HTML
 * @param {string} text - 原始文本
 * @returns {string} 渲染后的 HTML 字符串
 */
const renderMarkdown = (text) => {
  if (!text) return ''
  return text
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\n/g, '<br>')
    .replace(/`(.*?)`/g, '<code>$1</code>')
}

/**
 * 滚动消息列表到底部
 * 使用 nextTick 确保 DOM 更新后再滚动
 */
const scrollToBottom = () => {
  nextTick(() => {
    if (chatBox.value) chatBox.value.scrollTop = chatBox.value.scrollHeight
  })
}

/**
 * 发送消息并接收 AI 流式回复
 * 使用 SSE (Server-Sent Events) 方式逐字接收 AI 响应
 * @param {string} [text] - 可选的直接传入文本，若不传则使用输入框内容
 */
const sendMessage = (text) => {
  const msg = text || inputText.value.trim()
  if (!msg || loading.value) return
  inputText.value = '' // 清空输入框

  // 添加用户消息到列表
  messages.value.push({ role: 'user', content: msg })
  scrollToBottom()

  loading.value = true
  planReady.value = false

  // 预创建一条 AI 消息占位，后续逐字填充内容
  const aiMsg = { role: 'assistant', content: '' }
  messages.value.push(aiMsg)

  // 发起 SSE 流式请求到后端 AI 对话接口
  fetch('http://127.0.0.1:8000/api/ai/chat/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      message: msg,
      history: messages.value.slice(0, -1).map(m => ({ role: m.role, content: m.content }))
    })
  }).then(response => {
    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    let buffer = '' // 缓冲区，处理不完整的 SSE 行

    /**
     * 递归读取流数据
     * 解析 SSE 格式 (data: {...})，根据消息类型分别处理：
     * - text: 追加到 AI 消息内容（实现逐字显示效果）
     * - plan: 存储规划参数，显示确认栏
     * - error: 显示错误信息
     * - [DONE]: 结束流式读取
     */
    function read() {
      reader.read().then(({ done, value }) => {
        if (done) {
          loading.value = false
          scrollToBottom()
          return
        }

        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop() || '' // 保留不完整的行到下次处理

        for (const line of lines) {
          if (!line.startsWith('data: ')) continue
          const data = line.slice(6)
          if (data === '[DONE]') {
            loading.value = false
            scrollToBottom()
            return
          }
          try {
            const parsed = JSON.parse(data)
            if (parsed.type === 'text') {
              // 流式文本：逐字追加到 AI 消息
              aiMsg.content += parsed.content
              scrollToBottom()
            } else if (parsed.type === 'plan') {
              // 规划参数：存入 planData，显示确认栏
              planData.value = parsed.data
              planReady.value = true
              scrollToBottom()
            } else if (parsed.type === 'error') {
              // AI 返回错误
              aiMsg.content = '❌ AI 服务出错：' + parsed.content
              loading.value = false
              scrollToBottom()
            }
          } catch {}
        }
        read() // 继续读取下一块数据
      })
    }
    read()
  }).catch(err => {
    // 网络请求失败处理
    console.error('AI 请求失败:', err)
    aiMsg.content = '❌ 服务暂时不可用，请检查后端是否启动。错误：' + err.message
    loading.value = false
    scrollToBottom()
  })
}

/**
 * 执行 AI 生成的规划：将 planData 中的参数传入并跳转到行程结果页
 */
const executePlan = () => {
  if (!token) {
    showLoginDialog()
    return
  }
  if (!planData.value) return
  router.push({
    name: 'PlanResult',
    query: {
      city: planData.value.city,
      days: planData.value.days,
      tags: (planData.value.tags || []).join(','),
      budget: planData.value.budget || '',
      ...(chatMustInclude.value.length > 0 ? { must_include: chatMustInclude.value.join(',') } : {})
    }
  })
}
</script>

<style scoped>
/* 页面主容器：限制最大宽度并居中 */
.plan-container {
  max-width: 900px;
  margin: 0 auto;
  padding: 40px 20px;
}

/* 页面标题区域 */
.plan-header {
  text-align: center;
  margin-bottom: 24px;
}
.plan-header h1 {
  font-size: 2rem;
  color: #303133;
  margin-bottom: 8px;
}
.plan-header p {
  color: #909399;
  font-size: 15px;
}

/* 模式切换按钮区域 */
.mode-switch {
  display: flex;
  justify-content: center;
  gap: 12px;
  margin-bottom: 24px;
}
/* 切换按钮基础样式（胶囊形状） */
.switch-btn {
  padding: 10px 28px;
  border-radius: 24px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
  background: #f4f4f5;
  color: #606266;
  border: 2px solid transparent;
}
/* 按钮悬停效果 */
.switch-btn:hover {
  background: #ecf5ff;
  color: #409eff;
}
/* 按钮激活状态：蓝色背景 + 阴影 */
.switch-btn.active {
  background: #409eff;
  color: white;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.3);
}

/* 表单模式卡片样式 */
.plan-card {
  border-radius: 16px;
  padding: 10px;
}

/* ===== AI 对话相关样式 ===== */

/* 对话容器：白色圆角卡片，内部使用 flex 纵向布局 */
.chat-container {
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.06);
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

/* 消息列表区域：固定高度，内容溢出时可滚动 */
.chat-messages {
  height: 480px;
  overflow-y: auto;
  padding: 24px;
  scroll-behavior: smooth;
}

/* 欢迎区域样式 */
.chat-welcome {
  text-align: center;
  padding: 40px 20px 20px;
}
.welcome-icon {
  font-size: 48px;
  margin-bottom: 12px;
}
.chat-welcome h3 {
  margin: 0 0 8px;
  color: #303133;
  font-size: 18px;
}
.chat-welcome p {
  color: #909399;
  font-size: 14px;
  margin: 0 0 24px;
}
/* 快捷提示标签容器 */
.quick-prompts {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 10px;
}
/* 快捷提示标签样式（圆角胶囊） */
.prompt-chip {
  padding: 8px 16px;
  background: #f5f7fa;
  border: 1px solid #e4e7ed;
  border-radius: 20px;
  font-size: 13px;
  color: #606266;
  cursor: pointer;
  transition: all 0.2s;
}
.prompt-chip:hover {
  background: #ecf5ff;
  border-color: #409eff;
  color: #409eff;
}

/* 消息行：flex 布局，用户消息靠右，AI 消息靠左 */
.msg-row {
  display: flex;
  margin-bottom: 16px;
  gap: 10px;
}
.msg-user {
  justify-content: flex-end;
}
.msg-ai {
  justify-content: flex-start;
}
/* AI 头像（圆形，带机器人图标） */
.msg-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: #ecf5ff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  flex-shrink: 0;
}
/* 消息气泡通用样式 */
.msg-bubble {
  max-width: 75%;
  padding: 12px 16px;
  border-radius: 16px;
  font-size: 14px;
  line-height: 1.7;
}
/* 用户消息气泡：蓝色背景 */
.msg-user .msg-bubble {
  background: #409eff;
  color: white;
  border-bottom-right-radius: 4px;
}
/* AI 消息气泡：灰色背景 */
.msg-ai .msg-bubble {
  background: #f5f7fa;
  color: #303133;
  border-bottom-left-radius: 4px;
}
/* AI 消息中加粗文本样式 */
.msg-text :deep(strong) { font-weight: 600; }
/* AI 消息中行内代码样式 */
.msg-text :deep(code) {
  background: rgba(0,0,0,0.06);
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 13px;
}

/* 打字动画：三个点依次上下跳动 */
.typing-dots span {
  display: inline-block;
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #909399;
  margin: 0 2px;
  animation: bounce 1.4s infinite;
}
.typing-dots span:nth-child(2) { animation-delay: 0.2s; }
.typing-dots span:nth-child(3) { animation-delay: 0.4s; }
@keyframes bounce {
  0%, 80%, 100% { transform: translateY(0); }
  40% { transform: translateY(-8px); }
}

/* 规划确认栏：AI 返回规划参数后的操作区域 */
.plan-confirm {
  border-top: 1px solid #ebeef5;
  padding: 12px 24px;
  background: #f0f9eb;
}
.confirm-inner {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 6px;
  font-size: 14px;
  color: #303133;
}

/* 输入框区域 */
.chat-input {
  padding: 16px 24px;
  border-top: 1px solid #ebeef5;
  background: #fafafa;
}

/* ===== 收藏景点选择区域 ===== */
.favorites-section {
  margin-top: 16px;
  padding: 16px;
  background: #fdf6ec;
  border-radius: 8px;
  border: 1px solid #faecd8;
}
.favorites-label {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
  font-size: 14px;
  font-weight: 600;
  color: #303133;
}
.fav-checkbox {
  margin-right: 10px;
  margin-bottom: 8px;
}

/* AI 对话模式收藏区域 */
.chat-favorites {
  padding: 12px 24px;
  border-top: 1px solid #ebeef5;
  background: #fdf6ec;
}
.confirm-actions {
  padding: 10px 24px 16px;
  display: flex;
  gap: 10px;
}
</style>
