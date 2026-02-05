<template>
  <div class="dashboard-container">
    <div class="navbar">
      <div class="logo">
        🏭 Mini-MES <span class="version">v0.5</span>
      </div>
      <div class="user-info">
        <span class="username">👤 {{ username }}</span>
        <el-button type="danger" size="small" @click="handleLogout" plain>
          退出登录
        </el-button>
      </div>
    </div>

    <div class="content">
      <div class="header-actions">
        <h2 class="page-title">📊 实时生产看板</h2>
        <div class="btn-group">
          <el-tag type="success" effect="dark" class="status-tag">系统在线</el-tag>
          <el-button type="primary" @click="fetchData">手动刷新</el-button>
          <el-button type="warning" @click="exportData">导出报表</el-button>
        </div>
      </div>

      <el-table :data="tableData" style="width: 100%" border stripe v-loading="loading">
        <el-table-column prop="id" label="流水号" width="100" />
        <el-table-column prop="line_id" label="产线编号" width="120">
          <template #default="scope">
            <el-tag>{{ scope.row.line_id }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="device_id" label="采集设备" width="150" />
        <el-table-column prop="payload.sku" label="产品SKU" width="180">
          <template #default="scope">
            <span style="font-weight: bold; color: #409EFF">{{ scope.row.payload?.sku || 'N/A' }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="payload.weight" label="重量 (g)" width="120">
             <template #default="scope">
                {{ scope.row.payload?.weight }}
             </template>
        </el-table-column>
        <el-table-column label="入库时间">
          <template #default="scope">
             {{ formatDate(scope.row.timestamp) }}
          </template>
        </el-table-column>
      </el-table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router' // 👈 引入路由
import { ElMessage } from 'element-plus'

const router = useRouter()
const tableData = ref([])
const loading = ref(false)
const username = ref(localStorage.getItem('username') || 'Admin') // 获取用户名

// --- 🚪 退出登录逻辑 ---
const handleLogout = () => {
  // 1. 清除本地存储的 Token
  localStorage.removeItem('token')
  localStorage.removeItem('username')
  
  // 2. 提示
  ElMessage.info('已安全退出')
  
  // 3. 强制跳转回登录页
  router.push('/login')
}

const fetchData = async () => {
  loading.value = true
  try {
    const token = localStorage.getItem('token')
    
    const response = await fetch('/api/v1/data/list?limit=20', {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      }
    })

    const res = await response.json()
    
    // 🔍 调试大法：在浏览器控制台打印看看后端到底回了啥
    console.log("后端返回的数据:", res) 

    // 🛡️ 兼容性修复：既支持 {code:200, data:[...]} 也支持直接返回数组 [...]
    if (Array.isArray(res)) {
      // 情况A: 后端直接返回了数组 (Raw List)
      tableData.value = res
      ElMessage.success('数据已刷新')
    } else if (res.code === 200 && Array.isArray(res.data)) {
      // 情况B: 后端返回了标准包装 (Wrapped JSON)
      tableData.value = res.data
      ElMessage.success('数据已刷新')
    } else {
      // 情况C: 数据格式不对
      console.error("数据格式异常:", res)
      ElMessage.warning('暂无数据或格式错误')
    }

  } catch (error) {
    ElMessage.error('获取数据失败')
    console.error(error)
  } finally {
    loading.value = false
  }
}

const exportData = () => {
  window.open('http://localhost:8000/api/v1/data/export')
}

const formatDate = (ts) => {
  if (!ts) return ''
  return new Date(ts * 1000).toLocaleString()
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
/* 全局容器 */
.dashboard-container {
  background-color: #1a1a1a;
  min-height: 100vh;
  color: #fff;
}

/* 🟢 顶部导航栏样式 */
.navbar {
  height: 60px;
  background-color: #242424;
  border-bottom: 1px solid #333;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 40px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.2);
}

.logo {
  font-size: 20px;
  font-weight: bold;
  color: #fff;
  display: flex;
  align-items: center;
  gap: 10px;
}

.version {
  font-size: 12px;
  background: #409EFF;
  padding: 2px 6px;
  border-radius: 4px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 20px;
}

.username {
  color: #ccc;
  font-size: 14px;
}

/* 🟡 内容区样式 */
.content {
  padding: 40px;
  max-width: 1400px;
  margin: 0 auto;
}

.header-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}

.page-title {
  margin: 0;
  color: #eee;
}

.btn-group {
  display: flex;
  align-items: center;
  gap: 15px;
}
</style>