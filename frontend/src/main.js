/**
 * Vue 应用入口文件
 * =================
 * 职责：
 * 1. 创建 Vue 应用实例
 * 2. 注册全局插件（Element Plus UI 组件库、Vue Router 路由）
 * 3. 挂载到 DOM 的 #app 元素
 */

import { createApp } from 'vue'
import App from './App.vue'

// 1. 引入 Element Plus 及其全局样式
// Element Plus 是基于 Vue 3 的企业级 UI 组件库，提供按钮、表单、对话框等预制组件
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'

// 2. 引入路由配置（定义了 9 个页面路由）
import router from './router'

// 创建 Vue 应用实例
const app = createApp(App)

// 3. 注册插件
app.use(ElementPlus)  // 全局注册 Element Plus 组件
app.use(router)       // 启用 Vue Router

// 挂载到页面中 id 为 'app' 的 DOM 元素
app.mount('#app')
