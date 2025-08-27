<!-- views/Experiment/ExperimentLayout.vue -->
<template>
  <div class="experiment-layout">
    <!-- 继承主布局的侧边栏 -->
    <router-view name="sidebar" />

    <!-- 实验内容区域 -->
    <div class="content">
      <router-view />
      <!-- 这里会渲染ExperimentDetail或CodingEditor -->
    </div>
  </div>
</template>

<script setup lang="ts">
// 不需要额外逻辑，仅用于布局嵌套
</script>

<style scoped>
.experiment-layout {
  display: flex;
  min-height: 100vh;
  width: 100%;
}
.content {
  flex: 1;
  padding: 24px;
  background: #f5f7fa;
}
</style>
