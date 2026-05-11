<!--
  MapContainer.vue - 高德地图路线可视化组件
  ============================================
  功能概述：
    接收行程数据（按天分组的景点字典），在高德地图上绘制：
    - 每个景点的标记点（Marker），显示景点名称和序号
    - 每天的路线连线（Polyline），不同天使用不同颜色区分
    - 酒店标记点使用红色样式和 🏠 图标区分
    - 自动调整地图视野以适配所有标记点

  使用方式：
    <MapContainer :itinerary="itineraryData" />
    
  Props：
    - itinerary: Object - 按天分组的行程数据，格式 { "第1天": [景点A, 景点B], "第2天": [...] }
-->
<template>
  <!-- 地图容器外壳（固定高度，带圆角和阴影） -->
  <div class="map-wrapper">
    <!-- 高德地图挂载的 DOM 元素（ID 必须唯一） -->
    <div id="container"></div>
  </div>
</template>

<script setup>
/**
 * MapContainer.vue - 高德地图路线可视化组件逻辑
 * 
 * 主要功能：
 * - 加载高德地图 JS API（使用 @amap/amap-jsapi-loader）
 * - 根据行程数据绘制景点标记点和路线连线
 * - 监听数据变化自动重新绘制
 * - 组件销毁时释放地图资源
 */
import { onMounted, onUnmounted, watch, shallowRef } from 'vue';
import AMapLoader from '@amap/amap-jsapi-loader';

// ================= 1. 接收父组件的数据 =================
/**
 * 组件 Props 定义
 * @property {Object} itinerary - 后端返回的按天分组的行程字典
 *   格式示例：{ "第1天": [{ name, longitude, latitude, is_hotel, ... }] }
 */
const props = defineProps({
  itinerary: {
    type: Object,
    default: () => ({})
  }
});

// ================= 2. 定义局部变量 =================
/**
 * 地图实例（使用 shallowRef 避免深度响应式代理）
 * 为什么不用 ref？高德地图对象极其庞大，用 Vue 的深度响应式会导致页面卡顿甚至报错
 */
const map = shallowRef(null); 
/** 高德 AMap 核心类的引用（用于创建 Marker、Polyline 等） */
let AMapObj = null; 

// ================= 3. 初始化地图的核心函数 =================
/**
 * 初始化高德地图
 * 1. 设置安全密钥
 * 2. 加载高德地图 API
 * 3. 创建地图实例
 * 4. 如果已有行程数据，立即绘制路线
 */
const initMap = () => {
  // 【极其重要】设置高德安全密钥，必须在 AMapLoader.load 之前执行！
  window._AMapSecurityConfig = {
    // TODO: 替换为你自己的 Security Code
    securityJsCode: 'e2fb3d5510219fa7f84417647f5a7b39', 
  };

  // 加载高德地图 API
  AMapLoader.load({
    // TODO: 替换为你自己的 Key
    key: '4a70fa13b3dd131671ffcd28b55ea072', 
    version: '2.0', // 使用高德 2.0 版本
    plugins: ['AMap.Polyline'], // 按需加载折线插件
  }).then((AMap) => {
    AMapObj = AMap; // 保存 AMap 类引用

    // 实例化地图对象，挂载到 #container 元素
    map.value = new AMap.Map('container', {
      zoom: 11, // 初始缩放级别（数值越大看得越近）
      center: [116.397428, 39.90923], // 初始中心点（北京天安门）
    });

    // 如果加载时已有行程数据，立即绘制路线
    if (Object.keys(props.itinerary).length > 0) {
      drawRoutes();
    }
  }).catch((e) => {
    console.error('高德地图加载失败，请检查网络或 Key 是否正确：', e);
  });
};

// ================= 4. 画点和连线的核心逻辑 =================
/**
 * 在地图上绘制所有景点标记和路线连线
 * 处理逻辑：
 * 1. 清空地图上已有的旧标记和连线
 * 2. 遍历每天的景点，为每个景点创建标记点
 * 3. 收集每天的经纬度坐标，创建折线连线
 * 4. 自动调整地图视野以适配所有标记
 */
const drawRoutes = () => {
  // 地图未加载或无数据时直接返回
  if (!map.value || !AMapObj || !props.itinerary) return;

  // 每次绘制前清空旧内容
  map.value.clearMap();

  // 颜色池：每天使用不同颜色的路线，便于区分
  const colors = ['#FF3366', '#3366FF', '#33FF66', '#FF9933', '#9933FF'];
  let dayIndex = 0; // 当前天数索引（用于取颜色）

  // 遍历每天的行程
  for (const [day, spots] of Object.entries(props.itinerary)) {
    const path = []; // 当天所有景点的经纬度数组（用于画线）
    const color = colors[dayIndex % colors.length]; // 当天的路线颜色

    // 遍历当天的每个景点
    spots.forEach((spot, index) => {
      // 提取经纬度坐标 [经度, 纬度]
      const position = [spot.longitude, spot.latitude];
      path.push(position); // 加入路径数组

      // 构建标记点的文字标签内容
      // 酒店：红色背景 + 🏠 图标，不带编号
      // 景点：白色背景 + 序号 + 名称
      const labelContent = spot.is_hotel
        ? `<div style="padding: 2px 5px; background: #f56c6c; border: 1px solid #f56c6c; border-radius: 4px; font-size: 12px; color: white; font-weight: bold;">🏠 ${spot.name}</div>`
        : `<div style="padding: 2px 5px; background: white; border: 1px solid ${color}; border-radius: 4px; font-size: 12px; color: black;">${index}. ${spot.name}</div>`;

      // 创建标记点（Marker）
      const marker = new AMapObj.Marker({
        position: position,
        title: spot.name, // 鼠标悬停提示文字
        label: {
            content: labelContent, // 文字标签 HTML
            direction: 'right' // 标签显示在点的右侧
        }
      });
      // 将标记点添加到地图
      map.value.add(marker);
    });

    // 创建当天的路线连线（Polyline）
    const polyline = new AMapObj.Polyline({
      path: path, // 经纬度坐标数组
      strokeColor: color, // 线条颜色
      strokeWeight: 6, // 线条粗细（像素）
      strokeOpacity: 0.8, // 透明度
      showDir: true // 显示箭头方向（表示游玩顺序）
    });
    // 将连线添加到地图
    map.value.add(polyline);

    dayIndex++; // 天数索引递增
  }

  // 自动调整地图视野：将所有标记和连线完美居中缩放显示
  map.value.setFitView();
};

// ================= 5. Vue 生命周期钩子 =================
// 组件挂载时初始化地图
onMounted(() => {
  initMap();
});

// 组件销毁时释放地图资源，防止内存泄漏
onUnmounted(() => {
  if (map.value) {
    map.value.destroy();
  }
});

// ================= 6. 监听数据变化 =================
/**
 * 监听行程数据变化
 * 当用户拖拽排序或移除景点后，父组件的 itinerary 会变化
 * 此时自动重新绘制路线
 * deep: true 表示深度监听对象内部变化
 */
watch(() => props.itinerary, () => {
  drawRoutes();
}, { deep: true });

</script>

<style scoped>
/* 地图外壳样式 */
.map-wrapper {
  width: 100%;
  height: 600px; /* 地图固定高度 */
  border-radius: 8px; /* 圆角 */
  overflow: hidden;
  border: 2px solid #ebeef5; /* 边框 */
  margin-top: 20px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1); /* 阴影效果 */
}
/* 高德地图要求 container 必须有明确的宽高 */
#container {
  width: 100%;
  height: 100%;
}
</style>
