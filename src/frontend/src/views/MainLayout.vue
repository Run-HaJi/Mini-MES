<template>
  <div class="common-layout">
    <el-container direction="vertical" class="full-height">
      
      <el-header class="main-header">
        <div class="header-left">
          <span class="app-title">🏭 Mini-MES 工业数据采集与追溯系统</span>
        </div>
        
        <div class="header-right">
          <span class="user-badge">👤 Admin</span>
          <el-button type="danger" size="small" round plain @click="handleLogout" class="logout-btn">
            退出系统
          </el-button>
        </div>
      </el-header>

      <el-container class="body-container">
        
        <el-aside width="240px" class="aside-menu">
          <el-menu
            active-text-color="#409EFF"
            background-color="#1f1f1f"
            text-color="#bbb"
            :default-active="activeRoute"
            router
            class="custom-menu"
          >
            <div style="height: 20px;"></div>

            <el-menu-item index="/dashboard">
              <el-icon :size="20"><DataLine /></el-icon>
              <span class="menu-text">实时看板</span>
            </el-menu-item>

            <el-menu-item index="/operators">
              <el-icon :size="20"><User /></el-icon>
              <span class="menu-text">人员管理</span>
            </el-menu-item>
          </el-menu>
        </el-aside>

        <el-main class="main-content">
          <router-view />
        </el-main>

      </el-container>
    </el-container>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { DataLine, User } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()

const activeRoute = computed(() => route.path)

const handleLogout = () => {
  localStorage.removeItem('token')
  router.push('/login')
}
</script>

<style scoped>
/* 全屏容器 */
.full-height {
  height: 100vh;
  overflow: hidden;
}

/* 🟢 顶部 Header 样式重构 */
.main-header {
  background-color: #409EFF; /* 天蓝色背景 */
  color: #fff;
  height: 64px; /* 稍微加高一点，更有气势 */
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 30px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.15); /* 加点阴影，压住下方 */
  z-index: 100; /* 保证在最上层 */
}

.app-title {
  font-size: 22px; /* 字体加大 */
  font-weight: bold;
  letter-spacing: 1px;
  text-shadow: 0 1px 2px rgba(0,0,0,0.1);
}

.header-right {
  display: flex;
  align-items: center;
  gap: 20px;
}

.user-badge {
  font-size: 16px;
  font-weight: 500;
  opacity: 0.9;
}

.logout-btn {
  background-color: rgba(255,255,255,0.2);
  border: none;
  color: #fff;
}
.logout-btn:hover {
  background-color: rgba(255,255,255,0.3);
}

/* 🟡 下方主体布局 */
.body-container {
  height: calc(100vh - 64px); /* 减去 Header 高度 */
  background-color: #f5f7fa;
}

/* 侧边栏样式 */
.aside-menu {
  background-color: #1f1f1f; /* 深色背景 */
  border-right: none;
}

.custom-menu {
  border-right: none;
  width: 100%;
}

/* 🔥 核心修改：菜单项样式 (宽大、居中、圆角) */
:deep(.el-menu-item) {
  height: 56px; /* 加高 */
  line-height: 56px;
  margin: 8px auto; /* 上下间距8px，左右自动居中 */
  width: 85%; /* 占侧边栏宽度的 85% */
  border-radius: 8px; /* 圆角胶囊 */
  transition: all 0.3s;
}

/* 选中状态 */
:deep(.el-menu-item.is-active) {
  background-color: rgba(64, 158, 255, 0.15) !important; /* 淡淡的蓝色背景 */
  font-weight: bold;
}

/* 悬停状态 */
:deep(.el-menu-item:hover) {
  background-color: #333 !important;
}

.menu-text {
  font-size: 16px; /* 菜单文字加大 */
  margin-left: 10px;
}

/* 内容区 */
.main-content {
  padding: 20px;
  overflow-y: auto;
}
</style>