<!--
  SpotPreviewDialog.vue - 景点快速预览弹窗组件
  ================================================
  点击景点卡片后弹出，展示景点的详细信息，可跳转到完整详情页。

  Props：
    spot     - 景点数据对象
    visible  - 弹窗显示状态 (v-model)

  Events：
    update:visible - 弹窗显示状态变更
-->
<template>
  <el-dialog
    :model-value="visible"
    @update:model-value="$emit('update:visible', $event)"
    :title="spot?.name || ''"
    width="55%"
    align-center
  >
    <div v-if="spot" class="spot-detail-container">
      <!-- 景点大图 -->
      <img
        :src="`https://picsum.photos/seed/${spot.name}/800/400`"
        style="width: 100%; height: 250px; object-fit: cover; border-radius: 8px; margin-bottom: 20px;"
      />

      <!-- 景点详细信息表格 -->
      <el-descriptions :column="2" border>
        <el-descriptions-item label="所属城市">{{ spot.city }}</el-descriptions-item>
        <el-descriptions-item label="门票价格">
          <strong style="color: #f56c6c;">¥ {{ spot.price }}</strong>
        </el-descriptions-item>
        <el-descriptions-item label="建议游玩">{{ spot.duration }} 小时</el-descriptions-item>
        <el-descriptions-item label="景点评分">{{ spot.rating }} 分</el-descriptions-item>
        <el-descriptions-item label="兴趣标签" :span="2">
          <el-tag
            size="small"
            type="success"
            v-for="tag in (spot.tags || '').split(',')"
            :key="tag"
            style="margin-right: 5px;"
          >{{ tag }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="详细地址" :span="2">
          {{ spot.address || '暂无详细地址' }}
        </el-descriptions-item>
        <el-descriptions-item label="景点简介" :span="2">
          {{ spot.description || '暂无简介' }}
        </el-descriptions-item>
      </el-descriptions>
    </div>

    <!-- 弹窗底部按钮 -->
    <template #footer>
      <span class="dialog-footer">
        <el-button @click="$emit('update:visible', false)">关 闭</el-button>
        <el-button type="primary" @click="goToDetail">查看详情</el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script setup>
import { useRouter } from 'vue-router'

const props = defineProps({
  spot: { type: Object, default: () => ({}) },
  visible: { type: Boolean, default: false }
})

const emit = defineEmits(['update:visible'])
const router = useRouter()

const goToDetail = () => {
  if (props.spot?.id) {
    router.push(`/spot/${props.spot.name}`)
  }
  emit('update:visible', false)
}
</script>
