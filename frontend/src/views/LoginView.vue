<!--
  LoginView.vue - 登录/注册页面
  ================================
  功能概述：
    提供用户登录和注册两种功能，通过 Tab 切换。
    - 登录：用户名 + 密码，成功后存储 JWT token 到 localStorage 并跳转首页
    - 注册：用户名 + 密码（至少6位），成功后自动切换到登录 Tab

  页面结构：
    1. 品牌 Logo 区域（飞机图标 + 标题 + 副标题）
    2. Tab 切换（账号登录 / 注册新账号）
    3. 登录表单（用户名 + 密码）
    4. 注册表单（用户名 + 密码）
    5. 底部功能亮点展示（三个图标）
-->
<template>
  <!-- 页面容器：渐变紫色背景，垂直居中 -->
  <div class="login-container">
    <el-card class="login-card" shadow="always">
      <!-- 品牌 Logo 区域 -->
      <div class="logo-section">
        <span class="logo-emoji">✈️</span>
        <h2 class="title">智能旅游平台</h2>
        <p class="subtitle">发现世界，从这里开始</p>
      </div>
      
      <!-- Tab 切换：登录 / 注册 -->
      <el-tabs v-model="activeTab" stretch>
        
        <!-- ===== 登录 Tab ===== -->
        <el-tab-pane label="账号登录" name="login">
          <el-form :model="loginForm" label-width="0">
            <el-form-item>
              <el-input v-model="loginForm.username" placeholder="请输入用户名" size="large" prefix-icon="User" />
            </el-form-item>
            <el-form-item>
              <el-input v-model="loginForm.password" type="password" placeholder="请输入密码" size="large" prefix-icon="Lock" show-password @keyup.enter="handleLogin" />
            </el-form-item>
            <el-button type="primary" class="submit-btn" size="large" @click="handleLogin">登 录</el-button>
          </el-form>
        </el-tab-pane>

        <!-- ===== 注册 Tab ===== -->
        <el-tab-pane label="注册新账号" name="register">
          <el-form :model="registerForm" label-width="0">
            <el-form-item>
              <el-input v-model="registerForm.username" placeholder="设置你的用户名" size="large" prefix-icon="User" />
            </el-form-item>
            <el-form-item>
              <el-input v-model="registerForm.password" type="password" placeholder="设置密码 (至少6位)" size="large" prefix-icon="Lock" show-password @keyup.enter="handleRegister" />
            </el-form-item>
            <el-button type="success" class="submit-btn" size="large" @click="handleRegister">注 册</el-button>
          </el-form>
        </el-tab-pane>

      </el-tabs>

      <!-- 底部功能亮点展示 -->
      <div class="features">
        <div class="feature-item">
          <span>智能路线规划</span>
        </div>
        <div class="feature-item">
          <span>酒店位置推荐</span>
        </div>
        <div class="feature-item">
          <span>AI 智能对话</span>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
/**
 * LoginView.vue - 登录/注册页面逻辑
 * 
 * 主要功能：
 * - 用户登录（POST /api/login/），成功后存储 token 和用户名到 localStorage
 * - 用户注册（POST /api/register/），成功后自动切换到登录 Tab
 * - 基本的表单校验（非空、密码长度）
 */
import { ref } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

/** 路由实例 */
const router = useRouter()

/** 当前激活的 Tab：'login' 或 'register' */
const activeTab = ref('login')

/** 登录表单数据 */
const loginForm = ref({ username: '', password: '' })

/** 注册表单数据 */
const registerForm = ref({ username: '', password: '' })

/**
 * 处理登录请求
 * 校验非空后调用后端登录接口，成功后：
 * 1. 将 access_token 存入 localStorage
 * 2. 将用户名存入 localStorage
 * 3. 跳转到首页
 */
const handleLogin = async () => {
  if (!loginForm.value.username || !loginForm.value.password) {
    ElMessage.warning('用户名和密码不能为空哦！')
    return
  }
  try {
    const response = await axios.post('http://127.0.0.1:8000/api/login/', loginForm.value)
    // 存储认证信息到 localStorage
    localStorage.setItem('access_token', response.data.access)
    localStorage.setItem('username', loginForm.value.username)
    ElMessage.success('登录成功，欢迎回来！')
    // 刷新页面跳转到首页
    window.location.href = '/'
  } catch (error) {
    ElMessage.error('登录失败：用户名或密码错误！')
  }
}

/**
 * 处理注册请求
 * 校验非空和密码长度后调用后端注册接口，成功后：
 * 1. 切换到登录 Tab
 * 2. 自动填充登录表单的用户名
 * 3. 清空注册表单的密码
 */
const handleRegister = async () => {
  if (!registerForm.value.username || !registerForm.value.password) {
    ElMessage.warning('用户名和密码不能为空哦！')
    return
  }
  if (registerForm.value.password.length < 6) {
    ElMessage.warning('密码至少需要6位！')
    return
  }
  try {
    const response = await axios.post('http://127.0.0.1:8000/api/register/', registerForm.value)
    ElMessage.success(response.data.message)
    // 自动切换到登录 Tab 并填充用户名
    activeTab.value = 'login'
    loginForm.value.username = registerForm.value.username
    registerForm.value.password = ''
  } catch (error) {
    const errorMsg = error.response?.data?.error || '注册失败，请稍后再试'
    ElMessage.error(errorMsg)
  }
}
</script>

<style scoped>
/* 页面容器：渐变紫色背景，全屏居中 */
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: calc(100vh - 60px);
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 40px 0;
}
/* 登录卡片：固定宽度，圆角 */
.login-card {
  width: 420px;
  border-radius: 16px;
  overflow: hidden;
}
/* Logo 区域居中 */
.logo-section {
  text-align: center;
  margin-bottom: 24px;
}
.logo-emoji {
  font-size: 48px;
  display: block;
  margin-bottom: 10px;
}
.title {
  margin: 0;
  color: #303133;
  font-size: 24px;
}
.subtitle {
  margin: 5px 0 0 0;
  color: #909399;
  font-size: 14px;
}
/* 提交按钮：全宽、加粗 */
.submit-btn {
  width: 100%;
  margin-top: 10px;
  font-weight: bold;
  height: 44px;
}
/* 底部功能亮点：三列均分 */
.features {
  display: flex;
  justify-content: space-around;
  margin-top: 24px;
  padding-top: 20px;
  border-top: 1px solid #f0f0f0;
}
.feature-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  font-size: 13px;
  color: #909399;
}
</style>
