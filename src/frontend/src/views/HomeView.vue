<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'

// --- 1. 数据定义 ---
const tableData = ref([]) // 存放从后端拿来的列表
const loading = ref(false) // 加载转圈圈的状态

// --- 2. 核心功能：去后端拉数据 ---
// 给函数加个参数 manual，默认是 false (代表是自动刷新，不弹窗)
const fetchData = async (manual = false) => {
  // 如果是手动刷新，才显示转圈圈；自动刷新时表格别乱闪，体验更好
  if (manual) loading.value = true 
  
  try {
    const res = await axios.get('http://localhost:8000/api/v1/data/list')
    tableData.value = res.data
    
    // 关键点：只有手动触发时，才弹窗
    if (manual) {
      ElMessage.success('数据同步成功')
    }
  } catch (error) {
    console.error(error)
    // 报错还是要弹的，不然这时候不知道断网了
    ElMessage.error('连接服务器失败')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchData() // 第一次加载，静默
  
  // 定时器里也静默刷新，只更新数据，不弹窗
  setInterval(() => {
    fetchData(false)
  }, 2000) // 建议比 3000 稍微快一点点(比如2000)，保证不漏数据
})

// 🛠️ 新增：处理导出按钮点击
const handleExport = () => {
  // 简单粗暴方案：直接让浏览器访问这个下载链接
  // 这种方式最稳定，浏览器会自动处理下载弹窗
  window.location.href = 'http://localhost:8000/api/v1/data/export'
  
  ElMessage.success('正在生成报表，请留意下载弹窗...')
}
</script>

<template>
  <div class="dashboard-container">
    <div class="header">
      <div class="title">🏭 Mini-MES 实时生产看板</div>
      <div class="status-bar">
        <el-tag type="success" effect="dark">系统在线</el-tag>
      </div>
    </div>

    <div class="toolbar">
      <el-button type="primary" @click="fetchData(true)" :loading="loading">
        手动刷新
      </el-button>
      <el-button type="warning" plain @click="handleExport">
        导出报表
      </el-button>
    </div>

    <el-card class="data-card" shadow="always">
      <el-table 
        :data="tableData" 
        style="width: 100%" 
        height="500"
        stripe
        v-loading="loading"
        element-loading-text="正在同步现场数据..."
        element-loading-background="rgba(0, 0, 0, 0.7)"
      >
        <el-table-column prop="id" label="流水号" width="100" />
        <el-table-column prop="line_id" label="产线编号" width="120">
          <template #default="scope">
            <el-tag size="small" effect="plain">{{ scope.row.line_id }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="device_id" label="采集设备" width="150" />
        
        <el-table-column label="产品SKU" width="150">
          <template #default="scope">
            <span style="color: #409EFF; font-weight: bold;">
              {{ scope.row.payload.sku || '-' }}
            </span>
          </template>
        </el-table-column>
        
        <el-table-column label="重量 (g)" width="120">
          <template #default="scope">
            {{ scope.row.payload.weight || 0 }}
          </template>
        </el-table-column>

        <el-table-column prop="created_at" label="入库时间" />
      </el-table>
    </el-card>
  </div>
</template>

<style scoped>
/* 工业风样式定制 */
.dashboard-container {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  border-bottom: 2px solid #4c4d4f;
  padding-bottom: 10px;
}

.title {
  font-size: 24px;
  font-weight: 900; /* 极粗字体，强调工业感 */
  color: #E5EAF3;   /* 亮灰白 */
  letter-spacing: 1px;
}

.toolbar {
  margin-bottom: 15px;
}

.data-card {
  background-color: #1d1e1f; /* 深色卡片背景 */
  border: 1px solid #414243;
}
</style>