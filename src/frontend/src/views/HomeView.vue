<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'

// --- 1. 数据定义 ---
const tableData = ref([]) // 存放从后端拿来的列表
const loading = ref(false) // 加载转圈圈的状态

// --- 2. 核心功能：去后端拉数据 ---
const fetchData = async () => {
  loading.value = true
  try {
    // 请求我们刚才写的 GET 接口
    const res = await axios.get('http://localhost:8000/api/v1/data/list')
    tableData.value = res.data
    ElMessage.success('数据同步成功')
  } catch (error) {
    console.error(error)
    ElMessage.error('连接服务器失败，请检查 Docker 是否活着')
  } finally {
    loading.value = false
  }
}

// --- 3. 生命周期：页面一加载，就自动拉一次数据 ---
onMounted(() => {
  fetchData()
  
  // 可选：搞个定时器，每 5 秒自动刷新一次 (工业看板必备)
  setInterval(fetchData, 5000)
})
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
      <el-button type="primary" @click="fetchData" :loading="loading">
        手动刷新
      </el-button>
      <el-button type="warning" plain>导出报表</el-button>
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