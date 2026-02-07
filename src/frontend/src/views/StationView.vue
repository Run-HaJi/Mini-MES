<template>
  <div class="station-container">
    
    <div v-if="!currentOperator" class="login-panel">
      <div class="panel-title">🏭 工位终端接入</div>
      <div class="login-box">
        <el-input 
          v-model="loginCode" 
          placeholder="请扫描或输入工号" 
          size="large" 
          class="large-input"
          @keyup.enter="handleLogin"
        >
          <template #prefix>
            <el-icon><User /></el-icon>
          </template>
        </el-input>
        <el-button type="primary" size="large" class="login-btn" @click="handleLogin">
          上岗签到 (Check-in)
        </el-button>
      </div>
    </div>

    <div v-else class="work-panel">
      <div class="status-bar">
        <div class="operator-info">
          <el-icon><Avatar /></el-icon> 
          <span>操作员: {{ currentOperator.name }} ({{ currentOperator.code }})</span>
        </div>
        <div class="station-info">
          <el-tag effect="dark" type="success" size="large">设备在线</el-tag>
          <el-button type="danger" round size="small" @click="handleLogout" style="margin-left: 15px">下班</el-button>
        </div>
      </div>

      <div class="main-workspace">
        <el-card class="entry-card" shadow="hover">
          <template #header>
            <span class="card-title">📝 人工补录作业 (Manual Entry)</span>
          </template>
          
          <el-form :model="form" label-position="top" size="large">
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="设备编号 (Device ID)">
                  <el-select v-model="form.device_id" placeholder="选择当前设备" style="width: 100%">
                    <el-option label="PRESS-001 (一号冲压机)" value="PRESS-001" />
                    <el-option label="PRESS-002 (二号冲压机)" value="PRESS-002" />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                 <el-form-item label="产线 (Line)">
                   <el-select v-model="form.line_id" style="width: 100%">
                     <el-option label="LINE-A" value="LINE-A" />
                     <el-option label="LINE-B" value="LINE-B" />
                   </el-select>
                 </el-form-item>
              </el-col>
            </el-row>

            <el-form-item label="产品 SKU">
              <el-input v-model="form.sku" placeholder="扫描或输入 SKU 码" />
            </el-form-item>

            <el-form-item label="实测重量 (g)">
              <el-input-number v-model="form.weight" :precision="2" :step="0.1" style="width: 100%" />
            </el-form-item>
            
            <el-form-item label="生产批次 (Batch)">
              <el-input v-model="form.batch_id" placeholder="默认自动生成" />
            </el-form-item>

            <el-button type="primary" class="submit-btn" @click="handleSubmit">
              确认提交 (SUBMIT)
            </el-button>
          </el-form>
        </el-card>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { User, Avatar } from '@element-plus/icons-vue'

// --- 状态数据 ---
const loginCode = ref('')
const currentOperator = ref(null) // 存登录后的用户信息
const form = ref({
  device_id: 'PRESS-001',
  line_id: 'LINE-A',
  sku: '',
  weight: 0,
  batch_id: new Date().toISOString().slice(0,10).replace(/-/g,'') + '-MANUAL'
})


// --- 逻辑方法 ---
const handleLogin = async () => {
  if (!loginCode.value) {
    ElMessage.warning('请输入工号')
    return
  }

  try {
    const res = await fetch(`/api/v1/operators/by_code/${loginCode.value}`)
    
    if (res.ok) {
      const realUser = await res.json()
      
      // 1. 更新内存状态
      currentOperator.value = {
        code: realUser.code,
        name: realUser.name
      }
      
      // 💾 2. 新增：存入 LocalStorage (持久化)
      // 我们存成一个 JSON 字符串
      localStorage.setItem('stationUser', JSON.stringify(currentOperator.value))

      ElMessage.success(`欢迎上岗，${realUser.name} 师傅！`)
    } else {
      // ... (报错处理不变) ...
    }
  } catch (e) {
    ElMessage.error('连接服务器失败')
  }
}

const handleLogout = () => {
  // 1. 清空内存
  currentOperator.value = null
  loginCode.value = ''
  
  // 🗑️ 2. 新增：清空 LocalStorage
  localStorage.removeItem('stationUser')
  
  ElMessage.info('已安全下班')
}

// 2. 提交数据
const handleSubmit = async () => {
  if (!form.value.sku || form.value.weight <= 0) {
    ElMessage.error('请完善数据')
    return
  }

  const payload = {
    ...form.value,
    operator_id: currentOperator.value.code // 👈 关键：自动带入工号
  }

  try {
    const res = await fetch('/api/v1/station/submit', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })
    
    if (res.ok) {
      ElMessage.success('数据已录入系统')
      // 重置表单，准备下一条
      form.value.sku = ''
      form.value.weight = 0
    } else {
      ElMessage.error('提交失败')
    }
  } catch (e) {
    ElMessage.error('网络错误')
  }
}

// 🔄 自动恢复登录状态
onMounted(() => {
  // 1. 看看硬盘里有没有上次登录的人
  const savedUser = localStorage.getItem('stationUser')
  
  if (savedUser) {
    // 2. 如果有，直接恢复到内存里
    try {
      currentOperator.value = JSON.parse(savedUser)
      // 可选：给个提示，让他知道系统没忘了他
      // ElMessage.success(`欢迎回来，${currentOperator.value.name}`)
    } catch (e) {
      // 如果数据坏了，就清掉
      localStorage.removeItem('stationUser')
    }
  }
})
</script>

<style scoped>
/* 🌑 深色工业风背景 */
.station-container {
  height: 100vh;
  width: 100vw;
  background-color: #1a1a1a;
  color: #fff;
  display: flex;
  justify-content: center;
  align-items: center;
}

/* 登录面板 */
.login-panel {
  text-align: center;
  width: 400px;
}
.panel-title {
  font-size: 24px;
  margin-bottom: 30px;
  font-weight: bold;
  color: #409EFF;
}
.large-input {
  font-size: 18px;
  height: 50px;
  margin-bottom: 20px;
}
.login-btn {
  width: 100%;
  height: 50px;
  font-size: 18px;
}

/* 作业面板 */
.work-panel {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.status-bar {
  height: 60px;
  background-color: #2c2c2c;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 30px;
  border-bottom: 2px solid #409EFF; /* 顶部蓝条 */
}
.operator-info {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 18px;
  font-weight: bold;
}

.main-workspace {
  flex: 1;
  padding: 40px;
  display: flex;
  justify-content: center;
  background-color: #f0f2f5; /* 内容区还是用亮色，方便看字 */
}

.entry-card {
  width: 800px; /* 大宽屏卡片 */
  height: fit-content;
}
.card-title {
  font-size: 20px;
  font-weight: bold;
}

.submit-btn {
  margin-top: 30px;
  width: 100%;
  height: 60px; /* 超大按钮 */
  font-size: 24px;
  font-weight: bold;
}
</style>