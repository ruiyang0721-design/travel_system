<!--
  SpotCard.vue - 景点卡片组件
  ==============================
  可复用的景点展示卡片，包含图片、评分角标、名称、标签、价格。

  Props：
    spot    - 景点数据对象（name, city, rating, tags, price, duration 等）
    mode    - 展示模式：'default'（首页/景点大厅）| 'compact'（收藏页等）

  Events：
    click   - 点击卡片时触发，传递 spot 对象
-->
<template>
  <el-card
    shadow="hover"
    class="spot-card"
    :body-style="{ padding: '0px' }"
    style="cursor: pointer;"
    @click="$emit('click', spot)"
  >
    <!-- 景点图片区域 -->
    <div class="img-wrapper">
      <img
        :src="`https://picsum.photos/seed/${spot.name || spot.id}/400/250`"
        class="spot-img"
      />
      <!-- 评分角标 -->
      <div class="img-overlay">
        <el-tag effect="dark" type="warning" size="small">⭐ {{ spot.rating }}</el-tag>
      </div>
      <!-- 价格角标（compact 模式不显示） -->
      <div class="price-badge" v-if="mode !== 'compact' && spot.price > 0">¥{{ spot.price }}</div>
      <div class="price-badge free" v-else-if="mode !== 'compact' && spot.price == 0">免费</div>
    </div>

    <!-- 卡片内容区域 -->
    <div class="card-body">
      <!-- 名称 + 城市 -->
      <div class="card-top" v-if="mode !== 'compact'">
        <h3 class="spot-name">{{ spot.name }}</h3>
        <span class="spot-city" v-if="spot.city">{{ spot.city }}</span>
      </div>
      <h3 v-else class="spot-name" style="margin-bottom: 6px;">{{ spot.name }}</h3>

      <!-- 标签 -->
      <p class="spot-tags" v-if="mode !== 'compact'">
        {{ spot.city }} · {{ spot.tags }}
      </p>
      <p class="spot-tags" v-else>
        {{ spot.city }} · {{ spot.address || spot.tags }}
      </p>

      <!-- 底部：评分 + 价格 -->
      <div class="card-bottom">
        <el-rate v-model="spot.rating" disabled size="small" />
        <span class="spot-price">¥{{ spot.price }}起</span>
      </div>
    </div>
  </el-card>
</template>

<script setup>
defineProps({
  spot: { type: Object, required: true },
  mode: { type: String, default: 'default' }  // 'default' | 'compact'
})

defineEmits(['click'])
</script>

<style scoped>
.spot-card {
  border-radius: 12px;
  overflow: hidden;
  transition: transform 0.3s;
}
.spot-card:hover {
  transform: translateY(-5px);
}

.img-wrapper {
  position: relative;
  overflow: hidden;
}
.spot-img {
  width: 100%;
  height: 200px;
  object-fit: cover;
  transition: transform 0.4s;
}
.spot-card:hover .spot-img {
  transform: scale(1.05);
}

.img-overlay {
  position: absolute;
  top: 10px;
  right: 10px;
}

.price-badge {
  position: absolute;
  bottom: 10px;
  right: 10px;
  background: rgba(245, 108, 108, 0.9);
  color: white;
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: bold;
}
.price-badge.free {
  background: rgba(103, 194, 58, 0.9);
}

.card-body {
  padding: 14px;
}
.card-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 5px;
}
.spot-name {
  margin: 0;
  font-size: 16px;
  color: #303133;
  font-weight: 600;
}
.spot-city {
  font-size: 12px;
  color: #909399;
  background: #f4f4f5;
  padding: 2px 8px;
  border-radius: 10px;
}
.spot-tags {
  font-size: 12px;
  color: #909399;
  margin: 5px 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.card-bottom {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 10px;
}
.spot-price {
  color: #f56c6c;
  font-weight: bold;
}
</style>
