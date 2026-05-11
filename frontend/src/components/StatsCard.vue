<!--
  StatsCard.vue - 统计信息卡片组件
  ===================================
  带彩色左侧边框的统计数字卡片，用于展示关键数据指标。

  Props：
    title     - 指标名称（如"行程预算"）
    value     - 指标值（如"¥ 500"）
    subtitle  - 副标题说明
    color     - 左侧边框颜色：'red' | 'blue' | 'green' | 'orange'
    clickable - 是否可点击（hover 时有阴影效果）

  Events：
    click     - 点击卡片时触发
-->
<template>
  <el-card shadow="hover" class="stats-card" :class="[`border-${color}`, { clickable }]" @click="$emit('click')">
    <div class="stats-card-body">
      <div class="stats-content">
        <div class="stats-title">{{ title }}</div>
        <div class="stats-value">{{ value }}</div>
        <div class="stats-sub">{{ subtitle }}</div>
      </div>
    </div>
  </el-card>
</template>

<script setup>
defineProps({
  title: { type: String, required: true },
  value: { type: [String, Number], required: true },
  subtitle: { type: String, default: '' },
  color: { type: String, default: 'blue' },  // 'red' | 'blue' | 'green' | 'orange'
  clickable: { type: Boolean, default: false }
})

defineEmits(['click'])
</script>

<style scoped>
.stats-card {
  border-radius: 12px;
}
.stats-card-body {
  display: flex;
  align-items: center;
}
.stats-title {
  font-size: 13px;
  color: #909399;
}
.stats-value {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
  margin: 5px 0;
}
.stats-sub {
  font-size: 12px;
  color: #c0c4cc;
}

/* 彩色左侧边框 */
.border-red { border-left: 4px solid #f56c6c; }
.border-blue { border-left: 4px solid #409eff; }
.border-green { border-left: 4px solid #67c23a; }
.border-orange { border-left: 4px solid #e6a23c; }

/* 可点击状态 */
.clickable {
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}
.clickable:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
}
</style>
