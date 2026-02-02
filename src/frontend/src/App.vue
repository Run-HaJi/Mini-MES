<script setup>
import { RouterView } from 'vue-router'
</script>

<template>
  <div class="app-container">
    <RouterView />
  </div>
</template>

<style>
/* 全局重置：去掉浏览器的默认边距 */
body {
  margin: 0;
  padding: 0;
  font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', '微软雅黑', Arial, sans-serif;
  background-color: #f0f2f5; /* 浅灰底色，护眼 */
  -webkit-font-smoothing: antialiased;
}

#app {
  width: 100vw;
  height: 100vh;
}
</style>