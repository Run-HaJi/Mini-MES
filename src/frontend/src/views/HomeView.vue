<template>
  <div class="dashboard-container">
    <div class="navbar">
      <div class="logo">
        🏭 Mini-MES <span class="version">v0.6</span>
      </div>
      <div class="user-info">
        <span class="username">👤 {{ username }}</span>
        <el-button type="danger" size="small" @click="handleLogout" plain>
          退出登录
        </el-button>
      </div>
    </div>

    <div class="content">
      <div class="header-section">
        <div class="title-row">
          <h2 class="page-title">📊 历史追溯与查询</h2>
          <el-tag type="success" effect="dark" class="status-tag">系统在线</el-tag>
        </div>

        <div class="search-toolbar">
          <el-date-picker
            v-model="searchForm.dateRange"
            type="datetimerange"
            range-separator="至"
            start-placeholder="开始时间"
            end-placeholder="结束时间"
            :shortcuts="shortcuts"
            size="large"
            style="width: 380px"
          />
          
          <el-select 
            v-model="searchForm.lineId" 
            placeholder="选择产线" 
            clearable 
            size="large" 
            style="width: 150px"
          >
            <el-option label="LINE-A" value="LINE-A" />
            <el-option label="LINE-B" value="LINE-B" />
          </el-select>

          <el-button type="primary" icon="Search" size="large" @click="handleSearch">
            查询数据
          </el-button>
          
          <el-button icon="Refresh" size="large" @click="handleReset">
            重置
          </el-button>

          <div class="spacer"></div>
          
          <el-button type="warning" icon="Download" size="large" @click="exportData">
            导出报表
          </el-button>
        </div>
      </div>

      <el-table :data="tableData" style="width: 100%" border stripe v-loading="loading">
        <el-table-column prop="id" label="流水号" width="100" />
        <el-table-column prop="line_id" label="产线编号" width="120">
          <template #default="scope">
            <el-tag effect="plain">{{ scope.row.line_id }}</el-tag>
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
             {{ formatDate(scope.row.created_at || scope.row.timestamp) }}
          </template>
        </el-table-column>
      </el-table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Search, Refresh, Download } from '@element-plus/icons-vue'

const router = useRouter()
const tableData = ref([])
const loading = ref(false)
const username = ref(localStorage.getItem('username') || 'Admin')

// 🔍 搜索表单状态
const searchForm = ref({
  lineId: '',
  dateRange: []
})

// 快捷时间选项
const shortcuts = [
  { text: '最近1小时', value: () => { const end = new Date(); const start = new Date(); start.setTime(start.getTime() - 3600 * 1000 * 1); return [start, end] } },
  { text: '最近24小时', value: () => { const end = new Date(); const start = new Date(); start.setTime(start.getTime() - 3600 * 1000 * 24); return [start, end] } },
]

// --- 核心逻辑 ---

const fetchData = async () => {
  loading.value = true
  try {
    const token = localStorage.getItem('token')
    
    // 1. 构建基础 URL
    let url = '/api/v1/data/list?limit=50' // 查历史时稍微多看点，改到50条

    // 2. 动态拼接筛选参数
    if (searchForm.value.lineId) {
      url += `&line_id=${searchForm.value.lineId}`
    }

    if (searchForm.value.dateRange && searchForm.value.dateRange.length === 2) {
      // 前端 Date 对象转成 后端需要的时间戳 (秒)
      const start = Math.floor(new Date(searchForm.value.dateRange[0]).getTime() / 1000)
      const end = Math.floor(new Date(searchForm.value.dateRange[1]).getTime() / 1000)
      url += `&start_time=${start}&end_time=${end}`
    }
    
    // 3. 发请求
    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      }
    })

    const res = await response.json()
    
    // 兼容逻辑
    if (Array.isArray(res)) {
      tableData.value = res
      ElMessage.success(`查询成功，共找到 ${res.length} 条记录`)
    } else if (res.code === 200 && Array.isArray(res.data)) {
      tableData.value = res.data
    } else {
      tableData.value = []
      ElMessage.warning('未查询到数据')
    }

  } catch (error) {
    ElMessage.error('查询失败，请检查网络')
    console.error(error)
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  fetchData()
}

const handleReset = () => {
  searchForm.value.lineId = ''
  searchForm.value.dateRange = []
  fetchData()
}

const handleLogout = () => {
  localStorage.removeItem('token')
  localStorage.removeItem('username')
  router.push('/login')
}

const exportData = () => {
  window.open('http://localhost:8000/api/v1/data/export')
}

const formatDate = (val) => {
  if (!val) return ''
  // 兼容字符串时间(如 '2026-02-05...') 和 时间戳(如 17654...)
  const date = new Date(typeof val === 'number' ? val * 1000 : val)
  return date.toLocaleString()
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.dashboard-container {
  background-color: #1a1a1a;
  min-height: 100vh;
  color: #fff;
}

.navbar {
  height: 60px;
  background-color: #242424;
  border-bottom: 1px solid #333;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 40px;
}

.logo { font-size: 20px; font-weight: bold; }
.version { font-size: 12px; background: #E6A23C; color: #000; padding: 2px 6px; border-radius: 4px; }
.user-info { display: flex; align-items: center; gap: 20px; }
.username { color: #ccc; font-size: 14px; }

.content {
  padding: 30px 40px;
  max-width: 1400px;
  margin: 0 auto;
}

.header-section {
  background: #2c2c2c;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 20px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.2);
}

.title-row {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 20px;
}

.page-title { margin: 0; color: #eee; font-size: 18px; }

/* 搜索栏样式 */
.search-toolbar {
  display: flex;
  gap: 15px;
  flex-wrap: wrap;
  align-items: center;
}

.spacer { flex: 1; } /* 把导出按钮顶到最右边 */

:deep(.el-input__wrapper) {
  background-color: #1a1a1a;
  box-shadow: 0 0 0 1px #444 inset;
}
:deep(.el-input__inner) { color: #fff; }
:deep(.el-range-input) { color: #fff; }
:deep(.el-date-editor .el-range-separator) { color: #888; }
</style>