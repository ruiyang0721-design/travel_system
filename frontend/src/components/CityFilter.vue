<!--
  CityFilter.vue - 城市筛选组件
  =================================
  可复用的城市单选筛选栏，支持"全部城市"选项。

  Props：
    modelValue - 当前选中的城市 (v-model)
    cities     - 城市列表（可选，默认7个城市）
    showAll    - 是否显示"全部"选项（默认 true）

  Events：
    update:modelValue - 选中城市变更
    change            - 选中城市变更（携带城市名）
-->
<template>
  <el-radio-group :model-value="modelValue" @update:model-value="onUpdate">
    <el-radio-button v-if="showAll" label="">全部城市</el-radio-button>
    <el-radio-button v-for="city in cities" :key="city" :label="city">{{ city }}</el-radio-button>
  </el-radio-group>
</template>

<script setup>
const props = defineProps({
  modelValue: { type: String, default: '' },
  cities: {
    type: Array,
    default: () => ['北京', '上海', '成都', '西安', '杭州', '重庆', '广州']
  },
  showAll: { type: Boolean, default: true }
})

const emit = defineEmits(['update:modelValue', 'change'])

const onUpdate = (val) => {
  emit('update:modelValue', val)
  emit('change', val)
}
</script>
